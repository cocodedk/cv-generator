"""Tests for profile get operations."""
from unittest.mock import Mock
from backend.database import queries
from backend.tests.test_database.helpers.profile_queries.mocks import (
    setup_mock_session_for_read,
    create_mock_tx_with_result,
)


class TestGetProfile:
    """Test get_profile query."""

    def test_get_profile_success(self, mock_neo4j_connection):
        """Test successful profile retrieval."""
        mock_session = mock_neo4j_connection.session.return_value
        mock_result_data = {
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
        mock_tx, _ = create_mock_tx_with_result(mock_result_data)

        setup_mock_session_for_read(mock_session, mock_tx)

        result = queries.get_profile()

        assert result is not None
        assert result["personal_info"]["name"] == "John Doe"
        assert "updated_at" in result

    def test_get_profile_not_found(self, mock_neo4j_connection):
        """Test profile not found."""
        mock_session = mock_neo4j_connection.session.return_value
        mock_tx, _ = create_mock_tx_with_result(None)

        setup_mock_session_for_read(mock_session, mock_tx)

        result = queries.get_profile()

        assert result is None

    def test_get_profile_with_experiences(self, mock_neo4j_connection):
        """Test profile retrieval with experiences."""
        mock_session = mock_neo4j_connection.session.return_value
        exp_dict = {
            "title": "Developer",
            "company": "Tech Corp",
            "start_date": "2020-01",
        }
        mock_result_data = {
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
        mock_tx, _ = create_mock_tx_with_result(mock_result_data)

        setup_mock_session_for_read(mock_session, mock_tx)

        result = queries.get_profile()

        assert result is not None
        assert len(result["experience"]) == 1
        assert result["experience"][0]["title"] == "Developer"

    def test_list_profiles_success(self, mock_neo4j_connection):
        """Test successful profile list retrieval."""
        mock_session = mock_neo4j_connection.session.return_value
        mock_tx = Mock()
        mock_result = Mock()
        mock_record1 = Mock()
        mock_record1.get = Mock(
            side_effect=lambda key, default=None: {
                "name": "John Doe",
                "updated_at": "2024-01-01T00:00:00",
            }.get(key, default)
        )
        mock_record2 = Mock()
        mock_record2.get = Mock(
            side_effect=lambda key, default=None: {
                "name": "Jane Smith",
                "updated_at": "2024-01-02T00:00:00",
            }.get(key, default)
        )
        mock_result.__iter__ = Mock(return_value=iter([mock_record1, mock_record2]))
        mock_tx.run.return_value = mock_result

        setup_mock_session_for_read(mock_session, mock_tx)

        result = queries.list_profiles()

        assert result is not None
        assert len(result) == 2
        assert result[0]["name"] == "John Doe"
        assert result[0]["updated_at"] == "2024-01-01T00:00:00"
        assert result[1]["name"] == "Jane Smith"
        assert result[1]["updated_at"] == "2024-01-02T00:00:00"

    def test_list_profiles_empty(self, mock_neo4j_connection):
        """Test profile list when no profiles exist."""
        mock_session = mock_neo4j_connection.session.return_value
        mock_tx = Mock()
        mock_result = Mock()
        mock_result.__iter__ = Mock(return_value=iter([]))
        mock_tx.run.return_value = mock_result

        setup_mock_session_for_read(mock_session, mock_tx)

        result = queries.list_profiles()

        assert result is not None
        assert len(result) == 0

    def test_get_profile_by_updated_at_success(self, mock_neo4j_connection):
        """Test successful profile retrieval by updated_at."""
        mock_session = mock_neo4j_connection.session.return_value
        mock_result_data = {
            "person": {
                "name": "John Doe",
                "email": "john@example.com",
            },
            "profile": {
                "updated_at": "2024-01-01T00:00:00",
            },
            "experiences": [],
            "educations": [],
            "skills": [],
        }
        mock_tx, _ = create_mock_tx_with_result(mock_result_data)

        setup_mock_session_for_read(mock_session, mock_tx)

        result = queries.get_profile_by_updated_at("2024-01-01T00:00:00")

        assert result is not None
        assert result["personal_info"]["name"] == "John Doe"
        assert result["updated_at"] == "2024-01-01T00:00:00"

    def test_get_profile_by_updated_at_not_found(self, mock_neo4j_connection):
        """Test profile retrieval by updated_at when not found."""
        mock_session = mock_neo4j_connection.session.return_value
        mock_tx, _ = create_mock_tx_with_result(None)

        setup_mock_session_for_read(mock_session, mock_tx)

        result = queries.get_profile_by_updated_at("2024-01-01T00:00:00")

        assert result is None
