"""Recover Profile node and reconnect orphaned nodes."""
import sys
from datetime import datetime

# Add app directory to path (Docker container has /app as working directory)
sys.path.insert(0, "/app")

from backend.database.connection import Neo4jConnection


def recover_profile():
    """Recover Profile node and reconnect all orphaned nodes."""
    driver = Neo4jConnection.get_driver()
    database = Neo4jConnection.get_database()

    # Generate ISO timestamp
    updated_at = datetime.utcnow().isoformat()

    recovery_query = """
    // Step 1: Create Profile node with current timestamp
    CREATE (profile:Profile { updated_at: $updated_at })
    WITH profile

    // Step 2: Link first orphaned Person node to Profile
    MATCH (person:Person)
    WHERE NOT (person)-[:BELONGS_TO_PROFILE]->(:Profile)
    WITH profile, person
    LIMIT 1
    CREATE (person)-[:BELONGS_TO_PROFILE]->(profile)
    WITH profile

    // Step 3: Link all Experience nodes linked to any orphaned Person
    MATCH (orphaned_person:Person)-[:HAS_EXPERIENCE]->(exp:Experience)
    WHERE NOT (exp)-[:BELONGS_TO_PROFILE]->(:Profile)
    WITH profile, collect(DISTINCT exp) AS exps
    FOREACH (e IN exps | CREATE (e)-[:BELONGS_TO_PROFILE]->(profile))
    WITH profile

    // Step 4: Link all Education nodes linked to any orphaned Person
    MATCH (orphaned_person:Person)-[:HAS_EDUCATION]->(edu:Education)
    WHERE NOT (edu)-[:BELONGS_TO_PROFILE]->(:Profile)
    WITH profile, collect(DISTINCT edu) AS edus
    FOREACH (e IN edus | CREATE (e)-[:BELONGS_TO_PROFILE]->(profile))
    WITH profile

    // Step 5: Link all Skill nodes linked to any orphaned Person
    MATCH (orphaned_person:Person)-[:HAS_SKILL]->(skill:Skill)
    WHERE NOT (skill)-[:BELONGS_TO_PROFILE]->(:Profile)
    WITH profile, collect(DISTINCT skill) AS skills
    FOREACH (s IN skills | CREATE (s)-[:BELONGS_TO_PROFILE]->(profile))
    WITH profile

    // Step 6: Link all Project nodes linked to Experiences that are now linked to Profile
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
        print("=== Recovering Profile Node ===")

        # Check if Profile already exists
        check_query = "MATCH (p:Profile) RETURN count(p) AS count"
        result = session.run(check_query)
        count = result.single()["count"]

        if count > 0:
            print(f"⚠️  Profile already exists ({count} Profile node(s))")
            print("Skipping recovery. Use verification query to check connections.")
        else:
            # Run recovery
            result = session.run(recovery_query, updated_at=updated_at)
            record = result.single()
            if record:
                print(
                    f"✅ Profile created with updated_at: {record['profile_updated_at']}"
                )
            else:
                print("❌ Failed to create Profile")
                return

        # Verify recovery
        print("\n=== Verification ===")
        result = session.run(verification_query)
        record = result.single()
        if record:
            print(f"Profile updated_at: {record['updated_at']}")
            print(f"  Persons: {record['persons']}")
            print(f"  Experiences: {record['experiences']}")
            print(f"  Projects: {record['projects']}")
            print(f"  Educations: {record['educations']}")
            print(f"  Skills: {record['skills']}")

            if record["persons"] > 0:
                print("\n✅ Recovery successful! Profile is connected.")
            else:
                print("\n⚠️  Profile created but no Person nodes connected.")
        else:
            print("❌ Verification failed - Profile not found")


if __name__ == "__main__":
    try:
        recover_profile()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
    finally:
        Neo4jConnection.close()
