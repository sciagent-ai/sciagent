"""
Example Custom Tools

This file shows how to define custom tools that can be loaded into the agent.
You can:
1. Subclass BaseTool for full control
2. Use the @tool decorator for simple functions
3. Use FunctionTool wrapper for existing functions
"""
from typing import Dict, List, Optional
import requests
import json

from tools import BaseTool, ToolResult, FunctionTool, tool, ToolRegistry


# =============================================================================
# Method 1: Subclass BaseTool (full control)
# =============================================================================

class WebSearchTool(BaseTool):
    """Search the web using a search API"""
    
    name = "web_search"
    description = "Search the web for information. Returns top results with snippets."
    parameters = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query"
            },
            "num_results": {
                "type": "integer",
                "description": "Number of results to return (default: 5)",
                "default": 5
            }
        },
        "required": ["query"]
    }
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
    
    def execute(self, query: str, num_results: int = 5) -> ToolResult:
        # This is a mock - replace with actual search API
        # You could use: SerpAPI, Bing Search, Google Custom Search, etc.
        
        if not self.api_key:
            return ToolResult(
                success=False,
                output=None,
                error="No API key configured for web search"
            )
        
        # Mock response
        results = [
            {"title": f"Result {i+1} for: {query}", "snippet": f"Sample snippet {i+1}"}
            for i in range(num_results)
        ]
        
        return ToolResult(
            success=True,
            output=json.dumps(results, indent=2)
        )


class GitTool(BaseTool):
    """Git operations"""
    
    name = "git"
    description = "Execute git commands. Supports: status, log, diff, add, commit, push, pull, branch"
    parameters = {
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "Git subcommand (status, log, diff, add, commit, etc.)"
            },
            "args": {
                "type": "string",
                "description": "Additional arguments for the command"
            }
        },
        "required": ["command"]
    }
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = repo_path
    
    def execute(self, command: str, args: str = "") -> ToolResult:
        import subprocess
        
        # Whitelist safe commands
        safe_commands = ["status", "log", "diff", "add", "commit", "push", "pull", "branch", "checkout", "stash"]
        
        if command not in safe_commands:
            return ToolResult(
                success=False,
                output=None,
                error=f"Unsupported git command: {command}. Allowed: {safe_commands}"
            )
        
        try:
            full_command = f"git {command} {args}".strip()
            result = subprocess.run(
                full_command,
                shell=True,
                capture_output=True,
                text=True,
                cwd=self.repo_path
            )
            
            output = result.stdout or result.stderr
            return ToolResult(
                success=result.returncode == 0,
                output=output,
                error=None if result.returncode == 0 else f"Exit code: {result.returncode}"
            )
        except Exception as e:
            return ToolResult(success=False, output=None, error=str(e))


class HttpRequestTool(BaseTool):
    """Make HTTP requests"""
    
    name = "http_request"
    description = "Make HTTP requests to APIs or websites"
    parameters = {
        "type": "object",
        "properties": {
            "method": {
                "type": "string",
                "enum": ["GET", "POST", "PUT", "DELETE"],
                "description": "HTTP method"
            },
            "url": {
                "type": "string",
                "description": "URL to request"
            },
            "headers": {
                "type": "object",
                "description": "Request headers"
            },
            "body": {
                "type": "string",
                "description": "Request body (for POST/PUT)"
            }
        },
        "required": ["method", "url"]
    }
    
    def execute(
        self,
        method: str,
        url: str,
        headers: Dict = None,
        body: str = None
    ) -> ToolResult:
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                data=body,
                timeout=30
            )
            
            return ToolResult(
                success=response.ok,
                output=json.dumps({
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                    "body": response.text[:5000]  # Limit response size
                }, indent=2)
            )
        except Exception as e:
            return ToolResult(success=False, output=None, error=str(e))


# =============================================================================
# Method 2: Use @tool decorator (simple functions)
# =============================================================================

@tool(name="calculate", description="Perform mathematical calculations")
def calculate(expression: str) -> str:
    """
    Safely evaluate a mathematical expression
    
    Args:
        expression: Math expression like "2 + 2" or "sqrt(16)"
    """
    import ast
    import math
    
    # Safe evaluation with limited operations
    allowed_names = {
        k: v for k, v in math.__dict__.items() if not k.startswith("_")
    }
    allowed_names.update({"abs": abs, "round": round, "min": min, "max": max})
    
    try:
        # Parse and evaluate safely
        tree = ast.parse(expression, mode='eval')
        code = compile(tree, '<string>', 'eval')
        result = eval(code, {"__builtins__": {}}, allowed_names)
        return str(result)
    except Exception as e:
        raise ValueError(f"Cannot evaluate: {expression}. Error: {e}")


@tool(name="read_url", description="Fetch and read content from a URL")
def read_url(url: str) -> str:
    """
    Fetch content from a URL
    
    Args:
        url: The URL to fetch
    """
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.text[:10000]  # Limit size


@tool(name="json_query", description="Query JSON data using JMESPath-like syntax")
def json_query(data: str, query: str) -> str:
    """
    Query JSON data
    
    Args:
        data: JSON string to query
        query: Simple query path like "users[0].name" or "items.*.id"
    """
    import json
    
    obj = json.loads(data)
    
    # Simple path navigation
    parts = query.replace("[", ".").replace("]", "").split(".")
    result = obj
    
    for part in parts:
        if not part:
            continue
        if part == "*":
            if isinstance(result, list):
                result = result
            elif isinstance(result, dict):
                result = list(result.values())
        elif part.isdigit():
            result = result[int(part)]
        else:
            result = result[part]
    
    return json.dumps(result, indent=2)


# =============================================================================
# Method 3: Wrap existing functions with FunctionTool
# =============================================================================

def format_code(code: str, language: str = "python") -> str:
    """Format code using appropriate formatter"""
    if language == "python":
        try:
            import black
            return black.format_str(code, mode=black.Mode())
        except ImportError:
            return code
    return code

# Create tool from function
format_code_tool = FunctionTool(
    format_code,
    name="format_code",
    description="Format code using language-specific formatters"
)


# =============================================================================
# Registration Function (called by ToolRegistry.load_from_module)
# =============================================================================

def register_tools(registry: ToolRegistry):
    """
    Register all custom tools with the registry
    
    This function is called automatically when loading the module.
    """
    # Class-based tools
    registry.register(GitTool())
    registry.register(HttpRequestTool())
    
    # Decorated functions
    registry.register(calculate)
    registry.register(read_url)
    registry.register(json_query)
    
    # Wrapped functions
    registry.register(format_code_tool)
    
    # Optionally add web search if API key is available
    import os
    if os.environ.get("SEARCH_API_KEY"):
        registry.register(WebSearchTool(api_key=os.environ["SEARCH_API_KEY"]))


# Alternative: Export as TOOLS list (auto-discovered by load_from_module)
TOOLS = [
    GitTool(),
    HttpRequestTool(),
    format_code_tool,
]
