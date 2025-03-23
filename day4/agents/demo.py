import asyncio
from typing import Dict, List, Optional
from pydantic import BaseModel
import json
from datetime import datetime

class Parameter(BaseModel):
    name: str
    unit: str
    min: float
    max: float

class Requirement(BaseModel):
    parameter: str
    unit: str
    min: float
    max: float

class Requirements(BaseModel):
    application_area: str
    requirements: List[Requirement]
    features: List[str]

class Product(BaseModel):
    id: str
    name: str
    description: str
    parameters: Dict[str, Dict]
    features: List[str]
    applications: List[str]
    datasheet_url: str

class Solution(BaseModel):
    id: str
    name: str
    description: str
    requirements: Dict[str, Dict]
    reference_designs: List[Dict]
    products: List[Dict]

class ADIEngineerAgent:
    def __init__(self):
        # Mock product database
        self.products = {
            "AD8422": {
                "id": "AD8422",
                "name": "Precision Instrumentation Amplifier",
                "description": "Low power, rail-to-rail instrumentation amplifier with high CMRR",
                "parameters": {
                    "supply_voltage": {
                        "min": 2.7,
                        "max": 5.5,
                        "unit": "V"
                    },
                    "gain": {
                        "min": 1,
                        "max": 1000,
                        "unit": "V/V"
                    }
                },
                "features": ["low power", "rail-to-rail", "precision"],
                "applications": ["sensor interface", "medical instrumentation"],
                "datasheet_url": "https://www.analog.com/media/en/technical-documentation/data-sheets/AD8422.pdf"
            },
            "AD7124-8": {
                "id": "AD7124-8",
                "name": "Low Power, 24-Bit Sigma-Delta ADC",
                "description": "Low power, 24-bit sigma-delta ADC with integrated PGA",
                "parameters": {
                    "supply_voltage": {
                        "min": 2.7,
                        "max": 5.5,
                        "unit": "V"
                    },
                    "temperature_range": {
                        "min": -40,
                        "max": 85,
                        "unit": "°C"
                    }
                },
                "features": ["low power", "24-bit", "integrated PGA"],
                "applications": ["sensor interface", "industrial measurement"],
                "datasheet_url": "https://www.analog.com/media/en/technical-documentation/data-sheets/AD7124-8.pdf"
            }
        }

        # Mock solutions database
        self.solutions = {
            "CN0428": {
                "id": "CN0428",
                "name": "Temperature Measurement System",
                "description": "Complete temperature measurement solution with high accuracy",
                "requirements": {
                    "supply_voltage": {
                        "min": 2.7,
                        "max": 5.5,
                        "unit": "V"
                    },
                    "temperature_range": {
                        "min": -40,
                        "max": 85,
                        "unit": "°C"
                    }
                },
                "reference_designs": [
                    {
                        "id": "CN0428-SCH",
                        "name": "Schematic",
                        "format": "schematic",
                        "url": "https://www.analog.com/media/en/technical-documentation/reference-designs/CN0428-SCH.pdf"
                    }
                ],
                "products": [
                    {
                        "id": "AD8422",
                        "name": "Precision Instrumentation Amplifier",
                        "role": "signal conditioning"
                    },
                    {
                        "id": "AD7124-8",
                        "name": "Low Power, 24-Bit Sigma-Delta ADC",
                        "role": "analog-to-digital conversion"
                    }
                ]
            }
        }

    async def extract_requirements(self, query: str) -> Requirements:
        """Extract requirements from natural language query."""
        # In a real implementation, this would use an LLM
        if "3.3V" in query:
            return Requirements(
                application_area="sensor interface",
                requirements=[
                    Requirement(
                        parameter="supply_voltage",
                        unit="V",
                        min=3.3,
                        max=3.3
                    )
                ],
                features=["instrumentation amplifier"]
            )
        elif "5V" in query and "temperature" in query:
            return Requirements(
                application_area="precision measurement",
                requirements=[
                    Requirement(
                        parameter="supply_voltage",
                        unit="V",
                        min=5.0,
                        max=5.0
                    ),
                    Requirement(
                        parameter="temperature_range",
                        unit="°C",
                        min=-40,
                        max=85
                    )
                ],
                features=["low power", "reference design", "schematic"]
            )
        else:
            return Requirements(
                application_area="amplifier",
                requirements=[
                    Requirement(
                        parameter="supply_voltage",
                        unit="V",
                        min=10.0,
                        max=10.0
                    )
                ],
                features=[]
            )

    async def search_products(self, requirements: Requirements) -> List[Product]:
        """Search for products matching the requirements."""
        matching_products = []
        for product_id, product_data in self.products.items():
            product = Product(**product_data)
            if self._validate_requirements(product, requirements):
                matching_products.append(product)
        return matching_products

    async def search_solutions(self, requirements: Requirements) -> List[Solution]:
        """Search for solutions matching the requirements."""
        matching_solutions = []
        for solution_id, solution_data in self.solutions.items():
            solution = Solution(**solution_data)
            if self._validate_solution_requirements(solution, requirements):
                matching_solutions.append(solution)
        return matching_solutions

    def _validate_requirements(self, product: Product, requirements: Requirements) -> bool:
        """Validate if a product meets the requirements."""
        for req in requirements.requirements:
            if req.parameter in product.parameters:
                param = product.parameters[req.parameter]
                if req.min < param["min"] or req.max > param["max"]:
                    return False
        return True

    def _validate_solution_requirements(self, solution: Solution, requirements: Requirements) -> bool:
        """Validate if a solution meets the requirements."""
        for req in requirements.requirements:
            if req.parameter in solution.requirements:
                param = solution.requirements[req.parameter]
                if req.min < param["min"] or req.max > param["max"]:
                    return False
        return True

    async def analyze_parameters(self, products: List[Product], requirements: Requirements) -> Dict:
        """Analyze parameters of products against requirements."""
        comparison = {}
        validation = {}
        compatibility = {}

        for product in products:
            validation[product.id] = {}
            for req in requirements.requirements:
                if req.parameter in product.parameters:
                    param = product.parameters[req.parameter]
                    validation[product.id][req.parameter] = {
                        "status": "valid" if req.min >= param["min"] and req.max <= param["max"] else "invalid",
                        "message": "Parameter within range" if req.min >= param["min"] and req.max <= param["max"] else "Parameter out of range"
                    }

            compatibility[product.id] = {
                "status": "compatible" if all(v["status"] == "valid" for v in validation[product.id].values()) else "incompatible",
                "message": "Product meets all requirements" if all(v["status"] == "valid" for v in validation[product.id].values()) else "Product does not meet all requirements"
            }

        return {
            "comparison": comparison,
            "validation": validation,
            "compatibility": compatibility
        }

    async def run(self, query: str) -> Dict:
        """Run the complete recommendation process."""
        print(f"\nProcessing query: {query}")
        print("-" * 50)

        # Extract requirements
        requirements = await self.extract_requirements(query)
        print("\nExtracted Requirements:")
        print(json.dumps(requirements.dict(), indent=2))

        # Search for products
        products = await self.search_products(requirements)
        print("\nMatching Products:")
        print(json.dumps([p.dict() for p in products], indent=2))

        # Search for solutions
        solutions = await self.search_solutions(requirements)
        print("\nMatching Solutions:")
        print(json.dumps([s.dict() for s in solutions], indent=2))

        # Analyze parameters
        analysis = await self.analyze_parameters(products, requirements)
        print("\nParameter Analysis:")
        print(json.dumps(analysis, indent=2))

        return {
            "requirements": requirements.dict(),
            "products": [p.dict() for p in products],
            "solutions": [s.dict() for s in solutions],
            "analysis": analysis
        }

async def main():
    agent = ADIEngineerAgent()
    
    # Demo queries
    queries = [
        "I need an instrumentation amplifier for a sensor interface with 3.3V supply",
        """
        Looking for a solution for a precision measurement system:
        - Supply voltage: 5V
        - Temperature range: -40°C to 85°C
        - Need reference design with schematic
        - Low power consumption
        """,
        "Find an amplifier with invalid supply voltage 10V"
    ]

    print("ADI Engineer Agent Demo")
    print("=" * 50)

    for query in queries:
        try:
            await agent.run(query)
            print("\n" + "=" * 50)
        except Exception as e:
            print(f"\nError processing query: {str(e)}")
            print("=" * 50)

if __name__ == "__main__":
    asyncio.run(main()) 