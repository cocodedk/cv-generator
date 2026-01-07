"""Cover letter formatting utilities for HTML and text output."""

from datetime import datetime
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape

from backend.models import ProfileData

TEMPLATES_DIR = (
    Path(__file__).resolve().parent.parent.parent.parent
    / "cv_generator"
    / "templates"
    / "cover_letter"
)


def _format_profile_summary(profile: ProfileData) -> str:  # noqa: C901
    """Format profile data into a summary for LLM context."""
    lines = []

    # Personal info
    if profile.personal_info.name:
        lines.append(f"Name: {profile.personal_info.name}")
    if profile.personal_info.title:
        lines.append(f"Title: {profile.personal_info.title}")

    # Experience highlights (data is pre-filtered, use all items)
    if profile.experience:
        lines.append("\nExperience:")
        for exp in profile.experience:
            exp_lines = [f"  - {exp.title} at {exp.company}"]
            if exp.description:
                exp_lines.append(f"    Description: {exp.description}")
            for project in exp.projects:
                if project.name:
                    exp_lines.append(f"    Project: {project.name}")
                if project.highlights:
                    for highlight in project.highlights:
                        exp_lines.append(f"      • {highlight}")
            lines.extend(exp_lines)

    # Education (data is pre-filtered, use all items)
    if profile.education:
        lines.append("\nEducation:")
        for edu in profile.education:
            edu_line = f"  - {edu.degree}"
            if edu.institution:
                edu_line += f" from {edu.institution}"
            if edu.year:
                edu_line += f" ({edu.year})"
            lines.append(edu_line)

    # Skills (data is pre-filtered, use all items)
    if profile.skills:
        skill_names = [s.name for s in profile.skills]
        lines.append(f"\nSkills: {', '.join(skill_names)}")

    return "\n".join(lines)


def _format_as_html(
    profile: ProfileData,
    cover_letter_body: str,
    company_name: str,
    hiring_manager_name: str | None,
    company_address: str | None,
) -> str:
    """Format cover letter as HTML using Jinja2 template."""
    from backend.services.ai.cover_letter.address_utils import _normalize_address

    # Get current date
    current_date = datetime.now().strftime("%B %d, %Y")

    # Format sender address
    sender_address = None
    if profile.personal_info.address:
        addr = profile.personal_info.address
        addr_parts = [
            addr.street,
            addr.city,
            addr.state,
            addr.zip,
            addr.country,
        ]
        sender_address = ", ".join(filter(None, addr_parts))

    # Format body (convert paragraphs to HTML)
    body_html = cover_letter_body.replace("\n\n", "</p><p>").replace("\n", "<br>")
    if not body_html.startswith("<p>"):
        body_html = f"<p>{body_html}</p>"

    # Normalize company address (strip HTML breaks and normalize)
    normalized_address = (
        _normalize_address(company_address) if company_address else None
    )

    # Load template
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=select_autoescape(["html", "xml"]),
    )
    template = env.get_template("ats.html")

    # Signature - only add if not already in the closing
    signature = ""
    if profile.personal_info.name:
        # Check if the cover letter body already ends with the name
        body_lower = cover_letter_body.lower()
        name_lower = profile.personal_info.name.lower()
        if not body_lower.endswith(name_lower):
            signature = profile.personal_info.name

    html = template.render(
        sender_name=profile.personal_info.name,
        sender_title=profile.personal_info.title,
        sender_email=profile.personal_info.email,
        sender_phone=profile.personal_info.phone,
        sender_address=sender_address,
        date=current_date,
        hiring_manager_name=hiring_manager_name,
        company_name=company_name,
        company_address=normalized_address,
        cover_letter_body=body_html,
        signature=signature,
    )

    return html


def _format_as_text(  # noqa: C901
    profile: ProfileData,
    cover_letter_body: str,
    company_name: str,
    hiring_manager_name: str | None,
    company_address: str | None,
) -> str:
    """Format cover letter as plain text."""
    from backend.services.ai.cover_letter.address_utils import _strip_html_breaks

    # Get current date
    current_date = datetime.now().strftime("%B %d, %Y")

    # Format sender info
    sender_lines = []
    if profile.personal_info.name:
        sender_lines.append(profile.personal_info.name)
    if profile.personal_info.title:
        sender_lines.append(profile.personal_info.title)
    if profile.personal_info.email:
        sender_lines.append(profile.personal_info.email)
    if profile.personal_info.phone:
        sender_lines.append(profile.personal_info.phone)
    if profile.personal_info.address:
        addr = profile.personal_info.address
        addr_parts = [
            addr.street,
            addr.city,
            addr.state,
            addr.zip,
            addr.country,
        ]
        addr_line = ", ".join(filter(None, addr_parts))
        if addr_line:
            sender_lines.append(addr_line)

    sender_info = "\n".join(sender_lines)

    # Format recipient info
    recipient_lines = []
    if hiring_manager_name:
        recipient_lines.append(hiring_manager_name)
    recipient_lines.append(company_name)
    if company_address:
        # Strip HTML breaks and split into lines
        clean_address = _strip_html_breaks(company_address)
        if clean_address:
            recipient_lines.append(clean_address)
    recipient_info = "\n".join(recipient_lines)

    # Signature - only add if not already in the closing
    signature = ""
    if profile.personal_info.name:
        # Check if the cover letter body already ends with the name
        body_lower = cover_letter_body.lower()
        name_lower = profile.personal_info.name.lower()
        if not body_lower.endswith(name_lower):
            signature = profile.personal_info.name

    text = f"""{sender_info}

{current_date}

{recipient_info}

{cover_letter_body}

{signature}"""

    return text
