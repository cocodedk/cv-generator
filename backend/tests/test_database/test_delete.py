"""Tests for delete_cv query."""
from unittest.mock import Mock
from backend.database import queries


class TestDeleteCV:
    """Test delete_cv query."""

    def test_delete_cv_success(self, mock_neo4j_connection):
        """Test successful CV deletion."""
        mock_session = mock_neo4j_connection.session.return_value
        mock_result = Mock()
        mock_result.single.return_value = {"deleted": 1}
        mock_tx = Mock()
        mock_tx.run.return_value = mock_result

        def write_transaction_side_effect(work):
            return work(mock_tx)

        mock_session.write_transaction.side_effect = write_transaction_side_effect

        success = queries.delete_cv("test-id")

        assert success is True
        mock_tx.run.assert_called_once()

    def test_delete_cv_not_found(self, mock_neo4j_connection):
        """Test delete non-existent CV."""
        mock_session = mock_neo4j_connection.session.return_value
        mock_result = Mock()
        mock_result.single.return_value = {"deleted": 0}
        mock_tx = Mock()
        mock_tx.run.return_value = mock_result

        def write_transaction_side_effect(work):
            return work(mock_tx)

        mock_session.write_transaction.side_effect = write_transaction_side_effect

        success = queries.delete_cv("non-existent")

        assert success is False
