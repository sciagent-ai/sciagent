"""Session Management for SciAgent.

This module provides intelligent session management that balances fresh task
execution with long-horizon work continuity. It includes smart task boundary
detection, session linking, and systematic data organization.
"""

import os
import json
import pickle
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from dataclasses import asdict

from .state import (
    SessionMetadata, SessionType, SessionAction, IsolationLevel,
    SessionPreferences, SessionMetrics, AgentState
)
from .config import Config


class TaskBoundaryDetector:
    """Analyzes tasks to determine session boundaries and relationships."""
    
    def __init__(self):
        self.fresh_start_keywords = [
            "new", "different", "start fresh", "switch to", "begin",
            "create new", "start over", "reset", "clean slate"
        ]
        self.continuation_keywords = [
            "continue", "also", "furthermore", "moreover", "additionally", 
            "expand on", "build on", "keep working", "follow up"
        ]
        self.related_keywords = [
            "similar to", "like before", "improve", "enhance", "modify",
            "update", "fix", "debug", "optimize"
        ]
    
    def analyze_task_relationship(self, 
                                current_task: str,
                                recent_sessions: List[SessionMetadata],
                                time_threshold_hours: int = 24) -> Tuple[SessionAction, Optional[str], float]:
        """
        Analyze relationship between current task and recent sessions.
        
        Returns:
            Tuple of (recommended_action, target_session_id, confidence_score)
        """
        if not recent_sessions:
            return SessionAction.CREATE_FRESH, None, 1.0
        
        # Check for explicit user signals
        explicit_signal = self._check_explicit_signals(current_task)
        if explicit_signal:
            return explicit_signal, None, 0.95
        
        # Find most relevant recent session
        best_match = self._find_best_session_match(current_task, recent_sessions, time_threshold_hours)
        
        if not best_match:
            return SessionAction.CREATE_FRESH, None, 0.8
        
        session, similarity_score, time_factor = best_match
        
        # Decision logic
        combined_score = similarity_score * 0.7 + time_factor * 0.3
        
        if combined_score > 0.8:
            return SessionAction.CONTINUE_SESSION, session.session_id, combined_score
        elif combined_score > 0.6:
            return SessionAction.CREATE_RELATED, session.session_id, combined_score
        else:
            return SessionAction.CREATE_FRESH, None, combined_score
    
    def _check_explicit_signals(self, task: str) -> Optional[SessionAction]:
        """Check for explicit user signals about session boundaries."""
        task_lower = task.lower()
        
        if any(keyword in task_lower for keyword in self.fresh_start_keywords):
            return SessionAction.CREATE_FRESH
        
        if any(keyword in task_lower for keyword in self.continuation_keywords):
            return SessionAction.CONTINUE_SESSION
        
        return None
    
    def _find_best_session_match(self, 
                                task: str, 
                                sessions: List[SessionMetadata],
                                time_threshold_hours: int) -> Optional[Tuple[SessionMetadata, float, float]]:
        """Find the most relevant session based on similarity and recency."""
        now = datetime.now()
        best_match = None
        best_score = 0.0
        
        for session in sessions:
            if not session.is_active or session.completion_status == "abandoned":
                continue
            
            # Calculate semantic similarity
            similarity = self._calculate_semantic_similarity(task, session)
            
            # Calculate time factor
            last_active = datetime.fromisoformat(session.last_active.replace('Z', '+00:00').replace('+00:00', ''))
            time_diff = now - last_active
            hours_diff = time_diff.total_seconds() / 3600
            
            if hours_diff > time_threshold_hours:
                time_factor = 0.1  # Very old session
            else:
                time_factor = max(0.1, 1.0 - (hours_diff / time_threshold_hours))
            
            # Combined score
            combined_score = similarity * 0.7 + time_factor * 0.3
            
            if combined_score > best_score:
                best_score = combined_score
                best_match = (session, similarity, time_factor)
        
        return best_match if best_score > 0.3 else None
    
    def _calculate_semantic_similarity(self, task: str, session: SessionMetadata) -> float:
        """Calculate semantic similarity between task and session."""
        # Simple word-based similarity (can be enhanced with embeddings later)
        task_words = set(task.lower().split())
        
        session_text = " ".join([
            *session.original_tasks,
            session.description or "",
            *session.tags
        ]).lower()
        session_words = set(session_text.split())
        
        if not session_words:
            return 0.0
        
        intersection = task_words.intersection(session_words)
        union = task_words.union(session_words)
        
        return len(intersection) / len(union) if union else 0.0


class SessionManager:
    """Manages session lifecycle, relationships, and data organization."""
    
    def __init__(self, config: Config):
        self.config = config
        self.detector = TaskBoundaryDetector()
        self.sessions_dir = Path(".sciagent_sessions")  # Simplified path structure
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        self.active_session: Optional[SessionMetadata] = None
        self._session_cache: Dict[str, SessionMetadata] = {}
    
    def create_session_workspace(self, session_id: str) -> Path:
        """Create complete session workspace structure."""
        session_path = self.sessions_dir / session_id
        workspace_dirs = [
            "workspace/raw", 
            "workspace/extracted", 
            "workspace/output", 
            "memory", 
            "reflections", 
            "trajectory"
        ]
        for dir_path in workspace_dirs:
            (session_path / dir_path).mkdir(parents=True, exist_ok=True)
        return session_path
    
    def start_session_for_task(self, 
                             task: str,
                             session_type: Optional[SessionType] = None,
                             user_preferences: Optional[SessionPreferences] = None,
                             force_action: Optional[SessionAction] = None) -> Tuple[SessionMetadata, AgentState]:
        """
        Start a new session or resume existing based on intelligent analysis.
        
        Returns:
            Tuple of (session_metadata, agent_state)
        """
        if force_action:
            action, target_session_id, confidence = force_action, None, 1.0
        else:
            # Analyze task relationship to existing sessions
            recent_sessions = self._get_recent_sessions(hours=24)
            action, target_session_id, confidence = self.detector.analyze_task_relationship(
                task, recent_sessions
            )
        
        if action == SessionAction.CONTINUE_SESSION and target_session_id:
            return self._resume_session(target_session_id, task)
        elif action == SessionAction.CREATE_RELATED and target_session_id:
            return self._create_related_session(target_session_id, task, session_type, user_preferences)
        else:
            return self._create_fresh_session(task, session_type, user_preferences)
    
    def _create_fresh_session(self, 
                            task: str,
                            session_type: Optional[SessionType] = None,
                            user_preferences: Optional[SessionPreferences] = None) -> Tuple[SessionMetadata, AgentState]:
        """Create a completely new session."""
        session_id = self._generate_session_id(task)
        
        # Auto-detect session type if not provided
        if not session_type:
            session_type = self._detect_session_type(task)
        
        # Create session workspace structure
        session_path = self.create_session_workspace(session_id)
        
        # Create session metadata
        session_metadata = SessionMetadata(
            session_id=session_id,
            session_type=session_type,
            user_preferences=user_preferences or SessionPreferences(),
            original_tasks=[task],
            workspace_path=str(session_path)
        )
        
        # Initialize session metrics
        session_metadata.metrics = SessionMetrics(
            session_id=session_id,
            start_time=datetime.now().isoformat()
        )
        
        # Create agent state
        agent_state = AgentState(
            task_id=session_id,
            original_task=task,
            completed_steps=[],
            current_step="Starting new session",
            error_history=[],
            iteration_count=0,
            last_successful_operation="session_created",
            working_context={},
            session_metadata=session_metadata
        )
        
        # Save session
        self._save_session(session_metadata)
        self.active_session = session_metadata
        
        return session_metadata, agent_state
    
    def _resume_session(self, session_id: str, additional_task: str) -> Tuple[SessionMetadata, AgentState]:
        """Resume an existing session with additional context."""
        session_metadata = self._load_session(session_id)
        if not session_metadata:
            # Fallback to fresh session if can't load
            return self._create_fresh_session(additional_task)
        
        # Update session with new task
        session_metadata.original_tasks.append(additional_task)
        session_metadata.last_active = datetime.now().isoformat()
        
        # Load existing agent state
        state_file = self.sessions_dir / session_id / "agent_state.pkl"
        if state_file.exists():
            try:
                with open(state_file, 'rb') as f:
                    agent_state = pickle.load(f)
                
                # Update state for continuation
                agent_state.original_task += f"\n\nAdditional context: {additional_task}"
                agent_state.current_step = f"Continuing session with: {additional_task}"
                
            except Exception:
                # Fallback if state loading fails
                return self._create_fresh_session(additional_task)
        else:
            # Create new agent state if none exists
            agent_state = AgentState(
                task_id=session_id,
                original_task=additional_task,
                completed_steps=[],
                current_step="Resuming session",
                error_history=[],
                iteration_count=0,
                last_successful_operation="session_resumed",
                working_context={},
                session_metadata=session_metadata
            )
        
        # Update session metadata reference
        agent_state.session_metadata = session_metadata
        
        # Save updated session
        self._save_session(session_metadata)
        self.active_session = session_metadata
        
        return session_metadata, agent_state
    
    def _create_related_session(self, 
                              parent_session_id: str,
                              task: str,
                              session_type: Optional[SessionType] = None,
                              user_preferences: Optional[SessionPreferences] = None) -> Tuple[SessionMetadata, AgentState]:
        """Create a new session linked to a parent session."""
        parent_session = self._load_session(parent_session_id)
        if not parent_session:
            return self._create_fresh_session(task, session_type, user_preferences)
        
        session_id = self._generate_session_id(task)
        
        # Inherit session type and preferences from parent if not specified
        if not session_type:
            session_type = parent_session.session_type
        if not user_preferences:
            user_preferences = parent_session.user_preferences
        
        # Create session workspace structure
        session_path = self.create_session_workspace(session_id)
        
        # Create related session
        session_metadata = SessionMetadata(
            session_id=session_id,
            session_type=session_type,
            parent_session_id=parent_session_id,
            user_preferences=user_preferences,
            original_tasks=[task],
            tags=parent_session.tags.copy(),  # Inherit tags
            workspace_path=str(session_path)
        )
        
        # Initialize metrics
        session_metadata.metrics = SessionMetrics(
            session_id=session_id,
            start_time=datetime.now().isoformat()
        )
        
        # Update parent session's child list
        parent_session.child_session_ids.append(session_id)
        parent_session.related_session_ids.append(session_id)
        self._save_session(parent_session)
        
        # Extract relevant context from parent session
        inherited_context = self._extract_relevant_context(parent_session, task)
        
        # Create agent state with inherited context
        agent_state = AgentState(
            task_id=session_id,
            original_task=task,
            completed_steps=[],
            current_step="Starting related session",
            error_history=[],
            iteration_count=0,
            last_successful_operation="related_session_created",
            working_context={},
            session_metadata=session_metadata,
            inherited_context=inherited_context
        )
        
        # Save new session
        self._save_session(session_metadata)
        self.active_session = session_metadata
        
        return session_metadata, agent_state
    
    def _extract_relevant_context(self, parent_session: SessionMetadata, new_task: str) -> Dict[str, Any]:
        """Extract relevant context from parent session for inheritance."""
        context = {
            "parent_session_id": parent_session.session_id,
            "parent_session_type": parent_session.session_type.value,
            "inherited_tags": parent_session.tags.copy(),
            "parent_insights": []
        }
        
        # Try to load parent session insights/memories
        parent_workspace = Path(parent_session.workspace_path) if parent_session.workspace_path else None
        if parent_workspace and parent_workspace.exists():
            memory_dir = parent_workspace / "memory"
            if memory_dir.exists():
                try:
                    for memory_file in memory_dir.glob("*.json"):
                        with open(memory_file, 'r') as f:
                            memory_data = json.load(f)
                            if memory_data.get('confidence', 0) > 0.7:  # High confidence insights only
                                context["parent_insights"].append({
                                    "key": memory_data.get('key'),
                                    "content": memory_data.get('content'),
                                    "tags": memory_data.get('tags', [])
                                })
                except Exception:
                    pass  # Gracefully handle any file reading errors
        
        return context
    
    def _detect_session_type(self, task: str) -> SessionType:
        """Auto-detect session type based on task content."""
        task_lower = task.lower()
        
        # Exploratory indicators
        exploratory_keywords = [
            "research", "investigate", "explore", "analyze", "study", "understand",
            "learn", "discover", "examine", "survey", "review"
        ]
        
        # Focused indicators
        focused_keywords = [
            "implement", "build", "create", "develop", "write", "code",
            "fix", "solve", "complete", "finish", "deliver"
        ]
        
        # Maintenance indicators
        maintenance_keywords = [
            "update", "upgrade", "refactor", "clean", "optimize", "improve",
            "debug", "repair", "maintain", "modify"
        ]
        
        if any(keyword in task_lower for keyword in exploratory_keywords):
            return SessionType.EXPLORATORY
        elif any(keyword in task_lower for keyword in maintenance_keywords):
            return SessionType.MAINTENANCE
        elif any(keyword in task_lower for keyword in focused_keywords):
            return SessionType.FOCUSED
        else:
            return SessionType.EXPLORATORY  # Default to exploratory
    
    def _generate_session_id(self, task: str) -> str:
        """Generate a unique session ID."""
        content = f"{task}{datetime.now().isoformat()}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def _deserialize_session_data(self, session_data: Dict[str, Any]) -> SessionMetadata:
        """Convert JSON session data to SessionMetadata, handling enum conversion."""
        # Convert session_type string to enum
        if isinstance(session_data.get('session_type'), str):
            session_data['session_type'] = SessionType(session_data['session_type'])
        
        # Handle other potential enum fields if they exist in the future
        return SessionMetadata(**session_data)
    
    def _get_recent_sessions(self, hours: int = 24) -> List[SessionMetadata]:
        """Get sessions active within the specified time window."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_sessions = []
        
        for session_file in self.sessions_dir.glob("*/session_metadata.json"):
            try:
                with open(session_file, 'r') as f:
                    session_data = json.load(f)
                    last_active = datetime.fromisoformat(session_data['last_active'].replace('Z', '+00:00').replace('+00:00', ''))
                    
                    if last_active > cutoff_time:
                        session_metadata = self._deserialize_session_data(session_data)
                        recent_sessions.append(session_metadata)
            except Exception:
                continue  # Skip corrupted session files
        
        return sorted(recent_sessions, key=lambda s: s.last_active, reverse=True)
    
    def _load_session(self, session_id: str) -> Optional[SessionMetadata]:
        """Load session metadata from disk."""
        if session_id in self._session_cache:
            return self._session_cache[session_id]
        
        session_file = self.sessions_dir / session_id / "session_metadata.json"
        if not session_file.exists():
            return None
        
        try:
            with open(session_file, 'r') as f:
                session_data = json.load(f)
                session_metadata = self._deserialize_session_data(session_data)
                self._session_cache[session_id] = session_metadata
                return session_metadata
        except Exception:
            return None
    
    def _save_session(self, session_metadata: SessionMetadata):
        """Save session metadata to disk."""
        session_dir = self.sessions_dir / session_metadata.session_id
        session_dir.mkdir(parents=True, exist_ok=True)
        
        session_file = session_dir / "session_metadata.json"
        try:
            with open(session_file, 'w') as f:
                # Convert to dict for JSON serialization
                session_dict = asdict(session_metadata)
                json.dump(session_dict, f, indent=2, default=str)
            
            # Update cache
            self._session_cache[session_metadata.session_id] = session_metadata
            
        except Exception as e:
            print(f"Warning: Failed to save session metadata: {e}")
    
    def save_agent_state(self, agent_state: AgentState):
        """Save agent state for the current session."""
        if not self.active_session:
            return
        
        session_dir = self.sessions_dir / self.active_session.session_id
        state_file = session_dir / "agent_state.pkl"
        
        try:
            with open(state_file, 'wb') as f:
                pickle.dump(agent_state, f)
        except Exception as e:
            print(f"Warning: Failed to save agent state: {e}")
    
    def update_session_metrics(self, metrics_update: Dict[str, Any]):
        """Update metrics for the active session."""
        if not self.active_session or not self.active_session.metrics:
            return
        
        # Update metrics fields
        for key, value in metrics_update.items():
            if hasattr(self.active_session.metrics, key):
                setattr(self.active_session.metrics, key, value)
        
        # Update last active time
        self.active_session.last_active = datetime.now().isoformat()
        
        # Save updated session
        self._save_session(self.active_session)
    
    def track_cost_breakdown(self, operation_type: str, cost: float, tokens_used: int = 0, 
                           provider: str = "", model: str = ""):
        """Track cost breakdown for different operations."""
        if not self.active_session or not self.active_session.metrics:
            return
        
        try:
            metrics = self.active_session.metrics
            
            # Initialize cost breakdown if needed
            if not hasattr(metrics, 'cost_breakdown') or not metrics.cost_breakdown:
                metrics.cost_breakdown = {}
            
            # Update cost breakdown by operation type
            if operation_type not in metrics.cost_breakdown:
                metrics.cost_breakdown[operation_type] = 0.0
            metrics.cost_breakdown[operation_type] += cost
            
            # Update total cost and tokens
            metrics.total_cost += cost
            metrics.total_tokens_used += tokens_used
            
            # Update last active time
            self.active_session.last_active = datetime.now().isoformat()
            
            # Save updated session
            self._save_session(self.active_session)
            
        except Exception as e:
            print(f"Warning: Failed to track cost breakdown: {e}")
    
    def finalize_session(self, completion_status: str = "completed"):
        """Mark the current session as completed and clean up."""
        if not self.active_session:
            return
        
        self.active_session.completion_status = completion_status
        self.active_session.is_active = False
        
        if self.active_session.metrics:
            self.active_session.metrics.end_time = datetime.now().isoformat()
        
        self._save_session(self.active_session)
        self.active_session = None
    
    def get_session_summary(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get a summary of session activities and metrics."""
        session = self._load_session(session_id)
        if not session:
            return None
        
        summary = {
            "session_id": session_id,
            "session_type": session.session_type.value,
            "created_at": session.created_at,
            "last_active": session.last_active,
            "completion_status": session.completion_status,
            "original_tasks": session.original_tasks,
            "tags": session.tags,
            "parent_session": session.parent_session_id,
            "child_sessions": session.child_session_ids,
            "related_sessions": session.related_session_ids
        }
        
        if session.metrics:
            summary["metrics"] = {
                "duration": session.metrics.end_time or "ongoing",
                "total_tokens": session.metrics.total_tokens_used,
                "total_cost": session.metrics.total_cost,
                "files_created": len(session.metrics.files_created),
                "files_modified": len(session.metrics.files_modified),
                "success_rate": session.metrics.success_rate
            }
        
        return summary
    
    def migrate_legacy_session_data(self) -> bool:
        """Migrate existing .sci_agent_state.pkl and workspace to session format."""
        import shutil
        
        legacy_state = Path(".sci_agent_state.pkl")
        legacy_workspace = Path("workspace")
        legacy_progress = Path("progress.md")
        
        if not any([legacy_state.exists(), legacy_workspace.exists(), legacy_progress.exists()]):
            return False
            
        # Create migration session
        from datetime import datetime
        migration_session_id = f"migrated_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        session_path = self.create_session_workspace(migration_session_id)
        
        # Move files
        if legacy_state.exists():
            shutil.move(str(legacy_state), str(session_path / "agent_state.pkl"))
        if legacy_workspace.exists():
            shutil.move(str(legacy_workspace), str(session_path / "workspace"))
        if legacy_progress.exists():
            shutil.move(str(legacy_progress), str(session_path / "progress.md"))
            
        # Create session metadata for migrated session
        from .state import SessionMetadata, SessionType, SessionMetrics
        session_metadata = SessionMetadata(
            session_id=migration_session_id,
            session_type=SessionType.CONTINUATION,
            original_tasks=["Migrated legacy session"],
            workspace_path=str(session_path),
            description="Automatically migrated from legacy session data"
        )
        session_metadata.metrics = SessionMetrics(
            session_id=migration_session_id,
            start_time=datetime.now().isoformat()
        )
        self._save_session(session_metadata)
        
        return True
    
    def cleanup_abandoned_sessions(self, older_than_days: int = 30) -> list[str]:
        """Clean up abandoned sessions older than specified days."""
        from datetime import datetime, timedelta
        
        cutoff_time = datetime.now() - timedelta(days=older_than_days)
        abandoned_sessions = []
        
        for session_dir in self.sessions_dir.glob("*"):
            if not session_dir.is_dir():
                continue
                
            session_metadata_file = session_dir / "session_metadata.json"
            if not session_metadata_file.exists():
                continue
                
            try:
                import json
                with open(session_metadata_file, 'r') as f:
                    session_data = json.load(f)
                
                last_active = datetime.fromisoformat(
                    session_data.get('last_active', '').replace('Z', '+00:00').replace('+00:00', '')
                )
                
                if (last_active < cutoff_time and 
                    session_data.get('completion_status') == 'abandoned' and
                    not session_data.get('is_active', False)):
                    
                    import shutil
                    shutil.rmtree(session_dir)
                    abandoned_sessions.append(session_data.get('session_id', str(session_dir.name)))
                    
            except Exception:
                continue  # Skip problematic sessions
                
        return abandoned_sessions
    
    def restore_session(self, session_id: str, switch_workspace: bool = True) -> bool:
        """Restore complete session state including workspace context."""
        session = self._load_session(session_id)
        if not session:
            return False
            
        # Load agent state
        state_file = Path(session.workspace_path) / "agent_state.pkl"
        if state_file.exists():
            self.active_session = session
            return True
        return False
    
    def archive_session(self, session_id: str, archive_path: Path) -> bool:
        """Archive complete session to external location."""
        import shutil
        
        session_dir = self.sessions_dir / session_id
        if session_dir.exists():
            shutil.copytree(session_dir, archive_path / session_id)
            return True
        return False
    
    def list_session_artifacts(self, session_id: str) -> dict[str, list[str]]:
        """List all files created by session."""
        import glob
        
        session_dir = self.sessions_dir / session_id
        artifacts = {
            "workspace_files": list(glob.glob(str(session_dir / "workspace/**/*"), recursive=True)),
            "memory_files": list(glob.glob(str(session_dir / "memory/*.json"))),
            "reflection_files": list(glob.glob(str(session_dir / "reflections/*.json"))),
            "state_files": [str(session_dir / "agent_state.pkl"), str(session_dir / "progress.md")]
        }
        return artifacts
    
    def list_all_sessions(self) -> list[dict[str, str]]:
        """List all sessions with basic info."""
        sessions = []
        
        for session_dir in self.sessions_dir.glob("*"):
            if not session_dir.is_dir():
                continue
                
            session_metadata_file = session_dir / "session_metadata.json"
            if not session_metadata_file.exists():
                continue
                
            try:
                import json
                with open(session_metadata_file, 'r') as f:
                    session_data = json.load(f)
                
                sessions.append({
                    "session_id": session_data.get('session_id', str(session_dir.name)),
                    "session_type": session_data.get('session_type', 'unknown'),
                    "created_at": session_data.get('created_at', 'unknown'),
                    "last_active": session_data.get('last_active', 'unknown'),
                    "completion_status": session_data.get('completion_status', 'unknown'),
                    "is_active": session_data.get('is_active', False)
                })
                
            except Exception:
                continue
                
        return sorted(sessions, key=lambda s: s['last_active'], reverse=True)