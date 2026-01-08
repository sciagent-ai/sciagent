---
layout: default
title: Usage
nav_order: 5
---
# SCI Agent - Comprehensive Usage Guide

A complete AI-powered scientific computing and engineering agent with multi-LLM support, advanced reasoning capabilities, and comprehensive toolset for complex technical tasks.

## Table of Contents

- [Quick Start](#quick-start)
- [Installation](#installation)
- [Command Line Interface](#command-line-interface)
- [Configuration](#configuration)
- [Model Selection](#model-selection)
- [Core Tools](#core-tools)
- [Skills System](#skills-system)
- [Advanced Features](#advanced-features)
- [Programming Integration](#programming-integration)
- [Best Practices](#best-practices)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)

## Quick Start

### Basic Usage

```bash
# Simple task execution
python -m sciagent "Create a Python script to analyze scientific data"

# Interactive mode (if no task provided)
python -m sciagent
# Enter comprehensive task: [your task here]
```

### With API Key
```bash
# Using command line API key
python -m sciagent --api-key YOUR_API_KEY "Analyze this dataset"

# Using environment variables (recommended)
export ANTHROPIC_API_KEY=your_key_here
# or
export OPENAI_API_KEY=your_key_here
python -m sciagent "Your task here"
```

## Installation

### Requirements
- Python 3.8+
- API keys for LLM providers (Anthropic, OpenAI, etc.)

### Setup
```bash
# Clone the repository
git clone <repository-url>
cd sciagent

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
export ANTHROPIC_API_KEY="your_anthropic_key"
export OPENAI_API_KEY="your_openai_key"
export MISTRAL_API_KEY="your_mistral_key"  # optional
```

## Command Line Interface

### Basic Arguments

```bash
python -m sciagent [TASK] [OPTIONS]
```

### Core Options

| Option | Description | Default |
|--------|-------------|---------|
| `task` | Task description (positional) | Interactive prompt |
| `--working-dir` | Working directory | `.` |
| `--max-iterations` | Maximum iterations | `50` |
| `--debug` | Enable debug mode | `False` |
| `--resume TASK_ID` | Resume a previous task | None |

### Model Options

| Option | Description | Example |
|--------|-------------|---------|
| `--model` | Primary LLM model | `claude-sonnet-4-5-20250929` |
| `--models` | Comma-separated fallback models | `claude-sonnet-4-5-20250929,gpt-4o` |
| `--api-key` | API key (overrides env vars) | |

### Feature Toggles

| Option | Description | Default |
|--------|-------------|---------|
| `--no-progress` | Disable progress.md tracking | Enabled |
| `--no-web` | Disable web tools | Enabled |
| `--no-notebooks` | Disable notebook tools | Enabled |
| `--no-skills` | Disable skill system | Enabled |

### Examples

```bash
# Basic scientific analysis
python -m sciagent "Analyze the correlation between temperature and pressure in this dataset"

# Code development with specific model
python -m sciagent --model gpt-4o "Implement a neural network for time series prediction"

# Multi-model fallback
python -m sciagent --models "claude-sonnet-4-5-20250929,gpt-5.2,gemini-3.0-flash" "Complex data analysis task"

# Resume a previous task
python -m sciagent --resume abc123def

# Debug mode for troubleshooting
python -m sciagent --debug "Debug this Python script for errors"

# Disable web access for offline work
python -m sciagent --no-web "Refactor this local codebase"

# Maximum performance (disable skills system)
python -m sciagent --no-skills "Quick code fix needed"
```

## Configuration

### Environment Variables

The agent supports multiple LLM providers through environment variables:

```bash
# Anthropic (Claude)
export ANTHROPIC_API_KEY="your_key"

# OpenAI (GPT)
export OPENAI_API_KEY="your_key"

# Google (Gemini)
export GOOGLE_APPLICATION_CREDENTIALS="path/to/credentials.json"
# or
export GEMINI_API_KEY="your_key"

# Mistral
export MISTRAL_API_KEY="your_key"

# xAI (Grok)
export XAI_API_KEY="your_key"

# Cohere
export COHERE_API_KEY="your_key"

# Brave Search (recommended for enhanced web research)
export BRAVE_SEARCH_API_KEY="your_key"
```

### Configuration Parameters

The agent uses a comprehensive configuration system with these key parameters:

```python
from sciagent import Config

config = Config(
    # Model configuration
    model="claude-sonnet-4-5-20250929",  # Primary model
    models=["claude-sonnet-4-5-20250929", "gpt-4o"],  # Fallback models
    
    # Execution parameters
    max_iterations=25,                   # Maximum task iterations
    max_tool_executions_per_iteration=15, # Tools per iteration
    max_consecutive_same_tool=5,         # Prevent infinite loops
    
    # LLM parameters
    temperature=0.1,                     # Creativity (0.0-1.0)
    max_tokens=4096,                     # Response length
    reasoning_effort="medium",           # "none", "low", "medium", "high"
    
    # Feature toggles
    enable_web=True,                     # Web search/fetch
    enable_notebooks=True,               # Jupyter notebooks
    enable_skills=True,                  # Skill routing system
    enable_performance_monitoring=False,  # Performance metrics
    
    # Progress and state
    progress_tracking=True,              # progress.md file
    state_file=".sci_agent_state.pkl",  # State persistence
    context_retention=8,                 # Conversation history
    summarization_threshold=12,          # Auto-summarization
    
    # Advanced options
    max_sub_agents=3,                    # Concurrent sub-agents
    metrics_mode=True,                   # Detailed metrics
    verbosity="standard",                # "minimal", "standard", "verbose", "debug"
)
```

## Model Selection

### Recommended Models by Task Type

#### Scientific Computing & Engineering
- **`claude-sonnet-4-5-20250929`** - Best overall balance for scientific tasks
- **`claude-opus-4-5-20251101`** - Most powerful for complex analysis
- **`gpt-5.2`** - Excellent reasoning for mathematical problems

#### Code Development
- **`gpt-5.2-codex`** - Specialized for agentic coding
- **`claude-sonnet-4-5-20250929`** - Excellent code generation and debugging
- **`gpt-4.1`** - Strong at frontend and API development

#### Research & Analysis
- **`gemini-3.0-flash-thinking-experimental`** - Advanced thinking capabilities
- **`grok-4.1-fast-reasoning`** - Fast reasoning for complex analysis
- **`claude-opus-4-5-20251101`** - Deep research and synthesis

#### Quick Tasks
- **`claude-3-5-haiku-20241022`** - Fast and efficient
- **`gpt-4o-mini`** - Cost-effective for simple tasks
- **`gemini-2.0-flash-lite`** - Quick responses

### Model Fallback Strategy

```bash
# High-reliability setup (premium models)
--models "claude-opus-4-5-20251101,gpt-5.2,gemini-3.0-flash-thinking-experimental"

# Balanced cost/performance
--models "claude-sonnet-4-5-20250929,gpt-4o,gemini-2.5-pro"

# Budget-conscious
--models "claude-3-5-haiku-20241022,gpt-4o-mini,gemini-2.0-flash-lite"

# Coding-focused
--models "gpt-5.2-codex,claude-sonnet-4-5-20250929,codestral"
```

## Core Tools

The SCI Agent includes 17+ core tools for comprehensive scientific and engineering tasks:

### File Operations
- **`str_replace_editor`** - Create, read, edit files with precise control
- **`multi_edit`** - Atomic batch file editing with rollback
- **`glob_search`** - Pattern-based file discovery
- **`list_directory`** - Directory exploration
- **`advanced_file_ops`** - Enhanced file operations with analysis

### Search & Analysis
- **`grep_search`** - Regex pattern searching across files
- **`web_search`** - DuckDuckGo/Brave integration for research
- **`web_fetch`** - Fetch and analyze web content

### Execution & Development
- **`bash`** - Shell command execution with timeouts
- **`git_operations`** - Smart git workflows with auto-commit
- **`notebook_edit`** - Jupyter notebook creation and editing

### Task Management & Cognition
- **`task_agent`** - Spawn specialized sub-agents
- **`todo_write`** - Task tracking and progress management
- **`create_summary`** - Intelligent conversation summarization
- **`update_progress_md`** - Progress reporting
- **`ask_user_step`** - Interactive user guidance
- **`save_memory`** - Save insights and findings to persistent storage
- **`recall_memory`** - Search and retrieve previously saved insights
- **`reflect`** - Post-task analysis and learning from successes/failures

### Monitoring
- **`performance_monitor`** - Real-time performance tracking

## Skills System

The SCI Agent includes a sophisticated skill routing system for specialized capabilities.

**Important**: Skills are loaded from a `skills/` directory in your **working directory**, not the project directory. To use skills:

```bash
# Copy skills to your working directory
cp -r /path/to/sciagent/skills /your/working/directory/

# Or run from the sciagent project directory
cd /path/to/sciagent
python -m sciagent "your task here"
```

### Available Skills

#### Software Engineering
- **Triggers**: code, program, debug, test, fix, implement, refactor
- **Tools**: File operations, bash, search tools
- **Use Cases**: Code development, debugging, testing, refactoring

#### Experiment Design
- **Triggers**: experiment, design, optimization, bayesian, statistical
- **Tools**: Notebooks, web research, file operations
- **Use Cases**: DOE, Bayesian optimization, statistical analysis
- **Dependencies**: numpy, scipy, matplotlib

#### Literature Search & Evidence Synthesis
- **Triggers**: literature, papers, research, articles, citations, evidence, synthesis
- **Tools**: Web search, content analysis, summarization, memory system
- **Use Cases**: Research synthesis, bibliography creation, literature reviews, evidence-based analysis
- **Features**: File-based workspace management, citation formatting, source tracking

### Skill Configuration

```bash
# Enable all skills (default)
python -m sciagent "Design an experiment to optimize reaction conditions"

# Disable skills for maximum speed
python -m sciagent --no-skills "Quick code fix"

# Skills are automatically selected based on task keywords
```

## Advanced Features

### State Persistence & Resume

```bash
# Long-running tasks automatically save state
python -m sciagent "Complex multi-step analysis project"
# ... if interrupted ...

# Resume from where you left off
python -m sciagent --resume <task_id>
```

### Progress Tracking

The agent automatically creates detailed progress reports:

```markdown
# SCI Agent Progress Report

**Task ID:** abc123def
**Agent Version:** SCI (Complete AI Code Assistant)
**Tools Available:** 17 scientific tools
**Status:** In Progress

## Task Description
Your original task description

## Agent Capabilities
✅ **File Operations:** Create, edit, search files
✅ **Execution:** Shell commands with intelligent timeouts
✅ **Web Research:** Search and content fetching
✅ **Project Management:** Progress tracking and summaries
```

### Sub-Agent Spawning

For complex tasks, the agent can spawn specialized sub-agents:

```python
# Automatic sub-agent creation for:
# - Complex analysis subtasks
# - Parallel processing
# - Specialized domain work
# - Research vs. implementation separation
```

### Reasoning Modes

Configure reasoning depth for supported models:

```bash
# High reasoning for complex problems
python -m sciagent --model claude-opus-4-5-20251101 "Complex mathematical proof"

# Fast reasoning for quick tasks
python -m sciagent --model grok-4.1-fast-reasoning "Quick data analysis"
```

## Programming Integration

### Python API

```python
from sciagent import Config, SCIAgent

# Basic setup
config = Config(
    model="claude-sonnet-4-5-20250929",
    working_dir="./my_project",
    enable_web=True
)

agent = SCIAgent(config)

# Execute a task
result = agent.execute_task("Analyze this dataset and create visualizations")

# Check results
print(f"Success: {result['success']}")
print(f"Task ID: {result['task_id']}")
print(f"Iterations: {result['iterations']}")
```

### Advanced Python Usage

```python
# Multi-model fallback
config = Config(
    models=["claude-sonnet-4-5-20250929", "gpt-4o", "gemini-2.5-pro"],
    max_iterations=100,
    reasoning_effort="high"
)

# Progress callback
def progress_callback(entry):
    print(f"Progress: {entry.step} - {entry.status}")

agent = SCIAgent(config, progress_callback=progress_callback)

# Resume a previous task
result = agent.execute_task("", resume_task_id="previous_task_id")
```

### Jupyter Integration

```python
# In Jupyter notebooks
%load_ext sciagent_magic

# Use magic commands
%sciagent "Create a data analysis pipeline"
%%sciagent
Analyze this dataset:
- Load CSV data
- Clean and preprocess
- Create visualizations
- Export results
```

## Best Practices

### Task Description Guidelines

**Good task descriptions:**
```bash
# Specific and actionable
"Create a Python script to analyze temperature sensor data, calculate moving averages, and generate trend plots"

# Include context and requirements
"Refactor this legacy Flask application to use modern patterns, add error handling, and improve performance"

# Scientific workflows
"Design a DOE experiment to optimize reaction yield with 3 factors: temperature (50-100°C), pressure (1-5 bar), catalyst concentration (0.1-1.0%)"
```

**Avoid vague descriptions:**
```bash
# Too vague
"Fix my code"
"Analyze data"
"Make it better"
```

### Performance Optimization

```bash
# For speed-critical tasks
python -m sciagent --no-skills --model claude-3-5-haiku-20241022 "Quick fix"

# For maximum capability
python -m sciagent --model claude-opus-4-5-20251101 --max-iterations 100 "Complex analysis"

# For cost optimization
python -m sciagent --models "claude-3-5-haiku-20241022,gpt-4o-mini" "Simple task"
```

### Error Handling

```bash
# Debug mode for troubleshooting
python -m sciagent --debug --verbosity debug "Problematic task"

# Multi-model fallback for reliability
python -m sciagent --models "claude-sonnet-4-5-20250929,gpt-4o,gemini-2.5-pro" "Critical task"
```

## Examples

### Scientific Data Analysis

```bash
# Comprehensive data analysis
python -m sciagent "
Load the experimental_data.csv file, perform statistical analysis including:
1. Descriptive statistics and outlier detection
2. Correlation analysis between variables
3. Linear regression modeling
4. Create publication-quality plots
5. Export results to a summary report
"
```

### Code Development

```bash
# Full-stack development
python -m sciagent "
Create a REST API for a lab inventory system:
1. Design database schema with SQLAlchemy
2. Implement CRUD endpoints with FastAPI
3. Add authentication and validation
4. Create unit tests with pytest
5. Add API documentation
6. Containerize with Docker
"
```

### Research Project

```bash
# Literature review and analysis
python -m sciagent "
Conduct a literature review on machine learning in drug discovery:
1. Search for recent papers (2020-2024)
2. Analyze key trends and methods
3. Identify research gaps
4. Create a synthesis table
5. Write a comprehensive review document
"
```

### Experiment Design

```bash
# DOE optimization
python -m sciagent "
Design an experiment to optimize polymer synthesis:
- Factors: temperature (60-120°C), catalyst ratio (1:1-1:10), reaction time (1-24h)
- Response: yield percentage
- Use factorial design with center points
- Generate experiment matrix and analysis code
"
```

### Complex Refactoring

```bash
# Legacy code modernization
python -m sciagent "
Refactor this monolithic Python application:
1. Extract business logic into separate modules
2. Implement proper error handling
3. Add type hints and documentation
4. Create unit tests with >80% coverage
5. Set up CI/CD pipeline
6. Update dependencies to latest versions
"
```

## Troubleshooting

### Common Issues

#### API Key Problems
```bash
# Error: No API key found
export ANTHROPIC_API_KEY="your_key"
# or
python -m sciagent --api-key YOUR_KEY "task"
```

#### Model Not Available
```bash
# Error: Model not found
# Check available models:
python -c "from sciagent.model_config import get_available_models; print(get_available_models())"

# Use fallback models:
python -m sciagent --models "claude-sonnet-4-5-20250929,gpt-4o" "task"
```

#### Task Interruption
```bash
# Tasks are automatically resumable
# Check for task ID in output:
# Task can be resumed with: --resume abc123def
python -m sciagent --resume abc123def
```

#### Performance Issues
```bash
# Reduce iterations for faster execution
python -m sciagent --max-iterations 10 "simple task"

# Use faster models
python -m sciagent --model claude-3-5-haiku-20241022 "quick task"

# Disable unnecessary features
python -m sciagent --no-web --no-skills "offline task"
```

### Debug Mode

```bash
# Enable comprehensive debugging
python -m sciagent --debug --verbosity debug "problematic task"

# This provides:
# - Tool execution details
# - LLM call information
# - Error stack traces
# - Performance metrics
# - State transitions
```

### Logs and State Files

```bash
# Default files created:
ls -la .sci_agent_state.pkl  # State persistence
ls -la progress.md           # Progress report

# Custom locations:
python -m sciagent --working-dir /path/to/project "task"
```

### Getting Help

```bash
# Command line help
python -m sciagent --help

# Model information
python -c "
from sciagent.model_config import get_coding_models, get_reasoning_models
print('Coding Models:', get_coding_models())
print('Reasoning Models:', get_reasoning_models())
"
```

## Advanced Configuration Examples

### Research Configuration
```python
config = Config(
    models=["claude-opus-4-5-20251101", "gpt-5.2", "gemini-3.0-flash-thinking-experimental"],
    enable_web=True,
    enable_notebooks=True,
    reasoning_effort="high",
    max_iterations=100,
    temperature=0.2,
    max_sub_agents=5
)
```

### Production Configuration
```python
config = Config(
    models=["claude-sonnet-4-5-20250929", "gpt-4o"],
    enable_web=False,  # Offline operation
    enable_skills=False,  # Maximum speed
    reasoning_effort="medium",
    max_iterations=50,
    temperature=0.1,
    metrics_mode=True  # Detailed tracking
)
```

### Development Configuration
```python
config = Config(
    model="gpt-5.2-codex",  # Coding-specialized model
    enable_notebooks=True,
    debug_mode=True,
    verbosity="verbose",
    max_iterations=25,
    enable_performance_monitoring=True
)
```

---

For more information and updates, visit the project repository and documentation.
