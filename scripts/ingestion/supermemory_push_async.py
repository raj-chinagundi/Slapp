import os
import sys
import pandas as pd
import asyncio
import aiohttp
from pathlib import Path

# Ensure project src/ is importable when running from scripts/
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SRC_PATH = os.path.join(PROJECT_ROOT, "src")
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

from src.supermemory.client import build_headers, SUPERMEMORY_API_URL

# Optional: Load .env for scripts when present
try:
    from dotenv import load_dotenv
    env_path = Path(PROJECT_ROOT) / ".env"
    if env_path.exists():
        load_dotenv(env_path, override=True)
except Exception:
    pass

# Load dataset and drop rows with NaN values
CSV_PATH = os.path.join(PROJECT_ROOT, "final_products_complete.csv")
df = pd.read_csv(CSV_PATH).dropna()

API_URL = f"{SUPERMEMORY_API_URL}/documents"
headers = build_headers()

async def upload_product(session, row):
    payload = {
        "content": f"Product Description: {row['clothing_features']}",
        "containerTag": "closet",
        "metadata": {
            "name": row["name"],
            "url": row["product_url"],
            "image_url": row["image_url"],
            "brand": row["source"],
            "features": row["clothing_features"]
        }
    }
    
    try:
        async with session.post(API_URL, headers=headers, json=payload) as response:
            if response.status == 200:
                result = await response.json()
                print(f"✅ Stored: {row['name']} (ID: {result['id']})")
            else:
                text = await response.text()
                print(f"❌ Failed: {row['name']} | {response.status} | {text}")
    except Exception as e:
        print(f"❌ Error: {row['name']} | {str(e)}")

async def main():
    async with aiohttp.ClientSession() as session:
        tasks = [upload_product(session, row) for _, row in df.iterrows()]
        await asyncio.gather(*tasks)

# Run the async function
asyncio.run(main())