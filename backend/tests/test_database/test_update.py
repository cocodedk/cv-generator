"""Tests for update_cv query."""
import copy
import pytest
from unittest.mock import Mock
from backend.database import queries
from backend.database.connection import Neo4jConnection


class TestUpdateCV:
    """Test update_cv query."""

    def test_update_cv_success(self, mock_neo4j_connection, sample_cv_data):
        """Test successful CV update."""
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
        mock_session.write_transaction.assert_called_once()
        # After refactoring, update_cv makes multiple focused query calls
        assert (
            mock_tx.run.call_count >= 6
        )  # timestamp, delete, person, exp, edu, skills, verify

    def test_update_cv_not_found(self, mock_neo4j_connection, sample_cv_data):
        """Test update non-existent CV."""
        mock_session = mock_neo4j_connection.session.return_value
        mock_result = Mock()
        mock_result.single.return_value = None
        mock_tx = Mock()
        mock_tx.run.return_value = mock_result

        def write_transaction_side_effect(work):
            return work(mock_tx)

        mock_session.write_transaction.side_effect = write_transaction_side_effect

        success = queries.update_cv("non-existent", sample_cv_data)

        assert success is False

    @pytest.mark.integration
    def test_update_cv_integration(self, sample_cv_data):
        """Test CV update against real Neo4j to catch Cypher syntax errors."""
        if not Neo4jConnection.verify_connectivity():
            pytest.skip("Neo4j is not available for integration tests.")

        # Create a CV first
        cv_id = queries.create_cv(sample_cv_data)
        assert cv_id is not None

        try:
            # Update the CV with modified data
            updated_data = copy.deepcopy(sample_cv_data)
            updated_data["personal_info"]["name"] = "Updated Name"
            updated_data["personal_info"]["summary"] = "Updated summary"
            updated_data["experience"] = [
                {
                    "title": "Lead Developer",
                    "company": "New Corp",
                    "start_date": "2021-01",
                    "end_date": "2024-12",
                    "description": "Led teams across multiple initiatives.",
                    "location": "San Francisco",
                    "projects": [
                        {
                            "name": "Migration Program",
                            "description": "Moved legacy services to a new platform.",
                            "technologies": ["Python", "Neo4j"],
                            "highlights": ["Delivered the migration with zero downtime."],
                        }
                    ],
                }
            ]
            updated_data["education"] = []
            updated_data["skills"] = [
                {"name": "TypeScript", "category": "Programming", "level": "Expert"}
            ]

            # This would have failed with the variable redeclaration bug
            success = queries.update_cv(cv_id, updated_data)
            assert success is True

            # Verify the update worked by reading the CV back
            result = queries.get_cv_by_id(cv_id)
            assert result is not None
            assert result["personal_info"]["name"] == "Updated Name"
            assert result["personal_info"]["summary"] == "Updated summary"
            assert len(result["experience"]) == 1
            assert result["experience"][0]["title"] == "Lead Developer"
            assert len(result["education"]) == 0
            assert len(result["skills"]) == 1
            assert result["skills"][0]["name"] == "TypeScript"
        finally:
            # Clean up
            queries.delete_cv(cv_id)

    def test_update_cv_saves_theme(self, mock_neo4j_connection, sample_cv_data):
        """Test that theme is saved when updating CV."""
        mock_session = mock_neo4j_connection.session.return_value
        mock_result = Mock()
        mock_result.single.return_value = {"cv_id": "test-id"}
        mock_tx = Mock()
        mock_tx.run.return_value = mock_result

        def write_transaction_side_effect(work):
            return work(mock_tx)

        mock_session.write_transaction.side_effect = write_transaction_side_effect

        sample_cv_data["theme"] = "elegant"
        success = queries.update_cv("test-id", sample_cv_data)

        assert success is True
        # Verify theme was passed to _update_cv_timestamp
        # The first call should be _update_cv_timestamp which sets theme
        update_calls = [
            call for call in mock_tx.run.call_args_list if "theme" in str(call)
        ]
        assert len(update_calls) > 0

    @pytest.mark.integration
    def test_update_cv_changes_theme(self, sample_cv_data):
        """Test that theme can be changed from one value to another."""
        if not Neo4jConnection.verify_connectivity():
            pytest.skip("Neo4j is not available for integration tests.")

        # Create a CV with one theme
        sample_cv_data["theme"] = "modern"
        cv_id = queries.create_cv(sample_cv_data)
        assert cv_id is not None

        try:
            # Verify initial theme
            result = queries.get_cv_by_id(cv_id)
            assert result is not None
            assert result["theme"] == "modern"

            # Update with different theme
            updated_data = copy.deepcopy(sample_cv_data)
            updated_data["theme"] = "elegant"
            success = queries.update_cv(cv_id, updated_data)
            assert success is True

            # Verify theme was changed
            result = queries.get_cv_by_id(cv_id)
            assert result is not None
            assert result["theme"] == "elegant"
        finally:
            # Clean up
            queries.delete_cv(cv_id)

    @pytest.mark.integration
    def test_update_cv_integration_with_theme(self, sample_cv_data):
        """Test CV update integration including theme persistence."""
        if not Neo4jConnection.verify_connectivity():
            pytest.skip("Neo4j is not available for integration tests.")

        # Create a CV with theme
        sample_cv_data["theme"] = "minimal"
        cv_id = queries.create_cv(sample_cv_data)
        assert cv_id is not None

        try:
            # Update the CV with modified data and different theme
            updated_data = copy.deepcopy(sample_cv_data)
            updated_data["personal_info"]["name"] = "Updated Name"
            updated_data["theme"] = "accented"
            success = queries.update_cv(cv_id, updated_data)
            assert success is True

            # Verify the update worked including theme
            result = queries.get_cv_by_id(cv_id)
            assert result is not None
            assert result["personal_info"]["name"] == "Updated Name"
            assert result["theme"] == "accented"
        finally:
            # Clean up
            queries.delete_cv(cv_id)


class TestSetCVFilename:
    """Test set_cv_filename function."""

    def test_set_cv_filename_success(self, mock_neo4j_connection):
        """Test setting filename successfully."""
        mock_session = mock_neo4j_connection.session.return_value
        mock_result = Mock()
        mock_result.single.return_value = {"cv_id": "test-id"}
        mock_tx = Mock()
        mock_tx.run.return_value = mock_result

        def write_transaction_side_effect(work):
            return work(mock_tx)

        mock_session.write_transaction.side_effect = write_transaction_side_effect

        success = queries.set_cv_filename("test-id", "cv_test.docx")

        assert success is True
        mock_session.write_transaction.assert_called_once()
        mock_tx.run.assert_called_once()

    def test_set_cv_filename_not_found(self, mock_neo4j_connection):
        """Test setting filename for non-existent CV."""
        mock_session = mock_neo4j_connection.session.return_value
        mock_result = Mock()
        mock_result.single.return_value = None
        mock_tx = Mock()
        mock_tx.run.return_value = mock_result

        def write_transaction_side_effect(work):
            return work(mock_tx)

        mock_session.write_transaction.side_effect = write_transaction_side_effect

        success = queries.set_cv_filename("non-existent", "cv_test.docx")

        assert success is False
