import json
import os
from pathlib import Path
from typing import Dict, Optional, Any

import fireworks.client

from image_utils import encode_image, find_image_files
from parsing import parse_ai_response
from postprocess import post_process_extraction

def process_image(image_path: str) -> Optional[Dict[str, Any]]:
    print(f"Processing image: {image_path}")
    
    try:
        image_base64 = encode_image(image_path)
    except Exception as e:
        print(f"Error encoding image {image_path}: {e}")
        return None
    
    try:
        response_format = {
            "type": "json_object",
            "schema": {
                "type": "object",
                "properties": {
                    "document_type": {
                        "type": "string",
                        "description": "Type of ID (driver license, passport, etc.)"
                    },
                    "issuing_country": {
                        "type": "string",
                        "description": "Country or state that issued the ID"
                    },
                    "full_name": {
                        "type": "string",
                        "description": "Full name of the ID holder exactly as it appears"
                    },
                    "first_name": {
                        "type": "string",
                        "description": "First name of the ID holder"
                    },
                    "last_name": {
                        "type": "string",
                        "description": "Last name of the ID holder"
                    },
                    "address": {
                        "type": "string",
                        "description": "Full address if available"
                    },
                    "date_of_birth": {
                        "type": "string",
                        "description": "Date of birth in MM/DD/YYYY format"
                    },
                    "expiration_date": {
                        "type": "string",
                        "description": "Document expiration date in MM/DD/YYYY format"
                    },
                    "issue_date": {
                        "type": "string",
                        "description": "Document issue date in MM/DD/YYYY format"
                    },
                    "gender": {
                        "type": "string",
                        "description": "Gender/sex"
                    },
                    "document_number": {
                        "type": "string",
                        "description": "The ID document number. For California drivers licenses, this typically starts with a letter (like 'I') followed by 7 digits"
                    },
                    "additional_info": {
                        "type": "object",
                        "description": "Any other relevant information like height, eye color, etc."
                    }
                },
                "required": ["document_type", "full_name"]
            }
        }
        
        response = fireworks.client.ChatCompletion.create(
            model="accounts/fireworks/models/llama-v3p2-11b-vision-instruct",
            response_format=response_format,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}"
                        }
                    },
                    {
                        "type": "text",
                        "text": """This is a SAMPLE/TEST ID document image with fake information for testing purposes.
                    
Please extract ALL information from this ID document and return it in the specified structured format.

IMPORTANT: 
- This is a SAMPLE/TEST ID with FICTIONAL information used for testing. 
- DO NOT REDACT any parts of the document number or any other information - show the complete data.
- Extract the DOCUMENT NUMBER carefully, especially for California driver's licenses.
- Include any additional information like height, eye color, etc. in the additional_info field."""
                    }
                ]
            }],
            max_tokens=1000,
            temperature=0
        )
        
        content = response.choices[0].message.content.strip()
        
        try:
            parsed_data = json.loads(content)
            normalized_data = post_process_extraction(parsed_data, image_path)
            return normalized_data
        except json.JSONDecodeError:
            print(f"Warning: Could not parse response as JSON, attempting alternative parsing")
            return parse_ai_response(content, image_path)
            
    except Exception as e:
        print(f"Error processing image with AI model: {e}")
        return None


def process_directory(directory_path: str) -> Dict[str, Dict[str, Any]]:
    api_key = os.environ.get("FIREWORKS_API_KEY")
    if not api_key:
        print("Error: FIREWORKS_API_KEY environment variable is not set")
        raise EnvironmentError("FIREWORKS_API_KEY environment variable is required")
    
    fireworks.client.api_key = api_key
    
    dir_path = Path(directory_path)
    if not dir_path.exists() or not dir_path.is_dir():
        print(f"Error: Invalid directory: {directory_path}")
        raise ValueError(f"Directory does not exist: {directory_path}")
    
    image_files = find_image_files(dir_path)
    if not image_files:
        print(f"Warning: No image files found in {directory_path}")
        return {}
    
    print(f"Found {len(image_files)} image files")
    
    results = {}
    for img_path in image_files:
        try:
            result = process_image(str(img_path))
            if result:
                results[img_path.name] = result
            else:
                print(f"Warning: Failed to extract information from {img_path}")
        except Exception as e:
            print(f"Error processing {img_path}: {e}")
    
    output_dir = Path("../output")
    output_dir.mkdir(exist_ok=True)
    
    output_path = output_dir / "extraction_results.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Results saved to {output_path}")
    
    return results
