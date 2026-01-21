"""
Atomic tools - minimal set of composable primitives.

These 5 tools handle 90% of scientific/engineering tasks:
- shell: Execute bash commands
- file_ops: Read/write/edit files (filesystem is memory)
- search: Find files (glob) and content (grep)
- web: Search and fetch web content
- todo: Track task progress
"""

from tools.atomic.shell import ShellTool
from tools.atomic.file_ops import FileOpsTool
from tools.atomic.search import SearchTool
from tools.atomic.web import WebTool
from tools.atomic.todo import TodoTool

__all__ = [
    "ShellTool",
    "FileOpsTool",
    "SearchTool",
    "WebTool",
    "TodoTool",
]
