"""Tests for personal info dict scrambling."""

from backend.cv_generator.scramble import scramble_personal_info, SCRAMBLE_EXEMPT_FIELDS


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
