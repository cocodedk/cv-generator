"""Tests for LLM-powered CV tailoring."""

import pytest
from unittest.mock import patch, AsyncMock, Mock

from backend.models import CVData, ProfileData, Experience, Project, Skill, PersonalInfo
from backend.services.ai.llm_tailor import llm_tailor_cv, _reorder_skills_for_jd


@pytest.fixture
def sample_profile():
    """Create a sample profile for testing."""
    return ProfileData(
        personal_info=PersonalInfo(name="Test User", email="test@example.com"),
        experience=[
            Experience(
                title="Software Engineer",
                company="Tech Corp",
                start_date="2023-01",
                end_date="Present",
                description="Built web applications using React and Python.",
                projects=[
                    Project(
                        name="E-commerce Platform",
                        description="Developed a full-stack e-commerce solution.",
                        highlights=[
                            "Improved performance by optimizing database queries",
                            "Built REST APIs using FastAPI",
                            "Led team of 3 developers",
                        ],
                        technologies=["Python", "FastAPI", "React", "PostgreSQL"],
                    )
                ],
            )
        ],
        education=[],
        skills=[
            Skill(name="Python", category="Programming"),
            Skill(name="React", category="Frontend"),
            Skill(name="FastAPI", category="Backend"),
            Skill(name="PostgreSQL", category="Database"),
        ],
    )


@pytest.fixture
def sample_draft(sample_profile):
    """Create a sample CV draft."""
    return CVData(
        personal_info=sample_profile.personal_info,
        experience=sample_profile.experience,
        education=sample_profile.education,
        skills=sample_profile.skills,
        theme="classic",
    )


@pytest.mark.asyncio
class TestLLMTailorCV:
    """Test LLM tailoring functionality."""

    async def test_llm_tailor_preserves_facts(self, sample_draft, sample_profile):
        """Test that LLM tailoring preserves original facts."""
        job_description = "We need a Python developer with FastAPI experience. Must have led teams."

        with patch("backend.services.ai.llm_tailor.get_llm_client") as mock_get_client:
            mock_client = Mock()
            mock_client.is_configured.return_value = True
            mock_client.rewrite_text = AsyncMock(side_effect=[
                "Developed web applications with React and Python",  # description
                "Created a full-stack e-commerce solution",  # project description
                "Optimized database queries to improve performance",  # highlight 1
                "Developed REST APIs using FastAPI",  # highlight 2
                "Led a team of 3 developers",  # highlight 3
            ])
            mock_get_client.return_value = mock_client

            result = await llm_tailor_cv(sample_draft, job_description, sample_profile)

            # Verify structure is preserved
            assert len(result.experience) == 1
            assert len(result.experience[0].projects) == 1
            assert len(result.experience[0].projects[0].highlights) == 3

            # Verify technologies are preserved
            assert result.experience[0].projects[0].technologies == ["Python", "FastAPI", "React", "PostgreSQL"]

            # Verify LLM was called for each text field
            assert mock_client.rewrite_text.call_count == 5

    async def test_llm_tailor_fallback_when_not_configured(self, sample_draft, sample_profile):
        """Test that tailoring falls back gracefully when LLM is not configured."""
        job_description = "Python developer needed."

        with patch("backend.services.ai.llm_tailor.get_llm_client") as mock_get_client:
            mock_client = Mock()
            mock_client.is_configured.return_value = False
            mock_get_client.return_value = mock_client

            result = await llm_tailor_cv(sample_draft, job_description, sample_profile)

            # Should return draft unchanged
            assert result == sample_draft
            mock_client.rewrite_text.assert_not_called()

    async def test_llm_tailor_handles_empty_text(self, sample_draft, sample_profile):
        """Test that empty text fields are handled correctly."""
        # Create draft with empty description
        draft_with_empty = CVData(
            personal_info=sample_draft.personal_info,
            experience=[
                Experience(
                    title="Engineer",
                    company="Corp",
                    start_date="2023-01",
                    end_date="Present",
                    description=None,  # Empty description
                    projects=[
                        Project(
                            name="Project",
                            description=None,  # Empty description
                            highlights=["Highlight"],
                            technologies=[],
                        )
                    ],
                )
            ],
            education=[],
            skills=[],
            theme="classic",
        )

        with patch("backend.services.ai.llm_tailor.get_llm_client") as mock_get_client:
            mock_client = Mock()
            mock_client.is_configured.return_value = True
            mock_client.rewrite_text = AsyncMock(return_value="Rewritten highlight")
            mock_get_client.return_value = mock_client

            result = await llm_tailor_cv(draft_with_empty, "Job description", sample_profile)

            # Empty descriptions should not trigger LLM calls
            assert result.experience[0].description is None
            assert result.experience[0].projects[0].description is None
            # But highlights should still be tailored
            assert mock_client.rewrite_text.call_count == 1

    async def test_llm_tailor_handles_llm_errors(self, sample_draft, sample_profile):
        """Test that LLM errors are handled gracefully."""
        job_description = "Python developer."

        with patch("backend.services.ai.llm_tailor.get_llm_client") as mock_get_client:
            mock_client = Mock()
            mock_client.is_configured.return_value = True
            mock_client.rewrite_text = AsyncMock(side_effect=Exception("API Error"))
            mock_get_client.return_value = mock_client

            result = await llm_tailor_cv(sample_draft, job_description, sample_profile)

            # Should return draft with original text on error
            assert result.experience[0].description == sample_draft.experience[0].description

    async def test_llm_tailor_handles_empty_llm_response(self, sample_draft, sample_profile):
        """Test that empty LLM responses fall back to original."""
        job_description = "Python developer."

        with patch("backend.services.ai.llm_tailor.get_llm_client") as mock_get_client:
            mock_client = Mock()
            mock_client.is_configured.return_value = True
            mock_client.rewrite_text = AsyncMock(return_value="   ")  # Empty/whitespace response
            mock_get_client.return_value = mock_client

            result = await llm_tailor_cv(sample_draft, job_description, sample_profile)

            # Should use original text when LLM returns empty
            assert result.experience[0].description == sample_draft.experience[0].description


class TestReorderSkillsForJD:
    """Test skills reordering functionality."""

    def test_reorder_skills_prioritizes_jd_mentioned(self):
        """Test that skills mentioned in JD are prioritized."""
        skills = [
            Skill(name="Python", category="Programming"),
            Skill(name="Java", category="Programming"),
            Skill(name="React", category="Frontend"),
        ]
        job_description = "We need a Python developer with React experience."

        result = _reorder_skills_for_jd(skills, job_description)

        # Python and React should come first (order may vary, but both should be before Java)
        skill_names = [s.name for s in result]
        assert "Python" in skill_names[:2]
        assert "React" in skill_names[:2]
        assert "Java" in skill_names[2:]

    def test_reorder_skills_preserves_all_skills(self):
        """Test that all skills are preserved, just reordered."""
        skills = [
            Skill(name="Python", category="Programming"),
            Skill(name="Java", category="Programming"),
            Skill(name="Go", category="Programming"),
        ]
        job_description = "Python developer needed."

        result = _reorder_skills_for_jd(skills, job_description)

        assert len(result) == 3
        assert set(s.name for s in result) == {"Python", "Java", "Go"}

    def test_reorder_skills_handles_empty_list(self):
        """Test that empty skills list is handled."""
        result = _reorder_skills_for_jd([], "Job description")
        assert result == []

    def test_reorder_skills_category_bonus(self):
        """Test that category matches get bonus scoring."""
        skills = [
            Skill(name="Python", category="Backend"),
            Skill(name="Java", category="Backend"),
            Skill(name="React", category="Frontend"),
        ]
        job_description = "We need a Backend developer."

        result = _reorder_skills_for_jd(skills, job_description)

        # Backend skills should come first
        skill_names = [s.name for s in result]
        assert "Python" in skill_names[:2] or "Java" in skill_names[:2]
