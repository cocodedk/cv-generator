"""Experience and project models."""
from typing import Optional, List
import re
from pydantic import BaseModel, Field, field_validator, ValidationInfo
from pydantic_core import PydanticCustomError


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

    @field_validator("description")
    @classmethod
    def validate_description_length(
        cls, v: str | None, info: ValidationInfo
    ) -> str | None:
        """Validate description length by counting plain text (HTML stripped)."""
        if v is None:
            return v
        # Strip HTML tags to count only plain text
        plain_text = re.sub(r"<[^>]+>", "", v)
        # Replace HTML entities with single characters
        plain_text = plain_text.replace("&nbsp;", " ")
        plain_text = plain_text.replace("&amp;", "&")
        plain_text = plain_text.replace("&lt;", "<")
        plain_text = plain_text.replace("&gt;", ">")
        plain_text = plain_text.replace("&quot;", '"')
        plain_text = plain_text.replace("&#39;", "'")
        # Decode numeric entities
        plain_text = re.sub(r"&#(\d+);", lambda m: chr(int(m.group(1))), plain_text)
        if len(plain_text) > 300:
            raise PydanticCustomError(
                "string_too_long",
                "String should have at most 300 characters",
                {"max_length": 300},
            )
        return v
