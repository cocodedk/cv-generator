"""Tests for CV Assembler _apply_context_incorporation functionality."""

from backend.models import PersonalInfo, Experience, Project, CVData
from backend.services.ai.pipeline.models import ContextIncorporation
from backend.services.ai.pipeline.cv_assembler import _apply_context_incorporation


class TestApplyContextIncorporation:
    """Test the _apply_context_incorporation function."""

    def test_apply_context_incorporation_updates_summary(self):
        """Test that summary is updated correctly."""
        cv_data = CVData(
            personal_info=PersonalInfo(
                name="Test User",
                summary="Original summary"
            ),
            experience=[],
            education=[],
            skills=[],
        )

        incorporation = ContextIncorporation(
            summary_update="Additional information",
            project_highlights=[],
            experience_updates={}
        )

        result = _apply_context_incorporation(cv_data, incorporation)

        assert "Original summary" in result.personal_info.summary
        assert "Additional information" in result.personal_info.summary
        assert "\n\n" in result.personal_info.summary

    def test_apply_context_incorporation_updates_experience_descriptions(self):
        """Test that experience descriptions are updated correctly."""
        cv_data = CVData(
            personal_info=PersonalInfo(name="Test User"),
            experience=[
                Experience(
                    title="Engineer",
                    company="Test Corp",
                    start_date="2023-01",
                    description="Original description"
                )
            ],
            education=[],
            skills=[],
        )

        incorporation = ContextIncorporation(
            summary_update=None,
            project_highlights=[],
            experience_updates={0: "Updated description"}
        )

        result = _apply_context_incorporation(cv_data, incorporation)

        assert result.experience[0].description == "Updated description"

    def test_apply_context_incorporation_adds_project_highlights(self):
        """Test that project highlights are added correctly."""
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
                            highlights=["Existing highlight"],
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
            project_highlights=[(0, 0, "New highlight")],
            experience_updates={}
        )

        result = _apply_context_incorporation(cv_data, incorporation)

        highlights = result.experience[0].projects[0].highlights
        assert len(highlights) == 2
        assert "Existing highlight" in highlights
        assert "New highlight" in highlights

    def test_apply_context_incorporation_handles_empty_incorporation(self):
        """Test that empty incorporation doesn't change the CV."""
        original_cv = CVData(
            personal_info=PersonalInfo(name="Test User", summary="Summary"),
            experience=[],
            education=[],
            skills=[],
        )

        incorporation = ContextIncorporation(
            summary_update=None,
            project_highlights=[],
            experience_updates={}
        )

        result = _apply_context_incorporation(original_cv, incorporation)

        # Should be unchanged
        assert result == original_cv

    def test_apply_context_incorporation_preserves_cv_structure(self):
        """Test that all CV fields are preserved correctly."""
        cv_data = CVData(
            personal_info=PersonalInfo(
                name="Test User",
                title="Engineer",
                email="test@example.com",
                summary="Original summary"
            ),
            experience=[],
            education=[],
            skills=[],
            theme="classic",
            layout="default",
            target_company="Test Company",
            target_role="Test Role"
        )

        incorporation = ContextIncorporation(
            summary_update="Updated summary",
            project_highlights=[],
            experience_updates={}
        )

        result = _apply_context_incorporation(cv_data, incorporation)

        # All fields should be preserved
        assert result.personal_info.name == "Test User"
        assert result.personal_info.title == "Engineer"
        assert result.personal_info.email == "test@example.com"
        assert result.theme == "classic"
        assert result.layout == "default"
        assert result.target_company == "Test Company"
        assert result.target_role == "Test Role"
        assert "Updated summary" in result.personal_info.summary
