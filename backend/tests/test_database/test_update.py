"""Tests for update_cv query."""
from unittest.mock import Mock
from backend.database import queries


class TestUpdateCV:
    """Test update_cv query."""

    def test_update_cv_success(self, mock_neo4j_connection, sample_cv_data):
        """Test successful CV update."""
        mock_session = mock_neo4j_connection.session.return_value
        mock_result = Mock()
        mock_result.single.return_value = {"cv_id": "test-id"}
        mock_tx = Mock()
        mock_tx.run.return_value = mock_result

        def write_transaction_side_effect(work):
            return work(mock_tx)

        mock_session.write_transaction.side_effect = write_transaction_side_effect

        success = queries.update_cv("test-id", sample_cv_data)

        assert success is True
        mock_session.write_transaction.assert_called_once()
        mock_tx.run.assert_called_once()

    def test_update_cv_not_found(self, mock_neo4j_connection, sample_cv_data):
        """Test update non-existent CV."""
        mock_session = mock_neo4j_connection.session.return_value
        mock_result = Mock()
        mock_result.single.return_value = None
        mock_tx = Mock()
        mock_tx.run.return_value = mock_result

        def write_transaction_side_effect(work):
            return work(mock_tx)

        mock_session.write_transaction.side_effect = write_transaction_side_effect

        success = queries.update_cv("non-existent", sample_cv_data)

        assert success is False
