"""Skill node creation for profile update."""


def create_skill_nodes(tx, updated_at: str, person_element_id: str, skills: list):
    """Create Skill nodes and link to Profile and Person."""
    if not skills:
        return
    query = """
    MATCH (profile:Profile { updated_at: $updated_at })
    MATCH (person:Person) WHERE elementId(person) = $person_element_id
    UNWIND $skills AS skill
    CREATE (s:Skill {
        name: skill.name,
        category: skill.category,
        level: skill.level
    })
    CREATE (person)-[:HAS_SKILL]->(s)
    CREATE (s)-[:BELONGS_TO_PROFILE]->(profile)
    """
    tx.run(query, updated_at=updated_at, person_element_id=person_element_id, skills=skills)
