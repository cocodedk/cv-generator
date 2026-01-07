"""Main CV tailoring logic."""

from __future__ import annotations

import logging
from typing import List, Optional

from backend.models import CVData, Experience, Project
from backend.services.ai.llm_client import get_llm_client
from backend.services.ai.llm_tailor.text_tailoring import _tailor_text
from backend.services.ai.llm_tailor.skill_reordering import _reorder_skills_for_jd

logger = logging.getLogger(__name__)


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

    if not llm_client.is_configured():
        raise ValueError(
            "LLM is not configured. Set AI_ENABLED=true and configure API credentials."
        )

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
                    technologies=project.technologies,  # Never change technologies
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
