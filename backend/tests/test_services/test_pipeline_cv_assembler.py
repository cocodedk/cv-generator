"""Tests for CV Assembler (Step 5)."""

import pytest
from backend.models import PersonalInfo, Education, Skill
from backend.services.ai.pipeline.models import (
    JDAnalysis,
    SkillMapping,
    SkillMatch,
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
        assert isinstance(coverage.skill_justifications, dict)

    def test_assemble_cv_includes_skill_justifications(self):
        """Test that skill justifications are included in coverage summary."""
        adapted_content = AdaptedContent(
            experiences=[],
            adaptation_notes={},
        )

        personal_info = PersonalInfo(name="Test User")
        education = []
        skills = [Skill(name="Python", category="Languages", level="Expert")]

        skill_match = SkillMatch(
            profile_skill=skills[0],
            jd_requirement="python",
            match_type="exact",
            confidence=0.9,
            explanation="Direct match",
        )

        skill_mapping = SkillMapping(
            matched_skills=[skill_match],
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

        # Should have skill justifications
        assert "Python" in coverage.skill_justifications
        assert "[Direct Match]" in coverage.skill_justifications["Python"]

    def test_assemble_cv_categorizes_ecosystem_matches(self):
        """Test that ecosystem matches are categorized in justifications."""
        adapted_content = AdaptedContent(
            experiences=[],
            adaptation_notes={},
        )

        personal_info = PersonalInfo(name="Test User")
        education = []
        skills = [Skill(name="Express", category="Backend", level="Advanced")]

        skill_match = SkillMatch(
            profile_skill=skills[0],
            jd_requirement="node.js",
            match_type="ecosystem",
            confidence=0.75,
            explanation="Express is a Node.js framework",
        )

        skill_mapping = SkillMapping(
            matched_skills=[skill_match],
            selected_skills=skills,
            coverage_gaps=[],
        )

        jd_analysis = JDAnalysis(
            required_skills={"node.js"},
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

        # Should categorize ecosystem matches
        assert "Express" in coverage.skill_justifications
        assert "[Technology Ecosystem]" in coverage.skill_justifications["Express"]
        # Ecosystem matches should be in partially_covered
        assert "node.js" in coverage.partially_covered

    def test_assemble_cv_includes_responsibility_support_matches(self):
        """Test that responsibility support matches are included."""
        adapted_content = AdaptedContent(
            experiences=[],
            adaptation_notes={},
        )

        personal_info = PersonalInfo(name="Test User")
        education = []
        skills = [Skill(name="CI/CD", category="DevOps", level="Advanced")]

        skill_match = SkillMatch(
            profile_skill=skills[0],
            jd_requirement="deployment",
            match_type="responsibility_support",
            confidence=0.7,
            explanation="CI/CD supports deployment responsibilities",
        )

        skill_mapping = SkillMapping(
            matched_skills=[skill_match],
            selected_skills=skills,
            coverage_gaps=[],
        )

        jd_analysis = JDAnalysis(
            required_skills={"python"},
            preferred_skills=set(),
            responsibilities=["Deploy applications"],
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

        # Should include responsibility support matches
        assert "CI/CD" in coverage.skill_justifications
        assert "[Supports Responsibilities]" in coverage.skill_justifications["CI/CD"]
        assert "deployment" in coverage.partially_covered
