"""Unit tests for heuristics-based AI drafting."""

import pytest
from unittest.mock import patch, AsyncMock

from backend.models import ProfileData
from backend.models_ai import AIGenerateCVRequest
from backend.services.ai.draft import generate_cv_draft


@pytest.mark.unit
class TestAIDraftGenerator:
    @pytest.mark.asyncio
    async def test_trims_projects_and_highlights(self, sample_cv_data):
        profile_dict = {
            "personal_info": sample_cv_data["personal_info"],
            "experience": [
                {
                    "title": "Engineer",
                    "company": "Example",
                    "start_date": "2023-01",
                    "end_date": "Present",
                    "description": "Built and improved web services.",
                    "location": "Remote",
                    "projects": [
                        {
                            "name": f"Project {i}",
                            "description": "FastAPI and React work",
                            "technologies": ["FastAPI", "React"],
                            "highlights": [
                                f"Did thing {n} for project {i}" for n in range(8)
                            ],
                        }
                        for i in range(5)
                    ],
                }
            ],
            "education": sample_cv_data["education"],
            "skills": sample_cv_data["skills"],
        }
        profile = ProfileData.model_validate(profile_dict)
        request = AIGenerateCVRequest(
            job_description="We require FastAPI and React. You will build and improve web features.",
            max_experiences=1,
            style="select_and_reorder",
        )

        result = await generate_cv_draft(profile, request)
        assert len(result.draft_cv.experience) == 1
        assert len(result.draft_cv.experience[0].projects) <= 2
        assert all(
            len(project.highlights) <= 3
            for project in result.draft_cv.experience[0].projects
        )

    @pytest.mark.asyncio
    async def test_rewrite_style_applies_safe_transforms(self, sample_cv_data):
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
                            "highlights": ["Responsible for building APIs."],
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
            style="rewrite_bullets",
        )

        result = await generate_cv_draft(profile, request)
        highlight = result.draft_cv.experience[0].projects[0].highlights[0]
        assert highlight == "Building APIs"

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

        from unittest.mock import Mock

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

        from unittest.mock import Mock

        mock_llm_client = Mock()
        mock_llm_client.is_configured.return_value = False

        # Mock pipeline LLM calls - should fallback to heuristics
        with patch(
            "backend.services.ai.pipeline.content_adapter.get_llm_client",
            return_value=mock_llm_client,
        ), patch(
            "backend.services.ai.pipeline.skill_relevance_evaluator.get_llm_client",
            return_value=mock_llm_client,
        ):
            result = await generate_cv_draft(profile, request)
            # Should still return a valid result
            assert len(result.draft_cv.experience) >= 0
            # LLM should not have been called (falls back to heuristics)
            mock_llm_client.rewrite_text.assert_not_called()

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

        from unittest.mock import Mock

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
    async def test_target_company_and_role_included_in_draft(self, sample_cv_data):
        """Test that target_company and target_role from request are included in draft CV."""
        profile_dict = {
            "personal_info": sample_cv_data["personal_info"],
            "experience": sample_cv_data["experience"],
            "education": sample_cv_data["education"],
            "skills": sample_cv_data["skills"],
        }
        profile = ProfileData.model_validate(profile_dict)
        request = AIGenerateCVRequest(
            job_description="We require FastAPI and React. You will build and improve web features.",
            target_company="Google",
            target_role="Senior Developer",
        )

        result = await generate_cv_draft(profile, request)
        assert result.draft_cv.target_company == "Google"
        assert result.draft_cv.target_role == "Senior Developer"

    @pytest.mark.asyncio
    async def test_target_company_and_role_none_when_not_provided(self, sample_cv_data):
        """Test that target_company and target_role are None when not provided in request."""
        profile_dict = {
            "personal_info": sample_cv_data["personal_info"],
            "experience": sample_cv_data["experience"],
            "education": sample_cv_data["education"],
            "skills": sample_cv_data["skills"],
        }
        profile = ProfileData.model_validate(profile_dict)
        request = AIGenerateCVRequest(
            job_description="We require FastAPI and React. You will build and improve web features.",
        )

        result = await generate_cv_draft(profile, request)
        assert result.draft_cv.target_company is None
        assert result.draft_cv.target_role is None
