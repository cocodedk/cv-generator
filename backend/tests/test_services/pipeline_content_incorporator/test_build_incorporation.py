"""Tests for Content Incorporator _build_incorporation functionality."""

from backend.models import Experience, Project
from backend.services.ai.pipeline.content_incorporator import _build_incorporation
from backend.services.ai.pipeline.models import ContextAnalysis


class TestBuildIncorporation:
    """Test the _build_incorporation function."""

    def test_build_incorporation_for_summary_placement(self):
        """Test building incorporation for summary placement."""
        context_analysis = ContextAnalysis(
            type="content_statement",
            placement="summary",
            suggested_text="Available for remote work",
            reasoning="General availability statement"
        )

        selected_experiences = []

        result = _build_incorporation(context_analysis, selected_experiences)

        assert result.summary_update == "Available for remote work"
        assert result.project_highlights == []
        assert result.experience_updates == {}

    def test_build_incorporation_for_project_highlight_placement(self):
        """Test building incorporation for project highlight placement."""
        context_analysis = ContextAnalysis(
            type="achievement",
            placement="project_highlight",
            suggested_text="Reduced deployment time by 50%",
            reasoning="Project-specific achievement"
        )

        selected_experiences = [
            Experience(
                title="Engineer",
                company="Test Corp",
                start_date="2023-01",
                projects=[
                    Project(name="CI/CD Pipeline", highlights=["Built pipeline"], technologies=[])
                ]
            )
        ]

        result = _build_incorporation(context_analysis, selected_experiences)

        assert result.summary_update is None
        assert len(result.project_highlights) == 1
        assert result.project_highlights[0] == (0, 0, "Reduced deployment time by 50%")  # exp_idx, proj_idx, text
        assert result.experience_updates == {}

    def test_build_incorporation_for_project_highlight_no_projects_fallback(self):
        """Test project highlight placement falls back to summary when no projects available."""
        context_analysis = ContextAnalysis(
            type="achievement",
            placement="project_highlight",
            suggested_text="Achievement text",
            reasoning="Achievement"
        )

        selected_experiences = [
            Experience(
                title="Engineer",
                company="Test Corp",
                start_date="2023-01",
                projects=[]  # No projects
            )
        ]

        result = _build_incorporation(context_analysis, selected_experiences)

        # Should fallback to summary
        assert result.summary_update == "Achievement text"
        assert result.project_highlights == []
        assert result.experience_updates == {}

    def test_build_incorporation_for_experience_description_placement(self):
        """Test building incorporation for experience description placement."""
        context_analysis = ContextAnalysis(
            type="achievement",
            placement="experience_description",
            suggested_text="Led team of 5 developers",
            reasoning="Role-specific achievement"
        )

        selected_experiences = [
            Experience(
                title="Senior Engineer",
                company="Test Corp",
                start_date="2023-01",
                description="Built web applications"
            )
        ]

        result = _build_incorporation(context_analysis, selected_experiences)

        assert result.summary_update is None
        assert result.project_highlights == []
        assert len(result.experience_updates) == 1
        assert result.experience_updates[0] == "Built web applications\n\nLed team of 5 developers"

    def test_build_incorporation_for_experience_description_empty_existing(self):
        """Test experience description placement with empty existing description."""
        context_analysis = ContextAnalysis(
            type="content_statement",
            placement="experience_description",
            suggested_text="New description text",
            reasoning="New content"
        )

        selected_experiences = [
            Experience(
                title="Engineer",
                company="Test Corp",
                start_date="2023-01",
                description=None  # Empty description
            )
        ]

        result = _build_incorporation(context_analysis, selected_experiences)

        assert result.experience_updates[0] == "New description text"

    def test_build_incorporation_for_experience_description_no_experiences_fallback(self):
        """Test experience description placement falls back to summary when no experiences."""
        context_analysis = ContextAnalysis(
            type="achievement",
            placement="experience_description",
            suggested_text="Achievement text",
            reasoning="Achievement"
        )

        selected_experiences = []  # No experiences

        result = _build_incorporation(context_analysis, selected_experiences)

        # Should fallback to summary
        assert result.summary_update == "Achievement text"
        assert result.project_highlights == []
        assert result.experience_updates == {}
