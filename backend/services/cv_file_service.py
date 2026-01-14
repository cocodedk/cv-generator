"""Service for CV file generation operations."""
import base64
import copy
import json
import logging
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, Any, Optional
from backend.cv_generator.generator import DocxCVGenerator
from backend.cv_generator.layouts import LAYOUTS
from backend.cv_generator.print_html_renderer import render_print_html
from backend.database import queries

logger = logging.getLogger(__name__)


class CVFileService:
    """Service for generating CV files."""

    def __init__(
        self,
        output_dir: Path,
        showcase_dir: Path,
        showcase_keys_dir: Path,
        showcase_enabled: bool = True,
        scramble_key: Optional[str] = None,
    ):
        """Initialize service with output directory."""
        self.output_dir = output_dir
        self.showcase_dir = showcase_dir
        self.showcase_keys_dir = showcase_keys_dir
        self.showcase_enabled = showcase_enabled
        self.scramble_key = scramble_key
        self.docx_generator = DocxCVGenerator()

    def _build_output_path(
        self, cv_id: str, extension: str = ".html"
    ) -> tuple[str, Path]:
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

    def generate_showcase_for_cv(
        self, cv_id: str, cv_dict: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Generate HTML files for all layouts for public showcase."""
        if not self.showcase_enabled:
            logger.debug("Showcase generation disabled, skipping for CV %s", cv_id)
            return None

        theme = cv_dict.get("theme", "classic")
        logger.info(
            "Generating showcase for CV %s with theme %s in directory %s",
            cv_id, theme, self.showcase_dir
        )

        try:
            showcase_key = self.scramble_key or self._load_or_create_showcase_key(cv_id)
            layout_names = list(LAYOUTS.keys())
            cv_output_dir = self.showcase_dir / cv_id
            cv_output_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.error("Failed to set up showcase generation for CV %s: %s", cv_id, e)
            return None

        layouts = []
        for layout_name in layout_names:
            payload = copy.deepcopy(cv_dict)
            payload["layout"] = layout_name
            filename = f"{layout_name}-{theme}.html"
            output_path = cv_output_dir / filename
            html = render_print_html(
                payload,
                scramble_config={"enabled": True, "key": showcase_key},
            )
            output_path.write_text(html, encoding="utf-8")
            layouts.append(
                {
                    "layout": layout_name,
                    "theme": theme,
                    "file": f"{cv_id}/{filename}",
                }
            )

        manifest = {
            "cv_id": cv_id,
            "name": cv_dict.get("personal_info", {}).get("name") or "CV",
            "theme": theme,
            "layouts": layouts,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        (cv_output_dir / "manifest.json").write_text(
            json.dumps(manifest, indent=2, sort_keys=True),
            encoding="utf-8",
        )

        self._write_showcase_index()
        return manifest

    def generate_featured_templates(self) -> Optional[Dict[str, Any]]:
        """Generate multiple featured CV templates from the latest profile."""
        try:
            # Get the latest profile
            profile = queries.get_profile()
            if not profile:
                logger.warning("No profile found for featured templates generation")
                return None

            # Curated template combinations (layout + theme pairs)
            template_combinations = [
                # Web-optimized layouts with modern themes
                ("section-cards-grid", "modern"),
                ("section-cards-grid", "creative"),
                ("section-cards-grid", "elegant"),
                ("modern-sidebar", "modern"),
                ("modern-sidebar", "professional"),
                ("modern-sidebar", "minimal"),
                ("career-timeline", "modern"),
                ("career-timeline", "creative"),
                ("project-case-studies", "modern"),
                ("project-case-studies", "professional"),
                ("portfolio-spa", "modern"),
                ("portfolio-spa", "creative"),
                ("interactive-skills-matrix", "modern"),
                ("interactive-skills-matrix", "tech"),
                ("dark-mode-tech", "modern"),
                ("dark-mode-tech", "tech"),
                # Print-friendly layouts
                ("classic-two-column", "professional"),
                ("classic-two-column", "elegant"),
                ("ats-single-column", "minimal"),
                ("academic-cv", "professional"),
            ]

            templates_dir = Path(__file__).parent.parent.parent / "frontend" / "public" / "templates"
            templates_dir.mkdir(parents=True, exist_ok=True)

            templates = []
            for layout_name, theme_name in template_combinations:
                try:
                    # Prepare CV data for this layout and theme
                    cv_dict = self.prepare_cv_dict(profile)
                    cv_dict["layout"] = layout_name
                    cv_dict["theme"] = theme_name

                    # Generate filename and path
                    filename = f"{layout_name}-{theme_name}.html"
                    filepath = templates_dir / filename

                    # Generate HTML content
                    html_content = render_print_html(cv_dict)
                    filepath.write_text(html_content, encoding="utf-8")

                    # Get layout metadata
                    layout_info = LAYOUTS.get(layout_name, {})

                    templates.append({
                        "layout": layout_name,
                        "theme": theme_name,
                        "file": filename,
                        "name": f"{layout_info.get('name', layout_name)} ({theme_name})",
                        "description": layout_info.get('description', ''),
                        "print_friendly": layout_info.get('print_friendly', False),
                        "web_optimized": layout_info.get('web_optimized', False)
                    })

                    logger.debug("Generated template: %s", filename)

                except Exception as e:
                    logger.warning("Failed to generate template %s-%s: %s", layout_name, theme_name, e)
                    continue

            # Generate index.json with template metadata
            index_data = {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "profile_name": profile.get("personal_info", {}).get("name", "CV"),
                "templates": templates
            }

            index_path = templates_dir / "index.json"
            index_path.write_text(json.dumps(index_data, indent=2, sort_keys=True), encoding="utf-8")

            logger.info("Generated %d featured templates in %s", len(templates), templates_dir)
            return index_data

        except Exception as e:
            logger.exception("Failed to generate featured templates: %s", e)
            return None

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

    def _write_showcase_index(self) -> None:
        manifests = sorted(self.showcase_dir.glob("*/manifest.json"))
        cvs = []
        for manifest_path in manifests:
            try:
                content = json.loads(manifest_path.read_text(encoding="utf-8"))
                cvs.append(content)
            except json.JSONDecodeError:
                logger.warning("Skipping invalid manifest: %s", manifest_path)
        payload = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "cvs": cvs,
        }
        try:
            self.showcase_dir.mkdir(parents=True, exist_ok=True)
            (self.showcase_dir / "index.json").write_text(
                json.dumps(payload, indent=2, sort_keys=True),
                encoding="utf-8",
            )
        except Exception as e:
            logger.exception(
                "Failed to write showcase index.json: %s. Manifest data: %s",
                e,
                payload,
            )
            raise

    def _load_or_create_showcase_key(self, cv_id: str) -> str:
        self.showcase_keys_dir.mkdir(parents=True, exist_ok=True)
        key_path = self.showcase_keys_dir / f"{cv_id}.key"
        if key_path.exists():
            key = key_path.read_text(encoding="utf-8").strip()
            # Ensure existing key file has restrictive permissions
            try:
                os.chmod(key_path, 0o600)
            except OSError:
                # Log but don't fail if permission change fails
                logger.debug(
                    "Could not set restrictive permissions on existing key file: %s",
                    key_path,
                )
            return key
        key = base64.b64encode(os.urandom(24)).decode("ascii")
        key_path.write_text(key, encoding="utf-8")
        # Set restrictive permissions (owner read/write only)
        try:
            os.chmod(key_path, 0o600)
        except OSError:
            # Log but don't fail if permission change fails
            logger.debug(
                "Could not set restrictive permissions on key file: %s", key_path
            )
        return key

    def cleanup_old_download_files(self, max_age_hours: int = 24) -> int:
        """Clean up old download files that are older than max_age_hours.

        Returns the number of files cleaned up.
        """
        if not self.output_dir.exists():
            return 0

        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        cleaned_count = 0

        # Clean up HTML and DOCX files
        for pattern in ["*.html", "*.docx"]:
            for file_path in self.output_dir.glob(pattern):
                try:
                    # Skip if file is in showcase_keys directory
                    if "showcase_keys" in str(file_path):
                        continue

                    # Check file modification time
                    mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if mtime < cutoff_time:
                        file_path.unlink()
                        cleaned_count += 1
                        logger.info("Cleaned up old download file: %s", file_path)
                except (OSError, ValueError) as e:
                    logger.warning("Failed to clean up file %s: %s", file_path, e)

        return cleaned_count
