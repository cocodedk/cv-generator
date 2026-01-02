"""Tests for personal info scrambling utilities."""
import hashlib
from backend.cv_generator.scramble import (
    scramble_text,
    scramble_html_text,
    scramble_personal_info,
    _derive_offsets,
    SCRAMBLE_EXEMPT_FIELDS,
)


class TestDeriveOffsets:
    """Test key derivation for scrambling offsets."""

    def test_deterministic_offset_generation(self):
        """Test that same key produces same offsets."""
        key = "test-key-123"
        offset1 = _derive_offsets(key)
        offset2 = _derive_offsets(key)
        assert offset1 == offset2

    def test_offset_ranges(self):
        """Test that offsets are within valid ranges."""
        key = "test-key"
        alpha_offset, digit_offset = _derive_offsets(key)
        assert 0 <= alpha_offset < 26
        assert 0 <= digit_offset < 10

    def test_offsets_match_manual_sha256(self):
        """Test that offsets match a manual SHA256 derivation."""
        key = "test-key-abc-123"
        digest = hashlib.sha256(key.encode("utf-8")).digest()
        offset = int.from_bytes(digest[:4], "big")
        expected = (offset % 26, offset % 10)
        assert _derive_offsets(key) == expected


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
        from backend.cv_generator.scramble import _transform_text

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
        from backend.cv_generator.scramble import _transform_text
        import re

        parts = re.split(r"(<[^>]+>)", scrambled)
        reversed_parts = []
        for part in parts:
            if part.startswith("<") and part.endswith(">"):
                reversed_parts.append(part)
            else:
                reversed_parts.append(_transform_text(part, key, reverse=True))
        reversed_text = "".join(reversed_parts)
        assert reversed_text == text


class TestScramblePersonalInfo:
    """Test personal info dict scrambling."""

    def test_complete_personal_info_dict(self):
        """Test scrambling complete personal_info dict."""
        key = "test-key"
        personal_info = {
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "+1234567890",
            "address": {
                "street": "123 Main St",
                "city": "New York",
                "zip": "10001",
            },
            "summary": "Experienced developer",
            "photo": "path/to/photo.jpg",
        }
        scrambled = scramble_personal_info(personal_info, key)
        assert scrambled["name"] != personal_info["name"]
        assert scrambled["email"] != personal_info["email"]
        assert scrambled["phone"] != personal_info["phone"]
        assert scrambled["photo"] is None
        assert scrambled["summary"] != personal_info["summary"]

    def test_exempt_fields_linkedin(self):
        """Test that linkedin field is exempt from scrambling."""
        key = "test-key"
        personal_info = {
            "name": "John Doe",
            "linkedin": "https://linkedin.com/in/johndoe",
        }
        scrambled = scramble_personal_info(personal_info, key)
        assert scrambled["name"] != personal_info["name"]
        assert scrambled["linkedin"] == personal_info["linkedin"]

    def test_exempt_fields_github(self):
        """Test that github field is exempt from scrambling."""
        key = "test-key"
        personal_info = {
            "name": "John Doe",
            "github": "https://github.com/johndoe",
        }
        scrambled = scramble_personal_info(personal_info, key)
        assert scrambled["name"] != personal_info["name"]
        assert scrambled["github"] == personal_info["github"]

    def test_exempt_fields_website(self):
        """Test that website field is exempt from scrambling."""
        key = "test-key"
        personal_info = {
            "name": "John Doe",
            "website": "https://johndoe.com",
        }
        scrambled = scramble_personal_info(personal_info, key)
        assert scrambled["name"] != personal_info["name"]
        assert scrambled["website"] == personal_info["website"]

    def test_summary_uses_html_aware_scrambling(self):
        """Test that summary field uses HTML-aware scrambling."""
        key = "test-key"
        personal_info = {
            "name": "John Doe",
            "summary": "Hello <strong>John</strong> Doe",
        }
        scrambled = scramble_personal_info(personal_info, key)
        # HTML tags should be preserved
        assert "<strong>" in scrambled["summary"]
        assert "</strong>" in scrambled["summary"]
        # Text should be scrambled
        assert scrambled["summary"] != personal_info["summary"]

    def test_address_dict_format(self):
        """Test address field with dict format."""
        key = "test-key"
        personal_info = {
            "name": "John Doe",
            "address": {
                "street": "123 Main St",
                "city": "New York",
                "zip": "10001",
            },
        }
        scrambled = scramble_personal_info(personal_info, key)
        assert isinstance(scrambled["address"], dict)
        assert scrambled["address"]["street"] != personal_info["address"]["street"]
        assert scrambled["address"]["city"] != personal_info["address"]["city"]
        assert scrambled["address"]["zip"] != personal_info["address"]["zip"]

    def test_address_string_format(self):
        """Test address field with string format."""
        key = "test-key"
        personal_info = {
            "name": "John Doe",
            "address": "123 Main St, New York, NY 10001",
        }
        scrambled = scramble_personal_info(personal_info, key)
        assert isinstance(scrambled["address"], str)
        assert scrambled["address"] != personal_info["address"]

    def test_photo_field_set_to_none(self):
        """Test that photo field is set to None."""
        key = "test-key"
        personal_info = {
            "name": "John Doe",
            "photo": "path/to/photo.jpg",
        }
        scrambled = scramble_personal_info(personal_info, key)
        assert scrambled["photo"] is None

    def test_none_values_preserved(self):
        """Test that None values are preserved."""
        key = "test-key"
        personal_info = {
            "name": "John Doe",
            "email": None,
            "phone": None,
        }
        scrambled = scramble_personal_info(personal_info, key)
        assert scrambled["name"] != personal_info["name"]
        assert scrambled["email"] is None
        assert scrambled["phone"] is None

    def test_empty_dict_handling(self):
        """Test handling of empty dict."""
        key = "test-key"
        personal_info = {}
        scrambled = scramble_personal_info(personal_info, key)
        assert scrambled == {}

    def test_none_dict_handling(self):
        """Test handling of None dict."""
        key = "test-key"
        personal_info = None
        scrambled = scramble_personal_info(personal_info, key)
        assert scrambled == {}

    def test_all_exempt_fields_unchanged(self):
        """Test that all exempt fields remain unchanged."""
        key = "test-key"
        personal_info = {
            "name": "John Doe",
            "linkedin": "https://linkedin.com/in/johndoe",
            "github": "https://github.com/johndoe",
            "website": "https://johndoe.com",
        }
        scrambled = scramble_personal_info(personal_info, key)
        assert scrambled["name"] != personal_info["name"]
        for field in SCRAMBLE_EXEMPT_FIELDS:
            if field in personal_info:
                assert scrambled[field] == personal_info[field]
