"""Cypher queries for profile operations."""

CREATE_QUERY = """
CREATE (newProfile:Profile { updated_at: $updated_at })
CREATE (newPerson:Person { name: $name, title: $title, email: $email, phone: $phone,
    address_street: $address_street, address_city: $address_city,
    address_state: $address_state, address_zip: $address_zip,
    address_country: $address_country, linkedin: $linkedin,
    github: $github, website: $website, summary: $summary })
CREATE (newPerson)-[:BELONGS_TO_PROFILE]->(newProfile)
WITH newProfile, newPerson
FOREACH (exp IN COALESCE($experiences, []) |
    CREATE (experience:Experience { title: exp.title, company: exp.company,
        start_date: exp.start_date, end_date: exp.end_date,
        description: exp.description, location: exp.location })
    CREATE (newPerson)-[:HAS_EXPERIENCE]->(experience)
    CREATE (experience)-[:BELONGS_TO_PROFILE]->(newProfile)
    FOREACH (proj IN COALESCE(exp.projects, []) |
        CREATE (project:Project {
            name: proj.name,
            description: proj.description,
            url: proj.url,
            technologies: COALESCE(proj.technologies, []),
            highlights: COALESCE(proj.highlights, [])
        })
        CREATE (experience)-[:HAS_PROJECT]->(project)
        CREATE (project)-[:BELONGS_TO_PROFILE]->(newProfile)
    )
)
WITH newProfile, newPerson
FOREACH (edu IN COALESCE($educations, []) |
    CREATE (education:Education { degree: edu.degree, institution: edu.institution,
        year: edu.year, field: edu.field, gpa: edu.gpa })
    CREATE (newPerson)-[:HAS_EDUCATION]->(education)
    CREATE (education)-[:BELONGS_TO_PROFILE]->(newProfile)
)
WITH newProfile, newPerson
FOREACH (skill IN COALESCE($skills, []) |
    CREATE (s:Skill { name: skill.name, category: skill.category, level: skill.level })
    CREATE (newPerson)-[:HAS_SKILL]->(s)
    CREATE (s)-[:BELONGS_TO_PROFILE]->(newProfile)
)
RETURN newProfile
"""

UPDATE_QUERY = """
MATCH (profile:Profile)
WITH profile
ORDER BY profile.updated_at DESC
LIMIT 1
SET profile.updated_at = $updated_at
WITH profile
// Delete Projects first (leaf nodes, no dependencies)
MATCH (profile)<-[:BELONGS_TO_PROFILE]-(proj:Project)
DETACH DELETE proj
WITH profile
// Delete Experiences (after Projects are deleted)
MATCH (profile)<-[:BELONGS_TO_PROFILE]-(exp:Experience)
DETACH DELETE exp
WITH profile
// Delete Education nodes
MATCH (profile)<-[:BELONGS_TO_PROFILE]-(edu:Education)
DETACH DELETE edu
WITH profile
// Delete Skill nodes
MATCH (profile)<-[:BELONGS_TO_PROFILE]-(skill:Skill)
DETACH DELETE skill
WITH profile
// Delete Person node last (it references other nodes)
MATCH (old_person:Person)-[:BELONGS_TO_PROFILE]->(profile)
DETACH DELETE old_person
WITH profile
CREATE (newPerson:Person { name: $name, title: $title, email: $email, phone: $phone,
    address_street: $address_street, address_city: $address_city,
    address_state: $address_state, address_zip: $address_zip,
    address_country: $address_country, linkedin: $linkedin,
    github: $github, website: $website, summary: $summary })
CREATE (newPerson)-[:BELONGS_TO_PROFILE]->(profile)
WITH profile, newPerson
FOREACH (exp IN COALESCE($experiences, []) |
    CREATE (experience:Experience { title: exp.title, company: exp.company,
        start_date: exp.start_date, end_date: exp.end_date,
        description: exp.description, location: exp.location })
    CREATE (newPerson)-[:HAS_EXPERIENCE]->(experience)
    CREATE (experience)-[:BELONGS_TO_PROFILE]->(profile)
    FOREACH (proj IN COALESCE(exp.projects, []) |
        CREATE (project:Project {
            name: proj.name,
            description: proj.description,
            url: proj.url,
            technologies: COALESCE(proj.technologies, []),
            highlights: COALESCE(proj.highlights, [])
        })
        CREATE (experience)-[:HAS_PROJECT]->(project)
        CREATE (project)-[:BELONGS_TO_PROFILE]->(profile)
    )
)
WITH profile, newPerson
FOREACH (edu IN COALESCE($educations, []) |
    CREATE (education:Education { degree: edu.degree, institution: edu.institution,
        year: edu.year, field: edu.field, gpa: edu.gpa })
    CREATE (newPerson)-[:HAS_EDUCATION]->(education)
    CREATE (education)-[:BELONGS_TO_PROFILE]->(profile)
)
WITH profile, newPerson
FOREACH (skill IN COALESCE($skills, []) |
    CREATE (s:Skill { name: skill.name, category: skill.category, level: skill.level })
    CREATE (newPerson)-[:HAS_SKILL]->(s)
    CREATE (s)-[:BELONGS_TO_PROFILE]->(profile)
)
RETURN profile
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
ORDER BY profile.updated_at DESC
LIMIT 1
"""

LIST_PROFILES_QUERY = """
MATCH (profile:Profile)
OPTIONAL MATCH (person:Person)-[:BELONGS_TO_PROFILE]->(profile)
RETURN profile.updated_at AS updated_at, COALESCE(person.name, 'Unknown') AS name
ORDER BY profile.updated_at DESC
"""

GET_PROFILE_BY_UPDATED_AT_QUERY = """
MATCH (profile:Profile { updated_at: $updated_at })
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

DELETE_PROFILE_BY_UPDATED_AT_QUERY = """
MATCH (profile:Profile { updated_at: $updated_at })
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

DELETE_LATEST_QUERY = """
MATCH (profile:Profile)
WITH profile
ORDER BY profile.updated_at DESC
LIMIT 1
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
FOREACH (p IN projects | DETACH DELETE p)
FOREACH (e IN experiences | DETACH DELETE e)
FOREACH (e IN educations | DETACH DELETE e)
FOREACH (s IN skills | DETACH DELETE s)
FOREACH (p IN persons | DETACH DELETE p)
FOREACH (p IN profiles | DETACH DELETE p)
RETURN size(profiles) AS deleted
"""
