"""CV-related routes."""
import logging
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import FileResponse
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

    @router.post("/api/generate-cv", response_model=CVResponse)
    @limiter.limit("10/minute")
    async def generate_cv(request: Request, cv_data: CVData):
        """Generate ODT file from CV data and save to Neo4j."""
        try:
            cv_dict = cv_data.model_dump(exclude_none=False)
            # Ensure theme is always present
            if "theme" not in cv_dict or cv_dict["theme"] is None:
                cv_dict["theme"] = "classic"
            theme = cv_dict["theme"]
            logger.debug(
                "Generate CV endpoint: theme=%s, cv_dict keys=%s",
                theme,
                list(cv_dict.keys()),
            )
            cv_id = queries.create_cv(cv_dict)
            filename = cv_file_service.generate_file_for_cv(cv_id, cv_dict)
            return CVResponse(cv_id=cv_id, filename=filename, status="success")
        except Exception as e:
            logger.error("Failed to generate CV", exc_info=e)
            raise HTTPException(status_code=500, detail="Failed to generate CV")

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

    @router.get("/api/download/{filename}")
    async def download_cv(request: Request, filename: str):
        """Download generated CV file. Regenerates file on each request to ensure latest data."""
        # Use output_dir parameter as primary source, fall back to app attributes if None
        # Allow app.state.output_dir to override for test scenarios
        app_state_output_dir = getattr(request.app.state, "output_dir", None)
        if output_dir is not None:
            # Parameter is primary, but allow app.state override for tests
            current_output_dir = app_state_output_dir or output_dir
        else:
            # Parameter is None, fall back to app.state
            current_output_dir = app_state_output_dir

        if current_output_dir is None:
            raise HTTPException(
                status_code=500, detail="Output directory not configured"
            )

        # Validate filename to prevent path traversal
        if ".." in filename or "/" in filename or "\\" in filename:
            raise HTTPException(status_code=400, detail="Invalid filename")

        # Only allow .odt files
        if not filename.endswith(".odt"):
            raise HTTPException(status_code=400, detail="Invalid file type")

        # Find CV by filename and regenerate file with latest data
        cv = queries.get_cv_by_filename(filename)
        if not cv:
            raise HTTPException(status_code=404, detail="CV not found for filename")

        cv_id = cv["cv_id"]
        logger.debug(
            "Regenerating CV file for download: cv_id=%s, filename=%s, theme=%s",
            cv_id,
            filename,
            cv.get("theme", "classic"),
        )

        # Regenerate file with latest data from database
        cv_dict = cv_file_service.prepare_cv_dict(cv)
        cv_file_service.generate_file_for_cv(cv_id, cv_dict)

        file_path = current_output_dir / filename

        # Ensure file is within output directory (prevent path traversal)
        try:
            file_path.resolve().relative_to(current_output_dir.resolve())
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid file path")

        if not file_path.exists():
            raise HTTPException(status_code=500, detail="File generation failed")

        # Get file modification time for ETag
        file_mtime = file_path.stat().st_mtime

        response = FileResponse(
            path=str(file_path),
            filename=filename,
            media_type="application/vnd.oasis.opendocument.text",
        )

        # Set headers to prevent caching and ensure dynamic downloads
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        # Add ETag based on file modification time for cache validation
        response.headers["ETag"] = f'"{int(file_mtime)}"'

        return response

    @router.post("/api/cv/{cv_id}/generate", response_model=CVResponse)
    @limiter.limit("10/minute")
    async def generate_cv_file(request: Request, cv_id: str):
        """Generate ODT file for an existing CV."""
        try:
            cv = queries.get_cv_by_id(cv_id)
            if not cv:
                raise HTTPException(status_code=404, detail="CV not found")

            theme_from_db = cv.get("theme", "classic")
            logger.debug(
                "Generate CV file endpoint for %s: theme from DB=%s, cv keys=%s",
                cv_id,
                theme_from_db,
                list(cv.keys()),
            )

            cv_dict = cv_file_service.prepare_cv_dict(cv)
            filename = cv_file_service.generate_file_for_cv(cv_id, cv_dict)

            return CVResponse(cv_id=cv_id, filename=filename, status="success")
        except HTTPException:
            raise
        except Exception as e:
            logger.error("Failed to generate CV file for %s", cv_id, exc_info=e)
            raise HTTPException(status_code=500, detail="Failed to generate CV file")

    @router.put("/api/cv/{cv_id}", response_model=CVResponse)
    async def update_cv_endpoint(cv_id: str, cv_data: CVData):
        """Update CV data and regenerate ODT file."""
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

            # Regenerate ODT file with updated data
            cv = queries.get_cv_by_id(cv_id)
            if not cv:
                raise HTTPException(status_code=404, detail="CV not found after update")

            cv_dict_for_generation = cv_file_service.prepare_cv_dict(cv)
            filename = cv_file_service.generate_file_for_cv(
                cv_id, cv_dict_for_generation
            )

            return CVResponse(cv_id=cv_id, filename=filename, status="success")
        except HTTPException:
            raise
        except Exception as e:
            logger.error("Failed to update CV %s", cv_id, exc_info=e)
            raise HTTPException(status_code=500, detail="Failed to update CV")

    return router
