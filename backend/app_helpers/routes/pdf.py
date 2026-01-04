"""Long single-page PDF export routes."""

import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Request, Query
from fastapi.responses import Response
from slowapi import Limiter

from backend.cv_generator.print_html_renderer import render_print_html
from backend.database import queries
from backend.services.cv_file_service import CVFileService
from backend.services.pdf_service import PDFService
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class PDFExportRequest(BaseModel):
    """Request model for PDF export from HTML."""

    html: str = Field(..., min_length=1, description="HTML content to render")
    format: Optional[str] = Field(
        default="A4_WIDTH_LONG", description="Format identifier"
    )
    margin_mm: Optional[int] = Field(
        default=0, ge=0, description="Margin in millimeters"
    )


def create_pdf_router(  # noqa: C901
    limiter: Limiter, cv_file_service: CVFileService, pdf_service: PDFService
) -> APIRouter:
    """Create and return PDF router with dependencies."""
    router = APIRouter()

    @router.post("/export/pdf/long")
    @limiter.limit("30/minute")
    async def export_pdf_long(request: Request, pdf_request: PDFExportRequest):
        """Generate long single-page PDF from HTML content."""
        try:
            if not pdf_request.html or not pdf_request.html.strip():
                raise HTTPException(
                    status_code=422, detail="HTML content cannot be empty"
                )

            pdf_bytes = await pdf_service.generate_long_pdf(pdf_request.html)

            return Response(
                content=pdf_bytes,
                media_type="application/pdf",
                headers={"Content-Disposition": 'attachment; filename="cv_long.pdf"'},
            )
        except ValueError as e:
            logger.error("PDF export validation error: %s", e)
            raise HTTPException(status_code=422, detail=str(e)) from e
        except Exception as exc:
            logger.error("Failed to generate PDF", exc_info=exc)
            raise HTTPException(
                status_code=500, detail=f"PDF generation failed: {str(exc)}"
            ) from exc

    @router.post("/api/cv/{cv_id}/export-pdf/long")
    @limiter.limit("30/minute")
    async def export_pdf_long_for_cv(
        request: Request,
        cv_id: str,
        theme: Optional[str] = Query(None, description="CV theme name"),
        layout: Optional[str] = Query(None, description="CV layout name"),
    ):
        """Generate long single-page PDF for existing CV."""
        try:
            cv = queries.get_cv_by_id(cv_id)
            if not cv:
                raise HTTPException(status_code=404, detail="CV not found")

            # Prepare CV dict
            cv_dict = cv_file_service.prepare_cv_dict(cv)

            # Override theme/layout if provided
            if theme:
                cv_dict["theme"] = theme
            if layout:
                cv_dict["layout"] = layout

            # Ensure theme is set
            if "theme" not in cv_dict or cv_dict["theme"] is None:
                cv_dict["theme"] = "classic"

            # Render HTML
            html = render_print_html(cv_dict)

            # Generate PDF
            pdf_bytes = await pdf_service.generate_long_pdf(html)

            return Response(
                content=pdf_bytes,
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f'attachment; filename="cv_{cv_id[:8]}_long.pdf"'
                },
            )
        except HTTPException:
            raise
        except ValueError as e:
            logger.error("PDF export validation error for CV %s: %s", cv_id, e)
            raise HTTPException(status_code=422, detail=str(e)) from e
        except Exception as exc:
            logger.error("Failed to generate PDF for CV %s", cv_id, exc_info=exc)
            raise HTTPException(
                status_code=500, detail=f"PDF generation failed: {str(exc)}"
            ) from exc

    return router
