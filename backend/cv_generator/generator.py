"""DOCX generation pipeline."""
import tempfile
from pathlib import Path
from typing import Dict, Any
from backend.themes import validate_theme
from backend.cv_generator.html_renderer import render_html
from backend.cv_generator.pandoc import convert_html_to_docx
from backend.cv_generator.template_builder import ensure_template


class DocxCVGenerator:
    """Generate DOCX documents from CV data."""

    def generate(self, cv_data: Dict[str, Any], output_path: str) -> str:
        theme = validate_theme(cv_data.get("theme", "classic"))
        output = Path(output_path)
        if output.suffix.lower() != ".docx":
            output = output.with_suffix(".docx")
        output.parent.mkdir(parents=True, exist_ok=True)

        # Create temporary HTML file for intermediate conversion
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".html", delete=False, encoding="utf-8"
        ) as temp_file:
            html_path = Path(temp_file.name)
            temp_file.write(render_html(cv_data))

        try:
            reference_docx = ensure_template(theme)
            convert_html_to_docx(html_path, output, reference_docx)
        finally:
            # Clean up temporary HTML file
            if html_path.exists():
                html_path.unlink()

        return str(output)
