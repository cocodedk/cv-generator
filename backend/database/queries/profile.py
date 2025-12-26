"""Profile queries for master profile management."""
from typing import Optional, Dict, Any
from datetime import datetime
from backend.database.connection import Neo4jConnection
from backend.database.queries.profile_queries import (
    CREATE_QUERY,
    UPDATE_QUERY,
    GET_QUERY,
    DELETE_QUERY,
    DELETE_PROFILE_BY_UPDATED_AT_QUERY,
    LIST_PROFILES_QUERY,
    GET_PROFILE_BY_UPDATED_AT_QUERY,
)
from backend.database.queries.profile_helpers import (
    build_save_params,
    process_profile_record,
)


def _check_profile_exists(tx) -> bool:
    """Check if a Profile node exists."""
    query = "MATCH (profile:Profile) RETURN profile LIMIT 1"
    result = tx.run(query)
    return result.single() is not None


def create_profile(profile_data: Dict[str, Any]) -> bool:
    """Create a new master profile in Neo4j."""
    driver = Neo4jConnection.get_driver()
    database = Neo4jConnection.get_database()
    params = build_save_params(profile_data, datetime.utcnow().isoformat())
    with driver.session(database=database) as session:

        def work(tx):
            result = tx.run(CREATE_QUERY, **params)
            return result.single() is not None

        return session.execute_write(work)


def update_profile(profile_data: Dict[str, Any]) -> bool:
    """Update existing master profile in Neo4j."""
    driver = Neo4jConnection.get_driver()
    database = Neo4jConnection.get_database()
    params = build_save_params(profile_data, datetime.utcnow().isoformat())
    with driver.session(database=database) as session:

        def work(tx):
            result = tx.run(UPDATE_QUERY, **params)
            return result.single() is not None

        return session.execute_write(work)


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
    """Delete master profile and all related nodes."""
    driver = Neo4jConnection.get_driver()
    database = Neo4jConnection.get_database()
    with driver.session(database=database) as session:

        def work(tx):
            result = tx.run(DELETE_QUERY)
            record = result.single()
            return record and record.get("deleted", 0) > 0

        return session.execute_write(work)
