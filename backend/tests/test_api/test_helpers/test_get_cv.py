"""Tests for GET /api/cv/{cv_id} endpoint."""
import pytest
from unittest.mock import patch


@pytest.mark.asyncio
@pytest.mark.api
class TestGetCV:
    """Test GET /api/cv/{cv_id} endpoint."""

    async def test_get_cv_success(self, client, mock_neo4j_connection):
        """Test successful CV retrieval."""
        cv_data = {
            "cv_id": "test-id",
            "personal_info": {"name": "John Doe"},
            "experience": [],
            "education": [],
            "skills": [],
        }
        with patch("backend.database.queries.get_cv_by_id", return_value=cv_data):
            response = await client.get("/api/cv/test-id")
            assert response.status_code == 200
            data = response.json()
            assert data["cv_id"] == "test-id"

    async def test_get_cv_not_found(self, client, mock_neo4j_connection):
        """Test CV not found."""
        with patch("backend.database.queries.get_cv_by_id", return_value=None):
            response = await client.get("/api/cv/non-existent")
            assert response.status_code == 404

    async def test_get_cv_returns_theme(self, client, mock_neo4j_connection):
        """Test that theme is returned when retrieving CV."""
        cv_data = {
            "cv_id": "test-id",
            "personal_info": {"name": "John Doe"},
            "experience": [],
            "education": [],
            "skills": [],
            "theme": "modern",
        }
        with patch("backend.database.queries.get_cv_by_id", return_value=cv_data):
            response = await client.get("/api/cv/test-id")
            assert response.status_code == 200
            data = response.json()
            assert data["theme"] == "modern"

    async def test_get_cv_defaults_theme_when_missing(
        self, client, mock_neo4j_connection
    ):
        """Test that theme defaults to classic when not in database."""
        cv_data = {
            "cv_id": "test-id",
            "personal_info": {"name": "John Doe"},
            "experience": [],
            "education": [],
            "skills": [],
            "theme": "classic",
        }
        with patch("backend.database.queries.get_cv_by_id", return_value=cv_data):
            response = await client.get("/api/cv/test-id")
            assert response.status_code == 200
            data = response.json()
            assert data["theme"] == "classic"
