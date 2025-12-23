"""Lifespan context manager for FastAPI application."""
import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from backend.database.connection import Neo4jConnection

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown."""
    # Startup
    logger.info("Starting up CV Generator API...")
    max_retries = 5
    retry_count = 0

    while retry_count < max_retries:
        if Neo4jConnection.verify_connectivity():
            logger.info("Successfully connected to Neo4j database")
            break
        retry_count += 1
        logger.warning(
            f"Failed to connect to Neo4j database (attempt {retry_count}/{max_retries})"
        )
        if retry_count < max_retries:
            await asyncio.sleep(2)

    if retry_count >= max_retries:
        logger.error("Failed to connect to Neo4j database after multiple attempts")
        raise RuntimeError("Failed to connect to Neo4j database")

    yield

    # Shutdown
    Neo4jConnection.close()
