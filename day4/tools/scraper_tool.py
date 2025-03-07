"""
Web Scraping Tool for extracting content from web pages.
"""

from typing import Optional, List
from langchain.tools import BaseTool
from langchain.callbacks.manager import CallbackManagerForToolRun
import sys
import os
import asyncio
from pathlib import Path
from urllib.parse import urlparse

# Add the root directory to Python path to import the tools
root_dir = Path(__file__).resolve().parents[2]
sys.path.append(str(root_dir))

from tools.web_scraper import process_urls, validate_url

class WebScraperTool(BaseTool):
    """Tool that scrapes content from web pages."""
    
    name = "web_scraper"
    description = """Useful for extracting content from web pages.
    Input should be a URL or a list of URLs (comma-separated).
    Examples:
    - "https://example.com"
    - "https://example.com, https://another-example.com"
    """
    
    def _parse_urls(self, input_str: str) -> List[str]:
        """Parse and validate URLs from input string."""
        # Split by comma and strip whitespace
        urls = [url.strip() for url in input_str.split(",")]
        
        # Validate URLs
        valid_urls = []
        for url in urls:
            if validate_url(url):
                valid_urls.append(url)
        
        return valid_urls
    
    def _run(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Execute the web scraping tool."""
        try:
            # Parse and validate URLs
            urls = self._parse_urls(query)
            if not urls:
                return "No valid URLs provided. Please provide valid URLs."
            
            # Run the scraper
            results = asyncio.run(process_urls(urls, max_concurrent=3))
            
            # Format results
            formatted_results = []
            for url, content in zip(urls, results):
                formatted_results.append(f"=== Content from {url} ===")
                # Limit content length to avoid overwhelming the agent
                content_preview = content[:1000] + "..." if len(content) > 1000 else content
                formatted_results.append(content_preview)
                formatted_results.append("=" * 80)
            
            return "\n".join(formatted_results)
            
        except Exception as e:
            return f"Error scraping web pages: {str(e)}"
    
    def _arun(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Async version of the web scraping tool."""
        raise NotImplementedError("WebScraperTool does not support async")

# Example usage
if __name__ == "__main__":
    scraper_tool = WebScraperTool()
    
    # Test URLs
    test_urls = [
        "https://example.com",
        "https://example.com, https://httpbin.org/html"
    ]
    
    for urls in test_urls:
        print(f"\nScraping: {urls}")
        result = scraper_tool.run(urls)
        print(result) 