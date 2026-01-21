# Agent Improvement Analysis

**Date**: January 15, 2026
**Analysis Based On**: Comparison of two SWE runs (sciagent_claude_project_1 vs task1_2)

---

## Executive Summary

Two runs were compared for a metasurface discovery task. Both used Claude as the underlying model, but produced vastly different quality results:

| Metric | sciagent_claude_project_1 | task1_2 |
|--------|---------------------------|---------|
| **Efficiency** | 85.9% | 67.3% |
| **Phase Coverage** | 1.96π (98% of 2π) | 0.32π (16% of 2π) |
| **Objective Score** | 0.908 | 0.447 |
| **Achieves Target** | Yes | No |
| **Novelty Score** | 0.52-0.85 | 0.47 (not novel) |

**Key Finding**: sciagent_claude_project_1 was run through **Claude Code** (Anthropic's CLI), while task1_2 was run through the **SimpleSWECode agent**. The model was identical - the agent architecture made the difference.

---

## What Claude Code Did Differently

### 1. Web Search for Research

Claude Code used web search to gather domain knowledge before implementation:

```
Web Search("metasurface unit cell families 1550nm near-infrared phase coverage efficiency 2025")
Web Search(""metasurface unit cell" 1550nm silicon nanostructures phase coverage efficiency literature review")
Web Search("metasurface unit cell library database nanostructure families 1550nm phase efficiency comparison")
```

SimpleSWECode has a web tool (`tools/atomic/web.py`) but it may not be properly registered or prompted for use.

### 2. Robust Error Recovery + Iteration

Claude Code hit multiple errors and kept iterating:

```
Bash(python novel_discovery.py)
  → Error: Command timed out after 2m 0.0s

Write(run_discovery_demo.py)           ← Created simplified version
Bash(python run_discovery_demo.py)
  → Error: JSON serialization...

Update(novel_discovery.py)              ← Fixed the bug
Bash(python run_discovery_demo.py)      ← Success!
```

It encountered 3+ errors and recovered from each. SimpleSWECode has spiral detection but may give up too early.

### 3. Explicit Validation Step

Claude Code's todo list included an explicit validation step:

```
☐ Perform literature scan
☐ Build library of known cell types
☐ Set up RCWA simulation framework
☐ Implement Bayesian Optimization
☐ Use BO+RCWA to discover novel unit-cell (N=10 budget)
☐ Validate discovered cell family novelty  ← EXPLICIT VALIDATION STEP
```

It then created and ran a dedicated `novelty_validator.py` to verify results met criteria.

### 4. Higher Iteration Limit

Claude Code ran ~20+ iterations to complete the task. SimpleSWECode defaults to `max_iterations=10`.

### 5. Result Verification Before Completion

Claude Code verified results met targets before marking complete:
- Ran `novelty_validator.py`
- Confirmed efficiency >= 85%
- Confirmed phase coverage >= 1.9π
- Confirmed novelty score met threshold

---

## Recommended Agent Improvements

### 1. Add Mandatory Verification Step

**Problem**: Agent marks tasks complete without verifying results meet criteria.

**Solution**: Modify system prompt to require verification:

```python
# In agent.py DEFAULT_SYSTEM_PROMPT, add:
"""
## Mandatory Verification

For ANY task producing measurable results:
1. Add explicit todo: "Verify [specific criteria]"
2. Run verification code BEFORE marking complete
3. If verification fails, iterate - don't complete

Example todos for optimization:
- ☐ Verify efficiency >= 85%
- ☐ Verify phase coverage >= 1.9π
- ☐ Verify novelty score > 0.5
"""
```

### 2. Strengthen Error-Driven Iteration

**Problem**: Agent may stop on errors instead of fixing and retrying.

**Solution**: Add concrete fix suggestions for common errors:

```python
# In agent.py, add or modify:
def _handle_error_with_fix(self, error: str, tool_name: str) -> str:
    """Instead of just warning, suggest concrete fix and continue."""

    if "timeout" in error.lower():
        return "Timeout hit. Create simplified version of script and retry."
    if "json" in error.lower() and "serial" in error.lower():
        return "JSON serialization error. Add .tolist() or custom encoder, then retry."
    if "import" in error.lower():
        return "Import error. Check dependencies, install if needed, then retry."
    if "typeerror" in error.lower() and "complex" in error.lower():
        return "Complex number error. Use .real before float operations, then retry."

    return "Error occurred. Analyze, fix the code, and retry."
```

### 3. Ensure Web Search is Available

**Problem**: Web search tool exists but may not be registered for main agent.

**Solution**: Register web tool in default registry:

```python
# In tools.py or create_default_registry:
from tools.atomic.web import WebSearchTool

def create_default_registry(working_dir: str = ".") -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(BashTool(working_dir))
    registry.register(ViewTool())
    registry.register(WriteFileTool(working_dir))
    registry.register(StrReplaceTool(working_dir))
    registry.register(WebSearchTool())  # ADD THIS
    return registry
```

Also update system prompt to encourage web search for research tasks.

### 4. Implement Goal-Aware Todo System

**Problem**: Todos track completion but not whether goals were achieved.

**Solution**: Enhance TodoItem with success criteria:

```python
# In state.py, enhance TodoItem:
@dataclass
class TodoItem:
    description: str
    status: TodoStatus = TodoStatus.PENDING
    success_criteria: Optional[str] = None  # e.g., "efficiency >= 0.85"
    measured_value: Optional[str] = None    # e.g., "0.859"
    verified: bool = False

    def can_mark_done(self) -> bool:
        """Only allow completion if verified or no criteria"""
        if self.success_criteria:
            return self.verified
        return True
```

### 5. Increase Max Iterations

**Problem**: Default `max_iterations=10` is too low for complex tasks.

**Solution**: Increase default or make dynamic:

```python
# In agent.py AgentConfig:
@dataclass
class AgentConfig:
    max_iterations: int = 50  # Increase from 10

    # Or add dynamic calculation:
    def get_max_iterations(self, task_complexity: str = "medium") -> int:
        complexity_map = {
            "simple": 10,
            "medium": 30,
            "complex": 50,
            "research": 75
        }
        return complexity_map.get(task_complexity, 30)
```

### 6. Add Baseline-First Strategy

**Problem**: task1_2 explored novel approaches that didn't meet targets, instead of first establishing a working baseline.

**Solution**: Add to system prompt:

```python
"""
## Baseline-First Development

For optimization/discovery tasks:
1. FIRST: Implement a known-working approach that meets targets
2. THEN: Add novelty incrementally while maintaining targets
3. Compare novel approaches against baseline
4. Only claim "novel" if it matches or exceeds baseline performance

Never accept a novel approach that performs worse than baseline.
"""
```

### 7. Add Result Extraction from Tool Output

**Problem**: Agent doesn't parse and verify results from command output.

**Solution**: Add output parsing guidance:

```python
"""
## Result Verification Pattern

After running code that produces metrics:
1. Parse the output for key numbers (efficiency, coverage, score)
2. Compare against targets explicitly
3. Only mark complete if ALL targets met

Example:
- Ran: python optimize.py
- Output: "Best efficiency: 0.673, Phase coverage: 0.32π"
- Targets: efficiency >= 0.85, coverage >= 1.9π
- Status: FAIL - must iterate, not complete
"""
```

### 8. Add Exploration vs Exploitation Balance

**Problem**: task1_2 over-explored (3 novel geometries) without sufficiently optimizing any.

**Solution**: Add guidance for limited budgets:

```python
"""
## Exploration vs Exploitation (Limited Budget)

When budget is limited (e.g., N=10 evaluations):
- DON'T split budget across many approaches
- DO pick most promising approach early
- Spend 70%+ of budget optimizing best candidate
- Only pivot if current approach clearly won't work

Pattern:
  - 20% exploration (test 2-3 ideas quickly)
  - 80% exploitation (optimize the winner)
"""
```

---

## Implementation Priority

| Priority | Improvement | Impact | Effort |
|----------|-------------|--------|--------|
| **P0** | Mandatory verification step | High | Low |
| **P0** | Increase max_iterations | High | Trivial |
| **P1** | Error-driven iteration | High | Medium |
| **P1** | Register web search tool | Medium | Low |
| **P2** | Goal-aware todo system | Medium | Medium |
| **P2** | Baseline-first guidance | Medium | Low |
| **P3** | Result extraction pattern | Medium | Medium |

---

## Comparison: Claude Code vs SimpleSWECode Architecture

| Feature | Claude Code | SimpleSWECode | Gap |
|---------|-------------|---------------|-----|
| Web search | Built-in, used proactively | Tool exists, not used | Prompt + registration |
| Error recovery | Iterates through errors | Has spiral detection | Needs fix suggestions |
| Validation step | Explicit in workflow | Not enforced | System prompt |
| Max iterations | ~50+ effective | 10 default | Config change |
| Result verification | Checks before complete | Marks done without | Todo enhancement |
| Context management | Sophisticated compression | Basic compression | Similar |
| Subagents | Specialized (Explore, Plan) | Generic types | Subagent design |

---

## Conclusion

The quality difference between the two runs was not due to the model (both used Claude) but due to **agent architecture**:

1. **Claude Code iterated through errors** - SimpleSWECode needs stronger retry behavior
2. **Claude Code verified results** - SimpleSWECode needs mandatory verification steps
3. **Claude Code used web search** - SimpleSWECode has the tool but doesn't use it
4. **Claude Code had more iterations** - SimpleSWECode's default limit is too low

The fixes are straightforward: enhance the system prompt, register tools properly, increase iteration limits, and enforce verification before completion.

---

## Files Changed (Recommended)

```
agent.py          - System prompt enhancements, iteration handling
state.py          - Goal-aware TodoItem
tools.py          - Register web search in default registry
tools/registry.py - Ensure all atomic tools registered
```

---

## References

- sciagent_claude_project_1: `/Users/shrutibadhwar/Documents/2026/SWERuns/sciagent_claude_project_1/`
- task1_2: `/Users/shrutibadhwar/Documents/2026/SWERuns/task1_2/`
- Claude Code trajectory: `sciagent_claude_project_1/claudetrajectory.txt`
