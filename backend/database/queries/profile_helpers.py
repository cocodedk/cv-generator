"""Helper functions for profile operations."""
from typing import Optional, Dict, Any


def build_save_params(profile_data: Dict[str, Any], updated_at: str) -> Dict[str, Any]:
    """Build parameters for save_profile query."""
    personal_info = profile_data.get("personal_info", {})
    address = personal_info.get("address") or {}
    return {
        "updated_at": updated_at,
        "name": personal_info.get("name", ""),
        "title": personal_info.get("title"),
        "email": personal_info.get("email"),
        "phone": personal_info.get("phone"),
        "address_street": address.get("street"),
        "address_city": address.get("city"),
        "address_state": address.get("state"),
        "address_zip": address.get("zip"),
        "address_country": address.get("country"),
        "linkedin": personal_info.get("linkedin"),
        "github": personal_info.get("github"),
        "website": personal_info.get("website"),
        "summary": personal_info.get("summary"),
        "experiences": profile_data.get("experience", []),
        "educations": profile_data.get("education", []),
        "skills": profile_data.get("skills", []),
    }


def build_address(person: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Build address dict from person node properties."""
    fields = [
        "address_street",
        "address_city",
        "address_state",
        "address_zip",
        "address_country",
    ]
    if not any(person.get(f) for f in fields):
        return None
    return {k.replace("address_", ""): person.get(k) for k in fields}


def process_profile_record(record: Any) -> Optional[Dict[str, Any]]:
    """Process Neo4j record into profile dict."""
    if not record or not record["person"]:
        return None
    person = record["person"]
    return {
        "updated_at": record["profile"].get("updated_at"),
        "personal_info": {
            "name": person.get("name"),
            "title": person.get("title"),
            "email": person.get("email"),
            "phone": person.get("phone"),
            "address": build_address(person),
            "linkedin": person.get("linkedin"),
            "github": person.get("github"),
            "website": person.get("website"),
            "summary": person.get("summary"),
        },
        "experience": [dict(exp) for exp in record["experiences"] if exp],
        "education": [dict(edu) for edu in record["educations"] if edu],
        "skills": [dict(skill) for skill in record["skills"] if skill],
    }
