"""Tests for get_cv_by_id query."""
from unittest.mock import Mock
from backend.database import queries


class TestGetCV:
    """Test get_cv_by_id query."""

    def test_get_cv_success(self, mock_neo4j_connection):
        """Test successful CV retrieval."""
        mock_session = mock_neo4j_connection.session.return_value
        mock_record = Mock()
        mock_record.single.return_value = {
            "person": {
                "name": "John Doe",
                "email": "john@example.com",
                "address_street": "123 Main St",
                "address_city": "New York",
            },
            "cv": {
                "id": "test-id",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
            },
            "experiences": [],
            "educations": [],
            "skills": [],
        }
        mock_session.run.return_value = mock_record

        result = queries.get_cv_by_id("test-id")

        assert result is not None
        assert result["cv_id"] == "test-id"

    def test_get_cv_not_found(self, mock_neo4j_connection):
        """Test CV not found."""
        mock_session = mock_neo4j_connection.session.return_value
        mock_record = Mock()
        mock_record.single.return_value = None
        mock_session.run.return_value = mock_record

        result = queries.get_cv_by_id("non-existent")

        assert result is None
