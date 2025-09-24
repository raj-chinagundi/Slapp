import os
import pandas as pd
import requests

# Load dataset and drop rows with NaN values
df = pd.read_csv("final_products.csv").dropna()

API_URL = "https://api.supermemory.ai/v3/documents"
API_KEY = "sm_a3cfySA3Di6JBTkfRGNUZi_gJOZEQukLPdvegiMHZfmkPdKJsuJSDxIWTUVgrBUfNlzdrUAVeMbhkTkYlwtzbny"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

for _, row in df.iterrows():
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

    response = requests.post(API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        print(f"✅ Stored: {row['name']} (ID: {response.json()['id']})")
    else:
        print(f"❌ Failed: {row['name']} | {response.status_code} | {response.text}")