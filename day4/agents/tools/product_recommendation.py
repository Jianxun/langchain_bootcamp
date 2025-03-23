"""
Product Recommendation Tool for ADI products based on technical requirements.
"""

import json
from typing import Dict, List, Optional, Any, Union, Type
from langchain.tools import BaseTool
from langchain.callbacks.manager import CallbackManagerForToolRun
from pydantic import Field, BaseModel

class ProductRecommendationInput(BaseModel):
    application_area: str
    requirements: List[Dict]

class ProductRecommendationTool(BaseTool):
    """Tool for recommending ADI products based on technical requirements and application constraints."""
    
    name: str = "product_recommendation"
    description: str = """Use this tool to recommend products based on technical requirements.
    Input should be a JSON string with the following structure:
    {
        "application_area": "string",
        "requirements": [
            {
                "parameter": "string",
                "unit": "string",
                "min": float,
                "max": float
            }
        ]
    }
    """
    args_schema: Type[BaseModel] = ProductRecommendationInput
    
    @property
    def is_single_input(self) -> bool:
        """Whether the tool only accepts a single input."""
        return True
    
    products: Dict[str, Dict] = Field(
        default_factory=lambda: {
            "AD8232": {
                "name": "Low Power Instrumentation Amplifier",
                "description": "Low power instrumentation amplifier for medical applications",
                "parameters": {
                    "supply_voltage": {"unit": "V", "min": 2.7, "max": 5.5},
                    "power_consumption": {"unit": "mW", "min": 0.1, "max": 0.5}
                }
            }
        }
    )
    
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

    def _check_unit_compatibility(self, spec_unit: str, req_unit: str) -> bool:
        """Check if the units are compatible."""
        # Simple unit compatibility check - they should match exactly for now
        # TODO: Add unit conversion support
        return spec_unit == req_unit

    def _normalize_parameter_name(self, param: str) -> str:
        """Normalize parameter name to match product data format."""
        # Convert spaces to underscores and make lowercase
        return param.lower().replace(" ", "_")

    def _validate_requirement(self, requirement: Dict) -> None:
        """Validate a single requirement."""
        if not isinstance(requirement, dict):
            raise ValueError("Each requirement must be a dictionary")
        
        required_fields = ["parameter", "unit", "min", "max"]
        for field in required_fields:
            if field not in requirement:
                raise ValueError(f"Missing required field '{field}' in requirement")
        
        if not isinstance(requirement["parameter"], str):
            raise ValueError("Parameter must be a string")
        
        if not isinstance(requirement["unit"], str):
            raise ValueError("Unit must be a string")
        
        # Validate that the parameter exists in at least one product
        param = self._normalize_parameter_name(requirement["parameter"])
        param_exists = False
        for product in self.products.values():
            # Check both "parameters" and "specs" fields
            if param in product.get("parameters", {}) or param in product.get("specs", {}):
                param_exists = True
                break
        if not param_exists:
            raise ValueError(f"Unknown parameter: {requirement['parameter']}")

    def _parse_value(self, value: Union[str, float, int]) -> float:
        """Parse a value into a float, handling special cases."""
        # Convert numeric values to strings
        if isinstance(value, (int, float)):
            value_str = str(value)
        else:
            value_str = value.lower().strip()
        
        # Handle special cases
        if value_str == "low":
            return 0.0
        elif value_str == "high":
            return float("inf")
        elif value_str == "medium":
            return 5.0  # Default medium value
        elif value_str == "ultra-low":
            return 0.01
        elif value_str == "ultra-high":
            return 1000.0
            
        # Handle numeric values
        try:
            return float(value_str)
        except ValueError:
            raise ValueError(f"Invalid value format: {value_str}")

    def _meets_requirements(self, product: dict, requirements: List[dict]) -> bool:
        """Check if a product meets all requirements."""
        for req in requirements:
            param = self._normalize_parameter_name(req["parameter"])
            # Check both "parameters" and "specs" fields
            if param not in product.get("parameters", {}) and param not in product.get("specs", {}):
                return False

            # Get the spec from either field
            spec = product.get("parameters", {}).get(param) or product.get("specs", {}).get(param)
            if not isinstance(spec, dict):
                continue

            try:
                # Parse requirement values
                req_min = self._parse_value(req["min"])
                req_max = self._parse_value(req["max"])
                
                # Parse specification values
                spec_min = self._parse_value(spec.get("min", "0"))
                spec_max = self._parse_value(spec.get("max", "inf"))
                
                # Check if ranges overlap
                if spec_min > req_max or spec_max < req_min:
                    return False
                    
            except (ValueError, TypeError) as e:
                print(f"Warning: Error comparing values for {param}: {str(e)}")
                continue

        return True

    def _matches_features(self, product: Dict, features: List[str]) -> bool:
        """Check if a product matches the required features."""
        product_features = set(f.lower() for f in product.get("features", []))
        required_features = set(f.lower() for f in features)
        return required_features.issubset(product_features)

    def _matches_application(self, product: Dict, application_area: str) -> bool:
        """Check if a product is suitable for the application area."""
        return application_area.lower() in [a.lower() for a in product.get("applications", [])]

    def run(self, input_str: Union[str, Dict]) -> List[Dict]:
        """Run the product recommendation tool."""
        try:
            # Handle both string and dictionary inputs
            if isinstance(input_str, str):
                input_data = json.loads(input_str)
            else:
                input_data = input_str

            requirements = input_data.get("requirements", [])
            application_area = input_data.get("application_area", "")
            features = input_data.get("features", [])

            # Validate requirements first
            for req in requirements:
                self._validate_requirement(req)

            # Filter products based on requirements
            matching_products = []
            for product_id, product in self.products.items():
                if self._meets_requirements(product, requirements):
                    matching_products.append(product)

            # Sort by relevance to application area and features
            if application_area or features:
                matching_products.sort(
                    key=lambda p: (
                        application_area.lower() in p.get("description", "").lower(),
                        len(set(features) & set(p.get("features", [])))
                    ),
                    reverse=True
                )

            return matching_products
        except json.JSONDecodeError:
            raise ValueError("Invalid input format")
        except Exception as e:
            raise ValueError(f"Error processing requirements: {str(e)}")

    def _run(
        self,
        requirements: str,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Execute the tool."""
        try:
            # Parse input as JSON
            requirements_data = json.loads(requirements)
            
            # Execute recommendation
            results = self.run(requirements_data)
            
            # Format results as JSON
            return json.dumps(results, indent=2)
            
        except Exception as e:
            return f"Error finding recommendations: {str(e)}"

    async def _arun(self, requirements: Dict) -> List[Dict]:
        """Async version of the tool."""
        raise NotImplementedError("ProductRecommendationTool does not support async") 