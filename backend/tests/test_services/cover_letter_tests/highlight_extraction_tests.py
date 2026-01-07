"""Tests for highlight extraction functionality."""

import pytest

from backend.models import ProfileData, PersonalInfo
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

    def test_extract_highlights_used_no_matches(self, sample_profile):
        """Test extracting highlights when none match the job description."""
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

        jd = "We need someone with Java and Spring experience."
        highlights = _extract_highlights_used(sample_profile, jd)

        # Should return empty list when no matches
        assert len(highlights) == 0

    def test_extract_highlights_used_empty_profile(self):
        """Test extracting highlights from empty profile."""
        empty_profile = ProfileData(
            personal_info=PersonalInfo(name="Test", title="Developer"),
            experience=[],
            education=[],
            skills=[],
        )

        jd = "We need developers."
        highlights = _extract_highlights_used(empty_profile, jd)

        assert highlights == []

    def test_extract_highlights_used_no_experience(self, sample_profile):
        """Test extracting highlights when profile has no experience."""
        jd = "We need developers."
        highlights = _extract_highlights_used(sample_profile, jd)

        assert highlights == []

    def test_extract_highlights_used_experience_without_projects(self, sample_profile):
        """Test extracting highlights from experience without projects."""
        from backend.models import Experience

        sample_profile.experience = [
            Experience(
                title="Engineer",
                company="Corp",
                start_date="2020-01",
                end_date="2022-12",
                projects=[],  # No projects
            )
        ]

        jd = "We need engineers."
        highlights = _extract_highlights_used(sample_profile, jd)

        assert highlights == []

    def test_extract_highlights_used_projects_without_highlights(self, sample_profile):
        """Test extracting highlights from projects without highlights."""
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
                        highlights=[],  # No highlights
                    )
                ],
            )
        ]

        jd = "We need engineers."
        highlights = _extract_highlights_used(sample_profile, jd)

        assert highlights == []

    def test_extract_highlights_used_case_insensitive_matching(self, sample_profile):
        """Test that highlight extraction is case-insensitive."""
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
                        highlights=["Built PYTHON api", "Improved react PERFORMANCE"],
                    )
                ],
            )
        ]

        jd = "we need someone with python and REACT experience."
        highlights = _extract_highlights_used(sample_profile, jd)

        assert len(highlights) > 0
        assert any("PYTHON" in h or "react" in h for h in highlights)

    def test_extract_highlights_used_limited_results(self, sample_profile):
        """Test that highlight extraction is limited to top 5 results."""
        from backend.models import Experience, Project

        # Create multiple experiences with many highlights
        experiences = []
        for i in range(5):  # More than 3 experiences
            experiences.append(
                Experience(
                    title=f"Engineer {i}",
                    company=f"Corp {i}",
                    start_date="2020-01",
                    end_date="2022-12",
                    projects=[
                        Project(
                            name=f"Project {i}",
                            highlights=[
                                f"Built Python API {i}",
                                f"Improved React performance {i}",
                                f"Added Docker support {i}",
                            ],
                        )
                    ],
                )
            )

        sample_profile.experience = experiences

        jd = "We need Python and React developers."
        highlights = _extract_highlights_used(sample_profile, jd)

        # Should be limited to 5 results maximum
        assert len(highlights) <= 5

    def test_extract_highlights_used_partial_word_matches(self, sample_profile):
        """Test that partial word matches work."""
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
                        highlights=["Built microservices architecture", "Implemented API endpoints"],
                    )
                ],
            )
        ]

        jd = "We need someone with microservice experience."
        highlights = _extract_highlights_used(sample_profile, jd)

        assert len(highlights) > 0
        assert any("microservices" in h for h in highlights)

    def test_extract_highlights_used_multiple_experiences(self, sample_profile):
        """Test extracting highlights from multiple experiences."""
        from backend.models import Experience, Project

        sample_profile.experience = [
            Experience(
                title="Senior Engineer",
                company="Tech Corp",
                start_date="2020-01",
                end_date="2022-12",
                projects=[
                    Project(
                        name="API Project",
                        highlights=["Built REST API with Django"],
                    )
                ],
            ),
            Experience(
                title="Junior Engineer",
                company="Startup Inc",
                start_date="2018-01",
                end_date="2019-12",
                projects=[
                    Project(
                        name="Web App",
                        highlights=["Created React components"],
                    )
                ],
            ),
        ]

        jd = "We need Django and React developers."
        highlights = _extract_highlights_used(sample_profile, jd)

        assert len(highlights) > 0
        assert any("Django" in h for h in highlights)
        assert any("React" in h for h in highlights)
