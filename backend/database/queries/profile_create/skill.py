"""Skill node creation."""


def create_skill_nodes(tx, updated_at: str, skills: list):
    """Create Skill nodes and link to Profile and Person."""
    if not skills:
        return
    query = """
    MATCH (profile:Profile { updated_at: $updated_at })
    MATCH (person:Person)-[:BELONGS_TO_PROFILE]->(profile)
    UNWIND $skills AS skill
    CREATE (s:Skill {
        name: skill.name,
        category: skill.category,
        level: skill.level
    })
    CREATE (person)-[:HAS_SKILL]->(s)
    CREATE (s)-[:BELONGS_TO_PROFILE]->(profile)
    """
    result = tx.run(query, updated_at=updated_at, skills=skills)
    result.consume()
