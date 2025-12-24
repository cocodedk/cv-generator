"""CV-related routes."""
import logging
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, Request
from slowapi import Limiter
from backend.models import CVData, CVResponse, CVListResponse
from backend.database import queries
from backend.services.cv_file_service import CVFileService

logger = logging.getLogger(__name__)


def create_cv_router(  # noqa: C901
    limiter: Limiter,
    cv_file_service: CVFileService,
    output_dir: Optional[Path] = None,
) -> APIRouter:
    """Create and return CV router with dependencies."""
    router = APIRouter()

    @router.post("/api/save-cv", response_model=CVResponse)
    @limiter.limit("20/minute")
    async def save_cv(request: Request, cv_data: CVData):
        """Save CV data to Neo4j without generating file."""
        try:
            cv_dict = cv_data.model_dump()
            cv_id = queries.create_cv(cv_dict)
            return CVResponse(cv_id=cv_id, status="success")
        except Exception as e:
            logger.error("Failed to save CV", exc_info=e)
            raise HTTPException(status_code=500, detail="Failed to save CV")

    @router.get("/api/cv/{cv_id}")
    async def get_cv(cv_id: str):
        """Retrieve CV data from Neo4j."""
        cv = queries.get_cv_by_id(cv_id)
        if not cv:
            raise HTTPException(status_code=404, detail="CV not found")
        return cv

    @router.get("/api/cvs", response_model=CVListResponse)
    async def list_cvs(
        limit: int = Query(50, ge=1, le=100),
        offset: int = Query(0, ge=0),
        search: Optional[str] = None,
    ):
        """List all saved CVs with pagination."""
        try:
            result = queries.list_cvs(limit=limit, offset=offset, search=search)
            return CVListResponse(**result)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(
                "Failed to list CVs: %s (limit=%d, offset=%d, search=%s)",
                str(e),
                limit,
                offset,
                search,
                exc_info=e,
            )
            raise HTTPException(status_code=500, detail="Failed to list CVs")

    @router.delete("/api/cv/{cv_id}")
    async def delete_cv(cv_id: str):
        """Delete CV from Neo4j."""
        success = queries.delete_cv(cv_id)
        if not success:
            raise HTTPException(status_code=404, detail="CV not found")
        return {"status": "success", "message": "CV deleted"}

    @router.put("/api/cv/{cv_id}", response_model=CVResponse)
    async def update_cv_endpoint(cv_id: str, cv_data: CVData):
        """Update CV data."""
        try:
            cv_dict = cv_data.model_dump(exclude_none=False)
            # Ensure theme is always present
            if "theme" not in cv_dict or cv_dict["theme"] is None:
                cv_dict["theme"] = "classic"
            theme = cv_dict["theme"]
            logger.debug(
                "Update CV endpoint for %s: theme=%s",
                cv_id,
                theme,
            )
            success = queries.update_cv(cv_id, cv_dict)
            if not success:
                raise HTTPException(status_code=404, detail="CV not found")
            return CVResponse(cv_id=cv_id, status="success")
        except HTTPException:
            raise
        except Exception as e:
            logger.error("Failed to update CV %s", cv_id, exc_info=e)
            raise HTTPException(status_code=500, detail="Failed to update CV")

    return router
