"""Tests for profile endpoints."""
import pytest
from unittest.mock import patch, Mock
from backend.database import queries


@pytest.mark.asyncio
@pytest.mark.api
class TestSaveProfile:
    """Test POST /api/profile endpoint."""

    async def test_save_profile_success(
        self, client, sample_cv_data, mock_neo4j_connection
    ):
        """Test successful profile save."""
        profile_data = {
            "personal_info": sample_cv_data["personal_info"],
            "experience": sample_cv_data["experience"],
            "education": sample_cv_data["education"],
            "skills": sample_cv_data["skills"],
        }
        with patch("backend.app.queries.save_profile", return_value=True):
            response = await client.post("/api/profile", json=profile_data)
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert "message" in data

    async def test_save_profile_validation_error(self, client):
        """Test profile save with invalid data."""
        invalid_data = {"personal_info": {"name": ""}}  # Invalid: empty name
        response = await client.post("/api/profile", json=invalid_data)
        assert response.status_code == 422

    async def test_save_profile_server_error(
        self, client, sample_cv_data, mock_neo4j_connection
    ):
        """Test profile save with server error."""
        profile_data = {
            "personal_info": sample_cv_data["personal_info"],
            "experience": sample_cv_data["experience"],
            "education": sample_cv_data["education"],
            "skills": sample_cv_data["skills"],
        }
        with patch(
            "backend.app.queries.save_profile", side_effect=Exception("Database error")
        ):
            response = await client.post("/api/profile", json=profile_data)
            assert response.status_code == 500


@pytest.mark.asyncio
@pytest.mark.api
class TestGetProfile:
    """Test GET /api/profile endpoint."""

    async def test_get_profile_success(self, client, mock_neo4j_connection):
        """Test successful profile retrieval."""
        profile_data = {
            "personal_info": {"name": "John Doe", "email": "john@example.com"},
            "experience": [],
            "education": [],
            "skills": [],
            "updated_at": "2024-01-01T00:00:00",
        }
        with patch("backend.app.queries.get_profile", return_value=profile_data):
            response = await client.get("/api/profile")
            assert response.status_code == 200
            data = response.json()
            assert "personal_info" in data
            assert data["personal_info"]["name"] == "John Doe"

    async def test_get_profile_not_found(self, client, mock_neo4j_connection):
        """Test profile not found."""
        with patch("backend.app.queries.get_profile", return_value=None):
            response = await client.get("/api/profile")
            assert response.status_code == 404

    async def test_get_profile_server_error(self, client, mock_neo4j_connection):
        """Test get profile with server error."""
        with patch(
            "backend.app.queries.get_profile", side_effect=Exception("Database error")
        ):
            response = await client.get("/api/profile")
            assert response.status_code == 500


@pytest.mark.asyncio
@pytest.mark.api
class TestDeleteProfile:
    """Test DELETE /api/profile endpoint."""

    async def test_delete_profile_success(self, client, mock_neo4j_connection):
        """Test successful profile deletion."""
        with patch("backend.app.queries.delete_profile", return_value=True):
            response = await client.delete("/api/profile")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert "message" in data

    async def test_delete_profile_not_found(self, client, mock_neo4j_connection):
        """Test delete non-existent profile."""
        with patch("backend.app.queries.delete_profile", return_value=False):
            response = await client.delete("/api/profile")
            assert response.status_code == 404

    async def test_delete_profile_server_error(self, client, mock_neo4j_connection):
        """Test delete profile with server error."""
        with patch(
            "backend.app.queries.delete_profile",
            side_effect=Exception("Database error"),
        ):
            response = await client.delete("/api/profile")
            assert response.status_code == 500
