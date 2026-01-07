"""Tests for additional context functionality."""

import pytest
from unittest.mock import patch, AsyncMock, Mock

from backend.models import ProfileData
from backend.models_ai import AIGenerateCVRequest
from backend.services.ai.draft import generate_cv_draft


@pytest.mark.unit
class TestAdditionalContext:
    @pytest.mark.asyncio
    async def test_additional_context_passed_to_llm_tailor(self, sample_cv_data):
        """Test that additional_context is passed through to llm_tailor_cv."""
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
            additional_context="Rated among top 2% of AI coders in 2025",
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
            await generate_cv_draft(profile, request)
            # Verify LLM was called (through pipeline)
            assert mock_llm_client.rewrite_text.called
            # Verify additional_context was included in the prompt
            call_args = mock_llm_client.rewrite_text.call_args_list
            assert len(call_args) > 0
            # Check that additional_context appears in at least one prompt
            all_prompts = " ".join([call[0][1] for call in call_args if len(call[0]) > 1])
            assert (
                "top 2% of AI coders" in all_prompts
                or "Additional achievements" in all_prompts
                or "Additional Context" in all_prompts
            )

    @pytest.mark.asyncio
    async def test_additional_context_in_summary(self, sample_cv_data):
        """Test that additional_context appears in the summary output."""
        profile_dict = {
            "personal_info": sample_cv_data["personal_info"],
            "experience": sample_cv_data["experience"],
            "education": sample_cv_data["education"],
            "skills": sample_cv_data["skills"],
        }
        profile = ProfileData.model_validate(profile_dict)
        request = AIGenerateCVRequest(
            job_description="We require FastAPI and React. You will build and improve web features.",
            additional_context="Rated among top 2% of AI coders in 2025",
        )

        result = await generate_cv_draft(profile, request)
        # Check that additional_context appears in summary
        summary_text = " ".join(result.summary)
        assert "top 2%" in summary_text or "Additional context provided" in summary_text

    @pytest.mark.asyncio
    async def test_additional_context_as_directive_for_llm_tailor(self, sample_cv_data):
        """Test that additional_context is used as directive for all pipeline steps with llm_tailor style."""
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
            "skills": [{"name": "FastAPI"}, {"name": "Python"}],
        }
        profile = ProfileData.model_validate(profile_dict)
        request = AIGenerateCVRequest(
            job_description="Must have FastAPI. Build APIs.",
            max_experiences=1,
            style="llm_tailor",
            additional_context="Make this more enterprise-focused",
        )

        mock_llm_client = Mock()
        mock_llm_client.is_configured.return_value = True
        mock_llm_client.rewrite_text = AsyncMock(
            side_effect=[
                '{"required_skills":["FastAPI"],"preferred_skills":[],"responsibilities":["Build APIs"],"domain_keywords":[],"seniority_signals":[]}',  # JD analysis
                '{"relevant":true,"type":"direct","why":"Match","match":"FastAPI"}',  # Skill evaluation
                '{"relevant":true,"type":"direct","why":"Match","match":"Python"}',  # Skill evaluation
                "Built enterprise APIs",  # Content adaptation
            ]
        )

        # Mock pipeline LLM calls
        with patch(
            "backend.services.ai.pipeline.jd_analyzer.get_llm_client",
            return_value=mock_llm_client,
        ), patch(
            "backend.services.ai.pipeline.content_adapter.get_llm_client",
            return_value=mock_llm_client,
        ), patch(
            "backend.services.ai.pipeline.skill_relevance_evaluator.get_llm_client",
            return_value=mock_llm_client,
        ):
            await generate_cv_draft(profile, request)
            # Verify LLM was called multiple times (JD analysis, skill evaluation, content adaptation)
            assert mock_llm_client.rewrite_text.called
            call_args = mock_llm_client.rewrite_text.call_args_list

            # Check that directive appears in prompts
            all_prompts = " ".join([call[0][1] for call in call_args if len(call[0]) > 1])
            assert "DIRECTIVE" in all_prompts or "enterprise-focused" in all_prompts

    @pytest.mark.asyncio
    async def test_additional_context_not_directive_for_other_styles(self, sample_cv_data):
        """Test that additional_context is NOT used as directive for non-llm_tailor styles."""
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
            style="select_and_reorder",
            additional_context="Make this more enterprise-focused",
        )

        mock_llm_client = Mock()
        mock_llm_client.is_configured.return_value = True
        mock_llm_client.rewrite_text = AsyncMock(
            return_value='{"required_skills":["FastAPI"],"preferred_skills":[],"responsibilities":["Build APIs"],"domain_keywords":[],"seniority_signals":[]}'
        )

        # Mock JD analyzer LLM call
        with patch(
            "backend.services.ai.pipeline.jd_analyzer.get_llm_client",
            return_value=mock_llm_client,
        ):
            await generate_cv_draft(profile, request)
            # Verify LLM was called for JD analysis
            assert mock_llm_client.rewrite_text.called
            call_args = mock_llm_client.rewrite_text.call_args_list

            # For select_and_reorder style, directive should NOT appear in JD analysis prompt
            # (additional_context should only be passed to content adaptation, not as directive)
            if call_args:
                jd_prompt = call_args[0][0][1] if len(call_args[0][0]) > 1 else ""
                # Directive should not appear in JD analysis for non-llm_tailor styles
                assert "DIRECTIVE" not in jd_prompt or "enterprise-focused" not in jd_prompt
