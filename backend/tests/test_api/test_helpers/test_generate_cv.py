"""Tests for POST /api/generate-cv endpoint."""
import pytest
from unittest.mock import patch


@pytest.mark.asyncio
@pytest.mark.api
class TestGenerateCV:
    """Test POST /api/generate-cv endpoint."""

    async def test_generate_cv_success(
        self, client, sample_cv_data, mock_neo4j_connection, temp_output_dir
    ):
        """Test successful CV generation."""
        from backend.app import app

        original_output_dir = app.state.output_dir
        app.state.output_dir = temp_output_dir
        try:
            with patch("backend.database.queries.create_cv", return_value="test-cv-id"):
                with patch(
                    "backend.database.queries.set_cv_filename", return_value=True
                ):
                    with patch(
                        "backend.cv_generator.generator.CVGenerator.generate"
                    ) as mock_gen:
                        mock_gen.return_value = str(temp_output_dir / "cv_test.odt")
                        response = await client.post(
                            "/api/generate-cv", json=sample_cv_data
                        )
                        assert response.status_code == 200
                        data = response.json()
                        assert data["cv_id"] == "test-cv-id"
                        assert data["status"] == "success"
                        assert "filename" in data
        finally:
            app.state.output_dir = original_output_dir

    async def test_generate_cv_validation_error(self, client):
        """Test CV generation with invalid data."""
        invalid_data = {"personal_info": {"name": ""}}  # Invalid: empty name
        response = await client.post("/api/generate-cv", json=invalid_data)
        assert response.status_code == 422

    async def test_generate_cv_server_error(
        self, client, sample_cv_data, mock_neo4j_connection
    ):
        """Test CV generation with server error."""
        with patch(
            "backend.database.queries.create_cv",
            side_effect=Exception("Database error"),
        ):
            response = await client.post("/api/generate-cv", json=sample_cv_data)
            assert response.status_code == 500

    async def test_generate_cv_saves_theme(
        self, client, sample_cv_data, mock_neo4j_connection, temp_output_dir
    ):
        """Test that theme is saved when generating CV."""
        from backend.app import app

        original_output_dir = app.state.output_dir
        app.state.output_dir = temp_output_dir
        try:
            sample_cv_data["theme"] = "elegant"
            with patch("backend.database.queries.create_cv") as mock_create:
                mock_create.return_value = "test-cv-id"
                with patch(
                    "backend.database.queries.set_cv_filename", return_value=True
                ):
                    with patch(
                        "backend.cv_generator.generator.CVGenerator.generate"
                    ) as mock_gen:
                        mock_gen.return_value = str(temp_output_dir / "cv_test.odt")
                        response = await client.post(
                            "/api/generate-cv", json=sample_cv_data
                        )
                        assert response.status_code == 200
                        # Verify theme was passed to create_cv
                        call_args = mock_create.call_args
                        assert call_args is not None
                        assert call_args[0][0]["theme"] == "elegant"
        finally:
            app.state.output_dir = original_output_dir
