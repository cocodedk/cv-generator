"""Main markdown rendering logic."""

from typing import Dict, Any, List

from backend.cv_generator.markdown_renderer.sections import (
    _add_header,
    _add_contact_info,
    _add_summary,
    _add_experiences,
    _add_educations,
    _add_skills,
)


def render_markdown(cv_data: Dict[str, Any]) -> str:
    """Render CV data into Markdown."""
    lines: List[str] = []
    personal_info = cv_data.get("personal_info", {})
    _add_header(lines, personal_info)
    _add_contact_info(lines, personal_info)
    _add_summary(lines, personal_info)
    _add_experiences(lines, cv_data.get("experience", []))
    _add_educations(lines, cv_data.get("education", []))
    _add_skills(lines, cv_data.get("skills", []))
    content = "\n".join(lines).strip()
    return f"{content}\n" if content else ""
