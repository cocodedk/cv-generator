"""Tests for save_profile function."""
from backend.database import queries
from backend.tests.test_database.helpers.profile_queries.mocks import (
    setup_mock_session_for_read_write,
    create_mock_tx_with_result,
    create_mock_tx_with_multiple_results,
)


class TestSaveProfile:
    """Test save_profile query."""

    def test_save_profile_creates_new_profile(self, mock_neo4j_connection, sample_cv_data):
        """Test save_profile creates new profile when none exists."""
        profile_data = {
            "personal_info": sample_cv_data["personal_info"],
            "experience": sample_cv_data["experience"],
            "education": sample_cv_data["education"],
            "skills": sample_cv_data["skills"],
        }
        mock_session = mock_neo4j_connection.session.return_value

        # Mock read transaction (check if profile exists) - returns False
        mock_tx_read, _ = create_mock_tx_with_result(None)

        # Mock write transaction (create profile)
        mock_tx_write, _ = create_mock_tx_with_result({"profile": {}})

        setup_mock_session_for_read_write(mock_session, mock_tx_read, mock_tx_write)

        success = queries.save_profile(profile_data)

        assert success is True
        # Should call read_transaction to check existence, then write_transaction to create
        assert mock_session.read_transaction.call_count == 1
        assert mock_session.write_transaction.call_count == 1

    def test_save_profile_updates_existing_profile(self, mock_neo4j_connection, sample_cv_data):
        """Test save_profile updates existing profile."""
        profile_data = {
            "personal_info": sample_cv_data["personal_info"],
            "experience": sample_cv_data["experience"],
            "education": sample_cv_data["education"],
            "skills": sample_cv_data["skills"],
        }
        mock_session = mock_neo4j_connection.session.return_value

        # Mock read transaction (check if profile exists) - returns True
        mock_tx_read, _ = create_mock_tx_with_result({"profile": {}})

        # Mock write transaction (update profile) - multiple calls for new implementation
        mock_tx_write, _ = create_mock_tx_with_multiple_results([
            {"profile": {}},  # update_profile_timestamp
            {"deleted": 0},   # delete projects
            {"deleted": 0},   # delete experiences
            {"deleted": 0},   # delete education
            {"deleted": 0},   # delete skills
            {"deleted": 0},   # delete person
            {"remaining_persons": 0},  # verify_person_deletion
            {"person_element_id": "test-element-id"},  # create_person_node
            {"person_count": 1},  # verify_single_person
            None,  # create_experience_nodes
            None,  # create_education_nodes
            None,  # create_skill_nodes
            {"profile": {}},  # final verify
        ])

        setup_mock_session_for_read_write(mock_session, mock_tx_read, mock_tx_write)

        success = queries.save_profile(profile_data)

        assert success is True
        # Should call read_transaction to check existence, then write_transaction to update
        assert mock_session.read_transaction.call_count == 1
        assert mock_session.write_transaction.call_count == 1

    def test_save_profile_with_minimal_data(self, mock_neo4j_connection):
        """Test profile save with minimal data."""
        minimal_data = {
            "personal_info": {"name": "John Doe"},
            "experience": [],
            "education": [],
            "skills": [],
        }
        mock_session = mock_neo4j_connection.session.return_value

        # Mock read transaction (check if profile exists) - returns False
        mock_tx_read, _ = create_mock_tx_with_result(None)

        # Mock write transaction (create profile)
        mock_tx_write, _ = create_mock_tx_with_result({"profile": {}})

        setup_mock_session_for_read_write(mock_session, mock_tx_read, mock_tx_write)

        success = queries.save_profile(minimal_data)
        assert success is True

    def test_profile_node_persists_through_update(self, mock_neo4j_connection, sample_cv_data):
        """Test that Profile node is never deleted during update operations."""
        profile_data = {
            "personal_info": sample_cv_data["personal_info"],
            "experience": sample_cv_data["experience"],
            "education": sample_cv_data["education"],
            "skills": sample_cv_data["skills"],
        }
        mock_session = mock_neo4j_connection.session.return_value

        # Mock read transaction (check if profile exists) - returns True
        mock_tx_read, _ = create_mock_tx_with_result({"profile": {}})

        # Mock write transaction (update profile) - multiple calls for new implementation
        mock_tx_write, _ = create_mock_tx_with_multiple_results([
            {"profile": {}},  # update_profile_timestamp
            {"deleted": 0},   # delete projects
            {"deleted": 0},   # delete experiences
            {"deleted": 0},   # delete education
            {"deleted": 0},   # delete skills
            {"deleted": 0},   # delete person
            {"remaining_persons": 0},  # verify_person_deletion
            {"person_element_id": "test-element-id"},  # create_person_node
            {"person_count": 1},  # verify_single_person
            None,  # create_experience_nodes
            None,  # create_education_nodes
            None,  # create_skill_nodes
            {"profile": {"updated_at": "2024-01-01T00:00:00"}},  # final verify
        ])

        setup_mock_session_for_read_write(mock_session, mock_tx_read, mock_tx_write)

        success = queries.save_profile(profile_data)

        assert success is True
        # Verify UPDATE flow was called (not CREATE)
        # Check the first call which is update_profile_timestamp - should MATCH existing profile
        call_args_list = mock_tx_write.run.call_args_list
        assert len(call_args_list) > 0
        first_call = call_args_list[0]
        assert first_call is not None
        query_text = first_call[0][0] if first_call[0] else ""
        # UPDATE should MATCH existing profile, not CREATE new one
        assert "MATCH (profile:Profile)" in query_text
        assert query_text.strip().startswith("MATCH")  # UPDATE starts with MATCH
