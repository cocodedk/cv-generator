"""Profile node creation."""
from typing import Dict, Any


def create_profile_node(tx, updated_at: str):
    """Create Profile node."""
    query = "CREATE (newProfile:Profile { updated_at: $updated_at }) RETURN newProfile"
    result = tx.run(query, updated_at=updated_at)
    record = result.single()
    # Consume result to ensure query completes
    result.consume()
    # Return value is not used, but return for consistency
    if record:
        # Handle both dict-like records and direct access
        if hasattr(record, "get"):
            return record.get("newProfile") or record.get("profile")
        else:
            try:
                return record["newProfile"]
            except (KeyError, TypeError):
                return record
    return None
