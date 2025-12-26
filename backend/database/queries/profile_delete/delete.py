"""Delete profile queries - deletion operations."""
from backend.database.connection import Neo4jConnection


def _delete_profile_nodes_by_timestamp(tx, updated_at: str):
    """Delete all nodes for a specific profile by timestamp."""
    query = """
    MATCH (profile:Profile { updated_at: $updated_at })
    OPTIONAL MATCH (person:Person)-[:BELONGS_TO_PROFILE]->(profile)
    OPTIONAL MATCH (person)-[:HAS_EXPERIENCE]->(exp:Experience)-[:BELONGS_TO_PROFILE]->(profile)
    OPTIONAL MATCH (exp)-[:HAS_PROJECT]->(proj:Project)-[:BELONGS_TO_PROFILE]->(profile)
    OPTIONAL MATCH (person)-[:HAS_EDUCATION]->(edu:Education)-[:BELONGS_TO_PROFILE]->(profile)
    OPTIONAL MATCH (person)-[:HAS_SKILL]->(skill:Skill)-[:BELONGS_TO_PROFILE]->(profile)
    WITH [p IN collect(DISTINCT profile) WHERE p IS NOT NULL] AS profiles,
         [p IN collect(DISTINCT person) WHERE p IS NOT NULL] AS persons,
         [e IN collect(DISTINCT exp) WHERE e IS NOT NULL] AS experiences,
         [p IN collect(DISTINCT proj) WHERE p IS NOT NULL] AS projects,
         [e IN collect(DISTINCT edu) WHERE e IS NOT NULL] AS educations,
         [s IN collect(DISTINCT skill) WHERE s IS NOT NULL] AS skills
    FOREACH (p IN profiles | DETACH DELETE p)
    FOREACH (p IN persons | DETACH DELETE p)
    FOREACH (p IN projects | DETACH DELETE p)
    FOREACH (e IN experiences | DETACH DELETE e)
    FOREACH (e IN educations | DETACH DELETE e)
    FOREACH (s IN skills | DETACH DELETE s)
    RETURN size(profiles) AS deleted
    """
    result = tx.run(query, updated_at=updated_at)
    record = result.single()
    return record and record.get("deleted", 0) > 0


def _delete_all_profile_nodes(tx):
    """Delete all profile nodes."""
    query = """
    OPTIONAL MATCH (profile:Profile)
    OPTIONAL MATCH (person:Person)-[:BELONGS_TO_PROFILE]->(profile)
    OPTIONAL MATCH (person)-[:HAS_EXPERIENCE]->(exp:Experience)-[:BELONGS_TO_PROFILE]->(profile)
    OPTIONAL MATCH (exp)-[:HAS_PROJECT]->(proj:Project)-[:BELONGS_TO_PROFILE]->(profile)
    OPTIONAL MATCH (person)-[:HAS_EDUCATION]->(edu:Education)-[:BELONGS_TO_PROFILE]->(profile)
    OPTIONAL MATCH (person)-[:HAS_SKILL]->(skill:Skill)-[:BELONGS_TO_PROFILE]->(profile)
    WITH [p IN collect(DISTINCT profile) WHERE p IS NOT NULL] AS profiles,
         [p IN collect(DISTINCT person) WHERE p IS NOT NULL] AS persons,
         [e IN collect(DISTINCT exp) WHERE e IS NOT NULL] AS experiences,
         [p IN collect(DISTINCT proj) WHERE p IS NOT NULL] AS projects,
         [e IN collect(DISTINCT edu) WHERE e IS NOT NULL] AS educations,
         [s IN collect(DISTINCT skill) WHERE s IS NOT NULL] AS skills
    FOREACH (p IN profiles | DETACH DELETE p)
    FOREACH (p IN persons | DETACH DELETE p)
    FOREACH (p IN projects | DETACH DELETE p)
    FOREACH (e IN experiences | DETACH DELETE e)
    FOREACH (e IN educations | DETACH DELETE e)
    FOREACH (s IN skills | DETACH DELETE s)
    RETURN size(profiles) AS deleted
    """
    result = tx.run(query)
    record = result.single()
    return record and record.get("deleted", 0) > 0


def delete_profile() -> bool:
    """Delete master profile and all related nodes."""
    driver = Neo4jConnection.get_driver()
    database = Neo4jConnection.get_database()

    with driver.session(database=database) as session:

        def work(tx):
            return _delete_all_profile_nodes(tx)

        return session.execute_write(work)


def delete_profile_by_updated_at(updated_at: str) -> bool:
    """Delete a specific profile by its updated_at timestamp."""
    driver = Neo4jConnection.get_driver()
    database = Neo4jConnection.get_database()

    with driver.session(database=database) as session:

        def work(tx):
            return _delete_profile_nodes_by_timestamp(tx, updated_at)

        return session.execute_write(work)
