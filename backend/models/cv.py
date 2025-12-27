"""CV data and response models."""
from typing import Optional, List
from pydantic import BaseModel, Field
from backend.models.personal import PersonalInfo
from backend.models.experience import Experience
from backend.models.education import Education, Skill


class CVData(BaseModel):
    """Complete CV data model."""

    personal_info: PersonalInfo
    experience: List[Experience] = []
    education: List[Education] = []
    skills: List[Skill] = []
    theme: Optional[str] = Field(
        default="classic",
        description="CV theme: accented, classic, colorful, creative, elegant, executive, minimal, modern, professional, or tech",
    )
    layout: Optional[str] = Field(
        default="classic-two-column",
        description="CV layout: classic-two-column, ats-single-column, modern-sidebar, section-cards-grid, career-timeline, project-case-studies, portfolio-spa, interactive-skills-matrix, academic-cv, dark-mode-tech",
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
