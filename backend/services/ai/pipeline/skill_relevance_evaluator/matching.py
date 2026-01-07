"""Skill matching logic for JD requirements."""

import logging
import re
from typing import List

from backend.models import Skill
from backend.services.ai.pipeline.models import SkillMatch
from backend.services.ai.text import tech_terms_match

logger = logging.getLogger(__name__)


def _skill_in_raw_jd(skill_name: str, raw_jd: str) -> bool:
    """
    Check if skill name appears literally in JD text.

    Uses word boundary matching to avoid false positives like "Java" in "JavaScript".
    """
    jd_lower = raw_jd.lower()
    skill_lower = skill_name.lower()

    # Word boundary match
    pattern = r'\b' + re.escape(skill_lower) + r'\b'
    return bool(re.search(pattern, jd_lower))


def _match_skills_in_raw_jd(
    profile_skills: List[Skill],
    raw_jd: str,
    selected_skill_names: set[str],
) -> List[SkillMatch]:
    """LAYER 1: Check raw JD text for literal skill matches."""
    matched_skills_list: List[SkillMatch] = []
    for skill in profile_skills:
        if skill.name in selected_skill_names:
            continue

        if _skill_in_raw_jd(skill.name, raw_jd):
            logger.info(f"Raw JD match: '{skill.name}' found in job description")
            match = SkillMatch(
                profile_skill=skill,
                jd_requirement=skill.name,  # Self-reference for raw matches
                match_type="exact",
                confidence=0.98,
                explanation=f"'{skill.name}' appears directly in job description",
            )
            matched_skills_list.append(match)
            selected_skill_names.add(skill.name)
    return matched_skills_list


def _match_skills_to_requirements(
    profile_skills: List[Skill],
    all_jd_requirements: List[str],
    selected_skill_names: set[str],
) -> List[SkillMatch]:
    """LAYER 2: Check against extracted JD requirements using tech_terms_match."""
    matched_skills_list: List[SkillMatch] = []
    for skill in profile_skills:
        if skill.name in selected_skill_names:
            continue

        for req in all_jd_requirements:
            if tech_terms_match(skill.name, req):
                logger.info(f"Tech match: '{skill.name}' matches requirement '{req}'")
                match = SkillMatch(
                    profile_skill=skill,
                    jd_requirement=req,
                    match_type="exact",
                    confidence=0.9,
                    explanation=f"Technology match: {skill.name} ↔ {req}",
                )
                matched_skills_list.append(match)
                selected_skill_names.add(skill.name)
                break
    return matched_skills_list
