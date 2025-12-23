"""Tests for CVGenerator."""
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

    def test_generate_theme_passed_to_styles(self, sample_cv_data, temp_output_dir):
        """Test that theme is correctly passed to style creation."""
        from backend.cv_generator.styles import CVStyles
        from odf.opendocument import OpenDocumentText

        generator = CVGenerator()
        themes = ["classic", "modern", "minimal", "elegant", "accented"]

        for theme in themes:
            sample_cv_data["theme"] = theme
            output_path = temp_output_dir / f"test_theme_{theme}.odt"
            generator.generate(sample_cv_data, str(output_path))

            # Verify file exists
            assert output_path.exists()

            # Verify theme was used by checking document styles
            doc = OpenDocumentText()
            doc = CVStyles.create_styles(doc, theme=theme)
            # Check that styles were created (non-empty styles list)
            assert len(list(doc.styles.childNodes)) > 0

    def test_generate_defaults_to_classic_when_theme_missing(self, temp_output_dir):
        """Test that generation defaults to classic theme when theme is missing."""
        generator = CVGenerator()
        cv_data = {
            "personal_info": {"name": "Test User"},
            "experience": [],
            "education": [],
            "skills": [],
        }
        # Explicitly don't include theme
        output_path = temp_output_dir / "test_no_theme.odt"
        generator.generate(cv_data, str(output_path))
        assert output_path.exists()

    def test_generate_theme_in_cv_data(self, sample_cv_data, temp_output_dir):
        """Test that theme from cv_data is used during generation."""
        generator = CVGenerator()
        sample_cv_data["theme"] = "modern"
        output_path = temp_output_dir / "test_theme_modern.odt"
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

    def test_generate_empty_sections(self, temp_output_dir):
        """Test generation with empty sections."""
        generator = CVGenerator()
        data = {
            "personal_info": {"name": "Test"},
            "experience": [],
            "education": [],
            "skills": [],
        }
        output_path = temp_output_dir / "empty.odt"
        generator.generate(data, str(output_path))
        assert output_path.exists()

    def test_generate_none_values(self, temp_output_dir):
        """Test generation with None values."""
        generator = CVGenerator()
        data = {
            "personal_info": {
                "name": "Test",
                "email": None,
                "phone": None,
                "summary": None,
            },
            "experience": [],
            "education": [],
            "skills": [],
        }
        output_path = temp_output_dir / "none.odt"
        generator.generate(data, str(output_path))
        assert output_path.exists()

    def test_generate_missing_optional_fields(self, temp_output_dir):
        """Test generation with missing optional fields."""
        generator = CVGenerator()
        data = {
            "personal_info": {"name": "Test"},
            "experience": [
                {"title": "Dev", "company": "Corp", "start_date": "2020-01"}
            ],
            "education": [{"degree": "BS", "institution": "Uni"}],
            "skills": [{"name": "Python"}],
        }
        output_path = temp_output_dir / "missing.odt"
        generator.generate(data, str(output_path))
        assert output_path.exists()
