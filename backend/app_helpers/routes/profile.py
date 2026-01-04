"""Profile-related routes."""
import logging
from fastapi import APIRouter, HTTPException, Request
from slowapi import Limiter
from backend.models import (
    ProfileData,
    ProfileResponse,
    ProfileListResponse,
    ProfileListItem,
)
from backend.database import queries

logger = logging.getLogger(__name__)

_DELETE_CONFIRM_HEADER = "x-confirm-delete-profile"


def _is_delete_confirmed(request: Request) -> bool:
    value = (request.headers.get(_DELETE_CONFIRM_HEADER) or "").strip().lower()
    return value in {"true", "1", "yes"}


def _log_profile_delete_request(
    request: Request, updated_at: str | None = None
) -> None:
    client_host = request.client.host if request.client else None
    logger.warning(
        "Profile delete requested path=%s updated_at=%s ip=%s origin=%r referer=%r ua=%r",
        request.url.path,
        updated_at,
        client_host,
        request.headers.get("origin"),
        request.headers.get("referer"),
        request.headers.get("user-agent"),
    )


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

    @router.get("/api/profiles", response_model=ProfileListResponse)
    async def list_profiles_endpoint():
        """List all profiles with basic info."""
        try:
            profiles = queries.list_profiles()
            profile_items = [
                ProfileListItem(name=p["name"], updated_at=p["updated_at"])
                for p in profiles
            ]
            return ProfileListResponse(profiles=profile_items)
        except Exception as e:
            logger.error("Failed to list profiles", exc_info=e)
            raise HTTPException(status_code=500, detail="Failed to list profiles")

    @router.get("/api/profile/{updated_at}")
    async def get_profile_by_updated_at_endpoint(updated_at: str):
        """Get a specific profile by its updated_at timestamp."""
        try:
            profile = queries.get_profile_by_updated_at(updated_at)
            if not profile:
                raise HTTPException(status_code=404, detail="Profile not found")
            return profile
        except HTTPException:
            raise
        except Exception as e:
            logger.error("Failed to get profile by timestamp", exc_info=e)
            raise HTTPException(status_code=500, detail="Failed to get profile")

    @router.delete("/api/profile", response_model=ProfileResponse)
    async def delete_profile_endpoint(request: Request):
        """Delete master profile."""
        try:
            if not _is_delete_confirmed(request):
                raise HTTPException(
                    status_code=400,
                    detail=f"Missing header `{_DELETE_CONFIRM_HEADER}: true`",
                )
            _log_profile_delete_request(request)
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

    @router.delete("/api/profile/{updated_at}", response_model=ProfileResponse)
    async def delete_profile_by_updated_at_endpoint(request: Request, updated_at: str):
        """Delete a specific profile by its updated_at timestamp."""
        try:
            if not _is_delete_confirmed(request):
                raise HTTPException(
                    status_code=400,
                    detail=f"Missing header `{_DELETE_CONFIRM_HEADER}: true`",
                )
            _log_profile_delete_request(request, updated_at=updated_at)
            success = queries.delete_profile_by_updated_at(updated_at)
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
