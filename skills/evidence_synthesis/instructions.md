# Evidence Synthesis Skill v2

You are operating in **Evidence Synthesis Mode** - a rigorous scientific research workflow that produces properly cited, reproducible analyses.

## ⚠️ CRITICAL: Citation Requirements

**Every claim must be cited.** No exceptions.

- Use numbered citations: [1], [2], [3]
- Track ALL sources in a references section
- Include: Authors, Title, Source, Year, URL, DOI (if available)
- Mark source quality: 📗 peer-reviewed, 📙 preprint, 📘 government, 🌐 web

---

## Search Strategy: Search Once, Fetch Deep

### ❌ DON'T: Multiple Rapid Searches
```
web_search("CRISPR Cas9 efficiency")
web_search("CRISPR Cas12a efficiency")  
web_search("base editing comparison")
web_search("prime editing 2024")
→ 4 API calls → Rate limiting → Failure
```

### ✅ DO: One Comprehensive Search + Deep Fetches
```
web_search("CRISPR Cas9 Cas12a base editing prime editing efficiency comparison 2024")
→ Returns 5-10 results with URLs

web_fetch(url_1)  # Full content from top result
web_fetch(url_2)  # Full content from second result
web_fetch(url_3)  # Full content from third result
→ Rich data, no rate limiting
```

### Search Query Construction

Combine ALL key terms into ONE query:
- Topic + Subtopics + Comparison terms + Year
- Example: `"solid state electrolyte lithium battery ionic conductivity comparison review 2024"`

Maximum searches per task: **2**
- First search: Main comprehensive query
- Second search (if needed): Fill specific gap identified from first search

---

## Workflow Phases

### PHASE 1: Plan & Search (1-2 tool calls)

1. **Construct comprehensive query** combining:
   - Main topic
   - All comparison items
   - Key metrics of interest
   - "review" or "comparison" or "2024"

2. **Execute ONE search**:
   ```
   web_search(query="[comprehensive query]", num_results=8)
   ```

3. **Record all sources immediately** - even before reading content

### PHASE 2: Deep Fetch (3-5 tool calls)

1. **Prioritize sources by type**:
   - 📗 Peer-reviewed journals (Nature, Science, Cell, etc.)
   - 📙 Preprints (arXiv, bioRxiv, medRxiv)
   - 📘 Government sources (.gov)
   - 📂 Data repositories (GitHub datasets)
   - 🌐 Other web sources (use sparingly)

2. **Fetch top 3-5 sources**:
   ```
   web_fetch(url="[best_source_url]")
   ```

3. **Extract from each source**:
   - Key claims with page/section reference
   - Numerical data (sample sizes, effect sizes, percentages)
   - Methodology notes
   - Stated limitations
   - Author names and publication year

### PHASE 3: Evidence Compilation

Create `sources.md` tracking ALL sources:

```markdown
# Sources

## Included Sources (Cited)

[1] 📗 Smith J, Jones A. "Title of Paper." Nature. 2024.
    URL: https://...
    DOI: 10.1234/...
    Key data: efficacy 95%, n=500
    Quality: Peer-reviewed, large sample

[2] 📙 Lee K et al. "Preprint Title." bioRxiv. 2024.
    URL: https://...
    Key data: mechanism analysis
    Quality: Preprint, not yet peer-reviewed
    
## Excluded Sources (with reason)

[X1] Blog post - not peer reviewed
[X2] 2018 paper - outdated for this fast-moving field
```

### PHASE 4: Synthesis with Citations

Write findings with inline citations:

```markdown
## Findings

CRISPR-Cas9 demonstrates on-target efficiency of 70-90% in mammalian cells [1],
while Cas12a shows slightly lower efficiency (60-80%) but higher specificity [2].
However, these findings are contested - a recent preprint reports comparable 
efficiency for both systems under optimized conditions [3].

Base editors achieve precise single-nucleotide changes with 50-70% efficiency [4],
though off-target RNA editing remains a concern [5]. Prime editing offers the
highest precision but lowest efficiency (10-50%) [6].

**Key contradiction:** Sources [1] and [3] disagree on Cas9 vs Cas12a efficiency.
This may be due to different cell types used (HEK293 vs primary T cells) [3].
```

### PHASE 5: Data Extraction

Create `data/extracted_data.csv`:

```csv
source_id,system,metric,value,unit,sample_size,cell_type,year,notes
1,Cas9,on_target_efficiency,85,percent,500,HEK293,2024,
1,Cas9,off_target_rate,0.5,percent,500,HEK293,2024,
2,Cas12a,on_target_efficiency,72,percent,300,HEK293,2024,
3,Base_Editor,efficiency,65,percent,200,iPSC,2024,ABE8e variant
```

### PHASE 6: Analysis (if quantitative data available)

Create `data/analysis.py`:

```python
"""
Evidence synthesis analysis.
Sources: [1] Smith 2024, [2] Lee 2024, [3] Chen 2024
"""
import pandas as pd
import matplotlib.pyplot as plt

# Load extracted data
df = pd.read_csv('extracted_data.csv')

# Analysis with source tracking
print("Data sources:", df['source_id'].unique())

# Weighted mean (by sample size)
# Forest plot
# Heterogeneity assessment
```

### PHASE 7: Conclusions & Hypotheses

All conclusions must:
1. Cite supporting evidence
2. Note contradicting evidence
3. Acknowledge uncertainty
4. Be falsifiable

```markdown
## Conclusions

Based on evidence from 5 peer-reviewed sources [1-4, 6] and 1 preprint [5]:

1. **Supported conclusion:** Cas9 remains the most efficient system for 
   standard knockouts [1, 2, 4]. Confidence: HIGH (consistent across sources)

2. **Contested conclusion:** Cas12a specificity advantage is unclear.
   Sources [2, 3] support higher specificity, but [5] found no difference.
   Confidence: MEDIUM (conflicting evidence)

3. **Knowledge gap:** No head-to-head comparison of all four systems 
   in primary human T cells exists in the literature.

## Hypothesis

Based on gap identified above:

**H1:** Prime editing will show higher efficiency in primary T cells 
compared to immortalized cell lines due to [mechanism from source 4].

- **Testable prediction:** PE efficiency >30% in T cells vs <20% in HEK293
- **Required experiment:** Side-by-side comparison in both cell types
- **Sample size needed:** n=100 per condition for 80% power (α=0.05)
```

---

## Output Files Structure

```
output/
├── evidence_synthesis.md    # Main report with all citations
├── sources.md               # Detailed source tracking
├── references.bib           # BibTeX format (optional)
├── data/
│   ├── extracted_data.csv   # Quantitative data with source_id
│   └── analysis.py          # Reproducible analysis
└── figures/                  # If analysis generates plots
    └── comparison_chart.png
```

---

## Evidence Synthesis Report Template

```markdown
# Evidence Synthesis: [Topic]

**Generated:** [Date]
**Query:** [Original search query]
**Sources analyzed:** [N] peer-reviewed, [M] preprints, [K] other

## Executive Summary

[2-3 sentences with key findings. Cite sources.]

## Methods

- Search query: "[exact query used]"
- Search date: [date]
- Sources included: [N] of [M] results
- Inclusion criteria: [criteria]
- Exclusion criteria: [criteria]

## Findings

### [Subtopic 1]
[Findings with citations]

### [Subtopic 2]
[Findings with citations]

## Evidence Quality Assessment

| Source | Type | Sample Size | Methodology | Risk of Bias |
|--------|------|-------------|-------------|--------------|
| [1]    | RCT  | 500         | Double-blind| Low          |
| [2]    | Preprint | 50     | Open-label  | Medium       |

## Contradictions & Uncertainties

| Claim | Source A | Source B | Possible Explanation |
|-------|----------|----------|---------------------|
| ...   | [1]      | [3]      | Different methods   |

## Knowledge Gaps

1. [Gap 1] - No studies have examined...
2. [Gap 2] - Conflicting evidence on...

## Hypotheses

### Hypothesis 1: [Title]
- **Statement:** [Falsifiable statement]
- **Supporting evidence:** [Citations]
- **Contradicting evidence:** [Citations or "None identified"]
- **Proposed test:** [Brief experimental design]

## References

[1] 📗 Author A, Author B. "Title." *Journal*. Year. DOI: xxx. URL: xxx
[2] 📙 Author C et al. "Title." *bioRxiv*. Year. URL: xxx
[3] 📘 Agency. "Report Title." Year. URL: xxx

## Appendix: Excluded Sources

| Source | Reason for Exclusion |
|--------|---------------------|
| [X1]   | Published before 2020|
| [X2]   | Blog, not peer-reviewed |
```

---

## Quality Checklist

Before completing, verify:

- [ ] Every factual claim has a citation [N]
- [ ] All sources listed in References section
- [ ] Source quality indicated (📗📙📘🌐)
- [ ] Contradictions explicitly documented
- [ ] Uncertainty acknowledged where appropriate
- [ ] Hypotheses are falsifiable
- [ ] Data extraction is reproducible (CSV + source_id)
- [ ] Maximum 2 web_search calls used

---

## Common Mistakes to Avoid

❌ **No citations:** "CRISPR is 90% efficient" 
✅ **With citation:** "CRISPR-Cas9 achieves 90% efficiency in HEK293 cells [1]"

❌ **Vague sourcing:** "Studies show..."
✅ **Specific sourcing:** "Three RCTs [1-3] demonstrate..."

❌ **Ignoring contradictions:** Only citing supporting evidence
✅ **Balanced:** "Source [1] found X, but [2] found Y, possibly due to Z"

❌ **Multiple rapid searches:** 5 searches in a row
✅ **Strategic searching:** 1 comprehensive search + 3-5 deep fetches

❌ **Missing source quality:** All sources treated equally  
✅ **Quality-aware:** "Peer-reviewed evidence [1,2] suggests X; preprint [3] adds..."
