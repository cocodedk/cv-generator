"""Cypher queries for profile operations."""
_DELETE_SUBQUERY = """
CALL {
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
    RETURN 1 AS deleted
}
"""

CREATE_QUERY = f"""{_DELETE_SUBQUERY}
CREATE (newProfile:Profile {{ updated_at: $updated_at }})
CREATE (newPerson:Person {{ name: $name, email: $email, phone: $phone,
    address_street: $address_street, address_city: $address_city,
    address_state: $address_state, address_zip: $address_zip,
    address_country: $address_country, linkedin: $linkedin,
    github: $github, website: $website, summary: $summary }})
CREATE (newPerson)-[:BELONGS_TO_PROFILE]->(newProfile)
WITH newProfile, newPerson
FOREACH (exp IN COALESCE($experiences, []) |
    CREATE (experience:Experience {{ title: exp.title, company: exp.company,
        start_date: exp.start_date, end_date: exp.end_date,
        description: exp.description, location: exp.location }})
    CREATE (newPerson)-[:HAS_EXPERIENCE]->(experience)
    CREATE (experience)-[:BELONGS_TO_PROFILE]->(newProfile)
    FOREACH (proj IN COALESCE(exp.projects, []) |
        CREATE (project:Project {{
            name: proj.name,
            description: proj.description,
            url: proj.url,
            technologies: COALESCE(proj.technologies, []),
            highlights: COALESCE(proj.highlights, [])
        }})
        CREATE (experience)-[:HAS_PROJECT]->(project)
        CREATE (project)-[:BELONGS_TO_PROFILE]->(newProfile)
    )
)
WITH newProfile, newPerson
FOREACH (edu IN COALESCE($educations, []) |
    CREATE (education:Education {{ degree: edu.degree, institution: edu.institution,
        year: edu.year, field: edu.field, gpa: edu.gpa }})
    CREATE (newPerson)-[:HAS_EDUCATION]->(education)
    CREATE (education)-[:BELONGS_TO_PROFILE]->(newProfile)
)
WITH newProfile, newPerson
FOREACH (skill IN COALESCE($skills, []) |
    CREATE (s:Skill {{ name: skill.name, category: skill.category, level: skill.level }})
    CREATE (newPerson)-[:HAS_SKILL]->(s)
    CREATE (s)-[:BELONGS_TO_PROFILE]->(newProfile)
)
RETURN newProfile
"""

GET_QUERY = """
MATCH (profile:Profile)
OPTIONAL MATCH (person:Person)-[:BELONGS_TO_PROFILE]->(profile)
CALL {
    WITH profile, person
    OPTIONAL MATCH (person)-[:HAS_EXPERIENCE]->(exp:Experience)-[:BELONGS_TO_PROFILE]->(profile)
    WITH profile, exp
    OPTIONAL MATCH (exp)-[:HAS_PROJECT]->(proj:Project)-[:BELONGS_TO_PROFILE]->(profile)
    WITH exp, collect(DISTINCT proj) AS projects
    RETURN collect(
        CASE
            WHEN exp IS NULL THEN NULL
            ELSE exp{.*, projects: [p IN projects | p{.*}]}
        END
    ) AS experiences
}
CALL {
    WITH profile, person
    OPTIONAL MATCH (person)-[:HAS_EDUCATION]->(edu:Education)-[:BELONGS_TO_PROFILE]->(profile)
    RETURN collect(DISTINCT edu) AS educations
}
CALL {
    WITH profile, person
    OPTIONAL MATCH (person)-[:HAS_SKILL]->(skill:Skill)-[:BELONGS_TO_PROFILE]->(profile)
    RETURN collect(DISTINCT skill) AS skills
}
RETURN profile, person, experiences, educations, skills
"""

DELETE_QUERY = """
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
