"""Tests for Skill Relevance Evaluator."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from backend.models import Skill
from backend.services.ai.pipeline.models import JDAnalysis
from backend.services.ai.pipeline.skill_relevance_evaluator import (
    evaluate_all_skills,
    evaluate_skill_relevance,
    parse_relevance_response,
    _skill_in_raw_jd,
)


class TestSkillInRawJD:
    """Tests for raw JD text matching."""

    def test_finds_exact_match(self):
        """Test that exact skill name is found in JD."""
        jd = "Strong programming skills in Python and SQL."
        assert _skill_in_raw_jd("Python", jd) is True
        assert _skill_in_raw_jd("SQL", jd) is True

    def test_case_insensitive(self):
        """Test that matching is case-insensitive."""
        jd = "Experience with PYTHON and sql."
        assert _skill_in_raw_jd("Python", jd) is True
        assert _skill_in_raw_jd("python", jd) is True
        assert _skill_in_raw_jd("SQL", jd) is True

    def test_word_boundary_prevents_false_positives(self):
        """Test that Java doesn't match JavaScript."""
        jd = "Must have JavaScript experience."
        assert _skill_in_raw_jd("Java", jd) is False
        assert _skill_in_raw_jd("JavaScript", jd) is True

    def test_does_not_match_absent_skill(self):
        """Test that skills not in JD return False."""
        jd = "Experience with Python and Django."
        assert _skill_in_raw_jd("React", jd) is False
        assert _skill_in_raw_jd("Vue", jd) is False

    def test_matches_in_parentheses(self):
        """Test that skills in parentheses are found."""
        jd = "Experience with containerization (e.g., Docker, Kubernetes)."
        assert _skill_in_raw_jd("Docker", jd) is True
        assert _skill_in_raw_jd("Kubernetes", jd) is True


class TestRawJDMatching:
    """Tests for raw JD matching in evaluate_all_skills."""

    @pytest.mark.asyncio
    async def test_raw_jd_matching_finds_literal_skills(self):
        """Test that skills appearing literally in JD are matched."""
        profile_skills = [
            Skill(name="Python", category="Languages"),
            Skill(name="Docker", category="DevOps"),
            Skill(name="React", category="Frontend"),  # Not in JD
        ]
        jd_analysis = JDAnalysis(
            required_skills=set(),  # Empty - rely on raw JD matching
            preferred_skills=set(),
            responsibilities=[],
            domain_keywords=set(),
            seniority_signals=[],
        )
        raw_jd = "We need Python and Docker experience."

        mock_llm_client = Mock()
        mock_llm_client.is_configured.return_value = False

        with patch(
            "backend.services.ai.pipeline.skill_relevance_evaluator.evaluation.get_llm_client",
            return_value=mock_llm_client,
        ):
            result = await evaluate_all_skills(profile_skills, jd_analysis, raw_jd=raw_jd)

            selected_names = [s.name for s in result.selected_skills]
            assert "Python" in selected_names
            assert "Docker" in selected_names
            assert "React" not in selected_names


class TestSkillRelevanceEvaluator:
    @pytest.mark.asyncio
    async def test_evaluate_skill_relevance_direct_match(self):
        """Test that direct matches are identified."""
        skill = Skill(name="Python", category="Languages", level="Expert")
        jd_requirements = ["Python", "Django"]

        mock_llm_client = Mock()
        mock_llm_client.generate_text = AsyncMock(
            return_value='{"relevant":true,"type":"direct","why":"Exact match","match":"Python"}'
        )

        result = await evaluate_skill_relevance(skill, jd_requirements, mock_llm_client)

        assert result.relevant is True
        assert result.relevance_type == "direct"
        assert result.match == "Python"

    @pytest.mark.asyncio
    async def test_evaluate_skill_relevance_foundation(self):
        """Test that foundation/base language matches are identified."""
        skill = Skill(name="Python", category="Languages", level="Expert")
        jd_requirements = ["Django", "Flask"]

        mock_llm_client = Mock()
        mock_llm_client.generate_text = AsyncMock(
            return_value='{"relevant":true,"type":"foundation","why":"Django uses Python","match":"Django"}'
        )

        result = await evaluate_skill_relevance(skill, jd_requirements, mock_llm_client)

        assert result.relevant is True
        assert result.relevance_type == "foundation"
        assert "Django" in result.match

    @pytest.mark.asyncio
    async def test_evaluate_skill_relevance_alternative(self):
        """Test that alternative framework matches are identified."""
        skill = Skill(name="Flask", category="Frameworks", level="Advanced")
        jd_requirements = ["Django"]

        mock_llm_client = Mock()
        mock_llm_client.generate_text = AsyncMock(
            return_value='{"relevant":true,"type":"alternative","why":"Both Python web frameworks","match":"Django"}'
        )

        result = await evaluate_skill_relevance(skill, jd_requirements, mock_llm_client)

        assert result.relevant is True
        assert result.relevance_type == "alternative"

    @pytest.mark.asyncio
    async def test_evaluate_skill_relevance_not_relevant(self):
        """Test that irrelevant skills are correctly identified."""
        skill = Skill(name="COBOL", category="Legacy", level="Expert")
        jd_requirements = ["Python", "Django"]

        mock_llm_client = Mock()
        mock_llm_client.generate_text = AsyncMock(
            return_value='{"relevant":false,"type":"related","why":"Not related","match":""}'
        )

        result = await evaluate_skill_relevance(skill, jd_requirements, mock_llm_client)

        assert result.relevant is False

    def test_parse_relevance_response_valid_json(self):
        """Test parsing valid JSON response."""
        response = '{"relevant":true,"type":"foundation","why":"Django uses Python","match":"Django"}'
        result = parse_relevance_response(response)

        assert result.relevant is True
        assert result.relevance_type == "foundation"
        assert result.why == "Django uses Python"
        assert result.match == "Django"

    def test_parse_relevance_response_text_fallback(self):
        """Test parsing text response when JSON parsing fails."""
        response = "Yes, Python is relevant because Django uses it."
        result = parse_relevance_response(response)

        # Should infer relevance from text
        assert result.relevant is True

    def test_parse_relevance_response_invalid_json(self):
        """Test parsing invalid JSON falls back gracefully."""
        response = "This is not JSON at all"
        result = parse_relevance_response(response)

        # Should return not relevant as fallback
        assert result.relevant is False

    @pytest.mark.asyncio
    async def test_evaluate_all_skills_fallback_when_llm_not_configured(self):
        """Test that evaluator works when LLM not configured if all skills match in layers 1-2."""
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

        mock_llm_client = Mock()
        mock_llm_client.is_configured.return_value = False

        with patch(
            "backend.services.ai.pipeline.skill_relevance_evaluator.evaluation.get_llm_client",
            return_value=mock_llm_client,
        ):
            result = await evaluate_all_skills(profile_skills, jd_analysis, raw_jd="Python required")
            # Python matches via tech_terms_match in layer 2, so no LLM needed
            assert "Python" in [s.name for s in result.selected_skills]
            # Should not raise error because all skills matched without LLM

    @pytest.mark.asyncio
    async def test_evaluate_all_skills_filters_relevant_only(self):
        """Test that only relevant skills are included in result."""
        profile_skills = [
            Skill(name="Python", category="Languages", level="Expert"),
            Skill(name="COBOL", category="Legacy", level="Expert"),
        ]
        jd_analysis = JDAnalysis(
            required_skills={"python"},
            preferred_skills=set(),
            responsibilities=[],
            domain_keywords=set(),
            seniority_signals=[],
        )

        mock_llm_client = Mock()
        mock_llm_client.is_configured.return_value = True

        async def mock_rewrite(text, prompt):
            # Check for the specific skill being evaluated (in quotes after "Is the skill")
            if 'skill "Python"' in prompt:
                return '{"relevant":true,"type":"direct","why":"Match","match":"python"}'
            else:
                return '{"relevant":false,"type":"related","why":"Not relevant","match":""}'

        mock_llm_client.generate_text = AsyncMock(side_effect=mock_rewrite)

        with patch(
            "backend.services.ai.pipeline.skill_relevance_evaluator.evaluation.get_llm_client",
            return_value=mock_llm_client,
        ):
            result = await evaluate_all_skills(profile_skills, jd_analysis)

            # Should only include Python (COBOL may be added by heuristic fallback
            # but won't match python via tech_terms_match)
            assert "Python" in [s.name for s in result.selected_skills]
            # COBOL should not be in selected skills (no match to "python")
            assert "COBOL" not in [s.name for s in result.selected_skills]
