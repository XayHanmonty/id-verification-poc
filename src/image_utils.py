import base64
from pathlib import Path
from typing import List

def encode_image(image_path: str) -> str:
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        print(f"Failed to encode image {image_path}: {e}")
        raise

def find_image_files(directory: Path) -> List[Path]:
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
    image_files = []
    
    for ext in image_extensions:
        image_files.extend(list(directory.glob(f'*{ext}')))
        image_files.extend(list(directory.glob(f'*{ext.upper()}')))
    
    return image_files
