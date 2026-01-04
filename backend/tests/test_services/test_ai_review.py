"""Tests for AI review metadata generation."""

from backend.models import Experience, Project, Skill
from backend.models_ai import AIGenerateCVRequest
from backend.services.ai.review import build_summary


class TestBuildSummary:
    """Test build_summary function."""

    def test_summary_includes_target_role(self):
        """Test that target_role appears in summary."""
        request = AIGenerateCVRequest(
            job_description="We require FastAPI and React.",
            target_role="Full-stack Engineer",
        )
        experiences = []
        skills = []

        summary = build_summary(request, experiences, skills)

        assert any("Full-stack Engineer" in item for item in summary)

    def test_summary_includes_seniority(self):
        """Test that seniority appears in summary."""
        request = AIGenerateCVRequest(
            job_description="We require FastAPI and React.",
            seniority="Senior",
        )
        experiences = []
        skills = []

        summary = build_summary(request, experiences, skills)

        assert any("Senior" in item for item in summary)

    def test_summary_includes_additional_context(self):
        """Test that additional_context appears in summary."""
        request = AIGenerateCVRequest(
            job_description="We require FastAPI and React.",
            additional_context="Rated among top 2% of AI coders in 2025",
        )
        experiences = []
        skills = []

        summary = build_summary(request, experiences, skills)

        summary_text = " ".join(summary)
        assert "top 2%" in summary_text or "Additional context provided" in summary_text

    def test_summary_truncates_long_additional_context(self):
        """Test that very long additional_context is truncated in summary."""
        long_context = "A" * 200
        request = AIGenerateCVRequest(
            job_description="We require FastAPI and React.",
            additional_context=long_context,
        )
        experiences = []
        skills = []

        summary = build_summary(request, experiences, skills)

        summary_text = " ".join(summary)
        # Should be truncated (shows first 100 chars + "...")
        assert "..." in summary_text or len(summary_text) < len(long_context)

    def test_summary_includes_experience_and_skill_counts(self):
        """Test that experience and skill counts appear in summary."""
        request = AIGenerateCVRequest(job_description="We require FastAPI and React.")
        experiences = [
            Experience(
                title="Engineer",
                company="Corp",
                start_date="2023-01",
                end_date="Present",
                projects=[
                    Project(
                        name="Project",
                        highlights=["Highlight"],
                        technologies=["React"],
                    )
                ],
            )
        ]
        skills = [Skill(name="React", category="Frontend")]

        summary = build_summary(request, experiences, skills)

        summary_text = " ".join(summary)
        assert "1 experience" in summary_text or "1 experience(s)" in summary_text
        assert "1 skill" in summary_text or "1 skill(s)" in summary_text

    def test_summary_without_additional_context(self):
        """Test that summary works correctly without additional_context."""
        request = AIGenerateCVRequest(job_description="We require FastAPI and React.")
        experiences = []
        skills = []

        summary = build_summary(request, experiences, skills)

        summary_text = " ".join(summary)
        # Should not contain additional context references
        assert "Additional context provided" not in summary_text
        assert "0 experience" in summary_text or "0 experience(s)" in summary_text
