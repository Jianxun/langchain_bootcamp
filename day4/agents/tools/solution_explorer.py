"""
Solution Explorer Tool for finding relevant ADI solutions and reference designs.
"""

from typing import Dict, List, Optional, Any, Type
from langchain.tools import BaseTool
from langchain.callbacks.manager import CallbackManagerForToolRun
from pydantic import Field, BaseModel

class SolutionExplorerInput(BaseModel):
    application_domain: str
    requirements: Optional[List[Dict[str, float]]] = None
    format: Optional[str] = None

class SolutionExplorerTool(BaseTool):
    """Tool for exploring ADI solutions and reference designs."""
    
    name: str = "solution_explorer"
    description: str = """Use this tool to explore ADI solutions and reference designs.
    Input should be a JSON string with the following structure:
    {
        "application_domain": "string",
        "requirements": [
            {
                "parameter": "string",
                "value": float,
                "unit": "string"
            }
        ],
        "format": "string"
    }
    """
    args_schema: Type[BaseModel] = SolutionExplorerInput
    
    @property
    def is_single_input(self) -> bool:
        """Whether the tool only accepts a single input."""
        return True
    
    solutions: Dict[str, Dict] = Field(
        default_factory=dict,
        description="Dictionary of solution data"
    )
    
    def _matches_requirements(self, solution: Dict, requirements: Dict) -> bool:
        """Check if a solution meets the technical requirements."""
        if not requirements:
            return True
            
        for param, req in requirements.items():
            if param not in solution["requirements"]:
                return False
            
            if not self._check_value_constraint(solution["requirements"][param], req):
                return False
        
        return True

    def _check_value_constraint(self, spec_value: Dict, requirement: Dict) -> bool:
        """Check if a specification value meets the requirement constraints."""
        if "value" in spec_value:
            # For exact value specifications
            if "value" in requirement:
                return spec_value["value"] == requirement["value"]
            if "min" in requirement and spec_value["value"] < requirement["min"]:
                return False
            if "max" in requirement and spec_value["value"] > requirement["max"]:
                return False
        elif "typ" in spec_value:
            # For typical value specifications
            if "value" in requirement:
                return abs(spec_value["typ"] - requirement["value"]) / requirement["value"] < 0.1
            if "min" in requirement and spec_value["typ"] < requirement["min"]:
                return False
            if "max" in requirement and spec_value["typ"] > requirement["max"]:
                return False
        else:
            # For min/max range specifications
            if "value" in requirement:
                return (spec_value.get("min", float("-inf")) <= requirement["value"] <= 
                       spec_value.get("max", float("inf")))
            if ("min" in requirement and "max" in spec_value and 
                spec_value["max"] < requirement["min"]):
                return False
            if ("max" in requirement and "min" in spec_value and 
                spec_value["min"] > requirement["max"]):
                return False
        return True

    def _matches_domain(self, solution: Dict, domain: str) -> bool:
        """Check if a solution matches the application domain."""
        return domain in solution["application_domains"]

    def _filter_reference_designs(self, designs: List[Dict], format: Optional[str] = None) -> List[Dict]:
        """Filter reference designs by format if specified."""
        if not format:
            return designs
        return [d for d in designs if d["format"] == format]

    def run(self, query: Dict) -> List[Dict]:
        """
        Run the solution explorer tool.
        
        Args:
            query: Dict containing:
                - application_domain: str, target application domain
                - requirements: Optional[Dict[str, Dict]], technical requirements
                - format: Optional[str], desired reference design format
        
        Returns:
            List[Dict]: List of matching solutions with their reference designs
        """
        domain = query.get("application_domain")
        requirements = query.get("requirements", {})
        format = query.get("format")
        
        matches = []
        for solution_id, solution in self.solutions.items():
            # Check application domain if specified
            if domain and not self._matches_domain(solution, domain):
                continue
                
            # Check technical requirements if specified
            if requirements and not self._matches_requirements(solution, requirements):
                continue
                
            # Filter reference designs by format if specified
            filtered_designs = self._filter_reference_designs(solution["reference_designs"], format)
            
            # Add to matches if any reference designs match
            if filtered_designs:
                matches.append({
                    "id": solution_id,
                    "name": solution["name"],
                    "description": solution["description"],
                    "application_domains": solution["application_domains"],
                    "reference_designs": filtered_designs
                })
        
        return matches

    def _run(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Execute the tool."""
        try:
            import json
            # Parse input as JSON
            query_data = json.loads(query)
            
            # Execute solution search
            results = self.run(query_data)
            
            # Format results as JSON
            return json.dumps(results, indent=2)
            
        except Exception as e:
            return f"Error finding solutions: {str(e)}"

    async def _arun(self, query: Dict) -> List[Dict]:
        """Async version of the tool."""
        raise NotImplementedError("SolutionExplorerTool does not support async") 