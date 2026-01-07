"""Main skill relevance evaluation logic."""

import asyncio
import logging
from typing import List, Optional

from backend.models import Skill
from backend.services.ai.pipeline.models import JDAnalysis, SkillMapping, SkillMatch
from backend.services.ai.llm_client import get_llm_client
from backend.services.ai.pipeline.skill_relevance_evaluator.matching import _match_skills_in_raw_jd, _match_skills_to_requirements
from backend.services.ai.pipeline.skill_relevance_evaluator.processing import _process_llm_evaluation_results

logger = logging.getLogger(__name__)


async def evaluate_all_skills(
    profile_skills: List[Skill],
    jd_analysis: JDAnalysis,
    raw_jd: Optional[str] = None,
    additional_context: Optional[str] = None,
) -> SkillMapping:
    """
    Evaluate each profile skill individually for relevance to JD requirements.

    Args:
        profile_skills: All skills from user's profile
        jd_analysis: Analyzed JD requirements
        raw_jd: Raw job description text for direct matching
        additional_context: Optional directive to guide skill evaluation (e.g., "emphasize Python")

    Returns:
        SkillMapping with relevant skills and their matches
    """
    matched_skills_list: List[SkillMatch] = []
    selected_skill_names: set[str] = set()

    # Combine required and preferred skills for evaluation
    all_jd_requirements = list(jd_analysis.required_skills | jd_analysis.preferred_skills)

    # LAYER 1: First, check raw JD text for literal skill matches
    if raw_jd:
        matched_skills_list.extend(_match_skills_in_raw_jd(profile_skills, raw_jd, selected_skill_names))

    # LAYER 2: Check against extracted JD requirements using tech_terms_match
    matched_skills_list.extend(_match_skills_to_requirements(profile_skills, all_jd_requirements, selected_skill_names))

    # LAYER 3: LLM evaluation for remaining skills (semantic matching)
    remaining_skills = [s for s in profile_skills if s.name not in selected_skill_names]

    if remaining_skills and all_jd_requirements:
        llm_client = get_llm_client()

        if not llm_client.is_configured():
            raise ValueError(
                "LLM is not configured. Set AI_ENABLED=true and configure API credentials. "
                f"Need LLM to evaluate {len(remaining_skills)} remaining skills."
            )

        logger.info(
            f"Evaluating {len(remaining_skills)} remaining skills via LLM in parallel "
            f"(already matched {len(selected_skill_names)} via layers 1-2)"
        )

        # Import here to avoid circular imports
        from backend.services.ai.pipeline.skill_relevance_evaluator.llm_evaluation import _evaluate_skill_with_error_handling

        # Run all skill evaluations in parallel
        evaluation_results = await asyncio.gather(
            *[_evaluate_skill_with_error_handling(skill, all_jd_requirements, llm_client, additional_context) for skill in remaining_skills],
            return_exceptions=False
        )

        # Process results
        failed_skills = _process_llm_evaluation_results(evaluation_results, matched_skills_list, selected_skill_names)

        # Log summary if any skills failed
        if failed_skills:
            selected_skills = [s for s in profile_skills if s.name in selected_skill_names]
            logger.warning(
                f"Skipped {len(failed_skills)} skill(s) due to errors: {', '.join(failed_skills)}. "
                f"CV generation will continue with {len(selected_skills)} successfully evaluated skills."
            )

    selected_skills = [s for s in profile_skills if s.name in selected_skill_names]

    # Find gaps (JD requirements not covered)
    covered_requirements = {m.jd_requirement for m in matched_skills_list}
    gaps = [req for req in all_jd_requirements if req not in covered_requirements]

    return SkillMapping(
        matched_skills=matched_skills_list,
        selected_skills=selected_skills,
        coverage_gaps=gaps,
    )
