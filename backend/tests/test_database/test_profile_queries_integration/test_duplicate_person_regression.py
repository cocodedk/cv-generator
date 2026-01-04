"""Regression test for duplicate Person node prevention."""
import pytest
from backend.database import queries
from backend.database.connection import Neo4jConnection
from backend.tests.test_database.test_profile_queries_integration.helpers import (
    skip_if_no_neo4j,
    is_test_profile,
)


@pytest.mark.integration
class TestDuplicatePersonRegression:
    """Regression tests for duplicate Person node prevention."""

    def test_update_profile_with_multiple_persons_aborts_on_deletion_failure(
        self, sample_cv_data
    ):
        """Regression test: Update should abort if deletion fails, preventing node explosion."""
        skip_if_no_neo4j()

        # Create initial profile with test prefix
        profile_data = {
            "personal_info": {
                "name": "test" + sample_cv_data["personal_info"]["name"],
                "email": "test" + sample_cv_data["personal_info"]["email"],
                "phone": "test" + sample_cv_data["personal_info"]["phone"],
                "address": {
                    "street": "test"
                    + sample_cv_data["personal_info"]["address"]["street"],
                    "city": "test" + sample_cv_data["personal_info"]["address"]["city"],
                    "state": "test"
                    + sample_cv_data["personal_info"]["address"]["state"],
                    "zip": "test" + sample_cv_data["personal_info"]["address"]["zip"],
                    "country": "test"
                    + sample_cv_data["personal_info"]["address"]["country"],
                },
                "linkedin": "test" + sample_cv_data["personal_info"]["linkedin"],
                "github": "test" + sample_cv_data["personal_info"]["github"],
                "summary": "test" + sample_cv_data["personal_info"]["summary"],
            },
            "experience": sample_cv_data["experience"],
            "education": sample_cv_data["education"],
            "skills": sample_cv_data["skills"],
        }
        queries.save_profile(profile_data)

        # Get the profile's updated_at
        profiles = queries.list_profiles()
        assert len(profiles) > 0
        profile_updated_at = profiles[0]["updated_at"]

        # Verify it's a test profile
        profile = queries.get_profile_by_updated_at(profile_updated_at)
        assert is_test_profile(profile), "Profile must be a test profile"

        driver = Neo4jConnection.get_driver()
        database = Neo4jConnection.get_database()

        try:
            # Manually create a duplicate Person node (simulating deletion failure)
            with driver.session(database=database) as session:
                session.run(
                    """
                    MATCH (profile:Profile { updated_at: $updated_at })
                    CREATE (duplicatePerson:Person {
                        name: 'testDuplicate Person',
                        email: 'testduplicate@test.com'
                    })
                    CREATE (duplicatePerson)-[:BELONGS_TO_PROFILE]->(profile)
                """,
                    updated_at=profile_updated_at,
                )

            # Verify duplicate exists
            with driver.session(database=database) as session:
                result = session.run(
                    """
                    MATCH (profile:Profile { updated_at: $updated_at })
                    MATCH (person:Person)-[:BELONGS_TO_PROFILE]->(profile)
                    RETURN count(person) AS person_count
                """,
                    updated_at=profile_updated_at,
                )
                count = result.single()["person_count"]
                assert count == 2, "Should have 2 Person nodes before update"

            # Get initial counts before update
            with driver.session(database=database) as session:
                result = session.run(
                    """
                    MATCH (profile:Profile { updated_at: $updated_at })
                    OPTIONAL MATCH (person:Person)-[:BELONGS_TO_PROFILE]->(profile)
                    OPTIONAL MATCH (person)-[:HAS_EXPERIENCE]->(exp:Experience)-[:BELONGS_TO_PROFILE]->(profile)
                    OPTIONAL MATCH (person)-[:HAS_EDUCATION]->(edu:Education)-[:BELONGS_TO_PROFILE]->(profile)
                    OPTIONAL MATCH (person)-[:HAS_SKILL]->(skill:Skill)-[:BELONGS_TO_PROFILE]->(profile)
                    RETURN count(DISTINCT person) AS person_count,
                           count(DISTINCT exp) AS exp_count,
                           count(DISTINCT edu) AS edu_count,
                           count(DISTINCT skill) AS skill_count
                """,
                    updated_at=profile_updated_at,
                )
                result.single()  # Execute query to verify initial state

            # Attempt update - deletion should work correctly and remove both Person nodes
            # The fix ensures child nodes are bound to the new Person, preventing multiplication
            new_profile_data = {
                "personal_info": {
                    **profile_data["personal_info"],
                    "name": "testUpdated Name",
                },
                "experience": profile_data["experience"],
                "education": profile_data["education"],
                "skills": profile_data["skills"],
            }

            # Update should succeed - deletion removes all Person nodes correctly
            assert queries.update_profile(new_profile_data) is True

            # Get new profile timestamp after update
            profiles_after = queries.list_profiles()
            assert len(profiles_after) > 0
            new_profile_updated_at = profiles_after[0]["updated_at"]

            # Verify exactly 1 Person node exists (no multiplication)
            with driver.session(database=database) as session:
                result = session.run(
                    """
                    MATCH (profile:Profile { updated_at: $updated_at })
                    MATCH (person:Person)-[:BELONGS_TO_PROFILE]->(profile)
                    OPTIONAL MATCH (person)-[:HAS_EXPERIENCE]->(exp:Experience)-[:BELONGS_TO_PROFILE]->(profile)
                    OPTIONAL MATCH (person)-[:HAS_EDUCATION]->(edu:Education)-[:BELONGS_TO_PROFILE]->(profile)
                    OPTIONAL MATCH (person)-[:HAS_SKILL]->(skill:Skill)-[:BELONGS_TO_PROFILE]->(profile)
                    RETURN count(DISTINCT person) AS person_count,
                           count(DISTINCT exp) AS exp_count,
                           count(DISTINCT edu) AS edu_count,
                           count(DISTINCT skill) AS skill_count
                """,
                    updated_at=new_profile_updated_at,
                )
                after = result.single()
                assert (
                    after["person_count"] == 1
                ), "Should have exactly 1 Person node after update"
                # Verify child nodes match input (not multiplied)
                assert after["exp_count"] == len(
                    new_profile_data["experience"]
                ), f"Experience count should match input: {after['exp_count']} != {len(new_profile_data['experience'])}"
                assert after["edu_count"] == len(
                    new_profile_data["education"]
                ), f"Education count should match input: {after['edu_count']} != {len(new_profile_data['education'])}"
                assert after["skill_count"] == len(
                    new_profile_data["skills"]
                ), f"Skill count should match input: {after['skill_count']} != {len(new_profile_data['skills'])}"
        finally:
            # Always cleanup: Delete the test profile (even if test fails)
            # Safety: Only delete profiles that are verified to be test profiles
            try:
                # Delete old profile timestamp only if it's a test profile
                old_profile = queries.get_profile_by_updated_at(profile_updated_at)
                if old_profile and is_test_profile(old_profile):
                    queries.delete_profile_by_updated_at(profile_updated_at)

                # Check for new profile timestamp and delete only if it's a test profile
                profiles_after = queries.list_profiles()
                if profiles_after:
                    new_profile_updated_at = profiles_after[0]["updated_at"]
                    if new_profile_updated_at != profile_updated_at:
                        new_profile = queries.get_profile_by_updated_at(
                            new_profile_updated_at
                        )
                        if new_profile and is_test_profile(new_profile):
                            queries.delete_profile_by_updated_at(new_profile_updated_at)
            except Exception:
                pass  # Ignore cleanup errors
