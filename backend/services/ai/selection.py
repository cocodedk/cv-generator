"""Selection logic for experiences/projects/highlights/skills."""

from __future__ import annotations

from typing import List, Tuple

from backend.models import Education, Experience, Project, Skill
from backend.services.ai.scoring import score_item, top_n_scored
from backend.services.ai.text import extract_words, word_set


def select_experiences(
    experiences: List[Experience],
    spec,
    max_experiences: int,
) -> Tuple[List[Experience], List[str]]:
    if not experiences:
        return [], ["Profile has no experiences; draft will be sparse."]

    scored: List[Tuple[float, Experience]] = []
    for experience in experiences:
        exp_score = score_item(
            text_parts=[
                experience.title,
                experience.company,
                experience.description or "",
            ],
            technologies=[
                tech for project in experience.projects for tech in project.technologies
            ],
            start_date=experience.start_date,
            spec=spec,
        ).value
        scored.append((exp_score, experience))

    top_experiences = [
        experience for _, experience in top_n_scored(scored, max_experiences)
    ]
    trimmed: List[Experience] = []
    for experience in top_experiences:
        projects = _select_projects(experience, spec, max_projects=2)
        trimmed.append(
            Experience(**experience.model_dump(exclude={"projects"}), projects=projects)
        )

    return trimmed, []


def _select_projects(experience: Experience, spec, max_projects: int) -> List[Project]:
    if not experience.projects:
        return []

    scored: List[Tuple[float, Project]] = []
    for project in experience.projects:
        score = score_item(
            text_parts=[project.name, project.description or "", *project.highlights],
            technologies=project.technologies,
            start_date=experience.start_date,
            spec=spec,
        ).value
        scored.append((score, project))

    top_projects = [project for _, project in top_n_scored(scored, max_projects)]
    trimmed: List[Project] = []
    for project in top_projects:
        highlights = _select_highlights(project, spec, max_highlights=3)
        trimmed.append(
            Project(**project.model_dump(exclude={"highlights"}), highlights=highlights)
        )
    return trimmed


def _select_highlights(project: Project, spec, max_highlights: int) -> List[str]:
    if not project.highlights:
        return []
    scored: List[Tuple[float, str]] = []
    for highlight in project.highlights:
        score = score_item(
            text_parts=[highlight],
            technologies=project.technologies,
            start_date="2023-01",
            spec=spec,
        ).value
        scored.append((score, highlight))
    return [highlight for _, highlight in top_n_scored(scored, max_highlights)]


def select_education(
    education: List[Education], spec, max_education: int
) -> List[Education]:
    if not education:
        return []
    scored: List[Tuple[float, Education]] = []
    for edu in education:
        score = score_item(
            text_parts=[edu.degree, edu.institution, edu.field or ""],
            technologies=[],
            start_date="2020-01",
            spec=spec,
        ).value
        scored.append((score, edu))
    return [edu for _, edu in top_n_scored(scored, max_education)]


def select_skills(
    skills: List[Skill], spec, selected_experiences: List[Experience]
) -> List[Skill]:
    if not skills:
        return []

    # Build set of words from selected experiences for bonus scoring
    selected_text = " ".join(
        [
            exp.title
            + " "
            + " ".join(
                [proj.name + " " + " ".join(proj.technologies) for proj in exp.projects]
            )
            for exp in selected_experiences
        ]
    )
    selected_words = set(extract_words(selected_text))

    # Normalize keywords by stripping trailing punctuation for consistent matching
    def normalize_keyword(word: str) -> str:
        """Remove trailing punctuation from keywords."""
        return word.rstrip(".,;:!?")

    normalized_required = {normalize_keyword(kw) for kw in spec.required_keywords}
    normalized_preferred = {normalize_keyword(kw) for kw in spec.preferred_keywords}
    normalized_selected = {normalize_keyword(kw) for kw in selected_words}

    scored: List[Tuple[float, Skill]] = []
    for skill in skills:
        # Extract words from skill name AND category
        skill_words = word_set([skill.name, skill.category or ""])
        # Normalize skill words too
        normalized_skill_words = {normalize_keyword(kw) for kw in skill_words}

        # Check membership in job description keywords
        matches_required = bool(normalized_skill_words & normalized_required)
        matches_preferred = bool(normalized_skill_words & normalized_preferred)
        appears_in_selected = bool(normalized_skill_words & normalized_selected)

        # Weighted scoring: JD match is primary (70%), experience bonus (30%)
        score = (
            0.5 * float(matches_required)
            + 0.2 * float(matches_preferred)
            + 0.3 * float(appears_in_selected)
        )
        scored.append((score, skill))

    # Select top 18 skills with score > 0, fallback to top by original order if none match
    selected = [skill for score, skill in top_n_scored(scored, 18) if score > 0.0]

    # Fallback: if no skills matched, return first 10 skills from profile
    if not selected and skills:
        selected = skills[:10]

    return selected
