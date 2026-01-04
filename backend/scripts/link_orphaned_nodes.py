"""Link remaining orphaned nodes to Profile."""
import sys

# Add app directory to path (Docker container has /app as working directory)
sys.path.insert(0, "/app")

from backend.database.connection import Neo4jConnection


def link_orphaned_nodes():
    """Link any remaining orphaned nodes to the Profile."""
    driver = Neo4jConnection.get_driver()
    database = Neo4jConnection.get_database()

    link_query = """
    MATCH (profile:Profile)
    WITH profile

    // Link all orphaned Experience nodes (linked to any Person)
    MATCH (person:Person)-[:HAS_EXPERIENCE]->(exp:Experience)
    WHERE NOT (exp)-[:BELONGS_TO_PROFILE]->(:Profile)
    WITH profile, collect(DISTINCT exp) AS exps
    FOREACH (e IN exps | CREATE (e)-[:BELONGS_TO_PROFILE]->(profile))
    WITH profile

    // Link all orphaned Education nodes (linked to any Person)
    MATCH (person:Person)-[:HAS_EDUCATION]->(edu:Education)
    WHERE NOT (edu)-[:BELONGS_TO_PROFILE]->(:Profile)
    WITH profile, collect(DISTINCT edu) AS edus
    FOREACH (e IN edus | CREATE (e)-[:BELONGS_TO_PROFILE]->(profile))
    WITH profile

    // Link all orphaned Skill nodes (linked to any Person)
    MATCH (person:Person)-[:HAS_SKILL]->(skill:Skill)
    WHERE NOT (skill)-[:BELONGS_TO_PROFILE]->(:Profile)
    WITH profile, collect(DISTINCT skill) AS skills
    FOREACH (s IN skills | CREATE (s)-[:BELONGS_TO_PROFILE]->(profile))
    WITH profile

    // Link all orphaned Project nodes (linked to Experiences that are now linked to Profile)
    MATCH (exp:Experience)-[:HAS_PROJECT]->(proj:Project)
    WHERE (exp)-[:BELONGS_TO_PROFILE]->(profile)
      AND NOT (proj)-[:BELONGS_TO_PROFILE]->(:Profile)
    WITH profile, collect(DISTINCT proj) AS projs
    FOREACH (p IN projs | CREATE (p)-[:BELONGS_TO_PROFILE]->(profile))

    RETURN profile.updated_at AS profile_updated_at
    """

    verification_query = """
    MATCH (profile:Profile)
    OPTIONAL MATCH (person:Person)-[:BELONGS_TO_PROFILE]->(profile)
    OPTIONAL MATCH (person)-[:HAS_EXPERIENCE]->(exp:Experience)-[:BELONGS_TO_PROFILE]->(profile)
    OPTIONAL MATCH (person)-[:HAS_EDUCATION]->(edu:Education)-[:BELONGS_TO_PROFILE]->(profile)
    OPTIONAL MATCH (person)-[:HAS_SKILL]->(skill:Skill)-[:BELONGS_TO_PROFILE]->(profile)
    OPTIONAL MATCH (exp)-[:HAS_PROJECT]->(proj:Project)-[:BELONGS_TO_PROFILE]->(profile)
    RETURN profile.updated_at AS updated_at,
           count(DISTINCT person) AS persons,
           count(DISTINCT exp) AS experiences,
           count(DISTINCT proj) AS projects,
           count(DISTINCT edu) AS educations,
           count(DISTINCT skill) AS skills
    """

    with driver.session(database=database) as session:
        print("=== Linking Orphaned Nodes ===")

        # Check current state
        check_query = """
        MATCH (profile:Profile)
        OPTIONAL MATCH (exp:Experience) WHERE NOT (exp)-[:BELONGS_TO_PROFILE]->(:Profile)
        OPTIONAL MATCH (edu:Education) WHERE NOT (edu)-[:BELONGS_TO_PROFILE]->(:Profile)
        OPTIONAL MATCH (skill:Skill) WHERE NOT (skill)-[:BELONGS_TO_PROFILE]->(:Profile)
        RETURN count(DISTINCT exp) AS orphaned_exp,
               count(DISTINCT edu) AS orphaned_edu,
               count(DISTINCT skill) AS orphaned_skill
        """
        result = session.run(check_query)
        record = result.single()
        print("Orphaned nodes before linking:")
        print(f"  Experiences: {record['orphaned_exp']}")
        print(f"  Educations: {record['orphaned_edu']}")
        print(f"  Skills: {record['orphaned_skill']}")

        if (
            record["orphaned_exp"] == 0
            and record["orphaned_edu"] == 0
            and record["orphaned_skill"] == 0
        ):
            print("\n✅ No orphaned nodes found. Everything is already linked!")
        else:
            # Link orphaned nodes
            result = session.run(link_query)
            record = result.single()
            if record:
                print("\n✅ Linked orphaned nodes to Profile")
            else:
                print("\n❌ Failed to link nodes")
                return

        # Verify final state
        print("\n=== Final Verification ===")
        result = session.run(verification_query)
        record = result.single()
        if record:
            print(f"Profile updated_at: {record['updated_at']}")
            print(f"  Persons: {record['persons']}")
            print(f"  Experiences: {record['experiences']}")
            print(f"  Projects: {record['projects']}")
            print(f"  Educations: {record['educations']}")
            print(f"  Skills: {record['skills']}")

            # Check for remaining orphaned nodes
            check_after = """
            MATCH (exp:Experience) WHERE NOT (exp)-[:BELONGS_TO_PROFILE]->(:Profile)
            RETURN count(exp) AS orphaned_exp
            UNION ALL
            MATCH (edu:Education) WHERE NOT (edu)-[:BELONGS_TO_PROFILE]->(:Profile)
            RETURN count(edu) AS orphaned_edu
            UNION ALL
            MATCH (skill:Skill) WHERE NOT (skill)-[:BELONGS_TO_PROFILE]->(:Profile)
            RETURN count(skill) AS orphaned_skill
            """
            result = session.run(check_after)
            total_orphaned = sum([r.values()[0] for r in result])

            if total_orphaned == 0:
                print("\n✅ All nodes successfully linked to Profile!")
            else:
                print(f"\n⚠️  {total_orphaned} nodes still orphaned")


if __name__ == "__main__":
    try:
        link_orphaned_nodes()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
    finally:
        Neo4jConnection.close()
