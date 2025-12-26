"""Tests for DOCX CV endpoints."""
from unittest.mock import patch
import pytest
from backend.app import app


@pytest.mark.asyncio
@pytest.mark.api
class TestDocxRoutes:
    """Test DOCX-specific endpoints."""

    async def test_generate_cv_docx(self, client, sample_cv_data):
        """Ensure DOCX generation endpoint returns filename."""
        with patch(
            "backend.database.queries.create_cv", return_value="docx-cv-id"
        ):
            with patch(
                "backend.services.cv_file_service.CVFileService.generate_docx_for_cv",
                return_value="cv_docx.docx",
            ):
                response = await client.post(
                    "/api/generate-cv-docx", json=sample_cv_data
                )
        assert response.status_code == 200
        assert response.json()["filename"].endswith(".docx")

    async def test_download_docx(self, client, temp_output_dir):
        """Ensure DOCX download endpoint returns file."""
        test_file = temp_output_dir / "test_cv.docx"
        test_file.write_text("docx content")

        cv_data = {
            "cv_id": "docx-id",
            "personal_info": {"name": "John Doe"},
            "experience": [],
            "education": [],
            "skills": [],
            "theme": "classic",
            "filename": "test_cv.docx",
        }

        original_output_dir = getattr(app.state, "output_dir", None)
        app.state.output_dir = temp_output_dir
        try:
            with patch(
                "backend.database.queries.get_cv_by_filename",
                return_value=cv_data,
            ):
                with patch(
                    "backend.services.cv_file_service.CVFileService.generate_docx_for_cv",
                    return_value="test_cv.docx",
                ):
                    response = await client.get(
                        "/api/download-docx/test_cv.docx"
                    )
                    assert response.status_code == 200
                    assert (
                        response.headers["content-type"]
                        == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
        finally:
            app.state.output_dir = original_output_dir
