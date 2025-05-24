#!/usr/bin/env python3

import os
import argparse
import shutil

def rename_images(folder_path):
    """
    Rename all images in the folder to be sequentially numbered from 001.jpg
    
    Args:
        folder_path (str): Path to the folder containing images
    """
    # Get list of image files and sort them
    image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.heic', '.heif')
    image_files = [f for f in os.listdir(folder_path) 
                  if f.lower().endswith(image_extensions)]
    image_files.sort()
    
    # Create a temporary directory for the renaming process
    temp_dir = os.path.join(folder_path, '.temp')
    os.makedirs(temp_dir, exist_ok=True)
    
    try:
        # First, move all files to temp directory with their original names
        for filename in image_files:
            src = os.path.join(folder_path, filename)
            dst = os.path.join(temp_dir, filename)
            shutil.move(src, dst)
        
        # Then move them back with new sequential names
        for i, filename in enumerate(image_files, start=1):
            old_path = os.path.join(temp_dir, filename)
            new_name = f"{i:03d}.jpg"
            new_path = os.path.join(folder_path, new_name)
            shutil.move(old_path, new_path)
            print(f"Renamed: {filename} -> {new_name}")
            
    except Exception as e:
        print(f"Error during renaming: {str(e)}")
        # Try to recover files from temp directory if something went wrong
        for filename in os.listdir(temp_dir):
            src = os.path.join(temp_dir, filename)
            dst = os.path.join(folder_path, filename)
            if os.path.exists(src):
                shutil.move(src, dst)
    
    finally:
        # Clean up temp directory
        if os.path.exists(temp_dir):
            try:
                os.rmdir(temp_dir)
            except:
                pass

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Rename images in a folder to sequential numbers.')
    parser.add_argument('folder', type=str, help='Path to the folder containing images')
    
    args = parser.parse_args()
    
    # Check if folder exists
    if not os.path.isdir(args.folder):
        print(f"Error: {args.folder} is not a valid directory")
        return
    
    # Rename the images
    rename_images(args.folder)

if __name__ == '__main__':
    main() 