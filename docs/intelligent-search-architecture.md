# Intelligent Search Architecture Design

## Problem Statement

Current web search implementation in SciAgent faces token limit issues when performing multiple searches (15+ calls) for comprehensive research tasks. The system needs intelligent search planning and progressive disclosure similar to Claude Code's research mode.

## Claude Code's Architecture Insights

### Core Design Principles

**Single-threaded master loop** rather than complex multi-agent orchestration. This design prioritizes:
- Debuggability and transparency
- Reliability over complexity  
- Token efficiency through smart orchestration

### Token Optimization Strategies

1. **Programmatic Tool Calling (PTC)**
   - 37% token reduction (43,588 → 27,297 tokens on complex research)
   - Orchestrates tools through code rather than keeping results in context
   - Controls what information enters context window

2. **On-Demand Tool Discovery**
   - Discovers tools as needed vs loading all upfront
   - Claude only sees tools required for current task
   - Reduces context overhead

3. **Context Window Management**
   - Custom tools implement embeddings-based or BM25-based search
   - Retrieve only relevant information vs entire files
   - Smart summarization before context entry

### Research Mode Implementation

**Multi-Agent Research System:**
- Plans research process based on user queries
- Creates parallel agents searching simultaneously  
- Manages 200k token context limit via separate sub-task contexts
- Processes much larger content volumes than single-context approaches

**Subagents and Parallel Processing:**
- Enable parallelization through multiple isolated subagents
- Manage context through isolated windows
- Send only relevant information to orchestrator
- Excel at large-scale information processing

## Task Decomposition Strategy

### Hierarchical Task Breakdown
- **Huge tasks**: 15-25 subtasks
- **Large tasks**: 8-15 subtasks  
- **Medium tasks**: 3-8 subtasks
- **Small tasks**: Direct implementation

### Progressive Search Planning
Replace parallel search explosion with **Graph-of-Thoughts** pipeline:

**Scope → Plan → Retrieve → Triangulate → Draft → Critique → Package**

```python
# Instead of 15 parallel searches:
search_phases = [
    # Phase 1: Overview (broad, minimal fetch)
    {
        "phase": "overview", 
        "query": f"{main_query} overview fundamentals",
        "num_results": 5,
        "fetch_content": False
    },
    # Phase 2: Targeted (specific, deep fetch) 
    {
        "phase": "specific",
        "query": f"{main_query} best practices implementation",
        "num_results": 3,
        "fetch_content": True,
        "max_content_fetch": 2
    }
]
```

## Implementation Recommendations

### 1. Add SearchPlannerTool

```python
class SearchPlannerTool(BaseTool):
    """Plan progressive search strategy like Claude Code"""
    
    def plan_search_strategy(self, main_query: str, domain: str) -> List[Dict]:
        """Create intelligent search plan"""
        return [
            {
                "phase": "overview", 
                "query": f"{main_query} {domain} overview",
                "num_results": 5,
                "fetch_content": False,
                "priority": "high"
            },
            {
                "phase": "gaps", 
                "query": f"{main_query} {domain} implementation patterns",
                "num_results": 3,
                "fetch_content": True,
                "max_content_fetch": 2,
                "priority": "medium"
            }
        ]
```

### 2. Enhanced Content Intelligence

**Smart Content Extraction:**
```python
def extract_relevant_sections(self, content: str, query_terms: List[str]) -> str:
    """Extract only sections relevant to query - keep existing 3000 char limit"""
    
    paragraphs = content.split('\n\n')
    scored_paragraphs = []
    
    for para in paragraphs:
        score = sum(1 for term in query_terms if term.lower() in para.lower())
        if score > 0:
            scored_paragraphs.append((score, para))
    
    # Sort by relevance, take top sections
    scored_paragraphs.sort(key=lambda x: x[0], reverse=True)
    relevant_content = '\n\n'.join([para for score, para in scored_paragraphs[:3]])
    
    # Apply existing 3000 char limit
    if len(relevant_content) > 3000:
        relevant_content = relevant_content[:3000] + "..."
        
    return relevant_content
```

### 3. TaskAgent Integration for Context Isolation

```python
# Use TaskAgent for search phases to isolate context
class IntelligentSearchOrchestrator:
    
    def execute_search_plan(self, plan: List[Dict]) -> Dict[str, Any]:
        """Execute search plan with context isolation"""
        
        results = {}
        
        for phase in plan:
            # Each phase runs in separate TaskAgent context
            task_agent_input = {
                "task": f"Execute search: {phase['query']}",
                "search_params": phase
            }
            
            phase_results = self.task_agent.run(task_agent_input)
            
            # Only key findings bubble up to main context
            results[phase['phase']] = {
                "summary": phase_results.get('summary', ''),
                "key_sources": phase_results.get('top_sources', []),
                "findings": phase_results.get('key_findings', [])
            }
        
        return results
```

### 4. Performance Optimizations

**Caching Strategy:**
```python
# Add result caching to avoid re-fetching
class ContentCache:
    def __init__(self):
        self.url_cache = {}
        self.query_cache = {}
    
    def get_cached_content(self, url: str) -> Optional[str]:
        return self.url_cache.get(url)
    
    def cache_content(self, url: str, content: str):
        self.url_cache[url] = content
```

**Deduplication:**
```python
def deduplicate_sources(self, results: List[Dict]) -> List[Dict]:
    """Remove duplicate URLs/domains across searches"""
    seen_urls = set()
    unique_results = []
    
    for result in results:
        url = result.get('href', '')
        if url not in seen_urls:
            seen_urls.add(url)
            unique_results.append(result)
    
    return unique_results
```

## Expected Performance Gains

Based on Claude Code metrics:
- **37% token reduction** through context isolation
- **95% token reduction** through smart caching and compression
- **80% reduction** in research time for complex tasks
- **32.3% token reduction** through efficient context management

## Migration Strategy

1. **Phase 1**: Implement SearchPlannerTool alongside existing WebSearchTool
2. **Phase 2**: Add TaskAgent integration for context isolation
3. **Phase 3**: Implement content caching and deduplication
4. **Phase 4**: Add intelligent content extraction with relevance scoring

## Key Success Metrics

- Reduce token usage per research task by 30%+
- Complete comprehensive research with 3-5 searches instead of 15+
- Maintain or improve research quality through targeted content extraction
- Achieve faster research completion through progressive disclosure