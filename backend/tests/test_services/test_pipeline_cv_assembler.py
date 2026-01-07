"""Tests for CV Assembler (Step 5)."""

from backend.models import PersonalInfo, Skill, Experience, Project
from backend.services.ai.pipeline.models import (
    JDAnalysis,
    SkillMapping,
    SkillMatch,
    AdaptedContent,
    ContextIncorporation,
)
from backend.services.ai.pipeline.cv_assembler import assemble_cv, _apply_context_incorporation


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

    def test_assemble_cv_applies_context_incorporation(self):
        """Test that context incorporation is applied when provided."""
        adapted_content = AdaptedContent(
            experiences=[
                Experience(
                    title="Engineer",
                    company="Test Corp",
                    start_date="2023-01",
                    projects=[
                        Project(
                            name="Test Project",
                            highlights=["Original highlight"],
                            technologies=[]
                        )
                    ]
                )
            ],
            adaptation_notes={},
        )

        personal_info = PersonalInfo(name="Test User", summary="Original summary")
        education = []
        skills = [Skill(name="Python", category="Languages")]

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

        context_incorporation = ContextIncorporation(
            summary_update="Additional context",
            project_highlights=[(0, 0, "New project highlight")],
            experience_updates={}
        )

        cv, coverage = assemble_cv(
            adapted_content,
            personal_info,
            education,
            skills,
            skill_mapping,
            jd_analysis,
            context_incorporation,
        )

        # Summary should be updated
        assert "Original summary" in cv.personal_info.summary
        assert "Additional context" in cv.personal_info.summary

        # Project highlight should be added
        assert len(cv.experience[0].projects[0].highlights) == 2
        assert "Original highlight" in cv.experience[0].projects[0].highlights
        assert "New project highlight" in cv.experience[0].projects[0].highlights

    def test_assemble_cv_handles_none_context_incorporation(self):
        """Test that assemble_cv works correctly when context_incorporation is None."""
        adapted_content = AdaptedContent(
            experiences=[],
            adaptation_notes={},
        )

        personal_info = PersonalInfo(name="Test User")
        education = []
        skills = [Skill(name="Python", category="Languages")]

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
            None,  # No context incorporation
        )

        # Should work normally
        assert cv.personal_info.name == "Test User"
        assert len(cv.skills) == 1


class TestApplyContextIncorporation:
    """Test the _apply_context_incorporation function."""

    def test_apply_context_incorporation_updates_summary(self):
        """Test that summary is updated correctly."""
        from backend.models import CVData

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
        from backend.models import CVData

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
        from backend.models import CVData

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
        from backend.models import CVData

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
        from backend.models import CVData

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
