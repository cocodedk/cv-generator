"""Profile queries for master profile management."""
from typing import Optional, Dict, Any
from datetime import datetime
from backend.database.connection import Neo4jConnection
from backend.database.queries.profile_queries import (
    CREATE_QUERY,
    GET_QUERY,
    DELETE_QUERY,
)
from backend.database.queries.profile_helpers import (
    build_save_params,
    process_profile_record,
)


def save_profile(profile_data: Dict[str, Any]) -> bool:
    """Save or update master profile in Neo4j."""
    driver = Neo4jConnection.get_driver()
    database = Neo4jConnection.get_database()
    params = build_save_params(profile_data, datetime.utcnow().isoformat())
    with driver.session(database=database) as session:

        def work(tx):
            result = tx.run(CREATE_QUERY, **params)
            return result.single() is not None

        return session.write_transaction(work)


def get_profile() -> Optional[Dict[str, Any]]:
    """Retrieve master profile with all related nodes."""
    driver = Neo4jConnection.get_driver()
    database = Neo4jConnection.get_database()
    with driver.session(database=database) as session:
        return process_profile_record(session.run(GET_QUERY).single())


def delete_profile() -> bool:
    """Delete master profile and all related nodes."""
    driver = Neo4jConnection.get_driver()
    database = Neo4jConnection.get_database()
    with driver.session(database=database) as session:

        def work(tx):
            result = tx.run(DELETE_QUERY)
            record = result.single()
            return record and record.get("deleted", 0) > 0

        return session.write_transaction(work)
