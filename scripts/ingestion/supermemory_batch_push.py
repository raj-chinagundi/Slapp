import os
import sys
import pandas as pd
import requests
from typing import List, Dict
from pathlib import Path

# Ensure project src/ is importable when running from scripts/
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SRC_PATH = os.path.join(PROJECT_ROOT, "src")
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

from src.supermemory.client import SUPERMEMORY_API_URL, build_headers

# Optional: Load .env for scripts when present
try:
    from dotenv import load_dotenv
    env_path = Path(PROJECT_ROOT) / ".env"
    if env_path.exists():
        load_dotenv(env_path, override=True)
except Exception:
    pass

# Load dataset and drop rows with NaN values (path relative to project root)
CSV_PATH = os.path.join(PROJECT_ROOT, "final_products_complete.csv")
df = pd.read_csv(CSV_PATH).dropna()

API_URL = f"{SUPERMEMORY_API_URL}/documents/batch"
headers = build_headers()

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