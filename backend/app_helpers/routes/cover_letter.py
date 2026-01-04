"""Cover letter generation routes."""

import logging
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import Response
from slowapi import Limiter
from pydantic import ValidationError

from backend.database import queries
from backend.models import ProfileData
from backend.models_cover_letter import CoverLetterRequest, CoverLetterResponse
from backend.services.ai.cover_letter import generate_cover_letter
from backend.services.pdf_service import PDFService
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


def _format_validation_error(errors: list) -> str:
    """Convert Pydantic validation errors to user-friendly messages."""
    messages = []
    for err in errors:
        field_path = ".".join(str(loc) for loc in err["loc"])
        error_type = err.get("type", "")
        msg = err.get("msg", "")

        if "string_too_long" in error_type or "at most" in msg.lower():
            messages.append(f"The field '{field_path}' is too long.")
        elif "string_too_short" in error_type:
            messages.append(f"The field '{field_path}' is too short.")
        elif "missing" in error_type:
            messages.append(f"Required field '{field_path}' is missing.")
        else:
            messages.append(f"{field_path}: {msg}")

    return " | ".join(messages)


def _handle_validation_error(e: ValidationError) -> HTTPException:
    """Handle Pydantic validation errors."""
    friendly_msg = _format_validation_error(e.errors())
    logger.error(f"Cover letter validation failed: {friendly_msg}", exc_info=e)
    return HTTPException(status_code=400, detail=friendly_msg)


def _handle_value_error(e: ValueError) -> HTTPException:
    """Handle ValueError (configuration/processing errors)."""
    error_msg = str(e)
    logger.error(f"Cover letter generation error: {error_msg}", exc_info=e)
    if "not configured" in error_msg.lower():
        error_msg = (
            "AI cover letter generation requires LLM configuration. "
            "Please set AI_ENABLED=true and configure API credentials."
        )
    return HTTPException(status_code=400, detail=error_msg)


def _handle_generic_error(exc: Exception) -> HTTPException:
    """Handle generic exceptions."""
    error_msg = f"Failed to generate cover letter: {str(exc)}"
    logger.error(f"Failed to generate cover letter: {exc}", exc_info=exc)
    return HTTPException(status_code=500, detail=error_msg)


async def _handle_generate_cover_letter_request(
    payload: CoverLetterRequest,
) -> CoverLetterResponse:
    """Handle cover letter generation request."""
    profile_dict = queries.get_profile()
    if not profile_dict:
        raise HTTPException(status_code=404, detail="Profile not found")

    profile = ProfileData.model_validate(profile_dict)
    return await generate_cover_letter(profile, payload)


def create_cover_letter_router(  # noqa: C901
    limiter: Limiter, pdf_service: PDFService
) -> APIRouter:
    """Create cover letter router with generation and PDF export endpoints."""
    router = APIRouter()

    @router.post("/api/ai/generate-cover-letter", response_model=CoverLetterResponse)
    @limiter.limit("10/minute")
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

    class CoverLetterPDFRequest(BaseModel):
        """Request model for cover letter PDF export."""

        html: str = Field(..., min_length=1, description="HTML content to render")

    @router.post("/api/ai/cover-letter/pdf")
    @limiter.limit("30/minute")
    async def export_cover_letter_pdf(
        request: Request,
        pdf_request: CoverLetterPDFRequest,
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

    return router
