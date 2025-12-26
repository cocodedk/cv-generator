"""Check Profile nodes in database."""
from typing import List, Dict, Any


def check_profile_nodes(session) -> List[Dict[str, Any]]:
    """Check what Profile nodes exist in the database.

    Args:
        session: Neo4j database session

    Returns:
        List of profile records with updated_at timestamps
    """
    print("=== Profile Nodes ===")
    result = session.run(
        "MATCH (p:Profile) RETURN p.updated_at AS updated_at ORDER BY p.updated_at DESC"
    )
    profiles = list(result)
    print(f"Found {len(profiles)} Profile node(s):")
    for record in profiles:
        print(f"  - updated_at: {record['updated_at']}")

    if not profiles:
        print("  No Profile nodes found!")

    return profiles
