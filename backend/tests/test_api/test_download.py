"""Tests for HTML and DOCX download endpoints."""
import pytest
from unittest.mock import patch
from backend.app import app


@pytest.mark.asyncio
@pytest.mark.api
class TestDownloadHtml:
    """Test GET /api/download-html/{filename} endpoint."""

    async def test_download_html_success(
        self, client, temp_output_dir, mock_neo4j_connection
    ):
        """Test successful HTML file download with regeneration."""
        test_file = temp_output_dir / "test_cv.html"
        test_file.write_text("<html>test content</html>")

        cv_data = {
            "cv_id": "test-id",
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
                "backend.database.queries.get_cv_by_filename", return_value=cv_data
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

    async def test_download_html_not_found(
        self, client, temp_output_dir, mock_neo4j_connection
    ):
        """Test download non-existent HTML file."""
        original_output_dir = getattr(app.state, "output_dir", None)
        app.state.output_dir = temp_output_dir
        try:
            with patch(
                "backend.database.queries.get_cv_by_filename", return_value=None
            ):
                response = await client.get(
                    "/api/download-html/non_existent.html"
                )
                assert response.status_code == 404
        finally:
            app.state.output_dir = original_output_dir

    async def test_download_html_invalid_extension(self, client, temp_output_dir):
        """Test download HTML with invalid file extension."""
        original_output_dir = getattr(app.state, "output_dir", None)
        app.state.output_dir = temp_output_dir
        try:
            response = await client.get("/api/download-html/test.txt")
            assert response.status_code == 400
        finally:
            app.state.output_dir = original_output_dir


@pytest.mark.asyncio
@pytest.mark.api
class TestDownloadDocx:
    """Test GET /api/download-docx/{filename} endpoint."""

    async def test_download_docx_success(
        self, client, temp_output_dir, mock_neo4j_connection
    ):
        """Test successful DOCX file download with regeneration."""
        test_file = temp_output_dir / "test_cv.docx"
        test_file.write_text("docx content")

        cv_data = {
            "cv_id": "test-id",
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
                "backend.database.queries.get_cv_by_filename", return_value=cv_data
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

    async def test_download_docx_not_found(
        self, client, temp_output_dir, mock_neo4j_connection
    ):
        """Test download non-existent DOCX file."""
        original_output_dir = getattr(app.state, "output_dir", None)
        app.state.output_dir = temp_output_dir
        try:
            with patch(
                "backend.database.queries.get_cv_by_filename", return_value=None
            ):
                response = await client.get(
                    "/api/download-docx/non_existent.docx"
                )
                assert response.status_code == 404
        finally:
            app.state.output_dir = original_output_dir

    async def test_download_docx_invalid_extension(self, client, temp_output_dir):
        """Test download DOCX with invalid file extension."""
        original_output_dir = getattr(app.state, "output_dir", None)
        app.state.output_dir = temp_output_dir
        try:
            response = await client.get("/api/download-docx/test.txt")
            assert response.status_code == 400
        finally:
            app.state.output_dir = original_output_dir

    async def test_download_docx_path_traversal_attempt(self, client, temp_output_dir):
        """Test path traversal prevention for DOCX downloads."""
        original_output_dir = getattr(app.state, "output_dir", None)
        app.state.output_dir = temp_output_dir
        try:
            malicious_paths = [
                "../test.docx",
                "../../test.docx",
                "..\\test.docx",
                "/etc/passwd",
                "test/../test.docx",
            ]

            for path in malicious_paths:
                response = await client.get(f"/api/download-docx/{path}")
                assert response.status_code in [
                    400,
                    404,
                ], f"Path '{path}' should return 400 (validation) or 404 (route not matched), got {response.status_code}"
        finally:
            app.state.output_dir = original_output_dir
