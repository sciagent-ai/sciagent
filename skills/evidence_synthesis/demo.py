#!/usr/bin/env python3
"""
Evidence Synthesis Skill v2 - Demo Tasks

These demos use "Search Once, Fetch Deep" strategy:
- Maximum 2 web_search calls
- 3-5 web_fetch calls for full content
- All outputs include proper citations
"""

# =============================================================================
# DEMO 1: Quick Test (10-15 iterations)
# =============================================================================

QUICK_TEST = """
Research Task: CRISPR Gene Editing Systems Comparison

GOAL: Compare Cas9, Cas12a, Base Editors, and Prime Editors with citations

STEP 1 - SEARCH (ONE comprehensive search):
web_search("CRISPR Cas9 Cas12a base editing prime editing efficiency specificity comparison review 2024")

STEP 2 - FETCH (get full content from top 3 results):
Use web_fetch on the top 3 URLs from search results

STEP 3 - CREATE evidence_synthesis.md with:

# CRISPR Editing Systems Comparison

**Generated:** [today's date]
**Sources:** [N] analyzed

## Executive Summary
[2-3 sentences summarizing findings WITH citations like [1], [2]]

## Comparison Table
| System | Efficiency | Specificity | Best Use Case | Source |
|--------|------------|-------------|---------------|--------|
| Cas9 | X% | Y | ... | [1] |
| Cas12a | X% | Y | ... | [2] |
| Base Editor | X% | Y | ... | [1,3] |
| Prime Editor | X% | Y | ... | [2] |

## Key Findings
[Each finding must have a citation]

## Contradictions
[Any disagreements between sources]

## References
[1] 📗 Author. "Title." Journal. Year. URL: ...
[2] 📙 Author. "Title." bioRxiv. Year. URL: ...
[3] 🌐 Author. "Title." URL: ...

STEP 4 - CREATE sources.md with detailed source information

OUTPUT FILES: evidence_synthesis.md, sources.md
"""


# =============================================================================
# DEMO 2: Full Research (20-30 iterations)
# =============================================================================

FULL_RESEARCH = """
Research Task: mRNA Vaccine Efficacy Analysis with Citations

OBJECTIVE: Synthesize evidence on mRNA vaccine efficacy across variants

PHASE 1 - SEARCH (ONE comprehensive query):
web_search("mRNA vaccine Pfizer Moderna efficacy Omicron BA.5 XBB JN.1 comparison clinical trial 2024")

PHASE 2 - DEEP FETCH (3-5 sources):
Fetch full content from:
- Top peer-reviewed source (if available)
- Top preprint (if relevant)
- Government/CDC data source (if available)

PHASE 3 - CREATE evidence_synthesis.md:

# mRNA Vaccine Efficacy: Evidence Synthesis

**Generated:** [date]
**Search Query:** "mRNA vaccine Pfizer Moderna efficacy Omicron..."
**Sources Analyzed:** [N]

## Executive Summary
[Key findings with citations]

## Methods
- Search date: [date]
- Sources included: [N] peer-reviewed, [M] preprints, [K] other
- Inclusion criteria: Published 2023-2024, human subjects, efficacy data

## Findings by Variant

### Original & Alpha
[Findings with citations]

### Delta  
[Findings with citations]

### Omicron (BA.1, BA.5, XBB, JN.1)
[Findings with citations]

## Evidence Quality Assessment

| Source | Type | Sample Size | Population | Risk of Bias |
|--------|------|-------------|------------|--------------|
| [1]    | RCT  | 10,000      | Adults     | Low          |
| [2]    | Observational | 50,000 | Mixed  | Medium       |

## Contradictions & Uncertainties

| Finding | Source A | Source B | Explanation |
|---------|----------|----------|-------------|
| XBB efficacy | [1]: 45% | [3]: 62% | Different populations |

## Knowledge Gaps
1. Limited data on [X] - no studies found
2. Conflicting evidence on [Y]

## Hypothesis
Based on evidence gap:
**H1:** [Testable hypothesis based on findings]
- Supporting evidence: [1, 2]
- Test: [Brief experimental design]

## References
[1] 📗 Author A et al. "Title." *NEJM*. 2024. DOI: xxx. URL: xxx
[2] 📙 Author B et al. "Title." *medRxiv*. 2024. URL: xxx
[3] 📘 CDC. "Report Title." 2024. URL: xxx

PHASE 4 - CREATE data/efficacy_data.csv:
source_id,vaccine,variant,efficacy_pct,ci_lower,ci_upper,sample_size,population,months_post_dose

PHASE 5 - CREATE sources.md with full source details

OUTPUT: evidence_synthesis.md, sources.md, data/efficacy_data.csv
"""


# =============================================================================
# DEMO 3: Materials Science (20-30 iterations)  
# =============================================================================

MATERIALS_DEMO = """
Research Task: Solid-State Battery Electrolytes Review

OBJECTIVE: Compare solid-state electrolyte materials with citations

SEARCH (ONE query):
web_search("solid state electrolyte lithium battery LLZO LGPS sulfide polymer ionic conductivity comparison review 2024")

FETCH top 3-4 results with web_fetch

CREATE evidence_synthesis.md with:
- Comparison table (material, conductivity, stability, cost) - ALL cited
- Contradictions in reported conductivity values
- Knowledge gaps
- References with quality indicators

CREATE data/electrolytes.csv with source_id for traceability

OUTPUT: evidence_synthesis.md, sources.md, data/electrolytes.csv
"""


# =============================================================================
# PRINT DEMO MENU
# =============================================================================

def print_menu():
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║         EVIDENCE SYNTHESIS SKILL v2 - DEMO TASKS                             ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  All demos use "Search Once, Fetch Deep" strategy:                          ║
║  • Maximum 2 web_search calls (avoid rate limiting)                         ║
║  • 3-5 web_fetch calls for full content                                     ║
║  • All outputs include proper [citations]                                   ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  QUICK TEST (10-15 iterations):                                             ║
║  python -m sciagent --max-iterations 15 "[paste QUICK_TEST]"               ║
║                                                                              ║
║  FULL RESEARCH (20-30 iterations):                                          ║
║  python -m sciagent --max-iterations 30 "[paste FULL_RESEARCH]"            ║
║                                                                              ║
║  MATERIALS DEMO (20-30 iterations):                                         ║
║  python -m sciagent --max-iterations 30 "[paste MATERIALS_DEMO]"           ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        demo_name = sys.argv[1].lower()
        demos = {
            "quick": QUICK_TEST,
            "full": FULL_RESEARCH,
            "materials": MATERIALS_DEMO,
        }
        if demo_name in demos:
            print(demos[demo_name])
        else:
            print(f"Unknown demo: {demo_name}")
            print(f"Available: {', '.join(demos.keys())}")
    else:
        print_menu()
        print("\nQUICK TEST TASK (copy this):\n")
        print("-" * 60)
        print(QUICK_TEST)
        print("-" * 60)
