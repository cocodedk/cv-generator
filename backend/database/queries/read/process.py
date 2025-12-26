"""Process CV records into dictionaries."""
from typing import Optional, Dict, Any


def build_address(person: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Build address dict from person node properties."""
    if any(
        [
            person.get("address_street"),
            person.get("address_city"),
            person.get("address_state"),
            person.get("address_zip"),
            person.get("address_country"),
        ]
    ):
        return {
            "street": person.get("address_street"),
            "city": person.get("address_city"),
            "state": person.get("address_state"),
            "zip": person.get("address_zip"),
            "country": person.get("address_country"),
        }
    return None


def process_cv_record(record: Any) -> Optional[Dict[str, Any]]:
    """Process Neo4j record into CV dict."""
    if not record or not record["person"]:
        return None

    person = record["person"]
    experiences = [dict(exp) for exp in record["experiences"] if exp]
    educations = [dict(edu) for edu in record["educations"] if edu]
    skills = [dict(skill) for skill in record["skills"] if skill]

    return {
        "cv_id": record["cv"]["id"],
        "created_at": record["cv"]["created_at"],
        "updated_at": record["cv"]["updated_at"],
        "filename": record["cv"].get("filename"),
        "theme": record["cv"].get("theme", "classic"),
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
            "photo": person.get("photo"),
        },
        "experience": experiences,
        "education": educations,
        "skills": skills,
    }
