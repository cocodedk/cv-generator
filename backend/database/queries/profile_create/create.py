"""Main create profile function."""
from typing import Dict, Any
from datetime import datetime
from backend.database.connection import Neo4jConnection
from backend.database.queries.profile_helpers import build_save_params
from backend.database.queries.profile_create.profile import create_profile_node
from backend.database.queries.profile_create.person import create_person_node
from backend.database.queries.profile_create.experience import create_experience_nodes
from backend.database.queries.profile_create.education import create_education_nodes
from backend.database.queries.profile_create.skill import create_skill_nodes


def create_profile(profile_data: Dict[str, Any]) -> bool:
    """Create a new master profile in Neo4j."""
    driver = Neo4jConnection.get_driver()
    database = Neo4jConnection.get_database()
    updated_at = datetime.utcnow().isoformat()
    params = build_save_params(profile_data, updated_at)

    with driver.session(database=database) as session:

        def work(tx):
            # Create Profile node
            create_profile_node(tx, updated_at)

            # Create Person node
            create_person_node(tx, updated_at, params)

            # Create Experience nodes with Projects
            create_experience_nodes(tx, updated_at, params.get("experiences", []))

            # Create Education nodes
            create_education_nodes(tx, updated_at, params.get("educations", []))

            # Create Skill nodes
            create_skill_nodes(tx, updated_at, params.get("skills", []))

            # Verify profile was created
            verify_query = "MATCH (profile:Profile { updated_at: $updated_at }) RETURN profile"
            result = tx.run(verify_query, updated_at=updated_at)
            return result.single() is not None

        return session.execute_write(work)
