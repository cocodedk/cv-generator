"""Render CV data into print-friendly A4 HTML."""

import base64
import mimetypes
from pathlib import Path
from typing import Any, Dict

from jinja2 import Environment, FileSystemLoader, select_autoescape

from backend.cv_generator_docx.html_renderer import _prepare_template_data
from backend.themes import get_theme

TEMPLATES_DIR = Path(__file__).resolve().parent / "templates" / "print_html"


def render_print_html(cv_data: Dict[str, Any]) -> str:
    """Render CV data into HTML designed for browser print (A4)."""
    # Prepare template data first to get theme
    template_data = _prepare_template_data(cv_data)
    theme_name = template_data.get("theme", "classic")

    # Check for theme-specific template in print_html directory first
    theme_template_path = TEMPLATES_DIR / f"{theme_name}.html"

    # If not found in print_html, check html directory
    html_templates_dir = TEMPLATES_DIR.parent / "html"
    html_theme_template_path = html_templates_dir / f"{theme_name}.html"

    # Determine which template to use
    if theme_template_path.exists():
        # Use theme-specific template from print_html directory
        template_name = f"{theme_name}.html"
    elif html_theme_template_path.exists():
        # Use theme-specific template from html directory
        template_name = f"{theme_name}.html"
    else:
        # Fall back to base.html from print_html directory
        template_name = "base.html"

        # Get theme definition for CSS variables (only needed for base.html)
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

    # Create environment with both template directories for includes
    env = Environment(
        loader=FileSystemLoader([str(TEMPLATES_DIR), str(html_templates_dir)]),
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
