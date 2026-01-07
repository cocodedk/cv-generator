"""Section rendering functions."""

from typing import Dict, Any, List

from backend.cv_generator.markdown_renderer.experience_rendering import _render_experience
from backend.cv_generator.markdown_renderer.utils import _render_contact_table, _render_education, _render_skills


def _add_header(lines: List[str], personal_info: Dict[str, Any]) -> None:
    """Add YAML front matter header."""
    name = personal_info.get("name")
    title = personal_info.get("title")
    if name or title:
        lines.append("---")
        if name:
            lines.append(f'title: "{_yaml_escape(name)}"')
        if title:
            lines.append(f'subtitle: "{_yaml_escape(title)}"')
        lines.append("---")
        lines.append("")


def _add_contact_info(lines: List[str], personal_info: Dict[str, Any]) -> None:
    """Add contact information line."""
    contact_lines = _render_contact_table(personal_info)
    if contact_lines:
        lines.extend(contact_lines)
    lines.append("")


def _add_summary(lines: List[str], personal_info: Dict[str, Any]) -> None:
    """Add summary section."""
    summary = personal_info.get("summary")
    if summary:
        lines.extend(["## Summary", summary.strip(), ""])


def _add_experiences(lines: List[str], experiences: List[Dict[str, Any]]) -> None:
    """Add experience section."""
    if experiences:
        lines.append("## Experience")
        for exp in experiences:
            lines.extend(_render_experience(exp))
        lines.append("")


def _add_educations(lines: List[str], educations: List[Dict[str, Any]]) -> None:
    """Add education section."""
    if educations:
        lines.append("## Education")
        for edu in educations:
            lines.extend(_render_education(edu))
        lines.append("")


def _add_skills(lines: List[str], skills: List[Dict[str, Any]]) -> None:
    """Add skills section."""
    if skills:
        lines.append("## Skills")
        lines.extend(_render_skills(skills))
        lines.append("")


def _yaml_escape(value: str) -> str:
    return value.replace('"', "'").strip()
