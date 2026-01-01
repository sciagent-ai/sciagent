# Evidence Synthesis Skill

A horizontal (cross-domain) skill for scientific evidence gathering, synthesis, contradiction detection, and hypothesis generation.

## Overview

This skill transforms SciAgent into a scientific research assistant capable of:

- **Domain Detection**: Automatically identifies the scientific domain (chemistry, biology, physics, etc.)
- **Multi-Source Search**: Orchestrates searches across academic, data, and methodology sources
- **Contradiction Detection**: Identifies conflicts between studies
- **Uncertainty Quantification**: Tracks confidence levels and evidence quality
- **Hypothesis Generation**: Creates testable hypotheses ranked by novelty, feasibility, and impact
- **Experimental Design**: Generates validation protocols with power analysis

## Skill Structure

```
evidence_synthesis/
├── metadata.yaml      # Skill configuration and triggers
├── instructions.md    # Detailed guidance for the agent
├── workflow.yaml      # Multi-phase execution workflow
├── skill.py           # Custom skill class with intelligence
├── demo.py            # Example research tasks
└── README.md          # This file
```

## Trigger Keywords

The skill activates when tasks contain:
- research, literature, papers, studies, evidence
- synthesis, hypothesis, experimental design
- predict, forecast, analyze data
- pubmed, arxiv, meta-analysis
- contradiction, uncertainty, confidence interval

## Domain Detection

The skill automatically detects and adapts to:

| Domain | Keywords | Priority Sources |
|--------|----------|------------------|
| Chemistry | molecule, reaction, synthesis | PubChem, RSC |
| Biology | protein, gene, cell | PubMed, bioRxiv |
| Medicine | patient, treatment, clinical | PubMed, Cochrane |
| Physics | quantum, particle, field | arXiv |
| Materials | alloy, battery, semiconductor | Materials Project |
| Data Science | ML, neural network, benchmark | arXiv cs.LG, Papers With Code |

## Output Artifacts

Every research task produces:

1. **evidence_synthesis.md** - Structured synthesis with contradiction matrix
2. **hypotheses.md** - Ranked testable hypotheses
3. **experimental_design.md** - Validation protocol with power analysis
4. **data/** - CSV files and reproducible analysis scripts
5. **figures/** - Visualizations (plots, heatmaps)

## Example Tasks

### Quick Demo (5-10 min)
```bash
python -m sciagent "Research LLM scaling laws. Extract data from Chinchilla, 
GPT-4 papers. Fit power law model. Predict performance gain from 10x compute 
in 2026. Create scaling_data.csv and projection plot."
```

### Full Research (20-40 min)
```bash
python -m sciagent "Research mRNA vaccine efficacy trends 2021-2024.
Collect efficacy data by variant. Create CSV with effect sizes and CIs.
Fit decay model to predict 2025-2026 booster timing.
Identify contradictions between studies.
Generate hypothesis about variant escape.
Design validation experiment."
```

See `demo.py` for more examples.

## Phase-Based Workflow

1. **Domain Detection & Planning**
   - Detect domain from query
   - Classify query type (factual, comparative, predictive, etc.)
   - Generate domain-specific search queries

2. **Multi-Source Evidence Gathering**
   - Search academic sources (arXiv, PubMed, etc.)
   - Fetch data sources and benchmarks
   - Extract key claims and metrics

3. **Contradiction & Uncertainty Analysis**
   - Compare claims across sources
   - Identify conflicting findings
   - Quantify overall confidence

4. **Quantitative Synthesis**
   - Create data CSVs
   - Run statistical analysis
   - Generate visualizations

5. **Hypothesis Generation**
   - Identify knowledge gaps
   - Generate testable hypotheses
   - Rank by novelty, testability, impact

6. **Experimental Design**
   - Design validation study
   - Power analysis for sample size
   - Define success criteria

## Integration with MCP

This skill is designed to work with MCP servers when available:

- Scientific Papers MCP → Academic search
- R MCP Server → Statistical analysis
- RDKit MCP → Chemistry computations
- Materials Project MCP → Materials data

Until MCP integration is complete, the skill uses `web_search` and `web_fetch` tools.

## Quality Checklist

The skill ensures:
- [ ] Multiple independent sources consulted
- [ ] Contradictions explicitly documented
- [ ] Uncertainty quantified where possible
- [ ] Hypotheses are falsifiable
- [ ] Experimental designs include controls
- [ ] All analyses are reproducible (scripts provided)
- [ ] Limitations acknowledged

## Future Enhancements

- [ ] MCP server integration for specialized sources
- [ ] Multi-LLM consensus for controversial findings
- [ ] Automated meta-analysis pipeline
- [ ] Citation network analysis
- [ ] Preregistration template generation
