"""Experience and project reconstruction logic."""

import logging
from typing import Dict, Tuple, List

from backend.models import Experience, Project

logger = logging.getLogger(__name__)


def _reconstruct_project(
    project: Project,
    exp_idx: int,
    proj_idx: int,
    adapted_text_map: Dict[Tuple[str, str, str, str], Tuple[str, str | None]],
) -> Project:
    """Reconstruct a project with adapted content."""
    # Get adapted project description
    adapted_proj_desc = project.description
    proj_desc_key = ("proj_desc", str(exp_idx), str(proj_idx), "")
    if proj_desc_key in adapted_text_map:
        adapted_proj_desc, _ = adapted_text_map[proj_desc_key]
        logger.debug(f"    Project description adapted: {len(project.description)} → {len(adapted_proj_desc)} chars")

    # Get adapted highlights
    adapted_highlights: List[str] = []
    for hl_idx, highlight in enumerate(project.highlights):
        hl_key = ("highlight", str(exp_idx), str(proj_idx), str(hl_idx))
        if hl_key in adapted_text_map:
            adapted_hl, _ = adapted_text_map[hl_key]
            adapted_highlights.append(adapted_hl)
        else:
            adapted_highlights.append(highlight)  # Fallback

    return Project(
        name=project.name,
        description=adapted_proj_desc,
        highlights=adapted_highlights,
        technologies=project.technologies,  # Never change technologies
        url=project.url,
    )


def _reconstruct_experience(
    exp: Experience,
    exp_idx: int,
    adapted_text_map: Dict[Tuple[str, str, str, str], Tuple[str, str | None]],
    adaptation_notes: Dict[str, str],
) -> Experience:
    """Reconstruct an experience with adapted content."""
    logger.debug(f"Reconstructing experience {exp_idx+1}: {exp.title} at {exp.company}")

    # Get adapted description
    adapted_description = exp.description
    desc_key = ("exp_desc", str(exp_idx), "", "")
    if desc_key in adapted_text_map:
        adapted_description, error = adapted_text_map[desc_key]
        if adapted_description != exp.description:
            logger.info(f"  Description adapted: {len(exp.description)} → {len(adapted_description)} chars")
            adaptation_notes[f"{exp.company}_description"] = "Reworded to match JD terminology"

    # Reconstruct projects with adapted content
    adapted_projects = []
    for proj_idx, project in enumerate(exp.projects):
        adapted_projects.append(_reconstruct_project(project, exp_idx, proj_idx, adapted_text_map))

    return Experience(
        title=exp.title,
        company=exp.company,
        start_date=exp.start_date,
        end_date=exp.end_date,
        description=adapted_description,
        location=exp.location,
        projects=adapted_projects,
    )
