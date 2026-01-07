"""Tests for _build_field_path function."""

from backend.app_helpers.exception_handlers.field_paths import build_field_path


class TestBuildFieldPath:
    """Test _build_field_path function."""

    def test_empty_location(self):
        """Test empty location returns empty string."""
        assert build_field_path(()) == ""
        assert build_field_path(None) == ""

    def test_simple_field_paths(self):
        """Test simple field paths."""
        assert build_field_path(("name",)) == "name"
        assert build_field_path(("email",)) == "email"
        assert build_field_path(("personal_info", "name")) == "personal_info.name"

    def test_array_index_paths(self):
        """Test array index path generation."""
        assert build_field_path(("experience", 0, "title")) == "experience.0.title"
        assert build_field_path(("skills", 1, "name")) == "skills.1.name"
        assert build_field_path(("education", 2, "degree")) == "education.2.degree"

    def test_leading_array_index(self):
        """Test paths starting with array index."""
        assert build_field_path((0, "name")) == "0.name"

    def test_complex_nested_paths(self):
        """Test complex nested paths."""
        assert build_field_path(("experience", 0, "projects", 1, "name")) == "experience.0.projects.1.name"
