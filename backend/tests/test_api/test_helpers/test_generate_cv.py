"""Tests for POST /api/generate-cv-docx endpoint."""
import pytest
from unittest.mock import patch


@pytest.mark.asyncio
@pytest.mark.api
class TestGenerateCV:
    """Test POST /api/generate-cv-docx endpoint."""

    async def test_generate_cv_success(
        self, client, sample_cv_data, mock_neo4j_connection
    ):
        """Test successful DOCX CV generation."""
        with patch("backend.database.queries.create_cv", return_value="test-cv-id"):
            with patch(
                "backend.database.queries.set_cv_filename", return_value=True
            ):
                with patch(
                    "backend.services.cv_file_service.CVFileService.generate_docx_for_cv",
                    return_value="cv_test.docx",
                ):
                    response = await client.post(
                        "/api/generate-cv-docx", json=sample_cv_data
                    )
                    assert response.status_code == 200
                    data = response.json()
                    assert data["cv_id"] == "test-cv-id"
                    assert data["status"] == "success"
                    assert data["filename"].endswith(".docx")

    async def test_generate_cv_validation_error(self, client):
        """Test CV generation with invalid data."""
        invalid_data = {"personal_info": {"name": ""}}  # Invalid: empty name
        response = await client.post(
            "/api/generate-cv-docx", json=invalid_data
        )
        assert response.status_code == 422

    async def test_generate_cv_server_error(
        self, client, sample_cv_data, mock_neo4j_connection
    ):
        """Test CV generation with server error."""
        with patch(
            "backend.database.queries.create_cv",
            side_effect=Exception("Database error"),
        ):
            response = await client.post(
                "/api/generate-cv-docx", json=sample_cv_data
            )
            assert response.status_code == 500

    async def test_generate_cv_saves_theme(
        self, client, sample_cv_data, mock_neo4j_connection
    ):
        """Test that theme is saved when generating CV."""
        sample_cv_data["theme"] = "elegant"
        with patch("backend.database.queries.create_cv") as mock_create:
            mock_create.return_value = "test-cv-id"
            with patch(
                "backend.database.queries.set_cv_filename", return_value=True
            ):
                with patch(
                    "backend.services.cv_file_service.CVFileService.generate_docx_for_cv",
                    return_value="cv_test.docx",
                ):
                    response = await client.post(
                        "/api/generate-cv-docx", json=sample_cv_data
                    )
                    assert response.status_code == 200
                    # Verify theme was passed to create_cv
                    call_args = mock_create.call_args
                    assert call_args is not None
                    assert call_args[0][0]["theme"] == "elegant"
