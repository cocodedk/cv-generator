"""Delete CV queries."""
from backend.database.connection import Neo4jConnection


def delete_cv(cv_id: str) -> bool:
    """Delete CV and all related nodes."""
    driver = Neo4jConnection.get_driver()

    query = """
    MATCH (cv:CV {id: $cv_id})
    OPTIONAL MATCH (person:Person)-[:BELONGS_TO_CV]->(cv)
    OPTIONAL MATCH (person)-[:HAS_EXPERIENCE]->(exp:Experience)-[:BELONGS_TO_CV]->(cv)
    OPTIONAL MATCH (exp)-[:HAS_PROJECT]->(proj:Project)-[:BELONGS_TO_CV]->(cv)
    OPTIONAL MATCH (person)-[:HAS_EDUCATION]->(edu:Education)-[:BELONGS_TO_CV]->(cv)
    OPTIONAL MATCH (person)-[:HAS_SKILL]->(skill:Skill)-[:BELONGS_TO_CV]->(cv)
    DETACH DELETE proj, exp, edu, skill, person, cv
    RETURN count(cv) AS deleted
    """

    database = Neo4jConnection.get_database()
    with driver.session(database=database) as session:

        def work(tx):
            result = tx.run(query, cv_id=cv_id)
            record = result.single()
            deleted = record["deleted"] if record else 0
            return deleted > 0

        return session.execute_write(work)


def delete_cover_letter(cover_letter_id: str) -> bool:
    """Delete cover letter."""
    driver = Neo4jConnection.get_driver()

    query = """
    MATCH (cl:CoverLetter {id: $cover_letter_id})
    DELETE cl
    RETURN count(cl) AS deleted
    """

    database = Neo4jConnection.get_database()
    with driver.session(database=database) as session:

        def work(tx):
            result = tx.run(query, cover_letter_id=cover_letter_id)
            record = result.single()
            deleted = record["deleted"] if record else 0
            return deleted > 0

        return session.execute_write(work)
