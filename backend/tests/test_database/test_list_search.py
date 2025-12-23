"""Tests for search_cvs function."""
from unittest.mock import Mock
from backend.database import queries


class TestSearchCVs:
    """Test search_cvs function."""

    def test_search_cvs_by_skills(self, mock_neo4j_connection):
        """Test search by skills."""
        mock_session = mock_neo4j_connection.session.return_value
        mock_record = Mock()
        mock_record.__iter__ = Mock(
            return_value=iter(
                [
                    {
                        "cv": {"id": "cv1", "created_at": "2024-01-01"},
                        "person_name": "John Doe",
                    }
                ]
            )
        )
        mock_session.run.return_value = mock_record

        result = queries.search_cvs(skills=["Python", "JavaScript"])

        assert len(result) == 1
        assert result[0]["cv_id"] == "cv1"
        mock_session.run.assert_called_once()

    def test_search_cvs_by_experience_keywords(self, mock_neo4j_connection):
        """Test search by experience keywords."""
        mock_session = mock_neo4j_connection.session.return_value
        mock_record = Mock()
        mock_record.__iter__ = Mock(
            return_value=iter(
                [
                    {
                        "cv": {"id": "cv2", "created_at": "2024-01-02"},
                        "person_name": "Jane Doe",
                    }
                ]
            )
        )
        mock_session.run.return_value = mock_record

        result = queries.search_cvs(experience_keywords=["Developer", "Engineer"])

        assert len(result) == 1
        assert result[0]["cv_id"] == "cv2"

    def test_search_cvs_by_education_keywords(self, mock_neo4j_connection):
        """Test search by education keywords."""
        mock_session = mock_neo4j_connection.session.return_value
        mock_record = Mock()
        mock_record.__iter__ = Mock(
            return_value=iter(
                [
                    {
                        "cv": {"id": "cv3", "created_at": "2024-01-03"},
                        "person_name": "Bob Smith",
                    }
                ]
            )
        )
        mock_session.run.return_value = mock_record

        result = queries.search_cvs(education_keywords=["Computer Science"])

        assert len(result) == 1
        assert result[0]["cv_id"] == "cv3"

    def test_search_cvs_multiple_criteria(self, mock_neo4j_connection):
        """Test search with multiple criteria."""
        mock_session = mock_neo4j_connection.session.return_value
        mock_record = Mock()
        mock_record.__iter__ = Mock(
            return_value=iter(
                [
                    {
                        "cv": {"id": "cv4", "created_at": "2024-01-04"},
                        "person_name": "Alice Brown",
                    }
                ]
            )
        )
        mock_session.run.return_value = mock_record

        result = queries.search_cvs(
            skills=["Python"], experience_keywords=["Developer"]
        )

        assert len(result) == 1

    def test_search_cvs_no_criteria_returns_empty(self, mock_neo4j_connection):
        """Test search with no criteria returns empty list."""
        result = queries.search_cvs()

        assert result == []

    def test_search_cvs_empty_results(self, mock_neo4j_connection):
        """Test search returns empty list when no matches."""
        mock_session = mock_neo4j_connection.session.return_value
        mock_record = Mock()
        mock_record.__iter__ = Mock(return_value=iter([]))
        mock_session.run.return_value = mock_record

        result = queries.search_cvs(skills=["Nonexistent"])

        assert result == []
