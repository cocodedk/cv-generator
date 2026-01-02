"""HTML renderer module."""
from backend.cv_generator.html_renderer.prepare import prepare_template_data
from backend.cv_generator.html_renderer.render import render_html

# Alias for backward compatibility
_prepare_template_data = prepare_template_data

__all__ = ["render_html", "_prepare_template_data"]
