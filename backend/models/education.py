"""Education and skill models."""
from typing import Optional
from pydantic import BaseModel, Field


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
