"""Main update profile function."""
from typing import Dict, Any
from datetime import datetime
from backend.database.connection import Neo4jConnection
from backend.database.queries.profile_helpers import build_save_params
from backend.database.queries.profile_update.delete import (
    update_profile_timestamp,
    delete_profile_nodes,
)
from backend.database.queries.profile_update.person import create_person_node
from backend.database.queries.profile_update.experience import create_experience_nodes
from backend.database.queries.profile_update.education import create_education_nodes
from backend.database.queries.profile_update.skill import create_skill_nodes


def update_profile(profile_data: Dict[str, Any]) -> bool:
    """Update existing master profile in Neo4j."""
    driver = Neo4jConnection.get_driver()
    database = Neo4jConnection.get_database()
    updated_at = datetime.utcnow().isoformat()
    params = build_save_params(profile_data, updated_at)

    with driver.session(database=database) as session:

        def work(tx):
            # Update Profile timestamp
            update_profile_timestamp(tx, updated_at)

            # Delete old nodes
            delete_profile_nodes(tx, updated_at)

            # Create new Person node
            create_person_node(tx, updated_at, params)

            # Create Experience nodes with Projects
            create_experience_nodes(tx, updated_at, params.get("experiences", []))

            # Create Education nodes
            create_education_nodes(tx, updated_at, params.get("educations", []))

            # Create Skill nodes
            create_skill_nodes(tx, updated_at, params.get("skills", []))

            # Verify profile was updated
            verify_query = "MATCH (profile:Profile { updated_at: $updated_at }) RETURN profile"
            result = tx.run(verify_query, updated_at=updated_at)
            return result.single() is not None

        return session.execute_write(work)
