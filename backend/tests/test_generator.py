"""Tests for CVGenerator."""
import pytest
from pathlib import Path
from backend.cv_generator.generator import CVGenerator


class TestCVGenerator:
    """Test CVGenerator class."""

    def test_generate_creates_file(self, sample_cv_data, temp_output_dir):
        """Test that generate creates an ODT file."""
        generator = CVGenerator()
        output_path = temp_output_dir / "test_cv.odt"

        result = generator.generate(sample_cv_data, str(output_path))

        assert Path(result).exists()
        assert output_path.exists()
        assert output_path.suffix == ".odt"

    def test_generate_different_themes(self, sample_cv_data, temp_output_dir):
        """Test generation with different themes."""
        generator = CVGenerator()
        themes = ["classic", "modern", "minimal", "elegant", "accented"]

        for theme in themes:
            sample_cv_data["theme"] = theme
            output_path = temp_output_dir / f"test_{theme}.odt"
            generator.generate(sample_cv_data, str(output_path))
            assert output_path.exists()

    def test_format_address(self, sample_cv_data, temp_output_dir):
        """Test address formatting."""
        generator = CVGenerator()
        output_path = temp_output_dir / "test.odt"

        # Test with full address
        generator.generate(sample_cv_data, str(output_path))
        assert output_path.exists()

        # Test with partial address
        sample_cv_data["personal_info"]["address"] = {"city": "New York"}
        output_path2 = temp_output_dir / "test2.odt"
        generator.generate(sample_cv_data, str(output_path2))
        assert output_path2.exists()

    def test_generate_with_minimal_data(self, temp_output_dir):
        """Test generation with minimal required data."""
        generator = CVGenerator()
        minimal_data = {
            "personal_info": {"name": "Jane Doe"},
            "experience": [],
            "education": [],
            "skills": [],
        }
        output_path = temp_output_dir / "minimal.odt"
        generator.generate(minimal_data, str(output_path))
        assert output_path.exists()

    def test_generate_with_all_sections(self, sample_cv_data, temp_output_dir):
        """Test generation with all sections populated."""
        generator = CVGenerator()
        output_path = temp_output_dir / "full.odt"
        generator.generate(sample_cv_data, str(output_path))
        assert output_path.exists()

    def test_accented_theme_layout(self, sample_cv_data, temp_output_dir):
        """Test accented theme uses different layout."""
        generator = CVGenerator()
        sample_cv_data["theme"] = "accented"
        output_path = temp_output_dir / "accented.odt"
        generator.generate(sample_cv_data, str(output_path))
        assert output_path.exists()
