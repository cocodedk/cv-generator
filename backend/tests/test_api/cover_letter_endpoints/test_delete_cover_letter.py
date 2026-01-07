"""Tests for DELETE /api/cover-letters/{cover_letter_id} endpoint."""

import pytest
from unittest.mock import patch


@pytest.mark.asyncio
@pytest.mark.api
class TestDeleteCoverLetter:
    """Test DELETE /api/cover-letters/{cover_letter_id} endpoint."""

    async def test_delete_cover_letter_success(self, client, mock_neo4j_connection):
        """Test successful cover letter deletion."""
        with patch("backend.app_helpers.routes.cover_letter.endpoints.delete_cover_letter") as mock_delete:
            mock_delete.return_value = True

            response = await client.delete("/api/cover-letters/test-id")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"

    async def test_delete_cover_letter_not_found(self, client, mock_neo4j_connection):
        """Test deleting non-existent cover letter."""
        with patch("backend.app_helpers.routes.cover_letter.endpoints.delete_cover_letter") as mock_delete:
            mock_delete.return_value = False  # Indicates not found

            response = await client.delete("/api/cover-letters/non-existent-id")
            assert response.status_code == 404
            data = response.json()
            assert "Cover letter not found" in data["detail"]

    async def test_delete_cover_letter_database_error(self, client, mock_neo4j_connection):
        """Test delete cover letter with database error."""
        with patch("backend.app_helpers.routes.cover_letter.endpoints.delete_cover_letter") as mock_delete:
            mock_delete.side_effect = Exception("Database error")

            response = await client.delete("/api/cover-letters/test-id")
            assert response.status_code == 500
            data = response.json()
            assert "Failed to delete cover letter" in data["detail"]
