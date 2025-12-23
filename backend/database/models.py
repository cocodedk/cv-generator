"""Neo4j node and relationship models for CV data."""
from typing import Optional, List
from datetime import datetime
from uuid import uuid4


class PersonNode:
    """Person node model."""

    def __init__(
        self,
        name: str,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        address: Optional[str] = None,
        linkedin: Optional[str] = None,
        github: Optional[str] = None,
        website: Optional[str] = None,
        summary: Optional[str] = None,
    ):
        self.name = name
        self.email = email
        self.phone = phone
        self.address = address
        self.linkedin = linkedin
        self.github = github
        self.website = website
        self.summary = summary


class ExperienceNode:
    """Experience node model."""

    def __init__(
        self,
        title: str,
        company: str,
        start_date: str,
        end_date: Optional[str] = None,
        description: Optional[str] = None,
        location: Optional[str] = None,
    ):
        self.title = title
        self.company = company
        self.start_date = start_date
        self.end_date = end_date
        self.description = description
        self.location = location


class EducationNode:
    """Education node model."""

    def __init__(
        self,
        degree: str,
        institution: str,
        year: Optional[str] = None,
        field: Optional[str] = None,
        gpa: Optional[str] = None,
    ):
        self.degree = degree
        self.institution = institution
        self.year = year
        self.field = field
        self.gpa = gpa


class SkillNode:
    """Skill node model."""

    def __init__(
        self, name: str, category: Optional[str] = None, level: Optional[str] = None
    ):
        self.name = name
        self.category = category
        self.level = level


class CVNode:
    """CV node model."""

    def __init__(
        self,
        cv_id: Optional[str] = None,
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None,
    ):
        self.cv_id = cv_id or str(uuid4())
        self.created_at = created_at or datetime.utcnow().isoformat()
        self.updated_at = updated_at or datetime.utcnow().isoformat()
