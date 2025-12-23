"""Tests for database queries."""
import pytest
from unittest.mock import Mock, patch
from backend.database import queries


class TestCreateCV:
    """Test create_cv query."""

    def test_create_cv_success(self, mock_neo4j_connection, sample_cv_data):
        """Test successful CV creation."""
        mock_session = mock_neo4j_connection.session.return_value
        mock_result = Mock()
        mock_result.single.return_value = {"cv_id": "test-cv-id"}
        mock_session.write_transaction.return_value = mock_result

        cv_id = queries.create_cv(sample_cv_data)

        assert cv_id == "test-cv-id"
        mock_session.write_transaction.assert_called_once()

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
        mock_session.write_transaction.return_value = mock_result

        cv_id = queries.create_cv(minimal_data)
        assert cv_id == "minimal-id"


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


class TestUpdateCV:
    """Test update_cv query."""

    def test_update_cv_success(self, mock_neo4j_connection, sample_cv_data):
        """Test successful CV update."""
        mock_session = mock_neo4j_connection.session.return_value
        mock_result = Mock()
        mock_result.single.return_value = {"cv_id": "test-id"}
        mock_session.write_transaction.return_value = mock_result

        success = queries.update_cv("test-id", sample_cv_data)

        assert success is True
        mock_session.write_transaction.assert_called_once()

    def test_update_cv_not_found(self, mock_neo4j_connection, sample_cv_data):
        """Test update non-existent CV."""
        mock_session = mock_neo4j_connection.session.return_value
        mock_result = Mock()
        mock_result.single.return_value = None
        mock_session.write_transaction.return_value = mock_result

        success = queries.update_cv("non-existent", sample_cv_data)

        assert success is False


class TestDeleteCV:
    """Test delete_cv query."""

    def test_delete_cv_success(self, mock_neo4j_connection):
        """Test successful CV deletion."""
        mock_session = mock_neo4j_connection.session.return_value
        mock_result = Mock()
        mock_result.single.return_value = {"deleted": 1}
        mock_session.write_transaction.return_value = mock_result

        success = queries.delete_cv("test-id")

        assert success is True

    def test_delete_cv_not_found(self, mock_neo4j_connection):
        """Test delete non-existent CV."""
        mock_session = mock_neo4j_connection.session.return_value
        mock_result = Mock()
        mock_result.single.return_value = {"deleted": 0}
        mock_session.write_transaction.return_value = mock_result

        success = queries.delete_cv("non-existent")

        assert success is False


class TestListCVs:
    """Test list_cvs query."""

    def test_list_cvs_success(self, mock_neo4j_connection):
        """Test successful CV listing."""
        mock_session = mock_neo4j_connection.session.return_value

        # Mock count result
        mock_count_record = Mock()
        mock_count_record.single.return_value = {"total": 2}

        # Mock list result
        mock_list_record1 = Mock()
        mock_list_record1.__iter__ = Mock(
            return_value=iter(
                [
                    {
                        "cv": {
                            "id": "id1",
                            "created_at": "2024-01-01",
                            "updated_at": "2024-01-01",
                        },
                        "person_name": "John Doe",
                        "filename": "cv1.odt",
                    },
                    {
                        "cv": {
                            "id": "id2",
                            "created_at": "2024-01-02",
                            "updated_at": "2024-01-02",
                        },
                        "person_name": "Jane Doe",
                        "filename": None,
                    },
                ]
            )
        )

        mock_session.run.side_effect = [mock_count_record, mock_list_record1]

        result = queries.list_cvs(limit=10, offset=0)

        assert result["total"] == 2
        assert len(result["cvs"]) == 2

    def test_list_cvs_with_search(self, mock_neo4j_connection):
        """Test CV listing with search."""
        mock_session = mock_neo4j_connection.session.return_value

        mock_count_record = Mock()
        mock_count_record.single.return_value = {"total": 1}

        mock_list_record = Mock()
        mock_list_record.__iter__ = Mock(
            return_value=iter(
                [
                    {
                        "cv": {
                            "id": "id1",
                            "created_at": "2024-01-01",
                            "updated_at": "2024-01-01",
                        },
                        "person_name": "John Doe",
                        "filename": None,
                    }
                ]
            )
        )

        mock_session.run.side_effect = [mock_count_record, mock_list_record]

        result = queries.list_cvs(limit=10, offset=0, search="John")

        assert result["total"] == 1
        assert len(result["cvs"]) == 1
