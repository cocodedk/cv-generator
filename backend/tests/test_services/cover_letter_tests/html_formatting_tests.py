"""Tests for cover letter HTML formatting."""

import pytest

from backend.models import ProfileData, PersonalInfo, Address
from backend.services.ai.cover_letter import _format_as_html


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


class TestFormatAsHTML:
    """Test HTML formatting for cover letters."""

    def test_format_as_html_basic(self, sample_profile):
        """Test basic HTML formatting."""
        html = _format_as_html(
            profile=sample_profile,
            cover_letter_body="Dear Hiring Manager,\n\nThis is a test letter.",
            company_name="Tech Corp",
            hiring_manager_name="John Doe",
            company_address="123 Tech Street\nSan Francisco, CA 94102",
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
