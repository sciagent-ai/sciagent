# Session Management Analysis for SciAgent

## Executive Summary

Analysis of implementing intelligent session management that balances new task execution with long-horizon work continuity, while systematically tracking display traces, token usage, and compression metrics.

## Current Problem: Binary Choice

The existing system has only two modes:
- **Fresh start**: Complete amnesia, everything resets
- **Explicit resume**: Manual task_id recovery

## Proposed Solution: Intelligent Session Management

### 1. Session Types (Auto-detected or User-specified)

```python
class SessionType(Enum):
    EXPLORATORY = "exploratory"    # Research, discovery → accumulate context
    FOCUSED = "focused"           # Specific task → fresh start default  
    MAINTENANCE = "maintenance"   # Updates, fixes → link to related work
    CONTINUATION = "continuation" # Explicit ongoing work
```

### 2. Smart Boundary Detection

```python
def analyze_task_boundaries(new_task: str, recent_sessions: List) -> SessionAction:
    
    # Fresh start indicators
    if any(keyword in new_task.lower() for keyword in 
           ["new", "different", "start fresh", "switch to"]):
        return SessionAction.CREATE_FRESH
        
    # Continuation indicators  
    if any(keyword in new_task.lower() for keyword in
           ["continue", "also", "furthermore", "expand on"]):
        return SessionAction.CONTINUE_SESSION
        
    # Default: semantic similarity check against recent work
    similarity = calculate_similarity(new_task, recent_sessions)
    if similarity > 0.75:
        return SessionAction.CONTINUE_SESSION
    else:
        return SessionAction.CREATE_FRESH
```

### 3. Graduated Data Persistence Structure

```
/workspace/
├── sessions/
│   ├── session_abc123/           # Current session
│   │   ├── state.pkl            # Full agent state  
│   │   ├── workspace/           # Session workspace
│   │   └── progress.md          # Session progress
│   ├── session_def456/           # Previous session
│   └── shared/                   # Cross-session resources
│       ├── memory/              # Global insights
│       ├── templates/           # Reusable patterns  
│       └── exports/             # Finalized outputs
```

### 4. Selective Context Inheritance

```python
class SessionManager:
    def start_new_task(self, task: str, user_hint: Optional[str] = None):
        
        boundary_analysis = self.analyze_boundaries(task)
        
        if boundary_analysis == SessionAction.CONTINUE_SESSION:
            # Inherit relevant context only
            current_session = self.get_active_session()
            current_session.add_task_context(task)
            return current_session
            
        elif boundary_analysis == SessionAction.CREATE_RELATED:
            # New session but link to relevant previous work
            parent_session = self.find_most_relevant_session(task)
            new_session = self.create_session(
                inherit_memory=parent_session.relevant_memory(task),
                inherit_files=parent_session.relevant_files(task)
            )
            return new_session
            
        else:  # CREATE_FRESH
            return self.create_fresh_session()
```

### 5. User Controls

```bash
# Explicit session management
sciagent "continue working on the analysis"           # Auto-detect continuation
sciagent "start fresh: new data pipeline"            # Force fresh start  
sciagent --session-type=exploratory "investigate X"  # Set session type
sciagent --isolate "test this approach"              # Force isolation
```

### 6. Memory Scoping Strategy

```python
# Three levels of persistence
session_memory = {}     # Current session only
project_memory = {}     # Related work (days/weeks)  
global_memory = {}      # Permanent insights (cross-project)

# Automatic promotion
if insight.confidence > 0.9 and insight.reuse_count > 3:
    promote_to_global_memory(insight)
```

## Current System Strengths

### Display Traces
Your `AgentDisplay` class already tracks:
- Phase transitions (Thinking → Planning → Executing → Complete)
- Tool execution timestamps and durations
- Task decomposition visualization
- Metrics aggregation

### Token Usage
Comprehensive tracking via:
- Automatic LLM response token extraction
- Cost tracking when available
- Per-call token logging in debug mode
- Display integration with real-time updates

### Compression
Sophisticated system with:
- Automatic conversation summarization every 12 iterations
- Structured summary creation preserving key context
- Memory system for persistent insights
- Context-aware compression ratios

## Enhanced Session Integration

### 1. Session-Level Metrics Aggregation

```python
@dataclass
class SessionMetrics:
    session_id: str
    total_tokens_used: int = 0
    compression_events: List[CompressionEvent] = field(default_factory=list)
    display_traces: List[DisplayTrace] = field(default_factory=list)
    cost_breakdown: Dict[str, float] = field(default_factory=dict)
    efficiency_metrics: EfficiencyMetrics = field(default_factory=EfficiencyMetrics)

@dataclass 
class CompressionEvent:
    timestamp: str
    original_tokens: int
    compressed_tokens: int
    compression_ratio: float
    context_preserved: float  # How much context was retained
    
@dataclass
class DisplayTrace:
    timestamp: str
    phase: str
    action: str
    tokens_used: int
    duration: float
    files_affected: List[str]
```

### 2. Cross-Session Token Optimization

```python
class SessionTokenManager:
    def __init__(self):
        self.session_token_budgets = {}
        self.compression_strategies = {}
        
    def optimize_for_session_type(self, session_type: SessionType):
        if session_type == SessionType.EXPLORATORY:
            # Higher token budget, less aggressive compression
            return TokenStrategy(budget=50000, compression_threshold=15)
        elif session_type == SessionType.FOCUSED:
            # Lower budget, more aggressive compression  
            return TokenStrategy(budget=20000, compression_threshold=8)
            
    def track_compression_effectiveness(self, session_id: str):
        """Monitor how well compression preserves relevant context"""
        events = self.get_compression_events(session_id)
        return {
            "avg_compression_ratio": np.mean([e.compression_ratio for e in events]),
            "context_preservation": np.mean([e.context_preserved for e in events]),
            "token_savings": sum(e.original_tokens - e.compressed_tokens for e in events)
        }
```

### 3. Session-Aware Display State

```python
class SessionDisplay(AgentDisplay):
    def __init__(self, session_context: SessionContext):
        super().__init__()
        self.session_context = session_context
        self.cross_session_insights = []
        
    def display_session_context(self):
        """Show relevant context from related sessions"""
        if self.session_context.parent_session:
            related_insights = self.get_related_insights()
            self.print(f"📚 Building on previous work from {parent_id}")
            
    def track_cross_session_progress(self):
        """Display progress across multiple related sessions"""
        related_sessions = self.session_context.related_sessions
        combined_progress = self.aggregate_progress(related_sessions)
        return combined_progress
```

### 4. Intelligent Compression for Long-Horizon Tasks

```python
class SessionAwareCompressor:
    def compress_with_session_context(self, 
                                    messages: List[Dict], 
                                    session_memory: Dict[str, Any]) -> List[Dict]:
        """Compression that preserves cross-session context"""
        
        # Extract session-critical information
        persistent_insights = session_memory.get('key_insights', [])
        ongoing_patterns = session_memory.get('patterns', [])
        
        # Enhanced summarization prompt
        summary_prompt = f"""
        Summarize this conversation preserving:
        1. Key insights from this session: {persistent_insights}
        2. Ongoing work patterns: {ongoing_patterns}  
        3. Progress on long-term objectives
        4. Critical decisions and their reasoning
        """
        
        # Compress with session awareness
        return self._compress_with_enhanced_context(messages, summary_prompt)
```

## Benefits of This Approach

### For Short Tasks:
- Auto-detects independence and starts fresh
- No contamination from previous work
- Fast startup, minimal context

### For Long-horizon Work:
- Intelligent context accumulation
- Memory builds progressively  
- Related work stays connected

### User Control:
- Explicit overrides when auto-detection is wrong
- Session type hints guide behavior
- Isolation options when needed

### Data Management:
- Systematic organization by session
- Cross-session insights preserved
- Automatic archiving of completed work

## Benefits for Specific Use Cases

### Display Traces
- **Session timeline**: Visual progression across related tasks
- **Context switches**: When and why sessions started/ended
- **Efficiency patterns**: Which session types use resources most effectively

### Token Usage
- **Budget management**: Automatic token allocation based on session type
- **Compression optimization**: Learn which compression strategies work best
- **Cost attribution**: Track spending across long-horizon vs focused work

### Compression
- **Context preservation**: Maintain critical insights across session boundaries
- **Smart summarization**: Session-aware compression that preserves important patterns
- **Memory efficiency**: Graduated compression based on information importance

## Implementation Strategy

### Phase 1: Foundation (Week 1-2)
1. **Add session metadata structures** to `state.py`
2. **Implement basic SessionManager** in new `session_manager.py`
3. **Extend Config** with session management options
4. **Add session CLI flags** to `main.py`

### Phase 2: Intelligence (Week 3-4) 
1. **Implement TaskBoundaryDetector** with semantic analysis
2. **Enhance memory system** with session scoping
3. **Add session-aware workspace management**
4. **Implement user preference learning**

### Phase 3: Integration (Week 5-6)
1. **Integrate session management into CoreAgent**
2. **Add session context to skill system**
3. **Implement cross-session data organization**
4. **Add session archiving and cleanup**

### Phase 4: Optimization (Week 7-8)
1. **Performance optimization for session lookup**
2. **Memory usage optimization for long sessions**
3. **Advanced session analytics and insights**
4. **User experience polish**

## Implementation Priority

**Phase 1**: Extend existing metrics collection
```python
# Add session fields to existing AgentState
session_metrics: SessionMetrics = field(default_factory=SessionMetrics)
```

**Phase 2**: Enhance compression with session awareness
```python
# Extend existing summarization with session context
def _compress_with_session_awareness(self, session_context)
```

**Phase 3**: Cross-session analytics and optimization
```python
# Add session analysis to existing performance monitor
def analyze_session_efficiency(self, session_ids: List[str])
```

## Key Benefits

1. **Balanced Approach**: Automatic detection balances fresh starts vs continuity
2. **User Control**: Explicit flags and preferences for session behavior  
3. **Data Continuity**: Systematic memory and workspace accumulation
4. **Cross-Session Isolation**: Configurable boundaries prevent interference
5. **Performance**: Lazy loading and efficient session lookup
6. **Backward Compatibility**: Existing resume functionality preserved

This enhanced session management provides the intelligent balance between fresh task execution and long-horizon work continuity while maintaining user control and systematic data accumulation that the scientific computing domain requires. Your existing foundation for display traces, token usage, and compression is excellent and would integrate seamlessly with this session management approach.