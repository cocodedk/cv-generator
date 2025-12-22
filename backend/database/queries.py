"""Cypher queries for CV operations."""
from typing import Optional, List, Dict, Any
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

    database = Neo4jConnection.get_database()
    with driver.session(database=database) as session:
        result = session.write_transaction(
            lambda tx: tx.run(
                query,
                cv_id=cv_id,
                created_at=created_at,
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
        return result.single()["cv_id"]


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

        return {
            "cv_id": record["cv"]["id"],
            "created_at": record["cv"]["created_at"],
            "updated_at": record["cv"]["updated_at"],
            "personal_info": {
                "name": person.get("name"),
                "email": person.get("email"),
                "phone": person.get("phone"),
                "address": person.get("address"),
                "linkedin": person.get("linkedin"),
                "github": person.get("github"),
                "website": person.get("website"),
                "summary": person.get("summary")
            },
            "experience": experiences,
            "education": educations,
            "skills": skills
        }


def list_cvs(limit: int = 50, offset: int = 0, search: Optional[str] = None) -> Dict[str, Any]:
    """List all CVs with pagination."""
    driver = Neo4jConnection.get_driver()

    if search:
        query = """
        MATCH (cv:CV)
        OPTIONAL MATCH (person:Person)-[:BELONGS_TO_CV]->(cv)
        WHERE person.name CONTAINS $search
           OR person.email CONTAINS $search
        RETURN cv, person.name AS person_name
        ORDER BY cv.created_at DESC
        SKIP $offset
        LIMIT $limit
        """
        count_query = """
        MATCH (cv:CV)
        OPTIONAL MATCH (person:Person)-[:BELONGS_TO_CV]->(cv)
        WHERE person.name CONTAINS $search
           OR person.email CONTAINS $search
        RETURN count(cv) AS total
        """
    else:
        query = """
        MATCH (cv:CV)
        OPTIONAL MATCH (person:Person)-[:BELONGS_TO_CV]->(cv)
        RETURN cv, person.name AS person_name
        ORDER BY cv.created_at DESC
        SKIP $offset
        LIMIT $limit
        """
        count_query = "MATCH (cv:CV) RETURN count(cv) AS total"

    database = Neo4jConnection.get_database()
    with driver.session(database=database) as session:
        if search:
            count_result = session.run(count_query, search=search)
            results = session.run(query, search=search, offset=offset, limit=limit)
        else:
            count_result = session.run(count_query)
            results = session.run(query, offset=offset, limit=limit)

        total = count_result.single()["total"]
        cvs = [
            {
                "cv_id": record["cv"]["id"],
                "created_at": record["cv"]["created_at"],
                "updated_at": record["cv"]["updated_at"],
                "person_name": record["person_name"]
            }
            for record in results
        ]

        return {"cvs": cvs, "total": total}


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


def delete_cv(cv_id: str) -> bool:
    """Delete CV and all related nodes."""
    driver = Neo4jConnection.get_driver()

    query = """
    MATCH (cv:CV {id: $cv_id})
    OPTIONAL MATCH (person:Person)-[:BELONGS_TO_CV]->(cv)
    OPTIONAL MATCH (person)-[r1:HAS_EXPERIENCE]->(exp:Experience)-[:BELONGS_TO_CV]->(cv)
    OPTIONAL MATCH (person)-[r2:HAS_EDUCATION]->(edu:Education)-[:BELONGS_TO_CV]->(cv)
    OPTIONAL MATCH (person)-[r3:HAS_SKILL]->(skill:Skill)-[:BELONGS_TO_CV]->(cv)
    DELETE r1, r2, r3, exp, edu, skill, person, cv
    RETURN count(cv) AS deleted
    """

    database = Neo4jConnection.get_database()
    with driver.session(database=database) as session:
        result = session.write_transaction(
            lambda tx: tx.run(query, cv_id=cv_id)
        )
        deleted = result.single()["deleted"]
        return deleted > 0


def search_cvs(skills: Optional[List[str]] = None,
                experience_keywords: Optional[List[str]] = None,
                education_keywords: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """Search CVs by skills, experience, or education."""
    driver = Neo4jConnection.get_driver()

    conditions = []
    params = {}

    if skills:
        conditions.append("skill.name IN $skills")
        params["skills"] = skills

    if experience_keywords:
        conditions.append("(exp.title CONTAINS $exp_keyword OR exp.company CONTAINS $exp_keyword)")
        params["exp_keyword"] = experience_keywords[0]  # Simplified for now

    if education_keywords:
        conditions.append("(edu.degree CONTAINS $edu_keyword OR edu.institution CONTAINS $edu_keyword)")
        params["edu_keyword"] = education_keywords[0]  # Simplified for now

    if not conditions:
        return []

    where_clause = "WHERE " + " OR ".join(conditions)

    query = f"""
    MATCH (cv:CV)
    OPTIONAL MATCH (person:Person)-[:BELONGS_TO_CV]->(cv)
    OPTIONAL MATCH (person)-[:HAS_SKILL]->(skill:Skill)-[:BELONGS_TO_CV]->(cv)
    OPTIONAL MATCH (person)-[:HAS_EXPERIENCE]->(exp:Experience)-[:BELONGS_TO_CV]->(cv)
    OPTIONAL MATCH (person)-[:HAS_EDUCATION]->(edu:Education)-[:BELONGS_TO_CV]->(cv)
    {where_clause}
    RETURN DISTINCT cv, person.name AS person_name
    ORDER BY cv.created_at DESC
    """

    database = Neo4jConnection.get_database()
    with driver.session(database=database) as session:
        results = session.run(query, **params)
        return [
            {
                "cv_id": record["cv"]["id"],
                "created_at": record["cv"]["created_at"],
                "person_name": record["person_name"]
            }
            for record in results
        ]
