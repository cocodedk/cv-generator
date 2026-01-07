"""Tests for cover letter profile summary formatting."""

import pytest

from backend.models import ProfileData, PersonalInfo, Address
from backend.services.ai.cover_letter import _format_profile_summary


@pytest.fixture
def sample_profile():
    """Sample profile data for testing."""
    return ProfileData(
        personal_info=PersonalInfo(
            name="Jane Smith",
            title="Senior Software Engineer",
            email="jane@example.com",
            phone="+1234567890",
            address=Address(
                street="456 Oak Ave",
                city="San Francisco",
                state="CA",
                zip="94102",
                country="USA",
            ),
        ),
        experience=[],
        education=[],
        skills=[],
    )


class TestFormatProfileSummary:
    """Test profile summary formatting for cover letters."""

    def test_format_profile_summary_basic(self, sample_profile):
        """Test basic profile summary formatting with personal info."""
        summary = _format_profile_summary(sample_profile)
        assert "Jane Smith" in summary
        assert "Senior Software Engineer" in summary
        assert "jane@example.com" in summary
        assert "+1234567890" in summary

    def test_format_profile_summary_with_experience(self, sample_profile):
        """Test profile summary with experience data."""
        from backend.models import Experience, Project

        sample_profile.experience = [
            Experience(
                title="Software Engineer",
                company="Previous Corp",
                start_date="2020-01",
                end_date="2022-12",
                projects=[
                    Project(
                        name="Project A",
                        highlights=["Built API", "Improved performance"],
                    )
                ],
            )
        ]

        summary = _format_profile_summary(sample_profile)
        assert "Software Engineer" in summary
        assert "Previous Corp" in summary
        assert "Project A" in summary
        assert "Built API" in summary

    def test_format_profile_summary_with_skills(self, sample_profile):
        """Test profile summary with skills data."""
        from backend.models import Skill

        sample_profile.skills = [
            Skill(name="Python", category="Programming"),
            Skill(name="React", category="Frontend"),
        ]

        summary = _format_profile_summary(sample_profile)
        assert "Python" in summary
        assert "React" in summary
