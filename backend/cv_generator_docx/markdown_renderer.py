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
    contact_line = _render_contact_line(personal_info)
    if contact_line:
        lines.append(contact_line)
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


def _render_contact_line(personal_info: Dict[str, Any]) -> str:
    items: List[str] = []
    email = personal_info.get("email")
    if email:
        items.append(email)
    phone = personal_info.get("phone")
    if phone:
        items.append(phone)
    address = _format_address(personal_info.get("address"))
    if address:
        items.append(address)
    for key in ("linkedin", "github", "website"):
        value = personal_info.get(key)
        if value:
            items.append(value)
    return f"*{' | '.join(items)}*" if items else ""


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


def _render_experience(exp: Dict[str, Any]) -> List[str]:
    lines: List[str] = []
    title = exp.get("title", "")
    company = exp.get("company", "")
    heading = " - ".join([part for part in [title, company] if part])
    if heading:
        lines.append(f"### {heading}")
    dates = " - ".join(
        [part for part in [exp.get("start_date"), exp.get("end_date")] if part]
    )
    meta_parts = [part for part in [dates, exp.get("location")] if part]
    if meta_parts:
        lines.append(f"*{' | '.join(meta_parts)}*")
    description = exp.get("description") or ""
    desc_lines = _split_description(description)
    if len(desc_lines) > 1:
        lines.extend([f"- {line}" for line in desc_lines])
    elif desc_lines:
        lines.append(desc_lines[0])
    lines.append("")
    return lines


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
    skills_by_category: Dict[str, List[str]] = {}
    for skill in skills:
        category = skill.get("category") or "Other"
        skills_by_category.setdefault(category, []).append(skill.get("name", ""))

    for category, names in skills_by_category.items():
        lines.append(f"### {category}")
        for name in [value for value in names if value]:
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
