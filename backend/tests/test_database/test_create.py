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
        # create_cv now makes multiple query calls (CV, Person, Experience, Education, Skills)
        assert mock_tx.run.call_count >= 1

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

    def test_create_cv_with_theme(self, mock_neo4j_connection):
        """Test CV creation with theme provided."""
        data = {
            "personal_info": {"name": "John Doe"},
            "experience": [],
            "education": [],
            "skills": [],
            "theme": "modern",
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
        # Verify theme was passed to the first query (CV node creation)
        call_args_list = mock_tx.run.call_args_list
        assert len(call_args_list) > 0
        first_call = call_args_list[0]
        assert first_call is not None
        assert first_call[1]["theme"] == "modern"

    def test_create_cv_defaults_theme_when_missing(self, mock_neo4j_connection):
        """Test CV creation defaults to classic theme when not provided."""
        data = {
            "personal_info": {"name": "John Doe"},
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
        # Verify theme defaults to classic in the first query (CV node creation)
        call_args_list = mock_tx.run.call_args_list
        assert len(call_args_list) > 0
        first_call = call_args_list[0]
        assert first_call is not None
        assert first_call[1]["theme"] == "classic"

    def test_create_cv_with_all_themes(self, mock_neo4j_connection):
        """Test CV creation with all valid theme values."""
        themes = [
            "accented",
            "classic",
            "colorful",
            "creative",
            "elegant",
            "executive",
            "minimal",
            "modern",
            "professional",
            "tech",
        ]
        for theme in themes:
            data = {
                "personal_info": {"name": "John Doe"},
                "experience": [],
                "education": [],
                "skills": [],
                "theme": theme,
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
            # Verify theme was passed correctly in the first query (CV node creation)
            call_args_list = mock_tx.run.call_args_list
            assert len(call_args_list) > 0
            first_call = call_args_list[0]
            assert first_call is not None
            assert first_call[1]["theme"] == theme

    def test_create_cv_with_target_company_and_role(self, mock_neo4j_connection):
        """Test CV creation with target_company and target_role provided."""
        data = {
            "personal_info": {"name": "John Doe"},
            "experience": [],
            "education": [],
            "skills": [],
            "target_company": "Google",
            "target_role": "Senior Developer",
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
        # Verify target_company and target_role were passed to the first query (CV node creation)
        call_args_list = mock_tx.run.call_args_list
        assert len(call_args_list) > 0
        first_call = call_args_list[0]
        assert first_call is not None
        # Use .get() to safely access kwargs
        kwargs = first_call[1] if len(first_call) > 1 else {}
        assert kwargs.get("target_company") == "Google"
        assert kwargs.get("target_role") == "Senior Developer"

    def test_create_cv_with_none_target_fields(self, mock_neo4j_connection):
        """Test CV creation with None target_company and target_role."""
        data = {
            "personal_info": {"name": "John Doe"},
            "experience": [],
            "education": [],
            "skills": [],
            "target_company": None,
            "target_role": None,
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
        # Verify None values are passed correctly
        call_args_list = mock_tx.run.call_args_list
        assert len(call_args_list) > 0
        first_call = call_args_list[0]
        assert first_call is not None
        # Use .get() to safely access kwargs
        kwargs = first_call[1] if len(first_call) > 1 else {}
        assert kwargs.get("target_company") is None
        assert kwargs.get("target_role") is None
