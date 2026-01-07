"""Tests for profile formatting functions in cover letter selection."""

import pytest

from backend.models import ProfileData, PersonalInfo, Experience, Project, Skill
from backend.services.ai.cover_letter_selection import _format_profile_for_selection


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


class TestFormatProfileForSelection:
    """Test profile formatting for selection."""

    def test_format_profile_for_selection(self, sample_profile):
        """Test formatting profile with experiences and skills."""
        formatted = _format_profile_for_selection(sample_profile)

        assert "[0]" in formatted
        assert "[1]" in formatted
        assert "[2]" in formatted
        assert "Django" in formatted
        assert "Node.js" in formatted
        assert "LAMP" in formatted
        assert "Modern Tech Inc" in formatted
        assert "Startup Co" in formatted

    def test_format_profile_empty(self):
        """Test formatting empty profile."""
        profile = ProfileData(
            personal_info=PersonalInfo(name="Test", title="Developer"),
            experience=[],
            education=[],
            skills=[],
        )
        formatted = _format_profile_for_selection(profile)
        assert "EXPERIENCES:" in formatted
        # Skills section may not appear if skills list is empty
        # This is acceptable behavior
