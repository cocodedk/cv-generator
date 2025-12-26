"""Education node creation for profile update."""
from typing import Dict, Any


def create_education_nodes(tx, updated_at: str, educations: list):
    """Create Education nodes and link to Profile and Person."""
    if not educations:
        return
    query = """
    MATCH (profile:Profile { updated_at: $updated_at })
    MATCH (person:Person)-[:BELONGS_TO_PROFILE]->(profile)
    UNWIND $educations AS edu
    CREATE (education:Education {
        degree: edu.degree,
        institution: edu.institution,
        year: edu.year,
        field: edu.field,
        gpa: edu.gpa
    })
    CREATE (person)-[:HAS_EDUCATION]->(education)
    CREATE (education)-[:BELONGS_TO_PROFILE]->(profile)
    """
    tx.run(query, updated_at=updated_at, educations=educations)
