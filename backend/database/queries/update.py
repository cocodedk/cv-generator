"""Update CV queries."""
from typing import Dict, Any
from datetime import datetime
from backend.database.connection import Neo4jConnection


def _update_cv_timestamp(
    tx, cv_id: str, updated_at: str, theme: str = "classic"
) -> None:
    """Update CV timestamp and theme."""
    query = """
    MATCH (cv:CV {id: $cv_id})
    SET cv.updated_at = $updated_at,
        cv.theme = $theme
    """
    tx.run(query, cv_id=cv_id, updated_at=updated_at, theme=theme)


def _delete_cv_relationships(tx, cv_id: str) -> None:
    """Delete existing relationships and nodes for a CV."""
    query = """
    MATCH (cv:CV {id: $cv_id})
    OPTIONAL MATCH (old_person:Person)-[:BELONGS_TO_CV]->(cv)
    OPTIONAL MATCH (old_person)-[:HAS_EXPERIENCE]->(exp:Experience)-[:BELONGS_TO_CV]->(cv)
    OPTIONAL MATCH (exp)-[:HAS_PROJECT]->(proj:Project)-[:BELONGS_TO_CV]->(cv)
    OPTIONAL MATCH (old_person)-[:HAS_EDUCATION]->(edu:Education)-[:BELONGS_TO_CV]->(cv)
    OPTIONAL MATCH (old_person)-[:HAS_SKILL]->(skill:Skill)-[:BELONGS_TO_CV]->(cv)
    DETACH DELETE proj, exp, edu, skill, old_person
    """
    tx.run(query, cv_id=cv_id)


def _create_person_node(tx, cv_id: str, personal_info: Dict[str, Any]) -> None:
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
        summary: $summary
    })
    CREATE (person)-[:BELONGS_TO_CV]->(cv)
    """
    tx.run(
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
    )


def _create_experience_nodes(tx, cv_id: str, experiences: list) -> None:
    """Create Experience nodes and link to Person and CV."""
    if not experiences:
        return
    query = """
    MATCH (cv:CV {id: $cv_id})
    MATCH (person:Person)-[:BELONGS_TO_CV]->(cv)
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
    WITH cv, experience, exp
    UNWIND COALESCE(exp.projects, []) AS proj
    CREATE (project:Project {
        name: proj.name,
        description: proj.description,
        url: proj.url,
        technologies: COALESCE(proj.technologies, []),
        highlights: COALESCE(proj.highlights, [])
    })
    CREATE (experience)-[:HAS_PROJECT]->(project)
    CREATE (project)-[:BELONGS_TO_CV]->(cv)
    """
    tx.run(query, cv_id=cv_id, experiences=experiences)


def _create_education_nodes(tx, cv_id: str, educations: list) -> None:
    """Create Education nodes and link to Person and CV."""
    if not educations:
        return
    query = """
    MATCH (cv:CV {id: $cv_id})
    MATCH (person:Person)-[:BELONGS_TO_CV]->(cv)
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
    """
    tx.run(query, cv_id=cv_id, educations=educations)


def _create_skill_nodes(tx, cv_id: str, skills: list) -> None:
    """Create Skill nodes and link to Person and CV."""
    if not skills:
        return
    query = """
    MATCH (cv:CV {id: $cv_id})
    MATCH (person:Person)-[:BELONGS_TO_CV]->(cv)
    UNWIND $skills AS skill
    CREATE (s:Skill {
        name: skill.name,
        category: skill.category,
        level: skill.level
    })
    CREATE (person)-[:HAS_SKILL]->(s)
    CREATE (s)-[:BELONGS_TO_CV]->(cv)
    """
    tx.run(query, cv_id=cv_id, skills=skills)


def update_cv(cv_id: str, cv_data: Dict[str, Any]) -> bool:
    """Update CV data."""
    driver = Neo4jConnection.get_driver()
    database = Neo4jConnection.get_database()
    updated_at = datetime.utcnow().isoformat()
    personal_info = cv_data.get("personal_info", {})
    theme = cv_data.get("theme", "classic")

    with driver.session(database=database) as session:

        def work(tx):
            _update_cv_timestamp(tx, cv_id, updated_at, theme)
            _delete_cv_relationships(tx, cv_id)
            _create_person_node(tx, cv_id, personal_info)
            _create_experience_nodes(tx, cv_id, cv_data.get("experience", []))
            _create_education_nodes(tx, cv_id, cv_data.get("education", []))
            _create_skill_nodes(tx, cv_id, cv_data.get("skills", []))

            # Verify CV exists
            verify_query = "MATCH (cv:CV {id: $cv_id}) RETURN cv.id AS cv_id"
            result = tx.run(verify_query, cv_id=cv_id)
            record = result.single()
            return record is not None

        return session.execute_write(work)


def set_cv_filename(cv_id: str, filename: str) -> bool:
    """Set generated filename for a CV."""
    driver = Neo4jConnection.get_driver()
    database = Neo4jConnection.get_database()

    query = """
    MATCH (cv:CV {id: $cv_id})
    SET cv.filename = $filename,
        cv.updated_at = $updated_at
    RETURN cv.id AS cv_id
    """

    with driver.session(database=database) as session:

        def work(tx):
            result = tx.run(
                query,
                cv_id=cv_id,
                filename=filename,
                updated_at=datetime.utcnow().isoformat(),
            )
            record = result.single()
            return record is not None

        return session.execute_write(work)
