"""Main update profile function."""
from typing import Dict, Any
from datetime import datetime
from backend.database.connection import Neo4jConnection
from backend.database.queries.profile_helpers import build_save_params
from backend.database.queries.profile_update.delete import (
    update_profile_timestamp,
    delete_profile_nodes,
    verify_person_deletion,
    verify_single_person,
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

            # Verify deletion succeeded (fail hard)
            verify_person_deletion(tx, updated_at)

            # Create new Person node and capture its elementId
            person_element_id = create_person_node(tx, updated_at, params)

            # Verify exactly one Person exists (optional but good)
            verify_single_person(tx, updated_at)

            # Create Experience nodes bound to the new Person
            create_experience_nodes(tx, updated_at, person_element_id, params.get("experiences", []))

            # Create Education nodes bound to the new Person
            create_education_nodes(tx, updated_at, person_element_id, params.get("educations", []))

            # Create Skill nodes bound to the new Person
            create_skill_nodes(tx, updated_at, person_element_id, params.get("skills", []))

            # Verify profile was updated
            verify_query = "MATCH (profile:Profile { updated_at: $updated_at }) RETURN profile"
            result = tx.run(verify_query, updated_at=updated_at)
            profile_exists = result.single() is not None
            return profile_exists

        result = session.execute_write(work)
        return result
