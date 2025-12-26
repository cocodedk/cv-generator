"""Profile queries for master profile management."""
from typing import Optional, Dict, Any
from backend.database.connection import Neo4jConnection
from backend.database.queries.profile_queries import (
    GET_QUERY,
    DELETE_LATEST_QUERY,
    DELETE_PROFILE_BY_UPDATED_AT_QUERY,
    LIST_PROFILES_QUERY,
    GET_PROFILE_BY_UPDATED_AT_QUERY,
)
from backend.database.queries.profile_helpers import (
    process_profile_record,
)


def _check_profile_exists(tx) -> bool:
    """Check if a Profile node exists."""
    query = "MATCH (profile:Profile) RETURN profile LIMIT 1"
    result = tx.run(query)
    return result.single() is not None


def create_profile(profile_data: Dict[str, Any]) -> bool:
    """Create a new master profile in Neo4j."""
    # Use the fixed create_profile from profile_create module
    from backend.database.queries.profile_create.create import create_profile as create_profile_fixed
    return create_profile_fixed(profile_data)


def update_profile(profile_data: Dict[str, Any]) -> bool:
    """Update existing master profile in Neo4j."""
    # Use the fixed update_profile from profile_update module
    from backend.database.queries.profile_update.update import update_profile as update_profile_fixed
    return update_profile_fixed(profile_data)


def save_profile(profile_data: Dict[str, Any]) -> bool:
    """Save or update master profile in Neo4j.

    Checks if profile exists and calls update_profile() or create_profile() accordingly.
    This ensures the Profile node is never deleted during save operations.
    """
    driver = Neo4jConnection.get_driver()
    database = Neo4jConnection.get_database()

    with driver.session(database=database) as session:
        # Check if profile exists in a read transaction
        def check_work(tx):
            return _check_profile_exists(tx)

        profile_exists = session.execute_read(check_work)

    # Call appropriate method based on existence
    if profile_exists:
        return update_profile(profile_data)
    else:
        return create_profile(profile_data)


def get_profile() -> Optional[Dict[str, Any]]:
    """Retrieve master profile with all related nodes."""
    driver = Neo4jConnection.get_driver()
    database = Neo4jConnection.get_database()
    with driver.session(database=database) as session:

        def work(tx):
            result = tx.run(GET_QUERY)
            return result.single()

        record = session.execute_read(work)
        return process_profile_record(record)


def list_profiles() -> list[Dict[str, Any]]:
    """List all profiles with basic info (name, updated_at)."""
    driver = Neo4jConnection.get_driver()
    database = Neo4jConnection.get_database()
    with driver.session(database=database) as session:

        def work(tx):
            result = tx.run(LIST_PROFILES_QUERY)
            profiles = []
            for record in result:
                profiles.append({
                    "name": record.get("name", "Unknown"),
                    "updated_at": record.get("updated_at"),
                })
            return profiles

        return session.execute_read(work)


def get_profile_by_updated_at(updated_at: str) -> Optional[Dict[str, Any]]:
    """Retrieve a specific profile by its updated_at timestamp."""
    driver = Neo4jConnection.get_driver()
    database = Neo4jConnection.get_database()
    with driver.session(database=database) as session:

        def work(tx):
            result = tx.run(GET_PROFILE_BY_UPDATED_AT_QUERY, updated_at=updated_at)
            return result.single()

        record = session.execute_read(work)
        return process_profile_record(record)


def delete_profile_by_updated_at(updated_at: str) -> bool:
    """Delete a specific profile by its updated_at timestamp."""
    driver = Neo4jConnection.get_driver()
    database = Neo4jConnection.get_database()
    with driver.session(database=database) as session:

        def work(tx):
            result = tx.run(DELETE_PROFILE_BY_UPDATED_AT_QUERY, updated_at=updated_at)
            record = result.single()
            return record and record.get("deleted", 0) > 0

        return session.execute_write(work)


def delete_profile() -> bool:
    """Delete the most recently updated profile and all related nodes."""
    driver = Neo4jConnection.get_driver()
    database = Neo4jConnection.get_database()
    with driver.session(database=database) as session:

        def work(tx):
            result = tx.run(DELETE_LATEST_QUERY)
            record = result.single()
            return record and record.get("deleted", 0) > 0

        return session.execute_write(work)
