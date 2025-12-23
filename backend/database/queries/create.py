"""Create CV queries."""
from typing import Dict, Any
from datetime import datetime
from uuid import uuid4
from backend.database.connection import Neo4jConnection


def create_cv(cv_data: Dict[str, Any]) -> str:
    """Create a CV with all relationships in Neo4j."""
    driver = Neo4jConnection.get_driver()
    cv_id = str(uuid4())
    created_at = datetime.utcnow().isoformat()

    query = """
    // Create CV node
    CREATE (cv:CV {
        id: $cv_id,
        created_at: $created_at,
        updated_at: $created_at
    })

    // Create Person node
    CREATE (person:Person {
        name: $name,
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
        summary: $summary
    })
    CREATE (person)-[:BELONGS_TO_CV]->(cv)

    // Create Experience nodes
    WITH cv, person
    UNWIND $experiences AS exp
    CREATE (experience:Experience {
        title: exp.title,
        company: exp.company,
        start_date: exp.start_date,
        end_date: exp.end_date,
        description: exp.description,
        location: exp.location
    })
    CREATE (person)-[:HAS_EXPERIENCE]->(experience)
    CREATE (experience)-[:BELONGS_TO_CV]->(cv)

    // Create Education nodes
    WITH cv, person
    UNWIND $educations AS edu
    CREATE (education:Education {
        degree: edu.degree,
        institution: edu.institution,
        year: edu.year,
        field: edu.field,
        gpa: edu.gpa
    })
    CREATE (person)-[:HAS_EDUCATION]->(education)
    CREATE (education)-[:BELONGS_TO_CV]->(cv)

    // Create Skill nodes (per-CV to avoid cross-CV deletes and metadata bleed)
    WITH cv, person
    UNWIND $skills AS skill
    CREATE (s:Skill {
        name: skill.name,
        category: skill.category,
        level: skill.level
    })
    CREATE (person)-[:HAS_SKILL]->(s)
    CREATE (s)-[:BELONGS_TO_CV]->(cv)

    RETURN cv.id AS cv_id
    """

    database = Neo4jConnection.get_database()
    personal_info = cv_data.get("personal_info", {})
    address = personal_info.get("address") or {}

    with driver.session(database=database) as session:
        result = session.write_transaction(
            lambda tx: tx.run(
                query,
                cv_id=cv_id,
                created_at=created_at,
                name=personal_info.get("name", ""),
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
                experiences=cv_data.get("experience", []),
                educations=cv_data.get("education", []),
                skills=cv_data.get("skills", []),
            )
        )
        return result.single()["cv_id"]
