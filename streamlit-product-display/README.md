# Slapp-AI ⚡ - AI-Powered Fashion Discovery

A **Tinder-like fashion discovery app** that learns your style preferences through swiping and provides personalized clothing recommendations using AI.

## What It Does

**Imagine Tinder for Fashion** - but smarter! Users swipe through clothing items to express their preferences, and the AI learns their style to recommend products they'll actually love.

### Two-Phase Experience
- **Discovery Mode** (Swipes 1-20): Browse 6,000+ fashion items from 8+ premium brands
- **AI Mode** (Swipe 21+): Get personalized recommendations powered by SuperMemory AI
- **Real-time Learning**: Every swipe is instantly saved and analyzed

## Tech Stack

- **Frontend**: Streamlit (Python web app)
- **AI/ML**: SuperMemory API for preference learning and recommendations
- **Data**: 6,000+ products with AI-generated clothing descriptions (LLaVA Vision Model)
- **Brands**: Alo Yoga, Gymshark, NAKD, Princess Polly, Vuori, and more

## Project Structure

```
devhacks/
├── streamlit-product-display/           # Main Streamlit application
│   ├── src/
│   │   ├── app.py                      # Core app with swiping logic & UI
│   │   ├── user_memory.py              # Save preferences to SuperMemory
│   │   ├── get_user_preference.py      # Retrieve user preferences
│   │   ├── query_main_memory.py        # AI recommendation engine
│   │   ├── components/
│   │   │   └── product_card.py         # Product display components
│   │   └── utils/
│   │       └── data_loader.py          # CSV data loading utilities
│   ├── requirements.txt                # Python dependencies
│   └── README.md                       # Setup instructions
├── final_products_complete.csv         # Main product dataset (6k items)
├── ViT_Img_Descriptor.py              # LLaVA vision model for clothing analysis
├── supermemory_batch_push.py           # Bulk upload products to SuperMemory
├── supermemory_helper.py               # Individual product upload
├── supermemory_search.py               # Search functionality testing
├── utils/
│   └── preprocess.py                   # Unify brand-specific CSV files
└── data/                               # Brand-specific product datasets
    ├── alo_yoga_products.csv
    ├── gymshark_products.csv
    └── ...                             # Additional brand files
```

## Quick Setup

1. **Install dependencies**
   ```bash
   cd streamlit-product-display
   pip install -r requirements.txt
   ```

2. **Run the app**
   ```bash
   cd src
   streamlit run app.py
   ```

3. **Start discovering fashion**
   - Open browser to `http://localhost:8501`
   - Swipe ❤️ Like, ⭐ Super Like, or 👎 Pass on clothing items
   - Watch the AI learn your style and provide personalized recommendations

## How It Works

1. **Browse & Learn**: Users swipe through curated fashion items
2. **Preference Capture**: Each swipe is saved to SuperMemory with detailed product metadata
3. **AI Analysis**: SuperMemory analyzes collective preferences to understand user style
4. **Smart Recommendations**: AI queries the product database to find matching items
5. **Continuous Improvement**: More swipes = better recommendations

## Key Features

- **Session-based**: Each user gets a private style profile
- **Background AI Building**: Recommendations prepared while you browse
- **Fallback Systems**: App never breaks - switches to random products if needed
- **Rich Product Data**: AI-generated clothing descriptions enable semantic matching