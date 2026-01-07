"""Per-skill AI relevance evaluation using compact prompts."""

import asyncio
import logging
import json
import re
from typing import List, Optional
from backend.models import Skill
from backend.services.ai.pipeline.models import JDAnalysis, SkillRelevanceResult, SkillMapping, SkillMatch
from backend.services.ai.llm_client import get_llm_client
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
    response = await llm_client.rewrite_text("", prompt)
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
