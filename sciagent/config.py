"""Configuration definitions for the SCI Agent.

The :class:`Config` dataclass captures all of the tunable parameters
required to instantiate and run a scientific SCI agent. It holds
information such as API keys, working directories, iteration limits,
verbosity settings and feature toggles for optional capabilities like
web access and notebook support.
"""

from dataclasses import dataclass
from typing import Optional, List  # noqa: F401 for type hints

from .model_config import DEFAULT_MODEL


@dataclass
class Config:
    """Configuration parameters for a :class:`SCIAgent`.

    This dataclass captures all of the tunable parameters required to
    instantiate and run a scientific SCI agent. In addition to the
    original Anthropic‑centric settings, this version introduces
    additional fields to support multiple large language model (LLM)
    providers via the `litellm` library. The ``model`` field defines
    the identifier of the LLM to call (e.g. ``"claude-3-5-sonnet-20241022"``
    or ``"gpt-4-turbo"``). The ``models`` list can optionally be
    provided to specify a sequence of models to try in order; the
    agent will fall back to subsequent models if the initial call
    fails. API keys are not tied to a specific provider here; instead
    they must be made available through environment variables
    appropriate to the chosen provider (e.g. ``OPENAI_API_KEY`` for
    OpenAI models, ``ANTHROPIC_API_KEY`` for Claude models, etc.).

    Attributes
    ----------
    api_key: str
        Legacy API key used for backwards compatibility. If provided,
        the agent will set the appropriate environment variable for
        the selected model. When targeting OpenAI models this value
        will be assigned to ``OPENAI_API_KEY``; when targeting
        Anthropic models it will be assigned to ``ANTHROPIC_API_KEY``.
    model: str
        Identifier of the primary LLM model to use. Defaults to
        Claude Sonnet for parity with the original implementation.
    models: Optional[List[str]]
        Optional list of model identifiers to attempt in order. If
        specified, the agent will attempt to call each model until a
        successful response is obtained. This can be used to provide
        fail‑over across providers.
    working_dir: str
        Base directory in which the agent operates.
    max_iterations: int
        Maximum number of iterations the agent should run for a single task.
    debug_mode: bool
        When True the agent emits additional debugging output.
    verbosity: str
        Display verbosity level. One of ``"minimal"``, ``"standard"``,
        ``"verbose"``, or ``"debug"``.
    state_file: str
        Filename used to persist the agent's internal state between runs.
    progress_file: str
        Filename used to write a markdown report of progress.
    context_retention: int
        Number of recent conversation turns to retain when compressing history.
    summarization_threshold: int
        Number of iterations after which a summary of the conversation is
        generated automatically.
    progress_tracking: bool
        Whether to write progress updates to a markdown file.
    enable_web: bool
        Enable web search and fetch tools.
    enable_notebooks: bool
        Enable Jupyter notebook editing tools.
    enable_skills: bool
        Enable the skill system for task routing and specialized capabilities.
        When disabled, falls back to direct agent execution for maximum speed.
    max_sub_agents: int
        Maximum number of concurrent sub-agents that may be spawned.
    temperature: float
        Temperature parameter for LLM calls (0.0-1.0). Higher values make
        output more random.
    max_tokens: int
        Maximum number of tokens the LLM can generate in a single response.
    reasoning_effort: str
        Reasoning effort level for models that support it. One of "none", "low", 
        "medium", or "high". Controls the depth of reasoning/thinking for providers
        like Anthropic, OpenAI o-series, Gemini 3.0+, and xAI Grok models.
    metrics_mode: bool
        Enable detailed metrics tracking including token usage and execution times.
    user_confirmation: bool
        Ask for user confirmation before executing potentially destructive operations
        like file modifications, running commands, or continuing after task completion.
    """

    # Use Optional instead of PEP 604 union for compatibility with Python < 3.10
    api_key: Optional[str] = None
    model: str = DEFAULT_MODEL
    models: Optional[List[str]] = None
    working_dir: str = "."
    max_iterations: int = 25
    max_tool_executions_per_iteration: int = 50
    max_consecutive_same_tool: int = 15
    debug_mode: bool = False
    verbosity: str = "standard"
    state_file: str = ".sci_agent_state.pkl"
    progress_file: str = "progress.md"
    context_retention: int = 8
    summarization_threshold: int = 12
    progress_tracking: bool = True
    enable_web: bool = True
    enable_notebooks: bool = True
    enable_skills: bool = True
    enable_performance_monitoring: bool = False
    max_sub_agents: int = 3
    temperature: float = 0.1
    max_tokens: int = 4096
    reasoning_effort: str = "medium"
    metrics_mode: bool = True
    user_confirmation: bool = True
