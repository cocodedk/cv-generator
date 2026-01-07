"""Tests for address normalization functions."""

from backend.services.ai.cover_letter import _normalize_address, _strip_html_breaks


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
