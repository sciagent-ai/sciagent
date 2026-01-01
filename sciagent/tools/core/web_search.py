"""
Web search tool.

Perform web searches using Brave Search API (primary) or DuckDuckGo (fallback).
Enhanced with content fetching and intelligent analysis capabilities.
"""

from __future__ import annotations

from typing import Dict, Any, Optional, List
import requests
import re
from bs4 import BeautifulSoup
import time

from sciagent.base_tool import BaseTool

try:
    from ddgs import DDGS  # type: ignore[import-not-found]
except Exception:
    DDGS = None  # type: ignore

try:
    import requests
    BRAVE_AVAILABLE = True
except ImportError:
    BRAVE_AVAILABLE = False

try:
    import html2text
    HTML2TEXT_AVAILABLE = True
except ImportError:
    HTML2TEXT_AVAILABLE = False


class WebSearchTool(BaseTool):
    """Search the web for solutions and information with intelligent search strategies."""

    name = "web_search"
    description = "Search the web for solutions and information with intelligent search strategies"
    input_schema: Dict[str, Any] = {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search query"},
            "num_results": {"type": "number", "description": "Number of results", "default": 5},
            "fetch_content": {"type": "boolean", "description": "Fetch and analyze full content from top results", "default": False},
            "max_content_fetch": {"type": "number", "description": "Maximum number of pages to fetch content from", "default": 3},
            "search_strategy": {"type": "string", "description": "Search strategy: 'simple', 'progressive', or 'standard'", "enum": ["simple", "progressive", "standard"], "default": "auto"},
        },
        "required": ["query"],
    }

    def classify_query_complexity(self, query: str) -> str:
        """Classify if query needs simple, progressive, or standard search strategy."""
        query_lower = query.lower()
        query_words = query.split()
        
        # Simple query indicators
        simple_patterns = [
            len(query_words) <= 3,                    # Short queries
            query_lower.startswith(('what is', 'how to', 'where is')),  # Direct questions
            'documentation' in query_lower,           # Doc lookups
            'tutorial' in query_lower,                # Learning resources
            query_lower.startswith('github.com'),     # Specific URLs
            query_lower.endswith(' docs'),            # Documentation requests
        ]
        
        # Progressive (complex) query indicators  
        progressive_patterns = [
            len(query_words) >= 8,                    # Long queries
            'comprehensive' in query_lower,           # Research keywords
            'compare' in query_lower,
            'comparison' in query_lower,
            'architectures' in query_lower,
            'best practices' in query_lower,
            'survey' in query_lower,
            'overview' in query_lower,
            'analysis' in query_lower,
            'report' in query_lower,
            'state of the art' in query_lower,
            'landscape' in query_lower,
        ]
        
        if any(simple_patterns):
            return "simple"
        elif any(progressive_patterns):
            return "progressive"
        else:
            return "standard"  # Current behavior

    def _clean_html_content(self, html_content: str) -> str:
        """Extract clean text from HTML content."""
        try:
            if HTML2TEXT_AVAILABLE:
                h = html2text.HTML2Text()
                h.ignore_links = True
                h.ignore_images = True
                h.ignore_emphasis = False
                return h.handle(html_content)
            else:
                # Fallback to BeautifulSoup
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Remove script and style elements
                for script in soup(["script", "style", "nav", "header", "footer", "aside"]):
                    script.decompose()
                
                # Get text and clean it up
                text = soup.get_text()
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = ' '.join(chunk for chunk in chunks if chunk)
                
                return text
        except Exception as e:
            return f"Error extracting content: {str(e)}"

    def _fetch_page_content(self, url: str, timeout: int = 10) -> Dict[str, Any]:
        """Fetch and extract content from a single URL."""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
            response.raise_for_status()
            
            # Extract clean text content
            clean_content = self._clean_html_content(response.text)
            
            # Truncate if too long
            max_content_length = 3000
            if len(clean_content) > max_content_length:
                clean_content = clean_content[:max_content_length] + "..."
            
            return {
                "success": True,
                "content": clean_content,
                "content_length": len(clean_content),
                "status_code": response.status_code
            }
            
        except requests.exceptions.Timeout:
            return {"success": False, "error": "Request timeout"}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": f"Request failed: {str(e)}"}
        except Exception as e:
            return {"success": False, "error": f"Content extraction failed: {str(e)}"}

    def _analyze_fetched_content(self, results_with_content: List[Dict[str, Any]], query: str) -> str:
        """Analyze fetched content and create enhanced summaries."""
        analyzed_results = []
        
        for i, result in enumerate(results_with_content, 1):
            title = result.get('title', 'Unknown Title')
            href = result.get('href', '')
            original_body = result.get('body', '')
            content_data = result.get('fetched_content', {})
            
            if content_data.get('success') and content_data.get('content'):
                # Enhanced content available
                full_content = content_data['content']
                
                # Create a more detailed summary
                # Extract first few sentences or paragraphs
                sentences = re.split(r'[.!?]+', full_content)
                relevant_sentences = []
                
                # Look for sentences that might be relevant to the query
                query_words = query.lower().split()
                for sentence in sentences[:10]:  # Check first 10 sentences
                    sentence = sentence.strip()
                    if len(sentence) > 20:  # Skip very short sentences
                        # Check if sentence contains query terms
                        sentence_lower = sentence.lower()
                        if any(word in sentence_lower for word in query_words):
                            relevant_sentences.append(sentence)
                        elif not relevant_sentences and len(sentence) > 50:
                            # If no relevant sentences found yet, include substantial first sentence
                            relevant_sentences.append(sentence)
                
                # Create enhanced summary
                if relevant_sentences:
                    enhanced_summary = '. '.join(relevant_sentences[:2]) + '.'
                    if len(enhanced_summary) > 400:
                        enhanced_summary = enhanced_summary[:400] + "..."
                else:
                    # Fallback to first part of content
                    enhanced_summary = full_content[:300] + "..."
                
                analyzed_results.append(
                    f"{i}. **[{title}]({href})**\n"
                    f"   📄 Enhanced Summary: {enhanced_summary}\n"
                    f"   📊 Content: {content_data.get('content_length', 0)} chars analyzed\n"
                )
                
            else:
                # Fallback to original snippet
                error_msg = content_data.get('error', 'Content fetch failed')
                analyzed_results.append(
                    f"{i}. **[{title}]({href})**\n"
                    f"   📄 Basic Summary: {original_body}\n"
                    f"   ⚠️ Full content unavailable: {error_msg}\n"
                )
        
        return "\n".join(analyzed_results)

    def _search_brave(self, query: str, num_results: int) -> List[Dict[str, Any]]:
        """Search using Brave Search API."""
        import os
        
        api_key = os.getenv('BRAVE_SEARCH_API_KEY')
        if not api_key:
            print("⚠️ BRAVE_SEARCH_API_KEY not found in environment")
            return []
        
        try:
            url = "https://api.search.brave.com/res/v1/web/search"
            headers = {
                "Accept": "application/json",
                "Accept-Encoding": "gzip",
                "X-Subscription-Token": api_key
            }
            params = {
                "q": query,
                "count": num_results,
                "search_lang": "en",
                "country": "us",
                "safesearch": "moderate"
            }
            
            print(f"🔍 Searching Brave for: '{query}'")
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            if 'web' in data and 'results' in data['web']:
                for result in data['web']['results']:
                    results.append({
                        'title': result.get('title', ''),
                        'href': result.get('url', ''),
                        'body': result.get('description', '')
                    })
            
            print(f"📊 Brave returned {len(results)} results")
            return results
            
        except Exception as e:
            print(f"❌ Brave search failed: {str(e)}")
            return []

    def run(self, tool_input: Dict[str, Any], agent: Optional[Any] = None) -> Dict[str, Any]:
        try:
            query = tool_input.get("query", "")
            num_results = int(tool_input.get("num_results", 5))
            fetch_content = tool_input.get("fetch_content", False)
            max_content_fetch = min(int(tool_input.get("max_content_fetch", 3)), num_results)
            
            # Determine search strategy
            search_strategy = tool_input.get("search_strategy", "auto")
            if search_strategy == "auto":
                search_strategy = self.classify_query_complexity(query)
            
            print(f"🧠 Using {search_strategy} search strategy for: '{query}'")
            
            # Route to appropriate search method
            if search_strategy == "simple":
                return self._simple_search(query, tool_input)
            elif search_strategy == "progressive":
                return self._progressive_search(query, tool_input, agent)
            else:
                # Standard search (current behavior)
                return self._standard_search(query, tool_input)
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _standard_search(self, query: str, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """Standard search - current behavior for backward compatibility."""
        num_results = int(tool_input.get("num_results", 5))
        fetch_content = tool_input.get("fetch_content", False)
        max_content_fetch = min(int(tool_input.get("max_content_fetch", 3)), num_results)
        
        results: List[Dict[str, Any]] = []
        search_provider = "unknown"
        
        # Try Brave Search first (if API key available)
        if BRAVE_AVAILABLE:
            results = self._search_brave(query, num_results)
            search_provider = "Brave"
        
        # Fallback to DuckDuckGo if Brave fails or unavailable
        if not results and DDGS is not None:
            try:
                print(f"🔍 Searching DuckDuckGo for: '{query}'")
                with DDGS() as ddgs:
                    search_results = list(ddgs.text(query, max_results=num_results))
                    results = search_results
                    search_provider = "DuckDuckGo"
                print(f"📊 DuckDuckGo returned {len(results)} results")
            except Exception as e:
                print(f"❌ DuckDuckGo search failed: {str(e)}")
        
        # Debug logging for result processing
        print(f"🔍 Processing {len(results)} results from {search_provider}")
        if results:
            print(f"✅ Found {len(results)} search results")
        
        # Final check - if no search engines available
        if not results and DDGS is None and not BRAVE_AVAILABLE:
            return {
                "success": False,
                "error": "Web search is unavailable. Neither Brave Search API key nor duckduckgo_search is available.",
            }
            
        if not results:
            return {"success": False, "error": f"No results found for query: '{query}'"}
        
        if fetch_content:
            # Fetch content from top results
            for i, result in enumerate(results[:max_content_fetch]):
                url = result.get('href', '')
                if url:
                    content_data = self._fetch_page_content(url)
                    result['fetched_content'] = content_data
                    # Add small delay to be respectful
                    if i < max_content_fetch - 1:
                        time.sleep(1)
            
            # Use enhanced formatting with content analysis
            formatted_results = self._analyze_fetched_content(results[:max_content_fetch], query)
            
            # Add remaining results without content
            if len(results) > max_content_fetch:
                remaining_results = []
                for i, res in enumerate(results[max_content_fetch:], max_content_fetch + 1):
                    remaining_results.append(
                        f"{i}. [{res['title']}]({res['href']})\n   {res['body']}"
                    )
                if remaining_results:
                    formatted_results += "\n\n**Additional Results (summaries only):**\n\n" + "\n\n".join(remaining_results)
            
            output_header = f"🔍 Enhanced web search results for '{query}' (via {search_provider}, content analyzed):\n\n"
            
        else:
            # Standard formatting without content fetching
            formatted_results = "\n\n".join([
                f"{i+1}. [{res['title']}]({res['href']})\n{res['body']}"
                for i, res in enumerate(results)
            ])
            output_header = f"🔍 Web search results for '{query}' (via {search_provider}):\n\n"
        
        return {
            "success": True,
            "output": output_header + formatted_results,
            "query": query,
            "num_results": len(results),
            "results": results,
            "content_fetched": fetch_content,
            "placeholder": False,
        }

    def _simple_search(self, query: str, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """Optimized search for simple, direct queries."""
        print(f"🏃 Fast search for direct query")
        
        # Use fewer results but smarter content fetching
        results: List[Dict[str, Any]] = []
        search_provider = "unknown"
        
        # Try Brave Search first with limited results
        if BRAVE_AVAILABLE:
            results = self._search_brave(query, 3)  # Only 3 results
            search_provider = "Brave"
        
        # Fallback to DuckDuckGo 
        if not results and DDGS is not None:
            try:
                with DDGS() as ddgs:
                    search_results = list(ddgs.text(query, max_results=3))
                    results = search_results
                    search_provider = "DuckDuckGo"
            except Exception as e:
                print(f"❌ DuckDuckGo search failed: {str(e)}")
        
        if not results:
            return {"success": False, "error": f"No results found for query: '{query}'"}
        
        # Smart content fetching - only from most relevant result
        best_result = None
        for result in results:
            title_lower = result.get('title', '').lower()
            # Prefer documentation, official sources
            if any(keyword in title_lower for keyword in ['documentation', 'official', 'docs', 'tutorial']):
                best_result = result
                break
        
        if not best_result:
            best_result = results[0]  # Fallback to first result
        
        # Fetch content only from best result
        content_data = self._fetch_page_content(best_result.get('href', ''))
        best_result['fetched_content'] = content_data
        
        # Format results with focus on the best match
        if content_data.get('success'):
            main_content = self._analyze_fetched_content([best_result], query)
            other_results = "\n\n".join([
                f"{i+2}. [{res['title']}]({res['href']})\n   {res['body']}"
                for i, res in enumerate(results[1:])
            ])
            formatted_results = main_content + ("\n\n**Other Results:**\n\n" + other_results if other_results else "")
        else:
            # Fallback to standard formatting
            formatted_results = "\n\n".join([
                f"{i+1}. [{res['title']}]({res['href']})\n{res['body']}"
                for i, res in enumerate(results)
            ])
        
        output_header = f"🔍 Quick search results for '{query}' (via {search_provider}):\n\n"
        
        return {
            "success": True,
            "output": output_header + formatted_results,
            "query": query,
            "num_results": len(results),
            "results": results,
            "content_fetched": True,
            "search_strategy": "simple",
            "placeholder": False,
        }

    def _progressive_search(self, query: str, tool_input: Dict[str, Any], agent: Optional[Any] = None) -> Dict[str, Any]:
        """Multi-phase progressive search for complex research queries."""
        print(f"🔬 Progressive search for complex research")
        
        all_results = []
        search_phases = []
        
        # Phase 1: Overview search (broad, no content fetch)
        overview_query = f"{query} overview"
        overview_results = []
        
        if BRAVE_AVAILABLE:
            overview_results = self._search_brave(overview_query, 5)
            search_provider = "Brave"
        elif DDGS is not None:
            try:
                with DDGS() as ddgs:
                    overview_results = list(ddgs.text(overview_query, max_results=5))
                    search_provider = "DuckDuckGo"
            except Exception:
                pass
        
        if overview_results:
            search_phases.append(("Overview", overview_results))
            all_results.extend(overview_results[:3])  # Take top 3
            
            # Extract key terms from overview for targeted search
            key_terms = self._extract_key_terms_from_results(overview_results, query)
        else:
            key_terms = []
        
        # Phase 2: Targeted search based on key terms
        if key_terms:
            targeted_query = f"{query} {' '.join(key_terms[:2])}"
            print(f"🎯 Targeted search: {targeted_query}")
            
            targeted_results = []
            if BRAVE_AVAILABLE:
                targeted_results = self._search_brave(targeted_query, 3)
            elif DDGS is not None:
                try:
                    with DDGS() as ddgs:
                        targeted_results = list(ddgs.text(targeted_query, max_results=3))
                except Exception:
                    pass
            
            if targeted_results:
                search_phases.append(("Targeted", targeted_results))
                
                # Fetch content from top 2 targeted results
                for result in targeted_results[:2]:
                    content_data = self._fetch_page_content(result.get('href', ''))
                    result['fetched_content'] = content_data
                    time.sleep(1)  # Be respectful
                
                all_results.extend(targeted_results)
        
        if not all_results:
            return {"success": False, "error": f"No results found for query: '{query}'"}
        
        # Format progressive results with phase organization
        formatted_sections = []
        
        for phase_name, phase_results in search_phases:
            if phase_name == "Targeted" and any(r.get('fetched_content', {}).get('success') for r in phase_results):
                # Use detailed content analysis for targeted results
                section_content = self._analyze_fetched_content(
                    [r for r in phase_results if r.get('fetched_content', {}).get('success')], 
                    query
                )
            else:
                # Use basic formatting for overview
                section_content = "\n".join([
                    f"   • [{res['title']}]({res['href']})\n     {res['body'][:100]}..."
                    for res in phase_results[:3]
                ])
            
            formatted_sections.append(f"**{phase_name} Phase:**\n{section_content}")
        
        formatted_results = "\n\n".join(formatted_sections)
        output_header = f"🔍 Progressive search results for '{query}' (via {search_provider}, {len(search_phases)} phases):\n\n"
        
        return {
            "success": True,
            "output": output_header + formatted_results,
            "query": query,
            "num_results": len(all_results),
            "results": all_results,
            "content_fetched": True,
            "search_strategy": "progressive",
            "search_phases": len(search_phases),
            "placeholder": False,
        }

    def _extract_key_terms_from_results(self, results: List[Dict[str, Any]], original_query: str) -> List[str]:
        """Extract relevant technical terms from search results for follow-up queries."""
        # Combine all text from results
        text = " ".join([
            r.get('title', '') + " " + r.get('body', '') 
            for r in results
        ])
        
        original_terms = set(word.lower() for word in original_query.split())
        
        # Look for technical patterns
        import re
        tech_patterns = re.findall(r'\b[A-Z][a-z]+(?:[A-Z][a-z]*)*\b', text)  # CamelCase
        frameworks = re.findall(r'\b(?:React|Angular|Vue|Django|Flask|FastAPI|TensorFlow|PyTorch|Kubernetes|Docker)\b', text, re.IGNORECASE)
        
        candidate_terms = tech_patterns + frameworks
        
        # Filter out original query terms and common words
        stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should', 'could', 'can', 'may', 'might', 'must'}
        new_terms = [
            term for term in candidate_terms 
            if term.lower() not in original_terms and term.lower() not in stop_words and len(term) > 3
        ]
        
        # Return top 3 most frequent terms
        from collections import Counter
        return [term for term, count in Counter(new_terms).most_common(3)]


def get_tool() -> BaseTool:
    return WebSearchTool()