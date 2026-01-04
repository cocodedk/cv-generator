"""Unit tests for AI selection logic."""

import pytest
from backend.models import Skill
from backend.services.ai.selection import select_skills
from backend.services.ai.target_spec import build_target_spec


@pytest.mark.unit
class TestSkillSelection:
    def test_skills_vary_by_job_description(self):
        """Skills selected should differ based on job description keywords."""
        skills = [
            Skill(name="Python", category="Backend"),
            Skill(name="Django", category="Backend"),
            Skill(name="React", category="Frontend"),
            Skill(name="TypeScript", category="Frontend"),
            Skill(name="PostgreSQL", category="Database"),
        ]

        # Backend-focused job
        backend_spec = build_target_spec("We require Python and Django experience.")
        backend_skills = select_skills(skills, backend_spec, [])

        # Frontend-focused job
        frontend_spec = build_target_spec("Must have React and TypeScript skills.")
        frontend_skills = select_skills(skills, frontend_spec, [])

        # Skills should differ
        backend_names = {s.name for s in backend_skills}
        frontend_names = {s.name for s in frontend_skills}
        assert backend_names != frontend_names
        assert "Python" in backend_names or "Django" in backend_names
        assert "React" in frontend_names or "TypeScript" in frontend_names

    def test_required_keywords_score_higher_than_preferred(self):
        """Skills matching required keywords should rank above preferred."""
        skills = [
            Skill(name="Python", category="Backend"),
            Skill(name="Go", category="Backend"),
        ]
        # Use separate lines so preferred hint matching works correctly
        spec = build_target_spec("Must have Python.\nNice to have Go experience.")
        selected = select_skills(skills, spec, [])

        # Python (required) should come before Go (preferred)
        assert selected[0].name == "Python"

    def test_fallback_when_no_skills_match(self):
        """Should return some skills even if none match the job description."""
        skills = [
            Skill(name="COBOL", category="Legacy"),
            Skill(name="Fortran", category="Legacy"),
        ]
        spec = build_target_spec("We need React and TypeScript developers.")
        selected = select_skills(skills, spec, [])

        # Should fallback to returning skills rather than empty list
        assert len(selected) > 0
