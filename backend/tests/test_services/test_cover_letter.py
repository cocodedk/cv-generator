"""Tests for cover letter generation service."""

import pytest
from unittest.mock import patch, AsyncMock

from backend.models import ProfileData, PersonalInfo, Address
from backend.models_cover_letter import CoverLetterRequest, CoverLetterResponse
from backend.services.ai.cover_letter import (
    generate_cover_letter,
    _format_profile_summary,
    _format_as_html,
    _format_as_text,
    _extract_highlights_used,
    _normalize_address,
    _strip_html_breaks,
)


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


class TestFormatProfileSummary:
    """Test profile summary formatting."""

    def test_format_profile_summary_basic(self, sample_profile):
        """Test basic profile summary formatting."""
        summary = _format_profile_summary(sample_profile)
        assert "Jane Smith" in summary
        assert "Senior Software Engineer" in summary

    def test_format_profile_summary_with_experience(self, sample_profile):
        """Test profile summary with experience."""
        from backend.models import Experience, Project

        sample_profile.experience = [
            Experience(
                title="Software Engineer",
                company="Previous Corp",
                start_date="2020-01",
                end_date="2022-12",
                projects=[
                    Project(
                        name="Project A",
                        highlights=["Built API", "Improved performance"],
                    )
                ],
            )
        ]

        summary = _format_profile_summary(sample_profile)
        assert "Software Engineer" in summary
        assert "Previous Corp" in summary
        assert "Project A" in summary
        assert "Built API" in summary

    def test_format_profile_summary_with_skills(self, sample_profile):
        """Test profile summary with skills."""
        from backend.models import Skill

        sample_profile.skills = [
            Skill(name="Python", category="Programming"),
            Skill(name="React", category="Frontend"),
        ]

        summary = _format_profile_summary(sample_profile)
        assert "Python" in summary
        assert "React" in summary


class TestFormatAsHTML:
    """Test HTML formatting."""

    def test_format_as_html_basic(self, sample_profile):
        """Test basic HTML formatting."""
        html = _format_as_html(
            profile=sample_profile,
            cover_letter_body="Dear Hiring Manager,\n\nThis is a test letter.",
            company_name="Tech Corp",
            hiring_manager_name="John Doe",
            company_address="123 Tech St",
        )

        assert "Jane Smith" in html
        assert "Tech Corp" in html
        assert "John Doe" in html
        assert "Dear Hiring Manager" in html
        assert "<!DOCTYPE html>" in html

    def test_format_as_html_without_hiring_manager(self, sample_profile):
        """Test HTML formatting without hiring manager name."""
        html = _format_as_html(
            profile=sample_profile,
            cover_letter_body="Dear Hiring Manager,\n\nTest.",
            company_name="Tech Corp",
            hiring_manager_name=None,
            company_address=None,
        )

        assert "Tech Corp" in html
        assert "Jane Smith" in html

    def test_format_as_html_normalizes_address_breaks(self, sample_profile):
        """Test that HTML breaks in address are normalized."""
        # Address with HTML breaks
        address_with_breaks = (
            "Dirch Passers Alle 36, Postboks 250<br><br>2000 Frederiksberg København"
        )
        html = _format_as_html(
            profile=sample_profile,
            cover_letter_body="Test letter.",
            company_name="Tech Corp",
            hiring_manager_name=None,
            company_address=address_with_breaks,
        )

        # Should have normalized breaks (single <br> instead of <br><br>)
        assert "Dirch Passers Alle 36" in html
        assert "Postboks 250" in html
        assert "2000 Frederiksberg" in html
        # Should not have double breaks
        assert (
            "<br><br>" not in html or html.count("<br>") <= 2
        )  # At most 2 breaks for 2 lines


class TestFormatAsText:
    """Test plain text formatting."""

    def test_format_as_text_basic(self, sample_profile):
        """Test basic text formatting."""
        text = _format_as_text(
            profile=sample_profile,
            cover_letter_body="Dear Hiring Manager,\n\nThis is a test letter.",
            company_name="Tech Corp",
            hiring_manager_name="John Doe",
            company_address="123 Tech St",
        )

        assert "Jane Smith" in text
        assert "Tech Corp" in text
        assert "John Doe" in text
        assert "Dear Hiring Manager" in text


class TestNormalizeAddress:
    """Test address normalization functions."""

    def test_normalize_address_strips_html_breaks(self):
        """Test that HTML breaks are normalized to single breaks."""
        address = (
            "Dirch Passers Alle 36, Postboks 250<br><br>2000 Frederiksberg København"
        )
        normalized = _normalize_address(address)
        # Should have single breaks, not double
        assert "<br><br>" not in normalized
        assert "<br>" in normalized
        assert "Dirch Passers Alle 36" in normalized
        assert "Postboks 250" in normalized

    def test_normalize_address_handles_newlines(self):
        """Test that newlines are converted to breaks."""
        address = "Line 1\nLine 2\nLine 3"
        normalized = _normalize_address(address)
        assert "<br>" in normalized
        assert "\n" not in normalized

    def test_normalize_address_handles_mixed_breaks(self):
        """Test that mixed HTML breaks and newlines are normalized."""
        address = "Line 1<br>Line 2\nLine 3<br><br>Line 4"
        normalized = _normalize_address(address)
        assert "<br><br>" not in normalized
        assert "\n" not in normalized
        assert normalized.count("<br>") <= 3  # At most 3 breaks for 4 lines

    def test_normalize_address_empty(self):
        """Test that empty address returns empty string."""
        assert _normalize_address("") == ""
        assert _normalize_address(None) == ""

    def test_strip_html_breaks(self):
        """Test stripping HTML breaks for plain text."""
        text = "Line 1<br>Line 2<br><br>Line 3"
        stripped = _strip_html_breaks(text)
        assert "<br>" not in stripped
        assert "\n" in stripped
        assert "Line 1" in stripped
        assert "Line 2" in stripped
        assert "Line 3" in stripped


class TestExtractHighlightsUsed:
    """Test highlights extraction."""

    def test_extract_highlights_used(self, sample_profile):
        """Test extracting highlights that match job description."""
        from backend.models import Experience, Project

        sample_profile.experience = [
            Experience(
                title="Engineer",
                company="Corp",
                start_date="2020-01",
                end_date="2022-12",
                projects=[
                    Project(
                        name="Project",
                        highlights=["Built Python API", "Improved React performance"],
                    )
                ],
            )
        ]

        jd = "We need someone with Python and React experience."
        highlights = _extract_highlights_used(sample_profile, jd)

        assert len(highlights) > 0
        assert any("Python" in h or "React" in h for h in highlights)


class TestGenerateCoverLetter:
    """Test cover letter generation."""

    @pytest.mark.asyncio
    async def test_generate_cover_letter_success(self, sample_profile, sample_request):
        """Test successful cover letter generation."""
        from unittest.mock import Mock
        from backend.services.ai.cover_letter_selection import SelectedContent

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
        from unittest.mock import Mock

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
        from unittest.mock import Mock
        from backend.services.ai.cover_letter_selection import SelectedContent

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
        from unittest.mock import Mock
        from backend.services.ai.cover_letter_selection import SelectedContent

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
