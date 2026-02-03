"""File system tools: read, write, edit."""

from pathlib import Path
from typing import Any

from loguru import logger

from zergbot.agent.tools.base import Tool

# Security constants
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB default
BLOCKED_PATHS = [
    "/etc/shadow",
    "/etc/passwd",
    ".ssh/id_",
    ".env",
    ".git/config",
]


def _sanitize_path(path: str, workspace: Path | None = None) -> tuple[Path, str | None]:
    """
    Sanitize and validate a file path.

    Returns:
        Tuple of (resolved_path, error_message).
        If error_message is not None, the path is invalid.
    """
    try:
        file_path = Path(path).expanduser().resolve()

        # Check for blocked paths
        path_str = str(file_path).lower()
        for blocked in BLOCKED_PATHS:
            if blocked in path_str:
                return file_path, f"Error: Access to {blocked} is blocked for security"

        # If workspace is set, ensure path is within it
        if workspace:
            workspace = workspace.resolve()
            try:
                file_path.relative_to(workspace)
            except ValueError:
                return file_path, f"Error: Path must be within workspace"

        return file_path, None
    except Exception as e:
        return Path(path), f"Error: Invalid path"


class ReadFileTool(Tool):
    """Tool to read file contents."""

    def __init__(self, workspace: Path | None = None, max_size: int = MAX_FILE_SIZE):
        self.workspace = workspace
        self.max_size = max_size

    @property
    def name(self) -> str:
        return "read_file"

    @property
    def description(self) -> str:
        return "Read the contents of a file at the given path."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "The file path to read"}
            },
            "required": ["path"],
        }

    async def execute(self, path: str, **kwargs: Any) -> str:
        try:
            file_path, error = _sanitize_path(path, self.workspace)
            if error:
                return error

            if not file_path.exists():
                return "Error: File not found"
            if not file_path.is_file():
                return "Error: Not a file"

            # Check file size before reading
            size = file_path.stat().st_size
            if size > self.max_size:
                return f"Error: File too large ({size} bytes, max {self.max_size})"

            content = file_path.read_text(encoding="utf-8")
            return content
        except PermissionError:
            return "Error: Permission denied"
        except UnicodeDecodeError:
            return "Error: File is not valid UTF-8 text"
        except Exception as e:
            logger.debug(f"Read error for {path}: {e}")
            return "Error: Could not read file"


class WriteFileTool(Tool):
    """Tool to write content to a file."""

    def __init__(self, workspace: Path | None = None, max_size: int = MAX_FILE_SIZE):
        self.workspace = workspace
        self.max_size = max_size

    @property
    def name(self) -> str:
        return "write_file"

    @property
    def description(self) -> str:
        return "Write content to a file at the given path. Creates parent directories if needed."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "The file path to write to"},
                "content": {"type": "string", "description": "The content to write"},
            },
            "required": ["path", "content"],
        }

    async def execute(self, path: str, content: str, **kwargs: Any) -> str:
        try:
            file_path, error = _sanitize_path(path, self.workspace)
            if error:
                return error

            # Check content size
            if len(content.encode("utf-8")) > self.max_size:
                return f"Error: Content too large (max {self.max_size} bytes)"

            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content, encoding="utf-8")
            return f"Successfully wrote {len(content)} bytes"
        except PermissionError:
            return "Error: Permission denied"
        except Exception as e:
            logger.debug(f"Write error for {path}: {e}")
            return "Error: Could not write file"


class EditFileTool(Tool):
    """Tool to edit a file by replacing text."""

    def __init__(self, workspace: Path | None = None, max_size: int = MAX_FILE_SIZE):
        self.workspace = workspace
        self.max_size = max_size

    @property
    def name(self) -> str:
        return "edit_file"

    @property
    def description(self) -> str:
        return "Edit a file by replacing old_text with new_text. The old_text must exist exactly in the file."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "The file path to edit"},
                "old_text": {
                    "type": "string",
                    "description": "The exact text to find and replace",
                },
                "new_text": {
                    "type": "string",
                    "description": "The text to replace with",
                },
            },
            "required": ["path", "old_text", "new_text"],
        }

    async def execute(
        self, path: str, old_text: str, new_text: str, **kwargs: Any
    ) -> str:
        try:
            file_path, error = _sanitize_path(path, self.workspace)
            if error:
                return error

            if not file_path.exists():
                return "Error: File not found"

            # Check file size
            size = file_path.stat().st_size
            if size > self.max_size:
                return f"Error: File too large (max {self.max_size} bytes)"

            content = file_path.read_text(encoding="utf-8")

            if old_text not in content:
                return (
                    "Error: old_text not found in file. Make sure it matches exactly."
                )

            # Count occurrences
            count = content.count(old_text)
            if count > 1:
                return f"Warning: old_text appears {count} times. Please provide more context to make it unique."

            new_content = content.replace(old_text, new_text, 1)
            file_path.write_text(new_content, encoding="utf-8")

            return "Successfully edited file"
        except PermissionError:
            return "Error: Permission denied"
        except UnicodeDecodeError:
            return "Error: File is not valid UTF-8 text"
        except Exception as e:
            logger.debug(f"Edit error for {path}: {e}")
            return "Error: Could not edit file"


class ListDirTool(Tool):
    """Tool to list directory contents."""

    def __init__(self, workspace: Path | None = None, max_items: int = 1000):
        self.workspace = workspace
        self.max_items = max_items

    @property
    def name(self) -> str:
        return "list_dir"

    @property
    def description(self) -> str:
        return "List the contents of a directory."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "The directory path to list"}
            },
            "required": ["path"],
        }

    async def execute(self, path: str, **kwargs: Any) -> str:
        try:
            dir_path, error = _sanitize_path(path, self.workspace)
            if error:
                return error

            if not dir_path.exists():
                return "Error: Directory not found"
            if not dir_path.is_dir():
                return "Error: Not a directory"

            items = []
            count = 0
            for item in sorted(dir_path.iterdir()):
                if count >= self.max_items:
                    items.append(f"... ({count}+ items, truncated)")
                    break
                prefix = "📁 " if item.is_dir() else "📄 "
                items.append(f"{prefix}{item.name}")
                count += 1

            if not items:
                return "Directory is empty"

            return "\n".join(items)
        except PermissionError:
            return "Error: Permission denied"
        except Exception as e:
            logger.debug(f"ListDir error for {path}: {e}")
            return "Error: Could not list directory"
