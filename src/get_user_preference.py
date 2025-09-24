import requests
import streamlit as st

def get_user_preferences(session_id: str) -> dict:
    """
    Query user preferences from Supermemory and return the response.
    
    Args:
        session_id: Session ID to search for
        
    Returns:
        dict: Raw response from Supermemory API
    """
    url = "https://api.supermemory.ai/v4/search"

    payload = {"threshold":0.2,"include":{"documents":False,"summaries":False,"relatedMemories":False,"forgottenMemories":False},"limit":10,"rerank":False,"rewriteQuery":False,"q":"What are the user's clothing and fashion preferences based on their liked, disliked, and super-liked products?","containerTag":f"{session_id}_user"}

    headers = {
        "Authorization": f"Bearer {__import__('src.supermemory.client', fromlist=['get_api_key']).get_api_key()}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(url, json=payload, headers=headers)
    
    return response.json()