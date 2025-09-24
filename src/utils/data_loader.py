import pandas as pd
import random
import streamlit as st
import os

@st.cache_data
def load_products():
    """Load products from CSV file"""
    try:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        app_csv_path = os.path.join(base_dir, 'data', 'final_products_complete.csv')
        project_root = os.path.abspath(os.path.join(base_dir, '..'))
        root_csv_path = os.path.join(project_root, 'final_products_complete.csv')

        csv_path = app_csv_path if os.path.exists(app_csv_path) else root_csv_path
        df = pd.read_csv(csv_path)
        # Normalize image column to 'image'
        if 'image' not in df.columns and 'image_url' in df.columns:
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