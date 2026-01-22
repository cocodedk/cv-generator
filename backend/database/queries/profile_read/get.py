"""Get profile queries - retrieve full profile data."""
from typing import Optional, Dict, Any
from backend.database.connection import Neo4jConnection
from backend.database.queries.profile_helpers import process_profile_record
from backend.database.queries.profile_read.queries import build_full_profile_query


def get_profile() -> Optional[Dict[str, Any]]:
    """Retrieve master profile with all related nodes."""
    driver = Neo4jConnection.get_driver()
    database = Neo4jConnection.get_database()
    match_clause = "MATCH (profile:Profile)"
    query = (
        build_full_profile_query(match_clause)
        + """
    ORDER BY profile.updated_at DESC
    LIMIT 1
    """
    )

    with driver.session(database=database) as session:

        def work(tx):
            result = tx.run(query)
            return result.single()

        record = session.execute_read(work)
        return process_profile_record(record)


def get_profile_by_updated_at(updated_at: str) -> Optional[Dict[str, Any]]:
    """Retrieve a specific profile by its updated_at timestamp."""
    driver = Neo4jConnection.get_driver()
    database = Neo4jConnection.get_database()
    match_clause = "MATCH (profile:Profile { updated_at: $updated_at })"
    query = build_full_profile_query(match_clause)

    with driver.session(database=database) as session:

        def work(tx):
            result = tx.run(query, updated_at=updated_at)
            return result.single()

        record = session.execute_read(work)
        return process_profile_record(record)


def get_profile_by_language(language: str) -> Optional[Dict[str, Any]]:
    """Retrieve the most recent profile with the specified language."""
    driver = Neo4jConnection.get_driver()
    database = Neo4jConnection.get_database()
    match_clause = "MATCH (profile:Profile { language: $language })"
    query = (
        build_full_profile_query(match_clause)
        + """
    ORDER BY profile.updated_at DESC
    LIMIT 1
    """
    )

    with driver.session(database=database) as session:

        def work(tx):
            result = tx.run(query, language=language)
            return result.single()

        record = session.execute_read(work)
        return process_profile_record(record)
