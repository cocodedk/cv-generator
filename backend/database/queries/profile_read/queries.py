"""Common query building functions for profile read operations."""


def build_full_profile_query(match_clause: str) -> str:
    """Build the full profile query with all related nodes.

    Args:
        match_clause: The MATCH clause for the Profile node
                     (e.g., "MATCH (profile:Profile)" or
                      "MATCH (profile:Profile { updated_at: $updated_at })")

    Returns:
        Complete Cypher query string
    """
    return f"""
    {match_clause}
    OPTIONAL MATCH (person:Person)-[:BELONGS_TO_PROFILE]->(profile)
    CALL {{
        WITH profile, person
        OPTIONAL MATCH (person)-[:HAS_EXPERIENCE]->(exp:Experience)-[:BELONGS_TO_PROFILE]->(profile)
        WITH profile, exp
        OPTIONAL MATCH (exp)-[:HAS_PROJECT]->(proj:Project)-[:BELONGS_TO_PROFILE]->(profile)
        WITH exp, collect(DISTINCT proj) AS projects
        RETURN collect(
            CASE
                WHEN exp IS NULL THEN NULL
                ELSE exp{{.*, projects: [p IN projects | p{{.*}}]}}
            END
        ) AS experiences
    }}
    CALL {{
        WITH profile, person
        OPTIONAL MATCH (person)-[:HAS_EDUCATION]->(edu:Education)-[:BELONGS_TO_PROFILE]->(profile)
        RETURN collect(DISTINCT edu) AS educations
    }}
    CALL {{
        WITH profile, person
        OPTIONAL MATCH (person)-[:HAS_SKILL]->(skill:Skill)-[:BELONGS_TO_PROFILE]->(profile)
        RETURN collect(DISTINCT skill) AS skills
    }}
    """ + "RETURN profile{.*, language: profile.language}, person, experiences, educations, skills"
