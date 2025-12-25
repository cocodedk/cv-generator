"""Read CV queries."""
from typing import Optional, Dict, Any
from backend.database.connection import Neo4jConnection


def get_cv_by_id(cv_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve CV with all related nodes."""
    driver = Neo4jConnection.get_driver()

    query = """
    MATCH (cv:CV {id: $cv_id})
    OPTIONAL MATCH (person:Person)-[:BELONGS_TO_CV]->(cv)
    CALL {
        WITH cv, person
        OPTIONAL MATCH (person)-[:HAS_EXPERIENCE]->(exp:Experience)-[:BELONGS_TO_CV]->(cv)
        WITH cv, exp
        OPTIONAL MATCH (exp)-[:HAS_PROJECT]->(proj:Project)-[:BELONGS_TO_CV]->(cv)
        WITH exp, collect(DISTINCT proj) AS projects
        RETURN collect(
            CASE
                WHEN exp IS NULL THEN NULL
                ELSE exp{.*, projects: [p IN projects | p{.*}]}
            END
        ) AS experiences
    }
    CALL {
        WITH cv, person
        OPTIONAL MATCH (person)-[:HAS_EDUCATION]->(edu:Education)-[:BELONGS_TO_CV]->(cv)
        RETURN collect(DISTINCT edu) AS educations
    }
    CALL {
        WITH cv, person
        OPTIONAL MATCH (person)-[:HAS_SKILL]->(skill:Skill)-[:BELONGS_TO_CV]->(cv)
        RETURN collect(DISTINCT skill) AS skills
    }
    RETURN cv, person, experiences, educations, skills
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


def get_cv_by_filename(filename: str) -> Optional[Dict[str, Any]]:
    """Retrieve CV by filename with all related nodes."""
    driver = Neo4jConnection.get_driver()

    query = """
    MATCH (cv:CV {filename: $filename})
    OPTIONAL MATCH (person:Person)-[:BELONGS_TO_CV]->(cv)
    CALL {
        WITH cv, person
        OPTIONAL MATCH (person)-[:HAS_EXPERIENCE]->(exp:Experience)-[:BELONGS_TO_CV]->(cv)
        WITH cv, exp
        OPTIONAL MATCH (exp)-[:HAS_PROJECT]->(proj:Project)-[:BELONGS_TO_CV]->(cv)
        WITH exp, collect(DISTINCT proj) AS projects
        RETURN collect(
            CASE
                WHEN exp IS NULL THEN NULL
                ELSE exp{.*, projects: [p IN projects | p{.*}]}
            END
        ) AS experiences
    }
    CALL {
        WITH cv, person
        OPTIONAL MATCH (person)-[:HAS_EDUCATION]->(edu:Education)-[:BELONGS_TO_CV]->(cv)
        RETURN collect(DISTINCT edu) AS educations
    }
    CALL {
        WITH cv, person
        OPTIONAL MATCH (person)-[:HAS_SKILL]->(skill:Skill)-[:BELONGS_TO_CV]->(cv)
        RETURN collect(DISTINCT skill) AS skills
    }
    RETURN cv, person, experiences, educations, skills
    """

    database = Neo4jConnection.get_database()
    with driver.session(database=database) as session:
        result = session.run(query, filename=filename)
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
