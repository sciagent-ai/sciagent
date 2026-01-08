---
layout: default
title: Advanced Configuration
nav_order: 3
---

# SciAgent – Advanced Configuration

This guide covers advanced usage patterns, configuration options, and optimization strategies for power users and production deployments.

---

## Configuration System

### Environment Variables

Complete list of supported environment variables:

```bash
# LLM Provider API Keys
export OPENAI_API_KEY="your_openai_key"
export ANTHROPIC_API_KEY="your_anthropic_key"
export MISTRAL_API_KEY="your_mistral_key"
export COHERE_API_KEY="your_cohere_key"
export GOOGLE_API_KEY="your_google_key"

# Advanced Configuration
export SCIAGENT_DEFAULT_MODEL="gpt-4o"
export SCIAGENT_MAX_ITERATIONS="25"
export SCIAGENT_WORKING_DIR="/path/to/workspace"
export SCIAGENT_DEBUG="false"
export SCIAGENT_PROGRESS_TRACKING="true"
export SCIAGENT_WEB_ENABLED="true"
export SCIAGENT_NOTEBOOKS_ENABLED="true"
export SCIAGENT_SKILLS_ENABLED="true"

# Enhanced Web Search
export BRAVE_SEARCH_API_KEY="your_brave_key"
```

### Configuration File

Create a `.sciagent.json` in your working directory or home directory:

```json
{
  "default_model": "gpt-4o",
  "fallback_models": ["claude-3-sonnet-20240229", "gpt-3.5-turbo"],
  "max_iterations": 25,
  "temperature": 0.1,
  "max_tokens": 4096,
  "timeout": 300,
  "features": {
    "web": true,
    "notebooks": true,
    "skills": true,
    "progress_tracking": true
  },
  "tools": {
    "bash_timeout": 30,
    "max_file_size": "10MB",
    "search_depth": 3
  },
  "output": {
    "verbosity": "standard",
    "format": "markdown",
    "save_state": true
  }
}
```

---

## Model Selection Strategies

### Performance vs Cost Optimization

```bash
# High-performance setup (expensive but capable)
python -m sciagent \
  --model gpt-4o \
  --models "gpt-4o,claude-3-sonnet-20240229" \
  "Complex research task"

# Balanced setup (good performance, moderate cost)
python -m sciagent \
  --model claude-3-haiku-20240307 \
  --models "claude-3-haiku-20240307,gpt-3.5-turbo" \
  "Standard analysis task"

# Budget setup (fast and cheap)
python -m sciagent \
  --model gpt-3.5-turbo \
  --max-iterations 15 \
  "Simple task"
```

### Task-Specific Model Selection

```bash
# Code-heavy tasks (better reasoning about code)
python -m sciagent --model gpt-4o "Refactor Python codebase"

# Research tasks (better at synthesis)
python -m sciagent --model claude-3-sonnet-20240229 "Literature review"

# Quick tasks (fast responses)
python -m sciagent --model claude-3-haiku-20240307 "Fix this bug"
```

---

## Advanced Command Line Options

### Execution Control

```bash
# Timeout control
python -m sciagent --timeout 600 "Long-running analysis"

# Memory optimization
python -m sciagent --max-context-length 8000 "Large dataset task"

# Parallel execution
python -m sciagent --max-concurrent-tools 3 "Multi-step workflow"
```

### Output Control

```bash
# Custom output directory
python -m sciagent --output-dir /path/to/results "Analysis task"

# Structured output format
python -m sciagent --output-format json "Data processing task"

# Disable automatic file creation
python -m sciagent --no-auto-files "Read-only analysis"
```

### Debugging and Monitoring

```bash
# Verbose debugging
python -m sciagent --debug --log-level debug "Problematic task"

# Performance monitoring
python -m sciagent --profile --benchmark "Performance-critical task"

# Tool execution tracing
python -m sciagent --trace-tools "Understand tool usage"
```

---

## Skills System Configuration

### Custom Skill Definitions

Create `skills.yaml` in your working directory:

```yaml
skills:
  data_science:
    triggers: ["analyze", "statistics", "visualization", "pandas", "numpy"]
    tools: ["notebook_edit", "web_search", "str_replace_editor"]
    priority: high
    
  web_development:
    triggers: ["webapp", "api", "frontend", "backend", "django", "flask"]
    tools: ["str_replace_editor", "bash", "web_search"]
    priority: medium
    
  research:
    triggers: ["literature", "papers", "review", "survey", "academic", "evidence", "synthesis"]
    tools: ["web_search", "web_fetch", "str_replace_editor", "save_memory", "recall_memory"]
    priority: medium
    
  cognitive_tools:
    triggers: ["memory", "recall", "remember", "insight", "reflection", "learning"]
    tools: ["save_memory", "recall_memory", "reflect"]
    priority: high
```

### Skill Override

```bash
# Force specific skill
python -m sciagent --force-skill data_science "Analyze this dataset"

# Disable specific skills
python -m sciagent --disable-skills research,web_development "Code-only task"

# Enable memory system for learning tasks
python -m sciagent --force-skill cognitive_tools "Analyze and remember key insights"
```

---

## Tool Configuration

### Custom Tool Timeouts

```bash
# Increase bash command timeout
python -m sciagent --bash-timeout 120 "Long compilation task"

# Set web request timeout
python -m sciagent --web-timeout 60 "Fetch large documents"
```

### Tool Restrictions

```bash
# Disable potentially destructive tools
python -m sciagent --safe-mode "Automated analysis"

# Whitelist specific tools only
python -m sciagent --allowed-tools "str_replace_editor,web_search,save_memory" "Research task"
```

---

## State Management

### Custom State Files

```bash
# Use custom state file location
python -m sciagent --state-file /path/to/custom.state "Task"

# Disable state persistence
python -m sciagent --no-state "One-time task"
```

### State Inspection

```bash
# List all saved states
python -m sciagent --list-states

# Inspect specific state
python -m sciagent --inspect-state abc123def

# Clean old states
python -m sciagent --clean-states --older-than 7d
```

---

## Performance Optimization

### Memory Management

```bash
# Limit conversation history
python -m sciagent --max-history 10 "Long conversation"

# Enable context compression
python -m sciagent --compress-context "Large document analysis"
```

### Speed Optimization

```bash
# Minimal feature set for speed
python -m sciagent \
  --no-skills \
  --no-web \
  --no-notebooks \
  --max-iterations 10 \
  "Quick fix"

# Aggressive caching
python -m sciagent --cache-aggressive "Repeated similar tasks"
```

---

## Production Deployment

### Docker Configuration

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Set default configuration
ENV SCIAGENT_MAX_ITERATIONS=25
ENV SCIAGENT_PROGRESS_TRACKING=false
ENV SCIAGENT_DEBUG=false

ENTRYPOINT ["python", "-m", "sciagent"]
```

### Kubernetes Deployment

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: sciagent-config
data:
  config.json: |
    {
      "max_iterations": 25,
      "features": {
        "web": true,
        "progress_tracking": false
      }
    }
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sciagent
spec:
  replicas: 3
  selector:
    matchLabels:
      app: sciagent
  template:
    metadata:
      labels:
        app: sciagent
    spec:
      containers:
      - name: sciagent
        image: sciagent:latest
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: llm-keys
              key: openai
        volumeMounts:
        - name: config
          mountPath: /app/.sciagent.json
          subPath: config.json
      volumes:
      - name: config
        configMap:
          name: sciagent-config
```

---

## Integration Patterns

### CI/CD Integration

```yaml
# .github/workflows/sciagent.yml
name: SCI Agent Analysis
on: [push, pull_request]

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Setup Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.11'
    - name: Install SCI Agent
      run: |
        pip install -r requirements.txt
    - name: Run Analysis
      env:
        OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
      run: |
        python -m sciagent \
          --no-progress \
          --output-format json \
          --max-iterations 15 \
          "Analyze code quality and suggest improvements"
    - name: Upload Results
      uses: actions/upload-artifact@v2
      with:
        name: analysis-results
        path: results/
```

### Jupyter Integration

```python
# Custom Jupyter magic command
from IPython.core.magic import Magics, line_magic, cell_magic, magics_class
from sciagent import SCIAgent, Config

@magics_class
class SCIAgentMagics(Magics):
    
    @line_magic
    def sciagent(self, line):
        """Execute SCI Agent task from Jupyter"""
        config = Config(
            max_iterations=10,
            enable_notebooks=True,
            progress_tracking=False
        )
        agent = SCIAgent(config)
        result = agent.execute_task(line)
        return result
    
    @cell_magic
    def sciagent_task(self, line, cell):
        """Execute multi-line SCI Agent task"""
        config = Config(
            max_iterations=15,
            enable_notebooks=True,
            verbosity="verbose"
        )
        agent = SCIAgent(config)
        result = agent.execute_task(cell)
        return result

# Load the extension
ip = get_ipython()
ip.register_magic_function(SCIAgentMagics)
```

---

## Security and Access Control

### API Key Management

```bash
# Use key rotation
export OPENAI_API_KEY_PRIMARY="key1"
export OPENAI_API_KEY_SECONDARY="key2"
python -m sciagent --key-rotation "Long task"

# Restrict API usage
python -m sciagent --max-tokens-per-request 1000 "Budget-controlled task"
```

### Sandboxing

```bash
# Run in restricted environment
python -m sciagent \
  --sandbox \
  --no-bash \
  --read-only \
  "Safe analysis task"

# Whitelist allowed file paths
python -m sciagent \
  --allowed-paths "/safe/dir,/another/safe/dir" \
  "Restricted file access task"
```

---

## Monitoring and Observability

### Metrics Collection

```python
from sciagent import Config, SCIAgent
from sciagent.monitoring import MetricsCollector

# Enable detailed metrics
config = Config(
    enable_metrics=True,
    metrics_endpoint="http://prometheus:9090/metrics"
)

collector = MetricsCollector()
agent = SCIAgent(config, metrics_collector=collector)

result = agent.execute_task("Analysis task")

# Access metrics
print(f"Total tokens used: {collector.total_tokens}")
print(f"Tool executions: {collector.tool_executions}")
print(f"Task duration: {collector.duration_seconds}")
```

### Logging Configuration

```python
import logging
from sciagent import setup_logging

# Configure structured logging
setup_logging(
    level=logging.INFO,
    format="json",
    output="/var/log/sciagent.log"
)
```

---

## Custom Extensions

### Plugin Development

```python
from sciagent.plugins import ToolPlugin

class CustomAnalysisTool(ToolPlugin):
    name = "custom_analysis"
    description = "Perform custom data analysis"
    
    def execute(self, data_path: str, analysis_type: str) -> dict:
        """Custom analysis implementation"""
        # Your custom logic here
        return {"status": "complete", "results": "..."}

# Register the plugin
from sciagent import register_plugin
register_plugin(CustomAnalysisTool())
```

### Hook System

```python
from sciagent.hooks import Hook

class PreExecutionHook(Hook):
    def before_task(self, task: str, config: dict) -> dict:
        """Called before task execution"""
        # Modify task or config
        return {"task": task, "config": config}
    
    def after_iteration(self, iteration: int, result: dict) -> None:
        """Called after each iteration"""
        # Log or process iteration results
        pass

# Register hooks
from sciagent import register_hook
register_hook(PreExecutionHook())
```

---

## Best Practices for Advanced Usage

### Resource Management

- Monitor token usage with budget limits
- Use model fallbacks for reliability
- Implement proper timeout handling
- Cache frequently accessed data

### Error Handling

- Set up comprehensive logging
- Use retry mechanisms for transient failures
- Implement graceful degradation
- Monitor and alert on error rates

### Performance

- Profile tool usage patterns
- Optimize model selection for workload
- Use appropriate iteration limits
- Implement result caching where beneficial

---

This covers the advanced configuration options and patterns for SciAgent.
For internal API documentation and architecture details, see the internals guide.
