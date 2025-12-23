"""Read CV queries."""
from typing import Optional, Dict, Any
from backend.database.connection import Neo4jConnection


def get_cv_by_id(cv_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve CV with all related nodes."""
    driver = Neo4jConnection.get_driver()

    query = """
    MATCH (cv:CV {id: $cv_id})
    OPTIONAL MATCH (person:Person)-[:BELONGS_TO_CV]->(cv)
    OPTIONAL MATCH (person)-[:HAS_EXPERIENCE]->(exp:Experience)-[:BELONGS_TO_CV]->(cv)
    OPTIONAL MATCH (person)-[:HAS_EDUCATION]->(edu:Education)-[:BELONGS_TO_CV]->(cv)
    OPTIONAL MATCH (person)-[:HAS_SKILL]->(skill:Skill)-[:BELONGS_TO_CV]->(cv)

    RETURN cv, person,
           collect(DISTINCT exp) AS experiences,
           collect(DISTINCT edu) AS educations,
           collect(DISTINCT skill) AS skills
    """

    database = Neo4jConnection.get_database()
    with driver.session(database=database) as session:
        result = session.run(query, cv_id=cv_id)
        record = result.single()

        if not record or not record["person"]:
            return None

        person = record["person"]
        experiences = [dict(exp) for exp in record["experiences"] if exp]
        educations = [dict(edu) for edu in record["educations"] if edu]
        skills = [dict(skill) for skill in record["skills"] if skill]

        # Build address object from separate properties
        address = None
        if any(
            [
                person.get("address_street"),
                person.get("address_city"),
                person.get("address_state"),
                person.get("address_zip"),
                person.get("address_country"),
            ]
        ):
            address = {
                "street": person.get("address_street"),
                "city": person.get("address_city"),
                "state": person.get("address_state"),
                "zip": person.get("address_zip"),
                "country": person.get("address_country"),
            }

        return {
            "cv_id": record["cv"]["id"],
            "created_at": record["cv"]["created_at"],
            "updated_at": record["cv"]["updated_at"],
            "filename": record["cv"].get("filename"),
            "theme": record["cv"].get("theme", "classic"),
            "personal_info": {
                "name": person.get("name"),
                "email": person.get("email"),
                "phone": person.get("phone"),
                "address": address,
                "linkedin": person.get("linkedin"),
                "github": person.get("github"),
                "website": person.get("website"),
                "summary": person.get("summary"),
            },
            "experience": experiences,
            "education": educations,
            "skills": skills,
        }
