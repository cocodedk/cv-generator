"""Delete operations for profile update."""


def verify_person_deletion(tx, updated_at: str) -> None:
    """Fail update if any Person nodes remain for the target Profile."""
    query = """
    MATCH (profile:Profile { updated_at: $updated_at })
    OPTIONAL MATCH (person:Person)-[:BELONGS_TO_PROFILE]->(profile)
    RETURN count(person) AS remaining_persons
    """
    remaining = tx.run(query, updated_at=updated_at).single()["remaining_persons"]
    if remaining != 0:
        raise Exception(
            f"Deletion failed: {remaining} Person nodes still exist for profile updated_at={updated_at}"
        )


def verify_single_person(tx, updated_at: str) -> None:
    """Fail update if the Profile is linked to anything other than exactly one Person."""
    query = """
    MATCH (profile:Profile { updated_at: $updated_at })
    OPTIONAL MATCH (person:Person)-[:BELONGS_TO_PROFILE]->(profile)
    RETURN count(person) AS person_count
    """
    count = tx.run(query, updated_at=updated_at).single()["person_count"]
    if count != 1:
        raise Exception(
            f"Expected exactly 1 Person node, found {count} for profile updated_at={updated_at}"
        )


def update_profile_timestamp(tx, updated_at: str, language: str = "en"):
    """Update Profile timestamp and language."""
    query = """
    MATCH (profile:Profile)
    WITH profile
    ORDER BY profile.updated_at DESC
    LIMIT 1
    SET profile.updated_at = $updated_at, profile.language = $language
    RETURN profile
    """
    result = tx.run(query, updated_at=updated_at, language=language)
    return result.single() is not None


def delete_profile_nodes(tx, updated_at: str):
    """Delete old profile nodes in dependency order."""
    # Delete Projects first (leaf nodes, no dependencies)
    query_projects = """
    MATCH (profile:Profile { updated_at: $updated_at })
    OPTIONAL MATCH (profile)<-[:BELONGS_TO_PROFILE]-(proj:Project)
    WITH profile, collect(DISTINCT proj) AS projects
    FOREACH (p IN projects | DETACH DELETE p)
    RETURN count(projects) AS deleted
    """
    result = tx.run(query_projects, updated_at=updated_at)
    result.consume()  # Consume result to ensure query completes

    # Delete Experiences (after Projects are deleted)
    query_experiences = """
    MATCH (profile:Profile { updated_at: $updated_at })
    OPTIONAL MATCH (profile)<-[:BELONGS_TO_PROFILE]-(exp:Experience)
    WITH profile, collect(DISTINCT exp) AS experiences
    FOREACH (e IN experiences | DETACH DELETE e)
    RETURN count(experiences) AS deleted
    """
    result = tx.run(query_experiences, updated_at=updated_at)
    result.consume()

    # Delete Education nodes
    query_education = """
    MATCH (profile:Profile { updated_at: $updated_at })
    OPTIONAL MATCH (profile)<-[:BELONGS_TO_PROFILE]-(edu:Education)
    WITH profile, collect(DISTINCT edu) AS educations
    FOREACH (e IN educations | DETACH DELETE e)
    RETURN count(educations) AS deleted
    """
    result = tx.run(query_education, updated_at=updated_at)
    result.consume()

    # Delete Skill nodes
    query_skills = """
    MATCH (profile:Profile { updated_at: $updated_at })
    OPTIONAL MATCH (profile)<-[:BELONGS_TO_PROFILE]-(skill:Skill)
    WITH profile, collect(DISTINCT skill) AS skills
    FOREACH (s IN skills | DETACH DELETE s)
    RETURN count(skills) AS deleted
    """
    result = tx.run(query_skills, updated_at=updated_at)
    result.consume()

    # Delete Person node last (it references other nodes)
    query_person = """
    MATCH (profile:Profile { updated_at: $updated_at })
    OPTIONAL MATCH (old_person:Person)-[:BELONGS_TO_PROFILE]->(profile)
    WITH profile, collect(DISTINCT old_person) AS persons
    FOREACH (p IN persons | DETACH DELETE p)
    RETURN count(persons) AS deleted
    """
    result = tx.run(query_person, updated_at=updated_at)
    result.consume()
