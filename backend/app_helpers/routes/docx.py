"""DOCX-specific CV routes."""
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


def create_docx_router(
    limiter: Limiter,
    cv_file_service: CVFileService,
    output_dir: Optional[Path] = None,
) -> APIRouter:
    """Create and return DOCX router with dependencies."""
    router = APIRouter()

    @router.post("/api/generate-cv-docx", response_model=CVResponse)
    @limiter.limit("10/minute")
    async def generate_cv_docx(request: Request, cv_data: CVData):
        """Generate DOCX file from CV data and save to Neo4j."""
        return await _handle_generate_cv_docx(cv_data, cv_file_service)

    @router.get("/api/download-docx/{filename}")
    async def download_docx(request: Request, filename: str):
        """Download generated DOCX file."""
        return await _handle_download_docx(
            request, filename, output_dir, cv_file_service
        )

    @router.post("/api/cv/{cv_id}/generate-docx", response_model=CVResponse)
    @limiter.limit("10/minute")
    async def generate_cv_docx_file(request: Request, cv_id: str):
        """Generate DOCX file for an existing CV."""
        return await _handle_generate_cv_docx_file(cv_id, cv_file_service)

    return router


async def _handle_generate_cv_docx(
    cv_data: CVData, cv_file_service: CVFileService
) -> CVResponse:
    """Handle generate CV DOCX request."""
    try:
        cv_dict = cv_data.model_dump(exclude_none=False)
        _ensure_theme(cv_dict)
        cv_id = queries.create_cv(cv_dict)
        filename = cv_file_service.generate_docx_for_cv(cv_id, cv_dict)
        return CVResponse(cv_id=cv_id, filename=filename, status="success")
    except Exception as exc:
        logger.error("Failed to generate DOCX CV", exc_info=exc)
        raise HTTPException(status_code=500, detail="Failed to generate DOCX CV")


async def _handle_download_docx(
    request: Request,
    filename: str,
    output_dir: Optional[Path],
    cv_file_service: CVFileService,
) -> FileResponse:
    """Handle download DOCX file request."""
    current_output_dir = _resolve_output_dir(request, output_dir)

    # Only accept DOCX files
    if not filename.endswith(".docx"):
        raise HTTPException(status_code=400, detail="Invalid file type - only .docx files allowed")

    _validate_filename(filename)

    # Look up CV by filename
    cv = queries.get_cv_by_filename(filename)
    if not cv:
        raise HTTPException(status_code=404, detail="CV not found for filename")

    cv_id = cv["cv_id"]
    cv_dict = cv_file_service.prepare_cv_dict(cv)

    # Generate DOCX file
    cv_file_service.generate_docx_for_cv(cv_id, cv_dict)
    file_path = _resolve_file_path(current_output_dir, filename)
    return _build_docx_response(file_path, filename)


async def _handle_generate_cv_docx_file(
    cv_id: str, cv_file_service: CVFileService
) -> CVResponse:
    """Handle generate DOCX file for existing CV."""
    try:
        cv = queries.get_cv_by_id(cv_id)
        if not cv:
            raise HTTPException(status_code=404, detail="CV not found")
        cv_dict = cv_file_service.prepare_cv_dict(cv)
        filename = cv_file_service.generate_docx_for_cv(cv_id, cv_dict)
        return CVResponse(cv_id=cv_id, filename=filename, status="success")
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Failed to generate DOCX CV file for %s", cv_id, exc_info=exc)
        raise HTTPException(
            status_code=500, detail="Failed to generate DOCX CV file"
        )


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
        raise HTTPException(
            status_code=500, detail="Output directory not configured"
        )
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


def _build_docx_response(file_path: Path, filename: str) -> FileResponse:
    file_mtime = file_path.stat().st_mtime
    response = FileResponse(
        path=str(file_path),
        filename=filename,
        media_type=(
            "application/vnd.openxmlformats-officedocument"
            ".wordprocessingml.document"
        ),
    )
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    response.headers["ETag"] = f'"{int(file_mtime)}"'
    return response
