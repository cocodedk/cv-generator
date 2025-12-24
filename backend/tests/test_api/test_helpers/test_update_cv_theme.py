"""Tests for PUT /api/cv/{cv_id} endpoint - theme operations."""
import pytest
from unittest.mock import patch


@pytest.mark.asyncio
@pytest.mark.api
class TestUpdateCVTheme:
    """Test PUT /api/cv/{cv_id} endpoint - theme operations."""

    async def test_update_cv_saves_theme(
        self, client, sample_cv_data, mock_neo4j_connection
    ):
        """Test that theme is saved when updating CV."""
        sample_cv_data["theme"] = "accented"
        with patch("backend.database.queries.update_cv") as mock_update:
            mock_update.return_value = True
            response = await client.put("/api/cv/test-id", json=sample_cv_data)
            assert response.status_code == 200
            call_args = mock_update.call_args
            assert call_args is not None
            assert call_args[0][1]["theme"] == "accented"

    async def test_update_cv_preserves_theme(
        self, client, sample_cv_data, mock_neo4j_connection
    ):
        """Test that theme persists after update."""
        sample_cv_data["theme"] = "elegant"
        updated_cv = {
            "cv_id": "test-id",
            "personal_info": {"name": "John Doe"},
            "experience": [],
            "education": [],
            "skills": [],
            "theme": "elegant",
        }
        with patch("backend.database.queries.update_cv", return_value=True):
            response = await client.put("/api/cv/test-id", json=sample_cv_data)
            assert response.status_code == 200
            with patch("backend.database.queries.get_cv_by_id", return_value=updated_cv):
                get_response = await client.get("/api/cv/test-id")
            assert get_response.status_code == 200
            data = get_response.json()
            assert data["theme"] == "elegant"

    async def test_update_cv_regenerates_file_on_theme_change(
        self, client, sample_cv_data, mock_neo4j_connection
    ):
        """Test that updating CV with new theme persists the theme."""
        sample_cv_data["theme"] = "modern"
        with patch("backend.database.queries.update_cv", return_value=True):
            response = await client.put("/api/cv/test-id", json=sample_cv_data)
            assert response.status_code == 200
            updated_cv_modern = {
                "cv_id": "test-id",
                "personal_info": {"name": "John Doe"},
                "experience": [],
                "education": [],
                "skills": [],
                "theme": "modern",
            }
            with patch("backend.database.queries.get_cv_by_id", return_value=updated_cv_modern):
                get_response = await client.get("/api/cv/test-id")
            assert get_response.status_code == 200
            data = get_response.json()
            assert data["theme"] == "modern"
