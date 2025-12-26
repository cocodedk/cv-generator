"""Pydantic models for CV data validation."""
from typing import Optional, List
import re
from pydantic import BaseModel, EmailStr, Field, field_validator, ValidationInfo


class Address(BaseModel):
    """Address model with components."""

    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = None
    country: Optional[str] = None


class PersonalInfo(BaseModel):
    """Personal information model."""

    name: str = Field(..., min_length=1, max_length=200)
    title: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[Address] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    website: Optional[str] = None
    summary: Optional[str] = None

    @field_validator("email", mode="before")
    @classmethod
    def _empty_email_to_none(cls, value: object) -> object:
        if value == "":
            return None
        return value


class Project(BaseModel):
    """Project model nested under an experience."""

    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    highlights: List[str] = Field(default_factory=list)
    technologies: List[str] = Field(default_factory=list)
    url: Optional[str] = None


class Experience(BaseModel):
    """Work experience model."""

    title: str = Field(..., min_length=1, max_length=200)
    company: str = Field(..., min_length=1, max_length=200)
    start_date: str = Field(..., description="Start date in YYYY-MM format")
    end_date: Optional[str] = Field(
        None, description="End date in YYYY-MM format or 'Present'"
    )
    description: Optional[str] = Field(
        None,
        description="Keep this short; put details under projects. HTML formatting is supported.",
    )
    location: Optional[str] = None
    projects: List[Project] = Field(default_factory=list)

    @field_validator('description')
    @classmethod
    def validate_description_length(cls, v: str | None, info: ValidationInfo) -> str | None:
        """Validate description length by counting plain text (HTML stripped)."""
        if v is None:
            return v
        # Strip HTML tags to count only plain text
        plain_text = re.sub(r'<[^>]+>', '', v)
        # Replace HTML entities with single characters
        plain_text = plain_text.replace('&nbsp;', ' ')
        plain_text = plain_text.replace('&amp;', '&')
        plain_text = plain_text.replace('&lt;', '<')
        plain_text = plain_text.replace('&gt;', '>')
        plain_text = plain_text.replace('&quot;', '"')
        plain_text = plain_text.replace('&#39;', "'")
        # Decode numeric entities
        plain_text = re.sub(r'&#(\d+);', lambda m: chr(int(m.group(1))), plain_text)
        if len(plain_text) > 300:
            from pydantic_core import PydanticCustomError
            raise PydanticCustomError(
                'string_too_long',
                'String should have at most 300 characters',
                {'max_length': 300}
            )
        return v


class Education(BaseModel):
    """Education model."""

    degree: str = Field(..., min_length=1, max_length=200)
    institution: str = Field(..., min_length=1, max_length=200)
    year: Optional[str] = None
    field: Optional[str] = None
    gpa: Optional[str] = None


class Skill(BaseModel):
    """Skill model."""

    name: str = Field(..., min_length=1, max_length=100)
    category: Optional[str] = None
    level: Optional[str] = None


class CVData(BaseModel):
    """Complete CV data model."""

    personal_info: PersonalInfo
    experience: List[Experience] = []
    education: List[Education] = []
    skills: List[Skill] = []
    theme: Optional[str] = Field(
        default="classic",
        description="CV theme: classic, modern, minimal, elegant, or accented",
    )


class CVResponse(BaseModel):
    """CV creation response."""

    cv_id: str
    filename: Optional[str] = None
    status: str = "success"


class CVListItem(BaseModel):
    """CV list item."""

    cv_id: str
    created_at: str
    updated_at: str
    person_name: Optional[str] = None
    filename: Optional[str] = None


class CVListResponse(BaseModel):
    """CV list response."""

    cvs: List[CVListItem]
    total: int


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
