"""Tests for JD Analyzer (Step 1)."""

import pytest
from backend.services.ai.pipeline.jd_analyzer import (
    analyze_jd,
    _analyze_with_heuristics,
    _extract_tech_terms,
)


class TestExtractTechTerms:
    """Tests for smart tech term extraction."""

    def test_extracts_from_parentheses_eg_pattern(self):
        """Test extraction from (e.g., X, Y) patterns."""
        text = "Experience with infrastructure as code tools (e.g., Terraform)."
        terms = _extract_tech_terms(text)
        assert "Terraform" in terms or "terraform" in terms

    def test_extracts_multiple_from_parentheses(self):
        """Test extraction of multiple items from parentheses."""
        text = "Knowledge of containerization (e.g., Docker, Kubernetes)."
        terms = _extract_tech_terms(text)
        assert "Docker" in terms or "docker" in terms
        assert "Kubernetes" in terms or "kubernetes" in terms

    def test_extracts_known_single_word_tech(self):
        """Test extraction of known single-word tech terms."""
        text = "Strong programming skills in Python, SQL, and bash."
        terms = _extract_tech_terms(text)
        assert "python" in terms
        assert "sql" in terms
        assert "bash" in terms

    def test_extracts_known_multi_word_tech(self):
        """Test extraction of known multi-word tech terms."""
        text = "Experience with GitHub Actions and Azure DevOps."
        terms = _extract_tech_terms(text)
        assert "github actions" in terms
        assert "azure devops" in terms

    def test_extracts_cloud_providers(self):
        """Test extraction of cloud provider names."""
        text = "Working with Azure, AWS, GCP."
        terms = _extract_tech_terms(text)
        assert "azure" in terms
        assert "aws" in terms
        assert "gcp" in terms

    def test_does_not_extract_non_tech_words(self):
        """Test that common words are not extracted as tech."""
        text = "Strong experience with building solutions."
        terms = _extract_tech_terms(text)
        # These should not be in terms (they're stopwords or non-tech)
        assert "strong" not in terms
        assert "experience" not in terms
        assert "building" not in terms


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
