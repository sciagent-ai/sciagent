# Evidence Synthesis Skill v2.1

Scientific evidence gathering with **file-based working memory**.

## The Problem

Complex tasks fail because:
```
Search 1 (5K chars) + Search 2 (5K) + Search 3 (5K) + ... = Context overload = 🤯
```

## The Solution

```
Search 1 → Save to file → Extract 5 bullets → Clear context
Search 2 → Save to file → Extract 5 bullets → Clear context
...
Read extracted notes only → Write report
```

## Architecture

```
runs/workspace/
├── raw/                    # Full content (NEVER sent to LLM)
│   ├── source_001.md       # Archived for later search
│   └── source_002.md
│
├── extracted/              # Key points (LLM reads THIS)
│   ├── notes.md            # 5 bullets per source
│   ├── data.csv            # Structured data
│   └── citations.md        # References
│
└── output/
    └── report.md           # Final deliverable
```

## Key Rules

| Rule | Why |
|------|-----|
| Save immediately | Don't hold search results in context |
| Extract aggressively | 5000 chars → 5 bullets |
| Read selectively | Only notes.md, not raw/ |
| Search saved data | `grep` in raw/, don't re-fetch |
| Write in chunks | Max 20 lines per edit |

## Installation

```bash
# Copy skill
cp -r evidence_synthesis /path/to/sciagent/skills/

# Replace web_search.py (fixes rate limiting)
cp evidence_synthesis/web_search.py /path/to/sciagent/tools/core/

# Increase tool limit in agent.py
# Find: if tool_count >= 15
# Change to: if tool_count >= 50
```

## Quick Test

```bash
python -m sciagent --max-iterations 12 "
Compare CRISPR systems (Cas9, Cas12a, Base Editor, Prime Editor).
Search once, create runs/comparison.md with comparison table, 
all claims cited [1][2][3], references with 📗📙🌐.
Keep under 60 lines.
"
```

## File Memory Demo

```bash
python -m sciagent --max-iterations 20 "
CRISPR Research - File Memory Pattern

SETUP:
mkdir -p runs/workspace/raw runs/workspace/extracted runs/output

COLLECT:
Search 1: 'CRISPR Cas9 Cas12a efficiency 2024'
→ Save to runs/workspace/raw/source_001.md
→ Extract 5 bullets to notes.md
→ Add citation
→ Clear context

Search 2: 'base editor prime editor comparison'
→ Save to runs/workspace/raw/source_002.md
→ Extract 5 bullets to notes.md
→ Add citation

SYNTHESIZE:
Read notes.md (NOT raw files)
Create runs/output/report.md in chunks:
- Edit 1: Headers
- Edit 2: Table (15 lines)
- Edit 3: Findings with [1][2] (15 lines)
- Edit 4: References (10 lines)
"
```

## Citation Format

```
📗 Peer-reviewed: Nature, Science, Cell
📙 Preprint: arXiv, bioRxiv
📘 Government: .gov, WHO, CDC
🌐 Web: Other

In report:
Cas9 achieves 85% efficiency [1], while Cas12a shows 72% [2].

References:
[1] 📗 Kim et al. Nature Methods. 2024. URL: ...
[2] 📙 Chen et al. bioRxiv. 2024. URL: ...
```

## Files

```
evidence_synthesis/
├── instructions.md       # File-memory workflow
├── skill.py              # Domain detection
├── workspace_manager.py  # Python helper (optional)
├── web_search.py         # Fixed search (copy to tools/)
├── demo.py               # Example tasks
└── README.md
```

## Context Budget

| Content | Send to LLM? |
|---------|--------------|
| Raw sources (5K each) | ❌ Never |
| Extracted notes (500 chars) | ✅ Yes |
| Citations (300 chars) | ✅ Yes |

**6 sources raw = 30K chars = 🤯 overload**
**6 sources extracted = 1K chars = ✅ safe**
