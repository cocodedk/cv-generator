"""Related nodes creation (Experience, Education, Skill) for CV."""


def create_experience_nodes(tx, cv_id: str, experiences: list):
    """Create Experience nodes with Projects and link to CV and Person."""
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
    WITH cv, person, experience, exp
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


def create_education_nodes(tx, cv_id: str, educations: list):
    """Create Education nodes and link to CV and Person."""
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


def create_skill_nodes(tx, cv_id: str, skills: list):
    """Create Skill nodes and link to CV and Person."""
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
