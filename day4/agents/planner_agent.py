"""
Plan and Execute Agent Implementation

This agent follows a two-phase approach:
1. Planning Phase: Create a detailed plan of steps
2. Execution Phase: Execute each step in sequence

The agent can handle complex tasks by breaking them down into manageable steps.
"""

from typing import List, Optional, Dict, Any
from langchain_core.language_models.base import BaseLanguageModel
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from langchain.chains import LLMMathChain
from dotenv import load_dotenv
import json
import re

# Load environment variables
load_dotenv()

class Step(BaseModel):
    """A single step in the plan."""
    number: int = Field(description="Step number in the sequence")
    action: str = Field(description="The action to take")
    tool: str = Field(description="The tool to use for this action")
    input: str = Field(description="Input for the tool")

class Plan(BaseModel):
    """A complete plan with multiple steps."""
    steps: List[Step] = Field(description="List of steps in the plan")
    reasoning: str = Field(description="Reasoning behind the plan")

class PlanAndExecuteAgent:
    """Agent that plans and executes tasks using available tools."""

    def __init__(self, tools: List[BaseTool], llm: Optional[BaseLanguageModel] = None):
        """Initialize the agent with tools and an optional LLM."""
        self.tools = {tool.name: tool for tool in tools}
        self.llm = llm or ChatOpenAI(temperature=0, model="gpt-4o")
        self.planner_prompt = PromptTemplate(
            template=PLANNER_PROMPT,
            input_variables=["task", "tool_descriptions"]
        )

    def _extract_number(self, text: str) -> Optional[float]:
        """Extract the first number from text, handling various formats."""
        # Remove commas from numbers
        text = text.replace(",", "")
        # Look for numbers in scientific notation first
        sci_match = re.search(r'[-+]?\d*\.?\d+[eE][-+]?\d+', text)
        if sci_match:
            return float(sci_match.group())
        # Look for decimal numbers
        dec_match = re.search(r'[-+]?\d*\.?\d+', text)
        if dec_match:
            return float(dec_match.group())
        return None

    def _execute_step(self, step: Dict[str, Any]) -> str:
        """Execute a single step of the plan."""
        tool_name = step["tool"]
        if tool_name not in self.tools:
            return f"Error: Tool '{tool_name}' not found"
        
        tool = self.tools[tool_name]
        input_text = step["input"]
        
        # If this is a calculation step, try to extract numbers from previous results
        if tool_name == "Lookup" and "[" in input_text and "]" in input_text:
            # Replace placeholders with actual numbers if possible
            for placeholder in re.findall(r'\[(.*?)\]', input_text):
                number = self._extract_number(str(self.results))
                if number is not None:
                    input_text = input_text.replace(f"[{placeholder}]", str(number))
        
        try:
            result = tool.run(input_text)
            return result
        except Exception as e:
            return f"Error executing {tool_name}: {str(e)}"

    def run(self, task: str) -> str:
        """Run the agent on a task."""
        print(f"\nTask: {task}")
        print("Creating plan...")
        
        # Create the plan
        tool_descriptions = "\n".join(f"- {tool.name}: {tool.description}" for tool in self.tools.values())
        plan_creation = self.llm.invoke(
            self.planner_prompt.format(
                task=task,
                tool_descriptions=tool_descriptions
            )
        )
        
        try:
            # Parse the plan from the response
            plan_text = plan_creation.content
            # Extract the JSON part
            json_match = re.search(r'\{.*\}', plan_text, re.DOTALL)
            if not json_match:
                return "Error: Could not find JSON plan in response"
            
            plan_data = json.loads(json_match.group())
            steps = plan_data["plan"]
            reasoning = plan_data["reasoning"]
            
            print(f"\nReasoning: {reasoning}\n")
            
            # Execute each step
            self.results = []
            for step in steps:
                print(f"\nExecuting step {step['step']}: {step['action']}")
                result = self._execute_step(step)
                print(f"Result: {result}")
                self.results.append(result)
            
            return "\n".join(self.results)
        
        except json.JSONDecodeError:
            return "Error: Could not parse plan as JSON"
        except Exception as e:
            return f"Error executing plan: {str(e)}"

# Example usage
if __name__ == "__main__":
    import sys
    from pathlib import Path
    
    # Add the root directory to Python path to import the tools
    root_dir = Path(__file__).resolve().parents[2]
    sys.path.append(str(root_dir))
    
    # Import our existing tools
    from tools.search_engine import search_with_retry
    from tools.web_scraper import process_urls
    from langchain_community.utilities import WikipediaAPIWrapper
    
    class SearchTool(BaseTool):
        """Tool that performs web searches and can scrape content from web pages."""
        name: str = "Search"
        description: str = """Use this tool to search for information on the internet.
        Input should be a specific search query.
        The tool will return relevant search results with titles and summaries.
        For Wikipedia pages, it will automatically fetch the article content."""
        
        def _run(self, query: str) -> str:
            try:
                results = search_with_retry(query, max_results=3)
                if not results:
                    return "No results found."
                
                formatted_results = []
                for i, r in enumerate(results, 1):
                    title = r.get('title', 'N/A')
                    body = r.get('body', 'N/A')
                    url = r.get('href', 'N/A')
                    formatted_results.append(f"Result {i}:")
                    formatted_results.append(f"Title: {title}")
                    formatted_results.append(f"Summary: {body}")
                    formatted_results.append(f"URL: {url}\n")
                
                return "\n".join(formatted_results)
                
            except Exception as e:
                return f"Error performing search: {str(e)}"
        
        async def _arun(self, query: str) -> str:
            raise NotImplementedError("SearchTool does not support async")
    
    class LookupTool(BaseTool):
        """Tool that performs calculations using LangChain's math capabilities."""
        name = "Lookup"
        description = """Use this tool for mathematical calculations. 
        Input should be a mathematical expression with explicit numbers, e.g.:
        - "15 * 37115000" to calculate 15% of 37,115,000
        - "225000000 / 384400" to divide 225,000,000 by 384,400
        Do not use variables or text in the expression. Only use numbers and operators (+, -, *, /, **, etc.)."""
        
        def __init__(self, **data):
            """Initialize the tool with a math chain."""
            super().__init__(**data)
            self._math_chain = LLMMathChain.from_llm(llm=ChatOpenAI(temperature=0, model="gpt-4o"), verbose=True)
        
        def _run(self, query: str) -> str:
            """Execute the calculation using the math chain."""
            try:
                result = self._math_chain.run(query)
                # Extract just the number if the result contains an answer
                if "Answer:" in result:
                    result = result.split("Answer:")[1].strip()
                return f"Result: {result}"
            except Exception as e:
                return f"Error in calculation: {str(e)}"
        
        async def _arun(self, query: str) -> str:
            """Async version of the lookup tool."""
            raise NotImplementedError("LookupTool does not support async")
    
    # Create agent with our tools
    agent = PlanAndExecuteAgent(
        tools=[SearchTool(), LookupTool()],
        verbose=True
    )
    
    # Example tasks that require multiple steps
    tasks = [
        "What is the population of Tokyo and what is 15% of that number?",
        "Find the distance between Earth and Mars, then calculate how many times that distance could fit between Earth and the Moon",
        "What is the GDP of France, and what is that number divided by its population?"
    ]
    
    # Run tasks
    for task in tasks:
        print(f"\nTask: {task}")
        result = agent.run(task)
        
        # Print the plan
        print("\nPlan:")
        for step in result['plan']['steps']:
            print(f"{step['number']}. {step['action']} (using {step['tool']})")
        print(f"\nReasoning: {result['plan']['reasoning']}")
        
        # Print results
        print("\nResults:")
        for step_result in result['results']:
            step = step_result['step']
            print(f"\nStep {step['number']} ({step['action']}):")
            print(step_result['result']) 