"""Profile node creation."""


def create_profile_node(tx, updated_at: str, language: str = "en"):
    """Create Profile node."""
    query = "CREATE (newProfile:Profile { updated_at: $updated_at, language: $language }) RETURN newProfile"
    result = tx.run(query, updated_at=updated_at, language=language)
    record = result.single()
    # Consume result to ensure query completes
    result.consume()
    # Return value is not used, but return for consistency
    if record:
        if hasattr(record, "get"):
            return record.get("newProfile")
        else:
            try:
                return record["newProfile"]
            except (KeyError, TypeError):
                return record
    return None
