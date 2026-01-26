"""Profile-related routes."""
import logging
from fastapi import APIRouter, HTTPException, Request, Query
from slowapi import Limiter
from backend.models import (
    ProfileData,
    ProfileResponse,
    ProfileListResponse,
    ProfileListItem,
    TranslateProfileRequest,
    TranslateProfileResponse,
)
from backend.database import queries
from backend.database.queries import get_profile_by_language
from backend.services.profile_translation import get_translation_service

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


def create_profile_router(limiter: Limiter, cv_file_service=None) -> APIRouter:  # noqa: C901
    """Create and return profile router with dependencies."""
    router = APIRouter()

    @router.post("/api/profile", response_model=ProfileResponse)
    @limiter.limit("30/minute")
    async def save_profile_endpoint(request: Request, profile_data: ProfileData, create_new: bool = Query(False, alias="create_new")):
        """Save or update master profile."""
        try:
            profile_dict = profile_data.model_dump()
            success = queries.save_profile(profile_dict, create_new=create_new)
            if not success:
                raise HTTPException(status_code=500, detail="Failed to save profile")

            # Generate featured templates after profile save
            if cv_file_service:
                try:
                    await cv_file_service.generate_featured_templates()
                    logger.info("Generated featured templates after profile save")
                except Exception as e:
                    logger.warning("Failed to generate featured templates after profile save", exc_info=e)

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
                ProfileListItem(name=p["name"], updated_at=p["updated_at"], language=p["language"] or "en")
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

    @router.post("/api/profile/translate", response_model=TranslateProfileResponse)
    @limiter.limit("10/minute")
    async def translate_profile_endpoint(request: Request, translate_request: TranslateProfileRequest):
        """Translate a profile to another language using AI."""
        try:
            translation_service = get_translation_service()

            profile_dict = translate_request.profile_data.model_dump()
            source_language = profile_dict.get("language", "en")
            target_language = translate_request.target_language

            translated_profile_dict = await translation_service.translate_profile(
                profile_dict, target_language, source_language
            )

            # Convert back to ProfileData model
            translated_profile = ProfileData(**translated_profile_dict)

            # Check if a profile already exists with the target language
            existing_profile = get_profile_by_language(target_language)
            existing_profile_updated_at = existing_profile.get("updated_at") if existing_profile else None

            # Save the translated profile automatically
            create_new = existing_profile_updated_at is None
            logger.info(f"Saving translated profile: create_new={create_new}, language={translated_profile_dict.get('language')}")
            save_success = queries.save_profile(translated_profile_dict, create_new=create_new)

            if not save_success:
                logger.error("Failed to save translated profile")
                raise HTTPException(status_code=500, detail="Failed to save translated profile")

            # Get the updated/saved profile to return the correct updated_at
            saved_profile = get_profile_by_language(target_language)
            saved_profile_updated_at = saved_profile.get("updated_at") if saved_profile else None

            # Update message based on whether we're updating or creating
            if existing_profile_updated_at:
                message = f"Profile translated from {source_language} to {target_language} and saved successfully."
            else:
                message = f"Profile translated from {source_language} to {target_language} and saved as new profile."

            return TranslateProfileResponse(
                status="success",
                translated_profile=translated_profile,
                message=message,
                saved_profile_updated_at=saved_profile_updated_at
            )
        except ValueError as e:
            logger.error("Translation service not configured", exc_info=e)
            raise HTTPException(status_code=503, detail="AI translation service is not configured")
        except Exception as e:
            logger.error("Failed to translate profile", exc_info=e)
            raise HTTPException(status_code=500, detail="Failed to translate profile")

    return router
