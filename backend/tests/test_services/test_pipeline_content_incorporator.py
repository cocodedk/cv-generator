"""Tests for Content Incorporator (Step 6)."""

from backend.models import CVData, PersonalInfo, Experience, Project
from backend.services.ai.pipeline.content_incorporator import (
    incorporate_context,
    _build_incorporation,
    _apply_incorporation,
)
from backend.services.ai.pipeline.models import ContextAnalysis, ContextIncorporation


class TestContentIncorporator:
    """Test content incorporator functionality."""

    def test_incorporate_context_skips_directives(self):
        """Test that directive contexts are not incorporated."""
        cv_data = CVData(
            personal_info=PersonalInfo(name="Test User"),
            experience=[],
            education=[],
            skills=[],
        )

        context_analysis = ContextAnalysis(
            type="directive",
            placement="adaptation_guidance",
            suggested_text="Make it enterprise-focused",
            reasoning="This is a directive"
        )

        selected_experiences = []

        result = incorporate_context(cv_data, context_analysis, selected_experiences)

        # Should return unchanged CV data
        assert result == cv_data

    def test_incorporate_context_skips_adaptation_guidance(self):
        """Test that adaptation_guidance contexts are not incorporated."""
        cv_data = CVData(
            personal_info=PersonalInfo(name="Test User"),
            experience=[],
            education=[],
            skills=[],
        )

        context_analysis = ContextAnalysis(
            type="content_statement",
            placement="adaptation_guidance",
            suggested_text="Some guidance",
            reasoning="This is guidance"
        )

        selected_experiences = []

        result = incorporate_context(cv_data, context_analysis, selected_experiences)

        # Should return unchanged CV data
        assert result == cv_data


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


class TestApplyIncorporation:
    """Test the _apply_incorporation function."""

    def test_apply_incorporation_updates_summary(self):
        """Test applying incorporation that updates summary."""
        cv_data = CVData(
            personal_info=PersonalInfo(
                name="Test User",
                summary="Existing summary text"
            ),
            experience=[],
            education=[],
            skills=[],
        )

        incorporation = ContextIncorporation(
            summary_update="Additional summary text",
            project_highlights=[],
            experience_updates={}
        )

        result = _apply_incorporation(cv_data, incorporation)

        assert "Existing summary text" in result.personal_info.summary
        assert "Additional summary text" in result.personal_info.summary
        assert "\n\n" in result.personal_info.summary  # Should be separated by double newline

    def test_apply_incorporation_creates_new_summary(self):
        """Test applying incorporation that creates new summary when none exists."""
        cv_data = CVData(
            personal_info=PersonalInfo(
                name="Test User",
                summary=None  # No existing summary
            ),
            experience=[],
            education=[],
            skills=[],
        )

        incorporation = ContextIncorporation(
            summary_update="New summary text",
            project_highlights=[],
            experience_updates={}
        )

        result = _apply_incorporation(cv_data, incorporation)

        assert result.personal_info.summary == "New summary text"

    def test_apply_incorporation_updates_experience_descriptions(self):
        """Test applying incorporation that updates experience descriptions."""
        cv_data = CVData(
            personal_info=PersonalInfo(name="Test User"),
            experience=[
                Experience(
                    title="Engineer",
                    company="Test Corp",
                    start_date="2023-01",
                    description="Original description"
                ),
                Experience(
                    title="Senior Engineer",
                    company="Another Corp",
                    start_date="2024-01",
                    description="Another description"
                )
            ],
            education=[],
            skills=[],
        )

        incorporation = ContextIncorporation(
            summary_update=None,
            project_highlights=[],
            experience_updates={
                0: "Updated first experience description",
                1: "Updated second experience description"
            }
        )

        result = _apply_incorporation(cv_data, incorporation)

        assert result.experience[0].description == "Updated first experience description"
        assert result.experience[1].description == "Updated second experience description"

    def test_apply_incorporation_adds_project_highlights(self):
        """Test applying incorporation that adds project highlights."""
        cv_data = CVData(
            personal_info=PersonalInfo(name="Test User"),
            experience=[
                Experience(
                    title="Engineer",
                    company="Test Corp",
                    start_date="2023-01",
                    projects=[
                        Project(
                            name="Project A",
                            highlights=["Original highlight"],
                            technologies=[]
                        ),
                        Project(
                            name="Project B",
                            highlights=["Another highlight"],
                            technologies=[]
                        )
                    ]
                )
            ],
            education=[],
            skills=[],
        )

        incorporation = ContextIncorporation(
            summary_update=None,
            project_highlights=[
                (0, 0, "New highlight for Project A"),  # exp_idx, proj_idx, text
                (0, 1, "New highlight for Project B")
            ],
            experience_updates={}
        )

        result = _apply_incorporation(cv_data, incorporation)

        # Project A should have both original and new highlights
        assert len(result.experience[0].projects[0].highlights) == 2
        assert "Original highlight" in result.experience[0].projects[0].highlights
        assert "New highlight for Project A" in result.experience[0].projects[0].highlights

        # Project B should have both original and new highlights
        assert len(result.experience[0].projects[1].highlights) == 2
        assert "Another highlight" in result.experience[0].projects[1].highlights
        assert "New highlight for Project B" in result.experience[0].projects[1].highlights

    def test_apply_incorporation_handles_invalid_indices(self):
        """Test that invalid experience/project indices are handled gracefully."""
        cv_data = CVData(
            personal_info=PersonalInfo(name="Test User"),
            experience=[
                Experience(
                    title="Engineer",
                    company="Test Corp",
                    start_date="2023-01",
                    projects=[]
                )
            ],
            education=[],
            skills=[],
        )

        incorporation = ContextIncorporation(
            summary_update=None,
            project_highlights=[
                (999, 0, "Invalid experience index"),  # Invalid exp_idx
                (0, 999, "Invalid project index")       # Invalid proj_idx
            ],
            experience_updates={
                999: "Invalid experience update"  # Invalid exp_idx
            }
        )

        result = _apply_incorporation(cv_data, incorporation)

        # CV should remain unchanged since all indices are invalid
        assert result.experience[0].projects == []
        assert result.experience[0].description is None

    def test_apply_incorporation_preserves_other_fields(self):
        """Test that applying incorporation preserves all other CV fields."""
        original_cv = CVData(
            personal_info=PersonalInfo(
                name="Test User",
                title="Engineer",
                email="test@example.com",
                summary="Original summary"
            ),
            experience=[
                Experience(
                    title="Engineer",
                    company="Test Corp",
                    start_date="2023-01",
                    description="Original desc",
                    projects=[
                        Project(
                            name="Test Project",
                            highlights=["Original highlight"],
                            technologies=["Python"]
                        )
                    ]
                )
            ],
            education=[],
            skills=[],
            theme="classic",
            layout="default",
            target_company="Test Company",
            target_role="Senior Engineer"
        )

        incorporation = ContextIncorporation(
            summary_update="Updated summary",
            project_highlights=[(0, 0, "New highlight")],
            experience_updates={0: "Updated description"}
        )

        result = _apply_incorporation(original_cv, incorporation)

        # All other fields should be preserved
        assert result.personal_info.name == "Test User"
        assert result.personal_info.title == "Engineer"
        assert result.personal_info.email == "test@example.com"
        assert result.theme == "classic"
        assert result.layout == "default"
        assert result.target_company == "Test Company"
        assert result.target_role == "Senior Engineer"
        assert result.education == []
        assert result.skills == []

        # Technologies should be preserved
        assert result.experience[0].projects[0].technologies == ["Python"]
