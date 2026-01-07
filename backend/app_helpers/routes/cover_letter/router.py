"""Cover letter router creation."""

from fastapi import APIRouter, Request
from slowapi import Limiter

from backend.app_helpers.routes.cover_letter.endpoints import (
    generate_cover_letter_endpoint,
    export_cover_letter_pdf,
    save_cover_letter_endpoint,
    list_cover_letters_endpoint,
    get_cover_letter_endpoint,
    delete_cover_letter_endpoint,
)
from backend.models_cover_letter import (
    CoverLetterRequest,
    CoverLetterSaveRequest,
    CoverLetterResponse,
    CoverLetterData,
)
from backend.services.pdf_service import PDFService
from pydantic import BaseModel, Field


class CoverLetterPDFRequest(BaseModel):
    """Request model for cover letter PDF export."""
    html: str = Field(..., min_length=1, description="HTML content to render")


def create_cover_letter_router(
    limiter: Limiter, pdf_service: PDFService
) -> APIRouter:
    """Create cover letter router with generation and PDF export endpoints."""
    router = APIRouter()

    @router.post("/api/ai/generate-cover-letter", response_model=CoverLetterResponse)
    @limiter.limit("10/minute")
    async def generate_cover_letter_endpoint_decorated(
        request: Request, payload: CoverLetterRequest
    ):
        return await generate_cover_letter_endpoint(request, payload)

    @router.post("/api/ai/cover-letter/pdf")
    @limiter.limit("30/minute")
    async def export_cover_letter_pdf_decorated(
        request: Request, pdf_request: CoverLetterPDFRequest
    ):
        return await export_cover_letter_pdf(request, pdf_request, pdf_service)

    @router.post("/api/cover-letters", response_model=dict)
    @limiter.limit("30/minute")
    async def save_cover_letter_endpoint_decorated(
        request: Request, payload: CoverLetterSaveRequest
    ):
        return await save_cover_letter_endpoint(request, payload)

    @router.get("/api/cover-letters", response_model=dict)
    @limiter.limit("30/minute")
    async def list_cover_letters_endpoint_decorated(
        request: Request,
        limit: int = 50,
        offset: int = 0,
        search: str | None = None,
    ):
        return await list_cover_letters_endpoint(request, limit, offset, search)

    @router.get("/api/cover-letters/{cover_letter_id}", response_model=CoverLetterData)
    @limiter.limit("30/minute")
    async def get_cover_letter_endpoint_decorated(
        request: Request, cover_letter_id: str
    ):
        return await get_cover_letter_endpoint(request, cover_letter_id)

    @router.delete("/api/cover-letters/{cover_letter_id}")
    @limiter.limit("30/minute")
    async def delete_cover_letter_endpoint_decorated(
        request: Request, cover_letter_id: str
    ):
        return await delete_cover_letter_endpoint(request, cover_letter_id)

    return router
