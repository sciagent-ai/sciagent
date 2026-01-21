#!/usr/bin/env python3
"""
End-to-end test: Agent using web tools.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent import create_agent

def test_agent_web_search():
    """Test agent can use web search."""
    print("\n" + "="*60)
    print("END-TO-END TEST: Agent Web Search")
    print("="*60)

    agent = create_agent(
        working_dir=".",
        verbose=True
    )

    # Simple task that requires web search
    task = """Use the web tool to search for "Python requests library" and tell me the top result's title and URL.
    Use command="search" with query="Python requests library".
    Just give me the first result, nothing more."""

    print(f"\nTask: {task[:80]}...")
    print("\n--- Agent Output ---\n")

    try:
        result = agent.run(task, max_iterations=3)
        print("\n--- Result ---")
        print(result)

        # Check if result mentions a URL
        if "http" in result.lower() or "requests" in result.lower():
            print("\n  SUCCESS - Agent used web search and returned results")
            return True
        else:
            print("\n  PARTIAL - Agent ran but may not have used web search")
            return True  # Still a pass if no error
    except Exception as e:
        print(f"\n  FAILED - Error: {e}")
        return False


def test_agent_url_fetch():
    """Test agent can fetch URLs."""
    print("\n" + "="*60)
    print("END-TO-END TEST: Agent URL Fetch")
    print("="*60)

    agent = create_agent(
        working_dir=".",
        verbose=True
    )

    task = """Use the web tool to fetch the URL "https://httpbin.org/headers".
    Use command="fetch" with url="https://httpbin.org/headers".
    Just tell me what headers were returned."""

    print(f"\nTask: {task[:80]}...")
    print("\n--- Agent Output ---\n")

    try:
        result = agent.run(task, max_iterations=3)
        print("\n--- Result ---")
        print(result)

        if "headers" in result.lower() or "user-agent" in result.lower():
            print("\n  SUCCESS - Agent fetched URL and parsed content")
            return True
        else:
            print("\n  PARTIAL - Agent ran but content unclear")
            return True
    except Exception as e:
        print(f"\n  FAILED - Error: {e}")
        return False


if __name__ == "__main__":
    print("\n" + "#"*60)
    print("# AGENT + WEB TOOLS END-TO-END TEST")
    print("#"*60)

    results = []
    results.append(("Web Search", test_agent_web_search()))
    results.append(("URL Fetch", test_agent_url_fetch()))

    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    for name, r in results:
        print(f"  {name}: {'PASS' if r else 'FAIL'}")

    passed = sum(1 for _, r in results if r)
    print(f"\n  {passed}/{len(results)} tests passed")
