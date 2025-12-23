"""Health check routes."""
from fastapi import APIRouter
from backend.database.connection import Neo4jConnection

router = APIRouter()


@router.get("/api/health")
async def health_check():
    """Health check endpoint."""
    db_connected = Neo4jConnection.verify_connectivity()
    return {
        "status": "healthy" if db_connected else "unhealthy",
        "database": "connected" if db_connected else "disconnected",
    }
