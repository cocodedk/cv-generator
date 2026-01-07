"""LLM-based job description analysis."""

import logging
import re
from typing import Optional

from backend.services.ai.pipeline.models import JDAnalysis

logger = logging.getLogger(__name__)


async def _analyze_with_llm(
    llm_client, job_description: str, additional_context: Optional[str] = None
) -> JDAnalysis:
    """Use LLM to extract structured requirements."""
    directive_section = ""
    if additional_context and additional_context.strip():
        directive_section = f"""

DIRECTIVE: {additional_context}

Follow this directive when analyzing the job description. The directive should guide your extraction of requirements, skills, and responsibilities. For example, if the directive is "enterprise-focused", emphasize enterprise-related requirements and skills."""

    prompt = f"""Analyze this job description and extract structured requirements.{directive_section}

Job Description:
{job_description}

Extract and categorize:
1. Required skills/technologies (must-have)
2. Preferred skills/technologies (nice-to-have)
3. Key responsibilities/duties
4. Domain/industry keywords
5. Seniority level indicators

Return ONLY a JSON object with this structure:
{{
  "required_skills": ["skill1", "skill2", ...],
  "preferred_skills": ["skill1", "skill2", ...],
  "responsibilities": ["duty1", "duty2", ...],
  "domain_keywords": ["keyword1", "keyword2", ...],
  "seniority_signals": ["senior", "lead", ...]
}}

Be specific with technology names (e.g., "Node.js", "React", "PostgreSQL").
Include frameworks, languages, tools, and methodologies mentioned."""

    try:
        response = await llm_client.generate_text(
            prompt,
            system_prompt="You are a job description analyzer. Return only valid JSON."
        )
        # Parse JSON from response
        import json

        # Extract JSON from response (handle markdown code blocks)
        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            try:
                data = json.loads(json_match.group())
                return JDAnalysis(
                    required_skills=set(data.get("required_skills", [])),
                    preferred_skills=set(data.get("preferred_skills", [])),
                    responsibilities=data.get("responsibilities", [])[:10],
                    domain_keywords=set(data.get("domain_keywords", [])),
                    seniority_signals=data.get("seniority_signals", [])[:5],
                )
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse LLM JSON response: {e}, response: {response[:200]}")
                raise
    except Exception as e:
        logger.error(f"LLM JD analysis failed: {e}")
        raise

    # Fallback if parsing fails
    from backend.services.ai.pipeline.jd_analyzer.heuristic_analysis import _analyze_with_heuristics
    return _analyze_with_heuristics(job_description)
