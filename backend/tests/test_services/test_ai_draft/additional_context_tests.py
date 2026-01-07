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
        mock_llm_client.generate_text = AsyncMock(
            side_effect=[
                '{"type":"directive","placement":"adaptation_guidance","suggested_text":"Make this more enterprise-focused","reasoning":"This is a directive for how to adapt content"}',  # Context analysis
                '{"required_skills":["FastAPI"],"preferred_skills":[],"responsibilities":["Build APIs"],"domain_keywords":[],"seniority_signals":[]}',  # JD analysis
            ]
        )

        # Mock context analyzer and JD analyzer LLM calls
        with patch(
            "backend.services.ai.pipeline.context_analyzer.get_llm_client",
            return_value=mock_llm_client,
        ), patch(
            "backend.services.ai.pipeline.jd_analyzer.get_llm_client",
            return_value=mock_llm_client,
        ):
            await generate_cv_draft(profile, request)
            # Verify LLM was called for JD analysis (second call in side_effect)
            assert mock_llm_client.generate_text.call_count >= 2
            call_args_list = mock_llm_client.generate_text.call_args_list

            # Find the JD analysis call (contains "Analyze this job description")
            jd_call_args = None
            for call_args in call_args_list:
                prompt = call_args[0][0]  # generate_text(prompt, system_prompt)
                if "Analyze this job description" in prompt:
                    jd_call_args = call_args
                    break

            assert jd_call_args is not None, "JD analysis call not found"
            jd_prompt = jd_call_args[0][0]
            # Directive should appear in JD analysis when context analysis determines it's directive-type
            assert "DIRECTIVE:" in jd_prompt and "Make this more enterprise-focused" in jd_prompt
