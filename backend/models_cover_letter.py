"""Pydantic models for cover letter generation."""

from typing import Literal, Optional, List
from pydantic import BaseModel, Field


class CoverLetterRequest(BaseModel):
    """Request to generate a cover letter from profile + job description."""

    job_description: str = Field(..., min_length=20, max_length=20000)
    company_name: str = Field(..., min_length=1, max_length=200)
    hiring_manager_name: Optional[str] = Field(default=None, max_length=200)
    company_address: Optional[str] = Field(default=None, max_length=500)
    tone: Literal["professional", "enthusiastic", "conversational"] = "professional"


class CoverLetterResponse(BaseModel):
    """Response containing generated cover letter."""

    cover_letter_html: str = Field(..., description="HTML formatted cover letter")
    cover_letter_text: str = Field(..., description="Plain text version of cover letter")
    highlights_used: List[str] = Field(
        default_factory=list, description="Profile items referenced in the cover letter"
    )
    selected_experiences: List[str] = Field(
        default_factory=list, description="Names of experiences selected as most relevant"
    )
    selected_skills: List[str] = Field(
        default_factory=list, description="Skills selected as most relevant to the job"
    )
