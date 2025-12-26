"""Integration tests for profile queries against real Neo4j."""
import copy
import pytest
from backend.database import queries
from backend.database.connection import Neo4jConnection


def _skip_if_no_neo4j():
    if not Neo4jConnection.verify_connectivity():
        pytest.skip("Neo4j is not available for integration tests.")


@pytest.mark.integration
class TestProfileQueriesIntegration:
    """CRUD coverage for profile queries using live Neo4j.

    WARNING: These tests run against the live Neo4j database and will delete profiles!
    Run with: pytest -m integration
    """

    def test_profile_crud_roundtrip(self, sample_cv_data):
        _skip_if_no_neo4j()
        # Clean up any existing test data before starting
        queries.delete_profile()

        initial_data = {
            "personal_info": sample_cv_data["personal_info"],
            "experience": sample_cv_data["experience"],
            "education": sample_cv_data["education"],
            "skills": sample_cv_data["skills"],
        }
        assert queries.save_profile(initial_data) is True

        stored = queries.get_profile()
        assert stored is not None
        assert stored["personal_info"]["name"] == initial_data["personal_info"]["name"]
        assert len(stored["experience"]) == len(initial_data["experience"])
        assert len(stored["education"]) == len(initial_data["education"])
        assert len(stored["skills"]) == len(initial_data["skills"])

        updated_data = copy.deepcopy(initial_data)
        updated_data["personal_info"]["name"] = "Updated Name"
        updated_data["personal_info"]["summary"] = "Updated summary"
        updated_data["experience"] = []
        updated_data["education"] = []
        updated_data["skills"] = []

        assert queries.save_profile(updated_data) is True
        updated = queries.get_profile()
        assert updated is not None
        assert updated["personal_info"]["name"] == "Updated Name"
        assert updated["personal_info"]["summary"] == "Updated summary"
        assert updated["experience"] == []
        assert updated["education"] == []
        assert updated["skills"] == []

        assert queries.delete_profile() is True
        assert queries.get_profile() is None
