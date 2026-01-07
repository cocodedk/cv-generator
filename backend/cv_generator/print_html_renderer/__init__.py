"""Print HTML renderer package."""

# Re-export main functionality for backward compatibility
from backend.cv_generator.print_html_renderer.renderer import render_print_html
from backend.cv_generator.print_html_renderer.theme_builder import _build_theme_css
from backend.cv_generator.print_html_renderer.image_utils import _maybe_inline_image
from backend.cv_generator.print_html_renderer.scramble_injection import _inject_scramble_script, _scramble_script

__all__ = [
    "render_print_html",
    "_build_theme_css",
    "_maybe_inline_image",
    "_inject_scramble_script",
    "_scramble_script",
]
