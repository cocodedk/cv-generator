"""Tests for GET /api/cvs endpoint."""
import pytest
from unittest.mock import patch


@pytest.mark.asyncio
@pytest.mark.api
class TestListCVs:
    """Test GET /api/cvs endpoint."""

    async def test_list_cvs_success(self, client, mock_neo4j_connection):
        """Test successful CV listing."""
        list_data = {
            "cvs": [
                {
                    "cv_id": "id1",
                    "created_at": "2024-01-01T00:00:00",
                    "updated_at": "2024-01-01T00:00:00",
                    "person_name": "John Doe",
                }
            ],
            "total": 1,
        }
        with patch("backend.database.queries.list_cvs", return_value=list_data):
            response = await client.get("/api/cvs")
            assert response.status_code == 200
            data = response.json()
            assert data["total"] == 1
            assert len(data["cvs"]) == 1

    async def test_list_cvs_with_pagination(self, client, mock_neo4j_connection):
        """Test CV listing with pagination."""
        list_data = {"cvs": [], "total": 0}
        with patch("backend.database.queries.list_cvs", return_value=list_data):
            response = await client.get("/api/cvs?limit=10&offset=0")
            assert response.status_code == 200

    async def test_list_cvs_with_search(self, client, mock_neo4j_connection):
        """Test CV listing with search."""
        list_data = {"cvs": [], "total": 0}
        with patch("backend.database.queries.list_cvs", return_value=list_data):
            response = await client.get("/api/cvs?search=John")
            assert response.status_code == 200

    async def test_list_cvs_returns_target_company_and_role(self, client, mock_neo4j_connection):
        """Test CV listing returns target_company and target_role when present."""
        list_data = {
            "cvs": [
                {
                    "cv_id": "id1",
                    "created_at": "2024-01-01T00:00:00",
                    "updated_at": "2024-01-01T00:00:00",
                    "person_name": "John Doe",
                    "target_company": "Google",
                    "target_role": "Senior Developer",
                }
            ],
            "total": 1,
        }
        with patch("backend.database.queries.list_cvs", return_value=list_data):
            response = await client.get("/api/cvs")
            assert response.status_code == 200
            data = response.json()
            assert data["cvs"][0]["target_company"] == "Google"
            assert data["cvs"][0]["target_role"] == "Senior Developer"
