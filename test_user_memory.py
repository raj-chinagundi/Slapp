#!/usr/bin/env python3
"""
Test script for user_memory.py functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from user_memory import save_liked_product, save_super_liked_product

def test_user_memory():
    """Test the user memory functionality with sample data"""
    
    # Sample product data (mimicking the CSV structure)
    test_product = {
        'name': 'Test Airlift Intrigue Bra - Espresso',
        'product_url': 'https://www.aloyoga.com/products/test-product',
        'image': 'https://cdn.shopify.com/s/files/1/test-image.jpg',
        'source': 'alo_yoga',
        'clothing_features': 'The clothing item is a stylish sports bra with premium fabric and excellent support.'
    }
    
    print("Testing User Memory Integration...")
    print("=" * 50)
    
    # Test liked product
    print(f"Testing 'liked' product: {test_product['name']}")
    liked_result = save_liked_product(test_product)
    print(f"Liked product save result: {'✅ Success' if liked_result else '❌ Failed'}")
    
    print()
    
    # Test super-liked product
    print(f"Testing 'super-liked' product: {test_product['name']}")
    super_liked_result = save_super_liked_product(test_product)
    print(f"Super-liked product save result: {'✅ Success' if super_liked_result else '❌ Failed'}")
    
    print()
    print("=" * 50)
    
    if liked_result and super_liked_result:
        print("🎉 All tests passed! User memory integration is working.")
    else:
        print("⚠️ Some tests failed. Check your API configuration.")

if __name__ == "__main__":
    test_user_memory()