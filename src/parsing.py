import json
import re
from pathlib import Path
from typing import Dict, Optional, Any

def parse_ai_response(content: str, image_path: Optional[str] = None) -> Dict[str, Any]:
    try:
        clean_content = content.replace('```json', '').replace('```', '').strip()
        parsed_data = json.loads(clean_content)
        print("Successfully parsed response after markdown cleanup")
        return parsed_data
    except json.JSONDecodeError:
        print("Direct parsing failed, trying regex extraction")
    
    json_match = re.search(r'\{.*\}', content, re.DOTALL)
    if json_match:
        try:
            json_str = json_match.group(0)
            parsed_data = json.loads(json_str)
            print("Successfully extracted JSON using regex")
            return parsed_data
        except json.JSONDecodeError:
            print("Embedded JSON extraction failed")
    
    print("Attempting to extract structured data from unstructured response")
    return extract_structured_data(content, image_path)


def extract_structured_data(text: str, image_path: Optional[str] = None) -> Dict[str, Any]:
    structured_data = {
        "document_type": extract_field(text, "Document Type", "Type"),
        "issuing_country": extract_field(text, "Issuing Country", "Country"),
        "full_name": extract_field(text, "Full Name", "Name"),
        "first_name": extract_field(text, "First Name"),
        "last_name": extract_field(text, "Last Name"),
        "address": extract_field(text, "Address"),
        "date_of_birth": extract_field(text, "Date of Birth", "DOB", "Birth"),
        "expiration_date": extract_field(text, "Expiration Date", "Expires"),
        "issue_date": extract_field(text, "Issue Date", "Issued"),
        "gender": extract_field(text, "Gender", "Sex"),
        "document_number": extract_field(text, "Document Number", "ID Number", "License Number", "Number"),
        "additional_info": {}
    }
    
    for field, aliases in {
        "height": ["Height"],
        "eye_color": ["Eye", "Eyes", "Eye Color"],
        "hair_color": ["Hair", "Hair Color"],
        "weight": ["Weight"],
        "class": ["Class", "License Class"]
    }.items():
        value = extract_field(text, *aliases)
        if value:
            structured_data["additional_info"][field] = value
    
    if structured_data["document_number"] and image_path:
        image_filename = Path(image_path).name.lower()
        if "license" in image_filename:
            doc_num = structured_data["document_number"]
            if doc_num.startswith("11") and len(doc_num) >= 7:
                structured_data["document_number"] = "I" + doc_num[1:]
            elif doc_num.startswith("IL") and len(doc_num) >= 8:
                structured_data["document_number"] = "I" + doc_num[2:]
    
    structured_data = {k: v for k, v in structured_data.items() if v}
    if not structured_data.get("additional_info"):
        structured_data.pop("additional_info", None)
    
    if len(structured_data) <= 2:
        print("Insufficient structured data extracted, returning raw text")
        return {"raw_text": text}
    
    return structured_data


def extract_field(text: str, *field_names: str) -> Optional[str]:
    for field_name in field_names:
        patterns = [
            rf'\b{field_name}\s*:\s*([^,\n]+)',
            rf'\*\*{field_name}\*\*\s*:\s*([^,\n]+)',
            rf'\*\*{field_name}\*\*\s*:\s*([^\n]+)',
            rf'[\*\+]\s*\*?\*?{field_name}\*?\*?\s*:?\s*([^,\n]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
    
    return None
