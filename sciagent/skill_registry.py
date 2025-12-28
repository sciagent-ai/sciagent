"""Skill registry for dynamic skill discovery and management.

This module provides the SkillRegistry class that scans the skills directory,
loads skill metadata, and manages skill activation based on task requirements.
"""

from __future__ import annotations

import re
import time
from typing import Dict, List, Optional, Any, TYPE_CHECKING, Set
from pathlib import Path

from .skill import Skill, DefaultSkill, SkillActivation

if TYPE_CHECKING:
    from .core_agent import CoreAgent


class SkillRegistry:
    """Dynamic skill discovery and management system.
    
    The registry scans the skills directory for skill definitions,
    loads metadata for quick access, and provides methods to find
    and activate appropriate skills for given tasks.
    
    Supports both eager loading (traditional) and lazy loading modes
    for improved performance.
    """

    def __init__(self, skills_dir: Optional[Path] = None, lazy_loading: bool = True):
        self.skills_dir = skills_dir or Path("skills")
        self.lazy_loading = lazy_loading
        self.skills: Dict[str, Skill] = {}
        self.default_skill = DefaultSkill()
        self._activation_history: List[SkillActivation] = []
        
        # Lazy loading structures
        self._skill_metadata_cache: Dict[str, Dict[str, Any]] = {}
        self._compiled_triggers: Dict[str, List[re.Pattern]] = {}
        self._trigger_keywords: Dict[str, Set[str]] = {}
        self._loaded_skills: Set[str] = set()
        
    def load_skills(self) -> None:
        """Scan skills/ directory and load metadata for all skills.
        
        This method performs the initial discovery of skills. If lazy_loading
        is enabled, only metadata is cached and skills are loaded on demand.
        Otherwise, all skills are loaded immediately (eager loading).
        """
        if not self.skills_dir.exists():
            print(f"⚠️ Skills directory not found: {self.skills_dir}")
            print(f"   Creating directory and using default skill only")
            self.skills_dir.mkdir(parents=True, exist_ok=True)
            return
        
        if self.lazy_loading:
            self._scan_skill_metadata()
        else:
            self._load_all_skills_eager()
    
    def _scan_skill_metadata(self) -> None:
        """Scan skills directory and cache metadata for lazy loading."""
        skills_scanned = 0
        skills_failed = 0
        
        for skill_dir in self.skills_dir.iterdir():
            if not skill_dir.is_dir():
                continue
                
            metadata_file = skill_dir / "metadata.yaml"
            if not metadata_file.exists():
                continue
            
            try:
                import yaml
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata_data = yaml.safe_load(f)
                
                skill_name = metadata_data['name']
                self._skill_metadata_cache[skill_name] = {
                    'metadata': metadata_data,
                    'skill_dir': skill_dir
                }
                
                # Pre-compile triggers for fast matching
                self._precompile_triggers(skill_name, metadata_data.get('triggers', []))
                
                skills_scanned += 1
                
            except Exception as e:
                skills_failed += 1
                print(f"❌ Failed to scan skill metadata {skill_dir.name}: {e}")
        
        print(f"✅ Skills metadata scanned: {skills_scanned}, failed: {skills_failed}")
    
    def _load_all_skills_eager(self) -> None:
        """Load all skills immediately (eager loading)."""
        skills_loaded = 0
        skills_failed = 0
        
        for skill_dir in self.skills_dir.iterdir():
            if not skill_dir.is_dir():
                continue
                
            metadata_file = skill_dir / "metadata.yaml"
            if not metadata_file.exists():
                continue
            
            try:
                # For now, create a basic skill wrapper
                # In the future, this could load custom skill classes
                skill = BasicSkill(skill_dir)
                self.skills[skill.metadata.name] = skill
                self._loaded_skills.add(skill.metadata.name)
                skills_loaded += 1
                
                print(f"📚 Loaded skill: {skill.metadata.name} ({skill.metadata.domain})")
                
            except Exception as e:
                skills_failed += 1
                print(f"❌ Failed to load skill {skill_dir.name}: {e}")
        
        print(f"✅ Skills loaded: {skills_loaded}, failed: {skills_failed}")
    
    def _precompile_triggers(self, skill_name: str, triggers: List[str]) -> None:
        """Pre-compile trigger patterns for fast matching."""
        if not triggers:
            return
        
        compiled_patterns = []
        keywords = set()
        
        for trigger in triggers:
            # Simple keyword extraction for first-pass filtering
            if trigger.isalpha():
                keywords.add(trigger.lower())
            else:
                # Assume it might be a regex pattern
                try:
                    pattern = re.compile(trigger, re.IGNORECASE)
                    compiled_patterns.append(pattern)
                except re.error:
                    # Fallback to simple string matching
                    keywords.add(trigger.lower())
        
        if compiled_patterns:
            self._compiled_triggers[skill_name] = compiled_patterns
        if keywords:
            self._trigger_keywords[skill_name] = keywords
    
    def find_matching_skills(self, task: str, context: Dict[str, Any] = None) -> List[Skill]:
        """Find skills that should be triggered for the given task.
        
        Uses optimized matching with pre-filtering for lazy loading mode.
        
        Args:
            task: The task description to match against
            context: Optional context information (agent state, user preferences, etc.)
            
        Returns:
            List of skills that match, ordered by relevance
        """
        if self.lazy_loading:
            return self._find_matching_skills_lazy(task, context)
        else:
            return self._find_matching_skills_eager(task, context)
    
    def _find_matching_skills_eager(self, task: str, context: Dict[str, Any] = None) -> List[Skill]:
        """Find matching skills using eager loading (traditional approach)."""
        matching_skills = []
        
        # Check all registered skills
        for skill in self.skills.values():
            if skill.should_trigger(task, context):
                matching_skills.append(skill)
        
        # Sort by specificity (more triggers = more specific)
        matching_skills.sort(
            key=lambda s: len(s.metadata.triggers), 
            reverse=True
        )
        
        return matching_skills
    
    def _find_matching_skills_lazy(self, task: str, context: Dict[str, Any] = None) -> List[Skill]:
        """Find matching skills using lazy loading with pre-filtering."""
        # Step 1: Fast keyword-based pre-filtering
        candidate_skills = self._prefilter_skills(task)
        
        if not candidate_skills:
            return []
        
        # Step 2: Load only candidate skills and perform detailed matching
        matching_skills = []
        for skill_name in candidate_skills:
            skill = self._load_skill_on_demand(skill_name)
            if skill and skill.should_trigger(task, context):
                matching_skills.append(skill)
        
        # Sort by specificity (more triggers = more specific)
        matching_skills.sort(
            key=lambda s: len(s.metadata.triggers), 
            reverse=True
        )
        
        return matching_skills
    
    def _prefilter_skills(self, task: str) -> List[str]:
        """Fast pre-filtering based on keywords and compiled patterns.
        
        Returns list of skill names that might match the task.
        This is much faster than loading all skills.
        """
        task_lower = task.lower()
        candidate_skills = []
        
        # Check keyword-based triggers (fastest)
        for skill_name, keywords in self._trigger_keywords.items():
            for keyword in keywords:
                if keyword in task_lower:
                    candidate_skills.append(skill_name)
                    break
        
        # Check regex-based triggers (slower but still fast)
        for skill_name, patterns in self._compiled_triggers.items():
            if skill_name not in candidate_skills:  # Avoid duplicates
                for pattern in patterns:
                    if pattern.search(task):
                        candidate_skills.append(skill_name)
                        break
        
        return candidate_skills
    
    def _load_skill_on_demand(self, skill_name: str) -> Optional[Skill]:
        """Load a skill only when needed (lazy loading)."""
        # Return if already loaded
        if skill_name in self.skills:
            return self.skills[skill_name]
        
        # Check if we have metadata cached
        if skill_name not in self._skill_metadata_cache:
            return None
        
        try:
            # Load the skill
            skill_dir = self._skill_metadata_cache[skill_name]['skill_dir']
            skill = BasicSkill(skill_dir)
            
            # Cache the loaded skill
            self.skills[skill_name] = skill
            self._loaded_skills.add(skill_name)
            
            return skill
            
        except Exception as e:
            print(f"❌ Failed to lazy load skill {skill_name}: {e}")
            return None
    
    def load_matching_skills_only(self, task: str) -> List[Skill]:
        """Public API method: Load only skills that match the task patterns.
        
        This is the main optimization method that pre-filters skills
        before loading them, significantly reducing startup overhead.
        
        Args:
            task: The task description to match against
            
        Returns:
            List of loaded skills that match the task
        """
        if not self.lazy_loading:
            # In eager mode, just use existing find_matching_skills
            return self.find_matching_skills(task)
        
        # In lazy mode, use optimized loading
        candidate_skills = self._prefilter_skills(task)
        loaded_skills = []
        
        for skill_name in candidate_skills:
            skill = self._load_skill_on_demand(skill_name)
            if skill:
                loaded_skills.append(skill)
        
        return loaded_skills
    
    def get_skill(self, name: str) -> Optional[Skill]:
        """Retrieve a skill by name, loading it on demand if lazy loading is enabled."""
        # Check if already loaded
        if name in self.skills:
            return self.skills[name]
        
        # Try lazy loading if enabled
        if self.lazy_loading:
            return self._load_skill_on_demand(name)
        
        return None
    
    def get_default_skill(self) -> Skill:
        """Get the default skill for fallback execution."""
        return self.default_skill
    
    def activate_skill(self, skill: Skill, task: str, agent: 'CoreAgent') -> Dict[str, Any]:
        """Activate a skill and track its execution.
        
        Args:
            skill: The skill to activate
            task: The task to execute
            agent: The agent instance
            
        Returns:
            Execution result from the skill
        """
        start_time = time.time()
        
        try:
            # Validate dependencies before execution
            if not skill.validate_dependencies(agent):
                return {
                    "success": False,
                    "result": None,
                    "tools_used": [],
                    "duration": 0.0,
                    "errors": ["Skill dependencies not satisfied"]
                }
            
            # Execute the skill
            result = skill.execute(task, agent)
            
            # Record the activation
            duration = time.time() - start_time
            activation = SkillActivation(
                skill_name=skill.metadata.name,
                activation_time=time.strftime("%Y-%m-%d %H:%M:%S"),
                trigger_reason=f"Matched task: {task[:100]}...",
                execution_result=result,
                duration=duration,
                success=result.get("success", False),
                tools_used=result.get("tools_used", []),
                errors=result.get("errors", [])
            )
            
            self._activation_history.append(activation)
            
            # Keep only recent activations to prevent memory bloat
            if len(self._activation_history) > 100:
                self._activation_history = self._activation_history[-50:]
            
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            
            # Record failed activation
            activation = SkillActivation(
                skill_name=skill.metadata.name,
                activation_time=time.strftime("%Y-%m-%d %H:%M:%S"),
                trigger_reason=f"Matched task: {task[:100]}...",
                execution_result={"success": False, "error": str(e)},
                duration=duration,
                success=False,
                tools_used=[],
                errors=[str(e)]
            )
            
            self._activation_history.append(activation)
            
            return {
                "success": False,
                "result": None,
                "tools_used": [],
                "duration": duration,
                "errors": [f"Skill execution failed: {e}"]
            }
    
    def get_activation_history(self, limit: int = 10) -> List[SkillActivation]:
        """Get recent skill activation history."""
        return self._activation_history[-limit:]
    
    def get_skill_statistics(self) -> Dict[str, Any]:
        """Get statistics about skill usage and performance."""
        if not self._activation_history:
            return {"total_activations": 0, "skills": {}}
        
        stats = {
            "total_activations": len(self._activation_history),
            "skills": {}
        }
        
        # Calculate per-skill statistics
        for activation in self._activation_history:
            skill_name = activation.skill_name
            if skill_name not in stats["skills"]:
                stats["skills"][skill_name] = {
                    "activations": 0,
                    "success_rate": 0.0,
                    "avg_duration": 0.0,
                    "tools_used": set()
                }
            
            skill_stats = stats["skills"][skill_name]
            skill_stats["activations"] += 1
            skill_stats["tools_used"].update(activation.tools_used)
        
        # Calculate success rates and average durations
        for skill_name, skill_stats in stats["skills"].items():
            skill_activations = [a for a in self._activation_history if a.skill_name == skill_name]
            
            successes = sum(1 for a in skill_activations if a.success)
            skill_stats["success_rate"] = successes / len(skill_activations)
            skill_stats["avg_duration"] = sum(a.duration for a in skill_activations) / len(skill_activations)
            skill_stats["tools_used"] = list(skill_stats["tools_used"])
        
        return stats
    
    def list_skills(self) -> List[Dict[str, Any]]:
        """List all available skills with their metadata."""
        skills_info = []
        
        for skill in self.skills.values():
            skills_info.append({
                "name": skill.metadata.name,
                "description": skill.metadata.description,
                "domain": skill.metadata.domain,
                "version": skill.metadata.version,
                "triggers": skill.metadata.triggers,
                "tools": skill.metadata.allowed_tools,
                "horizontal": skill.metadata.horizontal,
                "tags": skill.metadata.tags
            })
        
        # Sort by domain and name for consistent ordering
        skills_info.sort(key=lambda x: (x["domain"], x["name"]))
        
        return skills_info
    
    def get_lazy_loading_stats(self) -> Dict[str, Any]:
        """Get statistics about lazy loading performance."""
        if not self.lazy_loading:
            return {"lazy_loading_enabled": False}
        
        total_skills = len(self._skill_metadata_cache)
        loaded_skills = len(self._loaded_skills)
        unloaded_skills = total_skills - loaded_skills
        
        return {
            "lazy_loading_enabled": True,
            "total_skills_discovered": total_skills,
            "skills_loaded": loaded_skills,
            "skills_unloaded": unloaded_skills,
            "memory_saved_percentage": (unloaded_skills / total_skills * 100) if total_skills > 0 else 0,
            "loaded_skill_names": list(self._loaded_skills),
            "trigger_keywords_cached": len(self._trigger_keywords),
            "compiled_patterns_cached": len(self._compiled_triggers)
        }
    
    def preload_frequent_skills(self, skill_names: List[str]) -> None:
        """Pre-load specific skills that are frequently used.
        
        This can be used to warm the cache with commonly used skills
        while keeping the benefits of lazy loading for rarely used ones.
        """
        if not self.lazy_loading:
            return
        
        loaded_count = 0
        for skill_name in skill_names:
            if skill_name not in self._loaded_skills:
                skill = self._load_skill_on_demand(skill_name)
                if skill:
                    loaded_count += 1
        
        if loaded_count > 0:
            print(f"📦 Pre-loaded {loaded_count} frequent skills")
    
    def clear_unloaded_skills(self) -> None:
        """Clear unloaded skills from memory to free up resources.
        
        This removes skills that were loaded but are no longer needed,
        while keeping their metadata cached for future lazy loading.
        """
        if not self.lazy_loading:
            return
        
        # Keep only skills that have been used recently
        # (This is a simple implementation; could be enhanced with usage tracking)
        skills_to_keep = set()
        recent_activations = self._activation_history[-10:]  # Last 10 activations
        
        for activation in recent_activations:
            skills_to_keep.add(activation.skill_name)
        
        removed_count = 0
        skills_to_remove = []
        
        for skill_name in self._loaded_skills:
            if skill_name not in skills_to_keep:
                skills_to_remove.append(skill_name)
        
        for skill_name in skills_to_remove:
            if skill_name in self.skills:
                del self.skills[skill_name]
                self._loaded_skills.discard(skill_name)
                removed_count += 1
        
        if removed_count > 0:
            print(f"🧹 Cleared {removed_count} unused skills from memory")


class BasicSkill(Skill):
    """Basic skill implementation that uses instructions and workflows.
    
    This is the default skill implementation that most skills will use.
    It loads instructions from instructions.md and optionally workflows
    from workflow.yaml for more complex execution patterns.
    """
    
    def execute(self, task: str, agent: 'CoreAgent') -> Dict[str, Any]:
        """Execute the skill using instructions and available tools.
        
        This implementation:
        1. Loads skill instructions
        2. Builds enhanced system prompt including skill-specific guidance
        3. Delegates to agent execution with skill context
        """
        try:
            # Get skill-specific instructions
            instructions = self.get_instructions()
            
            # Build enhanced prompt that includes skill context
            base_prompt = agent.build_system_prompt()
            enhanced_prompt = f"""{base_prompt}

ACTIVE SKILL: {self.metadata.name}
SKILL DOMAIN: {self.metadata.domain}
SKILL DESCRIPTION: {self.metadata.description}

SKILL-SPECIFIC GUIDANCE:
{instructions}

ALLOWED TOOLS FOR THIS SKILL: {', '.join(self.metadata.allowed_tools) or 'All available tools'}

Execute the task using the above skill guidance and available tools.
"""
            
            # Temporarily override the system prompt for this execution
            original_prompt_method = agent.build_system_prompt
            agent.build_system_prompt = lambda: enhanced_prompt
            
            try:
                # Execute with skill context
                result = agent.execute_task(task)
                
                return {
                    "success": result.get("success", True),
                    "result": result,
                    "tools_used": result.get("tools_used", []),
                    "duration": result.get("duration", 0.0),
                    "errors": result.get("errors", [])
                }
            finally:
                # Restore original prompt method
                agent.build_system_prompt = original_prompt_method
                
        except Exception as e:
            return {
                "success": False,
                "result": None,
                "tools_used": [],
                "duration": 0.0,
                "errors": [str(e)]
            }