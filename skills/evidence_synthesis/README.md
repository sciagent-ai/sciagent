# Evidence Synthesis Skill v2

Scientific evidence gathering with **proper citations and references**.

## Key Features

- ✅ **Every claim cited** - No uncited facts
- ✅ **Source quality tracking** - 📗 peer-reviewed, 📙 preprint, 📘 government, 🌐 web
- ✅ **Rate limit safe** - "Search Once, Fetch Deep" strategy
- ✅ **Structured outputs** - evidence_synthesis.md, sources.md, data/

## Installation

```bash
# 1. Copy skill to your sciagent
cp -r evidence_synthesis /path/to/sciagent/skills/

# 2. Replace web_search.py (fixes rate limiting)
cp evidence_synthesis/web_search.py /path/to/sciagent/tools/core/web_search.py

# 3. Remove tool-per-iteration limit (see below)
```

### Remove Tool Limit

Find and modify in `agent.py`:

```python
# Find this line (around line 200-300):
if tool_count >= 15:
    print("⚠️ Warning: Maximum tool executions...")

# Change to:
if tool_count >= 50:  # Increased limit
```

Or search:
```bash
grep -rn "Maximum tool executions\|tool_count.*15\|max.*tool" sciagent/
```

## Quick Test (10-15 iterations)

```bash
python -m sciagent --max-iterations 15 "
Research Task: CRISPR Gene Editing Systems Comparison

STEP 1 - ONE comprehensive search:
web_search('CRISPR Cas9 Cas12a base editing prime editing efficiency comparison 2024')

STEP 2 - Fetch top 3 results:
web_fetch on top 3 URLs

STEP 3 - Create evidence_synthesis.md with:
- Comparison table (ALL cells cite sources like [1], [2])
- Key findings (each cited)
- Contradictions between sources
- References section with quality indicators

OUTPUT: evidence_synthesis.md, sources.md
"
```

## Search Strategy

### ❌ Don't: Multiple Searches
```
web_search("CRISPR Cas9")
web_search("CRISPR Cas12a")
web_search("base editing")
→ Rate limiting → 429 errors → Failure
```

### ✅ Do: Search Once, Fetch Deep
```
web_search("CRISPR Cas9 Cas12a base editing comparison 2024")
→ Get URLs

web_fetch(url_1)
web_fetch(url_2)
web_fetch(url_3)
→ Full content, no rate limits
```

## Output Structure

```
output/
├── evidence_synthesis.md   # Main report with [citations]
│   ├── Executive Summary
│   ├── Methods
│   ├── Findings (all cited)
│   ├── Evidence Quality Table
│   ├── Contradictions
│   ├── Hypotheses
│   └── References [1], [2], ...
│
├── sources.md              # Detailed source tracking
│   ├── [1] Full citation + key claims
│   ├── [2] Full citation + key claims
│   └── Excluded sources + reasons
│
└── data/
    └── extracted_data.csv  # With source_id column
```

## Citation Format

```markdown
## Findings

CRISPR-Cas9 achieves 85% on-target efficiency in HEK293 cells [1],
while Cas12a shows 72% efficiency but higher specificity [2].
These findings conflict with a recent preprint reporting comparable
efficiency for both systems [3].

## References

[1] 📗 Smith J, Lee K. "Cas9 Efficiency Study." *Nature Methods*. 2024.
    DOI: 10.1038/xxx. URL: https://nature.com/...

[2] 📗 Chen A et al. "Cas12a Specificity." *Cell*. 2024.
    URL: https://cell.com/...

[3] 📙 Wang B. "CRISPR Comparison." *bioRxiv*. 2024.
    URL: https://biorxiv.org/...
```

## Source Quality Indicators

| Emoji | Type | Trust Level |
|-------|------|-------------|
| 📗 | Peer-reviewed | HIGH - Nature, Science, Cell, NEJM |
| 📙 | Preprint | MEDIUM - arXiv, bioRxiv, medRxiv |
| 📘 | Government | HIGH - .gov, WHO, CDC |
| 📂 | Repository | MEDIUM - GitHub datasets |
| 📖 | Encyclopedia | LOW - Wikipedia (background only) |
| 🌐 | Web | LOW - Blogs, general websites |

## Files

```
evidence_synthesis/
├── metadata.yaml      # Triggers: research, evidence, hypothesis, etc.
├── instructions.md    # Detailed workflow with citation requirements
├── skill.py           # Domain detection + prompt enhancement
├── web_search.py      # Fixed search with rate limiting (copy to tools/)
├── demo.py            # Test tasks
└── README.md          # This file
```

## Troubleshooting

### Rate Limiting (429 errors)
- The fixed `web_search.py` handles this automatically
- Uses exponential backoff (2s, 4s, 8s, 16s, 32s)
- Minimum 1.5s between requests

### Tool Limit Reached
- Find `tool_count >= 15` in `agent.py`
- Increase to 50 or remove the check

### Missing Citations in Output
- The skill instructions require citations
- If agent ignores, add to task: "EVERY claim must have [citation]"

## Domain Detection

The skill auto-detects domain and prioritizes sources:

| Domain | Detected By | Priority Sources |
|--------|-------------|------------------|
| Biology | protein, gene, CRISPR | PubMed, bioRxiv |
| Medicine | patient, clinical, drug | PubMed, Cochrane |
| Chemistry | molecule, reaction | PubChem, ACS |
| Physics | quantum, particle | arXiv |
| Data Science | ML, neural network | arXiv cs.LG, Papers With Code |
