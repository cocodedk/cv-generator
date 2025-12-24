"""Render CV data into print-friendly A4 HTML."""

import base64
import mimetypes
from pathlib import Path
from typing import Any, Dict

from jinja2 import Environment, FileSystemLoader, select_autoescape

from backend.cv_generator_docx.html_renderer import _prepare_template_data

TEMPLATES_DIR = Path(__file__).resolve().parent / "templates" / "print_html"


def render_print_html(cv_data: Dict[str, Any]) -> str:
    """Render CV data into HTML designed for browser print (A4)."""
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=select_autoescape(["html", "xml"]),
    )
    template = env.get_template("base.html")

    template_data = _prepare_template_data(cv_data)
    personal_info = template_data.get("personal_info", {})
    photo = personal_info.get("photo")
    if isinstance(photo, str):
        personal_info["photo"] = _maybe_inline_image(photo)

    return template.render(**template_data)


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
