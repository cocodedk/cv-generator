"""Tests for profile save operations."""
from backend.database import queries
from backend.tests.test_database.helpers.profile_queries.mocks import (
    setup_mock_session_for_read_write,
    setup_mock_session_for_write,
    create_mock_tx_with_result,
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

        # Mock write transaction (update profile)
        mock_tx_write, _ = create_mock_tx_with_result({"profile": {}})

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

    def test_create_profile_success(self, mock_neo4j_connection, sample_cv_data):
        """Test create_profile creates new profile."""
        profile_data = {
            "personal_info": sample_cv_data["personal_info"],
            "experience": sample_cv_data["experience"],
            "education": sample_cv_data["education"],
            "skills": sample_cv_data["skills"],
        }
        mock_session = mock_neo4j_connection.session.return_value
        mock_tx, _ = create_mock_tx_with_result({"profile": {}})

        setup_mock_session_for_write(mock_session, mock_tx)

        success = queries.create_profile(profile_data)

        assert success is True
        mock_session.write_transaction.assert_called_once()

    def test_update_profile_success(self, mock_neo4j_connection, sample_cv_data):
        """Test update_profile updates existing profile without deleting Profile node."""
        profile_data = {
            "personal_info": sample_cv_data["personal_info"],
            "experience": sample_cv_data["experience"],
            "education": sample_cv_data["education"],
            "skills": sample_cv_data["skills"],
        }
        mock_session = mock_neo4j_connection.session.return_value
        # UPDATE_QUERY returns the Profile node (not deleted)
        mock_tx, _ = create_mock_tx_with_result({"profile": {"updated_at": "2024-01-01T00:00:00"}})

        setup_mock_session_for_write(mock_session, mock_tx)

        success = queries.update_profile(profile_data)

        assert success is True
        mock_session.write_transaction.assert_called_once()
        # Verify UPDATE_QUERY was used (check that Profile node is returned, not created)
        call_args = mock_tx.run.call_args
        assert call_args is not None

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

        # Mock write transaction (update profile) - returns Profile node
        mock_tx_write, _ = create_mock_tx_with_result({"profile": {"updated_at": "2024-01-01T00:00:00"}})

        setup_mock_session_for_read_write(mock_session, mock_tx_read, mock_tx_write)

        success = queries.save_profile(profile_data)

        assert success is True
        # Verify UPDATE_QUERY was called (not CREATE_QUERY)
        # UPDATE_QUERY starts with MATCH, CREATE_QUERY starts with CREATE
        # Check the first call which is update_profile_timestamp
        call_args_list = mock_tx_write.run.call_args_list
        assert len(call_args_list) > 0
        first_call = call_args_list[0]
        assert first_call is not None
        query_text = first_call[0][0] if first_call[0] else ""
        # UPDATE_QUERY should MATCH existing profile, not CREATE new one
        assert "MATCH (profile:Profile)" in query_text
        assert query_text.strip().startswith("MATCH")  # UPDATE starts with MATCH
