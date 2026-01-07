"""Result processing and mapping logic."""

import logging
from typing import List, Optional

from backend.models import Skill
from backend.services.ai.pipeline.models import SkillRelevanceResult, SkillMatch

logger = logging.getLogger(__name__)


def _process_llm_evaluation_results(
    evaluation_results: List[tuple[Skill, Optional[SkillRelevanceResult], Optional[Exception]]],
    matched_skills_list: List[SkillMatch],
    selected_skill_names: set[str],
) -> List[str]:
    """Process LLM evaluation results and return list of failed skills."""
    failed_skills = []
    match_type_map = {
        "direct": "exact",
        "foundation": "ecosystem",
        "alternative": "ecosystem",
        "related": "related",
    }
    confidence_map = {
        "direct": 0.95,
        "foundation": 0.85,
        "alternative": 0.75,
        "related": 0.65,
    }

    for skill, result, error in evaluation_results:
        if error:
            failed_skills.append(skill.name)
            logger.warning(
                f"Skipping skill '{skill.name}' due to error: {error}. "
                f"Continuing with other skills."
            )
            continue

        if result and result.relevant:
            match_type = match_type_map.get(result.relevance_type, "related")
            confidence = confidence_map.get(result.relevance_type, 0.65)

            logger.info(
                f"LLM match: '{skill.name}' → '{result.match}' "
                f"(type: {result.relevance_type}, confidence: {confidence:.2f})"
            )

            match = SkillMatch(
                profile_skill=skill,
                jd_requirement=result.match,
                match_type=match_type,
                confidence=confidence,
                explanation=result.why,
            )
            matched_skills_list.append(match)
            selected_skill_names.add(skill.name)
        else:
            logger.debug(f"LLM determined '{skill.name}' is not relevant")

    return failed_skills
