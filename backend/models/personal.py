"""Personal information models."""
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator


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
