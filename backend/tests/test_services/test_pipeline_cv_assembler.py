"""Tests for CV Assembler (Step 5)."""

import pytest
from backend.models import PersonalInfo, Education, Skill
from backend.services.ai.pipeline.models import (
    JDAnalysis,
    SkillMapping,
    AdaptedContent,
)
from backend.services.ai.pipeline.cv_assembler import assemble_cv


class TestCVAssembler:
    def test_assemble_cv_creates_valid_cv(self):
        """Verify that assembler creates a valid CV from adapted content."""
        adapted_content = AdaptedContent(
            experiences=[],
            adaptation_notes={},
        )

        personal_info = PersonalInfo(name="Test User")
        education = []
        skills = [Skill(name="Python", category="Languages", level="Expert")]

        skill_mapping = SkillMapping(
            matched_skills=[],
            selected_skills=skills,
            coverage_gaps=[],
        )

        jd_analysis = JDAnalysis(
            required_skills={"python"},
            preferred_skills=set(),
            responsibilities=[],
            domain_keywords=set(),
            seniority_signals=[],
        )

        cv, coverage = assemble_cv(
            adapted_content,
            personal_info,
            education,
            skills,
            skill_mapping,
            jd_analysis,
        )

        assert cv.personal_info.name == "Test User"
        assert len(cv.skills) > 0
        assert isinstance(coverage.covered_requirements, list)
        assert isinstance(coverage.gaps, list)
