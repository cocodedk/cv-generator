"""Response parsing and skill evaluation logic."""

import json
import logging
import re
from typing import List, Optional

from backend.models import Skill
from backend.services.ai.pipeline.models import SkillRelevanceResult
from backend.services.ai.text import tech_terms_match

logger = logging.getLogger(__name__)


async def evaluate_skill_relevance(
    skill: Skill, jd_requirements: List[str], llm_client, additional_context: Optional[str] = None
) -> SkillRelevanceResult:
    """
    Evaluate single skill relevance using AI prompt.

    Args:
        skill: Profile skill to evaluate
        jd_requirements: List of JD required/preferred skills
        llm_client: LLM client instance
        additional_context: Optional directive to guide evaluation

    Returns:
        SkillRelevanceResult with relevance evaluation
    """
    # Improved prompt format for better LLM understanding
    jd_str = ", ".join(jd_requirements[:20])  # Limit to prevent prompt bloat
    directive_section = ""
    if additional_context and additional_context.strip():
        directive_section = f"""

DIRECTIVE: {additional_context}

Follow this directive when evaluating skill relevance. The directive should guide your assessment. For example, if the directive is "emphasize Python", give higher relevance scores to Python-related skills."""

    prompt = f"""Given these job requirements: {jd_str}{directive_section}

Is the skill "{skill.name}" relevant for this job?

Match types:
- direct: Exact or near-exact match (e.g., "Python" matches "Python")
- foundation: Underlying language/platform (e.g., "Python" for "Django")
- alternative: Similar technology (e.g., "PostgreSQL" for "MySQL")
- related: Generally related skill

Return JSON only: {{"relevant": true/false, "type": "direct|foundation|alternative|related", "why": "brief reason", "match": "which requirement"}}"""

    logger.debug(f"LLM prompt for '{skill.name}': {prompt[:200]}...")
    response = await llm_client.generate_text(
        prompt,
        system_prompt="You are a career skills analyst. Evaluate skill relevance accurately."
    )
    logger.debug(f"LLM response for '{skill.name}': {response[:200]}...")
    parsed = parse_relevance_response(response)
    logger.debug(f"Parsed result for '{skill.name}': relevant={parsed.relevant}, type={parsed.relevance_type}")
    return parsed


def _heuristic_skill_check(skill: Skill, jd_requirements: List[str]) -> SkillRelevanceResult:
    """Fallback heuristic check when LLM fails."""
    skill_name_lower = skill.name.lower()

    for req in jd_requirements:
        req_lower = req.lower()
        # Check exact match (case-insensitive)
        if skill_name_lower == req_lower:
            return SkillRelevanceResult(
                relevant=True,
                relevance_type="direct",
                why="Direct match (heuristic)",
                match=req,
            )
        # Check using tech_terms_match for variations
        if tech_terms_match(skill.name, req):
            return SkillRelevanceResult(
                relevant=True,
                relevance_type="direct",
                why="Technology match (heuristic)",
                match=req,
            )

    return SkillRelevanceResult(
        relevant=False,
        relevance_type="related",
        why="No direct match found",
        match="",
    )


def parse_relevance_response(response: str) -> SkillRelevanceResult:
    """Parse AI response into SkillRelevanceResult."""
    # Try to extract JSON from response
    json_match = re.search(r'\{[\s\S]*\}', response)
    if json_match:
        try:
            data = json.loads(json_match.group())
            return SkillRelevanceResult(
                relevant=bool(data.get("relevant", False)),
                relevance_type=data.get("type", "related"),
                why=data.get("why", ""),
                match=data.get("match", ""),
            )
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse relevance response: {e}, response: {response[:200]}")

    # Fallback: try to infer from text response
    response_lower = response.lower()
    if "relevant" in response_lower and ("true" in response_lower or "yes" in response_lower):
        return SkillRelevanceResult(
            relevant=True,
            relevance_type="related",
            why=response[:200],
            match="",
        )

    return SkillRelevanceResult(
        relevant=False,
        relevance_type="related",
        why="Could not parse response",
        match="",
    )
