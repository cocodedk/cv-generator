"""Tests for Content Incorporator incorporate_context functionality."""

from backend.models import CVData, PersonalInfo
from backend.services.ai.pipeline.content_incorporator import incorporate_context
from backend.services.ai.pipeline.models import ContextAnalysis


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
