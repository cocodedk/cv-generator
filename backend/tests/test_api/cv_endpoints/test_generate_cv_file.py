"""Tests for POST /api/cv/{cv_id}/generate-docx endpoint."""
import contextlib
import pytest
from unittest.mock import patch


@pytest.mark.asyncio
@pytest.mark.api
class TestGenerateCVFile:
    """Test POST /api/cv/{cv_id}/generate-docx endpoint."""

    async def test_generate_cv_file_uses_theme_from_db(
        self, client, mock_neo4j_connection
    ):
        """Test that generate DOCX CV file uses theme from database."""
        cv_data = {
            "cv_id": "test-cv-id",
            "personal_info": {"name": "John Doe"},
            "experience": [],
            "education": [],
            "skills": [],
            "theme": "minimal",
        }
        with contextlib.ExitStack() as stack:
            stack.enter_context(patch("backend.database.queries.get_cv_by_id", return_value=cv_data))
            stack.enter_context(patch("backend.database.queries.set_cv_filename", return_value=True))
            mock_generate = stack.enter_context(
                patch(
                    "backend.services.cv_file_service.CVFileService.generate_docx_for_cv",
                    return_value="cv_test.docx",
                )
            )
            response = await client.post("/api/cv/test-cv-id/generate-docx")
            assert response.status_code == 200
            call_args = mock_generate.call_args
            assert call_args is not None
            cv_dict = call_args[0][1]
            assert cv_dict["theme"] == "minimal"

    async def test_generate_cv_file_defaults_theme_when_missing(
        self, client, mock_neo4j_connection
    ):
        """Test that generate DOCX CV file defaults to classic when theme missing."""
        cv_data = {
            "cv_id": "test-cv-id",
            "personal_info": {"name": "John Doe"},
            "experience": [],
            "education": [],
            "skills": [],
            # No theme field
        }
        with contextlib.ExitStack() as stack:
            stack.enter_context(patch("backend.database.queries.get_cv_by_id", return_value=cv_data))
            stack.enter_context(patch("backend.database.queries.set_cv_filename", return_value=True))
            mock_generate = stack.enter_context(
                patch(
                    "backend.services.cv_file_service.CVFileService.generate_docx_for_cv",
                    return_value="cv_test.docx",
                )
            )
            response = await client.post("/api/cv/test-cv-id/generate-docx")
            assert response.status_code == 200
            call_args = mock_generate.call_args
            assert call_args is not None
            cv_dict = call_args[0][1]
            assert cv_dict["theme"] == "classic"
