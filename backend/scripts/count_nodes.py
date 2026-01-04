"""Script to count nodes in Neo4j database."""
import sys

# Add app directory to path (Docker container has /app as working directory)
sys.path.insert(0, "/app")

from backend.database.connection import Neo4jConnection


def count_all_nodes():
    """Count all nodes in the database by type."""
    driver = Neo4jConnection.get_driver()
    database = Neo4jConnection.get_database()

    query = """
    MATCH (n)
    RETURN labels(n) AS labels, count(n) AS count
    ORDER BY count DESC
    """

    with driver.session(database=database) as session:
        result = session.run(query)
        print("\n=== Node Counts by Type ===")
        total = 0
        for record in result:
            labels = record["labels"]
            count = record["count"]
            total += count
            label_str = ":".join(labels) if labels else "No Label"
            print(f"{label_str}: {count}")
        print(f"\nTotal nodes: {total}")

        # Also count relationships
        rel_query = """
        MATCH ()-[r]->()
        RETURN type(r) AS type, count(r) AS count
        ORDER BY count DESC
        """
        print("\n=== Relationship Counts by Type ===")
        rel_total = 0
        rel_result = session.run(rel_query)
        for record in rel_result:
            rel_type = record["type"]
            count = record["count"]
            rel_total += count
            print(f"{rel_type}: {count}")
        print(f"\nTotal relationships: {rel_total}")

        # Count Profile nodes and their connected nodes
        profile_query = """
        MATCH (profile:Profile)
        OPTIONAL MATCH (profile)<-[:BELONGS_TO_PROFILE]-(person:Person)
        OPTIONAL MATCH (profile)<-[:BELONGS_TO_PROFILE]-(exp:Experience)
        OPTIONAL MATCH (profile)<-[:BELONGS_TO_PROFILE]-(proj:Project)
        OPTIONAL MATCH (profile)<-[:BELONGS_TO_PROFILE]-(edu:Education)
        OPTIONAL MATCH (profile)<-[:BELONGS_TO_PROFILE]-(skill:Skill)
        RETURN profile.updated_at AS updated_at,
               count(DISTINCT person) AS persons,
               count(DISTINCT exp) AS experiences,
               count(DISTINCT proj) AS projects,
               count(DISTINCT edu) AS educations,
               count(DISTINCT skill) AS skills
        ORDER BY profile.updated_at DESC
        """
        print("\n=== Profile Details ===")
        profile_result = session.run(profile_query)
        for record in profile_result:
            print(f"\nProfile updated_at: {record['updated_at']}")
            print(f"  Persons: {record['persons']}")
            print(f"  Experiences: {record['experiences']}")
            print(f"  Projects: {record['projects']}")
            print(f"  Educations: {record['educations']}")
            print(f"  Skills: {record['skills']}")


if __name__ == "__main__":
    count_all_nodes()
