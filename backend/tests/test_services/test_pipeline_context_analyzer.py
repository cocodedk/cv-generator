"""Tests for Context Analyzer (Step 0)."""

import json
import pytest
from unittest.mock import AsyncMock, Mock, patch

from backend.services.ai.pipeline.context_analyzer import (
    analyze_additional_context,
    _analyze_with_llm,
)
from backend.services.ai.pipeline.models import ContextAnalysis


class TestContextAnalyzer:
    """Test context analyzer functionality."""

    @pytest.mark.asyncio
    async def test_analyze_additional_context_returns_none_for_empty_context(self):
        """Test that None is returned when additional_context is empty."""
        result = await analyze_additional_context("", "job description")
        assert result is None

        result = await analyze_additional_context(None, "job description")
        assert result is None

    @pytest.mark.asyncio
    async def test_analyze_additional_context_fallback_when_llm_not_configured(self):
        """Test fallback behavior when LLM is not configured."""
        # Mock LLM client as not configured
        mock_llm_client = Mock()
        mock_llm_client.is_configured.return_value = False

        with patch("backend.services.ai.pipeline.context_analyzer.get_llm_client", return_value=mock_llm_client):
            # Test directive detection fallback
            result = await analyze_additional_context("Make this more enterprise-focused", "job desc")
            assert result.type == "directive"
            assert result.placement == "adaptation_guidance"
            assert "enterprise-focused" in result.suggested_text

            # Test content statement fallback
            result = await analyze_additional_context("Rated top 2% of AI coders", "job desc")
            assert result.type == "content_statement"
            assert result.placement == "summary"
            assert "Rated top 2%" in result.suggested_text

    @pytest.mark.asyncio
    async def test_analyze_additional_context_with_llm_directive(self):
        """Test LLM analysis for directive context."""
        mock_llm_client = Mock()
        mock_llm_client.is_configured.return_value = True
        mock_llm_client.rewrite_text = AsyncMock(return_value=json.dumps({
            "type": "directive",
            "placement": "adaptation_guidance",
            "suggested_text": "Emphasize enterprise scalability",
            "reasoning": "This is guidance on how to adapt content"
        }))

        with patch("backend.services.ai.pipeline.context_analyzer.get_llm_client", return_value=mock_llm_client):
            result = await analyze_additional_context("Make this more enterprise-focused", "We need scalable solutions")

            assert result.type == "directive"
            assert result.placement == "adaptation_guidance"
            assert result.suggested_text == "Emphasize enterprise scalability"
            assert result.reasoning == "This is guidance on how to adapt content"

    @pytest.mark.asyncio
    async def test_analyze_additional_context_with_llm_content_statement(self):
        """Test LLM analysis for content statement context."""
        mock_llm_client = Mock()
        mock_llm_client.is_configured.return_value = True
        mock_llm_client.rewrite_text = AsyncMock(return_value=json.dumps({
            "type": "content_statement",
            "placement": "summary",
            "suggested_text": "Available for on-site work in San Francisco",
            "reasoning": "General statement about availability"
        }))

        with patch("backend.services.ai.pipeline.context_analyzer.get_llm_client", return_value=mock_llm_client):
            result = await analyze_additional_context("I am willing to relocate to San Francisco", "Remote work available")

            assert result.type == "content_statement"
            assert result.placement == "summary"
            assert result.suggested_text == "Available for on-site work in San Francisco"
            assert result.reasoning == "General statement about availability"

    @pytest.mark.asyncio
    async def test_analyze_additional_context_with_llm_achievement(self):
        """Test LLM analysis for achievement context."""
        mock_llm_client = Mock()
        mock_llm_client.is_configured.return_value = True
        mock_llm_client.rewrite_text = AsyncMock(return_value=json.dumps({
            "type": "achievement",
            "placement": "project_highlight",
            "suggested_text": "Rated among top 2% of AI developers globally in 2025",
            "reasoning": "Achievement should be highlighted in relevant projects"
        }))

        with patch("backend.services.ai.pipeline.context_analyzer.get_llm_client", return_value=mock_llm_client):
            result = await analyze_additional_context("Rated top 2% of AI coders in 2025", "Python developer needed")

            assert result.type == "achievement"
            assert result.placement == "project_highlight"
            assert "top 2%" in result.suggested_text
            assert result.reasoning == "Achievement should be highlighted in relevant projects"

    @pytest.mark.asyncio
    async def test_analyze_additional_context_with_llm_mixed(self):
        """Test LLM analysis for mixed context type."""
        mock_llm_client = Mock()
        mock_llm_client.is_configured.return_value = True
        mock_llm_client.rewrite_text = AsyncMock(return_value=json.dumps({
            "type": "mixed",
            "placement": "summary",
            "suggested_text": "Highly rated AI developer available for enterprise projects",
            "reasoning": "Contains both achievement and availability statement"
        }))

        with patch("backend.services.ai.pipeline.context_analyzer.get_llm_client", return_value=mock_llm_client):
            result = await analyze_additional_context("Rated top 2% of AI coders and willing to work enterprise", "Enterprise software")

            assert result.type == "mixed"
            assert result.placement == "summary"
            assert result.suggested_text == "Highly rated AI developer available for enterprise projects"

    @pytest.mark.asyncio
    async def test_analyze_additional_context_handles_llm_error(self):
        """Test that LLM errors are handled gracefully with fallback."""
        mock_llm_client = Mock()
        mock_llm_client.is_configured.return_value = True
        mock_llm_client.rewrite_text = AsyncMock(side_effect=Exception("API Error"))

        with patch("backend.services.ai.pipeline.context_analyzer.get_llm_client", return_value=mock_llm_client):
            result = await analyze_additional_context("Some context", "job description")

            # Should fallback to content_statement in summary
            assert result.type == "content_statement"
            assert result.placement == "summary"
            assert result.suggested_text == "Some context"
            assert "API Error" in result.reasoning

    @pytest.mark.asyncio
    async def test_analyze_additional_context_handles_invalid_json(self):
        """Test that invalid JSON responses are handled gracefully with fallback."""
        mock_llm_client = Mock()
        mock_llm_client.is_configured.return_value = True
        mock_llm_client.rewrite_text = AsyncMock(return_value="Invalid JSON response")

        with patch("backend.services.ai.pipeline.context_analyzer.get_llm_client", return_value=mock_llm_client):
            result = await analyze_additional_context("Some context", "job description")

            # Should fallback to content_statement in summary
            assert result.type == "content_statement"
            assert result.placement == "summary"
            assert result.suggested_text == "Some context"
            assert "No JSON found" in result.reasoning

    @pytest.mark.asyncio
    async def test_analyze_additional_context_handles_malformed_json(self):
        """Test that malformed JSON responses are handled gracefully with fallback."""
        mock_llm_client = Mock()
        mock_llm_client.is_configured.return_value = True
        mock_llm_client.rewrite_text = AsyncMock(return_value='{"type": "directive", "placement": "summary"')  # Missing closing brace

        with patch("backend.services.ai.pipeline.context_analyzer.get_llm_client", return_value=mock_llm_client):
            result = await analyze_additional_context("Some context", "job description")

            # Should fallback to content_statement in summary
            assert result.type == "content_statement"
            assert result.placement == "summary"
            assert result.suggested_text == "Some context"


class TestAnalyzeWithLLM:
    """Test the internal _analyze_with_llm function."""

    @pytest.mark.asyncio
    async def test_analyze_with_llm_constructs_correct_prompt(self):
        """Test that the LLM prompt is constructed correctly."""
        mock_llm_client = Mock()
        mock_llm_client.rewrite_text = AsyncMock(return_value=json.dumps({
            "type": "directive",
            "placement": "adaptation_guidance",
            "suggested_text": "Test response",
            "reasoning": "Test reasoning"
        }))

        await _analyze_with_llm(mock_llm_client, "test context", "test job description")

        # Verify the call was made
        assert mock_llm_client.rewrite_text.called
        call_args = mock_llm_client.rewrite_text.call_args

        # Check that the prompt contains expected elements
        prompt = call_args[0][1]  # Second positional argument
        assert "test context" in prompt
        assert "test job description" in prompt
        assert "Analyze this additional context" in prompt
        assert "directive|content_statement|achievement|mixed" in prompt

    @pytest.mark.asyncio
    async def test_analyze_with_llm_parses_json_response_correctly(self):
        """Test that JSON responses are parsed correctly."""
        mock_llm_client = Mock()
        mock_llm_client.rewrite_text = AsyncMock(return_value=json.dumps({
            "type": "achievement",
            "placement": "experience_description",
            "suggested_text": "Led team of 10 developers",
            "reasoning": "Role-specific achievement"
        }))

        result = await _analyze_with_llm(mock_llm_client, "Led a team", "Engineering job")

        assert isinstance(result, ContextAnalysis)
        assert result.type == "achievement"
        assert result.placement == "experience_description"
        assert result.suggested_text == "Led team of 10 developers"
        assert result.reasoning == "Role-specific achievement"
