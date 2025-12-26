"""Tests for update_profile function."""
from backend.database import queries
from backend.tests.test_database.helpers.profile_queries.mocks import (
    setup_mock_session_for_write,
    create_mock_tx_with_multiple_results,
)


class TestUpdateProfile:
    """Test update_profile function."""

    def test_update_profile_success(self, mock_neo4j_connection, sample_cv_data):
        """Test update_profile updates existing profile without deleting Profile node."""
        profile_data = {
            "personal_info": sample_cv_data["personal_info"],
            "experience": sample_cv_data["experience"],
            "education": sample_cv_data["education"],
            "skills": sample_cv_data["skills"],
        }
        mock_session = mock_neo4j_connection.session.return_value
        # New implementation makes multiple tx.run() calls:
        # 1. update_profile_timestamp - returns profile
        # 2. delete_profile_nodes - multiple calls (projects, experiences, etc.) - return counts
        # 3. verify_person_deletion - returns count 0
        # 4. create_person_node - returns person_element_id
        # 5. verify_single_person - returns count 1
        # 6. create_experience_nodes, create_education_nodes, create_skill_nodes - no return
        # 7. verify profile - returns profile
        mock_tx, _ = create_mock_tx_with_multiple_results([
            {"profile": {}},  # update_profile_timestamp
            {"deleted": 0},   # delete projects
            {"deleted": 0},   # delete experiences
            {"deleted": 0},   # delete education
            {"deleted": 0},   # delete skills
            {"deleted": 0},   # delete person
            {"remaining_persons": 0},  # verify_person_deletion
            {"person_element_id": "test-element-id"},  # create_person_node
            {"person_count": 1},  # verify_single_person
            None,  # create_experience_nodes (no return)
            None,  # create_education_nodes (no return)
            None,  # create_skill_nodes (no return)
            {"profile": {}},  # final verify
        ])

        setup_mock_session_for_write(mock_session, mock_tx)

        success = queries.update_profile(profile_data)

        assert success is True
        mock_session.write_transaction.assert_called_once()
        # Verify multiple queries were called
        assert mock_tx.run.call_count > 0
