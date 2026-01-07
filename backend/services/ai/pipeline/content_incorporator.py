"""Step 6: Incorporate additional_context into CV based on intelligent analysis."""

import logging
from typing import List
from backend.models import CVData, Experience, Project, PersonalInfo
from backend.services.ai.pipeline.models import ContextAnalysis, ContextIncorporation

logger = logging.getLogger(__name__)


def incorporate_context(
    cv_data: CVData,
    context_analysis: ContextAnalysis,
    selected_experiences: List[Experience],
) -> CVData:
    """
    Incorporate additional_context into CV based on intelligent analysis.

    Args:
        cv_data: Current CV data
        context_analysis: Analysis of how to incorporate the context
        selected_experiences: List of experiences selected for the CV

    Returns:
        Updated CVData with context incorporated
    """
    if context_analysis.type == "directive" or context_analysis.placement == "adaptation_guidance":
        # Directives are handled during adaptation, nothing to incorporate here
        logger.debug("Context is a directive, no content incorporation needed")
        return cv_data

    incorporation = _build_incorporation(context_analysis, selected_experiences)
    return _apply_incorporation(cv_data, incorporation)


def _build_incorporation(
    context_analysis: ContextAnalysis,
    selected_experiences: List[Experience],
) -> ContextIncorporation:
    """Build incorporation instructions from context analysis."""
    incorporation = ContextIncorporation()

    if context_analysis.placement == "summary":
        incorporation = ContextIncorporation(
            summary_update=context_analysis.suggested_text,
            project_highlights=[],
            experience_updates={}
        )
        logger.info(f"Incorporating context into summary: {context_analysis.suggested_text[:100]}...")

    elif context_analysis.placement == "project_highlight":
        # Find the most relevant project to add the highlight to
        # Default to first experience, first project if available
        exp_idx = 0
        proj_idx = 0
        if selected_experiences and selected_experiences[0].projects:
            incorporation = ContextIncorporation(
                summary_update=None,
                project_highlights=[(exp_idx, proj_idx, context_analysis.suggested_text)],
                experience_updates={}
            )
            logger.info(f"Incorporating context as project highlight: {context_analysis.suggested_text[:100]}...")
        else:
            # No projects available, fallback to summary
            logger.warning("No projects available, falling back to summary placement")
            incorporation = ContextIncorporation(
                summary_update=context_analysis.suggested_text,
                project_highlights=[],
                experience_updates={}
            )

    elif context_analysis.placement == "experience_description":
        # Add to first experience description
        if selected_experiences:
            exp_idx = 0
            current_desc = selected_experiences[exp_idx].description or ""
            # Integrate the suggested text with existing description
            if current_desc:
                updated_desc = f"{current_desc}\n\n{context_analysis.suggested_text}"
            else:
                updated_desc = context_analysis.suggested_text
            incorporation = ContextIncorporation(
                summary_update=None,
                project_highlights=[],
                experience_updates={exp_idx: updated_desc}
            )
            logger.info(f"Incorporating context into experience description: {context_analysis.suggested_text[:100]}...")
        else:
            # No experiences, fallback to summary
            logger.warning("No experiences available, falling back to summary placement")
            incorporation = ContextIncorporation(
                summary_update=context_analysis.suggested_text,
                project_highlights=[],
                experience_updates={}
            )

    return incorporation


def _apply_incorporation(
    cv_data: CVData,
    incorporation: ContextIncorporation,
) -> CVData:
    """Apply incorporation instructions to CV data."""
    # Update summary if provided
    updated_personal_info = cv_data.personal_info
    if incorporation.summary_update:
        current_summary = updated_personal_info.summary or ""
        if current_summary:
            # Append to existing summary
            updated_summary = f"{current_summary}\n\n{incorporation.summary_update}"
        else:
            # Create new summary
            updated_summary = incorporation.summary_update

        updated_personal_info = PersonalInfo(
            name=updated_personal_info.name,
            title=updated_personal_info.title,
            email=updated_personal_info.email,
            phone=updated_personal_info.phone,
            address=updated_personal_info.address,
            linkedin=updated_personal_info.linkedin,
            github=updated_personal_info.github,
            website=updated_personal_info.website,
            summary=updated_summary,
            photo=updated_personal_info.photo,
        )

    # Update experiences
    updated_experiences = list(cv_data.experience)

    # Apply experience description updates
    for exp_idx, updated_desc in incorporation.experience_updates.items():
        if exp_idx < len(updated_experiences):
            exp = updated_experiences[exp_idx]
            updated_experiences[exp_idx] = Experience(
                title=exp.title,
                company=exp.company,
                start_date=exp.start_date,
                end_date=exp.end_date,
                description=updated_desc,
                location=exp.location,
                projects=exp.projects,
            )

    # Apply project highlight additions
    for exp_idx, proj_idx, highlight_text in incorporation.project_highlights:
        if exp_idx < len(updated_experiences):
            exp = updated_experiences[exp_idx]
            if proj_idx < len(exp.projects):
                proj = exp.projects[proj_idx]
                updated_highlights = list(proj.highlights) + [highlight_text]
                updated_projects = list(exp.projects)
                updated_projects[proj_idx] = Project(
                    name=proj.name,
                    description=proj.description,
                    highlights=updated_highlights,
                    technologies=proj.technologies,
                    url=proj.url,
                )
                updated_experiences[exp_idx] = Experience(
                    title=exp.title,
                    company=exp.company,
                    start_date=exp.start_date,
                    end_date=exp.end_date,
                    description=exp.description,
                    location=exp.location,
                    projects=updated_projects,
                )

    # Return updated CV data
    return CVData(
        personal_info=updated_personal_info,
        experience=updated_experiences,
        education=cv_data.education,
        skills=cv_data.skills,
        theme=cv_data.theme,
        layout=cv_data.layout,
        target_company=cv_data.target_company,
        target_role=cv_data.target_role,
    )
