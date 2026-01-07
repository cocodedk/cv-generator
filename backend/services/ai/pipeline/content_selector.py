"""Step 3: Select relevant content from profile based on JD requirements."""

import logging
from typing import List, Dict, Optional
from backend.models import Experience, Project
from backend.services.ai.pipeline.models import JDAnalysis, SkillMapping, SelectionResult
from backend.services.ai.scoring import score_item, top_n_scored

logger = logging.getLogger(__name__)


def select_content(
    profile_experiences: List[Experience],
    jd_analysis: JDAnalysis,
    skill_mapping: SkillMapping,
    max_experiences: int = 4,
    additional_context: Optional[str] = None,
) -> SelectionResult:
    """
    Select relevant experiences, projects, and highlights from profile.

    Only selects from existing profile content - never creates new content.

    Args:
        profile_experiences: All experiences from user's profile
        jd_analysis: Analyzed JD requirements (already influenced by additional_context if provided)
        skill_mapping: Mapped skills (already influenced by additional_context if provided)
        max_experiences: Maximum number of experiences to include
        additional_context: Optional directive to guide selection (e.g., "enterprise-focused").
                           Note: Primary influence comes through jd_analysis and skill_mapping
                           which are already filtered by this directive in earlier pipeline steps.

    Returns:
        SelectionResult with selected content and indices
    """
    if not profile_experiences:
        return SelectionResult(experiences=[], selected_indices={})

    # Build a simple spec-like object for scoring compatibility
    class SimpleSpec:
        def __init__(self, jd: JDAnalysis):
            self.required_keywords = jd.required_skills
            self.preferred_keywords = jd.preferred_skills
            self.responsibilities = jd.responsibilities

    spec = SimpleSpec(jd_analysis)

    # Score and select experiences
    scored_experiences: List[tuple[float, Experience]] = []
    for exp in profile_experiences:
        # Score based on how well it matches JD requirements
        score = score_item(
            text_parts=[
                exp.title,
                exp.company,
                exp.description or "",
            ],
            technologies=[
                tech for project in exp.projects for tech in project.technologies
            ],
            start_date=exp.start_date,
            spec=spec,
        ).value
        scored_experiences.append((score, exp))

    # Select top experiences
    top_experiences = [
        exp for _, exp in top_n_scored(scored_experiences, max_experiences)
    ]

    # For each selected experience, select relevant projects and highlights
    selected_experiences: List[Experience] = []
    selected_indices: Dict[str, List[int]] = {}

    for exp in top_experiences:
        # Select projects (max 2 per experience)
        selected_projects = _select_projects(exp, spec, max_projects=2)

        # Build selected_indices mapping (for traceability)
        exp_id = f"{exp.company}_{exp.title}"
        project_indices = []
        highlight_indices_map: Dict[int, List[int]] = {}

        # Create a set of selected project names for comparison
        selected_project_names = {p.name for p in selected_projects}

        for idx, project in enumerate(exp.projects):
            if project.name in selected_project_names:
                project_indices.append(idx)
                # Select highlights for this project
                selected_highlights = _select_highlights(project, spec, max_highlights=3)
                highlight_indices = [
                    hl_idx for hl_idx, hl in enumerate(project.highlights)
                    if hl in selected_highlights
                ]
                highlight_indices_map[idx] = highlight_indices

        selected_indices[exp_id] = {
            "projects": project_indices,
            "highlights": highlight_indices_map,
        }

        # Create trimmed experience with selected projects
        trimmed_projects: List[Project] = []
        for project in selected_projects:
            selected_highlights = _select_highlights(project, spec, max_highlights=3)
            trimmed_project = Project(
                name=project.name,
                description=project.description,
                highlights=selected_highlights,
                technologies=project.technologies,
                url=project.url,
            )
            trimmed_projects.append(trimmed_project)

        trimmed_exp = Experience(
            title=exp.title,
            company=exp.company,
            start_date=exp.start_date,
            end_date=exp.end_date,
            description=exp.description,
            location=exp.location,
            projects=trimmed_projects,
        )
        selected_experiences.append(trimmed_exp)

    return SelectionResult(
        experiences=selected_experiences,
        selected_indices=selected_indices,
    )


def _select_projects(experience: Experience, spec, max_projects: int) -> List[Project]:
    """Select relevant projects from an experience."""
    if not experience.projects:
        return []

    scored: List[tuple[float, Project]] = []
    for project in experience.projects:
        score = score_item(
            text_parts=[project.name, project.description or "", *project.highlights],
            technologies=project.technologies,
            start_date=experience.start_date,
            spec=spec,
        ).value
        scored.append((score, project))

    return [project for _, project in top_n_scored(scored, max_projects)]


def _select_highlights(project: Project, spec, max_highlights: int) -> List[str]:
    """Select relevant highlights from a project."""
    if not project.highlights:
        return []

    scored: List[tuple[float, str]] = []
    for highlight in project.highlights:
        score = score_item(
            text_parts=[highlight],
            technologies=project.technologies,
            start_date="2023-01",
            spec=spec,
        ).value
        scored.append((score, highlight))

    return [highlight for _, highlight in top_n_scored(scored, max_highlights)]
