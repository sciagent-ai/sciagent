"""
Workspace Pattern - Agent-Level Data Accumulation Handler

This module provides intelligent task complexity detection and workspace
guidance for handling large data accumulation tasks in scientific computing.
"""

import re
from enum import Enum
from typing import List, Tuple


class TaskComplexity(Enum):
    SIMPLE = "simple"      # Direct execution, no workspace needed
    COMPLEX = "complex"    # Needs workspace pattern


# Indicators that suggest data accumulation
COMPLEXITY_INDICATORS = [
    # Scope indicators
    (r'\b(all|every|each|multiple|many|several|various)\b', 1),
    (r'\b(comprehensive|thorough|complete|full|extensive|detailed)\b', 2),
    
    # Action indicators suggesting iteration
    (r'\b(compare|analyze|evaluate|assess|review|summarize)\b', 1),
    (r'\b(identify|find|determine|discover|list)\s+(all|best|key|main)\b', 2),
    
    # Output indicators
    (r'\b(report|document|summary|analysis)\b', 1),
    (r'\b(save|output|write|store|export)\s+(to|in|results?)\b', 2),
    (r'\b(folder|directory)\b', 1),
    
    # Data source indicators
    (r'\b(database|query|records?|rows?|entries)\b', 1),
    (r'\b(simulation|monte\s*carlo|iterations?)\b', 2),
    (r'\b(files?|csvs?|jsons?|xmls?)\s+(in|from|across)\b', 1),
    (r'\b(api|endpoint|fetch|request)\s+(all|multiple)\b', 1),
    
    # Research indicators
    (r'\b(research|literature|papers?|studies|evidence)\b', 1),
    (r'\b(clinical\s+trial|endpoints?|biomarkers?)\b', 2),
    (r'\b(systematic|meta-?analysis)\b', 2),
    
    # Processing scope
    (r'\b(process|handle|transform)\s+(all|each|every|multiple)\b', 1),
    (r'\b(batch|bulk|mass)\s+\w+', 1),
]

# Indicators of simple tasks
SIMPLE_INDICATORS = [
    r'^what\s+is\b',
    r'^how\s+(do|does|to)\b',
    r'^define\b',
    r'^explain\s+\w+\s*$',
    r'\b(quick|brief|simple|single|one)\b',
    r'^calculate\s+\d',
]


def detect_complexity(task: str) -> Tuple[TaskComplexity, int, List[str]]:
    """
    Detect if a task will accumulate data and needs workspace pattern.
    
    Returns:
        (complexity, score, matched_indicators)
    """
    task_lower = task.lower()
    score = 0
    matches = []
    
    # Check for simple indicators first
    for pattern in SIMPLE_INDICATORS:
        if re.search(pattern, task_lower, re.IGNORECASE):
            return (TaskComplexity.SIMPLE, 0, ["simple_indicator"])
    
    # Score complexity indicators
    for pattern, weight in COMPLEXITY_INDICATORS:
        if re.search(pattern, task_lower, re.IGNORECASE):
            score += weight
            matches.append(pattern)
    
    # Task length as minor factor
    if len(task.split()) > 40:
        score += 1
        matches.append("long_task")
    
    # Threshold: score >= 3 means complex
    if score >= 3:
        return (TaskComplexity.COMPLEX, score, matches)
    else:
        return (TaskComplexity.SIMPLE, score, matches)


def get_workspace_guidance(output_folder: str = "workspace") -> str:
    """Get the workspace pattern instructions for complex tasks."""
    return f"""
═══════════════════════════════════════════════════════════════════════════════
⚠️  COMPLEX TASK DETECTED - USE WORKSPACE PATTERN
═══════════════════════════════════════════════════════════════════════════════

This task will accumulate data. To avoid context overload, use file-based memory:

## SETUP (do first)
```bash
mkdir -p {output_folder}/raw {output_folder}/extracted output
```

## FOR EACH DATA OPERATION (search, query, fetch, compute):
1. Execute the operation
2. SAVE full results to {output_folder}/raw/result_NNN.md (or .json, .csv)
3. EXTRACT key points (3-5 bullets or key values)
4. APPEND summary to {output_folder}/extracted/notes.md
5. CLEAR context - data is saved, don't hold it

## FINAL OUTPUT
- Read {output_folder}/extracted/notes.md (small, safe)
- DO NOT read {output_folder}/raw/* (too large)
- Write output in chunks (max 20-30 lines per edit)

## WHY THIS PATTERN?
Context window is limited. Holding multiple large results = overload = failures.
File system has unlimited storage. Save there, read selectively.

═══════════════════════════════════════════════════════════════════════════════
"""


def get_task_guidance(task: str) -> str:
    """
    Main entry point: analyze task and return appropriate guidance.
    
    Add this to your agent's system prompt for complex task handling.
    """
    complexity, score, matches = detect_complexity(task)
    
    if complexity == TaskComplexity.COMPLEX:
        return f"[Complexity Score: {score}] {get_workspace_guidance()}"
    else:
        return ""


# Agent prompt addition for general guidance
AGENT_PROMPT_ADDITION = """
## Task Execution Strategy

BEFORE starting any task, assess if it will accumulate data:

**SIMPLE tasks** (direct execution):
- Single query/search with direct answer
- Quick calculation
- Simple file read/write
- "What is X?", "Explain Y", "Calculate Z"

**COMPLEX tasks** (use workspace pattern):
- Multiple searches/queries to synthesize
- Processing many files
- Simulations with extensive output
- Reports requiring multiple data sources
- "Identify all", "Compare multiple", "Comprehensive analysis"

**For COMPLEX tasks, ALWAYS:**
1. Create workspace: `mkdir -p workspace/raw workspace/extracted output`
2. Save each data fetch to workspace/raw/
3. Extract key points to workspace/extracted/notes.md
4. Write output in chunks (max 25 lines per edit)
5. Never hold multiple large results in context

**Why:** File system = unlimited memory. Context = limited. Use files.
"""