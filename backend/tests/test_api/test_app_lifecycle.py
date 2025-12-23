"""Tests for app lifecycle events."""
import pytest
from unittest.mock import patch
from backend.app import app
from backend.database.connection import Neo4jConnection


class TestAppLifespan:
    """Test app lifespan context manager."""

    @pytest.mark.asyncio
    async def test_lifespan_startup_success(self):
        """Test lifespan startup with successful connection."""
        with patch.object(Neo4jConnection, "verify_connectivity", return_value=True):
            async with app.router.lifespan_context(app):
                Neo4jConnection.verify_connectivity.assert_called()

    @pytest.mark.asyncio
    async def test_lifespan_startup_retry_success(self):
        """Test lifespan startup with retry logic."""
        with patch.object(
            Neo4jConnection, "verify_connectivity", side_effect=[False, False, True]
        ):
            with patch("time.sleep"):
                async with app.router.lifespan_context(app):
                    assert Neo4jConnection.verify_connectivity.call_count == 3

    @pytest.mark.asyncio
    async def test_lifespan_startup_max_retries_fails(self):
        """Test lifespan startup fails after max retries."""
        with patch.object(Neo4jConnection, "verify_connectivity", return_value=False):
            with patch("time.sleep"):
                with pytest.raises(Exception, match="Failed to connect"):
                    async with app.router.lifespan_context(app):
                        pass
                assert Neo4jConnection.verify_connectivity.call_count == 5

    @pytest.mark.asyncio
    async def test_lifespan_shutdown_closes_connection(self):
        """Test lifespan shutdown closes database connection."""
        with patch.object(Neo4jConnection, "verify_connectivity", return_value=True):
            with patch.object(Neo4jConnection, "close") as mock_close:
                async with app.router.lifespan_context(app):
                    pass
                mock_close.assert_called_once()
