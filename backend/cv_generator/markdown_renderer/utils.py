"""Utility functions for markdown rendering."""

from typing import Dict, Any, List


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
    return str(value).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


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
