"""Tests for DELETE /api/cv/{cv_id} endpoint."""
import pytest
from unittest.mock import patch


@pytest.mark.asyncio
@pytest.mark.api
class TestDeleteCV:
    """Test DELETE /api/cv/{cv_id} endpoint."""

    async def test_delete_cv_success(self, client, mock_neo4j_connection):
        """Test successful CV deletion."""
        with patch("backend.database.queries.delete_cv", return_value=True):
            response = await client.delete("/api/cv/test-id")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"

    async def test_delete_cv_not_found(self, client, mock_neo4j_connection):
        """Test delete non-existent CV."""
        with patch("backend.database.queries.delete_cv", return_value=False):
            response = await client.delete("/api/cv/non-existent")
            assert response.status_code == 404
