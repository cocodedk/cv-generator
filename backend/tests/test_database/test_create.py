"""Tests for create_cv query."""
import re
from unittest.mock import Mock
from backend.database import queries


class TestCreateCV:
    """Test create_cv query."""

    def test_create_cv_success(self, mock_neo4j_connection, sample_cv_data):
        """Test successful CV creation."""
        mock_session = mock_neo4j_connection.session.return_value
        mock_result = Mock()
        mock_result.single.return_value = {"cv_id": "test-cv-id"}
        mock_tx = Mock()
        mock_tx.run.return_value = mock_result

        def write_transaction_side_effect(work):
            return work(mock_tx)

        mock_session.write_transaction.side_effect = write_transaction_side_effect

        cv_id = queries.create_cv(sample_cv_data)

        # Verify it returns a valid UUID string
        uuid_pattern = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
        assert re.match(uuid_pattern, cv_id), f"Expected UUID format, got: {cv_id}"
        assert isinstance(cv_id, str)
        mock_session.write_transaction.assert_called_once()
        mock_tx.run.assert_called_once()

    def test_create_cv_with_minimal_data(self, mock_neo4j_connection):
        """Test CV creation with minimal data."""
        minimal_data = {
            "personal_info": {"name": "John Doe"},
            "experience": [],
            "education": [],
            "skills": [],
        }
        mock_session = mock_neo4j_connection.session.return_value
        mock_result = Mock()
        mock_result.single.return_value = {"cv_id": "minimal-id"}
        mock_tx = Mock()
        mock_tx.run.return_value = mock_result

        def write_transaction_side_effect(work):
            return work(mock_tx)

        mock_session.write_transaction.side_effect = write_transaction_side_effect

        cv_id = queries.create_cv(minimal_data)
        # Verify it returns a valid UUID string
        uuid_pattern = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
        assert re.match(uuid_pattern, cv_id), f"Expected UUID format, got: {cv_id}"
        assert isinstance(cv_id, str)

    def test_create_cv_empty_arrays(self, mock_neo4j_connection):
        """Test CV creation with empty arrays."""
        data = {
            "personal_info": {"name": "Test"},
            "experience": [],
            "education": [],
            "skills": [],
        }
        mock_session = mock_neo4j_connection.session.return_value
        mock_result = Mock()
        mock_result.single.return_value = {"cv_id": "test-id"}
        mock_tx = Mock()
        mock_tx.run.return_value = mock_result

        def write_transaction_side_effect(work):
            return work(mock_tx)

        mock_session.write_transaction.side_effect = write_transaction_side_effect

        cv_id = queries.create_cv(data)
        assert isinstance(cv_id, str)

    def test_create_cv_none_values(self, mock_neo4j_connection):
        """Test CV creation with None values in optional fields."""
        data = {
            "personal_info": {
                "name": "Test",
                "email": None,
                "phone": None,
                "address": None,
            },
            "experience": [],
            "education": [],
            "skills": [],
        }
        mock_session = mock_neo4j_connection.session.return_value
        mock_result = Mock()
        mock_result.single.return_value = {"cv_id": "test-id"}
        mock_tx = Mock()
        mock_tx.run.return_value = mock_result

        def write_transaction_side_effect(work):
            return work(mock_tx)

        mock_session.write_transaction.side_effect = write_transaction_side_effect

        cv_id = queries.create_cv(data)
        assert isinstance(cv_id, str)
