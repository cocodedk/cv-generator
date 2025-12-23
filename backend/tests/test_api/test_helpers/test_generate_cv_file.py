"""Tests for POST /api/cv/{cv_id}/generate endpoint."""
import pytest
from unittest.mock import patch


@pytest.mark.asyncio
@pytest.mark.api
class TestGenerateCVFile:
    """Test POST /api/cv/{cv_id}/generate endpoint."""

    async def test_generate_cv_file_uses_theme_from_db(
        self, client, mock_neo4j_connection, temp_output_dir
    ):
        """Test that generate CV file uses theme from database."""
        from backend.app import app

        original_output_dir = app.state.output_dir
        app.state.output_dir = temp_output_dir
        try:
            cv_data = {
                "cv_id": "test-cv-id",
                "personal_info": {"name": "John Doe"},
                "experience": [],
                "education": [],
                "skills": [],
                "theme": "minimal",
            }
            with patch("backend.database.queries.get_cv_by_id", return_value=cv_data):
                with patch(
                    "backend.database.queries.set_cv_filename", return_value=True
                ):
                    with patch(
                        "backend.cv_generator.generator.CVGenerator.generate"
                    ) as mock_gen:
                        mock_gen.return_value = str(temp_output_dir / "cv_test.odt")
                        response = await client.post("/api/cv/test-cv-id/generate")
                        assert response.status_code == 200
                        # Verify generator was called with theme
                        assert mock_gen.called
                        call_args = mock_gen.call_args
                        assert call_args is not None
                        cv_dict = call_args[0][0]
                        assert cv_dict["theme"] == "minimal"
        finally:
            app.state.output_dir = original_output_dir

    async def test_generate_cv_file_defaults_theme_when_missing(
        self, client, mock_neo4j_connection, temp_output_dir
    ):
        """Test that generate CV file defaults to classic when theme missing."""
        from backend.app import app

        original_output_dir = app.state.output_dir
        app.state.output_dir = temp_output_dir
        try:
            cv_data = {
                "cv_id": "test-cv-id",
                "personal_info": {"name": "John Doe"},
                "experience": [],
                "education": [],
                "skills": [],
                # No theme field
            }
            with patch("backend.database.queries.get_cv_by_id", return_value=cv_data):
                with patch(
                    "backend.database.queries.set_cv_filename", return_value=True
                ):
                    with patch(
                        "backend.cv_generator.generator.CVGenerator.generate"
                    ) as mock_gen:
                        mock_gen.return_value = str(temp_output_dir / "cv_test.odt")
                        response = await client.post("/api/cv/test-cv-id/generate")
                        assert response.status_code == 200
                        # Verify generator was called with default theme
                        assert mock_gen.called
                        call_args = mock_gen.call_args
                        assert call_args is not None
                        cv_dict = call_args[0][0]
                        assert cv_dict["theme"] == "classic"
        finally:
            app.state.output_dir = original_output_dir
