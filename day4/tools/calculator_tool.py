"""
Calculator Tool for performing basic mathematical operations.
"""

from typing import Optional
from langchain.tools import BaseTool
from langchain.callbacks.manager import CallbackManagerForToolRun
import re
import math

class CalculatorTool(BaseTool):
    """Tool that performs basic mathematical calculations."""
    
    name = "calculator"
    description = """Useful for performing mathematical calculations.
    Input should be a mathematical expression using operators: +, -, *, /, **, sqrt, sin, cos, tan
    Examples:
    - "2 + 2"
    - "5 * 3"
    - "sqrt(16)"
    - "sin(30)"
    """
    
    def _clean_expression(self, expression: str) -> str:
        """Clean and validate the mathematical expression."""
        # Remove any characters that aren't mathematical operators or numbers
        cleaned = re.sub(r'[^0-9+\-*/().sqrt sin cos tan\s]', '', expression.lower())
        return cleaned
    
    def _evaluate_expression(self, expression: str) -> float:
        """Safely evaluate a mathematical expression."""
        # Define safe mathematical functions
        safe_dict = {
            'sqrt': math.sqrt,
            'sin': lambda x: math.sin(math.radians(x)),
            'cos': lambda x: math.cos(math.radians(x)),
            'tan': lambda x: math.tan(math.radians(x))
        }
        
        try:
            # Evaluate the expression in a safe context
            result = eval(expression, {"__builtins__": {}}, safe_dict)
            return float(result)
        except Exception as e:
            raise ValueError(f"Invalid mathematical expression: {str(e)}")
    
    def _run(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Execute the calculator tool."""
        try:
            # Clean the expression
            cleaned_expr = self._clean_expression(query)
            if not cleaned_expr:
                return "Please provide a valid mathematical expression"
            
            # Evaluate and return result
            result = self._evaluate_expression(cleaned_expr)
            return f"Result: {result}"
            
        except Exception as e:
            return f"Error calculating result: {str(e)}"
    
    def _arun(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Async version of the calculator tool."""
        raise NotImplementedError("CalculatorTool does not support async")

# Example usage
if __name__ == "__main__":
    calculator = CalculatorTool()
    
    # Test basic operations
    test_expressions = [
        "2 + 2",
        "10 - 5",
        "3 * 4",
        "15 / 3",
        "2 ** 3",
        "sqrt(16)",
        "sin(30)",
        "cos(60)",
        "tan(45)"
    ]
    
    for expr in test_expressions:
        result = calculator.run(expr)
        print(f"Expression: {expr}")
        print(f"{result}\n") 