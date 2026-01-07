"""Tests for selection prompt building in cover letter selection."""

import pytest

from backend.models import ProfileData, PersonalInfo, Experience, Project, Skill
from backend.services.ai.cover_letter_selection import (
    _format_profile_for_selection,
    _build_selection_prompt,
)


@pytest.fixture
def sample_profile():
    """Sample profile with multiple experiences and skills."""
    return ProfileData(
        personal_info=PersonalInfo(
            name="Jane Developer",
            title="Senior Software Engineer",
            email="jane@example.com",
        ),
        experience=[
            Experience(
                title="Senior Backend Engineer",
                company="Modern Tech Inc",
                start_date="2022-01",
                end_date="2024-12",
                projects=[
                    Project(
                        name="API Platform",
                        technologies=["Django", "Python", "PostgreSQL"],
                        highlights=[
                            "Built scalable REST API serving 1M+ requests/day",
                            "Led migration to microservices architecture",
                        ],
                    )
                ],
            ),
            Experience(
                title="Full Stack Developer",
                company="Startup Co",
                start_date="2020-01",
                end_date="2021-12",
                projects=[
                    Project(
                        name="Web Application",
                        technologies=["Node.js", "React", "MongoDB"],
                        highlights=[
                            "Developed full-stack web application",
                            "Implemented responsive UI components",
                        ],
                    )
                ],
            ),
            Experience(
                title="Junior Developer",
                company="Small Agency",
                start_date="2018-01",
                end_date="2019-12",
                projects=[
                    Project(
                        name="Portfolio Site",
                        technologies=["HTML", "CSS", "JavaScript"],
                        highlights=[
                            "Built responsive portfolio website",
                            "Optimized performance and SEO",
                        ],
                    )
                ],
            ),
        ],
        education=[],
        skills=[
            Skill(name="Django", category="Backend"),
            Skill(name="Python", category="Programming"),
            Skill(name="PostgreSQL", category="Database"),
            Skill(name="Node.js", category="Backend"),
            Skill(name="React", category="Frontend"),
            Skill(name="MongoDB", category="Database"),
            Skill(name="LAMP", category="Full Stack"),
        ],
    )


@pytest.fixture
def job_description_django():
    """Django-focused job description."""
    return """
    Senior Backend Engineer - Django/Python

    We are looking for an experienced backend engineer to join our team building
    scalable web applications using Django and Python.

    Requirements:
    - 3+ years experience with Django
    - Strong Python skills
    - Experience with PostgreSQL
    - REST API development
    - Microservices architecture

    Nice to have:
    - AWS experience
    - Docker containerization
    """


class TestBuildSelectionPrompt:
    """Test selection prompt building."""

    def test_build_selection_prompt(self, sample_profile, job_description_django):
        """Test building selection prompt."""
        profile_text = _format_profile_for_selection(sample_profile)
        prompt = _build_selection_prompt(profile_text, job_description_django)

        assert "JOB DESCRIPTION:" in prompt
        assert "CANDIDATE PROFILE:" in prompt
        assert "experience_indices" in prompt
        assert "skill_names" in prompt
        assert "key_highlights" in prompt
        assert "relevance_reasoning" in prompt

    def test_build_selection_prompt_empty_profile(self):
        """Test building selection prompt with empty profile."""
        profile_text = "EXPERIENCES:\n\nSKILLS:"
        job_desc = "We need a developer."
        prompt = _build_selection_prompt(profile_text, job_desc)

        assert job_desc in prompt
        assert profile_text in prompt
        assert "Return ONLY valid JSON" in prompt

    def test_build_selection_prompt_complex_job_desc(self):
        """Test building selection prompt with complex job description."""
        profile_text = "EXPERIENCES:\n[0] Engineer at Company\n\nSKILLS: Python"
        complex_job = """
        Senior Full Stack Developer

        We are looking for an experienced developer with:
        - 5+ years of experience
        - React and Node.js expertise
        - Cloud deployment experience

        Responsibilities:
        - Build scalable web applications
        - Lead technical architecture decisions
        - Mentor junior developers
        """
        prompt = _build_selection_prompt(profile_text, complex_job)

        assert complex_job in prompt
        assert profile_text in prompt
        assert "IMPORTANT:" in prompt
        assert "quality over quantity" in prompt
