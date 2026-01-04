"""Pydantic models for AI drafting features."""

from typing import Literal, Optional, List

from pydantic import BaseModel, Field

from backend.models import CVData


class EvidenceItem(BaseModel):
    """A single piece of evidence backing a requirement."""

    path: str = Field(..., description="JSON path into the profile/CV, e.g. experience[0].projects[1].highlights[2]")
    quote: str = Field(..., min_length=1, max_length=400)


class EvidenceMapping(BaseModel):
    """Maps a requirement to supporting evidence."""

    requirement: str = Field(..., min_length=1, max_length=200)
    evidence: List[EvidenceItem] = Field(default_factory=list)


class AIGenerateCVRequest(BaseModel):
    """Request to generate a tailored CV draft from saved profile + job description."""

    job_description: str = Field(..., min_length=20, max_length=20000)
    target_role: Optional[str] = Field(default=None, max_length=200)
    seniority: Optional[str] = Field(default=None, max_length=100)
    style: Literal["select_and_reorder", "rewrite_bullets", "llm_tailor"] = "select_and_reorder"
    max_experiences: Optional[int] = Field(default=None, ge=1, le=10)


class AIGenerateCVResponse(BaseModel):
    """Response containing a validated CV draft plus review metadata."""

    draft_cv: CVData
    warnings: List[str] = Field(default_factory=list)
    questions: List[str] = Field(default_factory=list)
    summary: List[str] = Field(default_factory=list)
    evidence_map: Optional[List[EvidenceMapping]] = None


class AIRewriteRequest(BaseModel):
    """Request to rewrite text using LLM."""

    text: str = Field(..., min_length=1, max_length=10000, description="Text to rewrite")
    prompt: str = Field(..., min_length=1, max_length=1000, description="User's prompt/instruction for rewriting")


class AIRewriteResponse(BaseModel):
    """Response containing rewritten text."""

    rewritten_text: str = Field(..., description="The rewritten text")
