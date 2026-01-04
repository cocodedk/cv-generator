"""Tests for create_profile function."""
from backend.database import queries
from backend.tests.test_database.helpers.profile_queries.mocks import (
    setup_mock_session_for_write,
    create_mock_tx_with_multiple_results,
)


class TestCreateProfile:
    """Test create_profile function."""

    def test_create_profile_success(self, mock_neo4j_connection, sample_cv_data):
        """Test create_profile creates new profile."""
        profile_data = {
            "personal_info": sample_cv_data["personal_info"],
            "experience": sample_cv_data["experience"],
            "education": sample_cv_data["education"],
            "skills": sample_cv_data["skills"],
        }
        mock_session = mock_neo4j_connection.session.return_value
        # New implementation makes multiple tx.run() calls:
        # 1. create_profile_node - no return
        # 2. create_person_node - returns person record
        # 3. create_experience_nodes, create_education_nodes, create_skill_nodes - no return
        # 4. verify profile - returns profile
        mock_tx, _ = create_mock_tx_with_multiple_results(
            [
                None,  # create_profile_node
                {"profile": {}, "newPerson": {}},  # create_person_node
                None,  # create_experience_nodes
                None,  # create_education_nodes
                None,  # create_skill_nodes
                {"profile": {}},  # final verify
            ]
        )

        setup_mock_session_for_write(mock_session, mock_tx)

        success = queries.create_profile(profile_data)

        assert success is True
        mock_session.write_transaction.assert_called_once()
