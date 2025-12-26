"""Skill node creation for CV update."""


def create_skill_nodes(tx, cv_id: str, skills: list):
    """Create Skill nodes and link to Person and CV."""
    if not skills:
        return
    query = """
    MATCH (cv:CV {id: $cv_id})
    MATCH (person:Person)-[:BELONGS_TO_CV]->(cv)
    UNWIND $skills AS skill
    CREATE (s:Skill {
        name: skill.name,
        category: skill.category,
        level: skill.level
    })
    CREATE (person)-[:HAS_SKILL]->(s)
    CREATE (s)-[:BELONGS_TO_CV]->(cv)
    """
    result = tx.run(query, cv_id=cv_id, skills=skills)
    result.consume()
