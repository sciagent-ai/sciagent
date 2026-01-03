---
layout: default
title: Quick Start
nav_order: 2
---

# SCI Agent – Quick Start Guide

SCI Agent is a command-line AI agent for scientific computing and engineering workflows.
It can plan and execute multi-step tasks such as literature review, code generation,
experiments, and refactoring while tracking progress and allowing tasks to be resumed
after interruption.

This guide explains how to run the agent, what it produces, and how to control and
inspect its work.

---

## Quick Start (30 seconds)

Run a task directly from the command line:

```bash
python -m sciagent "Analyze this dataset and generate summary statistics and plots"
```

If no task is provided, the agent will prompt you interactively:

```bash
python -m sciagent
# Enter comprehensive task:
```

### What happens when you run a task

During execution, the agent will:

* Plan the task step by step
* Use available tools (files, shell, web, notebooks, etc.)
* Create or modify files in the working directory
* Write a live progress report to `progress.md` (unless disabled)
* Save state so the task can be resumed later

When finished, a concise summary is printed to the terminal, including:

* success / failure status
* number of iterations
* task ID (used for resume)
* files created or modified

---

## Installation

### Requirements

* Python 3.8 or newer
* At least one supported LLM provider API key

### Setup

```bash
git clone <repository-url>
cd sciagent
pip install -r requirements.txt
```

Set at least one API key as an environment variable:

```bash
export OPENAI_API_KEY="your_key"
# or
export ANTHROPIC_API_KEY="your_key"
# or
export MISTRAL_API_KEY="your_key"

# Optional: For enhanced web search
export BRAVE_SEARCH_API_KEY="your_brave_key"
```

---

## Basic Command Line Usage

```bash
python -m sciagent [TASK] [OPTIONS]
```

Examples:

```bash
# Scientific analysis
python -m sciagent "Analyze experimental_data.csv and summarize key findings"

# Code refactoring
python -m sciagent "Refactor this repository to improve structure and add tests"

# Long-running task
python -m sciagent "Conduct a literature review and implement a baseline model"
```

---

## Core Options

| Option             | Description                         | Default |
| ------------------ | ----------------------------------- | ------- |
| `--working-dir`    | Directory the agent operates in     | `.`     |
| `--max-iterations` | Maximum reasoning / execution loops | `50`    |
| `--debug`          | Enable verbose debug output         | off     |
| `--resume TASK_ID` | Resume a previous task              | –       |

---

## Feature Toggles

The agent exposes switches to control capabilities at runtime:

| Option           | Effect                                |
| ---------------- | ------------------------------------- |
| `--no-progress`  | Disable writing `progress.md`         |
| `--no-web`       | Disable web search and fetch tools    |
| `--no-notebooks` | Disable Jupyter notebook tools        |
| `--no-skills`    | Disable skill routing (maximum speed) |

Examples:

```bash
# Offline execution
python -m sciagent --no-web "Refactor this local codebase"

# Fast execution (minimal reasoning overhead)
python -m sciagent --no-skills "Quick code fix"

# Disable progress file
python -m sciagent --no-progress "One-off analysis task"
```

---

## Model Selection

Select a primary model using `--model`:

```bash
python -m sciagent --model gpt-4o "Analyze this dataset"
```

You can also provide fallback models to improve reliability:

```bash
python -m sciagent \
  --models "primary_model,fallback_model" \
  "Complex multi-step task"
```

Model names depend on the LLM providers configured in your environment.
Refer to your provider's documentation or LiteLLM configuration for valid identifiers.

---

## Progress Tracking

By default, the agent creates a file named `progress.md` in the working directory.

This file includes:

* task description
* current status
* completed steps
* next planned actions

You can open this file at any time to understand what the agent is doing or has done.

---

## Resuming Interrupted Tasks

Long-running tasks automatically save state.

If execution stops (Ctrl-C, crash, network issue), the agent prints a task ID:

```text
Task can be resumed with: --resume abc123def
```

Resume the task using:

```bash
python -m sciagent --resume abc123def
```

The agent will continue from the last saved state.

---

## Inspecting File Changes

The agent may create or modify files in the working directory.

Typical outputs include:

* scripts and modules
* notebooks
* markdown summaries (e.g. literature reviews)
* configuration or experiment artifacts

Using the agent inside a git repository is strongly recommended.

---

## Common Usage Patterns

### Literature Review & Evidence Synthesis

```bash
python -m sciagent "
Search recent literature on topic X,
synthesize evidence with proper citations,
save insights to memory for future reference.
"
```

### Scientific Data Analysis with Memory

```bash
python -m sciagent "
Load experimental_data.csv,
clean the data,
perform statistical analysis,
generate plots,
and save key findings to memory.
"
```

### Experiment Design

```bash
python -m sciagent "
Design an experiment with three factors,
generate an experiment matrix,
and produce analysis code.
"
```

### Codebase Refactoring

```bash
python -m sciagent "
Refactor this repository,
improve structure and readability,
add tests,
and document the changes.
"
```

---

## Best Practices

* Be specific in task descriptions
* Run inside a version-controlled directory
* Use `--max-iterations` to limit cost and runtime
* Disable unused features (`--no-web`, `--no-skills`) for speed
* Resume instead of restarting long tasks

---

## Troubleshooting

### Missing API Key

```bash
export OPENAI_API_KEY="your_key"
# or
python -m sciagent --api-key YOUR_KEY "task"
```

### Task Took Too Long

```bash
python -m sciagent --max-iterations 10 "simple task"
```

### Debugging Errors

```bash
python -m sciagent --debug "problematic task"
```

---

## Getting Help

```bash
python -m sciagent --help
```

---

This quick start guide documents the stable, supported interface.
Advanced configuration and internal APIs are covered separately.
