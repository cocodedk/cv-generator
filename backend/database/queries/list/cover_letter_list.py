"""List cover letters with pagination."""
from typing import Optional, Dict, Any
from backend.database.connection import Neo4jConnection


def list_cover_letters(
    limit: int = 50, offset: int = 0, search: Optional[str] = None
) -> Dict[str, Any]:
    """List all cover letters with pagination."""
    driver = Neo4jConnection.get_driver()

    if search:
        query = """
        MATCH (cl:CoverLetter)
        WHERE cl.company_name CONTAINS $search
           OR cl.job_description CONTAINS $search
        RETURN cl
        ORDER BY cl.created_at DESC
        SKIP $offset
        LIMIT $limit
        """
        count_query = """
        MATCH (cl:CoverLetter)
        WHERE cl.company_name CONTAINS $search
           OR cl.job_description CONTAINS $search
        RETURN count(cl) AS total
        """
    else:
        query = """
        MATCH (cl:CoverLetter)
        RETURN cl
        ORDER BY cl.created_at DESC
        SKIP $offset
        LIMIT $limit
        """
        count_query = "MATCH (cl:CoverLetter) RETURN count(cl) AS total"

    database = Neo4jConnection.get_database()
    with driver.session(database=database) as session:

        def get_count(tx):
            if search:
                count_result = tx.run(count_query, search=search)
            else:
                count_result = tx.run(count_query)
            return count_result.single()["total"]

        def get_results(tx):
            if search:
                results = tx.run(query, search=search, offset=offset, limit=limit)
            else:
                results = tx.run(query, offset=offset, limit=limit)
            return [
                {
                    "cover_letter_id": record["cl"]["id"],
                    "created_at": record["cl"]["created_at"],
                    "updated_at": record["cl"]["updated_at"],
                    "company_name": record["cl"]["company_name"],
                    "hiring_manager_name": record["cl"]["hiring_manager_name"],
                    "tone": record["cl"]["tone"],
                }
                for record in results
            ]

        total = session.execute_read(get_count)
        cover_letters = session.execute_read(get_results)

        return {"cover_letters": cover_letters, "total": total}
