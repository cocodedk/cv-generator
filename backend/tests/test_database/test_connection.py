"""Tests for Neo4jConnection class."""
import os
from unittest.mock import Mock, patch
from backend.database.connection import Neo4jConnection


class TestNeo4jConnection:
    """Test Neo4jConnection class."""

    def test_get_driver_creates_on_first_call(self):
        """Test get_driver creates driver on first call."""
        Neo4jConnection._driver = None
        Neo4jConnection._database = None

        with patch("backend.database.connection.GraphDatabase") as mock_graph:
            mock_driver = Mock()
            mock_graph.driver.return_value = mock_driver

            with patch.dict(
                os.environ,
                {
                    "NEO4J_URI": "bolt://localhost:7687",
                    "NEO4J_USER": "neo4j",
                    "NEO4J_PASSWORD": "password",
                    "NEO4J_DATABASE": "testdb",
                },
            ):
                driver = Neo4jConnection.get_driver()

                assert driver is mock_driver
                mock_graph.driver.assert_called_once()

    def test_get_driver_reuses_existing_driver(self):
        """Test get_driver reuses existing driver."""
        mock_driver = Mock()
        Neo4jConnection._driver = mock_driver

        result = Neo4jConnection.get_driver()

        assert result is mock_driver

    def test_get_database_returns_correct_name(self):
        """Test get_database returns correct database name."""
        Neo4jConnection._database = None

        with patch.dict(os.environ, {"NEO4J_DATABASE": "mydb"}):
            db_name = Neo4jConnection.get_database()
            assert db_name == "mydb"

    def test_get_database_uses_cached_value(self):
        """Test get_database uses cached database name."""
        Neo4jConnection._database = "cached_db"

        db_name = Neo4jConnection.get_database()
        assert db_name == "cached_db"

    def test_close_closes_driver_and_resets(self):
        """Test close closes driver and resets state."""
        mock_driver = Mock()
        Neo4jConnection._driver = mock_driver
        Neo4jConnection._database = "testdb"

        Neo4jConnection.close()

        mock_driver.close.assert_called_once()
        assert Neo4jConnection._driver is None

    def test_close_with_no_driver(self):
        """Test close handles case when no driver exists."""
        Neo4jConnection._driver = None

        # Should not raise exception
        Neo4jConnection.close()

    def test_verify_connectivity_success(self):
        """Test verify_connectivity returns True on success."""
        mock_driver = Mock()
        mock_driver.verify_connectivity = Mock()
        Neo4jConnection._driver = mock_driver

        result = Neo4jConnection.verify_connectivity()

        assert result is True
        mock_driver.verify_connectivity.assert_called_once()

    def test_verify_connectivity_failure(self):
        """Test verify_connectivity returns False on failure."""
        mock_driver = Mock()
        mock_driver.verify_connectivity.side_effect = Exception("Connection failed")
        Neo4jConnection._driver = mock_driver

        result = Neo4jConnection.verify_connectivity()

        assert result is False

    def test_verify_connectivity_creates_driver_if_needed(self):
        """Test verify_connectivity creates driver if not exists."""
        Neo4jConnection._driver = None

        with patch("backend.database.connection.GraphDatabase") as mock_graph:
            mock_driver = Mock()
            mock_driver.verify_connectivity = Mock()
            mock_graph.driver.return_value = mock_driver

            with patch.dict(
                os.environ,
                {
                    "NEO4J_URI": "bolt://localhost:7687",
                    "NEO4J_USER": "neo4j",
                    "NEO4J_PASSWORD": "password",
                    "NEO4J_DATABASE": "testdb",
                },
            ):
                result = Neo4jConnection.verify_connectivity()

                assert result is True
                mock_driver.verify_connectivity.assert_called_once()
