"""CV-related routes."""
import logging
import csv
import io
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import StreamingResponse
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
            try:
                cv_file_service.generate_showcase_for_cv(cv_id, cv_dict)
            except Exception as e:
                logger.warning("Failed to generate showcase for %s", cv_id, exc_info=e)
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

    @router.get("/api/cvs/export")
    async def export_cvs(
        format: str = Query("csv", regex="^(csv)$", description="Export format (currently only csv supported)"),
        search: Optional[str] = None,
    ):
        """Export CV list as downloadable file."""
        try:
            # Get all CVs (no pagination for export)
            result = queries.list_cvs(limit=1000, offset=0, search=search)
            cvs = result["cvs"]

            if format == "csv":
                return await _export_cvs_csv(cvs)

            # Future: Add other formats here
            raise HTTPException(status_code=400, detail=f"Unsupported format: {format}")

        except HTTPException:
            raise
        except Exception as e:
            logger.error(
                "Failed to export CVs: %s (format=%s, search=%s)",
                str(e),
                format,
                search,
                exc_info=e,
            )
            raise HTTPException(status_code=500, detail="Failed to export CVs")

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
            # Ensure theme and layout are always present
            if "theme" not in cv_dict or cv_dict["theme"] is None:
                cv_dict["theme"] = "classic"
            if "layout" not in cv_dict or cv_dict["layout"] is None:
                cv_dict["layout"] = "classic-two-column"
            theme = cv_dict["theme"]
            layout = cv_dict["layout"]
            logger.debug(
                "Update CV endpoint for %s: theme=%s, layout=%s",
                cv_id,
                theme,
                layout,
            )
            success = queries.update_cv(cv_id, cv_dict)
            if not success:
                raise HTTPException(status_code=404, detail="CV not found")
            try:
                cv_file_service.generate_showcase_for_cv(cv_id, cv_dict)
            except Exception as e:
                logger.warning("Failed to generate showcase for %s", cv_id, exc_info=e)
            return CVResponse(cv_id=cv_id, status="success")
        except HTTPException:
            raise
        except Exception as e:
            logger.error("Failed to update CV %s", cv_id, exc_info=e)
            raise HTTPException(status_code=500, detail="Failed to update CV")

    @router.post("/api/generate-templates")
    async def generate_templates():
        """Generate featured CV templates from the latest profile."""
        try:
            result = await cv_file_service.generate_featured_templates()
            if result:
                return {
                    "status": "success",
                    "message": f"Generated {len(result['templates'])} templates",
                    "templates": result["templates"],
                    "profile_name": result.get("profile_name")
                }
            else:
                raise HTTPException(status_code=404, detail="No profile found to generate templates from")
        except Exception as e:
            logger.error("Failed to generate templates", exc_info=e)
            raise HTTPException(status_code=500, detail="Failed to generate templates")

    @router.get("/api/cv/download-featured")
    async def download_featured_cv():
        """Download the featured CV as DOCX."""
        try:
            # Get the latest profile
            profile = queries.get_profile()
            if not profile:
                raise HTTPException(status_code=404, detail="No profile found")

            # Generate DOCX from profile
            cv_dict = cv_file_service.prepare_cv_dict(profile)
            cv_dict["layout"] = "section-cards-grid"
            cv_dict["theme"] = "modern"

            # Create a temporary filename
            import uuid
            filename = f"featured-cv-{uuid.uuid4().hex[:8]}.docx"
            output_path = cv_file_service.output_dir / filename

            # Generate the DOCX
            cv_file_service.docx_generator.generate(cv_dict, str(output_path))

            # Return the file
            return StreamingResponse(
                open(output_path, "rb"),
                media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                headers={
                    "Content-Disposition": 'attachment; filename="Professional_CV.docx"',
                    "Cache-Control": "no-cache, no-store, must-revalidate",
                    "Pragma": "no-cache",
                    "Expires": "0"
                }
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error("Failed to download featured CV", exc_info=e)
            raise HTTPException(status_code=500, detail="Failed to download featured CV")

    return router


async def _export_cvs_csv(cvs: list) -> StreamingResponse:
    """Export CVs as CSV file."""
    from datetime import datetime

    def generate_csv():
        """Generate CSV data row by row."""
        # Create CSV writer
        output = io.StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow([
            "CV ID",
            "Person Name",
            "Target Company",
            "Target Role",
            "Created Date",
            "Updated Date",
            "Has File"
        ])

        # Write data rows
        for cv in cvs:
            created_date = ""
            updated_date = ""

            try:
                if cv.get("created_at"):
                    # Parse ISO format and format as readable date
                    dt = datetime.fromisoformat(cv["created_at"].replace('Z', '+00:00'))
                    created_date = dt.strftime("%Y-%m-%d %H:%M:%S")
            except (ValueError, AttributeError):
                created_date = cv.get("created_at", "")

            try:
                if cv.get("updated_at"):
                    # Parse ISO format and format as readable date
                    dt = datetime.fromisoformat(cv["updated_at"].replace('Z', '+00:00'))
                    updated_date = dt.strftime("%Y-%m-%d %H:%M:%S")
            except (ValueError, AttributeError):
                updated_date = cv.get("updated_at", "")

            writer.writerow([
                cv.get("cv_id", ""),
                cv.get("person_name", ""),
                cv.get("target_company", ""),
                cv.get("target_role", ""),
                created_date,
                updated_date,
                "Yes" if cv.get("filename") else "No"
            ])

        # Get the CSV content
        csv_content = output.getvalue()
        output.close()
        return csv_content

    # Generate filename with timestamp
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"cvs_export_{timestamp}.csv"

    # Return streaming response
    def iter_csv():
        yield generate_csv()

    return StreamingResponse(
        iter_csv(),
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        }
    )
