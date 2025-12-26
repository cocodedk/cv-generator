"""Check Person nodes for profiles."""
from typing import List, Dict, Any


def check_person_nodes(session, profiles: List[Dict[str, Any]]) -> None:
    """Check Person nodes for each profile.

    Args:
        session: Neo4j database session
        profiles: List of profile records with updated_at timestamps
    """
    print("\n=== Person Nodes ===")
    for record in profiles:
        updated_at = record['updated_at']
        result = session.run(
            "MATCH (profile:Profile { updated_at: $updated_at }) "
            "OPTIONAL MATCH (person:Person)-[:BELONGS_TO_PROFILE]->(profile) "
            "RETURN count(person) AS person_count, collect(person.name) AS names",
            updated_at=updated_at
        )
        person_record = result.single()
        person_count = person_record['person_count']
        names = person_record['names']
        print(f"Profile {updated_at}:")
        print(f"  Person nodes: {person_count}")
        if names:
            print(f"  Names: {names}")
        else:
            print("  ⚠️  NO PERSON NODES FOUND!")
