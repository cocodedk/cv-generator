"""Tests for JD Analyzer (Step 1)."""

import pytest
from backend.services.ai.pipeline.jd_analyzer import analyze_jd, _analyze_with_heuristics


class TestJDAnalyzer:
    def test_heuristic_analysis_extracts_required_skills(self):
        jd = "We require Python and FastAPI. Must have PostgreSQL experience."
        result = _analyze_with_heuristics(jd)

        # Check normalized versions (extract_words may include punctuation)
        required_normalized = {kw.rstrip(".,;:!?") for kw in result.required_skills}
        assert "python" in required_normalized
        assert "fastapi" in required_normalized
        assert "postgresql" in required_normalized

    def test_heuristic_analysis_extracts_preferred_skills(self):
        jd = "Nice to have: React, Docker. Bonus: Kubernetes."
        result = _analyze_with_heuristics(jd)

        assert "react" in result.preferred_skills or "react" in result.required_skills
        assert len(result.preferred_skills) > 0 or len(result.required_skills) > 0

    def test_heuristic_analysis_extracts_responsibilities(self):
        jd = "You will build APIs. Design systems. Lead teams."
        result = _analyze_with_heuristics(jd)

        assert len(result.responsibilities) > 0

    @pytest.mark.asyncio
    async def test_analyze_jd_fallback_to_heuristics_when_llm_not_configured(self):
        jd = "We require Python and FastAPI."
        result = await analyze_jd(jd)

        assert isinstance(result.required_skills, set)
        assert isinstance(result.preferred_skills, set)
        assert isinstance(result.responsibilities, list)
