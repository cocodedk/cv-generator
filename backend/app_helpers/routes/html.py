"""HTML-specific CV routes."""
import logging
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse
from slowapi import Limiter
from backend.models import CVData, CVResponse
from backend.database import queries
from backend.services.cv_file_service import CVFileService

logger = logging.getLogger(__name__)


def create_html_router(
    limiter: Limiter,
    cv_file_service: CVFileService,
    output_dir: Optional[Path] = None,
) -> APIRouter:
    """Create and return HTML router with dependencies."""
    router = APIRouter()

    @router.post("/api/generate-cv-html", response_model=CVResponse)
    @limiter.limit("10/minute")
    async def generate_cv_html(request: Request, cv_data: CVData):
        """Generate HTML file from CV data and save to Neo4j."""
        return await _handle_generate_cv_html(cv_data, cv_file_service)

    @router.get("/api/download-html/{filename}")
    async def download_html(request: Request, filename: str):
        """Download generated HTML file."""
        return await _handle_download_html(
            request, filename, output_dir, cv_file_service
        )

    @router.post("/api/cv/{cv_id}/generate-html", response_model=CVResponse)
    @limiter.limit("10/minute")
    async def generate_cv_html_file(request: Request, cv_id: str):
        """Generate HTML file for an existing CV."""
        return await _handle_generate_cv_html_file(cv_id, cv_file_service)

    return router


async def _handle_generate_cv_html(
    cv_data: CVData, cv_file_service: CVFileService
) -> CVResponse:
    """Handle generate CV HTML request."""
    try:
        cv_dict = cv_data.model_dump(exclude_none=False)
        _ensure_theme(cv_dict)
        cv_id = queries.create_cv(cv_dict)
        filename = cv_file_service.generate_file_for_cv(cv_id, cv_dict)
        return CVResponse(cv_id=cv_id, filename=filename, status="success")
    except Exception as exc:
        logger.error("Failed to generate HTML CV", exc_info=exc)
        raise HTTPException(status_code=500, detail="Failed to generate HTML CV")


async def _handle_download_html(
    request: Request,
    filename: str,
    output_dir: Optional[Path],
    cv_file_service: CVFileService,
) -> FileResponse:
    """Handle download HTML file request."""
    current_output_dir = _resolve_output_dir(request, output_dir)

    # Accept both HTML and DOCX files (for backward compatibility with old filenames)
    if not filename.endswith((".html", ".docx")):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type - only .html and .docx files allowed",
        )

    _validate_filename(filename)

    # Look up CV by filename (could be .docx from old data or .html from new)
    cv = queries.get_cv_by_filename(filename)
    if not cv:
        raise HTTPException(status_code=404, detail="CV not found for filename")

    cv_id = cv["cv_id"]
    cv_dict = cv_file_service.prepare_cv_dict(cv)

    # Always generate HTML file, regardless of requested filename extension
    # If filename ends with .docx (old data), generate HTML with .html extension
    html_filename = (
        filename.replace(".docx", ".html") if filename.endswith(".docx") else filename
    )

    # Log warning to prevent confusion with showcase files
    logger.warning(
        "Generating download file %s for CV %s - this is NOT for GitHub Pages publishing. "
        "Use showcase files from frontend/public/showcase/ for publishing.",
        html_filename, cv_id
    )

    cv_file_service.generate_file_for_cv(cv_id, cv_dict)
    file_path = _resolve_file_path(current_output_dir, html_filename)
    return _build_html_response(file_path, html_filename)


async def _handle_generate_cv_html_file(
    cv_id: str, cv_file_service: CVFileService
) -> CVResponse:
    """Handle generate HTML file for existing CV."""
    try:
        cv = queries.get_cv_by_id(cv_id)
        if not cv:
            raise HTTPException(status_code=404, detail="CV not found")
        cv_dict = cv_file_service.prepare_cv_dict(cv)
        filename = cv_file_service.generate_file_for_cv(cv_id, cv_dict)
        return CVResponse(cv_id=cv_id, filename=filename, status="success")
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Failed to generate HTML CV file for %s", cv_id, exc_info=exc)
        raise HTTPException(status_code=500, detail="Failed to generate HTML CV file")


def _ensure_theme(cv_dict: dict) -> None:
    if "theme" not in cv_dict or cv_dict["theme"] is None:
        cv_dict["theme"] = "classic"


def _resolve_output_dir(request: Request, output_dir: Optional[Path]) -> Path:
    app_state_output_dir = getattr(request.app.state, "output_dir", None)
    if output_dir is not None:
        current_output_dir = app_state_output_dir or output_dir
    else:
        current_output_dir = app_state_output_dir
    if current_output_dir is None:
        raise HTTPException(status_code=500, detail="Output directory not configured")
    return current_output_dir


def _validate_filename(filename: str) -> None:
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")


def _resolve_file_path(output_dir: Path, filename: str) -> Path:
    file_path = output_dir / filename
    try:
        file_path.resolve().relative_to(output_dir.resolve())
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid file path")
    if not file_path.exists():
        raise HTTPException(status_code=500, detail="File generation failed")
    return file_path


def _build_html_response(file_path: Path, filename: str) -> FileResponse:
    file_mtime = file_path.stat().st_mtime
    # Ensure filename ends with .html
    if not filename.endswith(".html"):
        filename = filename.replace(".docx", ".html")
    response = FileResponse(
        path=str(file_path),
        filename=filename,
        media_type="text/html",
    )
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    response.headers["ETag"] = f'"{int(file_mtime)}"'
    response.headers["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response
