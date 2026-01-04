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

    def test_get_cv_missing_address_fields(self, mock_neo4j_connection):
        """Test CV retrieval with missing address fields."""
        mock_session = mock_neo4j_connection.session.return_value
        mock_record = Mock()
        mock_record.single.return_value = {
            "person": {"name": "John Doe", "email": "john@example.com"},
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
        assert result["personal_info"]["address"] is None

    def test_get_cv_none_in_collections(self, mock_neo4j_connection):
        """Test CV retrieval with None values in collections."""
        mock_session = mock_neo4j_connection.session.return_value
        mock_record = Mock()
        mock_record.single.return_value = {
            "person": {"name": "John Doe"},
            "cv": {
                "id": "test-id",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
            },
            "experiences": [None, {"title": "Dev"}],
            "educations": [None],
            "skills": [None, None],
        }
        mock_session.run.return_value = mock_record

        result = queries.get_cv_by_id("test-id")

        assert result is not None
        assert len(result["experience"]) == 1
        assert len(result["education"]) == 0
        assert len(result["skills"]) == 0

    def test_get_cv_returns_theme(self, mock_neo4j_connection):
        """Test CV retrieval returns theme when present."""
        mock_session = mock_neo4j_connection.session.return_value
        mock_record = Mock()
        mock_record.single.return_value = {
            "person": {"name": "John Doe"},
            "cv": {
                "id": "test-id",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
                "theme": "modern",
            },
            "experiences": [],
            "educations": [],
            "skills": [],
        }
        mock_session.run.return_value = mock_record

        result = queries.get_cv_by_id("test-id")

        assert result is not None
        assert result["theme"] == "modern"

    def test_get_cv_defaults_theme_when_missing(self, mock_neo4j_connection):
        """Test CV retrieval defaults to classic when theme not present."""
        mock_session = mock_neo4j_connection.session.return_value
        mock_record = Mock()
        mock_record.single.return_value = {
            "person": {"name": "John Doe"},
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
        assert result["theme"] == "classic"


class TestGetCVByFilename:
    """Test get_cv_by_filename query."""

    def test_get_cv_by_filename_success(self, mock_neo4j_connection):
        """Test successful CV retrieval by filename."""
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
                "filename": "test_cv.html",
                "theme": "modern",
            },
            "experiences": [],
            "educations": [],
            "skills": [],
        }
        mock_session.run.return_value = mock_record

        result = queries.get_cv_by_filename("test_cv.html")

        assert result is not None
        assert result["cv_id"] == "test-id"
        assert result["filename"] == "test_cv.html"
        assert result["theme"] == "modern"

    def test_get_cv_by_filename_not_found(self, mock_neo4j_connection):
        """Test CV not found by filename."""
        mock_session = mock_neo4j_connection.session.return_value
        mock_record = Mock()
        mock_record.single.return_value = None
        mock_session.run.return_value = mock_record

        result = queries.get_cv_by_filename("non_existent.html")

        assert result is None

    def test_get_cv_by_filename_defaults_theme(self, mock_neo4j_connection):
        """Test CV retrieval by filename defaults to classic when theme missing."""
        mock_session = mock_neo4j_connection.session.return_value
        mock_record = Mock()
        mock_record.single.return_value = {
            "person": {"name": "John Doe"},
            "cv": {
                "id": "test-id",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
                "filename": "test_cv.html",
            },
            "experiences": [],
            "educations": [],
            "skills": [],
        }
        mock_session.run.return_value = mock_record

        result = queries.get_cv_by_filename("test_cv.html")

        assert result is not None
        assert result["theme"] == "classic"

    def test_get_cv_returns_target_company_and_role(self, mock_neo4j_connection):
        """Test CV retrieval returns target_company and target_role when present."""
        mock_session = mock_neo4j_connection.session.return_value
        mock_record = Mock()
        mock_record.single.return_value = {
            "person": {"name": "John Doe"},
            "cv": {
                "id": "test-id",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
                "target_company": "Google",
                "target_role": "Senior Developer",
            },
            "experiences": [],
            "educations": [],
            "skills": [],
        }
        mock_session.run.return_value = mock_record

        result = queries.get_cv_by_id("test-id")

        assert result is not None
        assert result["target_company"] == "Google"
        assert result["target_role"] == "Senior Developer"

    def test_get_cv_returns_none_for_missing_target_fields(self, mock_neo4j_connection):
        """Test CV retrieval returns None for target_company and target_role when missing."""
        mock_session = mock_neo4j_connection.session.return_value
        mock_record = Mock()
        mock_record.single.return_value = {
            "person": {"name": "John Doe"},
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
        assert result.get("target_company") is None
        assert result.get("target_role") is None
