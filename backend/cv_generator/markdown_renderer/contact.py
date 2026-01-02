"""Contact information rendering."""
from typing import Dict, Any, List
from backend.cv_generator.markdown_renderer.utils import escape_html, format_address


def render_contact_table(personal_info: Dict[str, Any]) -> List[str]:
    """Render contact information with Unicode icons."""
    lines: List[str] = []
    email = personal_info.get("email")
    if email:
        lines.append(f'<p style="font-size: 9pt;">✉ {escape_html(email)}</p>')
    phone = personal_info.get("phone")
    if phone:
        lines.append(f'<p style="font-size: 9pt;">☎ {escape_html(phone)}</p>')
    address = format_address(personal_info.get("address"))
    if address:
        lines.append(f'<p style="font-size: 9pt;">📍 {escape_html(address)}</p>')
    linkedin = personal_info.get("linkedin")
    if linkedin:
        lines.append(f'<p style="font-size: 9pt;">🔗 {escape_html(linkedin)}</p>')
    github = personal_info.get("github")
    if github:
        lines.append(f'<p style="font-size: 9pt;">💻 {escape_html(github)}</p>')
    website = personal_info.get("website")
    if website:
        lines.append(f'<p style="font-size: 9pt;">🌐 {escape_html(website)}</p>')
    return lines
