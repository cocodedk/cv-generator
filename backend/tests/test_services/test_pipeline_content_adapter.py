"""Tests for Content Adapter (Step 4)."""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from backend.models import Experience, Project
from backend.services.ai.pipeline.models import JDAnalysis, SelectionResult
from backend.services.ai.pipeline.content_adapter import adapt_content, _adapt_text


class TestContentAdapter:
    @pytest.mark.asyncio
    async def test_adapt_content_preserves_facts(self):
        """Verify that content adapter preserves all facts from profile."""
        selection_result = SelectionResult(
            experiences=[
                Experience(
                    title="Software Engineer",
                    company="Test Corp",
                    start_date="2023-01",
                    projects=[
                        Project(
                            name="API Project",
                            highlights=["Built REST API using Python"],
                            technologies=["Python"],
                        )
                    ],
                )
            ],
            selected_indices={},
        )

        jd_analysis = JDAnalysis(
            required_skills={"python", "api"},
            preferred_skills=set(),
            responsibilities=[],
            domain_keywords=set(),
            seniority_signals=[],
        )

        result = await adapt_content(selection_result, jd_analysis)

        # Should preserve core facts
        assert len(result.experiences) == 1
        assert result.experiences[0].title == "Software Engineer"
        assert result.experiences[0].company == "Test Corp"
        assert len(result.experiences[0].projects) == 1
        assert "Python" in result.experiences[0].projects[0].technologies

    @pytest.mark.asyncio
    async def test_adapt_single_text_item_fallback_on_character_limit_exceeded(self):
        """Test that content adapter falls back to original text when LLM output exceeds character limit."""
        from backend.services.ai.pipeline.content_adapter import _adapt_single_text_item

        # Create a mock LLM client that returns text exceeding the character limit
        mock_llm_client = Mock()
        mock_llm_client.rewrite_text = AsyncMock()

        # Create text that exceeds _MAX_DESCRIPTION_CHARS + 20 (400 + 20 = 420)
        # This should trigger the fallback since 425 > 420
        long_response = "A" * 425  # 425 characters
        mock_llm_client.rewrite_text.return_value = long_response

        original_text = "Original project description that should be preserved when LLM exceeds character limit."
        jd_summary = "Job requires Python and API skills."
        context_section = ""

        # Create task info tuple: (task_type, exp_idx, proj_idx, hl_idx, original_text)
        task_info = ("proj_desc", "0", "0", "", original_text)

        # Call _adapt_single_text_item which handles the error
        with patch('backend.services.ai.pipeline.content_adapter.logger') as mock_logger:
            result = await _adapt_single_text_item(
                mock_llm_client,
                task_info,
                jd_summary,
                context_section,
            )

        # Should return tuple: (task_type, exp_idx, proj_idx, hl_idx, original_text, adapted_text, error)
        task_type, exp_idx, proj_idx, hl_idx, orig_text, adapted_text, error = result

        # Should fall back to original text due to character limit exceeded
        assert adapted_text == original_text
        assert error is not None
        assert "character limit" in error

        # Should have logged the warning
        mock_logger.warning.assert_called_once()
        warning_call = mock_logger.warning.call_args[0][0]
        assert "Failed to adapt" in warning_call

    @pytest.mark.asyncio
    async def test_adapt_text_within_character_limit(self):
        """Test that content adapter works normally when LLM output is within character limits."""
        # Create a mock LLM client that returns text within the character limit
        mock_llm_client = Mock()
        mock_llm_client.rewrite_text = AsyncMock()

        # Create text that is within _MAX_DESCRIPTION_CHARS (400)
        valid_response = "A" * 350  # 350 characters, well under 400
        mock_llm_client.rewrite_text.return_value = valid_response

        original_text = "Original project description."
        jd_summary = "Job requires Python and API skills."
        context_type = "project description"

        # Call _adapt_text directly
        result = await _adapt_text(
            mock_llm_client,
            original_text,
            jd_summary,
            context_type,
            "",  # context_section
        )

        # Should return the adapted text (not fallback to original)
        assert result == valid_response
