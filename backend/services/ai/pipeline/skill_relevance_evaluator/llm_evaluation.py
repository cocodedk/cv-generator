"""LLM-based skill relevance evaluation."""

import logging
from typing import List, Optional

from backend.models import Skill
from backend.services.ai.pipeline.models import SkillRelevanceResult
from backend.services.ai.pipeline.skill_relevance_evaluator.parsing import evaluate_skill_relevance

logger = logging.getLogger(__name__)


async def _evaluate_skill_with_error_handling(
    skill: Skill, all_jd_requirements: List[str], llm_client, additional_context: Optional[str] = None
) -> tuple[Skill, Optional[SkillRelevanceResult], Optional[Exception]]:
    """Wrapper to handle errors per skill without stopping others."""
    try:
        logger.debug(f"LLM evaluating skill: '{skill.name}' against {len(all_jd_requirements)} requirements")
        result = await evaluate_skill_relevance(skill, all_jd_requirements, llm_client, additional_context)
        return skill, result, None
    except Exception as e:
        logger.error(f"Failed to evaluate skill '{skill.name}': {e}", exc_info=True)
        return skill, None, e
