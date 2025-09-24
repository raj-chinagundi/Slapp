import os
import pandas as pd

def preprocess_alo_yoga(df):
    """Preprocess Alo Yoga products - keeping only universal columns"""
    processed_df = pd.DataFrame()
    
    # Universal columns only (100% present across all brands)
    # No useful metadata in product_id (just index), so keep name as is
    processed_df['name'] = df['name']
    processed_df['product_url'] = df['product_url']
    processed_df['image_url'] = df['image_url']
    processed_df['source'] = 'alo_yoga'
    
    return processed_df

def preprocess_altardstate(df):
    """Preprocess Altar'd State products - keeping only universal columns"""
    processed_df = pd.DataFrame()
    
    # Universal columns only (100% present across all brands)
    processed_df['name'] = df['name']
    processed_df['product_url'] = df['url']
    processed_df['image_url'] = df['image_url']
    processed_df['source'] = 'altardstate'
    
    return processed_df

def preprocess_cupshe(df):
    """Preprocess Cupshe products - keeping only universal columns"""
    processed_df = pd.DataFrame()
    
    # Universal columns only (100% present across all brands)
    processed_df['name'] = df['name']
    processed_df['product_url'] = df['url']
    processed_df['image_url'] = df['image_url']
    processed_df['source'] = 'cupshe'
    
    return processed_df

def preprocess_edikted(df):
    """Preprocess Edikted products - keeping only universal columns"""
    processed_df = pd.DataFrame()
    
    # Universal columns only (100% present across all brands)
    processed_df['name'] = df['name']
    processed_df['product_url'] = df['url']
    processed_df['image_url'] = df['image_url']
    processed_df['source'] = 'edikted'
    
    return processed_df

def preprocess_gymshark(df):
    """Preprocess Gymshark products - keeping only universal columns"""
    processed_df = pd.DataFrame()

    processed_df['name'] = df['product_id'].combine(df['name'], lambda id, name: f"{name} ({id})")
    processed_df['product_url'] = df['url']
    processed_df['image_url'] = df['image_url']
    processed_df['source'] = 'gymshark'
    
    return processed_df

def preprocess_nakd(df):
    """Preprocess NA-KD products - keeping only universal columns"""
    processed_df = pd.DataFrame()
    
    # Universal columns only (100% present across all brands)
    processed_df['name'] = df['name']
    processed_df['product_url'] = df['url']
    processed_df['image_url'] = df['image_url']
    processed_df['source'] = 'nakd'
    
    return processed_df

def preprocess_princess_polly(df):
    """Preprocess Princess Polly products - keeping only universal columns"""
    processed_df = pd.DataFrame()
    
    # Universal columns only (100% present across all brands)
    # No useful metadata in product_id (just index), so keep name as is
    processed_df['name'] = df['title']
    processed_df['product_url'] = df['product_url']
    processed_df['image_url'] = df['image_url']
    processed_df['source'] = 'princess_polly'
    
    return processed_df

def preprocess_vuori(df):
    """Preprocess Vuori products - keeping only universal columns"""
    processed_df = pd.DataFrame()
    
    # Universal columns only (100% present across all brands)
    processed_df['name'] = df['product_id'].combine(df['name'], lambda id, name: f"{name} ({id})")
    processed_df['product_url'] = df['url']
    processed_df['image_url'] = df['image_url']
    processed_df['source'] = 'vuori'
    
    return processed_df

def create_unified_dataset():
    """Create a unified dataset from all CSV files"""
    data_dir = "data"
    csv_files = [
        ("alo_yoga_products.csv", preprocess_alo_yoga),
        ("altardstate_products.csv", preprocess_altardstate),
        ("cupshe_products.csv", preprocess_cupshe),
        ("edikted_products.csv", preprocess_edikted),
        ("gymshark_products.csv", preprocess_gymshark),
        ("nakd_products.csv", preprocess_nakd),
        ("princess_polly.csv", preprocess_princess_polly),
        ("vuori_products.csv", preprocess_vuori)
    ]
    
    unified_data = []
    
    for filename, preprocess_func in csv_files:
        filepath = os.path.join(data_dir, filename)
        if os.path.exists(filepath):
            print(f"Processing {filename}...")
            df = pd.read_csv(filepath)
            processed_df = preprocess_func(df)
            unified_data.append(processed_df)
            print(f"Processed {len(processed_df)} products from {filename}")
        else:
            print(f"File {filename} not found!")
    
    # Combine all datasets
    if unified_data:
        final_df = pd.concat(unified_data, ignore_index=True)
        print(f"\nTotal products in unified dataset: {len(final_df)}")
        return final_df
    else:
        print("No data to process!")
        return pd.DataFrame()

def main():
    """Main function to run preprocessing and create unified dataset"""
    print("Starting preprocessing of all CSV files...")
    
    # Create unified dataset
    unified_df = create_unified_dataset()
    
    if not unified_df.empty:
        # Save unified dataset
        output_path = "data/all_products.csv"
        unified_df.to_csv(output_path, index=False)
        print(f"\nUnified dataset saved to: {output_path}")
        
        # Display summary statistics
        print("\nDataset Summary:")
        print(f"Total products: {len(unified_df)}")
        print(f"Unique sources: {unified_df['source'].nunique()}")
        print(f"Sources: {unified_df['source'].value_counts().to_dict()}")
        
        # Show sample of data
        print("\nSample of unified data:")
        print(unified_df[['name', 'source', 'product_url']].head(10))
        
        # Show column info
        print("\nColumn information:")
        print(unified_df.info())
    
    return unified_df

if __name__ == "__main__":
    main()