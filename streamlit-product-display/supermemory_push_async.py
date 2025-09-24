import os
import pandas as pd
import asyncio
import aiohttp

# Load dataset and drop rows with NaN values
df = pd.read_csv("final_products_complete.csv").dropna()

API_URL = "https://api.supermemory.ai/v3/documents"
API_KEY = "sm_a3cfySA3Di6JBTkfRGNUZi_gJOZEQukLPdvegiMHZfmkPdKJsuJSDxIWTUVgrBUfNlzdrUAVeMbhkTkYlwtzbny"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

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