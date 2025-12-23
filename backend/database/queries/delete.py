"""Delete CV queries."""
from backend.database.connection import Neo4jConnection


def delete_cv(cv_id: str) -> bool:
    """Delete CV and all related nodes."""
    driver = Neo4jConnection.get_driver()

    query = """
    MATCH (cv:CV {id: $cv_id})
    OPTIONAL MATCH (person:Person)-[:BELONGS_TO_CV]->(cv)
    OPTIONAL MATCH (person)-[r1:HAS_EXPERIENCE]->(exp:Experience)-[:BELONGS_TO_CV]->(cv)
    OPTIONAL MATCH (person)-[r2:HAS_EDUCATION]->(edu:Education)-[:BELONGS_TO_CV]->(cv)
    OPTIONAL MATCH (person)-[r3:HAS_SKILL]->(skill:Skill)-[:BELONGS_TO_CV]->(cv)
    DELETE r1, r2, r3, exp, edu, skill, person, cv
    RETURN count(cv) AS deleted
    """

    database = Neo4jConnection.get_database()
    with driver.session(database=database) as session:
        result = session.write_transaction(lambda tx: tx.run(query, cv_id=cv_id))
        deleted = result.single()["deleted"]
        return deleted > 0
