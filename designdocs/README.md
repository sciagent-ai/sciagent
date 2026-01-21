# SWE Agent Framework

A modular, extensible Software Engineering Agent framework built on the patterns from Claude Code and similar tools.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           AGENT FRAMEWORK                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                │
│  │   LLM.py    │    │  TOOLS.py   │    │  STATE.py   │                │
│  │             │    │             │    │             │                │
│  │ - LiteLLM   │    │ - Registry  │    │ - Context   │                │
│  │ - Messages  │    │ - BaseTool  │    │ - Todos     │                │
│  │ - Streaming │    │ - Execution │    │ - Persist   │                │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘                │
│         │                  │                  │                        │
│         └──────────────────┼──────────────────┘                        │
│                            │                                           │
│                     ┌──────▼──────┐                                    │
│                     │  AGENT.py   │                                    │
│                     │             │                                    │
│                     │ Main Loop:  │                                    │
│                     │ Think→Act→  │                                    │
│                     │ Observe     │                                    │
│                     └──────┬──────┘                                    │
│                            │                                           │
│                     ┌──────▼──────┐                                    │
│                     │ SUBAGENT.py │                                    │
│                     │             │                                    │
│                     │ - Spawning  │                                    │
│                     │ - Isolation │                                    │
│                     │ - Parallel  │                                    │
│                     └─────────────┘                                    │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## Installation

```bash
pip install litellm requests
```

Set your API key:
```bash
export ANTHROPIC_API_KEY="your-key"
# or
export OPENAI_API_KEY="your-key"
```

## Quick Start

### One-Shot Task

```python
from swe_agent import run_task

result = run_task("Create a Python script that prints hello world")
print(result)
```

### Interactive Mode

```python
from swe_agent import create_agent

agent = create_agent()
agent.run_interactive()
```

### With Sub-Agents

```python
from swe_agent import create_agent_with_subagents

agent = create_agent_with_subagents()
agent.run("Research this codebase and write comprehensive tests")
```

### CLI Usage

```bash
# Single task
python main.py "Create a REST API with FastAPI"

# Interactive mode
python main.py --interactive

# Use different model
python main.py --model openai/gpt-4o "Analyze this code"

# Enable sub-agents
python main.py --subagents "Research and document this project"

# Load custom tools
python main.py --load-tools ./my_tools.py "Use my custom tool"
```

## Adding Custom Tools

### Method 1: Subclass BaseTool

```python
from swe_agent import BaseTool, ToolResult

class MyTool(BaseTool):
    name = "my_tool"
    description = "Does something useful"
    parameters = {
        "type": "object",
        "properties": {
            "input": {"type": "string", "description": "Input value"}
        },
        "required": ["input"]
    }
    
    def execute(self, input: str) -> ToolResult:
        result = do_something(input)
        return ToolResult(success=True, output=result)
```

### Method 2: Use @tool Decorator

```python
from swe_agent import tool

@tool(name="calculate", description="Perform math calculations")
def calculate(expression: str) -> str:
    return str(eval(expression))  # Use safe eval in production!
```

### Method 3: Wrap Existing Functions

```python
from swe_agent import FunctionTool

def my_function(x: int, y: int) -> int:
    return x + y

my_tool = FunctionTool(my_function, description="Add two numbers")
```

### Register Tools

```python
from swe_agent import create_default_registry

registry = create_default_registry()
registry.register(MyTool())
registry.register(calculate)

agent = create_agent(tools=registry)
```

## State Management

The framework provides three layers of state:

| Layer | Scope | Persistence | Use |
|-------|-------|-------------|-----|
| Context Window | Per-turn | Ephemeral | LLM messages |
| File System | Session | Session-persistent | Code, results |
| State Manager | Cross-session | Permanent | Session recovery |

### Save/Resume Sessions

```python
from swe_agent import create_agent

agent = create_agent()
agent.run("Start a complex task...")

# Save session
session_id = agent.save_session()

# Later: resume
agent2 = create_agent()
agent2.load_session(session_id)
agent2.run("Continue where we left off")
```

## Sub-Agent System

Sub-agents are isolated agent instances with their own context windows.

### Built-in Sub-Agents

| Name | Purpose | Tools |
|------|---------|-------|
| `researcher` | Explore and understand code | view, bash (read-only) |
| `reviewer` | Code review | view, bash |
| `test_writer` | Write tests | view, write_file, bash |
| `general` | Complex tasks | all |

### Using Sub-Agents

```python
from swe_agent import create_agent_with_subagents

agent = create_agent_with_subagents()

# The agent can now delegate tasks
agent.run("""
1. Use the researcher sub-agent to understand the codebase structure
2. Use the test_writer sub-agent to create tests for the main module
3. Review the tests and make improvements
""")
```

### Custom Sub-Agents

```python
from swe_agent.subagent import SubAgentConfig, SubAgentRegistry

config = SubAgentConfig(
    name="security_auditor",
    description="Audit code for security vulnerabilities",
    system_prompt="You are a security expert. Find vulnerabilities...",
    allowed_tools=["view", "bash"],
    model="anthropic/claude-sonnet-4-20250514"
)

registry = SubAgentRegistry()
registry.register(config)
```

## Supported Models

Via LiteLLM, you can use:

- **Anthropic**: `anthropic/claude-sonnet-4-20250514`, `anthropic/claude-opus-4-20250514`
- **OpenAI**: `openai/gpt-4o`, `openai/gpt-4-turbo`, `openai/o1`
- **Google**: `gemini/gemini-pro`, `gemini/gemini-1.5-pro`
- **Local**: `ollama/llama3`, `ollama/codellama`
- **Azure**: `azure/gpt-4`

```python
from swe_agent import create_agent

# Use different providers
agent = create_agent(model="openai/gpt-4o")
agent = create_agent(model="ollama/codellama")
```

## File Structure

```
swe_agent/
├── __init__.py      # Package exports
├── llm.py           # LLM interface (LiteLLM wrapper)
├── tools.py         # Tool system (registry, execution)
├── state.py         # State management (context, todos, persistence)
├── agent.py         # Core agent loop
├── subagent.py      # Sub-agent spawning and orchestration
├── example_tools.py # Example custom tools
└── main.py          # CLI entry point
```

## How It Works

### The Agent Loop

```python
while has_tool_calls and iteration < max_iterations:
    # 1. THINK: Send context to LLM
    response = llm.chat(messages, tools=tool_schemas)
    
    # 2. ACT: Execute any tool calls
    if response.has_tool_calls:
        for tool_call in response.tool_calls:
            result = tools.execute(tool_call.name, **tool_call.arguments)
            messages.append(tool_result_message)
    
    # 3. OBSERVE: Results feed back into next iteration
    else:
        # No tool calls = done
        return response.content
```

### Memory Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           MEMORY LAYERS                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  SHORT-TERM (Context Window)                                            │
│  ├── System prompt                                                      │
│  ├── User messages                                                      │
│  ├── Assistant messages                                                 │
│  ├── Tool calls & results                                               │
│  └── Compressed when approaching limit                                  │
│                                                                         │
│  MEDIUM-TERM (File System)                                              │
│  ├── Created files (.py, .json, .md)                                    │
│  ├── Intermediate results                                               │
│  └── Session-persistent, cleared on new session                         │
│                                                                         │
│  LONG-TERM (State Manager)                                              │
│  ├── Saved sessions (.agent_states/*.json)                              │
│  ├── Todo list state                                                    │
│  └── Cross-session persistent                                           │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## Extending the Framework

### Custom Agent Loop

```python
from swe_agent import AgentLoop, AgentConfig

class MyAgent(AgentLoop):
    def _single_step(self):
        # Custom step logic
        response = super()._single_step()
        
        # Add custom processing
        self.log_step(response)
        
        return response
```

### Callbacks

```python
agent = create_agent()

@agent.on_tool_start
def log_tool(name, args):
    print(f"Starting: {name}")

@agent.on_tool_end
def log_result(name, result):
    print(f"Finished: {name} -> {result.success}")

@agent.on_response
def log_response(content):
    print(f"Agent says: {content[:100]}...")
```

## License

MIT
