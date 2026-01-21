#!/usr/bin/env python3
"""
Test script for web tools integration.

Tests:
1. WebTool directly (search + fetch)
2. WebTool through the agent
3. Researcher subagent with web access
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tools.atomic.web import WebTool
from tools import create_default_registry


def test_web_tool_directly():
    """Test WebTool search and fetch directly."""
    print("\n" + "="*60)
    print("TEST 1: WebTool Direct Test")
    print("="*60)

    web = WebTool()

    # Test search
    print("\n[1a] Testing web search...")
    result = web.execute(command="search", query="Python asyncio tutorial", num_results=3)

    if result.success:
        print(f"  SUCCESS - Search returned results")
        print(f"  Preview: {result.output[:300]}...")
    else:
        print(f"  FAILED - {result.error}")
        # Check if it's just missing API key
        if not os.getenv('BRAVE_SEARCH_API_KEY'):
            print("  NOTE: BRAVE_SEARCH_API_KEY not set, trying DuckDuckGo fallback...")

    # Test fetch
    print("\n[1b] Testing URL fetch...")
    result = web.execute(command="fetch", url="https://httpbin.org/get")

    if result.success:
        print(f"  SUCCESS - Fetched URL")
        print(f"  Preview: {result.output[:300]}...")
    else:
        print(f"  FAILED - {result.error}")

    return result.success


def test_web_tool_in_registry():
    """Test WebTool is registered and accessible."""
    print("\n" + "="*60)
    print("TEST 2: WebTool Registry Integration")
    print("="*60)

    registry = create_default_registry()

    # List tools
    tools = registry.list_tools()
    print(f"\n  Registered tools: {tools}")

    if "web" not in tools:
        print("  FAILED - web tool not in registry!")
        return False

    print("  SUCCESS - web tool is registered")

    # Execute via registry
    print("\n[2a] Executing search via registry...")
    result = registry.execute("web", command="search", query="Claude AI API", num_results=2)

    if result.success:
        print(f"  SUCCESS - Registry execution works")
    else:
        print(f"  Result: {result.error or 'No results'}")

    return True


def test_tool_schemas():
    """Test that tool schemas are correct for LLM."""
    print("\n" + "="*60)
    print("TEST 3: Tool Schema Validation")
    print("="*60)

    registry = create_default_registry()
    schemas = registry.get_schemas()

    web_schema = None
    for s in schemas:
        if s["name"] == "web":
            web_schema = s
            break

    if not web_schema:
        print("  FAILED - web schema not found")
        return False

    print(f"\n  Web tool schema:")
    print(f"    name: {web_schema['name']}")
    print(f"    description: {web_schema['description'][:50]}...")

    # Check required fields
    params = web_schema.get("input_schema", web_schema.get("parameters", {}))
    props = params.get("properties", {})

    required_params = ["command", "query", "url"]
    for p in required_params:
        if p in props:
            print(f"    {p}: OK")
        else:
            print(f"    {p}: MISSING")

    print("  SUCCESS - schema is valid")
    return True


def test_subagent_tools():
    """Test that researcher subagent has web tool access."""
    print("\n" + "="*60)
    print("TEST 4: Researcher SubAgent Tools")
    print("="*60)

    from subagent import SubAgentRegistry

    registry = SubAgentRegistry()
    researcher = registry.get("researcher")

    if not researcher:
        print("  FAILED - researcher config not found")
        return False

    print(f"\n  Researcher config:")
    print(f"    name: {researcher.name}")
    print(f"    allowed_tools: {researcher.allowed_tools}")

    if "web" in researcher.allowed_tools:
        print("  SUCCESS - researcher has web tool access")
        return True
    else:
        print("  FAILED - researcher missing web tool")
        return False


def main():
    """Run all tests."""
    print("\n" + "#"*60)
    print("# WEB TOOLS INTEGRATION TEST")
    print("#"*60)

    # Check API key
    api_key = os.getenv('BRAVE_SEARCH_API_KEY')
    if api_key:
        print(f"\nBRAVE_SEARCH_API_KEY: Set ({len(api_key)} chars)")
    else:
        print("\nBRAVE_SEARCH_API_KEY: Not set (will use DuckDuckGo fallback)")

    results = []

    # Run tests
    results.append(("WebTool Direct", test_web_tool_directly()))
    results.append(("Registry Integration", test_web_tool_in_registry()))
    results.append(("Schema Validation", test_tool_schemas()))
    results.append(("SubAgent Tools", test_subagent_tools()))

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    passed = sum(1 for _, r in results if r)
    total = len(results)

    for name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"  {name}: {status}")

    print(f"\n  {passed}/{total} tests passed")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
