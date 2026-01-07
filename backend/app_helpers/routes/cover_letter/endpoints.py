"""Cover letter API endpoints."""

import logging
from fastapi import HTTPException, Request, Response
from pydantic import ValidationError

from backend.app_helpers.routes.cover_letter.error_handlers import (
    _handle_validation_error,
    _handle_value_error,
    _handle_generic_error,
)
from backend.app_helpers.routes.cover_letter.request_handlers import (
    _handle_generate_cover_letter_request,
)
from backend.database.connection import Neo4jConnection
from backend.database.queries.create.cover_letter import create_cover_letter_node
from backend.database.queries.list.cover_letter_list import list_cover_letters
from backend.database.queries.read.cover_letter_get import get_cover_letter_by_id
from backend.database.queries.delete import delete_cover_letter
from backend.models_cover_letter import CoverLetterRequest, CoverLetterSaveRequest, CoverLetterData
from backend.services.pdf_service import PDFService
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import uuid4

logger = logging.getLogger(__name__)


class CoverLetterPDFRequest(BaseModel):
    """Request model for cover letter PDF export."""

    html: str = Field(..., min_length=1, description="HTML content to render")


async def generate_cover_letter_endpoint(
    request: Request, payload: CoverLetterRequest
):
    """Generate a tailored cover letter from profile + job description."""
    try:
        return await _handle_generate_cover_letter_request(payload)
    except HTTPException:
        raise
    except ValidationError as e:
        raise _handle_validation_error(e)
    except ValueError as e:
        raise _handle_value_error(e)
    except Exception as exc:
        raise _handle_generic_error(exc)


async def export_cover_letter_pdf(
    request: Request,
    pdf_request: CoverLetterPDFRequest,
    pdf_service: PDFService,
):
    """Generate PDF from cover letter HTML."""
    try:
        if not pdf_request.html or not pdf_request.html.strip():
            raise HTTPException(
                status_code=422, detail="HTML content cannot be empty"
            )

        pdf_bytes = await pdf_service.generate_long_pdf(pdf_request.html)

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": 'attachment; filename="cover_letter.pdf"'
            },
        )
    except ValueError as e:
        logger.error("PDF export validation error: %s", e)
        raise HTTPException(status_code=422, detail=str(e)) from e
    except Exception as exc:
        logger.error("Failed to generate PDF", exc_info=exc)
        raise HTTPException(
            status_code=500, detail=f"PDF generation failed: {str(exc)}"
        ) from exc


async def save_cover_letter_endpoint(
    request: Request, payload: CoverLetterSaveRequest
):
    """Save a generated cover letter."""
    try:
        cover_letter_id = str(uuid4())
        created_at = datetime.utcnow().isoformat()

        with Neo4jConnection.get_driver().session() as session:
            session.execute_write(
                create_cover_letter_node,
                cover_letter_id=cover_letter_id,
                created_at=created_at,
                job_description=payload.request_data.job_description,
                company_name=payload.request_data.company_name,
                hiring_manager_name=payload.request_data.hiring_manager_name,
                company_address=payload.request_data.company_address,
                tone=payload.request_data.tone,
                cover_letter_html=payload.cover_letter_response.cover_letter_html,
                cover_letter_text=payload.cover_letter_response.cover_letter_text,
                highlights_used=payload.cover_letter_response.highlights_used,
                selected_experiences=payload.cover_letter_response.selected_experiences,
                selected_skills=payload.cover_letter_response.selected_skills,
            )

        return {"cover_letter_id": cover_letter_id, "status": "success"}
    except Exception as exc:
        logger.error("Failed to save cover letter", exc_info=exc)
        raise HTTPException(
            status_code=500, detail=f"Failed to save cover letter: {str(exc)}"
        )


async def list_cover_letters_endpoint(
    request: Request,
    limit: int = 50,
    offset: int = 0,
    search: str | None = None,
):
    """List saved cover letters."""
    try:
        return list_cover_letters(limit=limit, offset=offset, search=search)
    except Exception as exc:
        logger.error("Failed to list cover letters", exc_info=exc)
        raise HTTPException(
            status_code=500, detail=f"Failed to list cover letters: {str(exc)}"
        )


async def get_cover_letter_endpoint(
    request: Request, cover_letter_id: str
):
    """Get a specific cover letter by ID."""
    try:
        cover_letter = get_cover_letter_by_id(cover_letter_id)
        if not cover_letter:
            raise HTTPException(status_code=404, detail="Cover letter not found")

        return CoverLetterData.model_validate(cover_letter)
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Failed to get cover letter", exc_info=exc)
        raise HTTPException(
            status_code=500, detail=f"Failed to get cover letter: {str(exc)}"
        )


async def delete_cover_letter_endpoint(
    request: Request, cover_letter_id: str
):
    """Delete a cover letter."""
    try:
        deleted = delete_cover_letter(cover_letter_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Cover letter not found")

        return {"status": "success"}
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Failed to delete cover letter", exc_info=exc)
        raise HTTPException(
            status_code=500, detail=f"Failed to delete cover letter: {str(exc)}"
        )
