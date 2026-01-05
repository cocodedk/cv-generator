"""Per-skill AI relevance evaluation using compact prompts."""

import logging
import json
import re
from typing import List
from backend.models import Skill
from backend.services.ai.pipeline.models import JDAnalysis, SkillRelevanceResult, SkillMapping, SkillMatch
from backend.services.ai.llm_client import get_llm_client

logger = logging.getLogger(__name__)


async def evaluate_all_skills(
    profile_skills: List[Skill], jd_analysis: JDAnalysis
) -> SkillMapping:
    """
    Evaluate each profile skill individually for relevance to JD requirements.

    Args:
        profile_skills: All skills from user's profile
        jd_analysis: Analyzed JD requirements

    Returns:
        SkillMapping with relevant skills and their matches
    """
    llm_client = get_llm_client()

    if not llm_client.is_configured():
        logger.warning("LLM not configured, falling back to heuristic skill mapping")
        from backend.services.ai.pipeline.skill_mapper import map_skills
        return await map_skills(profile_skills, jd_analysis)

    # Combine required and preferred skills for evaluation
    all_jd_requirements = list(jd_analysis.required_skills | jd_analysis.preferred_skills)

    if not all_jd_requirements:
        return SkillMapping(
            matched_skills=[],
            selected_skills=[],
            coverage_gaps=[],
        )

    matched_skills_list: List[SkillMatch] = []
    selected_skill_names: set[str] = set()

    # Evaluate each skill individually
    for skill in profile_skills:
        try:
            result = await evaluate_skill_relevance(skill, all_jd_requirements, llm_client)

            if result.relevant:
                # Convert relevance type to match_type for compatibility
                match_type_map = {
                    "direct": "exact",
                    "foundation": "ecosystem",
                    "alternative": "ecosystem",
                    "related": "related",
                }
                match_type = match_type_map.get(result.relevance_type, "related")

                # Determine confidence based on relevance type
                confidence_map = {
                    "direct": 0.95,
                    "foundation": 0.85,
                    "alternative": 0.75,
                    "related": 0.65,
                }
                confidence = confidence_map.get(result.relevance_type, 0.65)

                match = SkillMatch(
                    profile_skill=skill,
                    jd_requirement=result.match,
                    match_type=match_type,
                    confidence=confidence,
                    explanation=result.why,
                )
                matched_skills_list.append(match)
                selected_skill_names.add(skill.name)
        except Exception as e:
            logger.warning(f"Failed to evaluate skill '{skill.name}': {e}")
            continue

    selected_skills = [s for s in profile_skills if s.name in selected_skill_names]

    # Find gaps (JD requirements not covered)
    covered_requirements = {m.jd_requirement for m in matched_skills_list}
    gaps = [req for req in all_jd_requirements if req not in covered_requirements]

    return SkillMapping(
        matched_skills=matched_skills_list,
        selected_skills=selected_skills,
        coverage_gaps=gaps,
    )


async def evaluate_skill_relevance(
    skill: Skill, jd_requirements: List[str], llm_client
) -> SkillRelevanceResult:
    """
    Evaluate single skill relevance using compact AI prompt.

    Args:
        skill: Profile skill to evaluate
        jd_requirements: List of JD required/preferred skills
        llm_client: LLM client instance

    Returns:
        SkillRelevanceResult with relevance evaluation
    """
    # Compact prompt format: ~40 tokens
    jd_str = ",".join(jd_requirements[:20])  # Limit to prevent prompt bloat
    prompt = f"JD:{jd_str}\nSkill:{skill.name}\nRelevant?{{relevant:bool,type:direct|foundation|alternative|related,why:str,match:str}}"

    try:
        response = await llm_client.rewrite_text("", prompt)
        return parse_relevance_response(response)
    except Exception as e:
        logger.error(f"LLM evaluation failed for skill '{skill.name}': {e}")
        # Fallback: return not relevant
        return SkillRelevanceResult(
            relevant=False,
            relevance_type="related",
            why="Evaluation failed",
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
