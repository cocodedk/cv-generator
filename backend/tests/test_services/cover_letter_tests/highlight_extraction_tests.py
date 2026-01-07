"""Tests for highlight extraction functionality."""

import pytest

from backend.models import ProfileData, PersonalInfo, Experience, Project
from backend.services.ai.cover_letter import _extract_highlights_used


@pytest.fixture
def sample_profile():
    """Sample profile data for testing."""
    return ProfileData(
        personal_info=PersonalInfo(
            name="Jane Smith",
            title="Senior Software Engineer",
            email="jane@example.com",
        ),
        experience=[],
        education=[],
        skills=[],
    )


class TestExtractHighlightsUsed:
    """Test highlights extraction from profile."""

    def test_extract_highlights_used(self, sample_profile):
        """Test extracting highlights that match job description."""
        from backend.models import Experience, Project

        sample_profile.experience = [
            Experience(
                title="Engineer",
                company="Corp",
                start_date="2020-01",
                end_date="2022-12",
                projects=[
                    Project(
                        name="Project",
                        highlights=["Built Python API", "Improved React performance"],
                    )
                ],
            )
        ]

        jd = "We need someone with Python and React experience."
        highlights = _extract_highlights_used(sample_profile, jd)

        assert len(highlights) > 0
        assert any("Python" in h or "React" in h for h in highlights)
