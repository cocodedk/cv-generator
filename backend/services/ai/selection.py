"""Selection logic for experiences/projects/highlights/skills."""

from __future__ import annotations

from typing import List, Tuple

from backend.models import Education, Experience, Project, Skill
from backend.services.ai.scoring import score_item, top_n_scored
from backend.services.ai.text import extract_words, word_set, tech_terms_match


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

    required_keywords = list(spec.required_keywords)
    preferred_keywords = list(spec.preferred_keywords)

    # Extract responsibility words for support detection
    responsibility_words = set()
    if hasattr(spec, 'responsibilities'):
        for resp in spec.responsibilities:
            responsibility_words.update(extract_words(resp))

    scored: List[Tuple[float, Skill]] = []
    for skill in skills:
        skill_words = word_set([skill.name, skill.category or ""])

        # Direct matches (exact or synonym)
        matches_required = any(
            tech_terms_match(skill.name, kw) for kw in required_keywords
        )
        matches_preferred = any(
            tech_terms_match(skill.name, kw) for kw in preferred_keywords
        )

        # Ecosystem/related matches: skill words overlap with JD keywords but not exact match
        ecosystem_match = False
        if not matches_required and not matches_preferred:
            skill_normalized = skill.name.lower()
            # Check for partial matches or word overlaps
            for kw in required_keywords + preferred_keywords:
                kw_normalized = kw.lower()
                if (skill_normalized in kw_normalized or kw_normalized in skill_normalized) and skill_normalized != kw_normalized:
                    ecosystem_match = True
                    break
                # Check word overlap
                kw_words = set(extract_words(kw))
                if skill_words & kw_words:
                    ecosystem_match = True
                    break

        # Responsibility support: skill words overlap with responsibility words
        responsibility_support = bool(skill_words & responsibility_words) if responsibility_words else False

        # Check if skill appears in selected experiences
        appears_in_selected = bool(skill_words & selected_words)

        # Updated weighted scoring:
        # 40% required direct match, 15% preferred direct match,
        # 25% ecosystem/related match, 10% responsibility support, 10% experience
        score = (
            0.40 * float(matches_required)
            + 0.15 * float(matches_preferred)
            + 0.25 * float(ecosystem_match)
            + 0.10 * float(responsibility_support)
            + 0.10 * float(appears_in_selected)
        )
        scored.append((score, skill))

    # Select top 18 skills with score > 0, fallback to top by original order if none match
    selected = [skill for score, skill in top_n_scored(scored, 18) if score > 0.0]

    # Fallback: if no skills matched, return first 10 skills from profile
    if not selected and skills:
        selected = skills[:10]

    return selected
