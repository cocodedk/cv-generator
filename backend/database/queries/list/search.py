"""Search CVs by skills, experience, or education."""
from typing import Optional, List, Dict, Any
from backend.database.connection import Neo4jConnection


def search_cvs(
    skills: Optional[List[str]] = None,
    experience_keywords: Optional[List[str]] = None,
    education_keywords: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """Search CVs by skills, experience, or education."""
    driver = Neo4jConnection.get_driver()

    conditions = []
    params = {}

    if skills:
        conditions.append("skill.name IN $skills")
        params["skills"] = skills

    if experience_keywords:
        conditions.append(
            "(exp.title CONTAINS $exp_keyword OR exp.company CONTAINS $exp_keyword)"
        )
        params["exp_keyword"] = experience_keywords[0]  # Simplified for now

    if education_keywords:
        conditions.append(
            "(edu.degree CONTAINS $edu_keyword OR edu.institution CONTAINS $edu_keyword)"
        )
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
        # Convert to list to consume all results before session closes
        cvs = [
            {
                "cv_id": record["cv"]["id"],
                "created_at": record["cv"]["created_at"],
                "person_name": record["person_name"],
            }
            for record in results
        ]
        return cvs
