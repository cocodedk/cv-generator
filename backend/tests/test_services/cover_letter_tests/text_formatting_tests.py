"""Tests for cover letter text formatting."""

import pytest

from backend.models import ProfileData, PersonalInfo, Address
from backend.services.ai.cover_letter import _format_as_text


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


class TestFormatAsText:
    """Test plain text formatting for cover letters."""

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
