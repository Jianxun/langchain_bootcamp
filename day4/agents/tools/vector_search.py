"""
Vector Search Tool for ADI products, categories, and solutions.
"""

from typing import Dict, List, Optional, Any, Type
import numpy as np
from langchain.tools import BaseTool
from langchain_core.embeddings import Embeddings
from langchain.callbacks.manager import CallbackManagerForToolRun
from pydantic import Field, BaseModel
import json

class VectorSearchInput(BaseModel):
    query: str
    search_type: str
    top_k: int
    min_score: float

class VectorSearchTool(BaseTool):
    """Tool for semantic search across ADI products, categories, and solutions."""
    
    name: str = "vector_search"
    description: str = """Use this tool to search across ADI products, categories, and solutions.
    Input should be a JSON string with the following structure:
    {
        "query": "string",
        "search_type": "products|categories|solutions",
        "top_k": int,
        "min_score": float
    }
    """
    args_schema: Type[BaseModel] = VectorSearchInput
    
    @property
    def is_single_input(self) -> bool:
        """Whether the tool only accepts a single input."""
        return True
    
    embeddings: Any = Field(
        description="Embeddings model to use for vector search"
    )
    products: Dict[str, Dict] = Field(
        default_factory=dict,
        description="Dictionary of product data"
    )
    categories: Dict[str, Dict] = Field(
        default_factory=dict,
        description="Dictionary of category data"
    )
    solutions: Dict[str, Dict] = Field(
        default_factory=dict,
        description="Dictionary of solution data"
    )
    
    # Internal state
    product_ids: List[str] = Field(default_factory=list, exclude=True)
    product_texts: List[str] = Field(default_factory=list, exclude=True)
    product_embeddings: List[List[float]] = Field(default_factory=list, exclude=True)
    
    category_ids: List[str] = Field(default_factory=list, exclude=True)
    category_texts: List[str] = Field(default_factory=list, exclude=True)
    category_embeddings: List[List[float]] = Field(default_factory=list, exclude=True)
    
    solution_ids: List[str] = Field(default_factory=list, exclude=True)
    solution_texts: List[str] = Field(default_factory=list, exclude=True)
    solution_embeddings: List[List[float]] = Field(default_factory=list, exclude=True)
    
    def __init__(self, **data):
        super().__init__(**data)
        self._initialize_vector_stores()
    
    def _initialize_vector_stores(self):
        """Initialize vector stores with embeddings."""
        # Initialize products
        for product_id, product in self.products.items():
            self.product_ids.append(product_id)
            text = f"{product['name']}\n{product.get('description', '')}"
            self.product_texts.append(text)
            self.product_embeddings.append(self.embeddings.embed_query(text))
        
        # Initialize categories
        for category_id, category in self.categories.items():
            self.category_ids.append(category_id)
            text = f"{category['name']}\n{category.get('description', '')}"
            self.category_texts.append(text)
            self.category_embeddings.append(self.embeddings.embed_query(text))
        
        # Initialize solutions
        for solution_id, solution in self.solutions.items():
            self.solution_ids.append(solution_id)
            text = f"{solution['name']}\n{solution.get('description', '')}"
            self.solution_texts.append(text)
            self.solution_embeddings.append(self.embeddings.embed_query(text))
    
    def _compute_similarities(self, query_embedding: List[float], embeddings: List[List[float]]) -> List[float]:
        """Compute cosine similarities between query and stored embeddings."""
        query_norm = np.linalg.norm(query_embedding)
        similarities = []
        for emb in embeddings:
            emb_norm = np.linalg.norm(emb)
            similarity = np.dot(query_embedding, emb) / (query_norm * emb_norm)
            similarities.append(float(similarity))
        return similarities
    
    def run(self, query: Dict) -> List[Dict]:
        """
        Run the vector search tool.
        
        Args:
            query: Dict containing:
                - query: str, the search query
                - search_type: "products" | "categories" | "solutions"
                - top_k: Optional[int], number of results to return
                - min_score: Optional[float], minimum similarity score
        
        Returns:
            List[Dict]: List of matching items with their details
        """
        search_query = query["query"]
        search_type = query["search_type"]
        top_k = query.get("top_k", 5)
        min_score = query.get("min_score", 0.0)
        
        if search_type not in ["products", "categories", "solutions"]:
            raise ValueError(f"Invalid search type: {search_type}")
        
        # Get the appropriate store based on search type
        if search_type == "products":
            ids = self.product_ids
            texts = self.product_texts
            embeddings = self.product_embeddings
            items = self.products
        elif search_type == "categories":
            ids = self.category_ids
            texts = self.category_texts
            embeddings = self.category_embeddings
            items = self.categories
        else:  # solutions
            ids = self.solution_ids
            texts = self.solution_texts
            embeddings = self.solution_embeddings
            items = self.solutions
        
        # Compute query embedding and similarities
        query_embedding = self.embeddings.embed_query(search_query)
        similarities = self._compute_similarities(query_embedding, embeddings)
        
        # Sort and filter results
        results = []
        for idx, score in enumerate(similarities):
            if score >= min_score:
                results.append({
                    "id": ids[idx],
                    "score": score,
                    "text": texts[idx],
                    **items[ids[idx]]
                })
        
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]
    
    def _run(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Execute the tool."""
        try:
            # Parse input as JSON
            input_data = json.loads(query)
            
            # Validate input
            if not isinstance(input_data, dict):
                raise ValueError("Input must be a JSON object")
            if "query" not in input_data:
                raise ValueError("Missing required field 'query'")
            if "search_type" not in input_data:
                raise ValueError("Missing required field 'search_type'")
            
            # Get search parameters
            search_query = input_data["query"]
            search_type = input_data["search_type"]
            top_k = input_data.get("top_k", 5)
            min_score = input_data.get("min_score", 0.0)
            
            # Validate search type
            if search_type not in ["products", "categories", "solutions"]:
                raise ValueError("Invalid search_type. Must be one of: products, categories, solutions")
            
            # Get the appropriate data store
            data_store = {
                "products": self.products,
                "categories": self.categories,
                "solutions": self.solutions
            }[search_type]
            
            if not data_store:
                return json.dumps({"results": [], "message": f"No {search_type} data available"})
            
            # Get embeddings for the query
            query_embedding = self.embeddings.embed_query(search_query)
            
            # Calculate scores for each item
            scores = []
            for id_, item in data_store.items():
                if "embedding" not in item:
                    continue
                score = float(np.dot(query_embedding, item["embedding"]))
                if score >= min_score:
                    scores.append((id_, item, score))
            
            # Sort by score and get top results
            scores.sort(key=lambda x: x[2], reverse=True)
            top_results = scores[:top_k]
            
            # Format results
            results = []
            for id_, item, score in top_results:
                result = {
                    "id": id_,
                    "name": item.get("name", ""),
                    "description": item.get("description", ""),
                    "score": score
                }
                results.append(result)
            
            return json.dumps({"results": results})
            
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON format")
        except Exception as e:
            raise ValueError(f"Error performing search: {str(e)}")
    
    async def _arun(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Async version of the tool."""
        raise NotImplementedError("VectorSearchTool does not support async") 