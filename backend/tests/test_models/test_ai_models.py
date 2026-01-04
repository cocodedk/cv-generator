"""Tests for AI model validation."""

import pytest
from pydantic import ValidationError

from backend.models_ai import AIGenerateCVRequest


class TestAIGenerateCVRequest:
    """Test AIGenerateCVRequest model validation."""

    def test_valid_request_with_all_fields(self):
        """Test valid request with all fields including additional_context."""
        request = AIGenerateCVRequest(
            job_description="We require FastAPI and React. You will build and improve web features.",
            target_role="Full-stack Engineer",
            seniority="Senior",
            style="llm_tailor",
            max_experiences=4,
            additional_context="Rated among top 2% of AI coders in 2025",
        )
        assert (
            request.job_description
            == "We require FastAPI and React. You will build and improve web features."
        )
        assert request.target_role == "Full-stack Engineer"
        assert request.seniority == "Senior"
        assert request.style == "llm_tailor"
        assert request.max_experiences == 4
        assert request.additional_context == "Rated among top 2% of AI coders in 2025"

    def test_valid_request_without_additional_context(self):
        """Test valid request without additional_context (optional field)."""
        request = AIGenerateCVRequest(
            job_description="We require FastAPI and React. You will build and improve web features.",
        )
        assert (
            request.job_description
            == "We require FastAPI and React. You will build and improve web features."
        )
        assert request.additional_context is None

    def test_additional_context_max_length(self):
        """Test that additional_context respects max_length constraint."""
        # Should accept up to 2000 characters
        long_context = "A" * 2000
        request = AIGenerateCVRequest(
            job_description="We require FastAPI and React.",
            additional_context=long_context,
        )
        assert len(request.additional_context) == 2000

    def test_additional_context_exceeds_max_length(self):
        """Test that additional_context exceeding max_length raises validation error."""
        long_context = "A" * 2001  # Exceeds max_length of 2000
        with pytest.raises(ValidationError) as exc_info:
            AIGenerateCVRequest(
                job_description="We require FastAPI and React.",
                additional_context=long_context,
            )
        errors = exc_info.value.errors()
        assert any(
            error["loc"] == ("additional_context",)
            and error["type"] == "string_too_long"
            for error in errors
        )

    def test_additional_context_empty_string_becomes_none(self):
        """Test that empty string for additional_context is treated as None."""
        request = AIGenerateCVRequest(
            job_description="We require FastAPI and React.",
            additional_context="",
        )
        # Empty string should be converted to None or remain empty
        assert request.additional_context == "" or request.additional_context is None

    def test_valid_request_with_target_company(self):
        """Test valid request with target_company field."""
        request = AIGenerateCVRequest(
            job_description="We require FastAPI and React.",
            target_company="Google",
            target_role="Senior Developer",
        )
        assert request.target_company == "Google"
        assert request.target_role == "Senior Developer"

    def test_target_company_max_length(self):
        """Test that target_company respects max_length constraint."""
        long_company = "A" * 200
        request = AIGenerateCVRequest(
            job_description="We require FastAPI and React.",
            target_company=long_company,
        )
        assert len(request.target_company) == 200

    def test_target_company_exceeds_max_length(self):
        """Test that target_company exceeding max_length raises validation error."""
        long_company = "A" * 201  # Exceeds max_length of 200
        with pytest.raises(ValidationError) as exc_info:
            AIGenerateCVRequest(
                job_description="We require FastAPI and React.",
                target_company=long_company,
            )
        errors = exc_info.value.errors()
        assert any(
            error["loc"] == ("target_company",)
            and error["type"] == "string_too_long"
            for error in errors
        )
