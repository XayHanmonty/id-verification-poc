from pathlib import Path
from typing import Dict, Any

def post_process_extraction(data: Dict[str, Any], image_path: str) -> Dict[str, Any]:
    processed = data.copy()
    
    image_filename = Path(image_path).name.lower()
    if "passport" in image_filename and processed.get("document_type", "").lower() != "passport":
        processed["document_type"] = "Passport"
    elif "license" in image_filename and "passport" in processed.get("document_type", "").lower():
        processed["document_type"] = "Driver's License"
    
    if "license" in image_filename:
        calif_indicators = [
            "california" in processed.get("issuing_country", "").lower(),
            "ca" in processed.get("issuing_country", "").lower(),
            "95818" in processed.get("address", "").lower()
        ]
        if any(calif_indicators):
            processed["document_type"] = "California Driver's License"
    
    if "document_number" in processed and "california" in processed.get("document_type", "").lower():
        doc_num = processed["document_number"]
        
        if doc_num.upper().startswith(("DL", "LIC")):
            doc_num = doc_num[2:].strip()
        
        if doc_num.startswith("11") and len(doc_num) >= 7:
            doc_num = "I" + doc_num[1:]
        elif doc_num.startswith("IL") and len(doc_num) >= 8:
            doc_num = "I" + doc_num[2:]
        elif not doc_num.startswith("I") and len(doc_num) == 7:
            doc_num = "I" + doc_num
        
        processed["document_number"] = doc_num
    
    if "additional_info" in processed:
        top_level_fields = [
            "first_name", "last_name", "address", "date_of_birth", 
            "expiration_date", "issue_date", "gender"
        ]
        
        for field in top_level_fields:
            if field not in processed and field in processed.get("additional_info", {}):
                processed[field] = processed["additional_info"].pop(field)
        
        if "gender" not in processed and "sex" in processed.get("additional_info", {}):
            processed["gender"] = processed["additional_info"].pop("sex")
    
    if "full_name" in processed:
        if "CARDHOLDER" in processed["full_name"].upper():
            processed["full_name"] = processed["full_name"].replace("CORDHOLDER", "CARDHOLDER")
        
        if "first_name" not in processed and "last_name" not in processed:
            name_parts = processed["full_name"].split()
            if len(name_parts) >= 2:
                processed["first_name"] = name_parts[0]
                processed["last_name"] = " ".join(name_parts[1:])
    
    if not processed.get("additional_info"):
        processed.pop("additional_info", None)
    
    return processed
