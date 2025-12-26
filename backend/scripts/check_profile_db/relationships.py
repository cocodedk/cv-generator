"""Check relationships for profiles."""
from typing import List, Dict, Any


def check_relationships(session, profiles: List[Dict[str, Any]]) -> None:
    """Check relationships for each profile.

    Args:
        session: Neo4j database session
        profiles: List of profile records with updated_at timestamps
    """
    print("\n=== Relationships ===")
    for record in profiles:
        updated_at = record['updated_at']
        result = session.run(
            "MATCH (profile:Profile { updated_at: $updated_at }) "
            "OPTIONAL MATCH (profile)<-[:BELONGS_TO_PROFILE]-(node) "
            "RETURN labels(node)[0] AS label, count(node) AS count",
            updated_at=updated_at
        )
        print(f"Profile {updated_at}:")
        for rel_record in result:
            label = rel_record['label']
            count = rel_record['count']
            if label:
                print(f"  {label}: {count}")
