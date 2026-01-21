"""
Shell execution tool.

Execute bash commands with smart timeout handling.
"""

from __future__ import annotations

import subprocess
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class ToolResult:
    """Result from tool execution."""
    success: bool
    output: Any
    error: Optional[str] = None


class ShellTool:
    """Execute bash commands with smart timeout and error handling."""

    name = "bash"
    description = "Execute bash commands. Use for running scripts, installing packages, executing Python, etc."

    parameters = {
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "The bash command to execute"
            },
            "timeout": {
                "type": "integer",
                "description": "Timeout in seconds (default: 120)",
                "default": 120
            }
        },
        "required": ["command"]
    }

    def __init__(self, working_dir: str = "."):
        self.working_dir = working_dir

    def _adjust_timeout(self, command: str, base_timeout: int) -> int:
        """Adjust timeout based on command type."""
        cmd_lower = command.lower()

        if any(kw in cmd_lower for kw in ["install", "pip", "npm", "apt", "brew"]):
            return min(300, base_timeout * 5)
        elif any(kw in cmd_lower for kw in ["git clone", "wget", "curl", "download"]):
            return min(180, base_timeout * 3)
        elif any(kw in cmd_lower for kw in ["test", "pytest", "npm test"]):
            return min(300, base_timeout * 5)
        elif any(kw in cmd_lower for kw in ["python", "python3"]):
            return min(600, base_timeout * 5)  # Python scripts may run long

        return base_timeout

    def execute(self, command: str = None, timeout: int = 120) -> ToolResult:
        """Execute a bash command."""
        if not command or not command.strip():
            return ToolResult(
                success=False,
                output=None,
                error="No command provided. The 'command' argument is required."
            )

        timeout = self._adjust_timeout(command, timeout)

        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=self.working_dir
            )

            output = ""
            if result.stdout:
                output += result.stdout
            if result.stderr:
                output += f"\n[stderr]\n{result.stderr}" if output else result.stderr

            return ToolResult(
                success=result.returncode == 0,
                output=output.strip() or "(no output)",
                error=None if result.returncode == 0 else f"Exit code: {result.returncode}"
            )

        except subprocess.TimeoutExpired:
            return ToolResult(success=False, output=None, error=f"Command timed out after {timeout}s")
        except Exception as e:
            return ToolResult(success=False, output=None, error=str(e))

    def to_schema(self) -> Dict:
        """Convert to OpenAI-style tool schema."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters
        }


def get_tool(working_dir: str = ".") -> ShellTool:
    """Factory function for tool discovery."""
    return ShellTool(working_dir)
