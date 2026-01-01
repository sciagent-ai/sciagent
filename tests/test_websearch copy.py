#!/usr/bin/env python3
"""
Test script for enhanced WebSearch tool.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'sciagent'))

from sciagent.tools.core.web_search import WebSearchTool

def test_basic_search():
    """Test basic search functionality."""
    print("=" * 60)
    print("TEST 1: Basic Search (DuckDuckGo fallback)")
    print("=" * 60)
    
    tool = WebSearchTool()
    result = tool.run({
        "query": "what is machine learning",
        "num_results": 3
    })
    
    print(f"Success: {result.get('success')}")
    print(f"Strategy: {result.get('search_strategy', 'standard')}")
    print(f"Results: {result.get('num_results')}")
    if result.get('success'):
        print("\n" + result.get('output', '')[:200] + "...")
    else:
        print(f"Error: {result.get('error')}")

def test_simple_strategy():
    """Test simple search strategy."""
    print("\n" + "=" * 60)
    print("TEST 2: Simple Strategy (Documentation Query)")
    print("=" * 60)
    
    tool = WebSearchTool()
    result = tool.run({
        "query": "FastAPI documentation",
        "num_results": 2,
        "search_strategy": "simple"
    })
    
    print(f"Success: {result.get('success')}")
    print(f"Strategy: {result.get('search_strategy', 'not set')}")
    print(f"Content Fetched: {result.get('content_fetched')}")
    if result.get('success'):
        print("\n" + result.get('output', '')[:300] + "...")

def test_progressive_strategy():
    """Test progressive search strategy."""
    print("\n" + "=" * 60)
    print("TEST 3: Progressive Strategy (Research Query)")
    print("=" * 60)
    
    tool = WebSearchTool()
    result = tool.run({
        "query": "comprehensive analysis of quantum computing algorithms",
        "num_results": 4,
        "search_strategy": "progressive"
    })
    
    print(f"Success: {result.get('success')}")
    print(f"Strategy: {result.get('search_strategy', 'not set')}")
    print(f"Phases: {result.get('search_phases', 'N/A')}")
    if result.get('success'):
        print("\n" + result.get('output', '')[:400] + "...")

def test_content_fetching():
    """Test content fetching capabilities."""
    print("\n" + "=" * 60)
    print("TEST 4: Content Fetching")
    print("=" * 60)
    
    tool = WebSearchTool()
    result = tool.run({
        "query": "Python tutorial",
        "num_results": 2,
        "fetch_content": True,
        "max_content_fetch": 1
    })
    
    print(f"Success: {result.get('success')}")
    print(f"Content Fetched: {result.get('content_fetched')}")
    if result.get('success'):
        output = result.get('output', '')
        print(f"\nContains 'Enhanced Summary': {'Enhanced Summary' in output}")
        print(f"Contains 'Content:': {'Content:' in output}")
        print("\n" + output[:500] + "...")

def test_auto_classification():
    """Test automatic query classification."""
    print("\n" + "=" * 60)
    print("TEST 5: Auto Classification")
    print("=" * 60)
    
    tool = WebSearchTool()
    
    # Test different query types
    test_queries = [
        "what is Docker",  # Should be simple
        "comprehensive overview of cloud computing architectures security best practices",  # Should be progressive
        "React vs Angular comparison"  # Should be standard
    ]
    
    for query in test_queries:
        strategy = tool.classify_query_complexity(query)
        print(f"Query: '{query[:40]}...'")
        print(f"  -> Classified as: {strategy}")

if __name__ == "__main__":
    print("Testing Enhanced WebSearch Tool")
    print("Note: This will use DuckDuckGo since BRAVE_SEARCH_API_KEY is not set")
    print()
    
    try:
        test_basic_search()
        test_simple_strategy() 
        test_progressive_strategy()
        test_content_fetching()
        test_auto_classification()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS COMPLETED")
        print("=" * 60)
        print("\n💡 To enable Brave Search:")
        print("   export BRAVE_SEARCH_API_KEY=your_api_key")
        print("   Get API key from: https://brave.com/search/api/")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()