import streamlit as st

def display_product_card(product):
    """Display a product card with image and name"""
    
    # Custom CSS for very compact card that fits in viewport at 100% zoom
    st.markdown("""
    <style>
    .stContainer > div {
        max-width: 250px !important;
        margin: 0 auto !important;
    }
    .product-image {
        border-radius: 8px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.15);
        max-width: 150px;
        margin: 0 auto;
        display: block;
    }
    /* Aggressively reduce spacing around elements */
    .stImage {
        margin-bottom: 0.25rem !important;
        margin-top: 0.25rem !important;
    }
    .element-container {
        margin-bottom: 0.1rem !important;
        margin-top: 0.1rem !important;
    }
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 0.5rem !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Product card container with much tighter centering
    with st.container():
        # Much more aggressive centering with wider outer columns
        col1, col2, col3 = st.columns([4, 1, 4])
        
        with col2:
            # Product image
            image_url = product.get('image')
            product_name = product.get('name', 'Unknown Product')
            
            # Debug: Show the image URL
            # st.caption(f"Image URL: {image_url}")
            
            if image_url:
                try:
                    # Very small image for ultra-compact view
                    st.image(image_url, width=150)
                except Exception as e:
                    st.error(f"Failed to load image: {str(e)}")
                    st.markdown(f"**{product_name}**")
            else:
                st.info("📷 No image URL found")
                st.markdown(f"**{product_name}**")
            
            # Very compact centered product name
            st.markdown(f"<h6 style='text-align: center; margin-top: 4px; margin-bottom: 4px; font-size: 14px;'>{product_name}</h6>", unsafe_allow_html=True)

def display_swipe_buttons():
    """Display the swipe action buttons"""
    # Make buttons very compact
    st.markdown("""
    <style>
    .stButton button {
        height: 35px !important;
        padding: 0.2rem 0.4rem !important;
        font-size: 0.85rem !important;
        margin: 0 !important;
    }
    .stButton {
        margin-bottom: 0.25rem !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4, col5 = st.columns([1.5, 1, 1, 1, 1.5])
    
    with col2:
        pass_clicked = st.button("👎 Pass", use_container_width=True, help="Not interested")
    
    with col3:
        super_like_clicked = st.button("⭐ Super Like", use_container_width=True, help="Love it!", type="primary")
    
    with col4:
        like_clicked = st.button("❤️ Like", use_container_width=True, help="Interested")
    
    return pass_clicked, super_like_clicked, like_clicked