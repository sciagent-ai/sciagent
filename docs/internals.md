---
theme: jekyll-theme-minimal
layout: page
title: Internal APIs & Architecture
permalink: /internals/
---

# SCI Agent – Internal APIs & Architecture

This guide documents the internal architecture, APIs, and extension points for developers who want to understand, modify, or extend SCI Agent.

---

## System Architecture

### Core Components

```
┌─────────────────────┐
│   CLI Interface     │
├─────────────────────┤
│   Task Manager      │
├─────────────────────┤
│   Agent Engine      │
├─────────────────────┤
│   Tool Registry     │
├─────────────────────┤
│   Model Interface   │
├─────────────────────┤
│   State Manager     │
└─────────────────────┘
```

### Module Structure

```
sciagent/
├── __main__.py              # CLI entry point
├── agent.py                 # Core agent implementation
├── config.py               # Configuration management
├── tools/                  # Tool implementations
│   ├── __init__.py
│   ├── base.py            # Base tool class
│   ├── file_ops.py        # File operation tools
│   ├── execution.py       # Shell execution tools
│   ├── search.py          # Search and analysis tools
│   └── web.py             # Web interaction tools
├── models/                 # LLM interface layer
│   ├── __init__.py
│   ├── base.py            # Base model interface
│   ├── openai.py          # OpenAI implementation
│   ├── anthropic.py       # Anthropic implementation
│   └── litellm.py         # LiteLLM wrapper
├── skills/                 # Skill routing system
│   ├── __init__.py
│   ├── base.py            # Base skill class
│   ├── registry.py        # Skill registration
│   └── definitions/       # Skill implementations
├── state/                  # State management
│   ├── __init__.py
│   ├── manager.py         # State persistence
│   └── serialization.py   # State serialization
└── utils/                  # Utility modules
    ├── __init__.py
    ├── logging.py         # Logging setup
    ├── validation.py      # Input validation
    └── formatting.py      # Output formatting
```

---

## Core APIs

### Agent Interface

```python
from sciagent import SCIAgent, Config

class SCIAgent:
    def __init__(self, config: Config, **kwargs):
        """Initialize the agent with configuration."""
        
    def execute_task(self, task: str, **kwargs) -> dict:
        """Execute a task and return results."""
        
    def resume_task(self, task_id: str) -> dict:
        """Resume a previously interrupted task."""
        
    def get_status(self) -> dict:
        """Get current agent status."""
        
    def stop(self) -> None:
        """Stop the current task execution."""
```

### Configuration API

```python
from sciagent import Config

class Config:
    def __init__(
        self,
        model: str = "gpt-4o",
        models: List[str] = None,
        max_iterations: int = 50,
        temperature: float = 0.1,
        max_tokens: int = 4096,
        working_dir: str = ".",
        enable_web: bool = True,
        enable_notebooks: bool = True,
        enable_skills: bool = True,
        progress_tracking: bool = True,
        debug: bool = False,
        **kwargs
    ):
        """Initialize configuration with parameters."""
        
    @classmethod
    def from_file(cls, path: str) -> 'Config':
        """Load configuration from file."""
        
    @classmethod
    def from_env(cls) -> 'Config':
        """Load configuration from environment variables."""
        
    def merge(self, other: 'Config') -> 'Config':
        """Merge with another configuration."""
        
    def validate(self) -> bool:
        """Validate configuration parameters."""
```

---

## Tool System

### Base Tool Interface

```python
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

class BaseTool(ABC):
    """Base class for all tools."""
    
    name: str
    description: str
    parameters: Dict[str, Any]
    
    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the tool with given parameters."""
        
    def validate_parameters(self, **kwargs) -> bool:
        """Validate input parameters."""
        
    def get_schema(self) -> Dict[str, Any]:
        """Get JSON schema for tool parameters."""
```

### Tool Registration

```python
from sciagent.tools import ToolRegistry

class ToolRegistry:
    def register(self, tool_class: type) -> None:
        """Register a tool class."""
        
    def get_tool(self, name: str) -> BaseTool:
        """Get tool instance by name."""
        
    def list_tools(self) -> List[str]:
        """List all registered tool names."""
        
    def filter_tools(self, criteria: Dict[str, Any]) -> List[BaseTool]:
        """Filter tools by criteria."""

# Global registry instance
registry = ToolRegistry()

# Register a custom tool
@registry.tool
class CustomTool(BaseTool):
    name = "custom_tool"
    description = "Custom tool implementation"
    
    def execute(self, **kwargs):
        return {"status": "success"}
```

### Built-in Tools

#### File Operations

```python
from sciagent.tools.file_ops import (
    StrReplaceEditor,
    MultiEdit,
    GlobSearch,
    ListDirectory,
    AdvancedFileOps
)

# Create and edit files
editor = StrReplaceEditor()
result = editor.execute(
    command="create",
    path="/path/to/file.py",
    file_text="print('Hello, World!')"
)

# Search for files
search = GlobSearch()
files = search.execute(pattern="*.py", path="/project")

# List directory contents
lister = ListDirectory()
contents = lister.execute(path="/project")
```

#### Execution Tools

```python
from sciagent.tools.execution import BashTool, GitOperations

# Execute shell commands
bash = BashTool()
result = bash.execute(command="ls -la", timeout=30)

# Git operations
git = GitOperations()
status = git.execute(operation="status")
commit = git.execute(
    operation="commit",
    message="Update documentation",
    files=["docs/"]
)
```

#### Search Tools

```python
from sciagent.tools.search import GrepSearch, WebSearch, WebFetch

# Search within files
grep = GrepSearch()
matches = grep.execute(
    pattern="class.*Agent",
    path="/project",
    file_types=["py"]
)

# Web search
web_search = WebSearch()
results = web_search.execute(query="machine learning papers 2024")

# Fetch web content
web_fetch = WebFetch()
content = web_fetch.execute(
    url="https://example.com/article",
    extract_text=True
)
```

---

## Model Interface

### Base Model Interface

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class BaseModel(ABC):
    """Base class for LLM interfaces."""
    
    def __init__(self, model_name: str, **kwargs):
        self.model_name = model_name
        
    @abstractmethod
    def generate(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate response from the model."""
        
    @abstractmethod
    def count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        
    def supports_tools(self) -> bool:
        """Check if model supports tool calling."""
        return False
        
    def max_context_length(self) -> int:
        """Get maximum context length."""
        return 4096
```

### Model Implementation Example

```python
from sciagent.models.base import BaseModel
import openai

class OpenAIModel(BaseModel):
    def __init__(self, model_name: str, api_key: str, **kwargs):
        super().__init__(model_name, **kwargs)
        self.client = openai.OpenAI(api_key=api_key)
        
    def generate(self, messages, tools=None, **kwargs):
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            tools=tools,
            **kwargs
        )
        return {
            "content": response.choices[0].message.content,
            "tool_calls": response.choices[0].message.tool_calls,
            "usage": response.usage.model_dump()
        }
        
    def count_tokens(self, text: str) -> int:
        # Token counting implementation
        return len(text) // 4  # Rough approximation
```

### Model Registry

```python
from sciagent.models import ModelRegistry

registry = ModelRegistry()

# Register custom model
registry.register("custom-model", CustomModel)

# Get model instance
model = registry.get_model("gpt-4o", api_key="...")

# List available models
models = registry.list_models()
```

---

## Skills System

### Base Skill Interface

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseSkill(ABC):
    """Base class for skills."""
    
    name: str
    description: str
    triggers: List[str]
    tools: List[str]
    dependencies: List[str] = []
    
    @abstractmethod
    def can_handle(self, task: str) -> float:
        """Return confidence score (0.0-1.0) for handling task."""
        
    def setup(self) -> bool:
        """Setup skill dependencies and resources."""
        return True
        
    def teardown(self) -> None:
        """Clean up skill resources."""
        pass
        
    def get_tools(self) -> List[str]:
        """Get list of required tools."""
        return self.tools
```

### Skill Implementation Example

```python
from sciagent.skills.base import BaseSkill

class DataScienceSkill(BaseSkill):
    name = "data_science"
    description = "Data analysis and visualization tasks"
    triggers = ["analyze", "statistics", "visualization", "pandas", "numpy"]
    tools = ["notebook_edit", "str_replace_editor", "bash"]
    dependencies = ["pandas", "numpy", "matplotlib"]
    
    def can_handle(self, task: str) -> float:
        task_lower = task.lower()
        score = 0.0
        
        for trigger in self.triggers:
            if trigger in task_lower:
                score += 0.2
                
        if "dataset" in task_lower or "data" in task_lower:
            score += 0.3
            
        return min(score, 1.0)
    
    def setup(self) -> bool:
        try:
            import pandas
            import numpy
            import matplotlib
            return True
        except ImportError:
            return False
```

### Skill Registry

```python
from sciagent.skills import SkillRegistry

registry = SkillRegistry()

# Register skill
registry.register(DataScienceSkill())

# Route task to best skill
best_skill = registry.route_task("Analyze this dataset")

# Get all skills for a task
skills = registry.get_applicable_skills("Create a web application")
```

---

## State Management

### State Interface

```python
from sciagent.state import StateManager
from dataclasses import dataclass
from typing import Any, Dict, Optional

@dataclass
class TaskState:
    task_id: str
    task_description: str
    current_iteration: int
    max_iterations: int
    messages: List[Dict[str, Any]]
    tool_calls: List[Dict[str, Any]]
    results: Dict[str, Any]
    metadata: Dict[str, Any]

class StateManager:
    def save_state(self, state: TaskState) -> bool:
        """Save task state to persistent storage."""
        
    def load_state(self, task_id: str) -> Optional[TaskState]:
        """Load task state from storage."""
        
    def list_states(self) -> List[str]:
        """List all saved task IDs."""
        
    def delete_state(self, task_id: str) -> bool:
        """Delete saved state."""
        
    def cleanup_old_states(self, max_age_days: int = 30) -> int:
        """Clean up old state files."""
```

### State Serialization

```python
from sciagent.state.serialization import StateSerializer

class StateSerializer:
    @staticmethod
    def serialize(state: TaskState) -> bytes:
        """Serialize state to bytes."""
        
    @staticmethod
    def deserialize(data: bytes) -> TaskState:
        """Deserialize state from bytes."""
        
    @staticmethod
    def compress(data: bytes) -> bytes:
        """Compress serialized data."""
        
    @staticmethod
    def decompress(data: bytes) -> bytes:
        """Decompress serialized data."""
```

---

## Extension Points

### Plugin System

```python
from sciagent.plugins import Plugin, PluginManager

class Plugin(ABC):
    """Base class for plugins."""
    
    name: str
    version: str
    
    @abstractmethod
    def initialize(self, agent: 'SCIAgent') -> None:
        """Initialize plugin with agent instance."""
        
    @abstractmethod
    def finalize(self) -> None:
        """Clean up plugin resources."""

class PluginManager:
    def register_plugin(self, plugin: Plugin) -> None:
        """Register a plugin."""
        
    def load_plugins_from_directory(self, path: str) -> None:
        """Load plugins from directory."""
        
    def get_plugin(self, name: str) -> Optional[Plugin]:
        """Get plugin by name."""
```

### Hook System

```python
from sciagent.hooks import HookManager, Hook
from typing import Callable, Any

class Hook:
    """Base class for hooks."""
    
    def before_task(self, task: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Called before task execution starts."""
        return {"task": task, "config": config}
        
    def after_task(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Called after task execution completes."""
        return result
        
    def before_iteration(self, iteration: int) -> None:
        """Called before each iteration."""
        pass
        
    def after_iteration(self, iteration: int, result: Dict[str, Any]) -> None:
        """Called after each iteration."""
        pass
        
    def on_tool_call(self, tool_name: str, parameters: Dict[str, Any]) -> None:
        """Called when a tool is executed."""
        pass

class HookManager:
    def register_hook(self, hook: Hook) -> None:
        """Register a hook."""
        
    def trigger(self, event: str, *args, **kwargs) -> Any:
        """Trigger all hooks for an event."""
```

---

## Error Handling

### Exception Hierarchy

```python
class SCIAgentException(Exception):
    """Base exception for SCI Agent."""
    pass

class ConfigurationError(SCIAgentException):
    """Configuration-related errors."""
    pass

class ToolExecutionError(SCIAgentException):
    """Tool execution failures."""
    pass

class ModelError(SCIAgentException):
    """LLM model-related errors."""
    pass

class StateError(SCIAgentException):
    """State management errors."""
    pass

class SkillError(SCIAgentException):
    """Skill system errors."""
    pass
```

### Error Recovery

```python
from sciagent.utils.recovery import ErrorRecovery

class ErrorRecovery:
    @staticmethod
    def handle_tool_error(error: ToolExecutionError, context: Dict[str, Any]) -> bool:
        """Attempt to recover from tool execution error."""
        
    @staticmethod
    def handle_model_error(error: ModelError, context: Dict[str, Any]) -> bool:
        """Attempt to recover from model error."""
        
    @staticmethod
    def should_retry(error: Exception, attempt: int) -> bool:
        """Determine if operation should be retried."""
```

---

## Testing Framework

### Test Utilities

```python
from sciagent.testing import MockAgent, MockTool, TestConfig

class TestAgent:
    def setUp(self):
        self.config = TestConfig(
            model="mock-model",
            max_iterations=5,
            enable_web=False
        )
        self.agent = MockAgent(self.config)
        
    def test_task_execution(self):
        result = self.agent.execute_task("Test task")
        self.assertTrue(result["success"])
        
    def test_tool_execution(self):
        tool = MockTool()
        result = tool.execute(test_param="value")
        self.assertEqual(result["status"], "success")
```

### Mocking Framework

```python
from sciagent.testing.mocks import MockModel, MockTool

# Mock model responses
mock_model = MockModel()
mock_model.set_response("This is a mock response")

# Mock tool execution
mock_tool = MockTool("test_tool")
mock_tool.set_result({"status": "success", "output": "test"})
```

---

## Performance Monitoring

### Metrics Collection

```python
from sciagent.monitoring import MetricsCollector, PerformanceMonitor

class MetricsCollector:
    def record_token_usage(self, model: str, tokens: int) -> None:
        """Record token usage for a model."""
        
    def record_tool_execution(self, tool: str, duration: float) -> None:
        """Record tool execution time."""
        
    def record_iteration(self, iteration: int, duration: float) -> None:
        """Record iteration timing."""
        
    def get_summary(self) -> Dict[str, Any]:
        """Get metrics summary."""

class PerformanceMonitor:
    def __enter__(self):
        self.start_time = time.time()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        self.record_duration(duration)
```

### Profiling

```python
from sciagent.monitoring.profiler import AgentProfiler

# Profile agent execution
with AgentProfiler() as profiler:
    result = agent.execute_task("Complex task")

# Get profiling results
profile_data = profiler.get_results()
profiler.save_report("profile.html")
```

---

This documentation covers the internal architecture and APIs for extending and customizing SCI Agent. For usage examples and configuration options, see the quickstart and advanced guides.
