# Tool Architecture: Atomic + Domain Modular Design

Based on Biomni's patterns for long-horizon scientific/engineering tasks.

---

## Layer 1: Atomic Tools (Always Loaded - 8-10 max)

These are **primitive operations** that compose into everything else:

```
atomic/
├── compute.py          # Python/Julia/R execution with sandboxing
├── file_ops.py         # read, write, edit (unified)
├── search.py           # glob + grep (unified)
├── shell.py            # bash execution
├── data_io.py          # load/save CSV, JSON, Parquet, HDF5, NetCDF
├── http.py             # fetch URLs, API calls
├── visualize.py        # matplotlib/plotly figure generation
└── version_control.py  # git operations
```

**Key principle**: Each atomic tool does ONE thing well. They're the "assembly language" of your agent.

| Atomic Tool | Operations | Why Atomic |
|-------------|-----------|------------|
| `compute` | `execute_python`, `execute_julia`, `execute_r` | Foundation for all analysis |
| `file_ops` | `read`, `write`, `edit`, `move`, `delete` | All file manipulation |
| `search` | `glob`, `grep`, `find_symbol` | All discovery |
| `data_io` | `load_data`, `save_data`, `convert_format` | Format-agnostic data handling |
| `http` | `fetch`, `post`, `query_api` | All external data access |
| `visualize` | `plot`, `save_figure`, `interactive_plot` | All visualization |

---

## Layer 2: Domain Modules (Loaded On-Demand)

Following Biomni's pattern, organize by scientific domain:

```
domain/
├── __init__.py                 # Domain registry & lazy loading
│
├── data_science/
│   ├── statistics.py           # hypothesis testing, regression, ANOVA
│   ├── ml_modeling.py          # sklearn, XGBoost, neural nets
│   ├── time_series.py          # forecasting, signal processing
│   └── dimensionality.py       # PCA, UMAP, t-SNE
│
├── engineering/
│   ├── simulation.py           # FEM, CFD interfaces
│   ├── optimization.py         # scipy.optimize, genetic algorithms
│   ├── signal_processing.py    # FFT, filtering, wavelets
│   └── control_systems.py      # transfer functions, PID
│
├── chemistry/
│   ├── molecular.py            # RDKit, molecular descriptors
│   ├── quantum_chem.py         # Psi4, ORCA interfaces
│   ├── databases.py            # PubChem, ChEMBL queries
│   └── reactions.py            # reaction prediction, retrosynthesis
│
├── materials/
│   ├── crystal.py              # pymatgen, structure analysis
│   ├── properties.py           # Materials Project, AFLOW queries
│   └── characterization.py     # XRD, spectroscopy analysis
│
├── biology/
│   ├── genomics.py             # sequence analysis, alignment
│   ├── proteomics.py           # UniProt, AlphaFold queries
│   ├── single_cell.py          # scanpy workflows
│   └── pathways.py             # KEGG, Reactome queries
│
├── physics/
│   ├── mechanics.py            # kinematics, dynamics
│   ├── electromagnetism.py     # field calculations
│   └── thermodynamics.py       # state equations, phase diagrams
│
└── geoscience/
    ├── spatial.py              # GIS operations, coordinate transforms
    ├── remote_sensing.py       # satellite data processing
    └── climate.py              # weather data, climate models
```

---

## Layer 3: Long-Horizon Task Support

Critical for complex scientific workflows. Biomni uses retrieval-augmented planning; here's a more explicit structure:

```
orchestration/
├── planning/
│   ├── task_decomposer.py      # Break complex tasks into subtasks
│   ├── dependency_graph.py     # Track task dependencies
│   └── plan_validator.py       # Verify plan feasibility
│
├── execution/
│   ├── checkpoint.py           # Save/restore execution state
│   ├── retry_handler.py        # Smart retry with backoff
│   └── parallel_executor.py    # Run independent subtasks in parallel
│
├── memory/
│   ├── working_memory.py       # Current task context
│   ├── episodic_memory.py      # What happened in this session
│   ├── semantic_memory.py      # Learned facts & patterns
│   └── procedural_memory.py    # Successful workflows to reuse
│
├── knowledge/
│   ├── protocol_library.py     # "Know-how" like Biomni
│   ├── best_practices.py       # Domain-specific guidelines
│   └── error_patterns.py       # Common failures & fixes
│
└── reflection/
    ├── progress_tracker.py     # Where are we in the plan?
    ├── self_evaluate.py        # Is this working?
    └── plan_reviser.py         # Adapt plan based on results
```

---

## Tool Loading Strategy (Avoiding Context Flood)

```python
class DomainAwareRegistry:
    """Load tools based on task domain detection"""

    # Always loaded - these are your primitives
    ATOMIC_TOOLS = [
        "compute", "file_ops", "search", "shell",
        "data_io", "http", "visualize", "version_control"
    ]

    # Loaded based on task classification
    DOMAIN_PROFILES = {
        "genomics": ["biology.genomics", "biology.proteomics", "data_science.statistics"],
        "materials": ["materials.crystal", "materials.properties", "chemistry.molecular"],
        "ml_analysis": ["data_science.ml_modeling", "data_science.statistics", "visualize"],
        "simulation": ["engineering.simulation", "engineering.optimization", "physics.mechanics"],
    }

    # Long-horizon tools - loaded for multi-step tasks
    ORCHESTRATION_TOOLS = [
        "planning.task_decomposer",
        "memory.working_memory",
        "reflection.progress_tracker"
    ]

    def load_for_task(self, task_description: str) -> List[Tool]:
        """Dynamically select tools based on task"""
        tools = self._load_atomic()  # Always 8 tools

        domain = self._classify_domain(task_description)
        tools += self._load_domain(domain)  # +3-5 domain tools

        if self._is_long_horizon(task_description):
            tools += self._load_orchestration()  # +3 planning tools

        return tools  # Total: 14-16 tools max per request
```

---

## Long-Horizon Task Flow

Here's how Claude Code-style task decomposition would work:

```
User: "Analyze the crystal structures in this dataset, predict their
       band gaps using ML, and identify candidates for solar cells"

┌─────────────────────────────────────────────────────────────────┐
│ 1. PLANNING PHASE                                               │
│    task_decomposer analyzes → creates subtask DAG               │
│    ┌──────────┐    ┌──────────┐    ┌──────────┐               │
│    │ Load &   │───▶│ Feature  │───▶│ Train ML │               │
│    │ Parse    │    │ Extract  │    │ Model    │               │
│    └──────────┘    └──────────┘    └──────────┘               │
│         │                               │                       │
│         ▼                               ▼                       │
│    ┌──────────┐                   ┌──────────┐                 │
│    │ Validate │                   │ Screen   │                 │
│    │ Structs  │                   │ Candidates│                │
│    └──────────┘                   └──────────┘                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ 2. DOMAIN TOOL LOADING                                          │
│    Detected: materials science + ML                             │
│    Loading: materials.crystal, materials.properties,            │
│             data_science.ml_modeling, data_science.statistics   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ 3. EXECUTION WITH CHECKPOINTS                                   │
│    Each subtask:                                                │
│    - Execute with atomic tools                                  │
│    - Checkpoint state after completion                          │
│    - Update working_memory with results                         │
│    - Reflect: did this succeed? adjust plan if needed           │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ 4. SYNTHESIS                                                    │
│    - Aggregate results from episodic_memory                     │
│    - Generate final report                                      │
│    - Store successful workflow in procedural_memory             │
└─────────────────────────────────────────────────────────────────┘
```

---

## Recommended File Structure

```
SimpleSWECode/
├── tools/
│   ├── __init__.py
│   ├── registry.py              # DomainAwareRegistry
│   │
│   ├── atomic/                  # Layer 1: Always loaded (8 tools)
│   │   ├── __init__.py
│   │   ├── compute.py
│   │   ├── file_ops.py
│   │   ├── search.py
│   │   ├── shell.py
│   │   ├── data_io.py
│   │   ├── http.py
│   │   ├── visualize.py
│   │   └── version_control.py
│   │
│   ├── domain/                  # Layer 2: Loaded on-demand
│   │   ├── __init__.py
│   │   ├── data_science/
│   │   ├── engineering/
│   │   ├── chemistry/
│   │   ├── materials/
│   │   ├── biology/
│   │   ├── physics/
│   │   └── geoscience/
│   │
│   └── orchestration/           # Layer 3: Long-horizon support
│       ├── __init__.py
│       ├── planning/
│       ├── execution/
│       ├── memory/
│       ├── knowledge/
│       └── reflection/
│
├── knowledge_base/              # Biomni-style "Know-How Library"
│   ├── protocols/               # Standard procedures by domain
│   ├── best_practices/          # Guidelines and tips
│   └── error_patterns/          # Common failures and fixes
│
├── agent.py                     # Main agent loop
├── llm.py                       # LLM interface
├── state.py                     # State management
└── main.py                      # CLI entry point
```

---

## Migration Guide: Current tools/core/ → New Structure

| Current Tool | New Location | Notes |
|--------------|--------------|-------|
| `bash.py` | `atomic/shell.py` | Rename |
| `str_replace_editor.py` | `atomic/file_ops.py` | Merge read/write/edit |
| `glob_search.py` | `atomic/search.py` | Merge with grep |
| `grep_search.py` | `atomic/search.py` | Merge with glob |
| `git_operations.py` | `atomic/version_control.py` | Rename |
| `web_fetch.py` | `atomic/http.py` | Rename |
| `todo_write.py` | `orchestration/planning/` | Move to orchestration |
| `save_memory.py` | `orchestration/memory/` | Move to orchestration |
| `recall_memory.py` | `orchestration/memory/` | Move to orchestration |
| `reflect.py` | `orchestration/reflection/` | Move to orchestration |
| `task_agent.py` | `orchestration/execution/` | Move to orchestration |
| `create_summary.py` | `orchestration/reflection/` | Move to orchestration |
| `update_progress_md.py` | `orchestration/reflection/` | Move to orchestration |
| `list_directory.py` | `atomic/file_ops.py` | Merge into file_ops |
| `multi_edit.py` | `atomic/file_ops.py` | Merge into file_ops |
| `advanced_file_ops.py` | `atomic/file_ops.py` | Merge into file_ops |
| `web_search.py` | `atomic/http.py` | Merge into http |
| `notebook_edit.py` | `domain/data_science/` | Domain-specific |
| `ask_user_step.py` | `orchestration/execution/` | Move to orchestration |
| `performance_monitor.py` | `orchestration/execution/` | Move to orchestration |

---

## Key Design Principles

1. **Atomic tools are composable primitives** - 8 tools that do one thing well
2. **Domain modules load on-demand** - classify task, load relevant domain (keeps context lean)
3. **Long-horizon = planning + memory + reflection** - not just more tools, but orchestration
4. **Knowledge base augments reasoning** - protocols/best-practices retrieved as needed (like Biomni's Know-How Library)
5. **Max ~15 tool schemas per LLM call** - atomic (8) + domain (4-5) + orchestration (3)
