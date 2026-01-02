"""Main markdown rendering function."""
from typing import Dict, Any, List
from backend.cv_generator.markdown_renderer.utils import yaml_escape
from backend.cv_generator.markdown_renderer.contact import render_contact_table
from backend.cv_generator.markdown_renderer.experience import render_experience
from backend.cv_generator.markdown_renderer.education import render_education
from backend.cv_generator.markdown_renderer.skills import render_skills


def render_markdown(cv_data: Dict[str, Any]) -> str:
    """Render CV data into Markdown."""
    lines: List[str] = []
    personal_info = cv_data.get("personal_info", {})
    add_header(lines, personal_info)
    add_contact_info(lines, personal_info)
    add_summary(lines, personal_info)
    add_experiences(lines, cv_data.get("experience", []))
    add_educations(lines, cv_data.get("education", []))
    add_skills(lines, cv_data.get("skills", []))
    content = "\n".join(lines).strip()
    return f"{content}\n" if content else ""


def add_header(lines: List[str], personal_info: Dict[str, Any]) -> None:
    """Add YAML front matter header."""
    name = personal_info.get("name")
    title = personal_info.get("title")
    if name or title:
        lines.append("---")
        if name:
            lines.append(f'title: "{yaml_escape(name)}"')
        if title:
            lines.append(f'subtitle: "{yaml_escape(title)}"')
        lines.append("---")
        lines.append("")


def add_contact_info(lines: List[str], personal_info: Dict[str, Any]) -> None:
    """Add contact information line."""
    contact_lines = render_contact_table(personal_info)
    if contact_lines:
        lines.extend(contact_lines)
    lines.append("")


def add_summary(lines: List[str], personal_info: Dict[str, Any]) -> None:
    """Add summary section."""
    summary = personal_info.get("summary")
    if summary:
        lines.extend(["## Summary", summary.strip(), ""])


def add_experiences(lines: List[str], experiences: List[Dict[str, Any]]) -> None:
    """Add experience section."""
    if experiences:
        lines.append("## Experience")
        for exp in experiences:
            lines.extend(render_experience(exp))
        lines.append("")


def add_educations(lines: List[str], educations: List[Dict[str, Any]]) -> None:
    """Add education section."""
    if educations:
        lines.append("## Education")
        for edu in educations:
            lines.extend(render_education(edu))
        lines.append("")


def add_skills(lines: List[str], skills: List[Dict[str, Any]]) -> None:
    """Add skills section."""
    if skills:
        lines.append("## Skills")
        lines.extend(render_skills(skills))
        lines.append("")
