#!/bin/bash
# =============================================================================
# EVIDENCE SYNTHESIS SKILL - READY-TO-RUN DEMOS
# =============================================================================
# Copy the skill folder to your sciagent/skills/ directory first:
#   cp -r skills/evidence_synthesis /path/to/sciagent/skills/

# =============================================================================
# QUICK DEMO (5 min) - LLM Scaling Laws
# =============================================================================

echo "Running quick demo: LLM Scaling Laws Analysis"

python -m sciagent --max-iterations 30 "
Scientific Research Task: LLM Scaling Laws Analysis

1. EVIDENCE GATHERING:
   - Search for 'Chinchilla scaling laws' and 'GPT-4 scaling'
   - Find compute-optimal training relationships
   - Collect: model_size (params), training_tokens, benchmark_scores

2. DATA EXTRACTION:
   - Create data/scaling_data.csv with columns:
     model, params_B, tokens_B, year, benchmark, score
   - Include: GPT-3, Chinchilla, LLaMA, GPT-4 (estimated)

3. ANALYSIS:
   - Create data/scaling_analysis.py that:
     * Plots params vs performance
     * Fits power law: score = k * params^a
     * Calculates R² and prediction intervals

4. PREDICTION:
   - Predict benchmark scores for 10T parameter model
   - Quantify uncertainty in prediction

5. OUTPUT:
   - evidence_synthesis.md (1-2 pages)
   - data/scaling_data.csv
   - data/scaling_analysis.py  
   - figures/scaling_plot.png

Keep analysis focused and reproducible.
"


# =============================================================================
# MEDIUM DEMO (15 min) - Drug Efficacy Meta-Analysis
# =============================================================================

echo "Running medium demo: Drug Efficacy Meta-Analysis"

python -m sciagent --max-iterations 50 "
Research Task: GLP-1 Agonist Weight Loss Efficacy

OBJECTIVE: Meta-analysis of GLP-1 agonists for weight loss

PHASE 1 - Search:
- Find clinical trials for semaglutide, tirzepatide, liraglutide
- Focus on weight loss outcomes (% body weight reduction)

PHASE 2 - Extract:
- Create data/glp1_trials.csv:
  drug, trial_name, n, duration_weeks, weight_loss_pct, ci_lower, ci_upper, year

PHASE 3 - Analyze:
- Create data/meta_analysis.py:
  * Calculate weighted mean effect size
  * Create forest plot
  * Test for heterogeneity (I²)
  * Funnel plot for publication bias

PHASE 4 - Synthesize:
- Compare efficacy across drugs
- Identify which patient populations benefit most
- Note any contradicting findings

PHASE 5 - Hypothesis:
- Generate hypothesis about mechanism differences
- Propose validation study design

OUTPUTS:
- evidence_synthesis.md
- data/glp1_trials.csv
- data/meta_analysis.py
- figures/forest_plot.png
- hypotheses.md
"


# =============================================================================
# FULL DEMO (30 min) - Novel Materials Prediction
# =============================================================================

echo "Running full demo: Battery Materials Discovery"

python -m sciagent --max-iterations 80 "
Research Task: Next-Generation Solid-State Electrolyte Prediction

CONTEXT: Solid-state batteries promise higher energy density and safety,
but current electrolytes have conductivity/stability tradeoffs.

PHASE 1 - EVIDENCE GATHERING:
Search for solid-state electrolyte materials 2022-2024:
- LLZO (garnet-type)
- LGPS (sulfide-type)
- Polymer electrolytes
- Composite/hybrid approaches

For each, collect:
- Ionic conductivity (S/cm at room temp)
- Electrochemical stability window (V)
- Air/moisture stability
- Scalability/cost indicators
- Technology readiness level (TRL)

PHASE 2 - DATA COMPILATION:
Create data/electrolytes.csv with:
material, type, conductivity_log, stability_V, air_stable, 
scalable, trl, reference, year

Note any conflicting conductivity values between studies.

PHASE 3 - ANALYSIS:
Create data/analysis.py that:
- Plots conductivity vs stability (log scale for conductivity)
- Identifies Pareto frontier (best tradeoff)
- Highlights gaps in composition space
- Compares to liquid electrolyte baseline (1 mS/cm, 4.5V)

PHASE 4 - PREDICTION:
- Which material class most likely to achieve target?
  Target: 1 mS/cm conductivity + 5V stability + air stable
- Estimate timeline based on improvement rates
- Quantify confidence in prediction

PHASE 5 - HYPOTHESIS GENERATION:
Generate 2-3 hypotheses about:
- Novel compositions in underexplored space
- Processing innovations to improve performance
- Hybrid approaches combining benefits

For each hypothesis:
- Statement (falsifiable)
- Evidence base
- Prediction (what we'd observe if true)
- Contradicting evidence
- Confidence level

PHASE 6 - EXPERIMENTAL DESIGN:
For top hypothesis, design validation:
- Computational screening protocol (DFT + ML)
- Synthesis approach with controls
- Characterization methods
- Sample size for statistical significance
- Expected outcomes and decision criteria

OUTPUTS:
- evidence_synthesis.md (with contradiction matrix)
- data/electrolytes.csv
- data/analysis.py
- figures/pareto_frontier.png
- figures/composition_space.png
- hypotheses.md (ranked)
- experimental_design.md
"
