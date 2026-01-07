"""Tests for GET /api/cover-letters endpoint."""

import pytest
from unittest.mock import patch


@pytest.mark.asyncio
@pytest.mark.api
class TestListCoverLetters:
    """Test GET /api/cover-letters endpoint."""

    async def test_list_cover_letters_success(self, client, mock_neo4j_connection):
        """Test successful cover letter listing."""
        with patch("backend.app_helpers.routes.cover_letter.endpoints.list_cover_letters") as mock_list:
            mock_list.return_value = {
                "cover_letters": [],
                "total": 0
            }
            response = await client.get("/api/cover-letters")
            assert response.status_code == 200

    async def test_list_cover_letters_with_pagination(self, client, mock_neo4j_connection):
        """Test cover letter listing with pagination."""
        with patch("backend.app_helpers.routes.cover_letter.endpoints.list_cover_letters") as mock_list:
            mock_list.return_value = {
                "cover_letters": [],
                "total": 0
            }
            response = await client.get("/api/cover-letters?limit=10&offset=5")
            assert response.status_code == 200

    async def test_list_cover_letters_with_search(self, client, mock_neo4j_connection):
        """Test cover letter listing with search."""
        with patch("backend.app_helpers.routes.cover_letter.endpoints.list_cover_letters") as mock_list:
            mock_list.return_value = {
                "cover_letters": [],
                "total": 0
            }
            response = await client.get("/api/cover-letters?search=Tech%20Corp")
            assert response.status_code == 200

    async def test_list_cover_letters_database_error(self, client, mock_neo4j_connection):
        """Test list cover letters with database error."""
        with patch("backend.app_helpers.routes.cover_letter.endpoints.list_cover_letters") as mock_list:
            mock_list.side_effect = Exception("Database error")

            response = await client.get("/api/cover-letters")
            assert response.status_code == 500
            data = response.json()
            assert "Failed to list cover letters" in data["detail"]
