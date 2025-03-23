"""
Tests for the ADI Engineer Agent and its tools.
"""

import pytest
from unittest.mock import Mock, patch
import numpy as np

from day4.agents.adi_engineer_agent import ADIEngineerAgent
from day4.agents.tools import (
    VectorSearchTool,
    ProductRecommendationTool,
    SolutionExplorerTool,
    ParameterAnalysisTool
)

# Mock data for testing
MOCK_PRODUCTS = {
    "AD8232": {
        "id": "AD8232",
        "name": "AD8232",
        "category": "Amplifiers",
        "description": "Single-Lead, Heart Rate Monitor Front End",
        "features": ["Low Power", "Medical"],
        "applications": ["Medical", "Industrial"],
        "specs": {
            "supply_voltage": {"min": 2.7, "max": 5.5, "unit": "V"},
            "power_consumption": {"value": 0.5, "unit": "mW"}
        }
    },
    "ADuM4121": {
        "id": "ADuM4121",
        "name": "ADuM4121",
        "category": "Isolators",
        "description": "High Speed Digital Isolator",
        "features": ["High Speed", "Safety"],
        "applications": ["Industrial", "Medical"],
        "specs": {
            "supply_voltage": {"min": 3.0, "max": 5.5, "unit": "V"},
            "isolation_voltage": {"value": 5000, "unit": "V"}
        }
    }
}

MOCK_CATEGORIES = {
    "Amplifiers": {
        "id": "Amplifiers",
        "name": "Amplifiers",
        "description": "Operational amplifiers and instrumentation amplifiers",
        "features": ["Low Power", "High Speed", "Precision"],
        "applications": ["Medical", "Industrial", "Automotive"]
    },
    "Isolators": {
        "id": "Isolators",
        "name": "Isolators",
        "description": "Digital and analog isolators",
        "features": ["Safety", "High Speed", "Low Power"],
        "applications": ["Industrial", "Medical", "Automotive"]
    }
}

MOCK_SOLUTIONS = {
    "ECG_Monitoring": {
        "id": "ECG_Monitoring",
        "name": "ECG Monitoring Solution",
        "description": "Complete solution for ECG monitoring",
        "application_domains": ["Medical"],
        "requirements": {
            "supply_voltage": {
                "min": 2.7,
                "max": 5.5,
                "unit": "V"
            }
        },
        "reference_designs": [
            {
                "id": "RD001",
                "name": "ECG Front End",
                "format": "Schematic",
                "url": "https://example.com/ecg-front-end"
            }
        ]
    },
    "Motor_Control": {
        "id": "Motor_Control",
        "name": "Motor Control Solution",
        "description": "Complete solution for motor control",
        "application_domains": ["Industrial"],
        "requirements": {
            "supply_voltage": {
                "min": 3.0,
                "max": 5.5,
                "unit": "V"
            }
        },
        "reference_designs": [
            {
                "id": "RD002",
                "name": "Motor Drive Circuit",
                "format": "Schematic",
                "url": "https://example.com/motor-drive"
            }
        ]
    }
}

class TestVectorSearchTool:
    """Test cases for VectorSearchTool."""

    @pytest.fixture(autouse=True)
    def setUp(self):
        """Set up test fixtures."""
        self.mock_embeddings = Mock()
        self.mock_embeddings.embed_query.return_value = np.array([0.1, 0.2, 0.3])
        self.tool = VectorSearchTool(
            embeddings=self.mock_embeddings,
            products=MOCK_PRODUCTS,
            categories=MOCK_CATEGORIES,
            solutions=MOCK_SOLUTIONS
        )

    def test_basic_search(self):
        """Test basic vector search functionality."""
        query = "Find low power amplifiers for medical applications"
        results = self.tool.run({
            "query": query,
            "search_type": "products",
            "top_k": 2
        })
        assert isinstance(results, list)
        assert len(results) > 0
        assert "AD8232" in [r["id"] for r in results]

    def test_category_search(self):
        """Test searching in categories."""
        query = "Find amplifier categories"
        results = self.tool.run({
            "query": query,
            "search_type": "categories",
            "top_k": 1
        })
        assert isinstance(results, list)
        assert len(results) > 0
        assert "Amplifiers" in [r["id"] for r in results]

    def test_solution_search(self):
        """Test searching in solutions."""
        query = "Find ECG monitoring solutions"
        results = self.tool.run({
            "query": query,
            "search_type": "solutions",
            "top_k": 1
        })
        assert isinstance(results, list)
        assert len(results) > 0
        assert "ECG_Monitoring" in [r["id"] for r in results]

    def test_min_score_filter(self):
        """Test filtering by minimum similarity score."""
        query = "Find low power amplifiers"
        results = self.tool.run({
            "query": query,
            "search_type": "products",
            "min_score": 0.9
        })
        assert isinstance(results, list)
        assert all(r["score"] >= 0.9 for r in results)

    def test_invalid_search_type(self):
        """Test handling of invalid search type."""
        query = "Find products"
        with pytest.raises(ValueError):
            self.tool.run({
                "query": query,
                "search_type": "invalid",
                "top_k": 1
            })

class TestProductRecommendationTool:
    """Test cases for ProductRecommendationTool."""

    @pytest.fixture(autouse=True)
    def setUp(self):
        """Set up test fixtures."""
        self.tool = ProductRecommendationTool(products=MOCK_PRODUCTS)

    def test_basic_recommendation(self):
        """Test basic product recommendation."""
        requirements = {
            "application_area": "Medical",
            "requirements": [
                {
                    "parameter": "supply_voltage",
                    "unit": "V",
                    "min": 2.7,
                    "max": 5.5
                }
            ],
            "features": ["Low Power"]
        }
        results = self.tool.run(requirements)
        assert isinstance(results, list)
        assert len(results) > 0
        assert "AD8232" in [r["id"] for r in results]

    def test_no_matches(self):
        """Test when no products match requirements."""
        requirements = {
            "application_area": "Medical",
            "requirements": [
                {
                    "parameter": "supply_voltage",
                    "unit": "V",
                    "min": 6.0,
                    "max": 12.0
                }
            ]
        }
        results = self.tool.run(requirements)
        assert isinstance(results, list)
        assert len(results) == 0

    def test_invalid_parameter(self):
        """Test handling of invalid parameter."""
        requirements = {
            "application_area": "Medical",
            "requirements": [
                {
                    "parameter": "invalid_param",
                    "unit": "V",
                    "min": 2.7,
                    "max": 5.5
                }
            ]
        }
        with pytest.raises(ValueError):
            self.tool.run(requirements)

    def test_invalid_requirement_format(self):
        """Test handling of invalid requirement format."""
        requirements = {
            "application_area": "Medical",
            "requirements": [
                {
                    "parameter": "supply_voltage"
                    # Missing unit
                }
            ]
        }
        with pytest.raises(ValueError):
            self.tool.run(requirements)

class TestSolutionExplorerTool:
    """Test cases for SolutionExplorerTool."""

    @pytest.fixture(autouse=True)
    def setUp(self):
        """Set up test fixtures."""
        self.tool = SolutionExplorerTool(solutions=MOCK_SOLUTIONS)

    def test_basic_solution_search(self):
        """Test basic solution search."""
        query = {
            "application_domain": "Medical",
            "requirements": {
                "supply_voltage": {
                    "min": 2.7,
                    "max": 5.5,
                    "unit": "V"
                }
            }
        }
        results = self.tool.run(query)
        assert isinstance(results, list)
        assert len(results) > 0
        assert "ECG_Monitoring" in [r["id"] for r in results]

    def test_no_matches(self):
        """Test when no solutions match requirements."""
        query = {
            "application_domain": "Medical",
            "requirements": {
                "supply_voltage": {
                    "min": 6.0,
                    "max": 12.0,
                    "unit": "V"
                }
            }
        }
        results = self.tool.run(query)
        assert isinstance(results, list)
        assert len(results) == 0

    def test_format_filter(self):
        """Test filtering reference designs by format."""
        query = {
            "application_domain": "Medical",
            "format": "Schematic"
        }
        results = self.tool.run(query)
        assert isinstance(results, list)
        assert len(results) > 0
        assert all(r["reference_designs"][0]["format"] == "Schematic" for r in results)

    def test_invalid_domain(self):
        """Test handling of invalid application domain."""
        query = {
            "application_domain": "Invalid",
            "requirements": {}
        }
        results = self.tool.run(query)
        assert isinstance(results, list)
        assert len(results) == 0

class TestParameterAnalysisTool:
    """Test cases for ParameterAnalysisTool."""

    @pytest.fixture(autouse=True)
    def setUp(self):
        """Set up test fixtures."""
        self.tool = ParameterAnalysisTool(products=MOCK_PRODUCTS)

    def test_basic_comparison(self):
        """Test basic parameter comparison."""
        query = {
            "products": ["AD8232", "ADuM4121"],
            "parameters": ["supply_voltage"]
        }
        results = self.tool.run(query)
        assert isinstance(results, dict)
        assert "supply_voltage" in results
        assert "values" in results["supply_voltage"]
        assert "AD8232" in results["supply_voltage"]["values"]
        assert "ADuM4121" in results["supply_voltage"]["values"]

    def test_unit_normalization(self):
        """Test unit normalization for comparison."""
        query = {
            "products": ["AD8232", "ADuM4121"],
            "parameters": ["supply_voltage"],
            "constraints": {
                "supply_voltage": {
                    "min": 2000,  # mV
                    "unit": "mV"
                }
            }
        }
        results = self.tool.run(query)
        assert isinstance(results, dict)
        assert "supply_voltage" in results
        assert "violations" in results["supply_voltage"]

    def test_constraint_validation(self):
        """Test constraint validation."""
        query = {
            "products": ["AD8232", "ADuM4121"],
            "parameters": ["supply_voltage"],
            "constraints": {
                "supply_voltage": {
                    "max": 3.0,  # V
                    "unit": "V"
                }
            }
        }
        results = self.tool.run(query)
        assert isinstance(results, dict)
        assert "supply_voltage" in results
        assert "violations" in results["supply_voltage"]
        assert len(results["supply_voltage"]["violations"]) > 0

    def test_missing_parameter(self):
        """Test handling of missing parameter."""
        query = {
            "products": ["AD8232", "ADuM4121"],
            "parameters": ["invalid_param"]
        }
        with pytest.raises(ValueError):
            self.tool.run(query)

    def test_missing_products(self):
        """Test handling of missing products."""
        query = {
            "products": [],
            "parameters": ["supply_voltage"]
        }
        with pytest.raises(ValueError):
            self.tool.run(query)

class TestADIEngineerAgent:
    """Test cases for ADIEngineerAgent."""

    @pytest.fixture(autouse=True)
    def setUp(self):
        """Set up test fixtures."""
        self.mock_embeddings = Mock()
        self.mock_embeddings.embed_query.return_value = np.array([0.1, 0.2, 0.3])
        self.agent = ADIEngineerAgent(
            products=MOCK_PRODUCTS,
            categories=MOCK_CATEGORIES,
            solutions=MOCK_SOLUTIONS,
            embeddings=self.mock_embeddings
        )

    def test_requirement_extraction(self):
        """Test extraction of requirements from user input."""
        user_input = "I need a low power amplifier for heart rate monitoring with supply voltage 2.7V to 5.5V"
        requirements = self.agent._extract_requirements(user_input)
        assert isinstance(requirements, dict)
        assert "application_area" in requirements
        assert "requirements" in requirements
        assert "features" in requirements

    def test_recommendation_formatting(self):
        """Test formatting of recommendations."""
        products = [
            {
                "id": "AD8232",
                "name": "AD8232",
                "category": "Amplifiers",
                "specs": {
                    "supply_voltage": {"min": 2.7, "max": 5.5, "unit": "V"}
                }
            }
        ]
        solutions = [
            {
                "id": "ECG_Monitoring",
                "name": "ECG Monitoring Solution",
                "description": "Complete solution for ECG monitoring"
            }
        ]
        formatted = self.agent._format_recommendations(products, solutions)
        assert isinstance(formatted, str)
        assert "AD8232" in formatted
        assert "ECG Monitoring Solution" in formatted

    def test_basic_query(self):
        """Test basic query handling."""
        user_input = "I need a low power amplifier for heart rate monitoring with supply voltage 2.7V to 5.5V"
        response = self.agent.run(user_input)
        assert isinstance(response, str)
        assert "AD8232" in response

    def test_no_matches(self):
        """Test handling of queries with no matches."""
        user_input = "I need a high voltage amplifier with 12V supply"
        response = self.agent.run(user_input)
        assert isinstance(response, str)
        # Check for any indication that no matches were found
        assert any(phrase in response.lower() for phrase in ["no matches", "no products match", "found no", "not found", "no match"])

    def test_error_handling(self):
        """Test error handling for invalid input."""
        user_input = ""
        response = self.agent.run(user_input)
        assert isinstance(response, str)
        assert "error" in response.lower() or "couldn't understand" in response.lower() 