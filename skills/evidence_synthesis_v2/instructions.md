# Evidence Synthesis Skill v2.1

## Core Principle: File-Based Working Memory

**Never hold large content in context. Save it, summarize it, read only what you need.**

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         MEMORY ARCHITECTURE                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   FETCH                    SAVE                      USE                │
│   ─────                    ────                      ───                │
│   web_search ─────────►  raw/source_001.md    (never sent to LLM)      │
│   web_fetch  ─────────►  raw/source_002.md    (searchable archive)     │
│   API call   ─────────►  raw/source_003.md                             │
│                               │                                         │
│                               ▼                                         │
│                          EXTRACT                                        │
│                          ───────                                        │
│                     Key points only                                     │
│                               │                                         │
│                               ▼                                         │
│                     extracted/notes.md    ◄──── LLM reads this         │
│                     extracted/data.csv                                  │
│                     extracted/citations.md                              │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Workspace Structure

```
runs/workspace/
├── raw/                      # Full fetched content (ARCHIVE)
│   ├── source_001.md         # Raw content from source 1
│   ├── source_002.md         # Raw content from source 2
│   └── manifest.json         # Index: id, url, title, type
│
├── extracted/                # Summaries (LLM READS THIS)
│   ├── notes.md              # Key points per source
│   ├── data.csv              # Structured data
│   └── citations.md          # Formatted references
│
└── analysis/                 # Code and results
    └── analysis.py

runs/output/                  # Final deliverables
└── report.md
```

---

## Workflow: Search → Save → Extract → Synthesize

### STEP 1: Setup Workspace
```bash
mkdir -p runs/workspace/raw runs/workspace/extracted runs/workspace/analysis runs/output
echo "# Research Notes" > runs/workspace/extracted/notes.md
echo "# Citations" > runs/workspace/extracted/citations.md
```

### STEP 2: For Each Search/Fetch

```
1. SEARCH or FETCH content

2. SAVE raw content immediately:
   File: runs/workspace/raw/source_001.md
   
   # Source 1: [Title]
   URL: [url]
   Type: peer_reviewed | preprint | government | web
   Retrieved: [date]
   ---
   [full content]

3. EXTRACT key points (3-5 bullets max):
   Append to: runs/workspace/extracted/notes.md
   
   ## [1] Source Title
   - Key finding 1
   - Key finding 2  
   - Data: X% efficiency
   
4. ADD citation:
   Append to: runs/workspace/extracted/citations.md
   
   [1] 📗 Author. "Title." Journal. Year. URL: ...

5. CLEAR context - content is saved, don't hold it
```

### STEP 3: If You Need Data Later
```
DON'T re-fetch. Search saved content:

grep "efficiency" runs/workspace/raw/*.md
cat runs/workspace/raw/source_001.md | head -50
```

### STEP 4: Synthesize
```
READ: runs/workspace/extracted/notes.md (small)
NOT:  runs/workspace/raw/* (large)

Write in chunks to: runs/output/report.md
```

---

## Key Rules

| Rule | Do | Don't |
|------|-----|-------|
| Save immediately | Search → Save to file | Hold search results in context |
| Extract aggressively | 5000 chars → 5 bullets | Keep full content |
| Read selectively | Read notes.md | Read all raw sources |
| Search saved data | grep in raw/ folder | Re-fetch from web |
| Write in chunks | 20 lines per edit | 200 line document |

---

## Citation Format

```
📗 Peer-reviewed: Nature, Science, Cell, NEJM
📙 Preprint: arXiv, bioRxiv, medRxiv  
📘 Government: .gov, WHO, CDC
📂 Repository: GitHub datasets
🌐 Web: Other sources
```

### notes.md format:
```markdown
## [1] CRISPR-Cas9 Efficiency Study
*URL: https://nature.com/...*
*Type: 📗 peer-reviewed*

- On-target efficiency: 85%
- Off-target rate: <1%
- Best for: Gene knockouts
```

### citations.md format:
```markdown
[1] 📗 Kim et al. "Title." Nature Methods. 2024. URL: ...
[2] 📙 Chen et al. "Title." bioRxiv. 2024. URL: ...
```

### Final report:
```markdown
Cas9 achieves 85% efficiency [1], while Cas12a shows 72% [2].
```

---

## Context Budget

| Content | Size | Send to LLM? |
|---------|------|--------------|
| Raw source (each) | 5,000 chars | ❌ Never |
| Extracted notes | 500 chars | ✅ Yes |
| Citations | 300 chars | ✅ Yes |
| **Total safe context** | ~1,000 chars | ✅ |

---

## Example Task Execution

**Setup:**
```bash
mkdir -p runs/workspace/raw runs/workspace/extracted runs/output
```

**Collect Source 1:**
```
Search "CRISPR Cas9 efficiency 2024"

Save full results → runs/workspace/raw/source_001.md

Extract to notes.md:
## [1] Cas9 Efficiency Study
- Efficiency: 85%
- Off-target: <1%

Add to citations.md:
[1] 📗 Kim et al. Nature Methods. 2024. URL: ...

Clear context → next source
```

**Collect Sources 2, 3:**
```
[Same pattern for each]
```

**Write Report (chunked):**
```
Read notes.md (small file only)

Edit 1: Create headers (5 lines)
Edit 2: Summary (15 lines)
Edit 3: Table (15 lines)
Edit 4: Findings with [1][2][3] (20 lines)
Edit 5: References (10 lines)
```

---

## Checklist

- [ ] Workspace directories created
- [ ] All sources saved to raw/
- [ ] Key points in notes.md (not raw content)
- [ ] Citations in citations.md
- [ ] Raw content NOT in LLM context
- [ ] Each edit under 25 lines
- [ ] All claims have [citations]
