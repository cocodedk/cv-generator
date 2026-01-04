"""Tests for cover letter models."""

import pytest
from pydantic import ValidationError

from backend.models_cover_letter import CoverLetterRequest, CoverLetterResponse


class TestCoverLetterRequest:
    """Test CoverLetterRequest model."""

    def test_valid_request(self):
        """Test valid cover letter request."""
        request = CoverLetterRequest(
            job_description="We are looking for a Senior Developer with Python experience.",
            company_name="Tech Corp",
            hiring_manager_name="John Doe",
            company_address="123 Tech Street\nSan Francisco, CA 94102",
            tone="professional",
        )
        assert request.job_description == "We are looking for a Senior Developer with Python experience."
        assert request.company_name == "Tech Corp"
        assert request.hiring_manager_name == "John Doe"
        assert request.tone == "professional"

    def test_request_with_minimal_fields(self):
        """Test request with only required fields."""
        request = CoverLetterRequest(
            job_description="We need a developer with Python experience.",
            company_name="Tech Corp",
        )
        assert request.job_description == "We need a developer with Python experience."
        assert request.company_name == "Tech Corp"
        assert request.hiring_manager_name is None
        assert request.company_address is None
        assert request.tone == "professional"  # Default value

    def test_request_job_description_too_short(self):
        """Test request with job description too short."""
        with pytest.raises(ValidationError) as exc_info:
            CoverLetterRequest(
                job_description="Short",  # Less than 20 chars
                company_name="Tech Corp",
            )
        errors = exc_info.value.errors()
        assert any("job_description" in str(err.get("loc", [])) for err in errors)

    def test_request_job_description_too_long(self):
        """Test request with job description too long."""
        long_jd = "A" * 20001  # Exceeds 20000 char limit
        with pytest.raises(ValidationError) as exc_info:
            CoverLetterRequest(
                job_description=long_jd,
                company_name="Tech Corp",
            )
        errors = exc_info.value.errors()
        assert any("job_description" in str(err.get("loc", [])) for err in errors)

    def test_request_invalid_tone(self):
        """Test request with invalid tone."""
        with pytest.raises(ValidationError) as exc_info:
            CoverLetterRequest(
                job_description="We need a developer.",
                company_name="Tech Corp",
                tone="invalid_tone",
            )
        errors = exc_info.value.errors()
        assert any("tone" in str(err.get("loc", [])) for err in errors)

    def test_request_valid_tones(self):
        """Test request with all valid tones."""
        tones = ["professional", "enthusiastic", "conversational"]
        for tone in tones:
            request = CoverLetterRequest(
                job_description="We need a developer.",
                company_name="Tech Corp",
                tone=tone,
            )
            assert request.tone == tone


class TestCoverLetterResponse:
    """Test CoverLetterResponse model."""

    def test_valid_response(self):
        """Test valid cover letter response."""
        response = CoverLetterResponse(
            cover_letter_html="<html><body>Cover letter HTML</body></html>",
            cover_letter_text="Cover letter plain text",
            highlights_used=["Highlight 1", "Highlight 2"],
        )
        assert response.cover_letter_html == "<html><body>Cover letter HTML</body></html>"
        assert response.cover_letter_text == "Cover letter plain text"
        assert len(response.highlights_used) == 2

    def test_response_with_empty_highlights(self):
        """Test response with empty highlights list."""
        response = CoverLetterResponse(
            cover_letter_html="<html><body>Cover letter</body></html>",
            cover_letter_text="Cover letter text",
            highlights_used=[],
        )
        assert response.highlights_used == []

    def test_response_default_highlights(self):
        """Test response with default highlights (empty list)."""
        response = CoverLetterResponse(
            cover_letter_html="<html><body>Cover letter</body></html>",
            cover_letter_text="Cover letter text",
        )
        assert response.highlights_used == []
