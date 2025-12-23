"""Tests for DOCX download endpoint."""
import pytest
from unittest.mock import patch
from backend.app import app


@pytest.mark.asyncio
@pytest.mark.api
class TestDownloadCV:
    """Test GET /api/download-docx/{filename} endpoint."""

    async def test_download_cv_success(
        self, client, temp_output_dir, mock_neo4j_connection
    ):
        """Test successful file download with regeneration."""
        # Create a test file (will be regenerated)
        test_file = temp_output_dir / "test_cv.docx"
        test_file.write_text("test content")

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
                    "backend.services.cv_file_service.CVFileService.generate_file_for_cv",
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

    async def test_download_cv_not_found(
        self, client, temp_output_dir, mock_neo4j_connection
    ):
        """Test download non-existent file."""
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

    async def test_download_cv_path_traversal_attempt(self, client, temp_output_dir):
        """Test path traversal prevention."""
        original_output_dir = getattr(app.state, "output_dir", None)
        app.state.output_dir = temp_output_dir
        try:
            # Test various path traversal attempts
            # Note: FastAPI normalizes paths before route matching, so paths with "../"
            # get normalized and don't match the route, returning 404 (which is secure).
            # Paths that do match the route are validated by the endpoint logic.
            malicious_paths = [
                "../test.docx",
                "../../test.docx",
                "..\\test.docx",
                "/etc/passwd",
                "test/../test.docx",
            ]

            for path in malicious_paths:
                response = await client.get(f"/api/download-docx/{path}")
                # FastAPI normalizes paths before route matching, so these return 404
                # which is still secure - they cannot access files outside the directory.
                # The endpoint validation would catch any that make it through.
                assert response.status_code in [
                    400,
                    404,
                ], f"Path '{path}' should return 400 (validation) or 404 (route not matched), got {response.status_code}"
        finally:
            app.state.output_dir = original_output_dir

    async def test_download_cv_invalid_extension(self, client, temp_output_dir):
        """Test download with invalid file extension."""
        original_output_dir = getattr(app.state, "output_dir", None)
        app.state.output_dir = temp_output_dir
        try:
            response = await client.get("/api/download-docx/test.txt")
            assert response.status_code == 400
        finally:
            app.state.output_dir = original_output_dir

    async def test_download_cv_only_docx_allowed(
        self, client, temp_output_dir, mock_neo4j_connection
    ):
        """Test that only .docx files are allowed."""
        test_file = temp_output_dir / "test_cv.docx"
        test_file.write_text("test")

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
                    "backend.services.cv_file_service.CVFileService.generate_file_for_cv",
                    return_value="test_cv.docx",
                ):
                    response = await client.get(
                        "/api/download-docx/test_cv.docx"
                    )
                    assert response.status_code == 200
        finally:
            app.state.output_dir = original_output_dir
