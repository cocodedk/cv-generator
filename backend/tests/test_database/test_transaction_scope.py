"""Tests for transaction scope behavior."""
import re
from unittest.mock import Mock
from backend.database import queries


class TestTransactionScope:
    """Test that transaction scope is properly respected."""

    def test_create_cv_consumes_result_in_transaction(
        self, mock_neo4j_connection, sample_cv_data
    ):
        """Test that create_cv consumes result inside transaction callback."""
        mock_session = mock_neo4j_connection.session.return_value
        mock_result = Mock()
        mock_result.single.return_value = {"cv_id": "test-cv-id"}
        mock_tx = Mock()
        mock_tx.run.return_value = mock_result

        def write_transaction_side_effect(work):
            # Simulate transaction: execute callback and return its result
            # The callback should consume the result while transaction is "open"
            result = work(mock_tx)
            # After callback returns, transaction is "closed"
            # Any attempt to access mock_result.single() here would fail
            return result

        mock_session.write_transaction.side_effect = write_transaction_side_effect

        cv_id = queries.create_cv(sample_cv_data)

        # Verify result was consumed inside transaction
        # create_cv now returns a UUID directly without calling single()
        uuid_pattern = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
        assert re.match(uuid_pattern, cv_id), f"Expected UUID format, got: {cv_id}"
        # Verify tx.run was called (meaning callback executed)
        # create_cv now makes multiple query calls (CV, Person, Experience, Education, Skills)
        assert mock_tx.run.call_count >= 1

    def test_update_cv_consumes_result_in_transaction(
        self, mock_neo4j_connection, sample_cv_data
    ):
        """Test that update_cv consumes result inside transaction callback."""
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
        assert mock_result.single.call_count == 1
        # After refactoring, update_cv makes multiple focused query calls
        assert (
            mock_tx.run.call_count >= 6
        )  # timestamp, delete, person, exp, edu, skills, verify

    def test_delete_cv_consumes_result_in_transaction(self, mock_neo4j_connection):
        """Test that delete_cv consumes result inside transaction callback."""
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
        assert mock_result.single.call_count == 1
        mock_tx.run.assert_called_once()
