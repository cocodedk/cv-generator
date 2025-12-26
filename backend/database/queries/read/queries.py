"""Common query building functions for CV read operations."""


def build_cv_query(match_clause: str) -> str:
    """Build the full CV query with all related nodes.

    Args:
        match_clause: The MATCH clause for the CV node
                     (e.g., "MATCH (cv:CV {id: $cv_id})" or
                      "MATCH (cv:CV {filename: $filename})")

    Returns:
        Complete Cypher query string
    """
    return f"""
    {match_clause}
    OPTIONAL MATCH (person:Person)-[:BELONGS_TO_CV]->(cv)
    CALL {{
        WITH cv, person
        OPTIONAL MATCH (person)-[:HAS_EXPERIENCE]->(exp:Experience)-[:BELONGS_TO_CV]->(cv)
        WITH cv, exp
        OPTIONAL MATCH (exp)-[:HAS_PROJECT]->(proj:Project)-[:BELONGS_TO_CV]->(cv)
        WITH exp, collect(DISTINCT proj) AS projects
        RETURN collect(
            CASE
                WHEN exp IS NULL THEN NULL
                ELSE exp{{.*, projects: [p IN projects | p{{.*}}]}}
            END
        ) AS experiences
    }}
    CALL {{
        WITH cv, person
        OPTIONAL MATCH (person)-[:HAS_EDUCATION]->(edu:Education)-[:BELONGS_TO_CV]->(cv)
        RETURN collect(DISTINCT edu) AS educations
    }}
    CALL {{
        WITH cv, person
        OPTIONAL MATCH (person)-[:HAS_SKILL]->(skill:Skill)-[:BELONGS_TO_CV]->(cv)
        RETURN collect(DISTINCT skill) AS skills
    }}
    RETURN cv, person, experiences, educations, skills
    """
