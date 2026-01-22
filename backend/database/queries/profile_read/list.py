"""List profile queries - retrieve basic profile information."""
from typing import Dict, Any
from backend.database.connection import Neo4jConnection


def list_profiles() -> list[Dict[str, Any]]:
    """List all profiles with basic info (name, updated_at).

    Returns one row per Profile node, aggregating Person nodes to avoid duplicates
    when multiple Person nodes are connected to the same Profile.
    """
    driver = Neo4jConnection.get_driver()
    database = Neo4jConnection.get_database()
    query = """
    MATCH (profile:Profile)
    OPTIONAL MATCH (person:Person)-[:BELONGS_TO_PROFILE]->(profile)
    WITH profile, collect(DISTINCT person.name)[0] AS person_name
    RETURN profile.updated_at AS updated_at, COALESCE(person_name, 'Unknown') AS name, COALESCE(profile.language, 'en') AS language
    ORDER BY profile.updated_at DESC
    """

    with driver.session(database=database) as session:

        def work(tx):
            result = tx.run(query)
            profiles = []
            for record in result:
                profiles.append(
                    {
                        "name": record.get("name", "Unknown"),
                        "updated_at": record.get("updated_at"),
                        "language": record.get("language", "en"),
                    }
                )
            return profiles

        return session.execute_read(work)
