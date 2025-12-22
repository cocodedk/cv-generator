"""Neo4j database connection management."""
import os
from typing import Optional
from neo4j import GraphDatabase, Driver
from dotenv import load_dotenv

load_dotenv()


class Neo4jConnection:
    """Manages Neo4j database connection."""

    _driver: Optional[Driver] = None
    _database: Optional[str] = None

    @classmethod
    def get_driver(cls) -> Driver:
        """Get or create Neo4j driver instance."""
        if cls._driver is None:
            uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
            user = os.getenv("NEO4J_USER", "neo4j")
            password = os.getenv("NEO4J_PASSWORD", "cvpassword")
            database = os.getenv("NEO4J_DATABASE", "neo4j")

            cls._driver = GraphDatabase.driver(
                uri,
                auth=(user, password)
            )
            cls._database = database
        return cls._driver

    @classmethod
    def get_database(cls) -> str:
        """Get the database name."""
        if cls._database is None:
            cls._database = os.getenv("NEO4J_DATABASE", "neo4j")
        return cls._database

    @classmethod
    def close(cls):
        """Close the Neo4j driver connection."""
        if cls._driver:
            cls._driver.close()
            cls._driver = None

    @classmethod
    def verify_connectivity(cls) -> bool:
        """Verify Neo4j connection is working."""
        try:
            driver = cls.get_driver()
            driver.verify_connectivity()
            return True
        except Exception:
            return False
