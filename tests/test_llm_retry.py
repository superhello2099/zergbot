"""Tests for LLM retry logic."""

import pytest
import httpx
import asyncio
from unittest.mock import Mock, AsyncMock, patch


class TestLLMRetry:
    """Test LLM call retry behavior."""

    @pytest.mark.asyncio
    async def test_retry_decorator_exists(self):
        """Retry decorator should be applied to _call_llm_with_retry."""
        from zergbot.agent.loop import AgentLoop
        from zergbot.bus.queue import MessageBus
        from pathlib import Path

        # Check that the method exists and has retry decorator
        assert hasattr(AgentLoop, "_call_llm_with_retry")

        # The retry decorator adds attributes
        method = AgentLoop._call_llm_with_retry
        assert hasattr(method, "retry")

    @pytest.mark.asyncio
    async def test_retry_on_http_error(self):
        """Should retry on HTTP errors."""
        from tenacity import retry, stop_after_attempt, retry_if_exception_type

        call_count = 0

        @retry(
            stop=stop_after_attempt(3), retry=retry_if_exception_type(httpx.HTTPError)
        )
        async def flaky_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise httpx.HTTPError("Connection failed")
            return "success"

        result = await flaky_function()
        assert result == "success"
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_retry_on_timeout(self):
        """Should retry on timeout errors."""
        from tenacity import retry, stop_after_attempt, retry_if_exception_type

        call_count = 0

        @retry(
            stop=stop_after_attempt(3),
            retry=retry_if_exception_type(asyncio.TimeoutError),
        )
        async def timeout_function():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise asyncio.TimeoutError()
            return "success"

        result = await timeout_function()
        assert result == "success"
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_max_retries_exceeded(self):
        """Should raise after max retries."""
        from tenacity import retry, stop_after_attempt, retry_if_exception_type

        @retry(
            stop=stop_after_attempt(3),
            retry=retry_if_exception_type(httpx.HTTPError),
            reraise=True,
        )
        async def always_fails():
            raise httpx.HTTPError("Always fails")

        with pytest.raises(httpx.HTTPError):
            await always_fails()
