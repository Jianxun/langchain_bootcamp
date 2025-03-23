def query_product_vector_store(query: str, k: int = 3) -> str:
    """
    Mock implementation of the vector store query function.
    In a real implementation, this would query a vector database.
    
    Args:
        query: The search query string
        k: Number of results to return (default: 3)
    
    Returns:
        A markdown formatted string containing the search results
    """
    # Mock product database
    products = {
        "AD8422": {
            "name": "Precision Instrumentation Amplifier",
            "description": "Low power, rail-to-rail instrumentation amplifier with high CMRR",
            "features": ["low power", "rail-to-rail", "precision"],
            "applications": ["sensor interface", "medical instrumentation"],
            "datasheet_url": "https://www.analog.com/media/en/technical-documentation/data-sheets/AD8422.pdf"
        },
        "AD7124-8": {
            "name": "Low Power, 24-Bit Sigma-Delta ADC",
            "description": "Low power, 24-bit sigma-delta ADC with integrated PGA",
            "features": ["low power", "24-bit", "integrated PGA"],
            "applications": ["sensor interface", "industrial measurement"],
            "datasheet_url": "https://www.analog.com/media/en/technical-documentation/data-sheets/AD7124-8.pdf"
        }
    }
    
    # Simple keyword matching for demo
    results = []
    query = query.lower()
    
    for product_id, product in products.items():
        if any(term in query for term in ["amplifier", "adc", "sensor"]):
            results.append(product)
    
    # Format results in markdown
    if not results:
        return "No matching products found."
    
    response = "Here are the matching products:\n\n"
    for product in results[:k]:
        response += f"### {product['name']}\n"
        response += f"{product['description']}\n\n"
        response += "**Features:**\n"
        for feature in product['features']:
            response += f"- {feature}\n"
        response += "\n**Applications:**\n"
        for app in product['applications']:
            response += f"- {app}\n"
        response += f"\n[View Datasheet]({product['datasheet_url']})\n\n"
    
    return response 