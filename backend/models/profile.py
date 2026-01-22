"""Profile data and response models."""
from typing import Optional, List
from pydantic import BaseModel, field_validator
from backend.models.personal import PersonalInfo
from backend.models.experience import Experience
from backend.models.education import Education, Skill

# Supported languages for profile translation (ISO 639-1 codes)
SUPPORTED_LANGUAGES = {
    "en", "es", "fr", "de", "it", "pt", "nl", "ru", "zh", "ja", "ko", "ar", "da"
}


class ProfileData(BaseModel):
    """Master profile data model (same structure as CVData)."""

    personal_info: PersonalInfo
    experience: List[Experience] = []
    education: List[Education] = []
    skills: List[Skill] = []
    language: str = "en"  # ISO 639-1 language code, default English


class ProfileResponse(BaseModel):
    """Profile operation response."""

    status: str = "success"
    message: Optional[str] = None


class ProfileListItem(BaseModel):
    """Profile list item with basic info."""

    name: str
    updated_at: str


class ProfileListResponse(BaseModel):
    """Response model for profile list."""

    profiles: List[ProfileListItem]


class TranslateProfileRequest(BaseModel):
    """Request model for profile translation."""

    profile_data: ProfileData
    target_language: str  # ISO 639-1 language code

    @field_validator('target_language')
    @classmethod
    def validate_target_language(cls, v):
        if v not in SUPPORTED_LANGUAGES:
            raise ValueError(f"Unsupported target language '{v}'. Supported languages are: {', '.join(sorted(SUPPORTED_LANGUAGES))}")
        return v


class TranslateProfileResponse(BaseModel):
    """Response model for profile translation."""

    status: str
    translated_profile: ProfileData
    message: Optional[str] = None
    existing_profile_updated_at: Optional[str] = None
