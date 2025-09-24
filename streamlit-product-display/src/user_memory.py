import os
import requests
import streamlit as st
from typing import Dict, Any, Optional
import uuid

# Configuration is sourced via Streamlit secrets; no dotenv loading here

from src.supermemory.client import build_headers, SUPERMEMORY_API_URL

API_URL = f"{SUPERMEMORY_API_URL}/documents"

def get_session_id() -> str:
    """
    Get or create a session ID for this Streamlit session.
    
    Returns:
        str: Unique session identifier
    """
    if 'session_id' not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())[:8]  # Short session ID
    return st.session_state.session_id

def push_to_supermemory(product: Dict[str, Any], preference_type: str = "liked") -> bool:
    """
    Push a liked product's metadata to Supermemory API.
    
    Args:
        product: Dictionary containing product information
        preference_type: Type of preference ("liked" or "super_liked")
    
    Returns:
        bool: True if successful, False otherwise
    """
    headers = build_headers()
    
    # Create the payload with product metadata
    # Handle both 'image' and 'image_url' field names
    image_url = product.get("image") or product.get("image_url", "")
    
    # Get session ID for container tag
    session_id = get_session_id()
    
    payload = {
        "content": f"Product Description: {product.get('clothing_features', 'No description available')}",
        "containerTag": f"{session_id}_user",
        "metadata": {
            "name": product.get("name", "Unknown Product"),
            "url": product.get("product_url", ""),
            "image_url": image_url,
            "brand": product.get("source", "Unknown Brand"),
            "features": product.get("clothing_features", ""),
            "preference_type": preference_type,
            "user_action": f"user_{preference_type}_this_product"
        }
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=10)
        
        if response.status_code == 200:
            return True
        else:
            st.error(f"Failed to save to memory: {response.status_code} - {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        st.error(f"Network error saving to memory: {str(e)}")
        return False
    except Exception as e:
        st.error(f"Unexpected error saving to memory: {str(e)}")
        return False

def save_liked_product(product: Dict[str, Any]) -> bool:
    """
    Save a liked product to user's memory.
    
    Args:
        product: Dictionary containing product information
        
    Returns:
        bool: True if successful, False otherwise
    """
    return push_to_supermemory(product, "liked")

def save_disliked_product(product: Dict[str, Any]) -> bool:
    """
    Save a disliked product to user's memory.
    
    Args:
        product: Dictionary containing product information
        
    Returns:
        bool: True if successful, False otherwise
    """
    return push_to_supermemory(product, "disliked")

def save_super_liked_product(product: Dict[str, Any]) -> bool:
    """
    Save a super-liked product to user's memory.
    
    Args:
        product: Dictionary containing product information
        
    Returns:
        bool: True if successful, False otherwise
    """
    return push_to_supermemory(product, "super_liked")

def batch_save_preferences(liked_products: list, super_liked_products: list, disliked_products: list = None) -> Dict[str, int]:
    """
    Save multiple products in batch (useful for end-of-session saving).
    
    Args:
        liked_products: List of liked product dictionaries
        super_liked_products: List of super-liked product dictionaries
        disliked_products: List of disliked product dictionaries
        
    Returns:
        dict: Summary of save results
    """
    if disliked_products is None:
        disliked_products = []
        
    results = {
        "liked_saved": 0,
        "liked_failed": 0,
        "super_liked_saved": 0,
        "super_liked_failed": 0,
        "disliked_saved": 0,
        "disliked_failed": 0
    }
    
    # Save liked products
    for product in liked_products:
        if save_liked_product(product):
            results["liked_saved"] += 1
        else:
            results["liked_failed"] += 1

    
    # Save super-liked products
    for product in super_liked_products:
        if save_super_liked_product(product):
            results["super_liked_saved"] += 1
        else:
            results["super_liked_failed"] += 1

    # Save disliked products
    for product in disliked_products:
        if save_disliked_product(product):
            results["disliked_saved"] += 1
        else:
            results["disliked_failed"] += 1

    
    return results

def show_save_status(product_name: str, success: bool, preference_type: str = "liked"):
    """
    Display save status to user.
    
    Args:
        product_name: Name of the product
        success: Whether the save was successful
        preference_type: Type of preference ("liked", "super_liked", or "disliked")
    """
    if success:
        if preference_type == "super_liked":
            st.success(f"⭐ Saved '{product_name}' to your super-liked memory!")
        elif preference_type == "disliked":
            st.success(f"👎 Saved '{product_name}' to your disliked memory!")
        else:
            st.success(f"❤️ Saved '{product_name}' to your liked memory!")
    else:
        st.warning(f"⚠️ Couldn't save '{product_name}' to memory - but it's still in your session!")
