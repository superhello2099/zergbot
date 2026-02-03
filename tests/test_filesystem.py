"""Tests for filesystem tools."""

import pytest
from pathlib import Path
import tempfile
import os

from zergbot.agent.tools.filesystem import (
    ReadFileTool,
    WriteFileTool,
    EditFileTool,
    ListDirTool,
)


class TestReadFileTool:
    """Test file reading tool."""

    def setup_method(self):
        self.tool = ReadFileTool()

    @pytest.mark.asyncio
    async def test_read_existing_file(self, temp_workspace):
        """Should read existing file."""
        test_file = temp_workspace / "test.txt"
        test_file.write_text("Hello, World!")

        result = await self.tool.execute(str(test_file))
        assert result == "Hello, World!"

    @pytest.mark.asyncio
    async def test_read_nonexistent_file(self):
        """Should return error for non-existent file."""
        result = await self.tool.execute("/nonexistent/file.txt")
        assert "Error" in result
        assert "not found" in result.lower()

    @pytest.mark.asyncio
    async def test_read_directory(self, temp_workspace):
        """Should return error when trying to read directory."""
        result = await self.tool.execute(str(temp_workspace))
        assert "Error" in result
        assert "Not a file" in result


class TestWriteFileTool:
    """Test file writing tool."""

    def setup_method(self):
        self.tool = WriteFileTool()

    @pytest.mark.asyncio
    async def test_write_new_file(self, temp_workspace):
        """Should write new file."""
        test_file = temp_workspace / "new.txt"

        result = await self.tool.execute(str(test_file), "Test content")

        assert "Successfully" in result
        assert test_file.exists()
        assert test_file.read_text() == "Test content"

    @pytest.mark.asyncio
    async def test_write_creates_parent_dirs(self, temp_workspace):
        """Should create parent directories."""
        test_file = temp_workspace / "a" / "b" / "c" / "test.txt"

        result = await self.tool.execute(str(test_file), "Nested content")

        assert "Successfully" in result
        assert test_file.exists()

    @pytest.mark.asyncio
    async def test_write_overwrites_existing(self, temp_workspace):
        """Should overwrite existing file."""
        test_file = temp_workspace / "existing.txt"
        test_file.write_text("Old content")

        await self.tool.execute(str(test_file), "New content")

        assert test_file.read_text() == "New content"


class TestEditFileTool:
    """Test file editing tool."""

    def setup_method(self):
        self.tool = EditFileTool()

    @pytest.mark.asyncio
    async def test_edit_replaces_text(self, temp_workspace):
        """Should replace text in file."""
        test_file = temp_workspace / "edit.txt"
        test_file.write_text("Hello, World!")

        result = await self.tool.execute(str(test_file), "World", "Python")

        assert "Successfully" in result
        assert test_file.read_text() == "Hello, Python!"

    @pytest.mark.asyncio
    async def test_edit_nonexistent_file(self):
        """Should return error for non-existent file."""
        result = await self.tool.execute("/nonexistent/file.txt", "old", "new")
        assert "Error" in result
        assert "not found" in result.lower()

    @pytest.mark.asyncio
    async def test_edit_text_not_found(self, temp_workspace):
        """Should return error when text not found."""
        test_file = temp_workspace / "edit.txt"
        test_file.write_text("Hello, World!")

        result = await self.tool.execute(str(test_file), "Python", "Java")

        assert "Error" in result
        assert "not found" in result.lower()

    @pytest.mark.asyncio
    async def test_edit_multiple_occurrences(self, temp_workspace):
        """Should warn about multiple occurrences."""
        test_file = temp_workspace / "edit.txt"
        test_file.write_text("Hello Hello Hello")

        result = await self.tool.execute(str(test_file), "Hello", "Hi")

        assert "Warning" in result or "3 times" in result


class TestListDirTool:
    """Test directory listing tool."""

    def setup_method(self):
        self.tool = ListDirTool()

    @pytest.mark.asyncio
    async def test_list_directory(self, temp_workspace):
        """Should list directory contents."""
        # Create some files and dirs
        (temp_workspace / "file.txt").write_text("content")
        (temp_workspace / "subdir").mkdir()

        result = await self.tool.execute(str(temp_workspace))

        assert "file.txt" in result
        assert "subdir" in result

    @pytest.mark.asyncio
    async def test_list_empty_directory(self, temp_workspace):
        """Should handle empty directory."""
        result = await self.tool.execute(str(temp_workspace))
        assert "empty" in result.lower()

    @pytest.mark.asyncio
    async def test_list_nonexistent_directory(self):
        """Should return error for non-existent directory."""
        result = await self.tool.execute("/nonexistent/dir")
        assert "Error" in result
        assert "not found" in result.lower()

    @pytest.mark.asyncio
    async def test_list_file_not_directory(self, temp_workspace):
        """Should return error when path is a file."""
        test_file = temp_workspace / "file.txt"
        test_file.write_text("content")

        result = await self.tool.execute(str(test_file))

        assert "Error" in result
        assert "Not a directory" in result
