"""Tests for health check endpoint."""
import pytest
from unittest.mock import patch


@pytest.mark.asyncio
@pytest.mark.api
class TestHealthEndpoint:
    """Test health check endpoint."""

    async def test_health_check_connected(self, client, mock_neo4j_connection):
        """Test health check when database is connected."""
        with patch(
            "backend.database.connection.Neo4jConnection.verify_connectivity",
            return_value=True,
        ):
            response = await client.get("/api/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert data["database"] == "connected"

    async def test_health_check_disconnected(self, client):
        """Test health check when database is disconnected."""
        with patch(
            "backend.database.connection.Neo4jConnection.verify_connectivity",
            return_value=False,
        ):
            response = await client.get("/api/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "unhealthy"
            assert data["database"] == "disconnected"
