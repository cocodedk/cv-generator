"""Tests for Skill Relevance Evaluator."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from backend.models import Skill
from backend.services.ai.pipeline.models import JDAnalysis
from backend.services.ai.pipeline.skill_relevance_evaluator import (
    evaluate_all_skills,
    evaluate_skill_relevance,
    parse_relevance_response,
)


class TestSkillRelevanceEvaluator:
    @pytest.mark.asyncio
    async def test_evaluate_skill_relevance_direct_match(self):
        """Test that direct matches are identified."""
        skill = Skill(name="Python", category="Languages", level="Expert")
        jd_requirements = ["Python", "Django"]

        mock_llm_client = Mock()
        mock_llm_client.rewrite_text = AsyncMock(
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
        mock_llm_client.rewrite_text = AsyncMock(
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
        mock_llm_client.rewrite_text = AsyncMock(
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
        mock_llm_client.rewrite_text = AsyncMock(
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
        """Test that evaluator falls back to heuristic mapper when LLM not configured."""
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
            "backend.services.ai.pipeline.skill_relevance_evaluator.get_llm_client",
            return_value=mock_llm_client,
        ):
            result = await evaluate_all_skills(profile_skills, jd_analysis)

            # Should use fallback mapper
            assert isinstance(result.matched_skills, list)
            assert isinstance(result.selected_skills, list)
            assert isinstance(result.coverage_gaps, list)

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
            if "Python" in prompt:
                return '{"relevant":true,"type":"direct","why":"Match","match":"python"}'
            else:
                return '{"relevant":false,"type":"related","why":"Not relevant","match":""}'

        mock_llm_client.rewrite_text = AsyncMock(side_effect=mock_rewrite)

        with patch(
            "backend.services.ai.pipeline.skill_relevance_evaluator.get_llm_client",
            return_value=mock_llm_client,
        ):
            result = await evaluate_all_skills(profile_skills, jd_analysis)

            # Should only include Python
            assert len(result.selected_skills) == 1
            assert result.selected_skills[0].name == "Python"
