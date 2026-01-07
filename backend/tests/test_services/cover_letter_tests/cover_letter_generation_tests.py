"""Tests for cover letter generation functionality."""

import pytest
from unittest.mock import patch, AsyncMock, Mock

from backend.models import ProfileData, PersonalInfo, Address
from backend.models_cover_letter import CoverLetterRequest, CoverLetterResponse
from backend.services.ai.cover_letter import generate_cover_letter
from backend.services.ai.cover_letter_selection import SelectedContent


@pytest.fixture
def sample_profile():
    """Sample profile data for testing."""
    return ProfileData(
        personal_info=PersonalInfo(
            name="Jane Smith",
            title="Senior Software Engineer",
            email="jane@example.com",
            phone="+1234567890",
            address=Address(
                street="456 Oak Ave",
                city="San Francisco",
                state="CA",
                zip="94102",
                country="USA",
            ),
        ),
        experience=[],
        education=[],
        skills=[],
    )


@pytest.fixture
def sample_request():
    """Sample cover letter request."""
    return CoverLetterRequest(
        job_description="We are looking for a Senior Software Engineer with Python experience.",
        company_name="Tech Corp",
        hiring_manager_name="John Doe",
        company_address="123 Tech Street\nSan Francisco, CA 94102",
        tone="professional",
    )


@pytest.fixture
def sample_request_with_llm_instructions():
    """Sample cover letter request with LLM instructions."""
    return CoverLetterRequest(
        job_description="We are looking for a Senior Software Engineer with Python experience.",
        company_name="Tech Corp",
        hiring_manager_name="John Doe",
        company_address="123 Tech Street\nSan Francisco, CA 94102",
        tone="professional",
        llm_instructions="Write in Spanish and keep it under 200 words",
    )


class TestGenerateCoverLetter:
    """Test cover letter generation."""

    @pytest.mark.asyncio
    async def test_generate_cover_letter_success(self, sample_profile, sample_request):
        """Test successful cover letter generation."""
        mock_llm_client = Mock()
        mock_llm_client.is_configured.return_value = True
        mock_llm_client.model = "gpt-3.5-turbo"
        mock_llm_client.api_key = "test-key"
        mock_llm_client.base_url = "https://api.test.com"
        mock_llm_client.timeout = 30
        mock_llm_client.rewrite_text = AsyncMock(
            return_value="Dear John Doe,\n\nI am writing to express my interest..."
        )

        # Mock selection response
        selected_content = SelectedContent(
            experience_indices=[],
            skill_names=[],
            key_highlights=[],
            relevance_reasoning="Test reasoning",
        )

        with patch(
            "backend.services.ai.cover_letter.get_llm_client",
            return_value=mock_llm_client,
        ):
            with patch(
                "backend.services.ai.cover_letter.select_relevant_content",
                return_value=selected_content,
            ):
                response = await generate_cover_letter(sample_profile, sample_request)

                assert isinstance(response, CoverLetterResponse)
                assert response.cover_letter_html
                assert response.cover_letter_text
                assert "Jane Smith" in response.cover_letter_html
                assert "Tech Corp" in response.cover_letter_html
                assert isinstance(response.selected_experiences, list)
                assert isinstance(response.selected_skills, list)
                mock_llm_client.rewrite_text.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_cover_letter_llm_not_configured(
        self, sample_profile, sample_request
    ):
        """Test cover letter generation when LLM is not configured."""
        mock_llm_client = Mock()
        mock_llm_client.is_configured.return_value = False

        with patch(
            "backend.services.ai.cover_letter.get_llm_client",
            return_value=mock_llm_client,
        ):
            with pytest.raises(ValueError, match="LLM is not configured"):
                await generate_cover_letter(sample_profile, sample_request)

    @pytest.mark.asyncio
    async def test_generate_cover_letter_llm_error(
        self, sample_profile, sample_request
    ):
        """Test cover letter generation when LLM raises error."""
        mock_llm_client = Mock()
        mock_llm_client.is_configured.return_value = True
        mock_llm_client.model = "gpt-3.5-turbo"
        mock_llm_client.api_key = "test-key"
        mock_llm_client.base_url = "https://api.test.com"
        mock_llm_client.timeout = 30
        mock_llm_client.rewrite_text = AsyncMock(side_effect=Exception("API Error"))

        selected_content = SelectedContent(
            experience_indices=[],
            skill_names=[],
            key_highlights=[],
            relevance_reasoning="Test",
        )

        with patch(
            "backend.services.ai.cover_letter.get_llm_client",
            return_value=mock_llm_client,
        ):
            with patch(
                "backend.services.ai.cover_letter.select_relevant_content",
                return_value=selected_content,
            ):
                with pytest.raises(ValueError, match="Failed to generate cover letter"):
                    await generate_cover_letter(sample_profile, sample_request)

    @pytest.mark.asyncio
    async def test_generate_cover_letter_different_tones(
        self, sample_profile, sample_request
    ):
        """Test cover letter generation with different tones."""
        mock_llm_client = Mock()
        mock_llm_client.is_configured.return_value = True
        mock_llm_client.model = "gpt-3.5-turbo"
        mock_llm_client.api_key = "test-key"
        mock_llm_client.base_url = "https://api.test.com"
        mock_llm_client.timeout = 30
        mock_llm_client.rewrite_text = AsyncMock(
            return_value="Dear Hiring Manager,\n\nTest letter."
        )

        selected_content = SelectedContent(
            experience_indices=[],
            skill_names=[],
            key_highlights=[],
            relevance_reasoning="Test",
        )

        tones = ["professional", "enthusiastic", "conversational"]
        for tone in tones:
            sample_request.tone = tone
            with patch(
                "backend.services.ai.cover_letter.get_llm_client",
                return_value=mock_llm_client,
            ):
                with patch(
                    "backend.services.ai.cover_letter.select_relevant_content",
                    return_value=selected_content,
                ):
                    response = await generate_cover_letter(
                        sample_profile, sample_request
                    )
                    assert response.cover_letter_html
                    # Verify prompt includes tone instruction
                    call_args = mock_llm_client.rewrite_text.call_args
                    assert (
                        tone in call_args[0][1].lower()
                        or "tone" in call_args[0][1].lower()
                    )

    @pytest.mark.asyncio
    async def test_generate_cover_letter_with_llm_instructions(
        self, sample_profile, sample_request_with_llm_instructions
    ):
        """Test cover letter generation with LLM instructions."""
        mock_llm_client = Mock()
        mock_llm_client.is_configured.return_value = True
        mock_llm_client.model = "gpt-3.5-turbo"
        mock_llm_client.api_key = "test-key"
        mock_llm_client.base_url = "https://api.test.com"
        mock_llm_client.timeout = 30
        mock_llm_client.rewrite_text = AsyncMock(
            return_value="Estimado John Doe,\n\nMe complace expresar mi interés..."
        )

        selected_content = SelectedContent(
            experience_indices=[],
            skill_names=[],
            key_highlights=[],
            relevance_reasoning="Test reasoning",
        )

        with patch(
            "backend.services.ai.cover_letter.get_llm_client",
            return_value=mock_llm_client,
        ):
            with patch(
                "backend.services.ai.cover_letter.select_relevant_content",
                return_value=selected_content,
            ):
                await generate_cover_letter(sample_profile, sample_request_with_llm_instructions)

                # Verify LLM instructions are included in the prompt
                call_args = mock_llm_client.rewrite_text.call_args
                prompt = call_args[0][1]
                assert "ADDITIONAL INSTRUCTIONS:" in prompt
                assert "Write in Spanish and keep it under 200 words" in prompt
