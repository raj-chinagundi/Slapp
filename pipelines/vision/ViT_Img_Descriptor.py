# Install required libraries for local environment
# pip install transformers torch torchvision accelerate bitsandbytes
# pip install pandas Pillow

import pandas as pd
from transformers import LlavaNextProcessor, LlavaNextForConditionalGeneration
import torch
import time
import gc
import os
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
import requests
from io import BytesIO
import numpy as np

def setup_llava_model():
    
    # Clear GPU memory first
    torch.cuda.empty_cache()
    gc.collect()
    
    # Set optimal PyTorch settings for A100
    torch.backends.cudnn.benchmark = True
    torch.backends.cudnn.enabled = True
    
    processor = LlavaNextProcessor.from_pretrained("llava-hf/llava-v1.6-mistral-7b-hf")
    
    # For A100 80GB - use full precision and no quantization for maximum speed
    model = LlavaNextForConditionalGeneration.from_pretrained(
        "llava-hf/llava-v1.6-mistral-7b-hf", 
        torch_dtype=torch.float16,  # Use fp16 for speed while maintaining quality
        low_cpu_mem_usage=True,
        device_map="auto",
        # Remove quantization for A100 - we have enough VRAM
        # load_in_4bit=False,  # Disabled for A100
        trust_remote_code=True
    )
    
    # Enable model compilation for faster inference (PyTorch 2.0+)
    if hasattr(torch, 'compile'):
        print("Compiling model for optimal A100 performance...")
        model = torch.compile(model, mode="max-autotune")
    
    print(f"Model loaded successfully!")
    print(f"GPU Memory: {torch.cuda.memory_allocated()/1024**3:.2f} GB allocated")
    print(f"GPU Memory Reserved: {torch.cuda.memory_reserved()/1024**3:.2f} GB")
    
    return processor, model

def download_image_batch(urls, max_workers=20):
    """Download images in parallel for faster processing"""
    def download_single(url):
        try:
            response = requests.get(url, timeout=10, stream=True)
            response.raise_for_status()
            image = Image.open(BytesIO(response.content)).convert('RGB')
            return url, image
        except Exception as e:
            print(f"Error downloading {url}: {str(e)}")
            return url, None
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(download_single, urls))
    
    return {url: img for url, img in results if img is not None}

def analyze_clothing_features_batch(image_batch, processor, model):
    """Analyze multiple clothing items in a single batch for maximum GPU utilization"""
    batch_results = {}
    
    # Prepare batch data
    prompts = []
    images = []
    urls = []
    
    prompt_template = """[INST] <image>
Analyze this clothing item and describe its key features including:
- Type of clothing (shirt, dress, pants, etc.)
- Color(s)
- Pattern (solid, striped, floral, etc.)
- Material/fabric texture if visible
- Style details (sleeves, collar, fit, etc.)
- Any notable design elements

Provide a concise description focusing on the main clothing features. [/INST]"""

    for url, image in image_batch.items():
        if image is not None:
            prompts.append(prompt_template)
            images.append(image)
            urls.append(url)
    
    if not images:
        return batch_results
    
    try:
        # Process batch
        inputs = processor(text=prompts, images=images, return_tensors="pt", padding=True)
        
        # Move to GPU
        if torch.cuda.is_available():
            inputs = {k: v.to(model.device) for k, v in inputs.items() if isinstance(v, torch.Tensor)}
        
        # Generate responses for the entire batch
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=200,
                do_sample=False,
                temperature=0.1,
                pad_token_id=processor.tokenizer.eos_token_id,
                # Optimize for batch processing
                use_cache=True,
                num_beams=1  # Faster than beam search
            )
        
        # Decode responses
        for i, (url, output) in enumerate(zip(urls, outputs)):
            response = processor.decode(output, skip_special_tokens=True)
            
            # Extract just the generated part
            if "[/INST]" in response:
                features = response.split("[/INST]")[-1].strip()
            else:
                features = response.strip()
            
            batch_results[url] = features
            
    except Exception as e:
        print(f"Error in batch processing: {str(e)}")
        # Fallback to individual processing
        for url, image in zip(urls, images):
            batch_results[url] = analyze_single_image(url, image, processor, model)
    
    return batch_results

def analyze_single_image(url, image, processor, model):
    """Fallback function for individual image analysis"""
    try:
        prompt = """[INST] <image>
Analyze this clothing item and describe its key features including:
- Type of clothing (shirt, dress, pants, etc.)
- Color(s)
- Pattern (solid, striped, floral, etc.)
- Material/fabric texture if visible
- Style details (sleeves, collar, fit, etc.)
- Any notable design elements

Provide a concise description focusing on the main clothing features. [/INST]"""

        inputs = processor(text=prompt, images=image, return_tensors="pt")
        
        if torch.cuda.is_available():
            inputs = {k: v.to(model.device) for k, v in inputs.items() if isinstance(v, torch.Tensor)}
        
        with torch.no_grad():
            output = model.generate(
                **inputs,
                max_new_tokens=200,
                do_sample=False,
                temperature=0.1,
                pad_token_id=processor.tokenizer.eos_token_id
            )
        
        response = processor.decode(output[0], skip_special_tokens=True)
        
        if "[/INST]" in response:
            features = response.split("[/INST]")[-1].strip()
        else:
            features = response.strip()
            
        return features
        
    except Exception as e:
        print(f"Error analyzing single image {url}: {str(e)}")
        return ""

def process_clothing_features(csv_file_path, output_file_path=None, batch_size=32):
    """Main function optimized for A100 80GB GPU with batch processing"""
    
    # Load the CSV file
    print("Loading CSV file...")
    df = pd.read_csv(csv_file_path)
    
    # Initialize the clothing_features column
    df['clothing_features'] = ""
    
    # Setup LLaVA model
    print("Setting up LLaVA 1.6 model...")
    processor, model = setup_llava_model()
    
    # Filter out rows with missing URLs
    valid_rows = df[df['image_url'].notna() & (df['image_url'] != "")]
    total_rows = len(valid_rows)
    print(f"Processing {total_rows} images in batches of {batch_size}...")
    
    # Process in batches for maximum A100 utilization
    processed = 0
    start_time = time.time()
    
    for batch_start in range(0, total_rows, batch_size):
        batch_end = min(batch_start + batch_size, total_rows)
        batch_rows = valid_rows.iloc[batch_start:batch_end]
        
        print(f"\nProcessing batch {batch_start//batch_size + 1}/{(total_rows-1)//batch_size + 1}")
        print(f"Images {batch_start + 1}-{batch_end} of {total_rows}")
        
        # Download images in parallel
        urls = batch_rows['image_url'].tolist()
        print(f"Downloading {len(urls)} images...")
        image_batch = download_image_batch(urls, max_workers=20)
        
        print(f"Successfully downloaded {len(image_batch)}/{len(urls)} images")
        
        # Analyze batch
        if image_batch:
            print("Analyzing clothing features...")
            batch_results = analyze_clothing_features_batch(image_batch, processor, model)
            
            # Update dataframe
            for idx in batch_rows.index:
                url = df.at[idx, 'image_url']
                if url in batch_results:
                    df.at[idx, 'clothing_features'] = batch_results[url]
                    processed += 1
        
        # Progress reporting
        elapsed = time.time() - start_time
        rate = processed / elapsed if elapsed > 0 else 0
        eta = (total_rows - processed) / rate if rate > 0 else 0
        
        print(f"✅ Batch complete. Processed: {processed}/{total_rows}")
        print(f"⚡ Rate: {rate:.2f} images/second")
        print(f"⏱️  ETA: {eta/60:.1f} minutes")
        
        # Save progress
        if output_file_path is None:
            output_file_path = csv_file_path.replace('.csv', '_with_features.csv')
        
        df.to_csv(output_file_path, index=False)
        print(f"💾 Progress saved to {output_file_path}")
        
        # Clear GPU cache
        torch.cuda.empty_cache()
        gc.collect()
    
    print(f"\n🎉 Processing complete! Final results saved to {output_file_path}")
    
    return df

def check_gpu_status():
    """Check GPU availability and memory"""
    if torch.cuda.is_available():
        for i in range(torch.cuda.device_count()):
            gpu_name = torch.cuda.get_device_name(i)
            total_memory = torch.cuda.get_device_properties(i).total_memory / 1024**3
            print(f"✅ GPU {i}: {gpu_name}")
            print(f"   Total Memory: {total_memory:.2f} GB")
            
        print(f"🔥 CUDA Version: {torch.version.cuda}")
        print(f"⚡ PyTorch Version: {torch.__version__}")
    else:
        print("❌ No GPU available")

# Check GPU status first
check_gpu_status()

# Usage example
if __name__ == "__main__":
    # Resolve project root and file paths relative to this script location
    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    input_file = os.path.join(PROJECT_ROOT, "data", "all_products.csv")
    output_file = os.path.join(PROJECT_ROOT, "final_products_complete.csv")
    
    # Adjust batch size based on your A100 memory usage
    # Start with 32, increase to 64 or higher if memory allows
    batch_size = 32
    
    # Process the file
    result_df = process_clothing_features(input_file, output_file, batch_size=batch_size)
    
    # Print summary
    successful_analyses = (result_df['clothing_features'] != "").sum()
    total_rows = len(result_df)
    print(f"\n📊 SUMMARY:")
    print(f"Total rows processed: {total_rows}")
    print(f"Successful analyses: {successful_analyses}")
    print(f"Failed analyses: {total_rows - successful_analyses}")
    print(f"Success rate: {(successful_analyses/total_rows)*100:.1f}%")
    
    # Show sample results
    print(f"\n🔍 SAMPLE RESULTS:")
    for i in range(min(3, len(result_df))):
        if result_df.iloc[i]['clothing_features']:
            print(f"\nProduct: {result_df.iloc[i]['name']}")
            print(f"Features: {result_df.iloc[i]['clothing_features']}")