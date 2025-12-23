"""Profile-related routes."""
import logging
from fastapi import APIRouter, HTTPException, Request
from slowapi import Limiter
from backend.models import ProfileData, ProfileResponse
from backend.database import queries

logger = logging.getLogger(__name__)


def create_profile_router(limiter: Limiter) -> APIRouter:  # noqa: C901
    """Create and return profile router with dependencies."""
    router = APIRouter()

    @router.post("/api/profile", response_model=ProfileResponse)
    @limiter.limit("30/minute")
    async def save_profile_endpoint(request: Request, profile_data: ProfileData):
        """Save or update master profile."""
        try:
            profile_dict = profile_data.model_dump()
            success = queries.save_profile(profile_dict)
            if not success:
                raise HTTPException(status_code=500, detail="Failed to save profile")
            return ProfileResponse(
                status="success", message="Profile saved successfully"
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error("Failed to save profile", exc_info=e)
            raise HTTPException(status_code=500, detail="Failed to save profile")

    @router.get("/api/profile")
    async def get_profile_endpoint():
        """Get master profile."""
        try:
            profile = queries.get_profile()
            if not profile:
                raise HTTPException(status_code=404, detail="Profile not found")
            return profile
        except HTTPException:
            raise
        except Exception as e:
            logger.error("Failed to get profile", exc_info=e)
            raise HTTPException(status_code=500, detail="Failed to get profile")

    @router.delete("/api/profile", response_model=ProfileResponse)
    async def delete_profile_endpoint():
        """Delete master profile."""
        try:
            success = queries.delete_profile()
            if not success:
                raise HTTPException(status_code=404, detail="Profile not found")
            return ProfileResponse(
                status="success", message="Profile deleted successfully"
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error("Failed to delete profile", exc_info=e)
            raise HTTPException(status_code=500, detail="Failed to delete profile")

    return router
