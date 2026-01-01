#!/usr/bin/env python3
"""
Evidence Synthesis Skill Demo

Example scientific research tasks that showcase the skill's capabilities.
Run these with:
    python -m sciagent "<task>"
"""

# =============================================================================
# DEMO TASKS - Ready to Run
# =============================================================================

DEMO_TASKS = {
    
    # ---------------------------------------------------------------------------
    # TIER 1: Impressive Scientific Research Demos
    # ---------------------------------------------------------------------------
    
    "mrna_prediction": """
    Research Task: mRNA Vaccine Efficacy Prediction for 2025-2026

    PHASE 1 - Evidence Gathering:
    - Search for mRNA vaccine efficacy studies (Pfizer, Moderna) 2021-2024
    - Find data on efficacy vs variants (Alpha, Delta, Omicron, BA.5, XBB, JN.1)
    - Collect: efficacy %, confidence intervals, time since vaccination, variant

    PHASE 2 - Data Extraction:
    - Create data/vaccine_efficacy.csv with columns:
      study, vaccine, variant, months_post_dose, efficacy_pct, ci_lower, ci_upper, n
    - Note any contradicting efficacy claims between studies

    PHASE 3 - Analysis:
    - Create data/analysis.py that:
      * Loads the CSV and plots efficacy decay curves by variant
      * Fits exponential decay model: efficacy = a * exp(-lambda * t)
      * Calculates weighted mean efficacy with heterogeneity (I²)
      * Creates forest plot of study effect sizes
      * Predicts efficacy at 12, 18, 24 months with confidence intervals

    PHASE 4 - Prediction:
    - Based on decay patterns, predict optimal booster timing for 2025-2026
    - Quantify prediction uncertainty

    PHASE 5 - Hypothesis Generation:
    - Generate 2-3 hypotheses about variant escape mechanisms
    - Propose experimental design to test the most tractable hypothesis

    OUTPUTS:
    - evidence_synthesis.md (with contradiction matrix)
    - data/vaccine_efficacy.csv
    - data/analysis.py
    - figures/ (decay curves, forest plot)
    - hypotheses.md
    - experimental_design.md
    """,
    
    "battery_materials": """
    Research Task: Solid-State Electrolyte Discovery for 2026 Batteries

    OBJECTIVE: Identify promising solid-state electrolyte materials for 
    next-generation lithium batteries that could reach commercialization by 2026.

    PHASE 1 - Literature Survey:
    - Search for solid-state electrolyte reviews 2022-2024
    - Focus on: LLZO, LGPS, sulfide, polymer, and hybrid electrolytes
    - Collect: ionic conductivity (S/cm), stability window (V), processing cost

    PHASE 2 - Data Compilation:
    - Create data/electrolytes.csv with:
      material, type, conductivity_S_cm, stability_V, cost_relative, 
      air_stability, scalability, TRL
    - Note conflicting conductivity values between studies

    PHASE 3 - Analysis:
    - Plot conductivity vs stability tradeoff (Pareto frontier)
    - Identify underexplored composition spaces
    - Compare against liquid electrolyte benchmarks

    PHASE 4 - Prediction:
    - Predict which material class most likely to reach 10 mS/cm + 5V window
    - Estimate timeline based on current TRL and improvement rates

    PHASE 5 - Experimental Design:
    - Design computational screening workflow for novel compositions
    - Propose synthesis + characterization protocol
    - Power analysis for validation sample size

    OUTPUTS:
    - evidence_synthesis.md
    - data/electrolytes.csv
    - data/pareto_analysis.py
    - figures/pareto_frontier.png
    - hypotheses.md (novel composition predictions)
    - experimental_design.md
    """,
    
    "protein_disorder": """
    Research Task: Intrinsically Disordered Protein Prediction

    SCIENTIFIC QUESTION: What sequence features predict intrinsic disorder, 
    and can we improve prediction for moonlighting proteins?

    PHASE 1 - Theory Survey:
    - Search literature for IDP prediction theories:
      * Charge distribution hypothesis
      * Proline content hypothesis  
      * Low complexity regions
      * Evolutionary pressure theories
    - Document contradictions between camps

    PHASE 2 - Benchmark Analysis:
    - Find existing IDP prediction benchmarks (DisProt, CAID)
    - Create data/methods_comparison.csv:
      method, year, accuracy, AUC, dataset, limitations

    PHASE 3 - Gap Analysis:
    - Identify where current predictors fail
    - Focus on moonlighting proteins (disorder-to-order transitions)
    - Quantify disagreement between predictors

    PHASE 4 - Hypothesis Generation:
    - Generate novel hypothesis about disorder prediction
    - Focus on underexplored features (local structure propensity, PTM sites)

    PHASE 5 - Experimental Design:
    - Design ML experiment to test hypothesis
    - Dataset: AlphaFold pLDDT as proxy for disorder
    - Features: sequence-based + predicted structure
    - Validation: 5-fold CV on DisProt holdout

    OUTPUTS:
    - evidence_synthesis.md (theory comparison)
    - data/methods_comparison.csv
    - hypotheses.md
    - experimental_design.md (ML protocol)
    - analysis/feature_importance.py
    """,
    
    # ---------------------------------------------------------------------------
    # TIER 2: Data-Driven Prediction Tasks
    # ---------------------------------------------------------------------------
    
    "climate_tipping": """
    Research Task: Arctic Sea Ice Tipping Point Analysis

    Analyze Arctic sea ice data to predict potential tipping points:

    1. GATHER DATA:
       - Search for Arctic sea ice extent datasets (NSIDC, PIOMAS)
       - Find September minimum extent data 1979-2024
       - Collect climate model projections (CMIP6)

    2. EXTRACT & ANALYZE:
       - Create data/sea_ice.csv with yearly minimum extent
       - Fit multiple models: linear, quadratic, logistic decline
       - Calculate Bayesian model comparison (BIC/AIC)
       - Plot with uncertainty bands

    3. PREDICT:
       - Forecast first ice-free September (< 1M km²)
       - Compare model predictions with uncertainty
       - Identify key assumptions and limitations

    4. HYPOTHESIS:
       - What feedback mechanism might trigger non-linear collapse?
       - Design observational study to detect early warning signals

    OUTPUTS: evidence_synthesis.md, data/sea_ice.csv, data/analysis.py, 
    figures/, hypotheses.md, experimental_design.md
    """,
    
    "drug_repurposing": """
    Research Task: Metformin Repurposing Opportunities

    Investigate metformin for indications beyond diabetes:

    1. EVIDENCE SYNTHESIS:
       - Search PubMed for metformin + cancer, aging, COVID, neurodegeneration
       - Compile: indication, study_type, effect_size, sample_size, year
       - Flag contradictory findings (e.g., cancer benefit vs harm)

    2. MECHANISM MAPPING:
       - Create network of metformin's known targets (AMPK, mTOR, etc.)
       - Link mechanisms to potential indications

    3. RANKING:
       - Score each indication by: evidence quality, mechanism plausibility,
         clinical feasibility, market potential
       - Identify top 3 repurposing candidates

    4. EXPERIMENTAL DESIGN:
       - For top candidate, design Phase II trial
       - Power analysis, endpoints, control group
       - Biomarkers for mechanism confirmation

    OUTPUTS: evidence_synthesis.md, data/metformin_indications.csv,
    mechanism_network.md, hypotheses.md, experimental_design.md
    """,
    
    # ---------------------------------------------------------------------------
    # TIER 3: Quick Demo Tasks (5-10 min)
    # ---------------------------------------------------------------------------
    
    "llm_scaling": """
    Quick Research: LLM Scaling Laws Analysis

    1. Search for scaling law papers (Chinchilla, GPT-4, etc.)
    2. Extract: model_size, training_tokens, benchmark_scores
    3. Create data/scaling_data.csv
    4. Fit power law: performance = k * (params)^a * (tokens)^b
    5. Predict: What performance gain from 10x compute in 2026?
    6. Create figures/scaling_projection.png

    Output: 1-page evidence_synthesis.md + data files
    """,
    
    "crispr_safety": """
    Quick Research: CRISPR Off-Target Effects

    1. Search for CRISPR off-target studies 2022-2024
    2. Compare: Cas9 vs Cas12a vs base editors vs prime editing
    3. Create comparison table with off-target rates
    4. Identify: Which system for which application?
    5. Hypothesis: What limits our detection of rare off-targets?

    Output: evidence_synthesis.md with comparison matrix
    """,
}


# =============================================================================
# DEMO RUNNER
# =============================================================================

def print_demo_menu():
    """Print available demo tasks."""
    print("\n" + "="*70)
    print("  EVIDENCE SYNTHESIS SKILL - DEMO TASKS")
    print("="*70)
    
    print("\n📊 TIER 1: Full Scientific Research Demos (20-40 min)\n")
    print("  mrna_prediction   - mRNA vaccine efficacy prediction 2025-2026")
    print("  battery_materials - Solid-state electrolyte discovery")
    print("  protein_disorder  - Intrinsically disordered protein prediction")
    
    print("\n📈 TIER 2: Data-Driven Prediction Tasks (15-25 min)\n")
    print("  climate_tipping   - Arctic sea ice tipping point analysis")
    print("  drug_repurposing  - Metformin repurposing opportunities")
    
    print("\n⚡ TIER 3: Quick Demos (5-10 min)\n")
    print("  llm_scaling       - LLM scaling laws analysis")
    print("  crispr_safety     - CRISPR off-target comparison")
    
    print("\n" + "-"*70)
    print("Run with:  python -m sciagent \"<paste task here>\"")
    print("Or:        python demo.py <task_name>")
    print("-"*70 + "\n")


def get_task(task_name: str) -> str:
    """Get task by name."""
    return DEMO_TASKS.get(task_name, "")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print_demo_menu()
    else:
        task_name = sys.argv[1]
        task = get_task(task_name)
        
        if task:
            print(f"\n📋 Task: {task_name}")
            print("-" * 50)
            print(task.strip())
            print("-" * 50)
            print(f"\nRun with:\n  python -m sciagent \"{task_name}\"")
            print(f"\nOr copy the task above and run:")
            print(f"  python -m sciagent \"<paste task>\"")
        else:
            print(f"❌ Unknown task: {task_name}")
            print_demo_menu()
