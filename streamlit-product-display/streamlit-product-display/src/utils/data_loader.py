import pandas as pd
import random
import streamlit as st

@st.cache_data
def load_products():
    """Load products from CSV file"""
    try:
        df = pd.read_csv('/Users/raj/Desktop/devhacks/final_products_complete.csv')
        # Rename image_url to image for consistency
        df = df.rename(columns={'image_url': 'image'})
        return df.to_dict('records')
    except Exception as e:
        st.error(f"Error loading products: {e}")
        return []

def get_random_products(num_products=10):
    """Get random products from the dataset"""
    products = load_products()
    if len(products) > num_products:
        return random.sample(products, num_products)
    return products