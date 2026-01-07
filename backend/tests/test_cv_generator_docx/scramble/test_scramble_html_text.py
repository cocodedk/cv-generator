"""Tests for HTML-aware scrambling."""

import re
from backend.cv_generator.scramble import scramble_html_text, _transform_text


class TestScrambleHtmlText:
    """Test HTML-aware scrambling."""

    def test_plain_text_no_html_tags(self):
        """Test with plain text containing no HTML tags."""
        key = "test-key"
        text = "John Doe"
        scrambled = scramble_html_text(text, key)
        # Should behave like scramble_text for plain text
        assert scrambled != text
        assert len(scrambled) == len(text)

    def test_html_tags_preserved(self):
        """Test that HTML tags are preserved."""
        key = "test-key"
        text = "Hello <strong>John</strong> Doe"
        scrambled = scramble_html_text(text, key)
        # HTML tags should be preserved
        assert "<strong>" in scrambled
        assert "</strong>" in scrambled
        # Text content should be scrambled
        assert "John" not in scrambled and scrambled != text

    def test_nested_html_tags(self):
        """Test with nested HTML tags."""
        key = "test-key"
        text = "<div><p>Hello <strong>John</strong></p></div>"
        scrambled = scramble_html_text(text, key)
        # All tags should be preserved
        assert "<div>" in scrambled
        assert "<p>" in scrambled
        assert "<strong>" in scrambled
        assert "</strong>" in scrambled
        assert "</p>" in scrambled
        assert "</div>" in scrambled

    def test_html_entities(self):
        """Test with HTML entities."""
        key = "test-key"
        text = "John &amp; Jane"
        scrambled = scramble_html_text(text, key)
        # HTML entities are scrambled like regular text (the & character is transformed)
        # But the structure should be preserved
        assert scrambled != text
        assert len(scrambled) == len(text)

    def test_reversibility_html(self):
        """Test that HTML scrambling is reversible."""
        key = "test-key"
        text = "Hello <strong>John</strong> Doe"
        scrambled = scramble_html_text(text, key)
        # Reverse by applying negative offset

        parts = re.split(r"(<[^>]+>)", scrambled)
        reversed_parts = []
        for part in parts:
            if part.startswith("<") and part.endswith(">"):
                reversed_parts.append(part)
            else:
                reversed_parts.append(_transform_text(part, key, reverse=True))
        reversed_text = "".join(reversed_parts)
        assert reversed_text == text
