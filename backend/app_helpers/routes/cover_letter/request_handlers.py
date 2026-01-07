"""Request handling utilities for cover letter endpoints."""

from fastapi import HTTPException

from backend.database import queries
from backend.models import ProfileData
from backend.models_cover_letter import CoverLetterResponse
from backend.services.ai.cover_letter import generate_cover_letter


async def _handle_generate_cover_letter_request(
    payload,
) -> CoverLetterResponse:
    """Handle cover letter generation request."""
    profile_dict = queries.get_profile()
    if not profile_dict:
        raise HTTPException(status_code=404, detail="Profile not found")

    profile = ProfileData.model_validate(profile_dict)
    return await generate_cover_letter(profile, payload)
