"""Helper functions for profile operations."""
from typing import Optional, Dict, Any


def safe_get(obj: Any, key: str, default: Any = None) -> Any:
    """Safely get value from object, handling dict-like and indexable objects."""
    if hasattr(obj, "get"):
        try:
            return obj.get(key, default)
        except TypeError:
            return obj.get(key)
    try:
        return obj[key]
    except Exception:
        return default


def ensure_list(value: Any) -> list:
    """Ensure value is a list, converting if necessary."""
    if not value:
        return []
    if isinstance(value, list):
        return value
    try:
        return list(value)
    except TypeError:
        return []


def build_personal_info(person: Dict[str, Any]) -> Dict[str, Any]:
    """Build personal_info dict from person node."""
    return {
        "name": safe_get(person, "name"),
        "title": safe_get(person, "title"),
        "email": safe_get(person, "email"),
        "phone": safe_get(person, "phone"),
        "address": build_address(person),
        "linkedin": safe_get(person, "linkedin"),
        "github": safe_get(person, "github"),
        "website": safe_get(person, "website"),
        "summary": safe_get(person, "summary"),
        "photo": safe_get(person, "photo"),
    }


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
        "photo": personal_info.get("photo"),
        "experiences": profile_data.get("experience", []),
        "educations": profile_data.get("education", []),
        "skills": profile_data.get("skills", []),
        "language": profile_data.get("language", "en"),
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
    if not record:
        return None

    person = safe_get(record, "person")
    profile = safe_get(record, "profile")
    if not person or not profile:
        return None

    experiences = ensure_list(safe_get(record, "experiences"))
    educations = ensure_list(safe_get(record, "educations"))
    skills = ensure_list(safe_get(record, "skills"))

    return {
        "updated_at": safe_get(profile, "updated_at"),
        "personal_info": build_personal_info(person),
        "experience": [dict(exp) for exp in experiences if exp],
        "education": [dict(edu) for edu in educations if edu],
        "skills": [dict(skill) for skill in skills if skill],
        "language": safe_get(profile, "language") or "en",
    }
