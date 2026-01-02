"""Browser-printable HTML (A4) CV routes."""

import logging
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from slowapi import Limiter

from backend.cv_generator.print_html_renderer import render_print_html
from backend.database import queries
from backend.models import CVData
from backend.services.cv_file_service import CVFileService

logger = logging.getLogger(__name__)


def create_print_html_router(limiter: Limiter, cv_file_service: CVFileService) -> APIRouter:
    router = APIRouter()

    @router.post("/api/render-print-html")
    @limiter.limit("20/minute")
    async def render_print_html_from_payload(request: Request, cv_data: CVData):
        try:
            cv_dict = cv_data.model_dump(exclude_none=False)
            if "theme" not in cv_dict or cv_dict["theme"] is None:
                cv_dict["theme"] = "classic"
            return HTMLResponse(render_print_html(cv_dict))
        except Exception as exc:
            logger.error("Failed to render print HTML", exc_info=exc)
            raise HTTPException(status_code=500, detail="Failed to render print HTML")

    @router.get("/api/cv/{cv_id}/print-html")
    @limiter.limit("30/minute")
    async def render_print_html_for_cv(request: Request, cv_id: str):
        try:
            cv = queries.get_cv_by_id(cv_id)
            if not cv:
                raise HTTPException(status_code=404, detail="CV not found")
            # Log raw CV data from database
            logger.info(
                "[print-html] Raw CV from DB - layout: %s, theme: %s",
                cv.get("layout"),
                cv.get("theme"),
            )
            cv_dict = cv_file_service.prepare_cv_dict(cv)
            layout = cv_dict.get("layout", "classic-two-column")
            logger.info(
                "[print-html] Prepared cv_dict for CV %s - layout: %s, theme: %s",
                cv_id,
                layout,
                cv_dict.get("theme"),
            )
            html = render_print_html(cv_dict)
            # Set no-cache headers to ensure fresh data
            return HTMLResponse(
                content=html,
                headers={
                    "Cache-Control": "no-cache, no-store, must-revalidate",
                    "Pragma": "no-cache",
                    "Expires": "0",
                },
            )
        except HTTPException:
            raise
        except Exception as exc:
            logger.error("Failed to render print HTML for %s", cv_id, exc_info=exc)
            raise HTTPException(
                status_code=500, detail="Failed to render print HTML for CV"
            )

    return router
