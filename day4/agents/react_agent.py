"""
ReAct (Reasoning + Acting) Agent Implementation
This agent follows the pattern of:
1. Observe the current state
2. Think about what to do
3. Act on the decision
4. Repeat until task is complete
"""

from typing import List, Optional, Any
from langchain_openai import ChatOpenAI
from langchain.agents import AgentType, initialize_agent
from langchain.tools import Tool, BaseTool
from langchain.callbacks.manager import CallbackManagerForToolRun
import os
from dotenv import load_dotenv
import sys
import asyncio
import time
from pathlib import Path
from langchain_community.utilities import WikipediaAPIWrapper

# Add the root directory to Python path to import the tools
root_dir = Path(__file__).resolve().parents[2]
sys.path.append(str(root_dir))

from tools.search_engine import search_with_retry
from tools.web_scraper import process_urls

# Load environment variables
load_dotenv()

class SearchTool(BaseTool):
    """Tool that performs web searches and can scrape content from web pages."""
    name: str = "Search"
    description: str = """Use this tool to search for information on the internet and optionally scrape webpage content.
    Input should be a specific search query.
    The tool will return relevant search results with titles and summaries.
    For Wikipedia pages, it will automatically fetch the article content using the Wikipedia API."""
    
    def _run(self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Execute the search tool."""
        try:
            # Add delay between searches to avoid rate limiting
            time.sleep(2)
            
            # Get multiple results for better coverage
            results = search_with_retry(query, max_results=5)
            if not results:
                return "No results found."
            
            # Format search results
            formatted_results = []
            urls_to_scrape = []
            wiki_queries = set()  # Track Wikipedia queries to avoid duplicates
            
            for i, result in enumerate(results[:3], 1):  # Use top 3 results
                title = result.get('title', 'N/A')
                body = result.get('body', 'N/A')
                url = result.get('href', 'N/A')
                formatted_results.append(f"Result {i}:\nTitle: {title}\nSummary: {body}\nURL: {url}\n")
                
                # Handle Wikipedia URLs using the API
                if 'wikipedia.org/wiki/' in url.lower():
                    try:
                        # Extract article title from URL
                        article_title = url.split('/wiki/')[-1].replace('_', ' ')
                        wiki_queries.add(article_title)
                    except:
                        pass
                # Handle non-Wikipedia URLs with scraping
                elif url.lower().endswith(('.html', '/', '')):
                    urls_to_scrape.append(url)
            
            # Fetch Wikipedia content if any Wikipedia URLs were found
            if wiki_queries:
                try:
                    # Create Wikipedia API wrapper only when needed
                    wikipedia = WikipediaAPIWrapper(top_k_results=2)
                    for query in wiki_queries:
                        # Add delay between Wikipedia API calls
                        time.sleep(1)
                        wiki_content = wikipedia.run(query)
                        if wiki_content:
                            formatted_results.append(f"\nWikipedia Content for '{query}':")
                            formatted_results.append(wiki_content)
                except Exception as e:
                    formatted_results.append(f"\nNote: Could not fetch Wikipedia content: {str(e)}")
            
            # If we have other URLs to scrape, get their content
            if urls_to_scrape:
                try:
                    # Scrape content from websites
                    scraped_contents = asyncio.run(process_urls(urls_to_scrape, max_concurrent=2))
                    
                    # Add scraped content to results
                    for i, content in enumerate(scraped_contents):
                        if content:
                            # Split content into lines and take first few meaningful lines
                            content_lines = [line.strip() for line in content.split('\n') 
                                          if line.strip() and len(line.strip()) > 10][:5]
                            if content_lines:
                                formatted_results.append(f"\nExtracted Content from {urls_to_scrape[i]}:")
                                formatted_results.extend(content_lines)
                
                except Exception as e:
                    formatted_results.append(f"\nNote: Could not scrape detailed information: {str(e)}")
            
            return "\n".join(formatted_results)
            
        except Exception as e:
            return f"Error performing search: {str(e)}"
    
    def _arun(self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Async version of the search tool."""
        raise NotImplementedError("SearchTool does not support async")

class LookupTool(BaseTool):
    """Tool that performs calculations and information lookup."""
    name: str = "Lookup"
    description: str = """Use this tool for mathematical calculations and basic information lookup.
    For calculations, input should be a mathematical expression using operators: +, -, *, /, %, ^
    For lookups, input should be a specific query about facts or information.
    Examples:
    - "25 * 4"
    - "500 / 10"
    - "15% of 80" (write as "15 * 80 / 100")"""
    
    def _run(self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Execute the lookup tool."""
        try:
            # Check if it's a mathematical expression
            if any(op in query for op in ['+', '-', '*', '/', '%']):
                # Clean the input
                cleaned_query = query.replace('^', '**')  # Replace ^ with ** for exponents
                
                # Create a safe dictionary of allowed functions
                safe_dict = {
                    'abs': abs,
                    'round': round,
                    'min': min,
                    'max': max
                }
                
                # Evaluate the expression
                result = eval(cleaned_query, {"__builtins__": {}}, safe_dict)
                return f"Result: {result}"
            else:
                return f"Looking up information about: {query}"
            
        except Exception as e:
            return f"Error in lookup: {str(e)}"
    
    def _arun(self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Async version of the lookup tool."""
        raise NotImplementedError("LookupTool does not support async")

class ReActAgent:
    """
    ReAct Agent that can use tools to accomplish tasks through reasoning and acting.
    """
    
    def __init__(
        self,
        tools: Optional[List[BaseTool]] = None,
        llm: Optional[Any] = None,
        verbose: bool = False
    ):
        """
        Initialize the ReAct agent with tools and an optional language model.
        
        Args:
            tools: List of tools the agent can use (defaults to SearchTool and LookupTool)
            llm: Language model to use (defaults to ChatOpenAI)
            verbose: Whether to print detailed outputs
        """
        # Initialize default tools if none provided
        self.tools = tools or [SearchTool(), LookupTool()]
        self.llm = llm or ChatOpenAI(
            temperature=0,
            model="gpt-4-turbo-preview"
        )
        self.verbose = verbose
        
        # Initialize the agent with ZERO_SHOT_REACT_DESCRIPTION
        self.agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=self.verbose,
            handle_parsing_errors=True,
            max_iterations=8
        )
    
    def run(self, task: str) -> str:
        """
        Execute a task using the agent.
        
        Args:
            task: The task description
            
        Returns:
            The result of executing the task
        """
        try:
            return self.agent.run(task)
        except Exception as e:
            return f"Error executing task: {str(e)}"

# Example usage
if __name__ == "__main__":
    # Create agent with default tools
    agent = ReActAgent(verbose=True)
    
    # Run example tasks
    tasks = [
        "Calculate 25% of 80",
        "What is the capital of France and what is its population divided by 1000?",
        "How far can a 2024 Subaru Outback go on a full tank of gas?",
        "What is the distance between earth and the moon and how long does it take a radio signal to travel that distance?",
    ]
    
    for task in tasks:
        print(f"\nTask: {task}")
        result = agent.run(task)
        print(f"Result: {result}\n") 