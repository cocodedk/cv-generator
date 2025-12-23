"""Pydantic models for CV data validation."""
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


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
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[Address] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    website: Optional[str] = None
    summary: Optional[str] = None


class Experience(BaseModel):
    """Work experience model."""

    title: str = Field(..., min_length=1, max_length=200)
    company: str = Field(..., min_length=1, max_length=200)
    start_date: str = Field(..., description="Start date in YYYY-MM format")
    end_date: Optional[str] = Field(
        None, description="End date in YYYY-MM format or 'Present'"
    )
    description: Optional[str] = None
    location: Optional[str] = None


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
