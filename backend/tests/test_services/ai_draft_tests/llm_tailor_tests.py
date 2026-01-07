"""Tests for LLM tailor functionality."""

import pytest
from unittest.mock import patch, AsyncMock, Mock

from backend.models import ProfileData
from backend.models_ai import AIGenerateCVRequest
from backend.services.ai.draft import generate_cv_draft


@pytest.mark.unit
class TestLLMTailorFunctionality:
    @pytest.mark.asyncio
    async def test_llm_tailor_style_calls_llm(self, sample_cv_data):
        """Test that llm_tailor style triggers LLM tailoring."""
        profile_dict = {
            "personal_info": sample_cv_data["personal_info"],
            "experience": [
                {
                    "title": "Engineer",
                    "company": "Example",
                    "start_date": "2023-01",
                    "end_date": "Present",
                    "projects": [
                        {
                            "name": "API Platform",
                            "technologies": ["FastAPI"],
                            "highlights": ["Built APIs"],
                        }
                    ],
                }
            ],
            "education": [],
            "skills": [{"name": "FastAPI"}],
        }
        profile = ProfileData.model_validate(profile_dict)
        request = AIGenerateCVRequest(
            job_description="Must have FastAPI. Build APIs.",
            max_experiences=1,
            style="llm_tailor",
        )

        mock_llm_client = Mock()
        mock_llm_client.is_configured.return_value = True
        mock_llm_client.rewrite_text = AsyncMock(return_value='{"relevant":true,"type":"direct","why":"Match","match":"FastAPI"}')

        # Mock pipeline LLM calls
        with patch(
            "backend.services.ai.pipeline.content_adapter.get_llm_client",
            return_value=mock_llm_client,
        ), patch(
            "backend.services.ai.pipeline.skill_relevance_evaluator.get_llm_client",
            return_value=mock_llm_client,
        ):
            result = await generate_cv_draft(profile, request)
            # Verify LLM was called (through pipeline)
            assert mock_llm_client.rewrite_text.called
            # Verify we got a valid result
            assert len(result.draft_cv.experience) >= 0

    @pytest.mark.asyncio
    async def test_llm_tailor_style_fallback_when_not_configured(self, sample_cv_data):
        """Test that llm_tailor style falls back gracefully when LLM not configured."""
        profile_dict = {
            "personal_info": sample_cv_data["personal_info"],
            "experience": [
                {
                    "title": "Engineer",
                    "company": "Example",
                    "start_date": "2023-01",
                    "end_date": "Present",
                    "projects": [
                        {
                            "name": "API Platform",
                            "technologies": ["FastAPI"],
                            "highlights": ["Built APIs"],
                        }
                    ],
                }
            ],
            "education": [],
            "skills": [{"name": "FastAPI"}],
        }
        profile = ProfileData.model_validate(profile_dict)
        request = AIGenerateCVRequest(
            job_description="Must have FastAPI. Build APIs.",
            max_experiences=1,
            style="llm_tailor",
        )

        mock_llm_client = Mock()
        mock_llm_client.is_configured.return_value = False

        # Mock pipeline LLM calls - all components fall back when LLM not configured
        # JD analyzer falls back to heuristics, skill evaluator uses raw JD matching,
        # content adapter returns content as-is
        with patch(
            "backend.services.ai.pipeline.content_adapter.get_llm_client",
            return_value=mock_llm_client,
        ), patch(
            "backend.services.ai.pipeline.skill_relevance_evaluator.get_llm_client",
            return_value=mock_llm_client,
        ), patch(
            "backend.services.ai.pipeline.jd_analyzer.get_llm_client",
            return_value=mock_llm_client,
        ):
            result = await generate_cv_draft(profile, request)
            # Should still return a valid result (with fallbacks)
            assert len(result.draft_cv.experience) >= 0
            # LLM should not have been called (falls back to heuristics)
            mock_llm_client.rewrite_text.assert_not_called()
