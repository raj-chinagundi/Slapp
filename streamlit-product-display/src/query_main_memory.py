import requests
import json
from typing import Optional, Dict, Any, List

def query_memories_with_collective(collective_memory: str, limit: int = 10) -> Dict[str, Any]:
    """
    Query supermemory using collective memory as the search query.
    
    Args:
        collective_memory (str): The concatenated memory string from user preferences
        limit (int): Maximum number of results to return (default: 10)
    
    Returns:
        Dict[str, Any]: Response from supermemory API
    """
    url = "https://api.supermemory.ai/v3/search"
    
    payload = {
        "q": collective_memory,  # Use "q" instead of "query"
        "chunkThreshold": 0,
        "documentThreshold": 0,
        "includeFullDocs": False,
        "includeSummary": False,
        "limit": limit,
        "onlyMatchingChunks": True,
        "rerank": False,
        "rewriteQuery": False
    }
    
    headers = {
        "Authorization": f"Bearer {__import__('src.supermemory.client', fromlist=['get_api_key']).get_api_key()}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error querying supermemory: {e}")
        print(f"Response status code: {response.status_code if 'response' in locals() else 'No response'}")
        if 'response' in locals():
            print(f"Response text: {response.text}")
        return {"error": str(e), "status_code": response.status_code if 'response' in locals() else None}

def extract_memory_insights(query_response: Dict[str, Any]) -> List[str]:
    """
    Extract memory insights from the supermemory query response.
    
    Args:
        query_response (Dict[str, Any]): Response from query_memories_with_collective
    
    Returns:
        List[str]: List of memory insights/content
    """
    insights = []
    
    if 'results' in query_response:
        for result in query_response['results']:
            # Check if result has chunks (for search results)
            if 'chunks' in result:
                for chunk in result['chunks']:
                    if 'content' in chunk and chunk['content']:
                        insights.append(chunk['content'])
            # Check if result has direct memory field (for memory results)
            elif 'memory' in result and result['memory']:
                insights.append(result['memory'])
            # Check if result has direct content field
            elif 'content' in result and result['content']:
                insights.append(result['content'])
    
    return insights

def extract_recommended_products(query_response: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extract product recommendations from the supermemory query response.
    
    Args:
        query_response (Dict[str, Any]): Response from query_memories_with_collective
    
    Returns:
        List[Dict[str, Any]]: List of unique product dictionaries with metadata
    """
    products = []
    seen_products = set()  # Track unique products
    
    if 'results' in query_response:
        for result in query_response['results']:
            if 'metadata' in result and result['metadata']:
                metadata = result['metadata']
                
                # Create a unique identifier for the product
                product_identifier = (
                    metadata.get('name', 'Unknown Product'),
                    metadata.get('brand', 'Unknown Brand'),
                    metadata.get('url', '')
                )
                
                # Skip if we've already seen this product
                if product_identifier in seen_products:
                    continue
                
                seen_products.add(product_identifier)
                
                # Create product dictionary in the same format as your existing products
                product = {
                    'name': metadata.get('name', 'Unknown Product'),
                    'url': metadata.get('url', ''),
                    'image': metadata.get('image_url', ''),  # Map image_url to image
                    'brand': metadata.get('brand', 'Unknown Brand'),
                    'description': metadata.get('features', ''),
                    'score': result.get('score', 0),
                    'document_id': result.get('documentId', ''),
                    'source': 'memory_recommendation'
                }
                
                # Add chunk content if available
                if 'chunks' in result and result['chunks']:
                    chunk = result['chunks'][0]  # Take first chunk
                    product['chunk_score'] = chunk.get('score', 0)
                    if not product['description'] and 'content' in chunk:
                        product['description'] = chunk['content']
                
                products.append(product)
    
    return products

def query_and_analyze_memories(collective_memory: str, limit: int = 10) -> Dict[str, Any]:
    """
    Query memories and return both raw response and extracted insights.
    
    Args:
        collective_memory (str): The concatenated memory string from user preferences
        limit (int): Maximum number of results to return
    
    Returns:
        Dict[str, Any]: Dictionary containing raw response and extracted insights
    """
    print(f"Querying supermemory with collective memory:")
    print(f"Query: {collective_memory[:200]}..." if len(collective_memory) > 200 else f"Query: {collective_memory}")
    print("-" * 50)
    
    # Query the API
    raw_response = query_memories_with_collective(collective_memory, limit)
    
    # Extract insights
    insights = extract_memory_insights(raw_response)
    
    # Extract recommended products
    recommended_products = extract_recommended_products(raw_response)
    
    # Create comprehensive result
    result = {
        "collective_memory_query": collective_memory,
        "raw_response": raw_response,
        "extracted_insights": insights,
        "recommended_products": recommended_products,
        "insights_count": len(insights),
        "products_count": len(recommended_products),
        "query_successful": "error" not in raw_response
    }
    
    # Print results
    print(f"Query successful: {result['query_successful']}")
    print(f"Found {result['insights_count']} memory insights")
    print(f"Found {result['products_count']} unique recommended products")
    
    if insights:
        print("\nExtracted Memory Insights:")
        for i, insight in enumerate(insights, 1):  # Show ALL insights
            print(f"{i}. {insight[:100]}...")
    
    if recommended_products:
        print("\nAll Unique Recommended Products:")
        for i, product in enumerate(recommended_products, 1):  # Show ALL unique recommended products
            print(f"{i}. {product['name']} ({product['brand']}) - Score: {product['score']:.3f}")
            if product.get('url'):
                print(f"   URL: {product['url']}")
            if product.get('description'):
                print(f"   Description: {product['description'][:100]}...")
            print()  # Empty line for better readability
    else:
        print("\nNo unique recommended products found.")
    
    return result

# Example usage function
def test_query_with_sample_memory():
    """
    Test function with sample collective memory.
    """
    sample_collective_memory = (
        "The style of the outfit is casual. The clothing item is a jacket. "
        "The clothing item is a pair of green pants. The dress has a casual yet fashionable style "
        "with a modern and trendy vibe. The clothing item is a sleeveless dress. "
        "The dress has an elegant and casual style."
    )
    
    return query_and_analyze_memories(sample_collective_memory)

if __name__ == "__main__":
    # Test the function
    test_result = test_query_with_sample_memory()
    print(f"\nTest completed. Found {test_result['insights_count']} insights.")