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
        WHERE person.name CONTAINS $search
           OR person.email CONTAINS $search
        RETURN cv, person.name AS person_name, cv.filename AS filename
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
        RETURN cv, person.name AS person_name, cv.filename AS filename
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
            }
            for record in results
        ]

        return {"cvs": cvs, "total": total}
