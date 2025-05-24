#!/usr/bin/env python3

import os
import argparse
from PIL import Image
from pillow_heif import register_heif_opener

# Register HEIF opener with Pillow
register_heif_opener()

def convert_to_grayscale(input_path, output_path):
    """
    Convert an image to grayscale.
    
    Args:
        input_path (str): Path to the input image
        output_path (str): Path where the grayscale image will be saved
    """
    try:
        # Open the image
        with Image.open(input_path) as img:
            # Convert to grayscale
            img_gray = img.convert('L')
            
            # Save the grayscale image
            img_gray.save(output_path, quality=95)
            print(f"Converted: {os.path.basename(input_path)} -> {os.path.basename(output_path)}")
            
    except Exception as e:
        print(f"Error processing {input_path}: {str(e)}")

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Convert images to grayscale.')
    parser.add_argument('folder', type=str, help='Path to the folder containing images')
    
    args = parser.parse_args()
    
    # Check if folder exists
    if not os.path.isdir(args.folder):
        print(f"Error: {args.folder} is not a valid directory")
        return
    
    # Get list of image files
    image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.heic', '.heif')
    image_files = [f for f in os.listdir(args.folder) 
                  if f.lower().endswith(image_extensions)]
    image_files.sort()
    
    # Process each image
    for filename in image_files:
        input_path = os.path.join(args.folder, filename)
        output_path = os.path.join(args.folder, filename)
        convert_to_grayscale(input_path, output_path)

if __name__ == '__main__':
    main() 