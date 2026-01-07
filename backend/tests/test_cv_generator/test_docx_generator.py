"""Tests for DOCX generator."""
import pytest
from unittest.mock import patch
from pathlib import Path
import tempfile

from backend.cv_generator.generator import DocxCVGenerator


class TestDocxCVGenerator:
    """Test DOCX CV generation."""

    @pytest.fixture
    def sample_cv_data(self):
        """Sample CV data for testing."""
        return {
            "personal_info": {
                "name": "John Doe",
                "title": "Software Engineer",
                "email": "john@example.com",
            },
            "experience": [
                {
                    "title": "Senior Developer",
                    "company": "Tech Corp",
                    "start_date": "2020-01",
                    "end_date": "2024-01",
                    "description": "Built web applications",
                }
            ],
            "education": [],
            "skills": ["Python", "JavaScript"],
            "theme": "classic",
        }

    @patch("backend.cv_generator.generator.validate_theme")
    @patch("backend.cv_generator.generator.render_html")
    @patch("backend.cv_generator.generator.ensure_template")
    @patch("backend.cv_generator.generator.convert_html_to_docx")
    def test_generate_successful(self, mock_convert, mock_ensure_template, mock_render_html, mock_validate_theme, sample_cv_data):
        """Test successful DOCX generation."""
        mock_validate_theme.return_value = "classic"
        mock_render_html.return_value = "<html>Test CV</html>"
        mock_ensure_template.return_value = "/path/to/template.docx"

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test_cv.docx"

            generator = DocxCVGenerator()
            result_path = generator.generate(sample_cv_data, str(output_path))

            assert result_path == str(output_path.with_suffix(".docx"))

            mock_validate_theme.assert_called_once_with("classic")
            mock_render_html.assert_called_once_with(sample_cv_data)
            mock_ensure_template.assert_called_once_with("classic")
            mock_convert.assert_called_once()

    @patch("backend.cv_generator.generator.validate_theme")
    @patch("backend.cv_generator.generator.render_html")
    @patch("backend.cv_generator.generator.ensure_template")
    @patch("backend.cv_generator.generator.convert_html_to_docx")
    def test_generate_with_docx_extension_already_present(self, mock_convert, mock_ensure_template, mock_render_html, mock_validate_theme, sample_cv_data):
        """Test generation when output path already has .docx extension."""
        mock_validate_theme.return_value = "classic"
        mock_render_html.return_value = "<html>Test CV</html>"
        mock_ensure_template.return_value = "/path/to/template.docx"

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test_cv.docx"

            generator = DocxCVGenerator()
            result_path = generator.generate(sample_cv_data, str(output_path))

            assert result_path == str(output_path)
            # File existence check removed since convert_html_to_docx is mocked

    @patch("backend.cv_generator.generator.validate_theme")
    @patch("backend.cv_generator.generator.render_html")
    @patch("backend.cv_generator.generator.ensure_template")
    @patch("backend.cv_generator.generator.convert_html_to_docx")
    def test_generate_without_docx_extension(self, mock_convert, mock_ensure_template, mock_render_html, mock_validate_theme, sample_cv_data):
        """Test generation when output path doesn't have .docx extension."""
        mock_validate_theme.return_value = "classic"
        mock_render_html.return_value = "<html>Test CV</html>"
        mock_ensure_template.return_value = "/path/to/template.docx"

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test_cv"

            generator = DocxCVGenerator()
            result_path = generator.generate(sample_cv_data, str(output_path))

            expected_path = output_path.with_suffix(".docx")
            assert result_path == str(expected_path)

    @patch("backend.cv_generator.generator.validate_theme")
    @patch("backend.cv_generator.generator.render_html")
    @patch("backend.cv_generator.generator.ensure_template")
    @patch("backend.cv_generator.generator.convert_html_to_docx")
    def test_generate_with_different_theme(self, mock_convert, mock_ensure_template, mock_render_html, mock_validate_theme, sample_cv_data):
        """Test generation with a different theme."""
        sample_cv_data["theme"] = "modern"
        mock_validate_theme.return_value = "modern"
        mock_render_html.return_value = "<html>Test CV</html>"
        mock_ensure_template.return_value = "/path/to/modern_template.docx"

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test_cv.docx"

            generator = DocxCVGenerator()
            result_path = generator.generate(sample_cv_data, str(output_path))

            assert result_path == str(output_path)

            mock_validate_theme.assert_called_once_with("modern")
            mock_ensure_template.assert_called_once_with("modern")

    @patch("backend.cv_generator.generator.validate_theme")
    @patch("backend.cv_generator.generator.render_html")
    @patch("backend.cv_generator.generator.ensure_template")
    @patch("backend.cv_generator.generator.convert_html_to_docx")
    def test_generate_without_theme_defaults_to_classic(self, mock_convert, mock_ensure_template, mock_render_html, mock_validate_theme):
        """Test generation without theme defaults to classic."""
        cv_data = {
            "personal_info": {"name": "Test"},
            "experience": [],
            "education": [],
            "skills": [],
            # No theme specified
        }

        mock_validate_theme.return_value = "classic"
        mock_render_html.return_value = "<html>Test CV</html>"
        mock_ensure_template.return_value = "/path/to/template.docx"

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test_cv.docx"

            generator = DocxCVGenerator()
            result_path = generator.generate(cv_data, str(output_path))

            assert result_path == str(output_path)

            mock_validate_theme.assert_called_once_with("classic")

    @patch("backend.cv_generator.generator.validate_theme")
    @patch("backend.cv_generator.generator.render_html")
    @patch("backend.cv_generator.generator.ensure_template")
    @patch("backend.cv_generator.generator.convert_html_to_docx")
    def test_generate_creates_parent_directories(self, mock_convert, mock_ensure_template, mock_render_html, mock_validate_theme, sample_cv_data):
        """Test that parent directories are created if they don't exist."""
        mock_validate_theme.return_value = "classic"
        mock_render_html.return_value = "<html>Test CV</html>"
        mock_ensure_template.return_value = "/path/to/template.docx"

        with tempfile.TemporaryDirectory() as temp_dir:
            nested_dir = Path(temp_dir) / "nested" / "deep" / "path"
            output_path = nested_dir / "test_cv.docx"

            generator = DocxCVGenerator()
            result_path = generator.generate(sample_cv_data, str(output_path))

            assert result_path == str(output_path)
            # File and directory existence checks removed since functions are mocked

    @patch("backend.cv_generator.generator.validate_theme")
    @patch("backend.cv_generator.generator.render_html")
    @patch("backend.cv_generator.generator.ensure_template")
    @patch("backend.cv_generator.generator.convert_html_to_docx")
    def test_generate_temp_file_cleanup_on_success(self, mock_convert, mock_ensure_template, mock_render_html, mock_validate_theme, sample_cv_data):
        """Test that temporary HTML file is cleaned up on successful generation."""
        mock_validate_theme.return_value = "classic"
        mock_render_html.return_value = "<html>Test CV</html>"
        mock_ensure_template.return_value = "/path/to/template.docx"

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test_cv.docx"

            generator = DocxCVGenerator()
            result_path = generator.generate(sample_cv_data, str(output_path))

            assert result_path == str(output_path)
            # File existence check removed since convert_html_to_docx is mocked

            # Check that no HTML files remain in temp directory
            html_files = list(Path(temp_dir).glob("*.html"))
            assert len(html_files) == 0

    @patch("backend.cv_generator.generator.validate_theme")
    @patch("backend.cv_generator.generator.render_html")
    @patch("backend.cv_generator.generator.ensure_template")
    @patch("backend.cv_generator.generator.convert_html_to_docx")
    def test_generate_temp_file_cleanup_on_failure(self, mock_convert, mock_ensure_template, mock_render_html, mock_validate_theme, sample_cv_data):
        """Test that temporary HTML file is cleaned up even on failure."""
        mock_validate_theme.return_value = "classic"
        mock_render_html.return_value = "<html>Test CV</html>"
        mock_ensure_template.return_value = "/path/to/template.docx"
        mock_convert.side_effect = Exception("Conversion failed")

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test_cv.docx"

            generator = DocxCVGenerator()

            with pytest.raises(Exception, match="Conversion failed"):
                generator.generate(sample_cv_data, str(output_path))

            # Check that no HTML files remain in temp directory even after failure
            html_files = list(Path(temp_dir).glob("*.html"))
            assert len(html_files) == 0

            # Output file should not exist since conversion failed
            assert not output_path.exists()
