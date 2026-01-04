"""LLM-powered CV tailoring that rewrites content to match job descriptions while preserving facts."""

from __future__ import annotations

import logging
import re
from typing import List, Optional

from backend.models import CVData, Experience, Project, Skill
from backend.services.ai.llm_client import get_llm_client

logger = logging.getLogger(__name__)

# Character limits for different CV fields (plain text, not HTML)
MAX_DESCRIPTION_CHARS = 280  # Leave buffer for the 300 char model limit
MAX_HIGHLIGHT_CHARS = 200


async def llm_tailor_cv(
    draft: CVData,
    job_description: str,
    original_profile: CVData,
    additional_context: Optional[str] = None,
) -> CVData:
    """
    Tailor CV content using LLM to better match job description.

    Rewords highlights, descriptions, and reorders skills while preserving
    all factual content from the original profile.

    Args:
        draft: The selected/reordered CV draft
        job_description: The job description to match against
        original_profile: Original profile for reference (to prevent hallucination)
        additional_context: Optional additional achievements or context to incorporate

    Returns:
        Tailored CV with reworded content
    """
    llm_client = get_llm_client()

    # If LLM is not configured, return draft unchanged with a warning logged
    if not llm_client.is_configured():
        logger.warning(
            "LLM not configured, skipping tailoring. Set AI_ENABLED=true and configure API."
        )
        return draft

    tailored_experiences: List[Experience] = []

    for experience in draft.experience:
        # Tailor experience description if present
        tailored_description = experience.description
        if experience.description:
            tailored_description = await _tailor_text(
                llm_client,
                experience.description,
                job_description,
                "experience description",
                additional_context,
            )

        # Tailor projects
        tailored_projects: List[Project] = []
        for project in experience.projects:
            # Tailor project description if present
            tailored_proj_description = project.description
            if project.description:
                tailored_proj_description = await _tailor_text(
                    llm_client,
                    project.description,
                    job_description,
                    "project description",
                    additional_context,
                )

            # Tailor highlights
            tailored_highlights: List[str] = []
            for highlight in project.highlights:
                tailored_highlight = await _tailor_text(
                    llm_client,
                    highlight,
                    job_description,
                    "bullet point",
                    additional_context,
                )
                tailored_highlights.append(tailored_highlight)

            tailored_projects.append(
                Project(
                    name=project.name,
                    description=tailored_proj_description,
                    highlights=tailored_highlights,
                    technologies=project.technologies,  # Keep technologies as-is
                    url=project.url,
                )
            )

        tailored_experiences.append(
            Experience(
                title=experience.title,
                company=experience.company,
                start_date=experience.start_date,
                end_date=experience.end_date,
                description=tailored_description,
                location=experience.location,
                projects=tailored_projects,
            )
        )

    # Reorder skills to prioritize JD-relevant ones (keep all skills, just reorder)
    tailored_skills = _reorder_skills_for_jd(draft.skills, job_description)

    return CVData(
        personal_info=draft.personal_info,
        experience=tailored_experiences,
        education=draft.education,
        skills=tailored_skills,
        theme=draft.theme,
    )


def _strip_html(text: str) -> str:
    """Strip HTML tags and decode entities to get plain text length."""
    plain = re.sub(r"<[^>]+>", "", text)
    plain = plain.replace("&nbsp;", " ")
    plain = plain.replace("&amp;", "&")
    plain = plain.replace("&lt;", "<")
    plain = plain.replace("&gt;", ">")
    plain = plain.replace("&quot;", '"')
    plain = plain.replace("&#39;", "'")
    plain = re.sub(r"&#(\d+);", lambda m: chr(int(m.group(1))), plain)
    return plain


def _get_max_chars(context: str) -> Optional[int]:
    """Get max character limit based on context type."""
    if "description" in context:
        return MAX_DESCRIPTION_CHARS
    elif "bullet" in context or "highlight" in context:
        return MAX_HIGHLIGHT_CHARS
    return None


async def _tailor_text(
    llm_client,
    original_text: str,
    job_description: str,
    context: str,
    additional_context: Optional[str] = None,
) -> str:
    """
    Tailor a single piece of text using LLM.

    Args:
        llm_client: Configured LLM client
        original_text: Text to tailor
        job_description: Job description context
        context: Description of what this text is (for error handling)
        additional_context: Optional additional achievements or context to incorporate

    Returns:
        Tailored text, or original if tailoring fails
    """
    if not original_text or not original_text.strip():
        return original_text

    max_chars = _get_max_chars(context)
    length_instruction = ""
    if max_chars:
        length_instruction = f"\n- Keep the rewritten text under {max_chars} characters (CRITICAL - do not exceed this limit)"

    additional_context_section = ""
    if additional_context and additional_context.strip():
        additional_context_section = f"""

Additional achievements/context to incorporate:
{additional_context[:1000]}
"""

    user_prompt = f"""Job Description:
{job_description[:2000]}{additional_context_section}

Original {context}:
{original_text}

CRITICAL: Reword the {context} above to better match the job description.

RULES:
- Use ONLY facts, metrics, technologies, and achievements that appear in the original text above
- You may rephrase and reorder emphasis, but DO NOT add anything new
- If the original says "improved performance", do NOT say "improved performance by 30%"
- If you cannot tailor without adding new claims, return the original text unchanged{length_instruction}

Return ONLY the reworded text, no explanations."""

    try:
        tailored = await llm_client.rewrite_text(original_text, user_prompt)
        # Validate that we got something back
        if not tailored or not tailored.strip():
            logger.warning(f"LLM returned empty result for {context}, using original")
            return original_text

        tailored = tailored.strip()

        # Validate length constraint - if exceeded, fall back to original
        if max_chars:
            plain_length = len(_strip_html(tailored))
            if plain_length > max_chars + 20:  # Small buffer for minor overruns
                logger.warning(
                    f"LLM result for {context} exceeds limit ({plain_length} > {max_chars}), using original"
                )
                return original_text

        return tailored
    except Exception as e:
        logger.error(f"Failed to tailor {context}: {e}", exc_info=True)
        return original_text  # Fallback to original on error


def _reorder_skills_for_jd(skills: List[Skill], job_description: str) -> List[Skill]:
    """
    Reorder skills list to prioritize JD-relevant skills.

    Uses simple keyword matching - skills mentioned in JD come first.
    This is a heuristic approach that doesn't require LLM.

    Args:
        skills: List of skills to reorder
        job_description: Job description text

    Returns:
        Reordered skills list
    """
    if not skills:
        return skills

    jd_lower = job_description.lower()

    # Score each skill by JD relevance
    scored_skills: List[tuple[float, Skill]] = []
    for skill in skills:
        skill_name_lower = skill.name.lower()
        # Check if skill name appears in JD
        score = 1.0 if skill_name_lower in jd_lower else 0.0
        # Bonus for category match
        if skill.category and skill.category.lower() in jd_lower:
            score += 0.5
        scored_skills.append((score, skill))

    # Sort by score (descending), then by original order for ties
    scored_skills.sort(key=lambda x: (-x[0], skills.index(x[1])))

    return [skill for _, skill in scored_skills]
