"""Tests for profile queries."""
import pytest
from unittest.mock import Mock, patch
from backend.database import queries


class TestSaveProfile:
    """Test save_profile query."""

    def test_save_profile_success(self, mock_neo4j_connection, sample_cv_data):
        """Test successful profile save."""
        profile_data = {
            "personal_info": sample_cv_data["personal_info"],
            "experience": sample_cv_data["experience"],
            "education": sample_cv_data["education"],
            "skills": sample_cv_data["skills"],
        }
        mock_session = mock_neo4j_connection.session.return_value
        mock_result = Mock()
        mock_result.single.return_value = {"profile": {}}
        mock_session.write_transaction.return_value = mock_result

        success = queries.save_profile(profile_data)

        assert success is True
        mock_session.write_transaction.assert_called_once()

    def test_save_profile_with_minimal_data(self, mock_neo4j_connection):
        """Test profile save with minimal data."""
        minimal_data = {
            "personal_info": {"name": "John Doe"},
            "experience": [],
            "education": [],
            "skills": [],
        }
        mock_session = mock_neo4j_connection.session.return_value
        mock_result = Mock()
        mock_result.single.return_value = {"profile": {}}
        mock_session.write_transaction.return_value = mock_result

        success = queries.save_profile(minimal_data)
        assert success is True


class TestGetProfile:
    """Test get_profile query."""

    def test_get_profile_success(self, mock_neo4j_connection):
        """Test successful profile retrieval."""
        mock_session = mock_neo4j_connection.session.return_value
        mock_record = Mock()
        mock_record.single.return_value = {
            "person": {
                "name": "John Doe",
                "email": "john@example.com",
                "address_street": "123 Main St",
                "address_city": "New York",
            },
            "profile": {
                "updated_at": "2024-01-01T00:00:00",
            },
            "experiences": [],
            "educations": [],
            "skills": [],
        }
        mock_session.run.return_value = mock_record

        result = queries.get_profile()

        assert result is not None
        assert result["personal_info"]["name"] == "John Doe"
        assert "updated_at" in result

    def test_get_profile_not_found(self, mock_neo4j_connection):
        """Test profile not found."""
        mock_session = mock_neo4j_connection.session.return_value
        mock_record = Mock()
        mock_record.single.return_value = None
        mock_session.run.return_value = mock_record

        result = queries.get_profile()

        assert result is None

    def test_get_profile_with_experiences(self, mock_neo4j_connection):
        """Test profile retrieval with experiences."""
        mock_session = mock_neo4j_connection.session.return_value
        # Use a dict-like object that can be converted with dict()
        exp_dict = {
            "title": "Developer",
            "company": "Tech Corp",
            "start_date": "2020-01",
        }
        mock_record = Mock()
        mock_record.single.return_value = {
            "person": {
                "name": "John Doe",
            },
            "profile": {
                "updated_at": "2024-01-01T00:00:00",
            },
            "experiences": [exp_dict],
            "educations": [],
            "skills": [],
        }
        mock_session.run.return_value = mock_record

        result = queries.get_profile()

        assert result is not None
        assert len(result["experience"]) == 1
        assert result["experience"][0]["title"] == "Developer"


class TestDeleteProfile:
    """Test delete_profile query."""

    def test_delete_profile_success(self, mock_neo4j_connection):
        """Test successful profile deletion."""
        mock_session = mock_neo4j_connection.session.return_value
        mock_result = Mock()
        mock_result.single.return_value = {"deleted": 1}
        mock_session.write_transaction.return_value = mock_result

        success = queries.delete_profile()

        assert success is True

    def test_delete_profile_not_found(self, mock_neo4j_connection):
        """Test delete non-existent profile."""
        mock_session = mock_neo4j_connection.session.return_value
        mock_result = Mock()
        mock_result.single.return_value = {"deleted": 0}
        mock_session.write_transaction.return_value = mock_result

        success = queries.delete_profile()

        assert success is False
