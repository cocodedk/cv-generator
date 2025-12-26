"""Tests for HTML CV endpoints."""
from unittest.mock import patch
import pytest
from backend.app import app


@pytest.mark.asyncio
@pytest.mark.api
class TestHtmlRoutes:
    """Test HTML-specific endpoints."""

    async def test_generate_cv_html(self, client, sample_cv_data):
        """Ensure HTML generation endpoint returns filename."""
        with patch(
            "backend.database.queries.create_cv", return_value="html-cv-id"
        ):
            with patch(
                "backend.services.cv_file_service.CVFileService.generate_file_for_cv",
                return_value="cv_html.html",
            ):
                response = await client.post(
                    "/api/generate-cv-html", json=sample_cv_data
                )
        assert response.status_code == 200
        assert response.json()["filename"].endswith(".html")

    async def test_download_html(self, client, temp_output_dir):
        """Ensure HTML download endpoint returns file."""
        test_file = temp_output_dir / "test_cv.html"
        test_file.write_text("<html>test content</html>")

        cv_data = {
            "cv_id": "html-id",
            "personal_info": {"name": "John Doe"},
            "experience": [],
            "education": [],
            "skills": [],
            "theme": "classic",
            "filename": "test_cv.html",
        }

        original_output_dir = getattr(app.state, "output_dir", None)
        app.state.output_dir = temp_output_dir
        try:
            with patch(
                "backend.database.queries.get_cv_by_filename",
                return_value=cv_data,
            ):
                with patch(
                    "backend.services.cv_file_service.CVFileService.generate_file_for_cv",
                    return_value="test_cv.html",
                ):
                    response = await client.get(
                        "/api/download-html/test_cv.html"
                    )
                    assert response.status_code == 200
                    assert response.headers["content-type"].startswith("text/html")
        finally:
            app.state.output_dir = original_output_dir
