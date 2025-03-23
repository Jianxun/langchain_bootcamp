"""
Parameter Analysis Tool for comparing technical parameters across ADI products.
"""

from typing import Dict, List, Optional, Any, Type
from langchain.tools import BaseTool
from langchain.callbacks.manager import CallbackManagerForToolRun
from pydantic import Field, BaseModel

class ParameterAnalysisInput(BaseModel):
    products: List[str]
    parameters: List[str]
    constraints: Dict[str, Dict]

class ParameterAnalysisTool(BaseTool):
    """Tool for analyzing and comparing technical parameters across products."""
    
    name: str = "parameter_analysis"
    description: str = """Use this tool to analyze and compare technical parameters across products.
    Input should be a JSON string with the following structure:
    {
        "products": ["string"],
        "parameters": ["string"],
        "constraints": {
            "parameter": "string",
            "min": float,
            "max": float,
            "unit": "string"
        }
    }
    """
    args_schema: Type[BaseModel] = ParameterAnalysisInput
    
    @property
    def is_single_input(self) -> bool:
        """Whether the tool only accepts a single input."""
        return True
    
    products: Dict[str, Dict] = Field(
        default_factory=dict,
        description="Dictionary of product data"
    )
    
    def _extract_parameter_value(self, spec: Dict) -> float:
        """Extract a single numeric value from a specification."""
        if "value" in spec:
            return spec["value"]
        elif "typ" in spec:
            return spec["typ"]
        elif "min" in spec and "max" in spec:
            return (spec["min"] + spec["max"]) / 2
        else:
            raise ValueError(f"Invalid specification format: {spec}")

    def _check_unit_compatibility(self, spec_unit: str, req_unit: str) -> bool:
        """Check if the units are compatible."""
        # Simple unit compatibility check - they should match exactly for now
        # TODO: Add unit conversion support
        return spec_unit == req_unit

    def _normalize_value(self, value: float, unit: str) -> float:
        """Normalize a value to a standard unit for comparison."""
        # TODO: Add unit conversion support
        return value

    def _validate_constraints(self, value: float, constraints: Dict) -> List[str]:
        """Validate a value against constraints and return any violations."""
        violations = []
        
        if "min" in constraints and value < constraints["min"]:
            violations.append(f"Value {value} is below minimum {constraints['min']}")
        if "max" in constraints and value > constraints["max"]:
            violations.append(f"Value {value} is above maximum {constraints['max']}")
        if "value" in constraints and abs(value - constraints["value"]) / constraints["value"] > 0.1:
            violations.append(f"Value {value} is not close to required {constraints['value']}")
            
        return violations

    def run(self, query: Dict) -> Dict:
        """
        Run the parameter analysis tool.
        
        Args:
            query: Dict containing:
                - products: List[str], list of product IDs to compare
                - parameters: List[str], list of parameters to analyze
                - constraints: Optional[Dict[str, Dict]], constraints for each parameter
        
        Returns:
            Dict: Analysis results including parameter comparisons and constraint violations
        """
        product_ids = query.get("products", [])
        parameters = query.get("parameters", [])
        constraints = query.get("constraints", {})
        
        if not product_ids:
            raise ValueError("No products specified")
        if not parameters:
            raise ValueError("No parameters specified")
            
        # Validate products exist
        for product_id in product_ids:
            if product_id not in self.products:
                raise ValueError(f"Product not found: {product_id}")
        
        # Filter out unknown parameters
        known_parameters = []
        unknown_parameters = []
        for param in parameters:
            if param in next(iter(self.products.values()))["specs"]:
                known_parameters.append(param)
            else:
                unknown_parameters.append(param)
        
        if not known_parameters:
            raise ValueError(f"No valid parameters found. Unknown parameters: {', '.join(unknown_parameters)}")
        
        # Compare parameters
        comparison = {}
        for param in known_parameters:
            param_comparison = {
                "parameter": param,
                "unit": next(iter(self.products.values()))["specs"][param]["unit"],
                "values": {},
                "violations": []
            }
            
            # Extract and normalize values for each product
            for product_id in product_ids:
                product = self.products[product_id]
                spec = product["specs"][param]
                
                try:
                    value = self._extract_parameter_value(spec)
                    normalized_value = self._normalize_value(value, spec["unit"])
                    param_comparison["values"][product_id] = {
                        "value": value,
                        "normalized": normalized_value,
                        "spec": spec
                    }
                except ValueError as e:
                    param_comparison["values"][product_id] = {
                        "error": str(e),
                        "spec": spec
                    }
            
            # Check constraints if specified
            if param in constraints:
                for product_id, value_info in param_comparison["values"].items():
                    if "error" not in value_info:
                        violations = self._validate_constraints(
                            value_info["normalized"],
                            constraints[param]
                        )
                        if violations:
                            param_comparison["violations"].append({
                                "product": product_id,
                                "violations": violations
                            })
            
            comparison[param] = param_comparison
        
        if unknown_parameters:
            comparison["unknown_parameters"] = unknown_parameters
        
        return comparison

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
            
            # Execute parameter analysis
            results = self.run(query_data)
            
            # Format results as JSON
            return json.dumps(results, indent=2)
            
        except ValueError as e:
            if "No valid parameters found" in str(e):
                # Extract unknown parameters from error message
                unknown_params = str(e).split("Unknown parameters: ")[1]
                return f"Cannot analyze parameters: {unknown_params} are not available in product specifications. Available parameters are: supply_voltage, isolation_voltage"
            return f"Error analyzing parameters: {str(e)}"
        except Exception as e:
            return f"Error analyzing parameters: {str(e)}"

    async def _arun(self, query: Dict) -> Dict:
        """Async version of the tool."""
        raise NotImplementedError("ParameterAnalysisTool does not support async") 