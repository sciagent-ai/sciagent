"""Skill abstraction for SWE-Agent v5.

This module defines the Skill base class and supporting metadata structures
for the unified agent platform. Skills represent high-level capabilities
that can be dynamically loaded and activated based on task requirements.
"""

from __future__ import annotations

import yaml
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, TYPE_CHECKING
from pathlib import Path
from abc import ABC, abstractmethod

if TYPE_CHECKING:
    from .core_agent import CoreAgent


@dataclass
class SkillMetadata:
    """Metadata for a skill loaded from metadata.yaml."""
    name: str
    description: str
    version: str = "1.0.0"
    triggers: List[str] = field(default_factory=list)  # Keywords/regex patterns
    allowed_tools: List[str] = field(default_factory=list)
    consensus: Optional[Dict[str, Any]] = None  # n_models, judge_model
    dependencies: List[str] = field(default_factory=list)
    domain: str = "general"  # e.g., "software_engineering", "scientific"
    horizontal: bool = True  # True for cross-domain skills
    tags: List[str] = field(default_factory=list)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SkillMetadata':
        """Create SkillMetadata from dictionary."""
        return cls(
            name=data['name'],
            description=data['description'],
            version=data.get('version', '1.0.0'),
            triggers=data.get('triggers', []),
            allowed_tools=data.get('allowed_tools', []),
            consensus=data.get('consensus'),
            dependencies=data.get('dependencies', []),
            domain=data.get('domain', 'general'),
            horizontal=data.get('horizontal', True),
            tags=data.get('tags', [])
        )


@dataclass 
class SkillActivation:
    """Record of a skill activation for tracking and analysis."""
    skill_name: str
    activation_time: str
    trigger_reason: str
    execution_result: Dict[str, Any]
    duration: float
    success: bool
    tools_used: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


class Skill(ABC):
    """Base class for all skills in the SWE-Agent v5 platform.
    
    Skills represent high-level capabilities that combine multiple tools
    and reasoning patterns to accomplish complex tasks. They use progressive
    disclosure - metadata is loaded immediately, but heavy resources like
    instructions and workflows are loaded only when needed.
    """

    def __init__(self, skill_path: Path):
        self.skill_path = skill_path
        self.metadata = self._load_metadata()
        self._instructions: Optional[str] = None  # Lazy loaded
        self._workflow: Optional[Dict[str, Any]] = None  # Lazy loaded
        self._mcp_tools: Optional[Any] = None  # FastMCP instance, lazy loaded
        
    def _load_metadata(self) -> SkillMetadata:
        """Load metadata.yaml from skill directory."""
        metadata_path = self.skill_path / "metadata.yaml"
        if not metadata_path.exists():
            raise FileNotFoundError(f"Skill metadata not found: {metadata_path}")
        
        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            return SkillMetadata.from_dict(data)
        except Exception as e:
            raise ValueError(f"Invalid skill metadata in {metadata_path}: {e}")
    
    def get_instructions(self) -> str:
        """Progressive disclosure: Load instructions.md only when needed."""
        if self._instructions is None:
            self._instructions = self._load_instructions()
        return self._instructions
    
    def _load_instructions(self) -> str:
        """Load instructions.md from skill directory."""
        instructions_path = self.skill_path / "instructions.md"
        if not instructions_path.exists():
            return f"# {self.metadata.name}\n\n{self.metadata.description}"
        
        try:
            with open(instructions_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"# {self.metadata.name}\n\nError loading instructions: {e}"
    
    def get_workflow(self) -> Optional[Dict[str, Any]]:
        """Load workflow.yaml for declarative task orchestration."""
        if self._workflow is None:
            self._workflow = self._load_workflow()
        return self._workflow
    
    def _load_workflow(self) -> Optional[Dict[str, Any]]:
        """Load workflow.yaml from skill directory."""
        workflow_path = self.skill_path / "workflow.yaml"
        if not workflow_path.exists():
            return None
        
        try:
            with open(workflow_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            # Log error but don't fail - workflow is optional
            return None
    
    def get_mcp_tools(self) -> Optional[Any]:
        """Load FastMCP tools if available."""
        if self._mcp_tools is None:
            self._mcp_tools = self._load_mcp_tools()
        return self._mcp_tools
    
    def _load_mcp_tools(self) -> Optional[Any]:
        """Load mcp_tools.py from skill directory."""
        mcp_tools_path = self.skill_path / "mcp_tools.py"
        if not mcp_tools_path.exists():
            return None
        
        try:
            # Dynamic import of the MCP tools module
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                f"{self.metadata.name}_mcp", mcp_tools_path
            )
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                # Look for 'mcp' attribute which should be a FastMCP instance
                return getattr(module, 'mcp', None)
        except Exception as e:
            # Log error but don't fail - MCP tools are optional
            return None
        
        return None
    
    def should_trigger(self, task: str, context: Dict[str, Any] = None) -> bool:
        """Check if this skill should be activated for the given task.
        
        Default implementation checks for trigger keywords in the task text.
        Subclasses can override for more sophisticated matching.
        """
        if not self.metadata.triggers:
            return False
        
        task_lower = task.lower()
        for trigger in self.metadata.triggers:
            if trigger.lower() in task_lower:
                return True
        
        return False
    
    def get_required_tools(self) -> List[str]:
        """Get list of tools this skill requires."""
        return self.metadata.allowed_tools.copy()
    
    def validate_dependencies(self, agent: 'CoreAgent') -> bool:
        """Validate that all required dependencies are available."""
        # Check tool dependencies
        available_tools = set(agent.registry.tools.keys())
        required_tools = set(self.metadata.allowed_tools)
        
        if not required_tools.issubset(available_tools):
            missing = required_tools - available_tools
            return False
        
        # Could add other dependency checks here (packages, services, etc.)
        return True
    
    @abstractmethod
    def execute(self, task: str, agent: 'CoreAgent') -> Dict[str, Any]:
        """Execute the skill using the provided agent.
        
        Args:
            task: The task description that triggered this skill
            agent: The agent instance with tools and capabilities
            
        Returns:
            Dict containing:
            - success: bool
            - result: Any (skill-specific result)
            - tools_used: List[str] 
            - duration: float
            - errors: List[str] (if any)
        """
        pass


class DefaultSkill(Skill):
    """Default skill implementation that delegates to standard agent execution.
    
    This serves as a fallback when no specific skills are triggered,
    maintaining backward compatibility with the existing agent behavior.
    """
    
    def __init__(self, skill_path: Optional[Path] = None):
        if skill_path is None:
            # Create a temporary metadata for the default skill
            self.metadata = SkillMetadata(
                name="default_execution",
                description="Default agent execution with full tool suite",
                triggers=["*"],  # Matches everything
                allowed_tools=[],  # No restrictions
                domain="general",
                horizontal=True
            )
            self.skill_path = Path(".")  # Current directory
        else:
            super().__init__(skill_path)
    
    def should_trigger(self, task: str, context: Dict[str, Any] = None) -> bool:
        """Default skill always matches as fallback."""
        return True
    
    def execute(self, task: str, agent: 'CoreAgent') -> Dict[str, Any]:
        """Execute using standard agent task execution."""
        try:
            # Delegate to the agent's execute_task method
            result = agent.execute_task(task)
            
            return {
                "success": result.get("success", True),
                "result": result,
                "tools_used": result.get("tools_used", []),
                "duration": result.get("duration", 0.0),
                "errors": result.get("errors", [])
            }
        except Exception as e:
            return {
                "success": False,
                "result": None,
                "tools_used": [],
                "duration": 0.0,
                "errors": [str(e)]
            }