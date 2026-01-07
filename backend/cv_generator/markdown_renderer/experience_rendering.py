"""Experience and project rendering functions."""

from typing import Dict, Any, List

from backend.cv_generator.markdown_renderer.utils import _split_description


def _render_experience(exp: Dict[str, Any]) -> List[str]:
    lines: List[str] = []
    _add_experience_header(lines, exp)
    _add_experience_meta(lines, exp)
    _add_experience_description(lines, exp.get("description") or "")
    _add_experience_projects(lines, exp.get("projects") or [])
    lines.append("")
    return lines


def _add_experience_header(lines: List[str], exp: Dict[str, Any]) -> None:
    """Add experience header with title and company."""
    title = exp.get("title", "")
    company = exp.get("company", "")
    heading = " - ".join([part for part in [title, company] if part])
    if heading:
        lines.append(f"### {heading}")


def _add_experience_meta(lines: List[str], exp: Dict[str, Any]) -> None:
    """Add experience metadata (dates and location)."""
    dates = " - ".join(
        [part for part in [exp.get("start_date"), exp.get("end_date")] if part]
    )
    meta_parts = [part for part in [dates, exp.get("location")] if part]
    if meta_parts:
        lines.append(f"*{' | '.join(meta_parts)}*")


def _add_experience_description(lines: List[str], description: str) -> None:
    """Add experience description."""
    desc_lines = _split_description(description)
    if len(desc_lines) > 1:
        lines.extend([f"- {line}" for line in desc_lines])
    elif desc_lines:
        lines.append(desc_lines[0])


def _add_experience_projects(lines: List[str], projects: List[Dict[str, Any]]) -> None:
    """Add experience projects."""
    for project in projects:
        _add_project_header(lines, project)
        _add_project_technologies(lines, project.get("technologies") or [])
        _add_project_highlights(lines, project.get("highlights") or [])


def _add_project_header(lines: List[str], project: Dict[str, Any]) -> None:
    """Add project header with name and description."""
    project_name = project.get("name") or ""
    project_desc = project.get("description") or ""
    project_heading = project_name
    if project_desc:
        project_heading = (
            f"{project_name} — {project_desc}" if project_name else project_desc
        )
    if project_heading:
        lines.append(f"**{project_heading}**")


def _add_project_technologies(lines: List[str], technologies: List[str]) -> None:
    """Add project technologies."""
    if technologies:
        lines.append(f"*Tech:* {', '.join(technologies)}")


def _add_project_highlights(lines: List[str], highlights: List[str]) -> None:
    """Add project highlights."""
    for highlight in highlights:
        if highlight:
            lines.append(f"- {highlight}")
