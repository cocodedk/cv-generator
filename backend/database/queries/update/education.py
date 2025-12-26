"""Education node creation for CV update."""


def create_education_nodes(tx, cv_id: str, educations: list):
    """Create Education nodes and link to Person and CV."""
    if not educations:
        return
    query = """
    MATCH (cv:CV {id: $cv_id})
    MATCH (person:Person)-[:BELONGS_TO_CV]->(cv)
    UNWIND $educations AS edu
    CREATE (education:Education {
        degree: edu.degree,
        institution: edu.institution,
        year: edu.year,
        field: edu.field,
        gpa: edu.gpa
    })
    CREATE (person)-[:HAS_EDUCATION]->(education)
    CREATE (education)-[:BELONGS_TO_CV]->(cv)
    """
    result = tx.run(query, cv_id=cv_id, educations=educations)
    result.consume()
