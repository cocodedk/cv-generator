"""Step 5: Assemble final CV and validate coverage."""

import logging
from typing import List, Dict
from backend.models import CVData, Education, PersonalInfo, Skill
from backend.services.ai.pipeline.models import (
    JDAnalysis,
    SkillMapping,
    AdaptedContent,
    CoverageSummary,
)
from backend.services.ai.selection import select_education

logger = logging.getLogger(__name__)


def assemble_cv(
    adapted_content: AdaptedContent,
    profile_personal_info: PersonalInfo,
    profile_education: List[Education],
    profile_skills: List[Skill],
    skill_mapping: SkillMapping,
    jd_analysis: JDAnalysis,
) -> tuple[CVData, CoverageSummary]:
    """
    Assemble final CV from adapted content and validate coverage.

    Args:
        adapted_content: Adapted experiences
        profile_personal_info: Personal info from profile
        profile_education: Education from profile
        profile_skills: All skills from profile
        skill_mapping: Skill mapping results
        jd_analysis: JD requirements

    Returns:
        Tuple of (CVData, CoverageSummary)
    """
    # Select education based on JD
    class SimpleSpec:
        def __init__(self, jd: JDAnalysis):
            self.required_keywords = jd.required_skills
            self.preferred_keywords = jd.preferred_skills
            self.responsibilities = jd.responsibilities

    spec = SimpleSpec(jd_analysis)
    selected_education = select_education(profile_education, spec, max_education=2)

    # Use mapped skills
    selected_skills = skill_mapping.selected_skills

    # If no skills matched, include top skills from profile
    if not selected_skills:
        selected_skills = profile_skills[:10]

    # Assemble CV
    draft_cv = CVData(
        personal_info=profile_personal_info,
        experience=adapted_content.experiences,
        education=selected_education,
        skills=selected_skills,
        theme="classic",
    )

    # Build coverage summary
    coverage_summary = _build_coverage_summary(
        draft_cv, skill_mapping, jd_analysis
    )

    return draft_cv, coverage_summary


def _build_coverage_summary(
    cv: CVData,
    skill_mapping: SkillMapping,
    jd_analysis: JDAnalysis,
) -> CoverageSummary:
    """Build summary of how CV covers JD requirements."""

    # Skills that are covered (direct matches)
    covered_requirements: List[str] = []
    for match in skill_mapping.matched_skills:
        if match.match_type in ("exact", "synonym", "covers"):
            covered_requirements.append(match.jd_requirement)

    # Partially covered (ecosystem, related, responsibility support, etc.)
    partially_covered: List[str] = []
    for match in skill_mapping.matched_skills:
        if match.match_type in ("related", "ecosystem", "responsibility_support", "domain_complement", "category_match"):
            partially_covered.append(match.jd_requirement)

    # Gaps
    gaps = skill_mapping.coverage_gaps

    # Skill justifications with categorization
    skill_justifications: Dict[str, str] = {}
    for match in skill_mapping.matched_skills:
        skill_name = match.profile_skill.name

        # Categorize match type for better justifications
        category_map = {
            "exact": "Direct Match",
            "synonym": "Direct Match",
            "covers": "Direct Match",
            "ecosystem": "Technology Ecosystem",
            "responsibility_support": "Supports Responsibilities",
            "domain_complement": "Domain Complement",
            "category_match": "Technology Category Match",
            "related": "Related Technology",
        }
        category = category_map.get(match.match_type, "Match")

        # Build enhanced justification
        if skill_name not in skill_justifications:
            justification = f"[{category}] {match.explanation}"
            skill_justifications[skill_name] = justification
        else:
            # If skill has multiple matches, combine them
            existing = skill_justifications[skill_name]
            if category not in existing:
                skill_justifications[skill_name] = f"{existing}; [{category}] {match.explanation}"

    return CoverageSummary(
        covered_requirements=list(set(covered_requirements)),
        partially_covered=list(set(partially_covered)),
        gaps=gaps,
        skill_justifications=skill_justifications,
    )
