"""Profile queries for master profile management."""
from typing import Optional, Dict, Any
from datetime import datetime
from backend.database.connection import Neo4jConnection


def save_profile(profile_data: Dict[str, Any]) -> bool:
    """Save or update master profile in Neo4j."""
    driver = Neo4jConnection.get_driver()
    database = Neo4jConnection.get_database()
    updated_at = datetime.utcnow().isoformat()

    # Delete existing profile if it exists, then create new one
    query = """
    // Delete existing profile and related nodes
    MATCH (profile:Profile)
    OPTIONAL MATCH (person:Person)-[:BELONGS_TO_PROFILE]->(profile)
    OPTIONAL MATCH (person)-[r1:HAS_EXPERIENCE]->(exp:Experience)-[:BELONGS_TO_PROFILE]->(profile)
    OPTIONAL MATCH (person)-[r2:HAS_EDUCATION]->(edu:Education)-[:BELONGS_TO_PROFILE]->(profile)
    OPTIONAL MATCH (person)-[r3:HAS_SKILL]->(skill:Skill)-[:BELONGS_TO_PROFILE]->(profile)
    DELETE r1, r2, r3, exp, edu, skill, person, profile

    // Create new Profile node
    CREATE (profile:Profile {
        updated_at: $updated_at
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
    CREATE (person)-[:BELONGS_TO_PROFILE]->(profile)

    // Create Experience nodes
    WITH profile, person
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
    CREATE (experience)-[:BELONGS_TO_PROFILE]->(profile)

    // Create Education nodes
    WITH profile, person
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

    // Create Skill nodes
    WITH profile, person
    UNWIND $skills AS skill
    CREATE (s:Skill {
        name: skill.name,
        category: skill.category,
        level: skill.level
    })
    CREATE (person)-[:HAS_SKILL]->(s)
    CREATE (s)-[:BELONGS_TO_PROFILE]->(profile)

    RETURN profile
    """

    personal_info = profile_data.get("personal_info", {})
    address = personal_info.get("address") or {}

    with driver.session(database=database) as session:
        result = session.write_transaction(
            lambda tx: tx.run(
                query,
                updated_at=updated_at,
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
                experiences=profile_data.get("experience", []),
                educations=profile_data.get("education", []),
                skills=profile_data.get("skills", []),
            )
        )
        return result.single() is not None


def get_profile() -> Optional[Dict[str, Any]]:
    """Retrieve master profile with all related nodes."""
    driver = Neo4jConnection.get_driver()
    database = Neo4jConnection.get_database()

    query = """
    MATCH (profile:Profile)
    OPTIONAL MATCH (person:Person)-[:BELONGS_TO_PROFILE]->(profile)
    OPTIONAL MATCH (person)-[:HAS_EXPERIENCE]->(exp:Experience)-[:BELONGS_TO_PROFILE]->(profile)
    OPTIONAL MATCH (person)-[:HAS_EDUCATION]->(edu:Education)-[:BELONGS_TO_PROFILE]->(profile)
    OPTIONAL MATCH (person)-[:HAS_SKILL]->(skill:Skill)-[:BELONGS_TO_PROFILE]->(profile)

    RETURN profile, person,
           collect(DISTINCT exp) AS experiences,
           collect(DISTINCT edu) AS educations,
           collect(DISTINCT skill) AS skills
    """

    with driver.session(database=database) as session:
        result = session.run(query)
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
            "updated_at": record["profile"].get("updated_at"),
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


def delete_profile() -> bool:
    """Delete master profile and all related nodes."""
    driver = Neo4jConnection.get_driver()
    database = Neo4jConnection.get_database()

    query = """
    MATCH (profile:Profile)
    OPTIONAL MATCH (person:Person)-[:BELONGS_TO_PROFILE]->(profile)
    OPTIONAL MATCH (person)-[r1:HAS_EXPERIENCE]->(exp:Experience)-[:BELONGS_TO_PROFILE]->(profile)
    OPTIONAL MATCH (person)-[r2:HAS_EDUCATION]->(edu:Education)-[:BELONGS_TO_PROFILE]->(profile)
    OPTIONAL MATCH (person)-[r3:HAS_SKILL]->(skill:Skill)-[:BELONGS_TO_PROFILE]->(profile)
    DELETE r1, r2, r3, exp, edu, skill, person, profile
    RETURN count(profile) AS deleted
    """

    with driver.session(database=database) as session:
        result = session.write_transaction(lambda tx: tx.run(query))
        deleted = result.single()["deleted"]
        return deleted > 0
