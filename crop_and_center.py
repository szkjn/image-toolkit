#!/usr/bin/env python3

import os
import argparse
from PIL import Image

def crop_and_center(input_path, output_path, size=512):
    """
    Process a single image by cropping it to a square from the center and resizing it.
    
    Args:
        input_path (str): Path to the input image
        output_path (str): Path where the processed image will be saved
        size (int): Target size for the square image (default: 512)
    """
    try:
        # Open the image
        with Image.open(input_path) as img:
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Get the dimensions
            width, height = img.size
            
            # Calculate the square crop dimensions
            crop_size = min(width, height)
            left = (width - crop_size) // 2
            top = (height - crop_size) // 2
            right = left + crop_size
            bottom = top + crop_size
            
            # Crop the image to a square from the center
            img_cropped = img.crop((left, top, right, bottom))
            
            # Resize the image
            img_resized = img_cropped.resize((size, size), Image.Resampling.LANCZOS)
            
            # Save the processed image
            img_resized.save(output_path, quality=95)
            print(f"Processed: {os.path.basename(input_path)} -> {os.path.basename(output_path)}")
            
    except Exception as e:
        print(f"Error processing {input_path}: {str(e)}")

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Process images by cropping to square and resizing.')
    parser.add_argument('--size', type=int, default=512,
                      help='Target size for the square image (default: 512)')
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    os.makedirs('output', exist_ok=True)
    
    # Get list of image files in input directory
    input_dir = 'input'
    output_dir = 'output'
    
    # Supported image formats
    image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.gif')
    
    # Get all image files and sort them
    image_files = [f for f in os.listdir(input_dir) 
                  if f.lower().endswith(image_extensions)]
    image_files.sort()
    
    # Process each image in the input directory
    for index, filename in enumerate(image_files, start=1):
        input_path = os.path.join(input_dir, filename)
        # Create new filename with sequential number
        new_filename = f"{index:03d}.jpg"  # This will create 001.jpg, 002.jpg, etc.
        output_path = os.path.join(output_dir, new_filename)
        crop_and_center(input_path, output_path, args.size)

if __name__ == '__main__':
    main() 