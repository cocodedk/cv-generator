"""Main HTML rendering function."""
from pathlib import Path
from typing import Dict, Any
from jinja2 import Environment, FileSystemLoader, select_autoescape
from backend.cv_generator_docx.html_renderer.prepare import prepare_template_data


TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates" / "html"


def render_html(cv_data: Dict[str, Any]) -> str:
    """Render CV data into HTML using Jinja2 templates."""
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=select_autoescape(["html", "xml"]),
    )

    # Prepare data for template
    template_data = prepare_template_data(cv_data)

    # Select template based on theme, fallback to base.html
    theme = template_data.get("theme", "classic")
    theme_template_path = TEMPLATES_DIR / f"{theme}.html"
    template_name = f"{theme}.html" if theme_template_path.exists() else "base.html"

    template = env.get_template(template_name)

    return template.render(**template_data)
