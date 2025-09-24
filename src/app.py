import streamlit as st
import os
import sys
import streamlit as st

# Ensure project root (which contains `src/`) is importable
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Environment configuration is read from Streamlit secrets; no dotenv loading
import pandas as pd
import requests
from io import BytesIO
from PIL import Image
import uuid
import time
from user_memory import save_liked_product, save_super_liked_product, save_disliked_product
from get_user_preference import get_user_preferences
from query_main_memory import query_and_analyze_memories
from utils.data_loader import get_random_products

# Page config
# add lightning bolt icon
st.set_page_config(page_title="Slapp-AI ⚡", layout="centered")

# Ensure the API key from Streamlit secrets is available to shared client via env
try:
    api_key = st.secrets.get("SUPERMEMORY_API_KEY")
    if api_key and not os.getenv("SUPERMEMORY_API_KEY"):
        os.environ["SUPERMEMORY_API_KEY"] = str(api_key)
except Exception:
    pass


def initialize_session_state():
    """Initialize session state variables"""
    if 'current_index' not in st.session_state:
        st.session_state.current_index = 0
    
    if 'total_swipes' not in st.session_state:
        st.session_state.total_swipes = 0
    
    if 'session_id' not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())[:8]
    
    if 'ai_mode' not in st.session_state:
        st.session_state.ai_mode = False
    
    if 'ai_recommendations' not in st.session_state:
        st.session_state.ai_recommendations = []
    
    if 'ai_index' not in st.session_state:
        st.session_state.ai_index = 0
    
    if 'background_building' not in st.session_state:
        st.session_state.background_building = False
    
    if 'recommendations_ready' not in st.session_state:
        st.session_state.recommendations_ready = False
    
    if 'pending_builds' not in st.session_state:
        st.session_state.pending_builds = set()  # Track which swipe numbers need AI building
    
    if 'last_saved_swipe' not in st.session_state:
        st.session_state.last_saved_swipe = 0  # Prevent duplicate saves
    
    if 'random_fallback_mode' not in st.session_state:
        st.session_state.random_fallback_mode = False
    
    if 'random_products' not in st.session_state:
        st.session_state.random_products = []
    
    if 'random_index' not in st.session_state:
        st.session_state.random_index = 0
    
    # Load CSV data once
    if 'products_df' not in st.session_state:
        csv_path = os.path.join(PROJECT_ROOT, 'final_products_complete.csv')
        st.session_state.products_df = pd.read_csv(csv_path).dropna()
        # Shuffle the dataframe to show random products each session
        st.session_state.products_df = st.session_state.products_df.sample(frac=1).reset_index(drop=True)
        print(f"📊 Loaded and shuffled {len(st.session_state.products_df)} products from CSV")

def save_swipe_immediately(action, product):
    """Save each swipe immediately to Supermemory"""
    try:
        session_id = st.session_state.session_id
        
        if action == 'like':
            save_liked_product(product)
            print(f"✅ Immediately saved LIKE: {product.get('name', 'Unknown')}")
        elif action == 'super_like':
            save_super_liked_product(product)
            print(f"⭐ Immediately saved SUPER LIKE: {product.get('name', 'Unknown')}")
        elif action == 'dislike':
            save_disliked_product(product)
            print(f"👎 Immediately saved DISLIKE: {product.get('name', 'Unknown')}")
            
    except Exception as e:
        print(f"❌ Failed to save {action}: {e}")

def get_ai_recommendations():
    """Query collective memory and get AI recommendations"""
    try:
        session_id = st.session_state.session_id
        print(f"🔍 Querying memory for session: {session_id}")
        
        # Get user's saved preferences from memory
        preferences_response = get_user_preferences(session_id)
        
        if isinstance(preferences_response, dict) and 'results' in preferences_response:
            print(f"📋 Found {len(preferences_response['results'])} memory items")
            
            # Extract all memory content
            memory_values = []
            for result in preferences_response['results']:
                if 'memory' in result and result['memory']:
                    memory_values.append(result['memory'])
            
            collective_memory = ' '.join(memory_values)
            print(f"🧠 Collective memory: {len(collective_memory)} chars")
            
            if collective_memory.strip():
                # Query AI for recommendations based on memory
                print(f"🤖 Querying AI for recommendations...")
                memory_query_result = query_and_analyze_memories(collective_memory, limit=20)
                recommendations = memory_query_result.get('recommended_products', [])
                
                print(f"✅ Got {len(recommendations)} AI recommendations")
                return recommendations
            else:
                print(f"⚠️ Empty collective memory")
                return []
        else:
            print(f"❌ No memory found")
            return []
            
    except Exception as e:
        print(f"💥 Failed to get AI recommendations: {e}")
        return []

def build_ai_recommendations_sync():
    """Synchronously build AI recommendations and add to pool"""
    try:
        print(f"🚀 Building AI recommendations synchronously...")
        new_recommendations = get_ai_recommendations()
        
        if new_recommendations:
            # Add to existing recommendations (don't replace)
            st.session_state.ai_recommendations.extend(new_recommendations)
            
            # Remove duplicates based on product name
            seen_names = set()
            unique_recs = []
            for rec in st.session_state.ai_recommendations:
                name = rec.get('name', 'Unknown')
                if name not in seen_names:
                    seen_names.add(name)
                    unique_recs.append(rec)
            
            st.session_state.ai_recommendations = unique_recs
            st.session_state.recommendations_ready = True
            
            print(f"🎯 Added recommendations. Total unique: {len(st.session_state.ai_recommendations)}")
            return True
        else:
            print(f"⚠️ No new recommendations found")
            return False
            
    except Exception as e:
        print(f"💥 AI building failed: {e}")
        return False

def get_current_product():
    """Get the current product to display"""
    if st.session_state.random_fallback_mode:
        # Random fallback mode - show random products
        if st.session_state.random_index < len(st.session_state.random_products):
            return st.session_state.random_products[st.session_state.random_index]
        else:
            # Load more random products if we've run out
            print(f"🎲 Loading more random products (current: {len(st.session_state.random_products)})")
            st.session_state.random_products.extend(get_random_products(10))
            print(f"🎲 Now have {len(st.session_state.random_products)} random products")
            if st.session_state.random_index < len(st.session_state.random_products):
                return st.session_state.random_products[st.session_state.random_index]
            else:
                return None
    elif st.session_state.ai_mode:
        # AI mode - show AI recommendations
        if st.session_state.ai_index < len(st.session_state.ai_recommendations):
            return st.session_state.ai_recommendations[st.session_state.ai_index]
        else:
            # AI recommendations exhausted - switch to random fallback
            print(f"🎲 AI recommendations exhausted ({st.session_state.ai_index}/{len(st.session_state.ai_recommendations)}), switching to random fallback...")
            st.session_state.random_fallback_mode = True
            st.session_state.random_products = get_random_products(20)
            st.session_state.random_index = 0
            print(f"🎲 Loaded {len(st.session_state.random_products)} random products for fallback")
            return get_current_product()  # Recursive call to get random product
    else:
        # CSV mode - show products from dataset
        if st.session_state.current_index < len(st.session_state.products_df):
            return st.session_state.products_df.iloc[st.session_state.current_index].to_dict()
        else:
            return None

def next_product():
    """Move to next product"""
    st.session_state.total_swipes += 1
    print(f"👆 Swipe #{st.session_state.total_swipes}")
    
    # Start building AI recommendations in background from swipe 30 onwards (every 5 swipes)
    if (st.session_state.total_swipes >= 10 and 
        st.session_state.total_swipes < 20 and 
        (st.session_state.total_swipes - 10) % 5 == 0 and
        not st.session_state.ai_mode):
        
        print(f"🔄 Background: Building AI recommendations at swipe {st.session_state.total_swipes}...")
        # Mark for processing instead of calling undefined function
        st.session_state.pending_builds.add(st.session_state.total_swipes)
    
    # Process pending builds when we have a moment (not at mode switch)
    if (st.session_state.pending_builds and 
        not st.session_state.background_building and 
        st.session_state.total_swipes < 20):
        
        # Process one pending build
        build_swipe = st.session_state.pending_builds.pop()
        st.session_state.background_building = True
        print(f"🔄 Processing AI build for swipe {build_swipe}...")
        
        if build_ai_recommendations_sync():
            print(f"✅ Completed AI build for swipe {build_swipe}")
        
        st.session_state.background_building = False
    
    # Instant switch to AI mode at 20 swipes (recommendations should be ready)
    if st.session_state.total_swipes == 20 and not st.session_state.ai_mode:
        print(f"� Switching to AI mode at 20 swipes...")
        
        if st.session_state.recommendations_ready and len(st.session_state.ai_recommendations) > 0:
            # Instant switch - recommendations are already built!
            st.session_state.ai_mode = True
            st.session_state.ai_index = 0
            print(f"✅ Instant switch! Using {len(st.session_state.ai_recommendations)} pre-built recommendations")
        else:
            # Fallback: build recommendations synchronously if background didn't work
            print(f"⚠️ Background recommendations not ready, building now...")
            with st.spinner("🤖 Getting AI recommendations..."):
                if build_ai_recommendations_sync():
                    st.session_state.ai_mode = True
                    st.session_state.ai_index = 0
                    print(f"✅ Fallback: Built {len(st.session_state.ai_recommendations)} recommendations")
                else:
                    print(f"❌ No AI recommendations available, continuing with CSV")

    # Continue building more AI recommendations (every 10 swipes after 20)
    elif (st.session_state.total_swipes > 20 and
          st.session_state.ai_mode and
          (st.session_state.total_swipes - 20) % 10 == 0):

        print(f"🔄 Background: Adding more AI recommendations at swipe {st.session_state.total_swipes}...")
        with st.spinner("🤖 Getting more recommendations..."):
            build_ai_recommendations_sync()
    
    # Move to next product
    if st.session_state.random_fallback_mode:
        st.session_state.random_index += 1
    elif st.session_state.ai_mode:
        st.session_state.ai_index += 1
    else:
        st.session_state.current_index += 1
    
    st.rerun()

def handle_swipe(action):
    """Handle user swipe action"""
    current_product = get_current_product()
    if current_product:
        # Prevent duplicate saves for the same swipe
        if st.session_state.total_swipes != st.session_state.last_saved_swipe:
            # Save immediately to Supermemory
            save_swipe_immediately(action, current_product)
            st.session_state.last_saved_swipe = st.session_state.total_swipes
        
        # Move to next product
        next_product()

# Initialize session state
initialize_session_state()

# Main UI
# center this 
st.markdown("<h2 style='text-align: center;'>Slapp-AI ⚡</h2>", unsafe_allow_html=True)


# Show mode indicator
if st.session_state.ai_mode:
    st.success(f"🤖 **AI Recommendations Mode** - Swipe #{st.session_state.total_swipes}")
    st.caption(f"Showing personalized recommendations based on your preferences")
else:
    st.info(f"📊 **Discover Mode** - Swipe #{st.session_state.total_swipes}/20")
    if st.session_state.total_swipes >= 30:
        if st.session_state.background_building:
            st.caption(f"🔄 Building AI recommendations in background... Switch at swipe 20!")
        elif st.session_state.recommendations_ready:
            st.caption(f"✅ AI recommendations ready! Switch at swipe 20!")
        else:
            st.caption(f"⚠️ AI recommendations not ready, keep swiping!")
    else:
        st.caption(f"Keep swiping to build your preferences. AI recommendations start at swipe 20!")

# Get current product
current_product = get_current_product()

if current_product:
    # Product display
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col2:
        # Product image - unify to 'image' with fallback to 'image_url'
        image_url = current_product.get('image', '') or current_product.get('image_url', '')
        
        if image_url:
            # Always fetch bytes with headers to avoid hotlinking issues; fallback to direct URL only if needed
            try:
                referer = None
                # Prefer product_url if present, otherwise derive referer from image_url domain
                product_url = current_product.get('product_url', '') or current_product.get('url', '')
                if product_url:
                    referer = product_url
                else:
                    try:
                        from urllib.parse import urlparse
                        parsed = urlparse(image_url)
                        referer = f"{parsed.scheme}://{parsed.netloc}/"
                    except Exception:
                        referer = None

                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
                }
                if referer:
                    headers["Referer"] = referer

                resp = requests.get(image_url, headers=headers, timeout=10)
                if resp.ok and resp.content and resp.headers.get('Content-Type','').startswith('image'):
                    try:
                        image_obj = Image.open(BytesIO(resp.content))
                        img_col1, img_col2, img_col3 = st.columns([1, 2, 1])
                        with img_col2:
                            st.image(image_obj, width=120)
                    except Exception as e:
                        # Fallback to direct bytes
                        img_col1, img_col2, img_col3 = st.columns([1, 2, 1])
                        with img_col2:
                            st.image(resp.content, width=120)
                else:
                    # Fallback to direct URL rendering
                    try:
                        img_col1, img_col2, img_col3 = st.columns([1, 2, 1])
                        with img_col2:
                            st.image(image_url, width=120)
                    except Exception:
                        st.markdown("<p style='text-align: center;'>📷 Image not available</p>", unsafe_allow_html=True)
            except Exception as _e:
                # Absolute fallback
                try:
                    img_col1, img_col2, img_col3 = st.columns([1, 2, 1])
                    with img_col2:
                        st.image(image_url, width=120)
                except Exception:
                    st.markdown("<p style='text-align: center;'>📷 Image not available</p>", unsafe_allow_html=True)
        else:
            st.markdown("<p style='text-align: center;'>📷 No image</p>", unsafe_allow_html=True)
        
        # Product details - centered
        product_name = current_product.get('name', 'Unknown Product')
        st.markdown(f"<h4 style='text-align: center;'>{product_name}</h3>", unsafe_allow_html=True)
        
        # Brand - handle different field names
        # brand = current_product.get('source', '') or current_product.get('brand', '')
        # if brand:
        #     st.write(f"**Brand:** {brand}")
        
        # Product URL - handle different field names  
        product_url = current_product.get('product_url', '') or current_product.get('url', '')
        if product_url:
            st.markdown(f"<p style='text-align: center;'><a href='{product_url}' target='_blank'>View Product</a></p>", unsafe_allow_html=True)
    
    # Action buttons
    st.write("")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("👎 Pass", use_container_width=True):
            handle_swipe('dislike')
    
    with col2:
        if st.button("⭐ Super Like", use_container_width=True):
            handle_swipe('super_like')
    
    with col3:
        if st.button("❤️ Like", use_container_width=True):
            handle_swipe('like')

else:
    if st.session_state.ai_mode:
        st.warning("🎯 No more AI recommendations available!")
        st.write("Keep swiping - we'll get more recommendations every 10 swipes!")
    else:
        st.warning("📦 No more products to show from the catalog!")
