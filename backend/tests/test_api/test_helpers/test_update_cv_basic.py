"""Tests for PUT /api/cv/{cv_id} endpoint - basic operations."""
import pytest
from unittest.mock import patch


@pytest.mark.asyncio
@pytest.mark.api
class TestUpdateCVBasic:
    """Test PUT /api/cv/{cv_id} endpoint - basic operations."""

    async def test_update_cv_success(
        self, client, sample_cv_data, mock_neo4j_connection
    ):
        """Test successful CV update."""
        with patch("backend.database.queries.update_cv", return_value=True):
            response = await client.put("/api/cv/test-id", json=sample_cv_data)
            assert response.status_code == 200
            data = response.json()
            assert data["cv_id"] == "test-id"
            assert data["status"] == "success"

    async def test_update_cv_not_found(
        self, client, sample_cv_data, mock_neo4j_connection
    ):
        """Test update non-existent CV."""
        with patch("backend.database.queries.update_cv", return_value=False):
            response = await client.put("/api/cv/non-existent", json=sample_cv_data)
            assert response.status_code == 404
