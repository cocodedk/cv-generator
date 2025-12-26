"""Profile data and response models."""
from typing import Optional, List
from pydantic import BaseModel
from backend.models.personal import PersonalInfo
from backend.models.experience import Experience
from backend.models.education import Education, Skill


class ProfileData(BaseModel):
    """Master profile data model (same structure as CVData)."""

    personal_info: PersonalInfo
    experience: List[Experience] = []
    education: List[Education] = []
    skills: List[Skill] = []


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
