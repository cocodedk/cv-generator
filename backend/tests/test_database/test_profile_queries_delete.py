"""Tests for profile delete operations."""
from unittest.mock import Mock
from backend.database import queries
from backend.tests.test_database.helpers.profile_queries.mocks import (
    setup_mock_session_for_write,
    create_mock_tx_with_result,
)


class TestDeleteProfile:
    """Test delete_profile query."""

    def test_delete_profile_success(self, mock_neo4j_connection):
        """Test successful profile deletion."""
        mock_session = mock_neo4j_connection.session.return_value
        mock_record = Mock()
        mock_record.get.return_value = 1
        mock_tx, _ = create_mock_tx_with_result(mock_record)

        setup_mock_session_for_write(mock_session, mock_tx)

        success = queries.delete_profile()

        assert success is True

    def test_delete_profile_not_found(self, mock_neo4j_connection):
        """Test delete non-existent profile."""
        mock_session = mock_neo4j_connection.session.return_value
        mock_record = Mock()
        mock_record.get.return_value = 0
        mock_tx, _ = create_mock_tx_with_result(mock_record)

        setup_mock_session_for_write(mock_session, mock_tx)

        success = queries.delete_profile()

        assert success is False

    def test_delete_profile_by_updated_at_success(self, mock_neo4j_connection):
        """Test successful deletion of specific profile by updated_at."""
        mock_session = mock_neo4j_connection.session.return_value
        mock_tx = Mock()
        mock_result = Mock()
        mock_record = Mock()
        mock_record.get.return_value = 1
        mock_result.single.return_value = mock_record
        mock_tx.run.return_value = mock_result

        def execute_work(work_func):
            return work_func(mock_tx)

        mock_session.write_transaction.side_effect = execute_work
        mock_session.execute_write.side_effect = execute_work

        success = queries.delete_profile_by_updated_at("2024-01-01T00:00:00")

        assert success is True
        # Verify the query was called with updated_at parameter
        call_args = mock_tx.run.call_args
        assert call_args is not None
        assert call_args[1]["updated_at"] == "2024-01-01T00:00:00"

    def test_delete_profile_by_updated_at_not_found(self, mock_neo4j_connection):
        """Test delete non-existent profile by updated_at."""
        mock_session = mock_neo4j_connection.session.return_value
        mock_tx = Mock()
        mock_result = Mock()
        mock_record = Mock()
        mock_record.get.return_value = 0
        mock_result.single.return_value = mock_record
        mock_tx.run.return_value = mock_result

        def execute_work(work_func):
            return work_func(mock_tx)

        mock_session.write_transaction.side_effect = execute_work
        mock_session.execute_write.side_effect = execute_work

        success = queries.delete_profile_by_updated_at("2024-01-01T00:00:00")

        assert success is False
