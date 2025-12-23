"""Tests for file download endpoint."""
import pytest
from pathlib import Path
from unittest.mock import patch


@pytest.mark.asyncio
@pytest.mark.api
class TestDownloadCV:
    """Test GET /api/download/{filename} endpoint."""

    async def test_download_cv_success(self, client, temp_output_dir):
        """Test successful file download."""
        # Create a test file
        test_file = temp_output_dir / "test_cv.odt"
        test_file.write_text("test content")

        import backend.app
        original_output_dir = backend.app.output_dir
        backend.app.output_dir = temp_output_dir
        try:
            response = await client.get("/api/download/test_cv.odt")
            assert response.status_code == 200
            assert response.headers["content-type"] == "application/vnd.oasis.opendocument.text"
        finally:
            backend.app.output_dir = original_output_dir

    async def test_download_cv_not_found(self, client, temp_output_dir):
        """Test download non-existent file."""
        import backend.app
        original_output_dir = backend.app.output_dir
        backend.app.output_dir = temp_output_dir
        try:
            response = await client.get("/api/download/non_existent.odt")
            assert response.status_code == 404
        finally:
            backend.app.output_dir = original_output_dir

    async def test_download_cv_path_traversal_attempt(self, client, temp_output_dir):
        """Test path traversal prevention."""
        import backend.app
        original_output_dir = backend.app.output_dir
        backend.app.output_dir = temp_output_dir
        try:
            # Test various path traversal attempts
            # Note: FastAPI normalizes paths before route matching, so paths with "../"
            # get normalized and don't match the route, returning 404 (which is secure).
            # Paths that do match the route are validated by the endpoint logic.
            malicious_paths = [
                "../test.odt",
                "../../test.odt",
                "..\\test.odt",
                "/etc/passwd",
                "test/../test.odt"
            ]

            for path in malicious_paths:
                response = await client.get(f"/api/download/{path}")
                # FastAPI normalizes paths before route matching, so these return 404
                # which is still secure - they cannot access files outside the directory.
                # The endpoint validation would catch any that make it through.
                assert response.status_code in [400, 404], \
                    f"Path '{path}' should return 400 (validation) or 404 (route not matched), got {response.status_code}"
        finally:
            backend.app.output_dir = original_output_dir

    async def test_download_cv_invalid_extension(self, client, temp_output_dir):
        """Test download with invalid file extension."""
        import backend.app
        original_output_dir = backend.app.output_dir
        backend.app.output_dir = temp_output_dir
        try:
            response = await client.get("/api/download/test.txt")
            assert response.status_code == 400
        finally:
            backend.app.output_dir = original_output_dir

    async def test_download_cv_only_odt_allowed(self, client, temp_output_dir):
        """Test that only .odt files are allowed."""
        test_file = temp_output_dir / "test_cv.odt"
        test_file.write_text("test")

        import backend.app
        original_output_dir = backend.app.output_dir
        backend.app.output_dir = temp_output_dir
        try:
            response = await client.get("/api/download/test_cv.odt")
            assert response.status_code == 200
        finally:
            backend.app.output_dir = original_output_dir
