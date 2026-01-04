"""CV node creation."""


def create_cv_node(
    tx, cv_id: str, created_at: str, theme: str, layout: str = "classic-two-column"
):
    """Create CV node."""
    query = """
    CREATE (cv:CV {
        id: $cv_id,
        created_at: $created_at,
        updated_at: $created_at,
        theme: $theme,
        layout: $layout
    })
    RETURN cv
    """
    result = tx.run(
        query, cv_id=cv_id, created_at=created_at, theme=theme, layout=layout
    )
    result.consume()
    return cv_id
