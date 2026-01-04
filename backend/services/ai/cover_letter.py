"""AI-powered cover letter generator from profile + job description."""

from __future__ import annotations

import logging
import re
from datetime import datetime
from pathlib import Path
from typing import List
from jinja2 import Environment, FileSystemLoader, select_autoescape

from backend.models import ProfileData
from backend.models_cover_letter import CoverLetterRequest, CoverLetterResponse
from backend.services.ai.llm_client import get_llm_client
from backend.services.ai.cover_letter_selection import select_relevant_content

logger = logging.getLogger(__name__)

TEMPLATES_DIR = Path(__file__).resolve().parent.parent.parent / "cv_generator" / "templates" / "cover_letter"


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


def _build_cover_letter_prompt(
    profile_summary: str,
    job_description: str,
    company_name: str,
    hiring_manager_name: str | None,
    tone: str,
    relevance_reasoning: str | None = None,
) -> str:
    """Build the LLM prompt for cover letter generation."""
    salutation = (
        f"Dear {hiring_manager_name},"
        if hiring_manager_name
        else "Dear Hiring Manager,"
    )

    tone_instructions = {
        "professional": "Use a formal, professional tone. Focus on achievements and qualifications.",
        "enthusiastic": "Use an energetic, positive tone while remaining professional. Show genuine excitement about the role.",
        "conversational": "Use a friendly, approachable tone. Be personable while maintaining professionalism.",
    }

    tone_guide = tone_instructions.get(tone, tone_instructions["professional"])

    reasoning_section = ""
    if relevance_reasoning:
        reasoning_section = f"\n\nRELEVANCE CONTEXT:\n{relevance_reasoning}\n\nThis explains why these specific experiences and skills were selected as most relevant to this role."

    prompt = f"""You are a professional cover letter writer. Generate a compelling cover letter based on the following information.

PROFILE INFORMATION:
{profile_summary}

JOB DESCRIPTION:
{job_description[:3000]}

COMPANY: {company_name}

SALUTATION: {salutation}

TONE: {tone_guide}{reasoning_section}

REQUIREMENTS:
1. Write a professional cover letter (3-4 paragraphs, approximately 300-400 words)
2. Opening paragraph: Hook that references the specific role and company
3. Body paragraphs (2-3): Match key achievements and skills from the profile to job requirements
4. Closing paragraph: Express enthusiasm and call to action
5. Use ONLY facts, achievements, and skills from the profile information above
6. DO NOT fabricate metrics, dates, or achievements not present in the profile
7. If specific information is missing, use general statements without making up details
8. Format the letter professionally with proper spacing

Return ONLY the cover letter body text (no header, date, or signature - those will be added separately). Start directly with the salutation and end with a professional closing like "Sincerely" or "Best regards"."""

    return prompt


async def generate_cover_letter(
    profile: ProfileData, request: CoverLetterRequest
) -> CoverLetterResponse:
    """
    Generate a tailored cover letter using LLM.

    Args:
        profile: User's saved profile data
        request: Cover letter generation request

    Returns:
        CoverLetterResponse with HTML and plain text versions

    Raises:
        ValueError: If LLM is not configured
    """
    llm_client = get_llm_client()

    if not llm_client.is_configured():
        raise ValueError(
            "LLM is not configured. Set AI_ENABLED=true and configure API credentials."
        )

    # Phase 1: Use LLM to select most relevant content
    try:
        selected_content = await select_relevant_content(
            profile=profile,
            job_description=request.job_description,
            llm_client=llm_client,
        )
    except Exception as e:
        logger.error(f"Failed to select relevant content: {e}", exc_info=True)
        raise ValueError(f"Failed to select relevant content: {str(e)}") from e

    # Filter profile to only selected items
    filtered_experiences = [
        profile.experience[idx] for idx in selected_content.experience_indices
    ]

    # Filter skills to only selected ones
    profile_skill_map = {s.name.lower(): s for s in profile.skills}
    filtered_skills = [
        profile_skill_map[skill_name.lower()]
        for skill_name in selected_content.skill_names
        if skill_name.lower() in profile_skill_map
    ]

    # Create filtered profile
    filtered_profile = ProfileData(
        personal_info=profile.personal_info,
        experience=filtered_experiences,
        education=profile.education,  # Keep all education for now
        skills=filtered_skills,
    )

    # Format filtered profile summary
    profile_summary = _format_profile_summary(filtered_profile)

    # Build prompt with relevance reasoning
    prompt = _build_cover_letter_prompt(
        profile_summary=profile_summary,
        job_description=request.job_description,
        company_name=request.company_name,
        hiring_manager_name=request.hiring_manager_name,
        tone=request.tone,
        relevance_reasoning=selected_content.relevance_reasoning,
    )

    # Phase 2: Generate cover letter body using LLM
    try:
        cover_letter_body = await llm_client.rewrite_text("", prompt)
        cover_letter_body = cover_letter_body.strip()
    except Exception as e:
        logger.error(f"Failed to generate cover letter: {e}", exc_info=True)
        raise ValueError(f"Failed to generate cover letter: {str(e)}") from e

    # Extract highlights used (from selected content)
    highlights_used = selected_content.key_highlights

    # Format as HTML
    cover_letter_html = _format_as_html(
        profile=profile,  # Use original profile for sender info
        cover_letter_body=cover_letter_body,
        company_name=request.company_name,
        hiring_manager_name=request.hiring_manager_name,
        company_address=request.company_address,
    )

    # Create plain text version
    cover_letter_text = _format_as_text(
        profile=profile,  # Use original profile for sender info
        cover_letter_body=cover_letter_body,
        company_name=request.company_name,
        hiring_manager_name=request.hiring_manager_name,
        company_address=request.company_address,
    )

    # Get selected experience names for response
    selected_experience_names = [
        profile.experience[idx].title
        for idx in selected_content.experience_indices
    ]

    return CoverLetterResponse(
        cover_letter_html=cover_letter_html,
        cover_letter_text=cover_letter_text,
        highlights_used=highlights_used,
        selected_experiences=selected_experience_names,
        selected_skills=selected_content.skill_names,
    )


def _extract_highlights_used(profile: ProfileData, job_description: str) -> List[str]:
    """Extract which profile highlights were likely used based on JD keywords."""
    highlights = []
    jd_lower = job_description.lower()

    # Check experience highlights
    for exp in profile.experience[:3]:
        for project in exp.projects[:2]:
            for highlight in project.highlights[:2]:
                # Simple keyword matching
                highlight_lower = highlight.lower()
                if any(word in jd_lower for word in highlight_lower.split()[:5]):
                    highlights.append(highlight)

    return highlights[:5]  # Limit to top 5


def _normalize_address(address: str) -> str:
    """
    Normalize address string by cleaning HTML breaks and newlines.

    Converts all line breaks (HTML <br> tags and newlines) to single <br> tags,
    and removes excessive breaks.
    """
    if not address:
        return ""

    # Replace HTML breaks (case-insensitive, with optional closing tag)
    # Replace <br>, <br/>, <br />, <BR>, etc. with newline
    address = re.sub(r'<br\s*/?>', '\n', address, flags=re.IGNORECASE)

    # Normalize multiple newlines to single newline
    address = re.sub(r'\n+', '\n', address)

    # Strip leading/trailing whitespace
    address = address.strip()

    # Convert single newlines to <br> tags
    address = address.replace('\n', '<br>')

    return address


def _format_as_html(
    profile: ProfileData,
    cover_letter_body: str,
    company_name: str,
    hiring_manager_name: str | None,
    company_address: str | None,
) -> str:
    """Format cover letter as HTML using Jinja2 template."""
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
    normalized_address = _normalize_address(company_address) if company_address else None

    # Load template
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=select_autoescape(["html", "xml"]),
    )
    template = env.get_template("ats.html")

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
        signature=profile.personal_info.name or "",
    )

    return html


def _strip_html_breaks(text: str) -> str:
    """Strip HTML break tags from text and convert to newlines."""
    if not text:
        return ""
    # Replace HTML breaks with newlines
    text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
    # Normalize multiple newlines
    text = re.sub(r'\n+', '\n', text)
    return text.strip()


def _format_as_text(
    profile: ProfileData,
    cover_letter_body: str,
    company_name: str,
    hiring_manager_name: str | None,
    company_address: str | None,
) -> str:
    """Format cover letter as plain text."""
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

    # Signature
    signature = profile.personal_info.name if profile.personal_info.name else ""

    text = f"""{sender_info}

{current_date}

{recipient_info}

{cover_letter_body}

{signature}"""

    return text
