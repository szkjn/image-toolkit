# Image Processing Scripts

A collection of Python scripts for image processing tasks.

## Requirements
```bash
pip install -r requirements.txt
```

## Scripts

### 1. Crop and Center (`crop_and_center.py`)
Crops images to square from center and resizes them.
```bash
python crop_and_center.py [--size 512]
```
- Input: Images in `input/` folder
- Output: Square images in `output/` folder
- Optional: `--size` for output dimensions (default: 512)

### 2. Detect Faces (`detect_faces.py`)
Detects and crops faces from images, preserving orientation.
```bash
python detect_faces.py [--size 512]
```
- Input: Images in `input/` folder
- Output: Face crops in `output/` folder
- Optional: `--size` for output dimensions (default: 512)

### 3. Rename Images (`rename_images.py`)
Renumbers images sequentially (001.jpg, 002.jpg, etc.).
```bash
python rename_images.py <folder_path>
```
- Input: Folder containing images
- Output: Renamed images in same folder

### 4. Convert to Grayscale (`to_grayscale.py`)
Converts images to black and white.
```bash
python to_grayscale.py <folder_path>
```
- Input: Folder containing images
- Output: Grayscale versions with "gray_" prefix

### 5. Generate Descriptions (`generate_descriptions.py`)
Creates text descriptions for images using AI.
```bash
python generate_descriptions.py <folder_path> --token <reference_token>
```
- Input: Folder containing images
- Output: Text files with same name as images (001.jpg -> 001.txt)
- Required: `--token` for reference prefix (e.g., jxyz_01)
- Uses BLIP model for image captioning 