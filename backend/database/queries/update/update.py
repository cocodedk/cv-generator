"""Main update CV function."""
from typing import Dict, Any
from datetime import datetime
from backend.database.connection import Neo4jConnection
from backend.database.queries.update.delete import (
    update_cv_timestamp,
    delete_cv_relationships,
)
from backend.database.queries.update.person import create_person_node
from backend.database.queries.update.experience import create_experience_nodes
from backend.database.queries.update.education import create_education_nodes
from backend.database.queries.update.skill import create_skill_nodes


def update_cv(cv_id: str, cv_data: Dict[str, Any]) -> bool:
    """Update CV data."""
    driver = Neo4jConnection.get_driver()
    database = Neo4jConnection.get_database()
    updated_at = datetime.utcnow().isoformat()
    personal_info = cv_data.get("personal_info", {})
    theme = cv_data.get("theme", "classic")
    layout = cv_data.get("layout", "classic-two-column")
    target_company = cv_data.get("target_company")
    target_role = cv_data.get("target_role")

    with driver.session(database=database) as session:

        def work(tx):
            update_cv_timestamp(tx, cv_id, updated_at, theme, layout, target_company, target_role)
            delete_cv_relationships(tx, cv_id)
            create_person_node(tx, cv_id, personal_info)
            create_experience_nodes(tx, cv_id, cv_data.get("experience", []))
            create_education_nodes(tx, cv_id, cv_data.get("education", []))
            create_skill_nodes(tx, cv_id, cv_data.get("skills", []))

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
