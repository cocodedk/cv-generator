"""Main skill mapping logic."""

import logging
from typing import List, Set

from backend.models import Skill
from backend.services.ai.pipeline.models import JDAnalysis, SkillMapping, SkillMatch
from backend.services.ai.llm_client import get_llm_client
from backend.services.ai.pipeline.skill_mapper.heuristic_mapping import _map_with_heuristics

logger = logging.getLogger(__name__)


async def map_skills(
    profile_skills: List[Skill],
    jd_analysis: JDAnalysis,
) -> SkillMapping:
    """
    Map profile skills to JD requirements with intelligent matching.

    Handles synonyms (e.g., "Node.js" matches "JavaScript") and related skills.

    Args:
        profile_skills: Skills from user's profile
        jd_analysis: Analyzed JD requirements

    Returns:
        SkillMapping with matched skills and gaps
    """
    llm_client = get_llm_client()

    if not llm_client.is_configured():
        raise ValueError(
            "LLM is not configured. Set AI_ENABLED=true and configure API credentials."
        )

    return await _map_with_llm(llm_client, profile_skills, jd_analysis)


async def _map_with_llm(
    llm_client, profile_skills: List[Skill], jd_analysis: JDAnalysis
) -> SkillMapping:
    """Use LLM to intelligently map skills with synonym understanding."""

    # Build skill list for prompt
    profile_skill_list = [
        f"- {skill.name} ({skill.category or 'Uncategorized'})"
        for skill in profile_skills
    ]

    jd_required_list = list(jd_analysis.required_skills)
    jd_preferred_list = list(jd_analysis.preferred_skills)

    prompt = f"""Map profile skills to job description requirements.

PROFILE SKILLS:
{chr(10).join(profile_skill_list[:50])}

JOB DESCRIPTION REQUIREMENTS:
Required: {', '.join(jd_required_list[:30])}
Preferred: {', '.join(jd_preferred_list[:30])}

For each profile skill, determine:
1. Does it match any JD requirement? (exact match, synonym, ecosystem, or related)
2. What type of match? (exact, synonym, ecosystem, related, covers)
3. Confidence level (0.0 to 1.0)
4. Brief explanation

Match types:
- exact: Identical or normalized same (e.g., "PostgreSQL" ↔ "Postgres")
- synonym: Same technology, different name (e.g., "JavaScript" ↔ "Node.js")
- ecosystem: Related technology from same ecosystem (e.g., "Express" when JD mentions "Node.js")
- related: Generally related but not same ecosystem (e.g., "React" ↔ "JavaScript")
- covers: Profile skill encompasses JD requirement

Examples:
- Profile: "JavaScript", JD: "Node.js" → synonym match (Node.js IS JavaScript runtime)
- Profile: "Express", JD: "Node.js" → ecosystem match (Express is Node.js framework)
- Profile: "Python", JD: "Python" → exact match
- Profile: "React", JD: "JavaScript" → related match (React uses JavaScript)
- Profile: "PostgreSQL", JD: "Postgres" → exact match (same thing)

Return ONLY a JSON array of matches:
[
  {{
    "profile_skill_name": "JavaScript",
    "jd_requirement": "Node.js",
    "match_type": "synonym",
    "confidence": 0.95,
    "explanation": "Node.js is a JavaScript runtime, so JavaScript covers this requirement"
  }},
  ...
]

Include matches for required skills first, then preferred. Only include skills that match."""

    try:
        response = await llm_client.generate_text(
            prompt,
            system_prompt="You are a skills categorization expert. Return only valid JSON."
        )
        import json
        import re

        # Extract JSON array from response
        json_match = re.search(r"\[[\s\S]*\]", response)
        if json_match:
            try:
                matches_data = json.loads(json_match.group())
            except json.JSONDecodeError as e:
                logger.error(
                    f"Failed to parse LLM skill mapping JSON: {e}, response: {response[:200]}"
                )
                raise

            matched_skills_list: List[SkillMatch] = []
            selected_skill_names: Set[str] = set()

            for match_data in matches_data:
                skill_name = match_data.get("profile_skill_name", "")
                # Find the skill object
                skill = next((s for s in profile_skills if s.name == skill_name), None)
                if skill:
                    match = SkillMatch(
                        profile_skill=skill,
                        jd_requirement=match_data.get("jd_requirement", ""),
                        match_type=match_data.get("match_type", "related"),
                        confidence=float(match_data.get("confidence", 0.5)),
                        explanation=match_data.get("explanation", ""),
                    )
                    matched_skills_list.append(match)
                    selected_skill_names.add(skill_name)

            # Get all matched skills
            selected_skills = [
                s for s in profile_skills if s.name in selected_skill_names
            ]

            # Find gaps (JD requirements not covered)
            covered_requirements = {m.jd_requirement for m in matched_skills_list}
            all_jd_requirements = (
                jd_analysis.required_skills | jd_analysis.preferred_skills
            )
            gaps = list(all_jd_requirements - covered_requirements)

            return SkillMapping(
                matched_skills=matched_skills_list,
                selected_skills=selected_skills,
                coverage_gaps=gaps,
            )
    except Exception as e:
        logger.error(f"Failed to parse LLM skill mapping response: {e}")
        raise

    # Fallback if parsing fails
    return _map_with_heuristics(profile_skills, jd_analysis)
