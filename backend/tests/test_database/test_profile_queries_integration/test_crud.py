"""CRUD integration tests for profile queries."""
import copy
import pytest
from backend.database import queries
from backend.tests.test_database.test_profile_queries_integration.helpers import (
    skip_if_no_neo4j,
    is_test_profile,
)


@pytest.mark.integration
class TestProfileCRUD:
    """CRUD coverage for profile queries using live Neo4j.

    WARNING: These tests run against the live Neo4j database and will delete the
    test-created profile. Other profiles in the database will remain intact.
    Run with: pytest -m integration

    TEST ISOLATION:
    - This test always creates NEW profiles using create_profile() to prevent
      overwriting real profile data
    - Before any update operation, it verifies the profile being updated is a test profile
    - All test data is prefixed with "test" to make it easily identifiable
    - Only profiles with "test" prefix are deleted at the end
    """

    def test_profile_crud_roundtrip(self, sample_cv_data):
        """Test complete CRUD cycle: create, read, update, delete."""
        skip_if_no_neo4j()

        # Prefix all string fields with "test" to make test data easily recognizable.
        # This ensures test profiles can be identified and safely deleted without
        # affecting real profiles in the database.
        initial_data = {
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
            "experience": [
                {
                    "title": "test" + exp["title"],
                    "company": "test" + exp["company"],
                    "start_date": exp["start_date"],
                    "end_date": exp["end_date"],
                    "description": "test" + exp["description"],
                    "location": "test" + exp["location"],
                    "projects": [
                        {
                            "name": "test" + proj["name"],
                            "description": "test" + proj["description"],
                            "technologies": [
                                "test" + tech for tech in proj["technologies"]
                            ],
                            "highlights": [
                                "test" + highlight for highlight in proj["highlights"]
                            ],
                            "url": "test" + proj["url"],
                        }
                        for proj in exp.get("projects", [])
                    ],
                }
                for exp in sample_cv_data["experience"]
            ],
            "education": [
                {
                    "degree": "test" + edu["degree"],
                    "institution": "test" + edu["institution"],
                    "year": edu["year"],
                    "field": "test" + edu["field"],
                    "gpa": edu["gpa"],
                }
                for edu in sample_cv_data["education"]
            ],
            "skills": [
                {
                    "name": "test" + skill["name"],
                    "category": "test" + skill["category"],
                    "level": skill["level"],
                }
                for skill in sample_cv_data["skills"]
            ],
        }
        # Always create a new profile to prevent overwriting real profiles
        # Using create_profile() ensures we never update existing profiles
        assert queries.create_profile(initial_data) is True

        # Track the profile immediately after creation
        stored = queries.get_profile()
        assert stored is not None
        assert stored["personal_info"]["name"] == initial_data["personal_info"]["name"]
        assert len(stored["experience"]) == len(initial_data["experience"])
        assert len(stored["education"]) == len(initial_data["education"])
        assert len(stored["skills"]) == len(initial_data["skills"])
        # Track the profile's updated_at timestamp immediately after creation
        # This ensures we're tracking the test profile we just created
        test_profile_updated_at = stored["updated_at"]
        # Verify the created profile is a test profile
        assert is_test_profile(stored), "Created profile must be a test profile"

        updated_data = copy.deepcopy(initial_data)
        updated_data["personal_info"]["name"] = "testUpdated Name"
        updated_data["personal_info"]["summary"] = "testUpdated summary"
        updated_data["experience"] = []
        updated_data["education"] = []
        updated_data["skills"] = []

        # Safety check: Verify the most recent profile is our test profile before updating
        # This prevents accidentally updating a real profile if it became more recent
        current_profile = queries.get_profile()
        assert current_profile is not None, "Profile should exist before update"
        assert is_test_profile(current_profile), (
            f"Safety check failed: Most recent profile is not a test profile. "
            f"Profile name: {current_profile['personal_info']['name']}. "
            f"This would overwrite real profile data. Aborting update."
        )
        # Verify we're updating the same profile we created
        assert current_profile["updated_at"] == test_profile_updated_at, (
            "Most recent profile is not the test profile we created. "
            "This would update a different profile. Aborting update."
        )

        # Safe to update - we've verified it's our test profile
        assert queries.save_profile(updated_data) is True
        updated = queries.get_profile()
        assert updated is not None
        assert updated["personal_info"]["name"] == "testUpdated Name"
        assert updated["personal_info"]["summary"] == "testUpdated summary"
        assert updated["experience"] == []
        assert updated["education"] == []
        assert updated["skills"] == []
        # Track the updated profile's timestamp (update changes the timestamp)
        test_profile_updated_at = updated["updated_at"]

        # Safety check: Verify the profile to be deleted is actually a test profile
        profile_to_delete = queries.get_profile_by_updated_at(test_profile_updated_at)
        assert profile_to_delete is not None, "Profile to delete not found"
        assert is_test_profile(profile_to_delete), (
            f"Safety check failed: Attempted to delete non-test profile. "
            f"Profile name: {profile_to_delete['personal_info']['name']}"
        )

        # Delete only the test-created profile, not all profiles
        assert queries.delete_profile_by_updated_at(test_profile_updated_at) is True
        # Verify the test profile was deleted
        deleted_profile = queries.get_profile_by_updated_at(test_profile_updated_at)
        assert deleted_profile is None
