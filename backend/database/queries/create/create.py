"""Main create CV function."""
from typing import Dict, Any
from datetime import datetime
from uuid import uuid4
from backend.database.connection import Neo4jConnection
from backend.database.queries.create.cv import create_cv_node
from backend.database.queries.create.person import create_person_node
from backend.database.queries.create.nodes import (
    create_experience_nodes,
    create_education_nodes,
    create_skill_nodes,
)


def create_cv(cv_data: Dict[str, Any]) -> str:
    """Create a CV with all relationships in Neo4j."""
    driver = Neo4jConnection.get_driver()
    database = Neo4jConnection.get_database()
    cv_id = str(uuid4())
    created_at = datetime.utcnow().isoformat()
    personal_info = cv_data.get("personal_info", {})
    theme = cv_data.get("theme", "classic")
    layout = cv_data.get("layout", "classic-two-column")
    target_company = cv_data.get("target_company")
    target_role = cv_data.get("target_role")

    with driver.session(database=database) as session:

        def work(tx):
            # Create CV node
            create_cv_node(tx, cv_id, created_at, theme, layout, target_company, target_role)

            # Create Person node
            create_person_node(tx, cv_id, personal_info)

            # Create Experience nodes with Projects
            create_experience_nodes(tx, cv_id, cv_data.get("experience", []))

            # Create Education nodes
            create_education_nodes(tx, cv_id, cv_data.get("education", []))

            # Create Skill nodes
            create_skill_nodes(tx, cv_id, cv_data.get("skills", []))

            # Return the cv_id (query confirms creation)
            return cv_id

        return session.execute_write(work)
