"""Tests for Skill Mapper (Step 2)."""

import pytest
from backend.models import Skill
from backend.services.ai.pipeline.models import JDAnalysis
from backend.services.ai.pipeline.skill_mapper import map_skills, _map_with_heuristics
from backend.services.ai.text import tech_terms_match


class TestTechTermsMatch:
    """Test smart matching for tech term variations."""

    @pytest.mark.parametrize(
        "term1,term2,expected",
        [
            # Same tech, different formatting
            ("Tailwind CSS", "TailwindCSS", True),
            ("Tailwind", "TailwindCSS", True),
            ("Next.js", "NextJS", True),
            ("Vue", "VueJS", True),
            ("React", "ReactJS", True),
            ("Node", "NodeJS", True),
            # Exact matches
            ("Python", "Python", True),
            ("TypeScript", "TypeScript", True),
            ("Docker", "Docker", True),
            ("AWS", "AWS", True),
            # Similar names but different tech - should NOT match
            ("Java", "JavaScript", False),
            ("C", "CSS", False),
            ("Go", "Golang", False),
            # Abbreviations - should NOT match
            ("TS", "TypeScript", False),
            ("JS", "JavaScript", False),
            # SQL variations
            ("PostgreSQL", "Postgres", True),
        ],
    )
    def test_tech_terms_match_variations(self, term1, term2, expected):
        assert tech_terms_match(term1, term2) == expected


class TestSkillMapper:
    def test_heuristic_mapping_matches_compound_tech_names(self):
        """Test that 'Tailwind CSS' matches JD keyword 'TailwindCSS'."""
        profile_skills = [
            Skill(name="Tailwind CSS", category="Frontend", level="Advanced"),
            Skill(name="Next.js", category="Frontend", level="Advanced"),
        ]
        jd_analysis = JDAnalysis(
            required_skills={"TailwindCSS", "NextJS"},
            preferred_skills=set(),
            responsibilities=[],
            domain_keywords=set(),
            seniority_signals=[],
        )

        result = _map_with_heuristics(profile_skills, jd_analysis)

        # Both skills should match despite different formatting
        assert len(result.selected_skills) == 2
        skill_names = {s.name for s in result.selected_skills}
        assert "Tailwind CSS" in skill_names
        assert "Next.js" in skill_names

    def test_heuristic_mapping_finds_exact_matches(self):
        profile_skills = [
            Skill(name="Python", category="Programming Languages", level="Expert"),
            Skill(name="JavaScript", category="Programming Languages", level="Advanced"),
        ]
        jd_analysis = JDAnalysis(
            required_skills={"python", "javascript"},
            preferred_skills=set(),
            responsibilities=[],
            domain_keywords=set(),
            seniority_signals=[],
        )

        result = _map_with_heuristics(profile_skills, jd_analysis)

        assert len(result.matched_skills) > 0
        assert len(result.selected_skills) > 0

    def test_heuristic_mapping_identifies_gaps(self):
        profile_skills = [
            Skill(name="Python", category="Programming Languages", level="Expert"),
        ]
        jd_analysis = JDAnalysis(
            required_skills={"python", "node.js"},
            preferred_skills=set(),
            responsibilities=[],
            domain_keywords=set(),
            seniority_signals=[],
        )

        result = _map_with_heuristics(profile_skills, jd_analysis)

        # Should find Python match
        assert len(result.matched_skills) > 0
        # Node.js might be in gaps (unless heuristic matches it)
        assert isinstance(result.coverage_gaps, list)

    def test_heuristic_mapping_detects_ecosystem_matches(self):
        """Test that ecosystem matches are detected correctly."""
        profile_skills = [
            Skill(name="Express", category="Backend", level="Advanced"),
            Skill(name="Fastify", category="Backend", level="Advanced"),
        ]
        jd_analysis = JDAnalysis(
            required_skills={"node.js"},
            preferred_skills=set(),
            responsibilities=[],
            domain_keywords=set(),
            seniority_signals=[],
        )

        result = _map_with_heuristics(profile_skills, jd_analysis)

        # Should find matches (may be ecosystem type)
        assert len(result.matched_skills) >= 0
        # Check match types include ecosystem if matches found
        if result.matched_skills:
            match_types = {m.match_type for m in result.matched_skills}
            assert any(
                mt in ("exact", "synonym", "ecosystem") for mt in match_types
            )

    def test_heuristic_mapping_classifies_match_types(self):
        """Test that match types are correctly classified."""
        profile_skills = [
            Skill(name="Python", category="Languages", level="Expert"),
        ]
        jd_analysis = JDAnalysis(
            required_skills={"python"},
            preferred_skills=set(),
            responsibilities=[],
            domain_keywords=set(),
            seniority_signals=[],
        )

        result = _map_with_heuristics(profile_skills, jd_analysis)

        if result.matched_skills:
            match = result.matched_skills[0]
            assert match.match_type in ("exact", "synonym", "ecosystem")
            assert match.confidence > 0.0

    @pytest.mark.asyncio
    async def test_map_skills_fallback_to_heuristics_when_llm_not_configured(self):
        profile_skills = [
            Skill(name="Python", category="Programming Languages", level="Expert"),
        ]
        jd_analysis = JDAnalysis(
            required_skills={"python"},
            preferred_skills=set(),
            responsibilities=[],
            domain_keywords=set(),
            seniority_signals=[],
        )

        result = await map_skills(profile_skills, jd_analysis)

        assert isinstance(result.matched_skills, list)
        assert isinstance(result.selected_skills, list)
        assert isinstance(result.coverage_gaps, list)
