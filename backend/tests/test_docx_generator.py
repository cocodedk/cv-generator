"""Tests for DOCX CV generation."""
import shutil
import pytest
from backend.cv_generator.generator import DocxCVGenerator
from backend.cv_generator.template_builder import ensure_template


@pytest.mark.integration
@pytest.mark.skipif(not shutil.which("pandoc"), reason="pandoc is required")
def test_docx_generator_creates_files(sample_cv_data, temp_output_dir):
    """Ensure DOCX and HTML outputs are created."""
    generator = DocxCVGenerator()
    output_path = temp_output_dir / "test.docx"

    generator.generate(sample_cv_data, str(output_path))

    assert output_path.exists()
    assert output_path.with_suffix(".html").exists()
    assert ensure_template(sample_cv_data["theme"]).exists()
