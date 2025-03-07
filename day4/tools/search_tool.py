"""
Web Search Tool using DuckDuckGo search engine.
"""

from typing import Optional
from langchain.tools import BaseTool
from langchain.callbacks.manager import CallbackManagerForToolRun
import sys
import os
from pathlib import Path

# Add the root directory to Python path to import the tools
root_dir = Path(__file__).resolve().parents[2]
sys.path.append(str(root_dir))

from tools.search_engine import search_with_retry

class WebSearchTool(BaseTool):
    """Tool that performs web searches using DuckDuckGo."""
    
    name = "web_search"
    description = """Useful for searching the web for current information.
    Input should be a search query.
    Examples:
    - "latest news about AI"
    - "weather in London"
    - "who won the last Super Bowl"
    """
    
    def _format_results(self, results, max_results=3):
        """Format search results into a readable string."""
        if not results:
            return "No results found."
        
        formatted = []
        for i, r in enumerate(results[:max_results], 1):
            formatted.append(f"Result {i}:")
            formatted.append(f"Title: {r.get('title', 'N/A')}")
            formatted.append(f"Summary: {r.get('body', 'N/A')}")
            formatted.append(f"URL: {r.get('href', 'N/A')}")
            formatted.append("")  # Empty line between results
        
        return "\n".join(formatted)
    
    def _run(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Execute the web search tool."""
        try:
            # Perform the search
            results = search_with_retry(query, max_results=3)
            
            # Format and return results
            return self._format_results(results)
            
        except Exception as e:
            return f"Error performing web search: {str(e)}"
    
    def _arun(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Async version of the web search tool."""
        raise NotImplementedError("WebSearchTool does not support async")

# Example usage
if __name__ == "__main__":
    search_tool = WebSearchTool()
    
    # Test searches
    test_queries = [
        "latest news about artificial intelligence",
        "weather in London",
        "who is Claude Shannon"
    ]
    
    for query in test_queries:
        print(f"\nSearching for: {query}")
        result = search_tool.run(query)
        print(result) 