"""Tests for list_cvs query."""
from unittest.mock import Mock
from backend.database import queries


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
                        "filename": "cv1.html",
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

    def test_list_cvs_returns_target_company_and_role(self, mock_neo4j_connection):
        """Test CV listing returns target_company and target_role when present."""
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
                        "target_company": "Google",
                        "target_role": "Senior Developer",
                    }
                ]
            )
        )

        mock_session.run.side_effect = [mock_count_record, mock_list_record]

        result = queries.list_cvs(limit=10, offset=0)

        assert result["total"] == 1
        assert len(result["cvs"]) == 1
        assert result["cvs"][0]["target_company"] == "Google"
        assert result["cvs"][0]["target_role"] == "Senior Developer"

    def test_list_cvs_returns_none_for_missing_target_fields(self, mock_neo4j_connection):
        """Test CV listing returns None for target_company and target_role when missing."""
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

        result = queries.list_cvs(limit=10, offset=0)

        assert result["total"] == 1
        assert len(result["cvs"]) == 1
        assert result["cvs"][0].get("target_company") is None
        assert result["cvs"][0].get("target_role") is None
