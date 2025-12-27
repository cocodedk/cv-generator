"""Render CV data into print-friendly A4 HTML."""

import base64
import logging
import mimetypes
from pathlib import Path
from typing import Any, Dict

from jinja2 import Environment, FileSystemLoader, select_autoescape

from backend.cv_generator_docx.html_renderer import _prepare_template_data
from backend.cv_generator_docx.layouts import validate_layout
from backend.themes import get_theme

logger = logging.getLogger(__name__)

TEMPLATES_DIR = Path(__file__).resolve().parent / "templates" / "print_html"
LAYOUTS_DIR = Path(__file__).resolve().parent / "templates" / "layouts"


def render_print_html(cv_data: Dict[str, Any]) -> str:
    """Render CV data into HTML designed for browser print (A4)."""
    # Prepare template data first to get theme and layout
    template_data = _prepare_template_data(cv_data)
    theme_name = template_data.get("theme", "classic")
    layout_name = template_data.get("layout", "classic-two-column")

    logger.debug(
        "[render_print_html] Input layout from cv_data: %s, from template_data: %s",
        cv_data.get("layout"),
        layout_name,
    )

    # Validate layout name
    layout_name = validate_layout(layout_name)

    # Check for layout-specific template in layouts directory
    layout_template_path = LAYOUTS_DIR / f"{layout_name}.html"

    logger.debug(
        "[render_print_html] Validated layout: %s, template path exists: %s",
        layout_name,
        layout_template_path.exists(),
    )

    # Determine which template to use
    if layout_template_path.exists():
        # Use layout template from layouts directory
        template_dir = LAYOUTS_DIR
        template_name = f"{layout_name}.html"
    else:
        # Fall back to theme-specific template in print_html directory
        theme_template_path = TEMPLATES_DIR / f"{theme_name}.html"
        if theme_template_path.exists():
            template_dir = TEMPLATES_DIR
            template_name = f"{theme_name}.html"
        else:
            # Final fallback to base.html
            template_dir = TEMPLATES_DIR
            template_name = "base.html"

    logger.info(
        "[render_print_html] Using template: %s from dir: %s",
        template_name,
        template_dir,
    )

    # Get theme definition for CSS variables
    theme = get_theme(theme_name)
    accent_color = theme.get("accent_color", theme.get("accent", "#0f766e"))
    section_color = theme.get("section", {}).get("color", accent_color)
    text_color = theme.get("normal", {}).get("color", "#0f172a")
    muted_color = theme.get("text_secondary", "#475569")

    # Add theme CSS variables to template data (will override :root variables)
    template_data["theme_css"] = _build_theme_css(
        accent=accent_color,
        accent_2=section_color,
        ink=text_color,
        muted=muted_color,
    )

    # Create environment with template directory for includes
    # Use both directories so layouts can include components
    env = Environment(
        loader=FileSystemLoader([str(template_dir), str(LAYOUTS_DIR)]),
        autoescape=select_autoescape(["html", "xml"]),
    )
    template = env.get_template(template_name)

    personal_info = template_data.get("personal_info", {})
    photo = personal_info.get("photo")
    if isinstance(photo, str):
        personal_info["photo"] = _maybe_inline_image(photo)

    return template.render(**template_data)


def _build_theme_css(accent: str, accent_2: str, ink: str, muted: str) -> str:
    """Build CSS override for theme colors."""
    # Return CSS that will override the :root variables
    return f":root{{--accent:{accent};--accent-2:{accent_2};--ink:{ink};--muted:{muted};}}"


def _maybe_inline_image(value: str) -> str:
    if value.startswith(("http://", "https://", "data:")):
        return value

    candidate = Path(value)
    if not candidate.is_file():
        return value

    mime, _ = mimetypes.guess_type(candidate.name)
    if mime is None:
        mime = "application/octet-stream"
    encoded = base64.b64encode(candidate.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"
