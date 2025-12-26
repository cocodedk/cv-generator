"""Check profile data in database."""
import sys

# Add app directory to path (Docker container has /app as working directory)
sys.path.insert(0, '/app')

from backend.database.connection import Neo4jConnection
from backend.database.queries.profile_queries import GET_QUERY


def check_profiles():
    """Check what profiles exist in the database."""
    driver = Neo4jConnection.get_driver()
    database = Neo4jConnection.get_database()

    with driver.session(database=database) as session:
        # Check all Profile nodes
        print("=== Profile Nodes ===")
        result = session.run("MATCH (p:Profile) RETURN p.updated_at AS updated_at ORDER BY p.updated_at DESC")
        profiles = list(result)
        print(f"Found {len(profiles)} Profile node(s):")
        for record in profiles:
            print(f"  - updated_at: {record['updated_at']}")

        if not profiles:
            print("  No Profile nodes found!")
            return

        # Check Person nodes for each profile
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

        # Check what GET_QUERY returns
        print("\n=== GET_QUERY Result ===")
        result = session.run(GET_QUERY)
        record = result.single()
        if record:
            print(f"Profile found: {record.get('profile', {}).get('updated_at', 'N/A')}")
            print(f"Person: {record.get('person')}")
            print(f"Experiences count: {len(record.get('experiences', [])) if record.get('experiences') else 0}")
            print(f"Educations count: {len(record.get('educations', [])) if record.get('educations') else 0}")
            print(f"Skills count: {len(record.get('skills', [])) if record.get('skills') else 0}")

            if not record.get('person'):
                print("  ⚠️  NO PERSON NODE IN RESULT!")
        else:
            print("  ⚠️  GET_QUERY returned no results!")

        # Check relationships
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


if __name__ == "__main__":
    try:
        check_profiles()
    finally:
        Neo4jConnection.close()
