"""Service for CV file generation operations."""
import logging
from pathlib import Path
from typing import Dict, Any
from backend.cv_generator_docx.generator import DocxCVGenerator
from backend.cv_generator_docx.print_html_renderer import render_print_html
from backend.database import queries

logger = logging.getLogger(__name__)


class CVFileService:
    """Service for generating CV files."""

    def __init__(self, output_dir: Path):
        """Initialize service with output directory."""
        self.output_dir = output_dir
        self.docx_generator = DocxCVGenerator()

    def _build_output_path(self, cv_id: str, extension: str = ".html") -> tuple[str, Path]:
        filename = f"cv_{cv_id[:8]}{extension}"
        output_path = self.output_dir / filename
        if output_path.exists():
            output_path.unlink()
        return filename, output_path

    def generate_file_for_cv(self, cv_id: str, cv_dict: Dict[str, Any]) -> str:
        """Generate HTML file for a CV and return filename."""
        # Ensure theme is always present in cv_dict
        if "theme" not in cv_dict or cv_dict["theme"] is None:
            cv_dict["theme"] = "classic"
        theme = cv_dict["theme"]
        logger.debug(
            "Generating HTML file for CV %s with theme: %s (cv_dict keys: %s)",
            cv_id,
            theme,
            list(cv_dict.keys()),
        )

        filename, output_path = self._build_output_path(cv_id, ".html")
        html_content = render_print_html(cv_dict)
        output_path.write_text(html_content, encoding="utf-8")

        # Persist generated filename
        queries.set_cv_filename(cv_id, filename)

        return filename

    def generate_docx_for_cv(self, cv_id: str, cv_dict: Dict[str, Any]) -> str:
        """Generate DOCX file for a CV and return filename."""
        # Ensure theme is always present in cv_dict
        if "theme" not in cv_dict or cv_dict["theme"] is None:
            cv_dict["theme"] = "classic"
        theme = cv_dict["theme"]
        logger.debug(
            "Generating DOCX file for CV %s with theme: %s (cv_dict keys: %s)",
            cv_id,
            theme,
            list(cv_dict.keys()),
        )

        filename, output_path = self._build_output_path(cv_id, ".docx")
        self.docx_generator.generate(cv_dict, str(output_path))

        # Persist generated filename
        queries.set_cv_filename(cv_id, filename)

        return filename

    def prepare_cv_dict(self, cv: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare CV data dict for generator from database result."""
        theme = cv.get("theme", "classic")
        layout = cv.get("layout", "classic-two-column")
        logger.debug(
            "Preparing CV dict with theme: %s, layout: %s (from cv keys: %s)",
            theme,
            layout,
            list(cv.keys()),
        )
        return {
            "personal_info": cv.get("personal_info", {}),
            "experience": cv.get("experience", []),
            "education": cv.get("education", []),
            "skills": cv.get("skills", []),
            # Default to "classic" for backward compatibility; can be overridden
            # by providing a "theme" field in the cv dict
            "theme": theme,
            "layout": layout,
        }
