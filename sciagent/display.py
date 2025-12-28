"""User display formatting for the SCI Agent.

The :class:`AgentDisplay` class provides a professional display with distinct
phases for thinking, planning, and execution.
"""

from typing import Dict, Any, Optional, List
import time
from datetime import datetime
from enum import Enum


class AgentPhase(Enum):
    """Agent execution phases."""
    THINKING = "thinking"
    PLANNING = "planning"
    EXECUTING = "executing"
    COMPLETE = "complete"


class AgentDisplay:
    """AI agent display with thinking and planning."""

    def __init__(self, verbosity_level: str = "verbose", indent_level: int = 0, metrics_mode: bool = False):
        """Initialize the display with verbosity control.

        Parameters
        ----------
        verbosity_level: str
            Desired verbosity (``"minimal"``, ``"standard"``, ``"verbose"`` or ``"debug"``).
        indent_level: int
            Indentation level applied to nested sub-agent output.
        metrics_mode: bool
            Enable detailed metrics tracking and display.
        """
        self.verbosity = verbosity_level
        self.show_debug = verbosity_level == "debug"
        self.indent_level = indent_level
        self.indent = "  " * indent_level
        self.metrics_mode = metrics_mode
        
        # Track current phase
        self.current_phase = None
        self.phase_start_time = None
        
        # Performance tracking (only when enabled)
        if self.metrics_mode:
            self.session_start_time = time.time()
            self.tool_metrics = {
                "calls": 0,
                "total_time": 0.0,
                "total_tokens": 0,
                "total_cost": 0.0,
                "tool_times": {},
                "current_tool_start": None,
                "phase_times": {}
            }
        else:
            self.tool_metrics = None

    # Phase Management --------------------------------------------------------

    def start_thinking_phase(self, context: str = "") -> None:
        """Start the thinking phase - agent is analyzing the problem."""
        self._end_current_phase()
        self.current_phase = AgentPhase.THINKING
        self.phase_start_time = time.time()
        
        print(f"\n{self.indent}╭─ 🧠 Thinking")
        if context and self.verbosity in ["verbose", "debug"]:
            print(f"{self.indent}│  {context}")

    def show_thinking(self, thought: str) -> None:
        """Display a thought during the thinking phase."""
        if self.current_phase != AgentPhase.THINKING:
            return
            
        if self.verbosity != "minimal":
            # Wrap long thoughts
            max_width = 80 - len(self.indent) - 3
            lines = self._wrap_text(thought, max_width)
            for line in lines:
                print(f"{self.indent}│  {line}")

    def start_planning_phase(self, num_steps: Optional[int] = None) -> None:
        """Start the planning phase - agent is creating an execution plan."""
        self._end_current_phase()
        self.current_phase = AgentPhase.PLANNING
        self.phase_start_time = time.time()
        
        header = f"📋 Planning"
        if num_steps:
            header += f" ({num_steps} steps)"
        print(f"\n{self.indent}╭─ {header}")

    def show_plan_step(self, step_num: int, description: str, details: str = "") -> None:
        """Display a single step in the execution plan."""
        if self.current_phase != AgentPhase.PLANNING:
            return
            
        print(f"{self.indent}│  {step_num}. {description}")
        if details and self.verbosity in ["verbose", "debug"]:
            detail_lines = self._wrap_text(details, 75 - len(self.indent))
            for line in detail_lines:
                print(f"{self.indent}│     {line}")

    def start_execution_phase(self) -> None:
        """Start the execution phase - agent is performing actions."""
        self._end_current_phase()
        self.current_phase = AgentPhase.EXECUTING
        self.phase_start_time = time.time()
        
        print(f"\n{self.indent}╭─ ⚡ Executing")

    def _end_current_phase(self) -> None:
        """End the current phase and print closing border."""
        if self.current_phase is None:
            return
            
        # Track phase duration
        if self.metrics_mode and self.tool_metrics and self.phase_start_time:
            duration = time.time() - self.phase_start_time
            phase_name = self.current_phase.value
            if phase_name not in self.tool_metrics["phase_times"]:
                self.tool_metrics["phase_times"][phase_name] = []
            self.tool_metrics["phase_times"][phase_name].append(duration)
        
        # Print closing border
        if self.verbosity != "minimal":
            print(f"{self.indent}╰─")

    # Tool Execution Display --------------------------------------------------

    def show_header(self, working_dir: str, tools_count: int) -> None:
        """Display a clean header at startup."""
        print(f"\n╔══════════════════════════════════════════════════════════════╗")
        print(f"║  🔧 WELCOME TO SCIAGENT                                      ║")
        print(f"╚══════════════════════════════════════════════════════════════╝")
        print(f"\n📁 Working directory: {working_dir}")
        if self.verbosity in ["verbose", "debug"]:
            print(f"⚙️  Available tools: {tools_count}")
        print()

    def show_task_start(self, task: str) -> None:
        """Show the start of a new task."""
        print(f"╭─────────────────────────────────────────────────────────────╮")
        print(f"│ 🎯 Task: {task[:55]}")
        if len(task) > 55:
            remaining = self._wrap_text(task[55:], 58)
            for line in remaining:
                print(f"│      {line}")
        print(f"╰─────────────────────────────────────────────────────────────╯\n")

    def show_tool_start(self, tool_name: str, params: str = "") -> None:
        """Display a tool invocation with professional formatting."""
        if self.metrics_mode and self.tool_metrics:
            self.tool_metrics["current_tool_start"] = time.time()
            self.tool_metrics["calls"] += 1
        
        display_name = self._get_tool_display_name(tool_name, params)
        timestamp = datetime.now().strftime("%H:%M:%S") if (self.verbosity == "debug" or self.metrics_mode) else ""
        prefix = f"[{timestamp}] " if timestamp else ""
        
        # Show in execution context if in that phase
        if self.current_phase == AgentPhase.EXECUTING:
            print(f"{self.indent}│  → {prefix}{display_name}")
        else:
            print(f"{self.indent}⏺ {prefix}{display_name}")

    def show_tool_result(self, tool_name: str, params: str, result: Dict[str, Any]) -> None:
        """Display a tool result with clean formatting."""
        duration = None
        
        # Track timing and metrics
        if self.metrics_mode and self.tool_metrics and self.tool_metrics["current_tool_start"]:
            duration = time.time() - self.tool_metrics["current_tool_start"]
            self.tool_metrics["total_time"] += duration
            if tool_name not in self.tool_metrics["tool_times"]:
                self.tool_metrics["tool_times"][tool_name] = []
            self.tool_metrics["tool_times"][tool_name].append(duration)
            self.tool_metrics["current_tool_start"] = None
            
            # Track tokens and cost if available
            if "tokens" in result:
                self.tool_metrics["total_tokens"] += result["tokens"]
            if "cost" in result:
                self.tool_metrics["total_cost"] += result["cost"]
        
        result_text = self._format_tool_result(tool_name, params, result)
        timing_info = self._get_timing_display(duration) if duration is not None else ""
        
        if result.get("success"):
            if self.current_phase == AgentPhase.EXECUTING:
                print(f"{self.indent}│    ✓ {result_text}{timing_info}")
            else:
                print(f"{self.indent}  ⎿ {result_text}{timing_info}")
        else:
            error_msg = self._format_error_message(result.get("error", "Operation failed"))
            if self.current_phase == AgentPhase.EXECUTING:
                print(f"{self.indent}│    ✗ {error_msg}")
            else:
                print(f"{self.indent}  ⎿ {error_msg}")

    def show_step_complete(self, step_num: int, description: str) -> None:
        """Mark a plan step as complete during execution."""
        if self.current_phase == AgentPhase.EXECUTING:
            print(f"{self.indent}│  ✓ Step {step_num}: {description}")

    def show_status(self, status: str, details: str = "") -> None:
        """Display status updates based on verbosity."""
        if self.verbosity != "minimal":
            if self.current_phase == AgentPhase.EXECUTING:
                prefix = f"{self.indent}│  "
            else:
                prefix = ""
            
            if details and self.verbosity in ["verbose", "debug"]:
                print(f"{prefix}📊 {status}: {details}")
            else:
                print(f"{prefix}📊 {status}")

    def show_progress(self, current: int, total: int, description: str = "") -> None:
        """Display a progress bar based on iterations."""
        if self.verbosity != "minimal":
            percentage = int((current / total) * 100) if total > 0 else 0
            bar = "█" * (percentage // 10) + "░" * (10 - percentage // 10)
            
            if self.current_phase == AgentPhase.EXECUTING:
                print(f"{self.indent}│  ⏳ [{bar}] {percentage}% {description}")
            else:
                print(f"{self.indent}⏳ [{bar}] {percentage}% {description}")

    def show_error(self, error: str, suggestion: str = "") -> None:
        """Display a user-friendly error message with optional suggestion."""
        if self.current_phase == AgentPhase.EXECUTING:
            print(f"{self.indent}│  ❌ {self._format_error_message(error)}")
            if suggestion:
                print(f"{self.indent}│     💡 {suggestion}")
        else:
            print(f"❌ {self._format_error_message(error)}")
            if suggestion:
                print(f"💡 Suggestion: {suggestion}")

    def show_success(self, message: str) -> None:
        """Display a success message."""
        self._end_current_phase()
        self.current_phase = AgentPhase.COMPLETE
        print(f"\n✅ {message}\n")

    def debug_log(self, message: str) -> None:
        """Display debug information when verbosity is debug."""
        if self.show_debug:
            if self.current_phase == AgentPhase.EXECUTING:
                print(f"{self.indent}│  🐛 DEBUG: {message}")
            else:
                print(f"🐛 DEBUG: {message}")

    # Internal formatting helpers ---------------------------------------------

    def _wrap_text(self, text: str, width: int) -> List[str]:
        """Wrap text to specified width."""
        words = text.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            word_length = len(word)
            if current_length + word_length + len(current_line) <= width:
                current_line.append(word)
                current_length += word_length
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]
                current_length = word_length
        
        if current_line:
            lines.append(" ".join(current_line))
        
        return lines if lines else [""]

    def _get_tool_display_name(self, tool_name: str, params: str) -> str:
        """Map a tool name to a user-friendly display representation."""
        name_map = {
            "str_replace_editor": "Edit",
            "bash": "Bash",
            "grep_search": "Search",
            "glob_search": "Find",
            "list_directory": "List",
            "web_search": "WebSearch",
            "web_fetch": "WebFetch",
            "todo_write": "TodoWrite",
            "task_agent": "TaskAgent",
            "notebook_edit": "NotebookEdit",
            "update_progress_md": "UpdateProgress",
            "ask_user_step": "AskUser",
            "create_summary": "CreateSummary",
            "multi_edit": "MultiEdit",
            "git_operations": "Git",
            "advanced_file_ops": "FileOps",
            "performance_monitor": "Monitor",
        }
        display_name = name_map.get(tool_name, tool_name.replace("_", " ").title())
        if params:
            if len(params) > 50:
                params = params[:47] + "..."
            return f"{display_name}({params})"
        return f"{display_name}()"

    def _format_tool_result(self, tool_name: str, params: str, result: Dict[str, Any]) -> str:
        """Format tool results in a user-friendly way."""
        if tool_name == "str_replace_editor":
            operation = result.get("operation", "edit")
            if operation == "create":
                return "Created file"
            elif operation == "str_replace":
                changes = result.get("changes", 1)
                return f"Made {changes} replacement{'s' if changes != 1 else ''}"
            elif operation in ["view", "view_range"]:
                lines = result.get("line_count", 0)
                if lines == 0:
                    return "File is empty"
                return f"Read {lines} line{'s' if lines != 1 else ''}"
            else:
                return "File modified"
        elif tool_name == "bash":
            if result.get("stdout"):
                output_lines = len(result["stdout"].split('\n'))
                return f"Command executed ({output_lines} lines output)"
            else:
                return "Command executed successfully"
        elif tool_name == "grep_search":
            matches = result.get("matches", 0)
            if matches == 0:
                return "No matches found"
            return f"Found {matches} match{'es' if matches != 1 else ''}"
        elif tool_name == "glob_search":
            files = result.get("files", [])
            return f"Found {len(files)} file{'s' if len(files) != 1 else ''}"
        elif tool_name == "list_directory":
            items = result.get("items", [])
            return f"Listed {len(items)} item{'s' if len(items) != 1 else ''}"
        elif tool_name == "web_search":
            results = result.get("results", [])
            return f"Found {len(results)} search result{'s' if len(results) != 1 else ''}"
        elif tool_name == "web_fetch":
            length = result.get("content_length", 0)
            return f"Fetched content ({length} characters)"
        elif tool_name == "todo_write":
            total = result.get("total_todos", 0)
            return f"Updated {total} todo{'s' if total != 1 else ''}"
        elif tool_name == "task_agent":
            return "Sub-agent completed task"
        elif tool_name == "multi_edit":
            edits = result.get("edits_made", 0)
            return f"Made {edits} edit{'s' if edits != 1 else ''}"
        elif tool_name == "git_operations":
            operation = result.get("operation", "operation")
            return f"Git {operation} completed"
        elif tool_name == "advanced_file_ops":
            operation = result.get("operation", "operation")
            files = result.get("files_affected", 1)
            return f"{operation.title()} on {files} file{'s' if files != 1 else ''}"
        elif tool_name == "performance_monitor":
            command = result.get("command", "monitor")
            return f"Performance {command} completed"
        else:
            return str(result.get("output", "Operation completed"))[:100]

    def _format_error_message(self, error: str) -> str:
        """Convert common error patterns into friendly messages."""
        error = str(error)
        if "No such file or directory" in error:
            return "File not found"
        elif "Permission denied" in error:
            return "Permission denied - check file permissions"
        elif "Command not found" in error:
            return "Command not available"
        elif "Connection refused" in error or "Network" in error:
            return "Network connection failed"
        elif "Timeout" in error.lower():
            return "Operation timed out"
        elif len(error) > 100:
            return error[:97] + "..."
        else:
            return error

    def _get_timing_display(self, duration: float) -> str:
        """Format timing information for display."""
        if self.metrics_mode or self.verbosity in ["verbose", "debug"]:
            if duration < 1:
                return f" ({duration*1000:.0f}ms)"
            else:
                return f" ({duration:.1f}s)"
        return ""

    # Performance and metrics methods -----------------------------------------

    def show_session_metrics(self) -> None:
        """Display comprehensive session metrics."""
        if not self.metrics_mode or not self.tool_metrics or self.verbosity == "minimal":
            return
        
        self._end_current_phase()
        session_duration = time.time() - self.session_start_time
        
        print("\n╔══════════════════════════════════════════════════════════════╗")
        print("║  📊 Session Metrics                                          ║")
        print("╚══════════════════════════════════════════════════════════════╝")
        print(f"   Duration: {self._format_duration(session_duration)}")
        print(f"   Tool calls: {self.tool_metrics['calls']}")
        print(f"   Total tokens: {self.tool_metrics['total_tokens']:,}")
        
        if self.tool_metrics['total_cost'] > 0:
            print(f"   Total cost: ${self.tool_metrics['total_cost']:.4f}")
        if self.tool_metrics['total_time'] > 0:
            print(f"   Tool execution time: {self._format_duration(self.tool_metrics['total_time'])}")
        
        # Show phase breakdown
        if self.tool_metrics['phase_times']:
            self._show_phase_breakdown()
        
        # Show slowest tools if in verbose mode
        if (self.verbosity in ["verbose", "debug"]) and self.tool_metrics['tool_times']:
            self._show_tool_performance()
        
        print()

    def show_task_breakdown(self, agent_state) -> None:
        """Display decomposed tasks, active tasks, and completed tasks."""
        if self.verbosity == "minimal":
            return
        
        print("\n╔══════════════════════════════════════════════════════════════╗")
        print("║  📋 Task Breakdown                                           ║")
        print("╚══════════════════════════════════════════════════════════════╝")
        
        # Show current todos
        if hasattr(agent_state, 'current_todos') and agent_state.current_todos:
            # Separate todos by status
            in_progress_todos = [todo for todo in agent_state.current_todos.values() if todo.get("status") == "in_progress"]
            pending_todos = [todo for todo in agent_state.current_todos.values() if todo.get("status") == "pending"]
            completed_todos = [todo for todo in agent_state.current_todos.values() if todo.get("status") == "completed"]
            
            if in_progress_todos:
                print("   🔄 Active Tasks:")
                for todo in in_progress_todos:
                    priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(todo.get("priority"), "")
                    print(f"     🔄 {todo.get('content', '')} {priority_emoji}")
            
            if pending_todos:
                print("   ☐ Pending Tasks:")
                for todo in pending_todos:
                    priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(todo.get("priority"), "")
                    print(f"     ☐ {todo.get('content', '')} {priority_emoji}")
            
            if completed_todos:
                print("   ✅ Completed Tasks:")
                # Show only recent completed tasks
                for todo in completed_todos[-5:]:
                    priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(todo.get("priority"), "")
                    print(f"     ☒ {todo.get('content', '')} {priority_emoji}")
            
            # Show summary
            total = len(agent_state.current_todos)
            print(f"   📊 Summary: {len(completed_todos)} completed, {len(in_progress_todos)} active, {len(pending_todos)} pending ({total} total)")
        
        # Show sub-agent tasks  
        if hasattr(agent_state, 'sub_agent_results') and agent_state.sub_agent_results:
            print("   🤖 Sub-Agent Tasks:")
            for i, sub_result in enumerate(agent_state.sub_agent_results):
                status = "✅" if sub_result.get("success") else "❌"
                task_desc = sub_result.get("task", f"Sub-task {i+1}")[:50]
                print(f"     {status} {task_desc}")
        
        # Show progress entries
        if hasattr(agent_state, 'progress') and agent_state.progress:
            active_tasks = [p for p in agent_state.progress if p.status == "in_progress"]
            completed_tasks = [p for p in agent_state.progress if p.status == "completed"]
            
            if active_tasks:
                print("   🔄 Active Operations:")
                for task in active_tasks[-3:]:  # Show last 3
                    print(f"     • {task.action}: {task.details[:50]}...")
            
            if completed_tasks and self.verbosity in ["verbose", "debug"]:
                print("   ✅ Recently Completed:")
                for task in completed_tasks[-3:]:  # Show last 3
                    print(f"     • {task.action}")
        
        print()

    def _show_phase_breakdown(self) -> None:
        """Show time spent in each agent phase."""
        print("\n   Phase breakdown:")
        phase_icons = {
            "thinking": "🧠",
            "planning": "📋",
            "executing": "⚡"
        }
        
        for phase, times in self.tool_metrics['phase_times'].items():
            total_time = sum(times)
            avg_time = total_time / len(times)
            icon = phase_icons.get(phase, "⏱️")
            print(f"     {icon} {phase.title()}: {self._format_duration(total_time)} total, "
                  f"{self._format_duration(avg_time)} avg ({len(times)}x)")

    def _show_tool_performance(self) -> None:
        """Show detailed tool performance breakdown."""
        tool_avg_times = {}
        for tool, times in self.tool_metrics['tool_times'].items():
            tool_avg_times[tool] = sum(times) / len(times)
        
        sorted_tools = sorted(tool_avg_times.items(), key=lambda x: x[1], reverse=True)
        print("\n   Tool performance:")
        for tool, avg_time in sorted_tools[:5]:  # Show top 5 slowest
            count = len(self.tool_metrics['tool_times'][tool])
            total_time = sum(self.tool_metrics['tool_times'][tool])
            display_name = self._get_tool_display_name(tool, "").split("(")[0]
            print(f"     {display_name}: {self._format_duration(avg_time)} avg, "
                  f"{self._format_duration(total_time)} total ({count}x)")

    def _format_duration(self, seconds: float) -> str:
        """Format duration in human-readable format."""
        if seconds < 1:
            return f"{seconds*1000:.0f}ms"
        elif seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            secs = seconds % 60
            return f"{minutes}m {secs:.0f}s"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}h {minutes}m"

    def update_token_cost(self, tokens: int, cost: float = 0.0) -> None:
        """Update token and cost tracking from external sources."""
        if self.metrics_mode and self.tool_metrics:
            self.tool_metrics["total_tokens"] += tokens
            self.tool_metrics["total_cost"] += cost

    def get_metrics_summary(self) -> Dict[str, Any]:
        """Return current metrics as a dictionary."""
        if not self.metrics_mode or not self.tool_metrics:
            return {"metrics_mode": False, "message": "Metrics tracking is disabled"}
        
        session_duration = time.time() - self.session_start_time
        return {
            "metrics_mode": True,
            "session_duration_seconds": round(session_duration, 1),
            "tool_calls": self.tool_metrics["calls"],
            "total_tokens": self.tool_metrics["total_tokens"],
            "total_cost": self.tool_metrics["total_cost"],
            "total_tool_time_seconds": round(self.tool_metrics["total_time"], 1),
            "phase_breakdown": {
                phase: {
                    "occurrences": len(times),
                    "total_time_seconds": round(sum(times), 1),
                    "avg_time_seconds": round(sum(times) / len(times), 2)
                }
                for phase, times in self.tool_metrics.get("phase_times", {}).items()
            },
            "tool_performance": {
                tool: {
                    "calls": len(times),
                    "total_time_seconds": round(sum(times), 1),
                    "avg_time_seconds": round(sum(times) / len(times), 2)
                }
                for tool, times in self.tool_metrics["tool_times"].items()
            }
        }

    def enable_metrics_mode(self) -> None:
        """Enable metrics tracking mode."""
        if not self.metrics_mode:
            self.metrics_mode = True
            self.session_start_time = time.time()
            self.tool_metrics = {
                "calls": 0,
                "total_time": 0.0,
                "total_tokens": 0,
                "total_cost": 0.0,
                "tool_times": {},
                "current_tool_start": None,
                "phase_times": {}
            }

    def disable_metrics_mode(self) -> None:
        """Disable metrics tracking mode."""
        self.metrics_mode = False
        self.tool_metrics = None
