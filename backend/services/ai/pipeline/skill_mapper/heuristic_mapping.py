"""Heuristic-based skill mapping."""

from typing import List, Set, Tuple

from backend.models import Skill
from backend.services.ai.pipeline.models import JDAnalysis, SkillMapping, SkillMatch
from backend.services.ai.text import tech_terms_match
from backend.services.ai.pipeline.skill_mapper.match_utils import _normalize_keyword, _determine_match_type_and_confidence


def _map_with_heuristics(
    profile_skills: List[Skill], jd_analysis: JDAnalysis
) -> SkillMapping:
    """Fallback heuristic matching when LLM is not available."""
    required_keywords = list(jd_analysis.required_skills)
    preferred_keywords = list(jd_analysis.preferred_skills)

    matched_skills_list: List[SkillMatch] = []
    selected_skill_names: Set[str] = set()
    covered_jd_requirements: Set[str] = set()

    for skill in profile_skills:
        # Check against required keywords first
        match, covered = _match_skill_to_keywords(
            skill, required_keywords, True, _normalize_keyword
        )
        if match:
            matched_skills_list.append(match)
            selected_skill_names.add(skill.name)
            covered_jd_requirements.update(covered)
            continue

        # If not matched to required, check preferred
        match, covered = _match_skill_to_keywords(
            skill, preferred_keywords, False, _normalize_keyword
        )
        if match:
            matched_skills_list.append(match)
            selected_skill_names.add(skill.name)
            covered_jd_requirements.update(covered)

    selected_skills = [s for s in profile_skills if s.name in selected_skill_names]

    # Find gaps
    all_jd_requirements = {_normalize_keyword(kw) for kw in required_keywords}
    all_jd_requirements |= {_normalize_keyword(kw) for kw in preferred_keywords}
    gaps = list(all_jd_requirements - covered_jd_requirements)

    return SkillMapping(
        matched_skills=matched_skills_list,
        selected_skills=selected_skills,
        coverage_gaps=gaps,
    )


def _match_skill_to_keywords(
    skill: Skill,
    keywords: List[str],
    is_required: bool,
    normalize_keyword_func,
) -> Tuple[SkillMatch | None, Set[str]]:
    """Match a skill to a list of keywords. Returns (match, covered_requirements)."""
    covered_requirements: Set[str] = set()
    for jd_kw in keywords:
        if tech_terms_match(skill.name, jd_kw):
            normalized_skill = normalize_keyword_func(skill.name)
            normalized_jd = normalize_keyword_func(jd_kw)
            match_type, confidence = _determine_match_type_and_confidence(
                normalized_skill, normalized_jd, is_required
            )

            prefix = "" if is_required else "Preferred "
            match = SkillMatch(
                profile_skill=skill,
                jd_requirement=normalized_jd,
                match_type=match_type,
                confidence=confidence,
                explanation=f"{prefix}match: '{skill.name}' ↔ '{jd_kw}' ({match_type})",
            )
            covered_requirements.add(normalized_jd)
            return match, covered_requirements
    return None, covered_requirements
