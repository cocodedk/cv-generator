"""Tests for GET /api/cover-letters/{cover_letter_id} endpoint."""

import pytest
from unittest.mock import patch


@pytest.mark.asyncio
@pytest.mark.api
class TestGetCoverLetter:
    """Test GET /api/cover-letters/{cover_letter_id} endpoint."""

    async def test_get_cover_letter_success(self, client, mock_neo4j_connection):
        """Test successful cover letter retrieval."""
        mock_cover_letter = {
            "cover_letter_id": "test-id",
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00",
            "job_description": "We need a Python developer.",
            "company_name": "Tech Corp",
            "hiring_manager_name": None,
            "company_address": None,
            "tone": "professional",
            "cover_letter_html": "<p>Test letter</p>",
            "cover_letter_text": "Test letter",
            "highlights_used": [],
            "selected_experiences": [],
            "selected_skills": ["Python"]
        }

        with patch("backend.app_helpers.routes.cover_letter.endpoints.get_cover_letter_by_id") as mock_get:
            mock_get.return_value = mock_cover_letter

            response = await client.get("/api/cover-letters/test-id")
            assert response.status_code == 200
            data = response.json()
            assert data["cover_letter_id"] == "test-id"

    async def test_get_cover_letter_not_found(self, client, mock_neo4j_connection):
        """Test getting non-existent cover letter."""
        response = await client.get("/api/cover-letters/non-existent-id")
        assert response.status_code == 404
        data = response.json()
        assert "Cover letter not found" in data["detail"]

    async def test_get_cover_letter_database_error(self, client, mock_neo4j_connection):
        """Test get cover letter with database error."""
        with patch("backend.app_helpers.routes.cover_letter.endpoints.get_cover_letter_by_id") as mock_get:
            mock_get.side_effect = Exception("Database error")

            response = await client.get("/api/cover-letters/test-id")
            assert response.status_code == 500
            data = response.json()
            assert "Failed to get cover letter" in data["detail"]
