"""Experience node creation for CV update."""


def create_experience_nodes(tx, cv_id: str, experiences: list):
    """Create Experience nodes and link to Person and CV."""
    if not experiences:
        return
    query = """
    MATCH (cv:CV {id: $cv_id})
    MATCH (person:Person)-[:BELONGS_TO_CV]->(cv)
    UNWIND $experiences AS exp
    CREATE (experience:Experience {
        title: exp.title,
        company: exp.company,
        start_date: exp.start_date,
        end_date: exp.end_date,
        description: exp.description,
        location: exp.location
    })
    CREATE (person)-[:HAS_EXPERIENCE]->(experience)
    CREATE (experience)-[:BELONGS_TO_CV]->(cv)
    WITH cv, experience, exp
    UNWIND COALESCE(exp.projects, []) AS proj
    CREATE (project:Project {
        name: proj.name,
        description: proj.description,
        url: proj.url,
        technologies: COALESCE(proj.technologies, []),
        highlights: COALESCE(proj.highlights, [])
    })
    CREATE (experience)-[:HAS_PROJECT]->(project)
    CREATE (project)-[:BELONGS_TO_CV]->(cv)
    """
    result = tx.run(query, cv_id=cv_id, experiences=experiences)
    result.consume()
