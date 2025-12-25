"""Render CV data into Markdown for DOCX conversion."""
from typing import Dict, Any, List


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


def _render_contact_table(personal_info: Dict[str, Any]) -> List[str]:
    """Render contact information with Unicode icons."""
    lines: List[str] = []
    email = personal_info.get("email")
    if email:
        lines.append(f'<p style="font-size: 9pt;">✉ {_escape_html(email)}</p>')
    phone = personal_info.get("phone")
    if phone:
        lines.append(f'<p style="font-size: 9pt;">☎ {_escape_html(phone)}</p>')
    address = _format_address(personal_info.get("address"))
    if address:
        lines.append(f'<p style="font-size: 9pt;">📍 {_escape_html(address)}</p>')
    linkedin = personal_info.get("linkedin")
    if linkedin:
        lines.append(f'<p style="font-size: 9pt;">🔗 {_escape_html(linkedin)}</p>')
    github = personal_info.get("github")
    if github:
        lines.append(f'<p style="font-size: 9pt;">💻 {_escape_html(github)}</p>')
    website = personal_info.get("website")
    if website:
        lines.append(f'<p style="font-size: 9pt;">🌐 {_escape_html(website)}</p>')
    return lines


def _format_address(address: Any) -> str:
    if not address:
        return ""
    if isinstance(address, str):
        return address
    parts = [
        address.get("street"),
        address.get("city"),
        address.get("state"),
        address.get("zip"),
        address.get("country"),
    ]
    return ", ".join([part for part in parts if part])


def _escape_html(value: str) -> str:
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


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
        project_heading = f"{project_name} — {project_desc}" if project_name else project_desc
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


def _render_education(edu: Dict[str, Any]) -> List[str]:
    lines: List[str] = []
    degree = edu.get("degree", "")
    institution = edu.get("institution", "")
    heading = ", ".join([part for part in [degree, institution] if part])
    if heading:
        lines.append(f"### {heading}")
    info_parts = [
        edu.get("year"),
        edu.get("field"),
        f"GPA: {edu['gpa']}" if edu.get("gpa") else None,
    ]
    info = " | ".join([part for part in info_parts if part])
    if info:
        lines.append(info)
    lines.append("")
    return lines


def _render_skills(skills: List[Dict[str, Any]]) -> List[str]:
    lines: List[str] = []
    skills_by_category: Dict[str, List[Dict[str, str]]] = {}
    for skill in skills:
        category = skill.get("category") or "Other"
        name = skill.get("name", "")
        if name:
            skill_obj = {"name": name}
            level = skill.get("level")
            if level:
                skill_obj["level"] = level
            skills_by_category.setdefault(category, []).append(skill_obj)

    for category, skill_list in skills_by_category.items():
        lines.append(f"### {category}")
        for skill in skill_list:
            name = skill.get("name", "")
            level = skill.get("level")
            if level:
                lines.append(f"- {name} ({level})")
            else:
                lines.append(f"- {name}")
        lines.append("")
    return lines


def _split_description(description: str) -> List[str]:
    if not description:
        return []
    lines = []
    for line in description.splitlines():
        clean = line.strip().lstrip("-*").strip()
        if clean:
            lines.append(clean)
    return lines


def _yaml_escape(value: str) -> str:
    return value.replace('"', "'").strip()
