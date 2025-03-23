"""
ADI Engineer Agent for helping customers explore ADI solutions and recommend products.
"""

import json
from typing import Dict, List, Optional, Any
from langchain.agents import AgentExecutor, initialize_agent, AgentType
from langchain.tools import Tool
from langchain_openai import ChatOpenAI
from langchain.prompts import MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
from langchain.schema import SystemMessage, HumanMessage, AIMessage

from .tools import (
    VectorSearchTool,
    ProductRecommendationTool,
    SolutionExplorerTool,
    ParameterAnalysisTool
)

class ADIEngineerAgent:
    """Agent for recommending ADI products based on user requirements."""
    
    def __init__(self, products: Optional[Dict] = None, categories: Optional[Dict] = None, solutions: Optional[Dict] = None, embeddings: Optional[Any] = None):
        """Initialize the ADI Engineer Agent."""
        # Initialize tools with provided data or defaults
        self.vector_search = VectorSearchTool(
            products=products or {},
            categories=categories or {},
            solutions=solutions or {},
            embeddings=embeddings
        )
        self.product_recommendation = ProductRecommendationTool(products=products or {})
        self.solution_explorer = SolutionExplorerTool(solutions=solutions or {})
        self.parameter_analysis = ParameterAnalysisTool(products=products or {})
        
        self.tools = [
            self.vector_search,
            self.product_recommendation,
            self.solution_explorer,
            self.parameter_analysis
        ]
        
        self.llm = ChatOpenAI(temperature=0)
        
        self.agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
            verbose=True,
            memory=ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True
            ),
            system_message="""You are an ADI Application Engineer helping customers find the right products.
            Follow these guidelines:
            1. When no products match the requirements, start your response with "No matches found:" or "No products match:"
            2. Explain why no matches were found and suggest alternatives if possible
            3. When recommending products, include specific product IDs and explain why they match the requirements
            4. For invalid or empty input, respond with "Error: Please provide valid requirements" or "Error: Input cannot be empty"
            5. Always format your responses in a clear, professional manner"""
        )
    
    def _extract_requirements(self, user_input: str) -> Dict:
        """Extract structured requirements from user input."""
        prompt = f"""Extract structured requirements from the following user input. Return a JSON object with:
- application_area: The main application area (e.g., "sensor interface", "power management")
- requirements: List of technical requirements, each with:
  - parameter: The parameter name (e.g., "supply voltage", "gain")
  - unit: The unit of measurement (e.g., "V", "dB")
  - min: Minimum value (can be numeric or string like "low")
  - max: Maximum value (can be numeric or string like "high")
- features: List of desired features (e.g., ["low power", "high accuracy"])

User input: {user_input}

Return only the JSON object, no other text."""

        try:
            response = self.llm.invoke(prompt)
            if isinstance(response, AIMessage):
                response = response.content
            requirements = json.loads(response)
            
            # Validate the structure
            if not isinstance(requirements, dict):
                raise ValueError("Requirements must be a dictionary")
            
            if "application_area" not in requirements:
                raise ValueError("Missing application_area field")
            
            if "requirements" not in requirements:
                raise ValueError("Missing requirements field")
            
            if "features" not in requirements:
                raise ValueError("Missing features field")
            
            return requirements
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse requirements JSON: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error extracting requirements: {str(e)}")
    
    def _format_recommendations(self, products: List[Dict], solutions: List[Dict]) -> str:
        """Format recommendations for display."""
        if not products and not solutions:
            return "No matches found: No products match the specified requirements."
        
        output = []
        
        if products:
            output.append("Recommended Products:")
            for product in products:
                output.append(f"- {product.get('id', '')}: {product.get('name', '')}")
                if "description" in product:
                    output.append(f"  Description: {product['description']}")
                
                # Check both parameters and specs fields
                specs = {}
                if "parameters" in product:
                    specs.update(product["parameters"])
                if "specs" in product:
                    specs.update(product["specs"])
                
                if specs:
                    output.append("  Key Specifications:")
                    for param, spec in specs.items():
                        if isinstance(spec, dict):
                            min_val = spec.get("min", spec.get("value", "N/A"))
                            max_val = spec.get("max", spec.get("value", "N/A"))
                            unit = spec.get("unit", "")
                            output.append(f"    {param}: {min_val} to {max_val} {unit}")
        
        if solutions:
            output.append("\nRelevant Solutions:")
            for solution in solutions:
                output.append(f"- {solution['name']}")
                if "description" in solution:
                    output.append(f"  Description: {solution['description']}")
                if "url" in solution:
                    output.append(f"  URL: {solution['url']}")
        
        return "\n".join(output)
    
    def run(self, user_input: str) -> str:
        """Process user input and return recommendations."""
        try:
            # Extract requirements
            requirements = self._extract_requirements(user_input)
            
            # Search for products
            try:
                # Convert requirements to the expected format
                product_query = {
                    "application_area": requirements["application_area"],
                    "requirements": requirements["requirements"],
                    "features": requirements.get("features", [])
                }
                
                # Call the product recommendation tool
                product_results = self.product_recommendation._run(json.dumps(product_query))
                matching_products = json.loads(product_results) if isinstance(product_results, str) else product_results
                
            except ValueError as e:
                # If no products match, return appropriate message
                if "Unknown parameter" in str(e):
                    return f"No matches found: {str(e)}"
                raise
            
            # Search for solutions
            try:
                # Convert requirements to the expected format
                solution_query = {
                    "application_domain": requirements["application_area"],
                    "requirements": requirements["requirements"],
                    "format": "all"  # Get all available formats
                }
                
                # Call the solution explorer tool
                solution_results = self.solution_explorer._run(json.dumps(solution_query))
                matching_solutions = json.loads(solution_results) if isinstance(solution_results, str) else solution_results
                
            except Exception as e:
                # If solution search fails, continue with empty solutions list
                matching_solutions = []
            
            # Format recommendations
            return self._format_recommendations(matching_products, matching_solutions)
            
        except Exception as e:
            return f"Error: {str(e)}" 