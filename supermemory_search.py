import requests

# SuperMemory API configuration
SEARCH_URL = "https://api.supermemory.ai/v3/search"
API_KEY = "sm_a3cfySA3Di6JBTkfRGNUZi_gJOZEQukLPdvegiMHZfmkPdKJsuJSDxIWTUVgrBUfNlzdrUAVeMbhkTkYlwtzbny"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def search_products(query, limit=5):
    """Search for top 5 products using the same payload structure"""
    payload = {
        "q": query,
        "limit": limit,
        "documentThreshold": 0.3
    }
    
    response = requests.post(SEARCH_URL, json=payload, headers=headers)
    
    if response.status_code == 200:
        results = response.json()
        print(results)
        for i, a in enumerate(results.get('results', []), 1):
            print(f"{i}. {a}\n","*"* 50, "\n\n")

    #     print(f"🔍 Found {len(results.get('documents', []))} products for: '{query}'\n")
        
    #     for i, doc in enumerate(results.get('documents', []), 1):
    #         metadata = doc.get('metadata', {})
    #         print(f"{i}. {metadata.get('name', 'Unknown Product')}")
    #         print(f"   Brand: {metadata.get('brand', 'N/A')}")
    #         print(f"   Features: {metadata.get('features', 'N/A')}")
    #         print(f"   URL: {metadata.get('url', 'N/A')}")
    #         print(f"   Score: {doc.get('score', 'N/A')}")
    #         print("-" * 50)
    # else:
    #     print(f"❌ Search failed: {response.status_code} | {response.text}")

# Example usage - just like your upload, but for search
if __name__ == "__main__":
    # Your search query - same simple structure as the example you showed
    search_query = """
    Find me the top 5 products similar to this description:
   ```Product Name: Airlift Intrigue Bra - Espresso
    Product Description:
    The clothing item in the image is a one-piece swimsuit. It is a dark brown or black color, with a solid pattern. The material appears to be a smooth, possibly silky or satin-like fabric. The swimsuit has thin straps and a low-cut neckline, which are typical features of a swimsuit. The style is sleeveless and has a fitted silhouette. There are no visible design elements such as ruffles or embellishments.```
    """
    search_products(search_query)