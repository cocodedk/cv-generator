"""Markdown renderer package."""

# Re-export main functionality for backward compatibility
from backend.cv_generator.markdown_renderer.renderer import render_markdown
from backend.cv_generator.markdown_renderer.sections import (
    _add_header,
    _add_contact_info,
    _add_summary,
    _add_experiences,
    _add_educations,
    _add_skills,
)
from backend.cv_generator.markdown_renderer.experience_rendering import (
    _render_experience,
    _add_experience_header,
    _add_experience_meta,
    _add_experience_description,
    _add_experience_projects,
    _add_project_header,
    _add_project_technologies,
    _add_project_highlights,
)
from backend.cv_generator.markdown_renderer.utils import (
    _render_contact_table,
    _format_address,
    _escape_html,
    _render_education,
    _render_skills,
    _split_description,
    _yaml_escape,
)

__all__ = [
    "render_markdown",
    "_add_header",
    "_add_contact_info",
    "_add_summary",
    "_add_experiences",
    "_add_educations",
    "_add_skills",
    "_render_experience",
    "_add_experience_header",
    "_add_experience_meta",
    "_add_experience_description",
    "_add_experience_projects",
    "_add_project_header",
    "_add_project_technologies",
    "_add_project_highlights",
    "_render_contact_table",
    "_format_address",
    "_escape_html",
    "_render_education",
    "_render_skills",
    "_split_description",
    "_yaml_escape",
]
