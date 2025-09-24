import os
import pandas as pd
import requests
from typing import List, Dict

# Load dataset and drop rows with NaN values
df = pd.read_csv("final_products_complete.csv").dropna()

API_URL = "https://api.supermemory.ai/v3/documents/batch"
API_KEY = "sm_a3cfySA3Di6JBTkfRGNUZi_gJOZEQukLPdvegiMHZfmkPdKJsuJSDxIWTUVgrBUfNlzdrUAVeMbhkTkYlwtzbny"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def create_batch_payload(rows: List[pd.Series]) -> Dict:
    """Create batch payload from DataFrame rows"""
    documents = []
    
    for _, row in rows:
        document = {
            "containerTag": "closet",
            "content": f"Product Description: {row['clothing_features']}",
            "metadata": {
                "name": row["name"],
                "url": row["product_url"],
                "image_url": row["image_url"],
                "brand": row["source"],
                "features": row["clothing_features"]
            }
        }
        documents.append(document)
    
    return {"documents": documents}

def upload_batch(batch_rows: List[pd.Series]) -> None:
    """Upload a batch of products to SuperMemory"""
    payload = create_batch_payload(batch_rows)
    
    try:
        response = requests.post(API_URL, json=payload, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Batch uploaded successfully: {len(batch_rows)} products")
            # Print individual results if available
            if 'results' in result:
                for i, item_result in enumerate(result['results']):
                    product_name = batch_rows[i][1]['name']
                    print(f"   - {product_name}: {item_result.get('status', 'unknown')}")
        else:
            print(f"❌ Batch upload failed: {response.status_code} | {response.text}")
            
    except Exception as e:
        print(f"❌ Batch upload error: {str(e)}")

def main():
    # Process in batches of 50 (adjust batch size as needed)
    batch_size = 100
    total_rows = len(df)
    
    print(f"Processing {total_rows} products in batches of {batch_size}...")
    
    for i in range(0, total_rows, batch_size):
        batch_end = min(i + batch_size, total_rows)
        batch_rows = list(df.iloc[i:batch_end].iterrows())
        
        print(f"\nUploading batch {i//batch_size + 1} (rows {i+1}-{batch_end})...")
        upload_batch(batch_rows)

if __name__ == "__main__":
    main()