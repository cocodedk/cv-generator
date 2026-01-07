"""Delete operations for CV update."""


def update_cv_timestamp(
    tx,
    cv_id: str,
    updated_at: str,
    theme: str = "classic",
    layout: str = "classic-two-column",
    target_company: str | None = None,
    target_role: str | None = None,
):
    """Update CV timestamp, theme, and layout."""
    query = """
    MATCH (cv:CV {id: $cv_id})
    SET cv.updated_at = $updated_at,
        cv.theme = $theme,
        cv.layout = $layout,
        cv.target_company = $target_company,
        cv.target_role = $target_role
    """
    result = tx.run(
        query, cv_id=cv_id, updated_at=updated_at, theme=theme, layout=layout,
        target_company=target_company, target_role=target_role
    )
    result.consume()


def delete_cv_relationships(tx, cv_id: str):
    """Delete existing relationships and nodes for a CV."""
    query = """
    MATCH (cv:CV {id: $cv_id})
    OPTIONAL MATCH (old_person:Person)-[:BELONGS_TO_CV]->(cv)
    OPTIONAL MATCH (old_person)-[:HAS_EXPERIENCE]->(exp:Experience)-[:BELONGS_TO_CV]->(cv)
    OPTIONAL MATCH (exp)-[:HAS_PROJECT]->(proj:Project)-[:BELONGS_TO_CV]->(cv)
    OPTIONAL MATCH (old_person)-[:HAS_EDUCATION]->(edu:Education)-[:BELONGS_TO_CV]->(cv)
    OPTIONAL MATCH (old_person)-[:HAS_SKILL]->(skill:Skill)-[:BELONGS_TO_CV]->(cv)
    DETACH DELETE proj, exp, edu, skill, old_person
    """
    result = tx.run(query, cv_id=cv_id)
    result.consume()
