"""Tests for basic text scrambling."""

from backend.cv_generator.scramble import scramble_text, _transform_text


class TestScrambleText:
    """Test basic text scrambling."""

    def test_simple_string_name(self):
        """Test scrambling a simple name."""
        key = "test-key"
        text = "John Doe"
        scrambled = scramble_text(text, key)
        assert scrambled != text
        assert len(scrambled) == len(text)
        assert scrambled.count(" ") == text.count(" ")

    def test_simple_string_email(self):
        """Test scrambling an email address."""
        key = "test-key"
        text = "john.doe@example.com"
        scrambled = scramble_text(text, key)
        assert scrambled != text
        assert len(scrambled) == len(text)
        # Special characters should be preserved
        assert "@" in scrambled
        assert "." in scrambled

    def test_simple_string_phone(self):
        """Test scrambling a phone number."""
        key = "test-key"
        text = "+1234567890"
        scrambled = scramble_text(text, key)
        assert scrambled != text
        assert len(scrambled) == len(text)
        # Plus sign should be preserved
        assert "+" in scrambled

    def test_mixed_case(self):
        """Test scrambling with mixed case."""
        key = "test-key"
        text = "JohnDoe"
        scrambled = scramble_text(text, key)
        assert scrambled != text
        # Case should be preserved
        assert scrambled[0].isupper() == text[0].isupper()
        assert scrambled[4].isupper() == text[4].isupper()

    def test_digits_phone_number(self):
        """Test scrambling digits in phone numbers."""
        key = "test-key"
        text = "1234567890"
        scrambled = scramble_text(text, key)
        assert scrambled != text
        assert len(scrambled) == len(text)
        # All should still be digits
        assert scrambled.isdigit()

    def test_digits_postal_code(self):
        """Test scrambling digits in postal codes."""
        key = "test-key"
        text = "10001"
        scrambled = scramble_text(text, key)
        assert scrambled != text
        assert len(scrambled) == len(text)
        assert scrambled.isdigit()

    def test_special_characters_preserved(self):
        """Test that special characters are preserved."""
        key = "test-key"
        text = "John.Doe@example.com"
        scrambled = scramble_text(text, key)
        # Special characters should be in same positions
        assert "." in scrambled
        assert "@" in scrambled
        # Count should match
        assert scrambled.count(".") == text.count(".")
        assert scrambled.count("@") == text.count("@")

    def test_unicode_characters_preserved(self):
        """Test that Unicode characters are preserved."""
        key = "test-key"
        text = "東京"
        scrambled = scramble_text(text, key)
        # Unicode should be preserved as-is
        assert scrambled == text

    def test_determinism(self):
        """Test that same key and text produce same output."""
        key = "test-key"
        text = "John Doe"
        scrambled1 = scramble_text(text, key)
        scrambled2 = scramble_text(text, key)
        assert scrambled1 == scrambled2

    def test_reversibility(self):
        """Test that scrambling is reversible."""
        key = "test-key"
        text = "John Doe"
        scrambled = scramble_text(text, key)
        # Reverse by applying negative offset
        reversed_text = _transform_text(scrambled, key, reverse=True)
        assert reversed_text == text

    def test_empty_string(self):
        """Test scrambling empty string."""
        key = "test-key"
        text = ""
        scrambled = scramble_text(text, key)
        assert scrambled == ""

    def test_whitespace_preserved(self):
        """Test that whitespace is preserved."""
        key = "test-key"
        text = "John  Doe\nTest"
        scrambled = scramble_text(text, key)
        # Whitespace should be preserved
        assert "  " in scrambled
        assert "\n" in scrambled
