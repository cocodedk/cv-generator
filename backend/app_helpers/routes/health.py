"""Health check routes."""
from fastapi import APIRouter
from backend.database.connection import Neo4jConnection
from backend.services.cv_file_service import CVFileService


def create_health_router(cv_file_service: CVFileService) -> APIRouter:
    """Create health router with dependencies."""
    router = APIRouter()

    @router.get("/api/health")
    async def health_check():
        """Health check endpoint."""
        db_connected = Neo4jConnection.verify_connectivity()
        return {
            "status": "healthy" if db_connected else "unhealthy",
            "database": "connected" if db_connected else "disconnected",
        }

    @router.post("/api/admin/cleanup-download-files")
    async def cleanup_download_files(max_age_hours: int = 24):
        """Clean up old download files (admin endpoint)."""
        try:
            cleaned_count = cv_file_service.cleanup_old_download_files(max_age_hours)
            return {
                "status": "success",
                "files_cleaned": cleaned_count,
                "max_age_hours": max_age_hours,
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
            }

    return router
