# SCI Agent with Multi-LLM Support

A comprehensive AI-powered scientific computing and engineering agent that can perform complex scientific and engineering tasks using multiple LLM providers through LiteLLM integration. This agent supports OpenAI, Anthropic, Google (Gemini), xAI (Grok), Mistral, Azure OpenAI, and many other providers with intelligent fallback capabilities and advanced reasoning support.

## Features

🤖 **Multi-LLM Support**: Works with OpenAI (GPT), Anthropic (Claude), Google (Gemini), xAI (Grok), Mistral, Azure OpenAI, and 100+ other models via LiteLLM
🧠 **Advanced Reasoning**: Supports reasoning capabilities across providers with configurable effort levels
🔧 **Comprehensive Toolset**: Built-in tools for file operations, web search, bash execution, notebook editing, and more  
📊 **Progress Tracking**: Automatic progress reporting with markdown summaries
🔄 **Resume Capability**: Can pause and resume long-running tasks
🌐 **Web Integration**: Search capabilities and web content fetching
📋 **Sub-Agent Spawning**: Can create specialized sub-agents for complex subtasks
🛡️ **Error Recovery**: Intelligent error handling with model fallback
💾 **State Persistence**: Maintains state between sessions for complex projects

## Quick Start

### Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd sciagent
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your API keys (choose one or more):
```bash
# OpenAI
export OPENAI_API_KEY=sk-...

# Anthropic
export ANTHROPIC_API_KEY=sk-ant-...

# Mistral  
export MISTRAL_API_KEY=sk-...

# xAI (Grok)
export XAI_API_KEY=xai-...

# Azure OpenAI
export AZURE_API_KEY=...
export AZURE_API_BASE="https://<your-resource>.openai.azure.com"

# Brave Search (recommended for enhanced web search)
export BRAVE_SEARCH_API_KEY=BSA-...
```

### Basic Usage

Run a simple task:
```bash
python -m sciagent "Create a simple Python calculator script"
```

Use a specific model:
```bash
python -m sciagent --model gpt-4o-mini "Analyze this codebase and create documentation"
```

Use model fallback chain:
```bash
python -m sciagent \
  --model claude-3-5-sonnet-20241022 \
  --models gpt-4o-mini,mistral/mistral-large-latest \
  "Refactor this code for better performance"
```

## Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `task` | Task description (or enter interactively) | - |
| `--working-dir` | Working directory | `.` |
| `--max-iterations` | Maximum iterations | `50` |
| `--model` | Primary LLM model | `claude-3-5-sonnet-20241022` |
| `--models` | Comma-separated fallback models | - |
| `--api-key` | API key (overrides env vars) | - |
| `--debug` | Enable debug mode | `False` |
| `--resume` | Resume task by ID | - |
| `--no-progress` | Disable progress.md tracking | `False` |
| `--no-web` | Disable web tools | `False` |
| `--no-notebooks` | Disable notebook tools | `False` |
| `--no-skills` | Disable skill system for maximum speed | `False` |
| `--reasoning-effort` | Reasoning effort level (none/low/medium/high) | `medium` |
| `--temperature` | Model temperature (0.0-1.0) | `0.1` |

## Supported Models

### OpenAI
- `gpt-5.2`, `gpt-5.1`, `gpt-5` (with reasoning)
- `gpt-5.2-codex`, `gpt-5.1-codex` (specialized for coding)
- `gpt-4o`, `gpt-4o-mini`, `gpt-4-turbo`, `gpt-4`
- `gpt-3.5-turbo`

### Anthropic
- `claude-sonnet-4-5-20250929`, `claude-opus-4-5-20251101` (latest with reasoning)
- `claude-3-5-sonnet-20241022`, `claude-3-5-haiku-20241022`
- `claude-3-haiku-20240307`, `claude-3-opus-20240229`

### Google (Gemini)
- `gemini-3.0-flash-thinking-experimental`, `gemini-3.0-flash` (latest with thinking)
- `gemini-2.5-pro`, `gemini-2.5-flash`, `gemini-2.0-flash`
- `gemini-1.5-pro`, `gemini-1.5-flash`

### xAI (Grok)
- `grok-4.1-fast-reasoning`, `grok-4.1`, `grok-4` (with reasoning)
- `grok-3`, `grok-3-mini-beta`
- `grok-2`, `grok-2-vision`

### Mistral
- `mistral-large-latest`, `mistral-medium-latest`, `mistral-small-latest`
- `codestral` (specialized for coding)

### Azure OpenAI
- `azure/<deployment_name>`

And many more via [LiteLLM](https://docs.litellm.ai/docs/providers)!

## Architecture

```
sciagent/
├── main.py              # CLI entry point
├── config.py            # Configuration management
├── agent.py             # Core agent implementation
├── state.py             # State management
├── display.py           # Output formatting
├── tool_registry.py     # Dynamic tool discovery
├── base_tool.py         # Tool base class
└── tools/               # Tool implementations
    ├── core/            # Core tools (bash, file ops, etc.)
    └── domain/          # Domain-specific tools
```

## Available Tools

The agent comes with a comprehensive set of tools:

### Core Tools
- **File Operations**: Create, edit, search files with intelligent editing
- **Bash Execution**: Run shell commands with safety checks
- **Web Search**: DuckDuckGo/Brave integration for research
- **Web Fetch**: Retrieve and analyze web content
- **Notebook Editing**: Jupyter notebook manipulation
- **Directory Listing**: Explore project structure
- **Progress Tracking**: Automatic documentation generation
- **Sub-Agent Tasks**: Spawn specialized agents for complex subtasks

### Cognitive Tools
- **Memory System**: Save and recall insights across sessions (`save_memory`, `recall_memory`)
- **Reflection**: Post-task analysis and learning (`reflect`)
- **Evidence Synthesis**: Scientific literature analysis with workspace management

### Skills System
- **Evidence Synthesis**: Advanced scientific research with file-based memory
- **Experiment Design**: Scientific experiment planning
- **Literature Search**: Academic paper discovery and analysis
- **Software Engineering**: Code development and architecture

## Examples

### Scientific Research
```bash
python -m sciagent \
  --max-iterations 30 \
  "Research CRISPR gene editing efficiency: Cas9 vs Cas12a vs base editors. Create evidence-based comparison with citations."
```

### Code Analysis
```bash
python -m sciagent \
  --working-dir /path/to/project \
  "Analyze this codebase and identify potential security vulnerabilities"
```

### Evidence Synthesis
```bash
python -m sciagent \
  --max-iterations 20 \
  "Search for recent papers on quantum computing error correction. Save findings to workspace and synthesize key insights."
```

### Feature Development
```bash
python -m sciagent \
  --max-iterations 100 \
  "Add authentication system to this Flask app with JWT tokens"
```

### Documentation Generation  
```bash
python -m sciagent \
  --no-web \
  "Generate comprehensive API documentation for all Python modules"
```

### Bug Fixing with Memory
```bash
python -m sciagent \
  --resume task_123 \
  "Continue debugging the database connection issues. Save any insights for future reference."
```

## Configuration

The agent uses a `Config` dataclass for all settings. Key configuration options:

- **API Integration**: Supports multiple providers with automatic key detection
- **Model Fallback**: Specify backup models for reliability
- **Resource Limits**: Control iteration counts and sub-agent spawning
- **Feature Toggles**: Enable/disable web access, notebook support, skills, etc.
- **State Management**: Configure persistence and progress tracking
- **Memory System**: Automatic saving of insights and learnings to `.sciagent_workspace/`
- **Skills Integration**: Optional domain-specific capabilities (evidence synthesis, etc.)

## Progress Tracking

The agent automatically generates `progress.md` files that include:
- Task breakdown and current status
- Files created/modified
- Tools used and their outcomes
- Iteration summaries
- Error logs and recovery actions

## Resuming Tasks

Long-running tasks can be paused and resumed:

1. Tasks are automatically assigned unique IDs
2. State is persisted automatically
3. Resume with `--resume <task_id>`
4. Progress is maintained across sessions

## Error Handling

The agent includes robust error handling:
- **Model Fallback**: Automatically tries backup models on failures
- **Tool Error Recovery**: Graceful handling of tool execution errors  
- **Rate Limit Management**: Built-in retry logic for API limits
- **State Recovery**: Can recover from crashes and interruptions

## Development

### Adding New Tools

1. Create a new file in `tools/core/` or `tools/domain/`
2. Inherit from `BaseTool` and implement required methods
3. The tool will be automatically discovered by the registry

Example:
```python
from ..base_tool import BaseTool

class MyCustomTool(BaseTool):
    def get_name(self) -> str:
        return "my_custom_tool"
    
    def get_description(self) -> str:
        return "Description of what this tool does"
    
    def get_parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "input": {"type": "string", "description": "Input parameter"}
            },
            "required": ["input"]
        }
    
    def execute(self, **kwargs) -> dict:
        # Tool implementation
        return {"success": True, "result": "Tool output"}
```

### Testing

Test with different models:
```bash
# Quick smoke tests
python -m sciagent --max-iterations 1 --model gpt-4o-mini "Say hello"
python -m sciagent --max-iterations 1 --model claude-3-5-sonnet-20241022 "Say hello"
```

Enable debug logging:
```bash
export LITELLM_LOG=DEBUG
python -m sciagent --debug "Your task here"
```

## Troubleshooting

### Common Issues

**"No API key found"**
- Ensure environment variables are set correctly for your chosen provider
- Use `--api-key` flag as an alternative
- Check that model name matches provider (e.g., `gpt-4o` requires `OPENAI_API_KEY`)

**"Model not found"**  
- Verify model name is correct for the provider
- Check if you have access to the specific model
- Try a different model as fallback

**"Task won't resume"**
- Check if state file exists in working directory
- Ensure task ID is correct
- Try starting fresh if state file is corrupted

**Tools not working**
- Check if required dependencies are installed (`pip install -r requirements.txt`)
- Some tools require internet access
- Verify file permissions in working directory

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add new tools or improve existing functionality
4. Test with multiple LLM providers
5. Submit a pull request

## License
MIT License

## Acknowledgments
Built by human with major contributions from:
- Claude Code, GPT-5, Kiro, Grok

Built on top of:
- [LiteLLM](https://github.com/BerriAI/litellm) for multi-provider LLM support
- [DuckDuckGo Search](https://github.com/deedy5/duckduckgo_search) for web search capabilities

---

For detailed usage examples and advanced configuration, see [USAGE.md](USAGE.md).
