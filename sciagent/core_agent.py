"""Core agent base class for unified SWE and scientific workflows.

This module contains the :class:`CoreAgent` class which provides the
foundational functionality shared across all agent types in the SWE-Agent
v5 architecture. This includes LLM management, tool registry, state
persistence, error handling, and progress tracking.
"""

from __future__ import annotations

import os
import pickle
import time
from typing import Dict, List, Any, Optional
from pathlib import Path
from abc import ABC, abstractmethod

# Optional imports for third-party services
try:
    import litellm  # type: ignore[import-not-found]
except Exception:
    litellm = None  # type: ignore[assignment]

from .config import Config
from .state import AgentState, ConversationSummary
from .display import AgentDisplay
from .tool_registry import DynamicToolRegistry
from .model_config import get_model_with_provider, PROVIDER_PATTERNS

# Conditional import for skill system (optional)
try:
    from .skill_registry import SkillRegistry
except ImportError:
    SkillRegistry = None


class CoreAgent(ABC):
    """Base agent class for unified SWE and scientific workflows.
    
    Provides core functionality that is shared across all agent types:
    - LLM abstraction and multi-provider support with fallback
    - Tool registry management and execution
    - State management and persistence
    - Progress tracking and summarization
    - Error handling and recovery
    - Conversation compression and context management
    
    Subclasses must implement:
    - build_system_prompt(): Agent-specific system prompt generation
    - execute_task(): Main task execution logic
    """

    def __init__(self, config: Config, progress_callback=None, indent_level: int = 0):
        self.config = config
        self.progress_callback = progress_callback
        self.indent_level = indent_level
        
        # Ensure litellm is available
        if litellm is None:
            raise ImportError(
                "The litellm library is required but not installed. Please install it to use the agent."
            )
        
        # Configure LiteLLM for cross-provider compatibility
        if config.debug_mode:
            try:
                # Disable noisy LiteLLM logging but keep sciagent debug info
                litellm.set_verbose = False
                print("🔍 Sciagent debug mode enabled (LiteLLM verbose disabled)")
            except Exception as e:
                print(f"⚠️ Could not configure LiteLLM: {e}")
        
        # Initialize sub-agent tracking
        self.active_sub_agents = 0
        
        # Initialize performance monitor if enabled
        self.performance_monitor = None
        if getattr(config, 'enable_performance_monitoring', False):
            try:
                # Import and initialize performance monitor
                from .tools.core.performance_monitor import PerformanceMonitorTool
                self.performance_monitor = PerformanceMonitorTool()
                self.performance_monitor._start_monitoring()
            except ImportError:
                print("⚠️ Performance monitoring requested but dependencies not available")
        
        # Configure environment variables for API keys
        self._configure_api_keys()
        
        # Initialize display system with verbosity control
        verbosity = "debug" if config.debug_mode else config.verbosity
        self.display = AgentDisplay(verbosity_level=verbosity, indent_level=indent_level, metrics_mode=config.metrics_mode)
        
        # State and progress file paths
        self.state_path = Path(config.working_dir) / config.state_file
        self.progress_path = Path(config.working_dir) / config.progress_file
        
        # Agent state (will be initialized by subclasses)
        self.state: Optional[AgentState] = None
        
        # Initialize skill system (optional)
        self.skill_registry: Optional[SkillRegistry] = None
        if config.enable_skills and SkillRegistry is not None:
            try:
                # Check if skills directory exists
                skills_dir = Path(config.working_dir) / "skills"
                if skills_dir.exists():
                    self.skill_registry = SkillRegistry(skills_dir, lazy_loading=True)
                    self.skill_registry.load_skills()
                    print(f"🎯 Skills system enabled with {len(self.skill_registry._skill_metadata_cache)} skills")
                else:
                    print("⚠️ Skills directory not found, skill system disabled")
            except Exception as e:
                print(f"⚠️ Failed to initialize skill system: {e}")
                self.skill_registry = None
        elif not config.enable_skills:
            print("⚡ Skills system disabled - using fast mode")
        
        # Initialize tool registry (to be configured by subclasses)
        self.registry = DynamicToolRegistry(
            search_paths=[
                "sciagent.tools.core",
                "sciagent.tools.domain",
            ],
            config=self.config,
        )
        
        # Determine list of models to try with proper provider prefixes
        if self.config.models:
            self.models = [get_model_with_provider(model) for model in self.config.models]
        else:
            self.models = [get_model_with_provider(self.config.model)]
        
        # Configure tool support for models without native function calling
        self._prepare_function_calling_support()
        
        # Change to working directory
        if config.working_dir != ".":
            os.chdir(config.working_dir)

    @abstractmethod
    def build_system_prompt(self, task: str = "") -> str:
        """Build the system prompt for this agent type.
        
        Args:
            task: Optional task description for dynamic prompt generation
            
        Returns:
            str: The complete system prompt for the agent
        """
        pass

    @abstractmethod
    def execute_task(self, task: str, **kwargs) -> Dict[str, Any]:
        """Execute a task using this agent.
        
        Args:
            task: The task description to execute
            **kwargs: Additional task-specific parameters
            
        Returns:
            Dict containing task execution results
        """
        pass
    
    def execute_task_with_skills(self, task: str, **kwargs) -> Dict[str, Any]:
        """Execute a task with optional skill routing.
        
        This method provides the skill system integration. If skills are enabled,
        it will attempt to find and use appropriate skills. Otherwise, it falls
        back to direct task execution.
        
        Args:
            task: The task description to execute
            **kwargs: Additional task-specific parameters
            
        Returns:
            Dict containing task execution results
        """
        # Fast path: skills disabled, execute directly
        if not self.config.enable_skills or self.skill_registry is None:
            return self.execute_task(task, **kwargs)
        
        # Skills enabled: find matching skills
        try:
            matching_skills = self.skill_registry.find_matching_skills(task)
            
            if matching_skills:
                # Use the best matching skill
                best_skill = matching_skills[0]
                print(f"🎯 Using skill: {best_skill.metadata.name}")
                return self.skill_registry.activate_skill(best_skill, task, self)
            else:
                # No matching skills, fall back to default execution
                self.display.debug_log("No matching skills found, using default execution")
                return self.execute_task(task, **kwargs)
                
        except Exception as e:
            # Skill system error, fall back gracefully
            print(f"⚠️ Skill system error: {e}, falling back to direct execution")
            return self.execute_task(task, **kwargs)

    def _configure_api_keys(self) -> None:
        """Set environment variables for API keys based on the chosen model(s).

        The agent accepts a single ``api_key`` for backwards compatibility
        but may need to set provider‑specific environment variables (e.g.
        ``OPENAI_API_KEY`` or ``ANTHROPIC_API_KEY``). If the relevant
        environment variable is already defined, the value from the
        configuration is not used to override it.
        """
        # Nothing to configure if no api_key provided
        if not self.config.api_key:
            return
        
        # Determine all models to inspect
        candidate_models: List[str] = []
        if self.config.models:
            candidate_models = self.config.models
        elif self.config.model:
            candidate_models = [self.config.model]
        
        # For each model guess the provider and set env var if missing
        for model in candidate_models:
            # Extract model name from provider/model format if present
            model_name = model.split('/')[-1] if '/' in model else model
            lower_model = model_name.lower()
            
            # Use provider patterns to detect and set appropriate env vars
            for provider, patterns in PROVIDER_PATTERNS.items():
                if any(pattern in lower_model for pattern in patterns):
                    env_key = f"{provider.upper()}_API_KEY"
                    if not os.getenv(env_key):
                        os.environ[env_key] = self.config.api_key  # pragma: no cover
                    break

    def _prepare_function_calling_support(self) -> None:
        """Enable function calling for models lacking native support.

        LiteLLM exposes a global flag ``add_function_to_prompt`` that
        instructs the library to embed tool definitions directly in the
        prompt for providers which do not support the OpenAI function
        calling API.
        """
        try:
            # Guard against missing litellm import
            if litellm is None:
                return
            
            # Reset to False by default; will enable if any model lacks support
            setattr(litellm, "add_function_to_prompt", False)
            
            # Check each configured model for function calling support
            for model in self.models:
                if litellm is not None:
                    supports_tools = litellm.supports_function_calling(model)
                    if not supports_tools:
                        setattr(litellm, "add_function_to_prompt", True)
                        self.display.debug_log(f"Enabled prompt-based function calling for {model}")
                        break
        except Exception as e:
            # Graceful fallback if function calling detection fails
            self.display.debug_log(f"Could not determine function calling support: {e}")

    def _call_llm(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        max_tokens: Optional[int] = None,
        **extra_params: Any,
    ) -> Any:
        """Invoke the LLM using the configured models with optional fallback.

        Parameters
        ----------
        messages: List[Dict[str, Any]]
            Conversation history in the OpenAI chat format.
        tools: Optional[List[Dict[str, Any]]]
            Tool definitions formatted for the LLM. When provided the LLM
            will be asked to call tools when appropriate.
        max_tokens: Optional[int]
            Maximum number of tokens in the response. If ``None`` the
            provider default is used.
        extra_params: dict
            Additional keyword arguments passed through to ``litellm.completion``.

        Returns
        -------
        Any
            The LLM response object from litellm.completion
        """
        if litellm is None:
            raise ImportError("litellm is required but not available")
        
        # Prepare completion parameters
        completion_kwargs = {
            "messages": messages,
            "max_tokens": max_tokens or self.config.max_tokens,
            "temperature": self.config.temperature,
            **extra_params
        }
        
        if tools:
            completion_kwargs["tools"] = tools
        
        # Try each model in sequence until one succeeds
        last_error = None
        start_time = time.time()
        
        for model in self.models:
            try:
                completion_kwargs["model"] = model
                response = litellm.completion(**completion_kwargs)
                
                # Extract token usage from response if available
                tokens_used = 0
                if hasattr(response, 'usage') and response.usage:
                    tokens_used = getattr(response.usage, 'total_tokens', 0)
                    if tokens_used == 0:
                        # Fallback to sum of prompt + completion tokens
                        prompt_tokens = getattr(response.usage, 'prompt_tokens', 0)
                        completion_tokens = getattr(response.usage, 'completion_tokens', 0)
                        tokens_used = prompt_tokens + completion_tokens
                
                # Track performance if monitoring enabled
                if self.performance_monitor:
                    end_time = time.time()
                    self.performance_monitor.track_tool_execution(
                        tool_name="llm_call",
                        start_time=start_time,
                        end_time=end_time,
                        success=True,
                        model=model,
                        tokens_requested=max_tokens or self.config.max_tokens,
                        tools_provided=len(tools) if tools else 0
                    )
                
                # Update display with token usage for metrics mode
                if tokens_used > 0:
                    self.display.update_token_cost(tokens_used)
                
                if self.config.debug_mode:
                    self.display.debug_log(f"LLM call successful with model: {model} ({tokens_used} tokens)")
                
                return response
            except Exception as e:
                last_error = e
                self.display.debug_log(f"Model {model} failed: {e}")
                continue
        
        # Track failed LLM call
        if self.performance_monitor:
            end_time = time.time()
            self.performance_monitor.track_tool_execution(
                tool_name="llm_call",
                start_time=start_time,
                end_time=end_time,
                success=False,
                error=str(last_error),
                models_attempted=len(self.models)
            )
        
        # If all models failed, raise the last error
        raise Exception(f"All configured models failed. Last error: {last_error}")

    def _create_intelligent_summary(self, messages: List[Dict[str, Any]]) -> None:
        """Leverage the LLM to create a structured summary of recent conversation."""
        try:
            recent_messages = messages[-10:]
            summary_prompt = (
                "Analyze this agent conversation and create a comprehensive summary:\n"
                "1. Key accomplishments with technical details\n"
                "2. Current focus and technical context\n"
                "3. Files created/modified and their purposes\n"
                "4. Any errors resolved and solutions found\n"
                "5. Next logical steps with specific actions\n"
                "6. Tool usage patterns and effectiveness\n\n"
                "Be comprehensive but concise - this summary will guide future work."
            )
            
            summary_messages = [
                {"role": "user", "content": summary_prompt},
                {"role": "assistant", "content": str(recent_messages)},
            ]
            
            response = self._call_llm(
                messages=summary_messages,
                max_tokens=1000,
                temperature=0.3
            )
            
            # Extract and structure the summary
            summary_text = response.choices[0].message.content
            
            # Create structured summary object
            summary = ConversationSummary(
                timestamp=str(Path().resolve()),
                token_count=len(str(messages)),
                message_count=len(messages),
                key_accomplishments=self._extract_accomplishments(summary_text),
                current_focus=self._extract_current_focus(summary_text),
                files_created_modified=list(self.state.files_tracking.keys()) if self.state else [],
                errors_resolved=[],  # Will be enhanced in future
                next_steps=self._extract_next_steps(summary_text),
                raw_summary=summary_text
            )
            
            if self.state:
                self.state.conversation_summaries.append(summary)
                self.display.debug_log("Intelligent summary created")
            
        except Exception as e:
            self.display.debug_log(f"Could not create intelligent summary: {e}")

    def _compress_conversation_with_summary(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Compress conversation using the latest summary to save tokens."""
        if not self.state or not self.state.conversation_summaries:
            return messages
        
        latest_summary = self.state.conversation_summaries[-1]
        summary_text = (
            "AGENT COMPREHENSIVE SUMMARY:\n"
            f"Key accomplishments: {', '.join(latest_summary.key_accomplishments)}\n"
            f"Current focus: {latest_summary.current_focus}\n"
            f"Files tracked: {len(latest_summary.files_created_modified)} ("
            + ", ".join(latest_summary.files_created_modified[:5])
            + (" ..." if len(latest_summary.files_created_modified) > 5 else "")
            + ")\n"
            f"Errors resolved: {', '.join(latest_summary.errors_resolved)}\n"
            f"Next steps: {', '.join(latest_summary.next_steps)}\n"
        )
        
        compressed = [
            messages[0],  # Keep system message
            {"role": "user", "content": f"COMPREHENSIVE CONTEXT: {summary_text}"}
        ] + messages[-self.config.context_retention :]
        
        return compressed

    def _extract_accomplishments(self, summary_text: str) -> List[str]:
        """Extract key accomplishments from summary text."""
        # Simple regex-based extraction - can be enhanced
        import re
        accomplishments = re.findall(r'(?:accomplished|completed|created|fixed|implemented)[^.]*', summary_text.lower())
        return accomplishments[:5]  # Limit to top 5

    def _extract_current_focus(self, summary_text: str) -> str:
        """Extract current focus from summary text."""
        import re
        focus_match = re.search(r'(?:current focus|focusing on|working on)[^.]*', summary_text.lower())
        return focus_match.group(0) if focus_match else "Continuing development work"

    def _extract_next_steps(self, summary_text: str) -> List[str]:
        """Extract next steps from summary text."""
        import re
        steps = re.findall(r'(?:next|should|need to|will)[^.]*', summary_text.lower())
        return steps[:3]  # Limit to top 3

    def _save_state(self) -> None:
        """Persist the agent's internal state to disk."""
        if not self.state:
            return
        
        try:
            with open(self.state_path, 'wb') as f:
                pickle.dump(self.state, f)
            
            if self.config.debug_mode:
                file_count = len(self.state.files_tracking) if hasattr(self.state, 'files_tracking') else 0
                self.display.debug_log(f"State saved: {file_count} files tracked")
        except Exception as e:
            self.display.debug_log(f"Could not save state: {e}")

    def _load_state(self, task_id: str) -> bool:
        """Load a previously saved state from disk."""
        try:
            if not self.state_path.exists():
                return False
            
            with open(self.state_path, 'rb') as f:
                loaded_state: AgentState = pickle.load(f)
            
            if loaded_state.task_id == task_id:
                self.state = loaded_state
                return True
            
            return False
        except Exception as e:
            self.display.debug_log(f"Could not load state: {e}")
            return False

    def _handle_error_with_full_context(self, error: Exception, messages: List[Dict[str, Any]]) -> str:
        """Handle errors with comprehensive context and recovery suggestions."""
        error_context = f"Error: {type(error).__name__}: {str(error)}"
        
        if self.config.debug_mode:
            self.display.debug_log(f"Error handled: {error_context}")
        
        return f"An error occurred: {error_context}. Please review and try again with adjustments."

    def _cleanup_state(self) -> None:
        """Clean up temporary state and resources."""
        try:
            if self.state_path.exists():
                # Optionally remove state file or archive it
                pass
        except Exception as e:
            self.display.debug_log(f"Could not cleanup state: {e}")