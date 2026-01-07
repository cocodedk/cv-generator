"""Tests for build_friendly_field_name function."""

from backend.app_helpers.exception_handlers.field_names import build_friendly_field_name


class TestBuildFriendlyFieldName:
    """Test build_friendly_field_name function."""

    def test_empty_location(self):
        """Test empty location returns Unknown field."""
        assert build_friendly_field_name(()) == "Unknown field"
        assert build_friendly_field_name(None) == "Unknown field"

    def test_personal_info_fields(self):
        """Test personal info field name conversion."""
        # Top-level personal info fields
        assert build_friendly_field_name(("personal_info", "name")) == "Full Name"
        assert build_friendly_field_name(("personal_info", "email")) == "Email"
        assert build_friendly_field_name(("personal_info", "phone")) == "Phone"
        assert build_friendly_field_name(("personal_info", "title")) == "Professional Title"
        assert build_friendly_field_name(("personal_info", "summary")) == "Professional Summary"
        assert build_friendly_field_name(("personal_info", "linkedin")) == "LinkedIn"
        assert build_friendly_field_name(("personal_info", "github")) == "GitHub"
        assert build_friendly_field_name(("personal_info", "website")) == "Website"
        assert build_friendly_field_name(("personal_info", "address")) == "Address"

    def test_experience_array_indices(self):
        """Test experience array index handling."""
        assert build_friendly_field_name(("experience", 0, "title")) == "Experience 1 - Job Title"
        assert build_friendly_field_name(("experience", 1, "company")) == "Experience 2 - Company"
        assert build_friendly_field_name(("experience", 2, "description")) == "Experience 3 - Role Summary"
        assert build_friendly_field_name(("experience", 0, "start_date")) == "Experience 1 - Start Date"
        assert build_friendly_field_name(("experience", 0, "end_date")) == "Experience 1 - End Date"
        assert build_friendly_field_name(("experience", 0, "location")) == "Experience 1 - Location"

    def test_education_array_indices(self):
        """Test education array index handling."""
        assert build_friendly_field_name(("education", 0, "degree")) == "Education 1 - Degree"
        assert build_friendly_field_name(("education", 1, "institution")) == "Education 2 - Institution"
        assert build_friendly_field_name(("education", 0, "year")) == "Education 1 - Year"
        assert build_friendly_field_name(("education", 0, "field")) == "Education 1 - Field"
        assert build_friendly_field_name(("education", 0, "gpa")) == "Education 1 - GPA"

    def test_skills_array_indices(self):
        """Test skills array index handling."""
        assert build_friendly_field_name(("skills", 0, "name")) == "Skill 1 - Skill Name"
        assert build_friendly_field_name(("skills", 1, "category")) == "Skill 2 - Category"
        assert build_friendly_field_name(("skills", 2, "level")) == "Skill 3 - Level"

    def test_unknown_sections_and_fields(self):
        """Test unknown sections and fields fallback to title case."""
        # Unknown section with field - both get processed as field names
        assert build_friendly_field_name(("unknown_section", "field")) == "Unknown SectionField"
        # Known section with unknown field - field gets title cased
        assert build_friendly_field_name(("personal_info", "unknown_field")) == "Unknown Field"
        # Single unknown field
        assert build_friendly_field_name(("some_field",)) == "Some Field"

    def test_generic_array_handling(self):
        """Test generic array handling for unknown array types."""
        result = build_friendly_field_name(("unknown_array", 0, "field"))
        # Current logic handles unknown arrays reasonably
        assert "unknown_array[0]" in result and "Field" in result

    def test_complex_nested_paths(self):
        """Test complex nested paths."""
        # Experience with nested projects - current logic handles basic nesting
        result = build_friendly_field_name(("experience", 0, "projects", 0, "name"))
        # The current implementation gives a reasonable result for deep nesting
        assert "Experience 1" in result and "Name" in result
