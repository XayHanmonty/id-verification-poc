import json
import os
import sys
from pathlib import Path

import fireworks.client

from extraction import process_directory

def main():
    directory_path = "../data/images"
    output_dir = "../output"
    
    api_key = os.environ.get("FIREWORKS_API_KEY")
    if not api_key:
        print("Error: FIREWORKS_API_KEY environment variable is not set")
        return 1
    
    fireworks.client.api_key = api_key
    
    output_dir_path = Path(output_dir)
    output_dir_path.mkdir(exist_ok=True)
    
    try:
        print(f"Processing directory: {directory_path}")
        results = process_directory(directory_path)
        
        if not results:
            print("Warning: No results extracted")
            return 1
        
        print(f"Processed {len(results)} images successfully")
        
        first_image = next(iter(results))
        print(f"Sample extraction from {first_image}:")
        print(json.dumps(results[first_image], indent=2))
        
        return 0
    
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
