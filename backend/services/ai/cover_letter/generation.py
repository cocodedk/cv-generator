"""Main cover letter generation logic."""

from __future__ import annotations

import logging

from backend.models import ProfileData
from backend.models_cover_letter import CoverLetterRequest, CoverLetterResponse
from backend.services.ai.llm_client import get_llm_client
from backend.services.ai.cover_letter_selection import select_relevant_content
from backend.services.ai.cover_letter.formatting import _format_profile_summary, _format_as_html, _format_as_text
from backend.services.ai.cover_letter.prompt_builder import _build_cover_letter_prompt

logger = logging.getLogger(__name__)


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
        llm_instructions=request.llm_instructions,
    )

    # Phase 2: Generate cover letter body using LLM
    try:
        cover_letter_body = await llm_client.generate_text(
            prompt,
            system_prompt="You are a professional cover letter writer. Generate compelling, tailored cover letters."
        )
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
        profile.experience[idx].title for idx in selected_content.experience_indices
    ]

    return CoverLetterResponse(
        cover_letter_html=cover_letter_html,
        cover_letter_text=cover_letter_text,
        highlights_used=highlights_used,
        selected_experiences=selected_experience_names,
        selected_skills=selected_content.skill_names,
    )
