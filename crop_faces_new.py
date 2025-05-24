#!/usr/bin/env python3

import os
import argparse
from PIL import Image, UnidentifiedImageError
import mediapipe as mp
import numpy as np
from pillow_heif import register_heif_opener
import re

# Register HEIF opener with Pillow
register_heif_opener()

def main():
    parser = argparse.ArgumentParser(description='Detects faces, crops them (face is ~2/3 of image), and saves as 512x512 JPGs.')
    parser.add_argument('--input_dir', type=str, default='input',
                        help='Directory containing input images. Default: "input"')
    parser.add_argument('--output_dir', type=str, default='output',
                        help='Directory to save processed images. Default: "output"')
    parser.add_argument('--size', type=int, default=512,
                        help='Target size for the output square image (default: 512)')
    args = parser.parse_args()

    input_dir_abs = os.path.abspath(args.input_dir)
    output_dir_abs = os.path.abspath(args.output_dir)

    os.makedirs(output_dir_abs, exist_ok=True)

    # Supported image formats
    image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.heic', '.heif',
                        '.JPG', '.JPEG', '.PNG', '.BMP', '.GIF', '.HEIC', '.HEIF')

    try:
        image_files = [f for f in os.listdir(input_dir_abs) if f.lower().endswith(image_extensions)]
        image_files.sort()
    except FileNotFoundError:
        print(f"Error: Input directory '{input_dir_abs}' not found.")
        return
    except Exception as e:
        print(f"Error listing files in input directory '{input_dir_abs}': {e}")
        return

    if not image_files:
        print(f"No image files found in '{input_dir_abs}'.")
        return

    # Find the highest existing output file number to continue sequence
    output_files = [f for f in os.listdir(output_dir_abs) if re.match(r'\\d{3,}\\.jpg$', f)]
    face_counter = 1
    if output_files:
        try:
            max_num = max(int(os.path.splitext(f)[0]) for f in output_files)
            face_counter = max_num + 1
        except ValueError:
            print("Warning: Could not parse existing output filenames to determine counter. Starting from 1.")
            # face_counter remains 1

    # Initialize MediaPipe Face Detection
    mp_face_detection = mp.solutions.face_detection
    face_detection = mp_face_detection.FaceDetection(
        model_selection=1,  # Use the full model for better accuracy
        min_detection_confidence=0.5
    )

    print(f"Processing images from: {input_dir_abs}")
    print(f"Saving cropped faces to: {output_dir_abs}")
    print(f"Output size for faces: {args.size}x{args.size}px")

    for filename in image_files:
        input_path = os.path.join(input_dir_abs, filename)
        try:
            pil_image = Image.open(input_path)

            # Ensure image is in RGB format
            if pil_image.mode == 'RGBA' or pil_image.mode == 'LA' or \
               (pil_image.mode == 'P' and 'transparency' in pil_image.info):
                pil_image = pil_image.convert('RGB')
            elif pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')

            image_np = np.array(pil_image)
            h_img, w_img, _ = image_np.shape

            # Detect faces
            results = face_detection.process(image_np)

            if not results.detections:
                print(f"No faces found in {filename}")
                continue

            print(f"Found {len(results.detections)} face(s) in {filename}")
            for i, detection in enumerate(results.detections):
                bbox = detection.location_data.relative_bounding_box
                
                # Convert relative bbox to absolute pixel coordinates
                abs_x = int(bbox.xmin * w_img)
                abs_y = int(bbox.ymin * h_img)
                abs_w = int(bbox.width * w_img)
                abs_h = int(bbox.height * h_img)

                if abs_w <= 0 or abs_h <= 0:
                    print(f"Skipping zero-dimension face detection in {filename} (face #{i+1})")
                    continue

                face_cx = abs_x + abs_w / 2
                face_cy = abs_y + abs_h / 2
                face_max_dim = max(abs_w, abs_h)

                # Desired side length of the square crop region where face_max_dim is 2/3 of it.
                ideal_crop_box_side = face_max_dim * 3.0

                # Calculate initial tentative crop box coordinates (can be outside image bounds)
                cl = face_cx - ideal_crop_box_side / 2
                ct = face_cy - ideal_crop_box_side / 2
                cr = face_cx + ideal_crop_box_side / 2
                cb = face_cy + ideal_crop_box_side / 2

                # Clip these coordinates to image boundaries
                final_crop_x1 = max(0, int(round(cl)))
                final_crop_y1 = max(0, int(round(ct)))
                final_crop_x2 = min(w_img, int(round(cr)))
                final_crop_y2 = min(h_img, int(round(cb)))
                
                # Calculate width and height of this clipped box
                clipped_w = final_crop_x2 - final_crop_x1
                clipped_h = final_crop_y2 - final_crop_y1

                if clipped_w <= 0 or clipped_h <= 0:
                    print(f"Skipping face #{i+1} in {filename}: Crop region has zero or negative size after clipping.")
                    continue
                
                # Determine the side of the square crop (smallest of clipped dimensions)
                square_side = min(clipped_w, clipped_h)

                # Center this square within the clipped_w x clipped_h region
                clipped_center_x = final_crop_x1 + clipped_w / 2
                clipped_center_y = final_crop_y1 + clipped_h / 2

                crop_x_start = int(round(clipped_center_x - square_side / 2))
                crop_y_start = int(round(clipped_center_y - square_side / 2))
                
                # Ensure start coordinates are non-negative after rounding and centering
                crop_x_start = max(0, crop_x_start)
                crop_y_start = max(0, crop_y_start)

                crop_x_end = crop_x_start + square_side
                crop_y_end = crop_y_start + square_side
                
                # Final adjustments to ensure the square crop fits entirely within image bounds
                if crop_x_end > w_img:
                    crop_x_start = w_img - square_side
                    crop_x_end = w_img 
                if crop_y_end > h_img:
                    crop_y_start = h_img - square_side
                    crop_y_end = h_img
                
                # After potential shifts, re-ensure start is not negative
                crop_x_start = max(0, crop_x_start)
                crop_y_start = max(0, crop_y_start)
                
                # Validate final crop dimensions
                if square_side <= 0 or crop_x_start >= w_img or crop_y_start >= h_img or \
                   crop_x_start + square_side > w_img or crop_y_start + square_side > h_img :
                     print(f"Skipping face #{i+1} in {filename}: Invalid final crop dimensions (side: {square_side}, x:{crop_x_start}, y:{crop_y_start})")
                     continue
                
                cropped_face_arr = image_np[crop_y_start:crop_y_end, crop_x_start:crop_x_end]

                if cropped_face_arr.size == 0:
                    print(f"Warning: Crop for face #{i+1} in {filename} resulted in an empty image. Skipping.")
                    continue
                
                cropped_pil_image = Image.fromarray(cropped_face_arr)
                resized_image = cropped_pil_image.resize((args.size, args.size), Image.Resampling.LANCZOS)

                output_filename = f"{face_counter:03d}.jpg"
                current_output_path = os.path.join(output_dir_abs, output_filename)
                resized_image.save(current_output_path, quality=95)
                
                print(f"Saved: {current_output_path} (Original: {filename}, Face #{i+1}, Crop: {square_side}x{square_side}px)")
                face_counter += 1
        
        except FileNotFoundError:
            print(f"Error: Image file not found: {input_path}")
            continue
        except UnidentifiedImageError:
            print(f"Error: Cannot identify image file (possibly corrupt or unsupported format): {input_path}")
            continue
        except Exception as e:
            print(f"Error processing image {filename}: {str(e)}")
            continue
            
    face_detection.close()
    print("Processing complete.")

if __name__ == '__main__':
    main() 