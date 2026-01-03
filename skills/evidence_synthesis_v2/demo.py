#!/usr/bin/env python3
"""
Evidence Synthesis Skill v2.1 - File-Memory Pattern Demos

Key principle: Save raw content to files, extract key points, read only what you need.
"""

# =============================================================================
# DEMO 1: Simple (10-12 iterations)
# =============================================================================

SIMPLE_DEMO = """
Compare CRISPR systems (Cas9, Cas12a, Base Editor, Prime Editor).

Search once, create runs/comparison.md with:
- Comparison table (efficiency, specificity, use case)
- All claims cited [1][2][3]
- References with 📗📙🌐 indicators

Keep under 60 lines.
"""

# =============================================================================
# DEMO 2: File-Memory Pattern (15-20 iterations)
# =============================================================================

FILE_MEMORY_DEMO = """
CRISPR Research - File Memory Pattern

## SETUP
mkdir -p runs/workspace/raw runs/workspace/extracted runs/output
Create runs/workspace/extracted/notes.md with "# Research Notes"
Create runs/workspace/extracted/citations.md with "# Citations"

## COLLECT (save each source immediately)

Search 1: "CRISPR Cas9 Cas12a efficiency comparison 2024"
→ Save raw results to runs/workspace/raw/source_001.md
→ Extract 3-5 bullet key points to notes.md
→ Add citation to citations.md
→ Clear context

Search 2: "base editor prime editor efficiency 2024"  
→ Save raw results to runs/workspace/raw/source_002.md
→ Extract 3-5 bullet key points to notes.md
→ Add citation to citations.md
→ Clear context

## SYNTHESIZE (read only extracted notes)
Read runs/workspace/extracted/notes.md
Read runs/workspace/extracted/citations.md

Create runs/output/report.md in chunks:
- Edit 1: Headers only
- Edit 2: Comparison table (15 lines)
- Edit 3: Key findings with [1][2] citations (15 lines)
- Edit 4: References (10 lines)

Each edit max 20 lines.
"""


# =============================================================================
# DEMO 3: Complex with Analysis (25-35 iterations)
# =============================================================================

COMPLEX_DEMO = """
CRISPR Research - Full Analysis with File Memory

## SETUP
mkdir -p runs/workspace/raw runs/workspace/extracted runs/workspace/analysis runs/output

## COLLECT PHASE (save everything)

Search 1: "CRISPR Cas9 efficiency clinical trials 2024"
→ Save to runs/workspace/raw/source_001.md
→ Extract to notes.md: 3-5 bullets
→ Add citation

Search 2: "Cas12a Cas9 comparison specificity"
→ Save to runs/workspace/raw/source_002.md
→ Extract to notes.md
→ Add citation

Search 3: "base editor prime editor therapeutic applications"
→ Save to runs/workspace/raw/source_003.md  
→ Extract to notes.md
→ Add citation

## DATA EXTRACTION
Read notes.md, create runs/workspace/extracted/data.csv:
source_id,system,efficiency,specificity,best_use,limitation

## ANALYSIS
Create runs/workspace/analysis/compare.py:
- Load data.csv
- Print comparison statistics
- (no plots needed)

Run the analysis script.

## REPORT (chunked writes)
Read notes.md and data.csv (NOT raw files)

Create runs/output/report.md:
- Edit 1: Headers (5 lines)
- Edit 2: Summary with citations (15 lines)
- Edit 3: Comparison table (15 lines)
- Edit 4: Key findings [1][2][3] (20 lines)
- Edit 5: References 📗📙🌐 (10 lines)

Each edit max 20 lines.
"""


# =============================================================================
# PRINT MENU
# =============================================================================

def print_menu():
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║         EVIDENCE SYNTHESIS SKILL v2.1 - FILE MEMORY PATTERN                  ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  KEY PRINCIPLE: Save raw data to files, extract key points,                  ║
║                 read only what you need for each step.                       ║
║                                                                              ║
║  WORKSPACE STRUCTURE:                                                        ║
║    runs/workspace/raw/        ← Full content (archive)                       ║
║    runs/workspace/extracted/  ← Key points (LLM reads this)                  ║
║    runs/output/               ← Final deliverables                           ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  SIMPLE (10-12 iter):      python -m sciagent --max-iterations 12           ║
║  FILE MEMORY (15-20 iter): python -m sciagent --max-iterations 20           ║
║  COMPLEX (25-35 iter):     python -m sciagent --max-iterations 35           ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")


def get_demo(name: str) -> str:
    demos = {
        "simple": SIMPLE_DEMO,
        "memory": FILE_MEMORY_DEMO,
        "complex": COMPLEX_DEMO,
    }
    return demos.get(name.lower(), "")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        demo = get_demo(sys.argv[1])
        if demo:
            print(demo)
        else:
            print(f"Unknown demo. Available: simple, memory, complex")
    else:
        print_menu()
        print("\n" + "="*60)
        print("FILE MEMORY DEMO (recommended):")
        print("="*60)
        print(FILE_MEMORY_DEMO)
