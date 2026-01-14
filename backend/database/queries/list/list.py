"""List CVs with pagination."""
from typing import Optional, Dict, Any
from backend.database.connection import Neo4jConnection


def list_cvs(
    limit: int = 50, offset: int = 0, search: Optional[str] = None
) -> Dict[str, Any]:
    """List all CVs with pagination."""
    driver = Neo4jConnection.get_driver()

    if search:
        query = """
        MATCH (cv:CV)
        OPTIONAL MATCH (person:Person)-[:BELONGS_TO_CV]->(cv)
        WITH cv, person
        WHERE (person.name IS NOT NULL AND person.name CONTAINS $search)
           OR (person.email IS NOT NULL AND person.email CONTAINS $search)
           OR (cv.target_company IS NOT NULL AND cv.target_company CONTAINS $search)
           OR (cv.target_role IS NOT NULL AND cv.target_role CONTAINS $search)
        RETURN cv, person.name AS person_name, cv.filename AS filename,
               cv.target_company AS target_company, cv.target_role AS target_role
        ORDER BY cv.created_at DESC
        SKIP $offset
        LIMIT $limit
        """
        count_query = """
        MATCH (cv:CV)
        OPTIONAL MATCH (person:Person)-[:BELONGS_TO_CV]->(cv)
        WITH cv, person
        WHERE (person.name IS NOT NULL AND person.name CONTAINS $search)
           OR (person.email IS NOT NULL AND person.email CONTAINS $search)
           OR (cv.target_company IS NOT NULL AND cv.target_company CONTAINS $search)
           OR (cv.target_role IS NOT NULL AND cv.target_role CONTAINS $search)
        RETURN count(cv) AS total
        """
    else:
        query = """
        MATCH (cv:CV)
        OPTIONAL MATCH (person:Person)-[:BELONGS_TO_CV]->(cv)
        RETURN cv, person.name AS person_name, cv.filename AS filename,
               cv.target_company AS target_company, cv.target_role AS target_role
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
        # Convert to list to consume all results before session closes
        cvs = [
            {
                "cv_id": record["cv"]["id"],
                "created_at": record["cv"]["created_at"],
                "updated_at": record["cv"]["updated_at"],
                "person_name": record["person_name"],
                "filename": record["filename"],
                "target_company": record.get("target_company"),
                "target_role": record.get("target_role"),
            }
            for record in results
        ]

        return {"cvs": cvs, "total": total}
