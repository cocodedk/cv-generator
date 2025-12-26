"""Check profile data in database.

This script checks the state of profile data in the Neo4j database.
It examines Profile nodes, Person nodes, GET_QUERY results, and relationships.

Usage:
    docker-compose exec app python backend/scripts/check_profile_db.py
"""
import sys

# Add app directory to path (Docker container has /app as working directory)
sys.path.insert(0, '/app')

from backend.database.connection import Neo4jConnection
from backend.database.queries.profile_queries import GET_QUERY
from backend.scripts.check_profile_db import (
    check_profile_nodes,
    check_person_nodes,
    check_get_query_result,
    check_relationships,
)


def check_profiles():
    """Check what profiles exist in the database."""
    driver = Neo4jConnection.get_driver()
    database = Neo4jConnection.get_database()

    with driver.session(database=database) as session:
        profiles = check_profile_nodes(session)

        if not profiles:
            return

        check_person_nodes(session, profiles)
        check_get_query_result(session, GET_QUERY)
        check_relationships(session, profiles)


if __name__ == "__main__":
    try:
        check_profiles()
    finally:
        Neo4jConnection.close()
