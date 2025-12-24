"""DOCX generation pipeline."""
from pathlib import Path
from typing import Dict, Any
from backend.themes import validate_theme
from backend.cv_generator_docx.html_renderer import render_html
from backend.cv_generator_docx.pandoc import convert_html_to_docx
from backend.cv_generator_docx.template_builder import ensure_template


class DocxCVGenerator:
    """Generate DOCX documents from CV data."""

    def generate(self, cv_data: Dict[str, Any], output_path: str) -> str:
        theme = validate_theme(cv_data.get("theme", "classic"))
        output = Path(output_path)
        if output.suffix.lower() != ".docx":
            output = output.with_suffix(".docx")
        output.parent.mkdir(parents=True, exist_ok=True)

        html_path = output.with_suffix(".html")
        html_path.write_text(render_html(cv_data), encoding="utf-8")

        reference_docx = ensure_template(theme)
        convert_html_to_docx(html_path, output, reference_docx)
        return str(output)
