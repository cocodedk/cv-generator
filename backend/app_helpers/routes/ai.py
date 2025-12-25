"""AI drafting routes (heuristics-first)."""

import logging
from fastapi import APIRouter, HTTPException, Request
from slowapi import Limiter

from backend.database import queries
from backend.models import ProfileData
from backend.models_ai import AIGenerateCVRequest, AIGenerateCVResponse
from backend.services.ai.draft import generate_cv_draft

logger = logging.getLogger(__name__)


def create_ai_router(limiter: Limiter) -> APIRouter:
    router = APIRouter()

    @router.post("/api/ai/generate-cv", response_model=AIGenerateCVResponse)
    @limiter.limit("10/minute")
    async def generate_cv_from_profile_and_jd(request: Request, payload: AIGenerateCVRequest):
        try:
            profile_dict = queries.get_profile()
            if not profile_dict:
                raise HTTPException(status_code=404, detail="Profile not found")

            profile = ProfileData.model_validate(profile_dict)
            return generate_cv_draft(profile, payload)
        except HTTPException:
            raise
        except Exception as exc:
            logger.error("Failed to generate CV draft", exc_info=exc)
            raise HTTPException(status_code=500, detail="Failed to generate CV draft")

    return router
