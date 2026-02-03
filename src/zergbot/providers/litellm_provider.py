"""LiteLLM provider implementation for multi-provider support."""

import os
from typing import Any

import litellm
from litellm import acompletion

from zergbot.providers.base import LLMProvider, LLMResponse, ToolCallRequest


class LiteLLMProvider(LLMProvider):
    """
    LLM provider using LiteLLM for multi-provider support.

    Supports OpenRouter, Anthropic, OpenAI, and many other providers through
    a unified interface.
    """

    def __init__(
        self,
        api_key: str | None = None,
        api_base: str | None = None,
        default_model: str = "anthropic/claude-opus-4-5",
    ):
        super().__init__(api_key, api_base)
        self.default_model = default_model

        # Detect OpenRouter by api_key prefix or explicit api_base
        self.is_openrouter = (api_key and api_key.startswith("sk-or-")) or (
            api_base and "openrouter" in api_base
        )

        # Detect custom OpenAI-compatible endpoint (like FLAMINGO/vLLM)
        self.is_custom_openai = (
            api_base and "openai.com" not in api_base and "openrouter" not in api_base
        )

        # Store for later use in chat()
        self.api_base = api_base
        self.api_key = api_key

        # Configure environment for OpenRouter
        if api_key and self.is_openrouter:
            os.environ["OPENROUTER_API_KEY"] = api_key

        # Disable LiteLLM logging noise
        litellm.suppress_debug_info = True

    async def chat(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        model: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> LLMResponse:
        """
        Send a chat completion request via LiteLLM.

        Args:
            messages: List of message dicts with 'role' and 'content'.
            tools: Optional list of tool definitions in OpenAI format.
            model: Model identifier (e.g., 'anthropic/claude-sonnet-4-5').
            max_tokens: Maximum tokens in response.
            temperature: Sampling temperature.

        Returns:
            LLMResponse with content and/or tool calls.
        """
        model = model or self.default_model

        # For custom OpenAI-compatible endpoints (vLLM, FLAMINGO, etc.)
        # Use OpenAI SDK directly to avoid litellm's API key validation
        if self.is_custom_openai:
            return await self._chat_openai_direct(
                messages, tools, model, max_tokens, temperature
            )

        # For OpenRouter, prefix model name if not already prefixed
        if self.is_openrouter and not model.startswith("openrouter/"):
            model = f"openrouter/{model}"

        kwargs: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        # Pass API credentials
        if self.api_base:
            kwargs["api_base"] = self.api_base
        if self.api_key:
            kwargs["api_key"] = self.api_key

        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"

        try:
            response = await acompletion(**kwargs)
            return self._parse_response(response)
        except Exception as e:
            # Return error as content for graceful handling
            return LLMResponse(
                content=f"Error calling LLM: {str(e)}",
                finish_reason="error",
            )

    async def _chat_openai_direct(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None,
        model: str,
        max_tokens: int,
        temperature: float,
    ) -> LLMResponse:
        """Direct OpenAI SDK call for custom endpoints (vLLM, FLAMINGO, etc.)."""
        from openai import AsyncOpenAI

        # Strip openai/ prefix if present
        if model.startswith("openai/"):
            model = model[7:]

        client = AsyncOpenAI(
            api_key=self.api_key or "sk-local",
            base_url=self.api_base,
        )

        kwargs: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"

        try:
            response = await client.chat.completions.create(**kwargs)
            return self._parse_openai_response(response)
        except Exception as e:
            return LLMResponse(
                content=f"Error calling LLM: {str(e)}",
                finish_reason="error",
            )

    def _parse_openai_response(self, response: Any) -> LLMResponse:
        """Parse OpenAI SDK response into our standard format."""
        choice = response.choices[0]
        message = choice.message

        tool_calls = []
        if message.tool_calls:
            import json

            for tc in message.tool_calls:
                args = tc.function.arguments
                if isinstance(args, str):
                    try:
                        args = json.loads(args)
                    except json.JSONDecodeError:
                        args = {"raw": args}

                tool_calls.append(
                    ToolCallRequest(
                        id=tc.id,
                        name=tc.function.name,
                        arguments=args,
                    )
                )

        usage = {}
        if response.usage:
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            }

        return LLMResponse(
            content=message.content,
            tool_calls=tool_calls,
            finish_reason=choice.finish_reason or "stop",
            usage=usage,
        )

    def _parse_response(self, response: Any) -> LLMResponse:
        """Parse LiteLLM response into our standard format."""
        choice = response.choices[0]
        message = choice.message

        tool_calls = []
        if hasattr(message, "tool_calls") and message.tool_calls:
            for tc in message.tool_calls:
                # Parse arguments from JSON string if needed
                args = tc.function.arguments
                if isinstance(args, str):
                    import json

                    try:
                        args = json.loads(args)
                    except json.JSONDecodeError:
                        args = {"raw": args}

                tool_calls.append(
                    ToolCallRequest(
                        id=tc.id,
                        name=tc.function.name,
                        arguments=args,
                    )
                )

        usage = {}
        if hasattr(response, "usage") and response.usage:
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            }

        return LLMResponse(
            content=message.content,
            tool_calls=tool_calls,
            finish_reason=choice.finish_reason or "stop",
            usage=usage,
        )

    def get_default_model(self) -> str:
        """Get the default model."""
        return self.default_model
