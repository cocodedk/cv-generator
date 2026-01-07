"""Get cover letter queries - retrieve cover letter data."""
from typing import Optional, Dict, Any
from backend.database.connection import Neo4jConnection


def get_cover_letter_by_id(cover_letter_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve cover letter by ID."""
    driver = Neo4jConnection.get_driver()
    database = Neo4jConnection.get_database()

    query = """
    MATCH (cl:CoverLetter {id: $cover_letter_id})
    RETURN cl
    """

    with driver.session(database=database) as session:
        result = session.run(query, cover_letter_id=cover_letter_id)
        record = result.single()

        if record:
            cl = record["cl"]
            return {
                "cover_letter_id": cl["id"],
                "created_at": cl["created_at"],
                "updated_at": cl["updated_at"],
                "job_description": cl["job_description"],
                "company_name": cl["company_name"],
                "hiring_manager_name": cl.get("hiring_manager_name"),
                "company_address": cl.get("company_address"),
                "tone": cl["tone"],
                "cover_letter_html": cl.get("cover_letter_html"),
                "cover_letter_text": cl.get("cover_letter_text"),
                "highlights_used": cl.get("highlights_used", []),
                "selected_experiences": cl.get("selected_experiences", []),
                "selected_skills": cl.get("selected_skills", []),
            }

        return None
