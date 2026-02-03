"""Tests for subagent manager."""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from pathlib import Path

from zergbot.agent.subagent import SubagentManager
from zergbot.bus.queue import MessageBus


class TestSubagentManager:
    """Test subagent lifecycle management."""

    def setup_method(self):
        self.mock_provider = Mock()
        self.mock_provider.get_default_model.return_value = "test-model"
        self.workspace = Path("/tmp/zergbot_test")
        self.bus = MessageBus()

        self.manager = SubagentManager(
            provider=self.mock_provider,
            workspace=self.workspace,
            bus=self.bus,
        )

    def test_init(self):
        """Manager should initialize properly."""
        assert self.manager.provider == self.mock_provider
        assert self.manager.workspace == self.workspace
        assert self.manager._running_tasks == {}
        assert self.manager._shutting_down is False

    def test_get_running_count_empty(self):
        """Should return 0 when no tasks running."""
        assert self.manager.get_running_count() == 0

    def test_get_running_tasks_empty(self):
        """Should return empty list when no tasks running."""
        assert self.manager.get_running_tasks() == []

    @pytest.mark.asyncio
    async def test_spawn_returns_status(self):
        """Spawn should return a status message."""
        # Mock the provider.chat to return immediately
        self.mock_provider.chat = AsyncMock(
            return_value=Mock(
                has_tool_calls=False, content="Task completed", tool_calls=[]
            )
        )

        result = await self.manager.spawn(
            task="Test task", label="Test", origin_channel="cli", origin_chat_id="test"
        )

        assert "started" in result.lower()
        assert "Test" in result

    @pytest.mark.asyncio
    async def test_spawn_blocked_during_shutdown(self):
        """Should not spawn during shutdown."""
        self.manager._shutting_down = True
        result = await self.manager.spawn("Test task")
        assert "Error" in result or "shutdown" in result.lower()

    @pytest.mark.asyncio
    async def test_cancel_nonexistent_task(self):
        """Cancel should return False for non-existent task."""
        result = await self.manager.cancel_task("nonexistent-id")
        assert result is False

    @pytest.mark.asyncio
    async def test_shutdown_empty(self):
        """Shutdown should work with no running tasks."""
        await self.manager.shutdown(timeout=1.0)
        assert self.manager._shutting_down is False  # Reset after shutdown

    @pytest.mark.asyncio
    async def test_shutdown_clears_tasks(self):
        """Shutdown should clear all tasks."""

        # Create a mock task
        async def mock_task():
            await asyncio.sleep(10)

        task = asyncio.create_task(mock_task())
        self.manager._running_tasks["test-id"] = task

        await self.manager.shutdown(timeout=1.0)

        assert len(self.manager._running_tasks) == 0
        assert task.cancelled() or task.done()


class TestSubagentPrompt:
    """Test subagent prompt building."""

    def setup_method(self):
        self.mock_provider = Mock()
        self.mock_provider.get_default_model.return_value = "test-model"
        self.manager = SubagentManager(
            provider=self.mock_provider,
            workspace=Path("/tmp/test"),
            bus=MessageBus(),
        )

    def test_build_prompt_contains_task(self):
        """Prompt should contain the task."""
        task = "Research the latest AI news"
        prompt = self.manager._build_subagent_prompt(task)
        assert task in prompt

    def test_build_prompt_contains_workspace(self):
        """Prompt should contain workspace path."""
        prompt = self.manager._build_subagent_prompt("test")
        assert "/tmp/test" in prompt

    def test_build_prompt_contains_rules(self):
        """Prompt should contain rules."""
        prompt = self.manager._build_subagent_prompt("test")
        assert "Rules" in prompt or "rules" in prompt
