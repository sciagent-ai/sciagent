# Tool Architecture v2: Filesystem-as-Memory Model

**Key Insight**: Claude Code uses the filesystem as its memory system. No separate memory tools needed.

---

## The Pattern Claude Code Uses

```
Write Python file    → Code persists
Write JSON file      → Data persists
Read file back       → Recall
Execute Python       → Use results
```

---

## Minimal Tool Set (5 Atomic Tools)

```python
ATOMIC_TOOLS = [
    "bash",        # Execute shell commands and Python scripts
    "file_ops",    # Read/Write/Edit - THIS IS MEMORY
    "search",      # Glob + Grep combined
    "web",         # WebSearch + WebFetch combined
    "todo",        # Track task progress
]
```

---

## Tool Specifications

### 1. `bash` (shell.py)
Execute shell commands with timeout and output capture.

```python
class BashTool:
    name = "bash"

    def execute(self, command: str, timeout: int = 120) -> ToolResult:
        """Run shell command, return stdout/stderr"""
```

### 2. `file_ops` (file_ops.py)
Unified file operations - read, write, edit, list.

```python
class FileOpsTool:
    name = "file_ops"

    def read(self, path: str, start_line: int = None, end_line: int = None) -> str:
        """Read file contents with optional line range"""

    def write(self, path: str, content: str) -> ToolResult:
        """Create or overwrite file"""

    def edit(self, path: str, old_str: str, new_str: str) -> ToolResult:
        """Replace unique string in file"""

    def list(self, path: str, recursive: bool = False) -> List[str]:
        """List directory contents"""
```

### 3. `search` (search.py)
Combined glob and grep functionality.

```python
class SearchTool:
    name = "search"

    def glob(self, pattern: str, path: str = ".") -> List[str]:
        """Find files matching glob pattern"""

    def grep(self, pattern: str, path: str = ".",
             regex: bool = True, context_lines: int = 0) -> List[Match]:
        """Search file contents for pattern"""
```

### 4. `web` (web.py)
Combined web search and fetch.

```python
class WebTool:
    name = "web"

    def search(self, query: str, num_results: int = 10) -> List[SearchResult]:
        """Search the web"""

    def fetch(self, url: str) -> str:
        """Fetch and extract content from URL"""
```

### 5. `todo` (todo.py)
Task tracking for long-horizon work.

```python
class TodoTool:
    name = "todo"

    def write(self, todos: List[dict]) -> ToolResult:
        """Update todo list with tasks and statuses"""
```

---

## Memory Patterns: Use Files

### Pattern 1: Data Persistence (JSON)
```python
# Agent writes JSON for structured data
# results.json
{
    "unit_cells": [...],
    "simulation_results": {...},
    "best_candidates": [...]
}
```

### Pattern 2: Code Persistence (Python modules)
```python
# Agent writes Python modules that can be imported
# metasurface_library.py
KNOWN_UNIT_CELLS = {
    "nanopillar": {"phase_range": [0, 2*pi], "efficiency": 0.85},
    "nanofin": {"phase_range": [0, 2*pi], "efficiency": 0.92},
}
```

### Pattern 3: Literature/Sources Persistence
```python
# Agent stores citations, not raw search results
# sources.json
{
    "query": "metasurface unit cell 1550nm phase coverage",
    "date": "2026-01-14",
    "sources": [
        {
            "title": "High-efficiency silicon metasurfaces",
            "url": "https://...",
            "key_finding": "nanopillars achieve 92% efficiency at 1550nm"
        },
        {
            "title": "Full 2π phase coverage with nanofins",
            "url": "https://...",
            "key_finding": "aspect ratio >3 required for full phase"
        }
    ]
}
```

**Rule**: Store distilled knowledge and citations, not raw search results.

---

## Real Example: Metasurface Discovery Task

What Claude Code created with just 5 tools:

| File Created | Purpose | Tool Used |
|--------------|---------|-----------|
| `metasurface_library.py` | Store known unit cells | `file_ops.write` |
| `rcwa_simulator.py` | RCWA simulation code | `file_ops.write` |
| `bayesian_optimizer.py` | BO framework | `file_ops.write` |
| `novelty_validator.py` | Check novelty | `file_ops.write` |
| `run_discovery_demo.py` | Orchestration | `file_ops.write` |
| `sources.json` | Literature citations | `file_ops.write` |
| `demo_discovery_results.json` | Results | (script output) |

Execution: `bash("python run_discovery_demo.py")`

---

## Implementation Plan

### Step 1: Create directory structure
```
tools/
├── atomic/
│   ├── __init__.py
│   ├── shell.py      # bash tool
│   ├── file_ops.py   # read/write/edit/list
│   ├── search.py     # glob + grep
│   ├── web.py        # search + fetch
│   └── todo.py       # task tracking
└── registry.py       # tool loading & registration
```

### Step 2: Merge existing tools
```
bash.py                    → atomic/shell.py
str_replace_editor.py  ─┬─→ atomic/file_ops.py
list_directory.py      ─┘
glob_search.py         ─┬─→ atomic/search.py
grep_search.py         ─┘
web_fetch.py           ─┬─→ atomic/web.py
web_search.py          ─┘
todo_write.py              → atomic/todo.py
```

### Step 3: Archive unused tools
```
save_memory.py             → ARCHIVE (filesystem is memory)
recall_memory.py           → ARCHIVE (filesystem is memory)
reflect.py                 → ARCHIVE (add later if needed)
create_summary.py          → ARCHIVE
update_progress_md.py      → ARCHIVE
multi_edit.py              → ARCHIVE (file_ops.edit handles this)
advanced_file_ops.py       → ARCHIVE (file_ops handles this)
notebook_edit.py           → ARCHIVE (defer to domain/)
task_agent.py              → ARCHIVE (add when sub-agents needed)
ask_user_step.py           → ARCHIVE
performance_monitor.py     → ARCHIVE
git_operations.py          → ARCHIVE (can use bash for git)
```

### Step 4: Update main registry
```python
# tools/registry.py
def create_default_registry(working_dir: str = ".") -> ToolRegistry:
    from tools.atomic.shell import ShellTool
    from tools.atomic.file_ops import FileOpsTool
    from tools.atomic.search import SearchTool
    from tools.atomic.web import WebTool
    from tools.atomic.todo import TodoTool

    registry = ToolRegistry()
    registry.register(ShellTool(working_dir))
    registry.register(FileOpsTool(working_dir))
    registry.register(SearchTool(working_dir))
    registry.register(WebTool())
    registry.register(TodoTool())
    return registry  # 5 tools total
```

---

## Comparison: Before vs After

| Before (22 tools) | After (5 tools) | Notes |
|-------------------|-----------------|-------|
| bash | bash (shell.py) | Keep |
| str_replace_editor | file_ops.py | Merge |
| list_directory | file_ops.py | Merge |
| glob_search | search.py | Merge |
| grep_search | search.py | Merge |
| web_fetch | web.py | Merge |
| web_search | web.py | Merge |
| todo_write | todo.py | Keep |
| save_memory | - | Remove |
| recall_memory | - | Remove |
| reflect | - | Remove |
| create_summary | - | Remove |
| update_progress_md | - | Remove |
| multi_edit | - | Remove |
| advanced_file_ops | - | Remove |
| notebook_edit | - | Defer |
| task_agent | - | Defer |
| ask_user_step | - | Defer |
| performance_monitor | - | Remove |
| git_operations | - | Optional |

---

## Why This Works

1. **Filesystem IS memory** - JSON, Python files persist data
2. **Less context overhead** - 5 tool schemas vs 22
3. **Composable** - write code that does complex things, then execute
4. **Debuggable** - all artifacts are files you can inspect
5. **Matches Claude Code** - proven pattern for complex scientific tasks
6. **Citations preserved** - sources.json captures literature provenance

---

## Adding Domain Tools Later

When needed, add domain-specific tools:

```
tools/
├── atomic/           # Always loaded (5 tools)
└── domain/           # Loaded on-demand
    ├── data_science/
    │   └── notebook.py
    ├── engineering/
    │   └── simulation.py
    └── chemistry/
        └── molecular.py
```

Load pattern:
```python
if task_needs_notebooks:
    registry.register(NotebookTool())
```
