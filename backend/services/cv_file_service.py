"""Service for CV file generation operations."""
from pathlib import Path
from typing import Dict, Any
from backend.cv_generator.generator import CVGenerator
from backend.database import queries


class CVFileService:
    """Service for generating CV files."""

    def __init__(self, output_dir: Path):
        """Initialize service with output directory."""
        self.output_dir = output_dir
        self.generator = CVGenerator()

    def generate_file_for_cv(self, cv_id: str, cv_dict: Dict[str, Any]) -> str:
        """Generate ODT file for a CV and return filename."""
        filename = f"cv_{cv_id[:8]}.odt"
        output_path = self.output_dir / filename

        # Delete old file if it exists (in case regenerating)
        if output_path.exists():
            output_path.unlink()

        # Generate ODT file
        self.generator.generate(cv_dict, str(output_path))

        # Persist generated filename
        queries.set_cv_filename(cv_id, filename)

        return filename

    def prepare_cv_dict(self, cv: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare CV data dict for generator from database result."""
        return {
            "personal_info": cv.get("personal_info", {}),
            "experience": cv.get("experience", []),
            "education": cv.get("education", []),
            "skills": cv.get("skills", []),
            "theme": "classic",  # Default theme (not stored in DB)
        }
