"""Shell execution tool with security safeguards."""

import asyncio
import os
import re
from typing import Any

from loguru import logger

from zergbot.agent.tools.base import Tool

# Dangerous patterns that could cause harm
DANGEROUS_PATTERNS = [
    # Destructive file operations
    (r"rm\s+(-[rf]+\s+)?/", "recursive delete from root"),
    (r"rm\s+-[rf]*\s+~", "delete home directory"),
    (r"rm\s+-[rf]*\s+\*", "wildcard delete"),
    (r"mkfs\.", "format filesystem"),
    (r"dd\s+if=.+of=/dev/", "overwrite disk device"),
    (r">\s*/dev/sd[a-z]", "overwrite disk"),
    (r"chmod\s+777\s+/", "insecure permissions on root"),
    (r"chown\s+-R\s+.+\s+/", "recursive chown from root"),
    # Privilege escalation
    (r"sudo\s+rm", "sudo delete"),
    (r"sudo\s+chmod", "sudo chmod"),
    (r"sudo\s+chown", "sudo chown"),
    # Fork bomb / resource exhaustion
    (r":\(\)\s*\{\s*:\|:&\s*\}\s*;:", "fork bomb"),
    (r"while\s+true.*done", "infinite loop"),
    # Sensitive file access
    (r"cat.+/etc/shadow", "read shadow file"),
    (r"cat.+\.ssh/id_", "read SSH private key"),
    (r"cat.+\.env", "read environment file"),
    # Network exfiltration
    (r"curl.+\|.*(bash|sh)", "curl pipe to shell"),
    (r"wget.+\|.*(bash|sh)", "wget pipe to shell"),
    (r"nc\s+-[e]", "netcat reverse shell"),
]

# Commands that are always blocked (exact match)
BLOCKED_COMMANDS = [
    ":(){ :|:& };:",  # Fork bomb
    "rm -rf /",
    "rm -rf /*",
    "rm -rf ~",
    "rm -rf ~/*",
]


class ExecTool(Tool):
    """
    Tool to execute shell commands with security safeguards.

    By default, blocks dangerous patterns that could:
    - Delete critical files/directories
    - Access sensitive credentials
    - Cause resource exhaustion
    - Enable remote code execution

    Set allow_dangerous=True to bypass (NOT recommended for untrusted input).
    """

    def __init__(
        self,
        timeout: int = 60,
        working_dir: str | None = None,
        allow_dangerous: bool = False,
    ):
        self.timeout = timeout
        self.working_dir = working_dir
        self.allow_dangerous = allow_dangerous

    @property
    def name(self) -> str:
        return "exec"

    @property
    def description(self) -> str:
        return "Execute a shell command and return its output. Use with caution."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The shell command to execute",
                },
                "working_dir": {
                    "type": "string",
                    "description": "Optional working directory for the command",
                },
            },
            "required": ["command"],
        }

    def _check_dangerous(self, command: str) -> str | None:
        """
        Check if command contains dangerous patterns.

        Returns:
            Error message if dangerous, None if safe.
        """
        # Normalize command for checking
        cmd_lower = command.lower().strip()

        # Check exact blocked commands
        for blocked in BLOCKED_COMMANDS:
            if blocked in cmd_lower:
                return f"Blocked: '{blocked}' is not allowed for safety"

        # Check dangerous patterns
        for pattern, description in DANGEROUS_PATTERNS:
            if re.search(pattern, command, re.IGNORECASE):
                return f"Blocked: {description} (pattern: {pattern})"

        return None

    async def execute(
        self, command: str, working_dir: str | None = None, **kwargs: Any
    ) -> str:
        """Execute a shell command with security checks."""
        cwd = working_dir or self.working_dir or os.getcwd()

        # Security check (unless explicitly bypassed)
        if not self.allow_dangerous:
            danger = self._check_dangerous(command)
            if danger:
                logger.warning(f"Blocked dangerous command: {command}")
                return f"Error: {danger}. This command was blocked for security."

        # Log command execution
        logger.debug(f"Executing: {command} (cwd={cwd})")

        try:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd,
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), timeout=self.timeout
                )
            except asyncio.TimeoutError:
                process.kill()
                return f"Error: Command timed out after {self.timeout} seconds"

            output_parts = []

            if stdout:
                output_parts.append(stdout.decode("utf-8", errors="replace"))

            if stderr:
                stderr_text = stderr.decode("utf-8", errors="replace")
                if stderr_text.strip():
                    output_parts.append(f"STDERR:\n{stderr_text}")

            if process.returncode != 0:
                output_parts.append(f"\nExit code: {process.returncode}")

            result = "\n".join(output_parts) if output_parts else "(no output)"

            # Truncate very long output
            max_len = 10000
            if len(result) > max_len:
                result = (
                    result[:max_len]
                    + f"\n... (truncated, {len(result) - max_len} more chars)"
                )

            return result

        except Exception as e:
            return f"Error executing command: {str(e)}"
