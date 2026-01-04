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
        mock_llm_client.rewrite_text = AsyncMock(return_value="LLM-tailored text")

        with patch(
            "backend.services.ai.llm_tailor.get_llm_client",
            return_value=mock_llm_client,
        ):
            result = await generate_cv_draft(profile, request)
            # Verify LLM was called for tailoring
            assert mock_llm_client.rewrite_text.called
            # Verify we got a valid result
            assert len(result.draft_cv.experience) == 1

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

        with patch(
            "backend.services.ai.llm_tailor.get_llm_client",
            return_value=mock_llm_client,
        ):
            result = await generate_cv_draft(profile, request)
            # Should still return a valid result
            assert len(result.draft_cv.experience) == 1
            # LLM should not have been called
            mock_llm_client.rewrite_text.assert_not_called()
            # Original content should be preserved
            assert (
                result.draft_cv.experience[0].projects[0].highlights[0] == "Built APIs"
            )

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
        mock_llm_client.rewrite_text = AsyncMock(return_value="Tailored text")

        with patch(
            "backend.services.ai.llm_tailor.get_llm_client",
            return_value=mock_llm_client,
        ):
            await generate_cv_draft(profile, request)
            # Verify LLM was called
            assert mock_llm_client.rewrite_text.called
            # Verify additional_context was included in the prompt
            call_args = mock_llm_client.rewrite_text.call_args_list
            assert len(call_args) > 0
            # Check that additional_context appears in the prompt
            prompt_text = call_args[0][0][1]  # Second argument is the prompt
            assert (
                "top 2% of AI coders" in prompt_text
                or "Additional achievements" in prompt_text
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
