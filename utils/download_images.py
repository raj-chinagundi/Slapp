# read data from unified csv and download images
import os
import pandas as pd
import requests
from tqdm import tqdm
from urllib.parse import urlparse
from pathlib import Path

# I want to also be able to relate the image back to product so keep the index number of image same as product index

def download_image(image_url, save_dir, index=None):
    """Download an image from a URL and save it to the specified directory."""
    try:
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()  # Raise an error for bad responses
        parsed_url = urlparse(image_url)
        filename = os.path.basename(parsed_url.path)

        if index is not None:
            # If index is provided, rename the file to include the index
            save_path = os.path.join(save_dir, f"{index}_{filename}")

        with open(save_path, 'wb') as f:
            f.write(response.content)
        return save_path
    except Exception as e:
        print(f"Failed to download {image_url}: {e}")
        return None

import concurrent.futures

# do this concurrently for speed
def download_images_from_unified_dataset(unified_df, save_dir, max_workers=8):
    """Download all images from the unified dataset concurrently."""
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    def download_single_image(args):
        index, row = args
        image_url = row['image_url']
        return download_image(image_url, save_dir, index=index)

    # Create list of arguments for concurrent processing
    download_args = [(index, row) for index, row in unified_df.iterrows()]
    
    # Track failed downloads
    failed_indices = []
    
    # Use ThreadPoolExecutor for concurrent downloads
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all download tasks
        future_to_args = {executor.submit(download_single_image, args): args for args in download_args}
        
        # Process completed downloads with progress bar
        for future in tqdm(concurrent.futures.as_completed(future_to_args), 
                          total=len(download_args), 
                          desc="Downloading images"):
            try:
                result = future.result()
                if result is None:
                    args = future_to_args[future]
                    failed_indices.append(args[0])
                    print(f"Failed to download image for index {args[0]}")
            except Exception as exc:
                args = future_to_args[future]
                failed_indices.append(args[0])
                print(f"Download generated an exception for index {args[0]}: {exc}")
    
    return failed_indices

if __name__ == "__main__":
    # # First, create the unified dataset
    # create_unified_dataset()
    
    # Load the unified dataset
    unified_csv_path = "data/all_products.csv"
    if not os.path.exists(unified_csv_path):
        print(f"Unified dataset not found at {unified_csv_path}. Please run the preprocessing step first.")
        exit(1)
    
    unified_df = pd.read_csv(unified_csv_path)
    print(f"Starting with {len(unified_df)} products")
    
    # Directory to save downloaded images
    images_save_dir = "./images"
    
    # Download images and get failed indices
    failed_indices = download_images_from_unified_dataset(unified_df, images_save_dir)
    
    # Remove failed rows from CSV
    if failed_indices:
        print(f"Removing {len(failed_indices)} products with failed image downloads")
        unified_df_cleaned = unified_df.drop(index=failed_indices).reset_index(drop=True)
        unified_df_cleaned.to_csv(unified_csv_path, index=False)
        print(f"CSV updated: {len(unified_df_cleaned)} products remaining")
    else:
        print("All downloads successful - no changes to CSV")
    
    print(f"Images downloaded to {images_save_dir}")