"""Skill reordering utilities."""

from typing import List

from backend.models import Skill


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
