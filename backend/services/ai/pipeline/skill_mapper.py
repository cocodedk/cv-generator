"""Step 2: Map profile skills to JD requirements with intelligent matching."""

import logging
from typing import List, Set
from backend.models import Skill
from backend.services.ai.pipeline.models import JDAnalysis, SkillMapping, SkillMatch
from backend.services.ai.llm_client import get_llm_client
from backend.services.ai.text import normalize_text, tech_terms_match

logger = logging.getLogger(__name__)


async def map_skills(
    profile_skills: List[Skill], jd_analysis: JDAnalysis
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
        response = await llm_client.rewrite_text("", prompt)
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


def _map_with_heuristics(
    profile_skills: List[Skill], jd_analysis: JDAnalysis
) -> SkillMapping:
    """Fallback heuristic matching when LLM is not available."""

    def normalize_keyword(word: str) -> str:
        """Normalize keyword for matching."""
        return normalize_text(word.rstrip(".,;:!?"))

    required_keywords = list(jd_analysis.required_skills)
    preferred_keywords = list(jd_analysis.preferred_skills)

    matched_skills_list: List[SkillMatch] = []
    selected_skill_names: Set[str] = set()
    covered_jd_requirements: Set[str] = set()

    for skill in profile_skills:
        skill_matched = False

        # Check against required keywords using smart matching
        for jd_kw in required_keywords:
            if tech_terms_match(skill.name, jd_kw):
                # Determine match type: exact if normalized same, otherwise ecosystem/related
                normalized_skill = normalize_keyword(skill.name)
                normalized_jd = normalize_keyword(jd_kw)

                if normalized_skill == normalized_jd:
                    match_type = "exact"
                    confidence = 0.9
                elif normalized_skill in normalized_jd or normalized_jd in normalized_skill:
                    match_type = "synonym"
                    confidence = 0.85
                else:
                    # Related match - could be ecosystem
                    match_type = "ecosystem"
                    confidence = 0.75

                match = SkillMatch(
                    profile_skill=skill,
                    jd_requirement=normalize_keyword(jd_kw),
                    match_type=match_type,
                    confidence=confidence,
                    explanation=f"Match: '{skill.name}' ↔ '{jd_kw}' ({match_type})",
                )
                matched_skills_list.append(match)
                selected_skill_names.add(skill.name)
                covered_jd_requirements.add(normalize_keyword(jd_kw))
                skill_matched = True
                break

        # If not matched to required, check preferred
        if not skill_matched:
            for jd_kw in preferred_keywords:
                if tech_terms_match(skill.name, jd_kw):
                    normalized_skill = normalize_keyword(skill.name)
                    normalized_jd = normalize_keyword(jd_kw)

                    if normalized_skill == normalized_jd:
                        match_type = "exact"
                        confidence = 0.7
                    elif normalized_skill in normalized_jd or normalized_jd in normalized_skill:
                        match_type = "synonym"
                        confidence = 0.65
                    else:
                        match_type = "ecosystem"
                        confidence = 0.6

                    match = SkillMatch(
                        profile_skill=skill,
                        jd_requirement=normalize_keyword(jd_kw),
                        match_type=match_type,
                        confidence=confidence,
                        explanation=f"Preferred match: '{skill.name}' ↔ '{jd_kw}' ({match_type})",
                    )
                    matched_skills_list.append(match)
                    selected_skill_names.add(skill.name)
                    covered_jd_requirements.add(normalize_keyword(jd_kw))
                    break

    selected_skills = [s for s in profile_skills if s.name in selected_skill_names]

    # Find gaps
    all_jd_requirements = {normalize_keyword(kw) for kw in required_keywords}
    all_jd_requirements |= {normalize_keyword(kw) for kw in preferred_keywords}
    gaps = list(all_jd_requirements - covered_jd_requirements)

    return SkillMapping(
        matched_skills=matched_skills_list,
        selected_skills=selected_skills,
        coverage_gaps=gaps,
    )
