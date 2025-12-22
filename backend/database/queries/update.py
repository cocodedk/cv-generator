"""Update CV queries."""
from typing import Dict, Any
from datetime import datetime
from backend.database.connection import Neo4jConnection


def update_cv(cv_id: str, cv_data: Dict[str, Any]) -> bool:
    """Update CV data."""
    driver = Neo4jConnection.get_driver()
    database = Neo4jConnection.get_database()
    updated_at = datetime.utcnow().isoformat()

    # Delete existing relationships and nodes, then recreate with same CV ID
    update_query = """
    MATCH (cv:CV {id: $cv_id})
    SET cv.updated_at = $updated_at

    // Delete existing relationships and nodes
    OPTIONAL MATCH (person:Person)-[:BELONGS_TO_CV]->(cv)
    OPTIONAL MATCH (person)-[r1:HAS_EXPERIENCE]->(exp:Experience)-[:BELONGS_TO_CV]->(cv)
    OPTIONAL MATCH (person)-[r2:HAS_EDUCATION]->(edu:Education)-[:BELONGS_TO_CV]->(cv)
    OPTIONAL MATCH (person)-[r3:HAS_SKILL]->(skill:Skill)-[:BELONGS_TO_CV]->(cv)
    DELETE r1, r2, r3, exp, edu, skill, person

    // Recreate Person node
    CREATE (person:Person {
        name: $name,
        email: $email,
        phone: $phone,
        address: $address,
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

    // Create Skill nodes
    WITH cv, person
    UNWIND $skills AS skill
    MERGE (s:Skill {name: skill.name})
    ON CREATE SET s.category = skill.category, s.level = skill.level
    CREATE (person)-[:HAS_SKILL]->(s)
    CREATE (s)-[:BELONGS_TO_CV]->(cv)

    RETURN cv.id AS cv_id
    """

    with driver.session(database=database) as session:
        result = session.write_transaction(
            lambda tx: tx.run(
                update_query,
                cv_id=cv_id,
                updated_at=updated_at,
                name=cv_data.get("personal_info", {}).get("name", ""),
                email=cv_data.get("personal_info", {}).get("email"),
                phone=cv_data.get("personal_info", {}).get("phone"),
                address=cv_data.get("personal_info", {}).get("address"),
                linkedin=cv_data.get("personal_info", {}).get("linkedin"),
                github=cv_data.get("personal_info", {}).get("github"),
                website=cv_data.get("personal_info", {}).get("website"),
                summary=cv_data.get("personal_info", {}).get("summary"),
                experiences=cv_data.get("experience", []),
                educations=cv_data.get("education", []),
                skills=cv_data.get("skills", [])
            )
        )
        return result.single() is not None
