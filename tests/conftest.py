"""Pytest configuration and fixtures."""

import asyncio
import pytest
from pathlib import Path
import tempfile
import shutil


@pytest.fixture
def temp_workspace():
    """Create a temporary workspace directory."""
    workspace = Path(tempfile.mkdtemp(prefix="zergbot_test_"))
    yield workspace
    shutil.rmtree(workspace, ignore_errors=True)


@pytest.fixture
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()
