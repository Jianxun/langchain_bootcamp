# ADI Engineer Agent Tools Documentation

## VectorSearchTool

### Purpose
Performs semantic search across products, categories, and solutions using vector embeddings.

### Implementation
```python
class VectorSearchTool(BaseTool):
    name: str = "vector_search"
    description: str = "Search for products, categories, or solutions using semantic similarity"
    
    def __init__(self, products: Dict, categories: Dict, solutions: Dict, embeddings: Any):
        self.embeddings = embeddings
        self.product_store = FAISS.from_texts(
            texts=[p["description"] for p in products.values()],
            metadatas=list(products.values()),
            embedding=self.embeddings
        )
        # Similar stores for categories and solutions
```

### Input Format
```json
{
    "query": "string",
    "search_type": "products" | "categories" | "solutions",
    "top_k": int,
    "min_score": float
}
```

### Output Format
```json
[
    {
        "id": "string",
        "name": "string",
        "description": "string",
        "score": float,
        "metadata": {}
    }
]
```

### Recommended Production Implementation
1. Use a distributed vector store (e.g., Milvus, Weaviate)
2. Implement caching for frequent queries
3. Add support for hybrid search (keyword + semantic)
4. Implement result ranking and filtering

## ProductRecommendationTool

### Purpose
Recommends products based on technical requirements and application constraints.

### Implementation
```python
class ProductRecommendationTool(BaseTool):
    name: str = "product_recommendation"
    description: str = "Recommend products based on technical requirements"
    
    def __init__(self, products: Dict):
        self.products = products
        self.parameter_validator = ParameterValidator()
        self.unit_converter = UnitConverter()
```

### Input Format
```json
{
    "application_area": "string",
    "requirements": [
        {
            "parameter": "string",
            "unit": "string",
            "min": float | string,
            "max": float | string
        }
    ],
    "features": ["string"]
}
```

### Output Format
```json
[
    {
        "id": "string",
        "name": "string",
        "description": "string",
        "parameters": {},
        "specs": {},
        "features": ["string"],
        "applications": ["string"]
    }
]
```

### Recommended Production Implementation
1. Use a proper database for product data
2. Implement parameter normalization and validation
3. Add support for complex parameter relationships
4. Implement caching for frequent queries

## SolutionExplorerTool

### Purpose
Explores solution spaces and retrieves relevant reference designs.

### Implementation
```python
class SolutionExplorerTool(BaseTool):
    name: str = "solution_explorer"
    description: str = "Explore solution spaces and find reference designs"
    
    def __init__(self, solutions: Dict):
        self.solutions = solutions
        self.requirement_matcher = RequirementMatcher()
```

### Input Format
```json
{
    "application_domain": "string",
    "requirements": [
        {
            "parameter": "string",
            "unit": "string",
            "min": float | string,
            "max": float | string
        }
    ],
    "format": "all" | "schematic" | "layout" | "code"
}
```

### Output Format
```json
[
    {
        "id": "string",
        "name": "string",
        "description": "string",
        "requirements": {},
        "reference_designs": [
            {
                "id": "string",
                "name": "string",
                "format": "string",
                "url": "string"
            }
        ]
    }
]
```

### Recommended Production Implementation
1. Use a document store for solution data
2. Implement solution versioning
3. Add support for solution dependencies
4. Implement solution validation

## ParameterAnalysisTool

### Purpose
Analyzes and compares technical parameters across products.

### Implementation
```python
class ParameterAnalysisTool(BaseTool):
    name: str = "parameter_analysis"
    description: str = "Analyze and compare technical parameters"
    
    def __init__(self, products: Dict):
        self.products = products
        self.unit_converter = UnitConverter()
        self.parameter_validator = ParameterValidator()
```

### Input Format
```json
{
    "products": ["string"],
    "parameters": ["string"],
    "constraints": [
        {
            "parameter": "string",
            "unit": "string",
            "min": float | string,
            "max": float | string
        }
    ]
}
```

### Output Format
```json
{
    "comparison": {
        "parameter": {
            "unit": "string",
            "values": {
                "product_id": {
                    "min": float,
                    "max": float,
                    "value": float
                }
            }
        }
    },
    "validation": {
        "product_id": {
            "parameter": {
                "status": "valid" | "invalid",
                "message": "string"
            }
        }
    }
}
```

### Recommended Production Implementation
1. Implement parameter relationship validation
2. Add support for complex unit conversions
3. Implement parameter dependency analysis
4. Add support for parameter optimization

## Common Features

### 1. Error Handling
```python
class ToolError(Exception):
    """Base class for tool errors."""
    pass

class ValidationError(ToolError):
    """Raised when input validation fails."""
    pass

class ProcessingError(ToolError):
    """Raised when processing fails."""
    pass

def handle_tool_error(func):
    """Decorator for handling tool errors."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValidationError as e:
            return {"error": "validation", "message": str(e)}
        except ProcessingError as e:
            return {"error": "processing", "message": str(e)}
        except Exception as e:
            return {"error": "unknown", "message": str(e)}
    return wrapper
```

### 2. Logging
```python
import logging
from opentelemetry import trace

class ToolLogger:
    def __init__(self, tool_name: str):
        self.logger = logging.getLogger(tool_name)
        self.tracer = trace.get_tracer(tool_name)
    
    def log_operation(self, operation: str, **kwargs):
        with self.tracer.start_as_current_span(operation) as span:
            for key, value in kwargs.items():
                span.set_attribute(key, str(value))
            self.logger.info(f"Operation: {operation}", extra=kwargs)
```

### 3. Caching
```python
from functools import lru_cache
from redis import Redis

class ToolCache:
    def __init__(self, tool_name: str):
        self.redis = Redis(host='localhost', port=6379, db=0)
        self.tool_name = tool_name
    
    def get_cached_result(self, key: str) -> Optional[Dict]:
        cached = self.redis.get(f"{self.tool_name}:{key}")
        return json.loads(cached) if cached else None
    
    def set_cached_result(self, key: str, result: Dict, ttl: int = 3600):
        self.redis.setex(
            f"{self.tool_name}:{key}",
            ttl,
            json.dumps(result)
        )
```

### 4. Validation
```python
from pydantic import BaseModel, Field

class ToolInput(BaseModel):
    """Base class for tool inputs."""
    class Config:
        arbitrary_types_allowed = True

class ToolOutput(BaseModel):
    """Base class for tool outputs."""
    class Config:
        arbitrary_types_allowed = True

def validate_input(input_data: Dict, input_model: Type[ToolInput]) -> ToolInput:
    """Validate tool input data."""
    try:
        return input_model(**input_data)
    except ValidationError as e:
        raise ValidationError(f"Invalid input: {str(e)}")
``` 