#!/usr/bin/env python3

import os
import argparse
import requests
import base64
from PIL import Image
from pillow_heif import register_heif_opener

api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    raise ValueError("Please set the OPENAI_API_KEY environment variable")

# Register HEIF opener with Pillow
register_heif_opener()

def encode_image_to_base64(image_path):
    with Image.open(image_path) as img:
        img = img.convert('RGB')
        from io import BytesIO
        buffer = BytesIO()
        img.save(buffer, format='JPEG')
        return base64.b64encode(buffer.getvalue()).decode('utf-8')

def generate_description_openai(image_path, reference_token):
    prompt = f"""Describe the subject of the image in one line, consistently starting with: 'a photo of a person ...'.
    Include facial expression, head angle or orientation, visible clothing or accessories, and lighting context.
    For example: 'a photo of a person smiling, looking at camera, wearing a padded coat, indoor lighting'
    """
    base64_image = encode_image_to_base64(image_path)
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]
            }
        ],
        "max_tokens": 300
    }
    try:
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        response.raise_for_status()
        description = response.json()["choices"][0]["message"]["content"].strip()
        return f"{reference_token}, {description}"
    except Exception as e:
        print(f"Error processing {image_path}: {str(e)}")
        return f"{reference_token}, Error generating description"

def main():
    parser = argparse.ArgumentParser(description='Generate detailed descriptions for images using OpenAI Vision API.')
    parser.add_argument('folder', type=str, help='Path to the folder containing images')
    parser.add_argument('--token', type=str, required=True, help='Reference token to prefix descriptions')
    args = parser.parse_args()

    if not os.path.isdir(args.folder):
        print(f"Error: {args.folder} is not a valid directory")
        return

    image_extensions = ('.jpg', '.JPG', '.jpeg', '.png', '.PNG', '.bmp', '.gif', '.heic', '.HEIC', '.heif')
    image_files = [f for f in os.listdir(args.folder) if f.lower().endswith(image_extensions)]
    image_files.sort()

    for filename in image_files:
        if filename.startswith('gray_'):
            continue
        input_path = os.path.join(args.folder, filename)
        output_path = os.path.join(args.folder, f"{os.path.splitext(filename)[0]}.txt")
        print(f"Processing {filename}...")
        description = generate_description_openai(input_path, args.token)
        with open(output_path, 'w') as f:
            f.write(description)
        print(f"Generated description for {filename}")

if __name__ == '__main__':
    main() 