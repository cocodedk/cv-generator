"""Person node creation for CV update."""
from typing import Dict, Any


def create_person_node(tx, cv_id: str, personal_info: Dict[str, Any]):
    """Create Person node and link to CV."""
    address = personal_info.get("address") or {}
    query = """
    MATCH (cv:CV {id: $cv_id})
    CREATE (person:Person {
        name: $name,
        title: $title,
        email: $email,
        phone: $phone,
        address_street: $address_street,
        address_city: $address_city,
        address_state: $address_state,
        address_zip: $address_zip,
        address_country: $address_country,
        linkedin: $linkedin,
        github: $github,
        website: $website,
        summary: $summary,
        photo: $photo
    })
    CREATE (person)-[:BELONGS_TO_CV]->(cv)
    """
    result = tx.run(
        query,
        cv_id=cv_id,
        name=personal_info.get("name", ""),
        title=personal_info.get("title"),
        email=personal_info.get("email"),
        phone=personal_info.get("phone"),
        address_street=address.get("street"),
        address_city=address.get("city"),
        address_state=address.get("state"),
        address_zip=address.get("zip"),
        address_country=address.get("country"),
        linkedin=personal_info.get("linkedin"),
        github=personal_info.get("github"),
        website=personal_info.get("website"),
        summary=personal_info.get("summary"),
        photo=personal_info.get("photo"),
    )
    result.consume()
