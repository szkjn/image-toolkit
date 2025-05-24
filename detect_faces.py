#!/usr/bin/env python3

import os
import argparse
from PIL import Image
import mediapipe as mp
import numpy as np
from pillow_heif import register_heif_opener
import re

# Register HEIF opener with Pillow
register_heif_opener()

def detect_faces(input_path, output_path, size=512):
    """
    Process a single image by detecting faces and saving each face as a square image.
    Preserves original image orientation.
    
    Args:
        input_path (str): Path to the input image
        output_path (str): Path where the processed face image will be saved
        size (int): Target size for the square image (default: 512)
    """
    try:
        # Initialize MediaPipe Face Detection
        mp_face_detection = mp.solutions.face_detection
        face_detection = mp_face_detection.FaceDetection(
            model_selection=1,  # Use the full model for better accuracy
            min_detection_confidence=0.5
        )
        
        # Read the image
        image = np.array(Image.open(input_path))
        
        # Convert the image to RGB if it's not
        if image.shape[2] == 4:  # If image has alpha channel
            image = image[:, :, :3]
        
        # Detect faces
        results = face_detection.process(image)
        
        if not results.detections:
            print(f"No faces found in {os.path.basename(input_path)}")
            return
        
        # Process each face found in the image
        for i, detection in enumerate(results.detections):
            # Get the bounding box
            bbox = detection.location_data.relative_bounding_box
            h, w, _ = image.shape
            
            # Convert relative coordinates to absolute
            x = int(bbox.xmin * w)
            y = int(bbox.ymin * h)
            width = int(bbox.width * w)
            height = int(bbox.height * h)
            
            # Add padding around the face
            padding = int(max(width, height) * 0.2)  # 20% padding
            
            # Calculate the square crop dimensions
            crop_size = max(width, height) + (padding * 2)
            
            # Calculate the center of the face
            center_x = x + width // 2
            center_y = y + height // 2
            
            # Calculate the crop coordinates with padding
            crop_left = max(0, center_x - crop_size // 2)
            crop_top = max(0, center_y - crop_size // 2)
            crop_right = min(w, crop_left + crop_size)
            crop_bottom = min(h, crop_top + crop_size)
            
            # Ensure the crop is square
            crop_size = min(crop_right - crop_left, crop_bottom - crop_top)
            crop_right = crop_left + crop_size
            crop_bottom = crop_top + crop_size
            
            # Crop the face
            face_image = Image.fromarray(image[crop_top:crop_bottom, crop_left:crop_right])
            
            # Resize the face image
            face_image = face_image.resize((size, size), Image.Resampling.LANCZOS)
            
            # Save the face image
            face_image.save(output_path, quality=95)
            print(f"Processed face {i+1} from {os.path.basename(input_path)} -> {os.path.basename(output_path)}")
            
    except Exception as e:
        print(f"Error processing {input_path}: {str(e)}")

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Process images by detecting and cropping faces.')
    parser.add_argument('--size', type=int, default=512,
                      help='Target size for the square image (default: 512)')
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    os.makedirs('output', exist_ok=True)
    
    # Get list of image files in input directory
    input_dir = 'input'
    output_dir = 'output'
    
    # Supported image formats
    image_extensions = ('.jpg', '.JPG', '.jpeg', '.png', '.PNG', '.bmp', '.gif', '.heic', '.HEIC', '.heif')
    
    # Get all image files and sort them
    image_files = [f for f in os.listdir(input_dir) 
                  if f.lower().endswith(image_extensions)]
    image_files.sort()
    
    # Find the highest existing output file number
    output_files = [f for f in os.listdir(output_dir) if re.match(r'\d{3}\.jpg$', f)]
    if output_files:
        max_num = max(int(os.path.splitext(f)[0]) for f in output_files)
        face_counter = max_num + 1
    else:
        face_counter = 1
    
    # Initialize MediaPipe Face Detection once
    mp_face_detection = mp.solutions.face_detection
    face_detection = mp_face_detection.FaceDetection(
        model_selection=1,
        min_detection_confidence=0.5
    )
    
    # Process each image in the input directory
    for filename in image_files:
        input_path = os.path.join(input_dir, filename)
        
        try:
            # Read the image
            image = np.array(Image.open(input_path))
            if image.shape[2] == 4:  # If image has alpha channel
                image = image[:, :, :3]
            
            # Detect faces
            results = face_detection.process(image)
            
            # Skip if no faces found
            if not results.detections:
                print(f"No faces found in {filename}")
                continue
            
            # Process each face in the image
            for _ in results.detections:
                # Create new filename with sequential number
                new_filename = f"{face_counter:03d}.jpg"  # This will create 001.jpg, 002.jpg, etc.
                output_path = os.path.join(output_dir, new_filename)
                detect_faces(input_path, output_path, args.size)
                face_counter += 1
                
        except Exception as e:
            print(f"Error processing {filename}: {str(e)}")
            continue

if __name__ == '__main__':
    main() 