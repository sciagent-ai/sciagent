# Complex Research Task Template

## Architecture: File-Based Working Memory

For complex tasks, DON'T hold everything in context. Instead:

1. **Write to files immediately** after each step
2. **Read only what you need** for current step
3. **Summarize aggressively** - raw data → key points
4. **Checkpoint after each phase** - task can resume

---

## Phased Workflow

### PHASE 1: Setup & Planning
```
Create workspace:
- runs/workspace/notes.md       (running observations)
- runs/workspace/sources.md     (track all sources)
- runs/workspace/data/          (extracted data)
- runs/output/                  (final deliverables)

Write task plan to notes.md
```

### PHASE 2: Data Collection (One source at a time)
```
For each search/API call:
1. Execute search
2. IMMEDIATELY write key points to notes.md:
   "## Source 1: [Title]
   - Key finding: X
   - Data point: Y
   - Citation: [1] Author, Title, URL"
3. Clear search results from mind
4. Move to next source

DO NOT hold multiple search results in context simultaneously.
```

### PHASE 3: Data Extraction
```
Read notes.md (summaries only, not raw data)
Create data.csv with structured data
Each row references source_id
```

### PHASE 4: Analysis
```
Read data.csv
Run analysis code
Save results to runs/workspace/analysis_results.md
Save figures to runs/workspace/figures/
```

### PHASE 5: Synthesis
```
Read ONLY:
- notes.md (key points)
- analysis_results.md (findings)
- sources.md (for citations)

Write final document in chunks:
- output/report.md (section by section)
```

---

## Example: Complex CRISPR Analysis

### Task
"Compare CRISPR systems with efficiency data, run statistical analysis, generate figures, create cited report"

### Execution

**Step 1: Setup**
```bash
mkdir -p runs/workspace/data runs/workspace/figures runs/output
```

**Step 2: Create notes.md**
```markdown
# CRISPR Research Notes

## Task
Compare Cas9, Cas12a, Base Editors, Prime Editors

## Sources Collected
(will be filled as we search)

## Key Data Points
(will be filled as we extract)
```

**Step 3: Search + Immediate Note-Taking**
```
Search: "CRISPR Cas9 efficiency 2024"

IMMEDIATELY write to notes.md:
"## Source 1: Nature Methods 2024
- Cas9 on-target: 85% in HEK293
- Off-target: <1%
- Citation: [1] Kim et al, Nature Methods, 2024, URL..."

(Don't keep search results in context - they're in notes.md now)
```

**Step 4: Repeat for Each System**
```
Search Cas12a → write to notes.md → clear context
Search Base Editor → write to notes.md → clear context
Search Prime Editor → write to notes.md → clear context
```

**Step 5: Extract Structured Data**
```
Read notes.md
Create data/efficiency.csv:
source_id,system,efficiency,cell_type,year
1,Cas9,85,HEK293,2024
2,Cas12a,72,HEK293,2024
...
```

**Step 6: Analysis**
```python
# data/analysis.py
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('efficiency.csv')

# Create comparison chart
fig, ax = plt.subplots()
df.groupby('system')['efficiency'].mean().plot(kind='bar', ax=ax)
plt.savefig('../figures/efficiency_comparison.png')

# Save stats
stats = df.groupby('system')['efficiency'].describe()
stats.to_csv('stats_summary.csv')
```

**Step 7: Write Report (Section by Section)**
```
# Edit 1: Headers only
Create output/report.md with structure

# Edit 2: Executive Summary (10 lines)
Read notes.md, write summary

# Edit 3: Comparison Table (15 lines)
Read data/efficiency.csv, create table

# Edit 4: Analysis Results (15 lines)
Read figures/, stats_summary.csv, write findings

# Edit 5: References (10 lines)
Read sources.md, format citations
```

---

## Key Patterns

### Pattern 1: Immediate Externalization
```
❌ Bad: Search → Hold in context → Search → Hold → Search → Synthesize
✅ Good: Search → Write to file → Clear → Search → Write to file → Read files → Synthesize
```

### Pattern 2: Chunked Writing
```
❌ Bad: Generate 200-line document in one edit
✅ Good: Generate 20 lines, save, generate 20 lines, save...
```

### Pattern 3: Read-Only-What-You-Need
```
❌ Bad: "Read all my notes and all my data and all sources..."
✅ Good: "Read the efficiency column from data.csv for the comparison table"
```

### Pattern 4: Sub-Agents for Parallel Work
```
Main Agent:
├── task_agent: "Research Cas9, save to workspace/cas9.md"
├── task_agent: "Research Cas12a, save to workspace/cas12a.md"  
├── task_agent: "Research Base Editors, save to workspace/base.md"
└── Main: "Read workspace/*.md, create comparison report"
```

---

## Task Template for Complex Research

```
[TASK NAME]

## Setup
Create runs/workspace/ with notes.md and sources.md

## Phase 1: Data Collection
For each topic:
1. Search ONE topic
2. Write 3-5 bullet summary to notes.md immediately
3. Add citation to sources.md
4. Move to next topic

## Phase 2: Data Extraction  
Read notes.md, create data.csv with structured data

## Phase 3: Analysis
Create and run analysis.py, save results to workspace/

## Phase 4: Report (write in chunks)
Create output/report.md:
- Edit 1: Structure only
- Edit 2: Summary (max 10 lines)
- Edit 3: Table (max 15 lines)
- Edit 4: Findings (max 20 lines)
- Edit 5: References (max 10 lines)

## Rules
- Never hold more than ONE search result in context
- Each file edit under 30 lines
- Save after every step
```
