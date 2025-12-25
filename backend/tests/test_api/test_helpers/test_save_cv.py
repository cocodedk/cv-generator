"""Tests for POST /api/save-cv endpoint."""
import pytest
from unittest.mock import patch


@pytest.mark.asyncio
@pytest.mark.api
class TestSaveCV:
    """Test POST /api/save-cv endpoint."""

    async def test_save_cv_success(self, client, sample_cv_data, mock_neo4j_connection):
        """Test successful CV save."""
        with patch("backend.database.queries.create_cv", return_value="test-cv-id") as mock_create:
            response = await client.post("/api/save-cv", json=sample_cv_data)
            assert response.status_code == 200
            data = response.json()
            assert data["cv_id"] == "test-cv-id"
            assert data["status"] == "success"
            call_args = mock_create.call_args
            assert call_args is not None
            assert call_args[0][0]["experience"][0]["projects"][0]["name"] == "Internal Platform"

    async def test_save_cv_validation_error(self, client):
        """Test CV save with invalid data."""
        invalid_data = {"personal_info": {}}  # Missing required name
        response = await client.post("/api/save-cv", json=invalid_data)
        assert response.status_code == 422

    async def test_save_cv_saves_theme(
        self, client, sample_cv_data, mock_neo4j_connection
    ):
        """Test that theme is saved when saving CV."""
        sample_cv_data["theme"] = "minimal"
        with patch("backend.database.queries.create_cv") as mock_create:
            mock_create.return_value = "test-cv-id"
            response = await client.post("/api/save-cv", json=sample_cv_data)
            assert response.status_code == 200
            # Verify theme was passed to create_cv
            call_args = mock_create.call_args
            assert call_args is not None
            assert call_args[0][0]["theme"] == "minimal"
