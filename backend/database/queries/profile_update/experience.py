"""Experience node creation for profile update."""


def create_experience_nodes(
    tx, updated_at: str, person_element_id: str, experiences: list
):
    """Create Experience nodes with Projects and link to Profile and Person."""
    if not experiences:
        return
    query = """
    MATCH (profile:Profile { updated_at: $updated_at })
    MATCH (person:Person) WHERE elementId(person) = $person_element_id
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
    CREATE (experience)-[:BELONGS_TO_PROFILE]->(profile)
    WITH profile, person, experience, exp
    UNWIND COALESCE(exp.projects, []) AS proj
    CREATE (project:Project {
        name: proj.name,
        description: proj.description,
        url: proj.url,
        technologies: COALESCE(proj.technologies, []),
        highlights: COALESCE(proj.highlights, [])
    })
    CREATE (experience)-[:HAS_PROJECT]->(project)
    CREATE (project)-[:BELONGS_TO_PROFILE]->(profile)
    """
    tx.run(
        query,
        updated_at=updated_at,
        person_element_id=person_element_id,
        experiences=experiences,
    )
