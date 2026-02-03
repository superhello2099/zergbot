"""Subagent manager for background task execution."""

import asyncio
import json
import uuid
from pathlib import Path
from typing import Any

from loguru import logger

from zergbot.bus.events import InboundMessage
from zergbot.bus.queue import MessageBus
from zergbot.providers.base import LLMProvider
from zergbot.agent.tools.registry import ToolRegistry
from zergbot.agent.tools.filesystem import ReadFileTool, WriteFileTool, ListDirTool
from zergbot.agent.tools.shell import ExecTool
from zergbot.agent.tools.web import WebSearchTool, WebFetchTool


class SubagentManager:
    """
    Manages background subagent execution.

    Subagents are lightweight agent instances that run in the background
    to handle specific tasks. They share the same LLM provider but have
    isolated context and a focused system prompt.
    """

    def __init__(
        self,
        provider: LLMProvider,
        workspace: Path,
        bus: MessageBus,
        model: str | None = None,
        brave_api_key: str | None = None,
    ):
        self.provider = provider
        self.workspace = workspace
        self.bus = bus
        self.model = model or provider.get_default_model()
        self.brave_api_key = brave_api_key
        self._running_tasks: dict[str, asyncio.Task[None]] = {}
        self._shutting_down = False

    async def spawn(
        self,
        task: str,
        label: str | None = None,
        origin_channel: str = "cli",
        origin_chat_id: str = "direct",
    ) -> str:
        """
        Spawn a subagent to execute a task in the background.

        Args:
            task: The task description for the subagent.
            label: Optional human-readable label for the task.
            origin_channel: The channel to announce results to.
            origin_chat_id: The chat ID to announce results to.

        Returns:
            Status message indicating the subagent was started.
        """
        if self._shutting_down:
            return "Error: Cannot spawn subagent during shutdown."

        task_id = str(uuid.uuid4())[:8]
        display_label = label or task[:30] + ("..." if len(task) > 30 else "")

        origin = {
            "channel": origin_channel,
            "chat_id": origin_chat_id,
        }

        # Create background task with safe wrapper
        bg_task = asyncio.create_task(
            self._run_subagent_safe(task_id, task, display_label, origin),
            name=f"subagent-{task_id}",
        )
        self._running_tasks[task_id] = bg_task

        logger.info(f"Spawned subagent [{task_id}]: {display_label}")
        return f"Subagent [{display_label}] started (id: {task_id}). I'll notify you when it completes."

    async def _run_subagent_safe(
        self,
        task_id: str,
        task: str,
        label: str,
        origin: dict[str, str],
    ) -> None:
        """
        Safe wrapper around subagent execution.

        Handles exceptions and cleanup properly.
        """
        try:
            await self._run_subagent(task_id, task, label, origin)
        except asyncio.CancelledError:
            logger.info(f"Subagent [{task_id}] was cancelled")
            # Don't announce on cancellation (shutdown scenario)
            raise
        except Exception as e:
            logger.exception(f"Subagent [{task_id}] crashed: {e}")
            # Announce error to user
            await self._announce_result(
                task_id, label, task, f"Subagent crashed: {str(e)}", origin, "error"
            )
        finally:
            # Always cleanup task from registry
            self._running_tasks.pop(task_id, None)
            logger.debug(f"Subagent [{task_id}] cleaned up")

    async def _run_subagent(
        self,
        task_id: str,
        task: str,
        label: str,
        origin: dict[str, str],
    ) -> None:
        """Execute the subagent task and announce the result."""
        logger.info(f"Subagent [{task_id}] starting task: {label}")

        # Build subagent tools (no message tool, no spawn tool)
        tools = ToolRegistry()
        tools.register(ReadFileTool())
        tools.register(WriteFileTool())
        tools.register(ListDirTool())
        tools.register(ExecTool(working_dir=str(self.workspace)))
        tools.register(WebSearchTool(api_key=self.brave_api_key))
        tools.register(WebFetchTool())

        # Build messages with subagent-specific prompt
        system_prompt = self._build_subagent_prompt(task)
        messages: list[dict[str, Any]] = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": task},
        ]

        # Run agent loop (limited iterations)
        max_iterations = 15
        iteration = 0
        final_result: str | None = None

        while iteration < max_iterations:
            iteration += 1

            # Check for cancellation between iterations
            if self._shutting_down:
                logger.info(f"Subagent [{task_id}] stopping due to shutdown")
                return

            response = await self.provider.chat(
                messages=messages,
                tools=tools.get_definitions(),
                model=self.model,
            )

            if response.has_tool_calls:
                # Add assistant message with tool calls
                tool_call_dicts = [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.name,
                            "arguments": json.dumps(tc.arguments),
                        },
                    }
                    for tc in response.tool_calls
                ]
                messages.append(
                    {
                        "role": "assistant",
                        "content": response.content or "",
                        "tool_calls": tool_call_dicts,
                    }
                )

                # Execute tools
                for tool_call in response.tool_calls:
                    logger.debug(f"Subagent [{task_id}] executing: {tool_call.name}")
                    result = await tools.execute(tool_call.name, tool_call.arguments)
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": tool_call.name,
                            "content": result,
                        }
                    )
            else:
                final_result = response.content
                break

        if final_result is None:
            final_result = "Task completed but no final response was generated."

        logger.info(f"Subagent [{task_id}] completed successfully")
        await self._announce_result(task_id, label, task, final_result, origin, "ok")

    async def _announce_result(
        self,
        task_id: str,
        label: str,
        task: str,
        result: str,
        origin: dict[str, str],
        status: str,
    ) -> None:
        """Announce the subagent result to the main agent via the message bus."""
        status_text = "completed successfully" if status == "ok" else "failed"

        announce_content = f"""[Subagent '{label}' {status_text}]

Task: {task}

Result:
{result}

Summarize this naturally for the user. Keep it brief (1-2 sentences). Do not mention technical details like "subagent" or task IDs."""

        # Inject as system message to trigger main agent
        msg = InboundMessage(
            channel="system",
            sender_id="subagent",
            chat_id=f"{origin['channel']}:{origin['chat_id']}",
            content=announce_content,
        )

        await self.bus.publish_inbound(msg)
        logger.debug(
            f"Subagent [{task_id}] announced result to {origin['channel']}:{origin['chat_id']}"
        )

    def _build_subagent_prompt(self, task: str) -> str:
        """Build a focused system prompt for the subagent."""
        return f"""# Subagent

You are a subagent spawned by the main agent to complete a specific task.

## Your Task
{task}

## Rules
1. Stay focused - complete only the assigned task, nothing else
2. Your final response will be reported back to the main agent
3. Do not initiate conversations or take on side tasks
4. Be concise but informative in your findings

## What You Can Do
- Read and write files in the workspace
- Execute shell commands
- Search the web and fetch web pages
- Complete the task thoroughly

## What You Cannot Do
- Send messages directly to users (no message tool available)
- Spawn other subagents
- Access the main agent's conversation history

## Workspace
Your workspace is at: {self.workspace}

When you have completed the task, provide a clear summary of your findings or actions."""

    def get_running_count(self) -> int:
        """Return the number of currently running subagents."""
        return len(self._running_tasks)

    def get_running_tasks(self) -> list[str]:
        """Return list of running task IDs."""
        return list(self._running_tasks.keys())

    async def shutdown(self, timeout: float = 30.0) -> None:
        """
        Gracefully shutdown all running subagents.

        Args:
            timeout: Maximum time to wait for subagents to finish.
        """
        if not self._running_tasks:
            logger.info("No subagents to shutdown")
            return

        self._shutting_down = True
        task_count = len(self._running_tasks)
        logger.info(f"Shutting down {task_count} subagent(s)...")

        # Get all tasks
        tasks = list(self._running_tasks.values())

        # Cancel all tasks
        for task in tasks:
            if not task.done():
                task.cancel()

        # Wait for all tasks to complete with timeout
        if tasks:
            try:
                await asyncio.wait_for(
                    asyncio.gather(*tasks, return_exceptions=True),
                    timeout=timeout,
                )
                logger.info(f"All {task_count} subagent(s) shut down cleanly")
            except asyncio.TimeoutError:
                logger.warning(
                    f"Shutdown timeout after {timeout}s, some subagents may not have cleaned up"
                )

        # Clear any remaining tasks
        self._running_tasks.clear()
        self._shutting_down = False

    async def cancel_task(self, task_id: str) -> bool:
        """
        Cancel a specific subagent task.

        Args:
            task_id: The task ID to cancel.

        Returns:
            True if task was found and cancelled, False otherwise.
        """
        task = self._running_tasks.get(task_id)
        if task is None:
            return False

        if not task.done():
            task.cancel()
            logger.info(f"Cancelled subagent [{task_id}]")
            return True

        return False
