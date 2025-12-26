"""Person node creation."""
from typing import Dict, Any


def create_person_node(tx, updated_at: str, params: Dict[str, Any]):
    """Create Person node and link to Profile."""
    query = """
    MATCH (profile:Profile { updated_at: $updated_at })
    CREATE (newPerson:Person {
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
    CREATE (newPerson)-[:BELONGS_TO_PROFILE]->(profile)
    RETURN profile, newPerson
    """
    # Remove updated_at from params since we're passing it explicitly
    params_without_updated_at = {k: v for k, v in params.items() if k != 'updated_at'}
    result = tx.run(query, updated_at=updated_at, **params_without_updated_at)
    return result.single()
