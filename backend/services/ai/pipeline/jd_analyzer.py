"""Step 1: Analyze job description to extract structured requirements."""

import logging
from typing import Set, List
from backend.services.ai.pipeline.models import JDAnalysis
from backend.services.ai.llm_client import get_llm_client
from backend.services.ai.text import extract_words, normalize_text

logger = logging.getLogger(__name__)

_REQUIRED_HINTS = ("must", "required", "requirement", "you will", "we need", "essential")
_PREFERRED_HINTS = ("nice to have", "plus", "bonus", "preferred", "desirable")
_SENIORITY_SIGNALS = ("senior", "lead", "principal", "architect", "manager", "director", "junior", "mid", "entry")


async def analyze_jd(job_description: str) -> JDAnalysis:
    """
    Analyze job description to extract structured requirements.

    Uses LLM if available for better understanding, falls back to heuristics.

    Args:
        job_description: The job description text

    Returns:
        JDAnalysis with extracted requirements
    """
    llm_client = get_llm_client()

    if llm_client.is_configured():
        try:
            return await _analyze_with_llm(llm_client, job_description)
        except Exception as e:
            logger.warning(f"LLM analysis failed, falling back to heuristics: {e}")

    return _analyze_with_heuristics(job_description)


async def _analyze_with_llm(llm_client, job_description: str) -> JDAnalysis:
    """Use LLM to extract structured requirements."""
    prompt = f"""Analyze this job description and extract structured requirements.

Job Description:
{job_description[:3000]}

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
        response = await llm_client.rewrite_text("", prompt)
        # Parse JSON from response
        import json
        import re

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
    return _analyze_with_heuristics(job_description)


def _analyze_with_heuristics(job_description: str) -> JDAnalysis:
    """Fallback heuristic analysis when LLM is not available."""
    lines = [normalize_text(line) for line in job_description.splitlines() if line.strip()]

    required: Set[str] = set()
    preferred: Set[str] = set()
    responsibilities: List[str] = []
    domain_keywords: Set[str] = set()
    seniority_signals: List[str] = []

    for line in lines:
        words = set(extract_words(line))

        # Check for required skills
        if any(hint in line for hint in _REQUIRED_HINTS):
            required.update(words)

        # Check for preferred skills
        if any(hint in line for hint in _PREFERRED_HINTS):
            preferred.update(words)

        # Extract responsibilities
        if any(verb in line for verb in ("build", "design", "own", "lead", "deliver", "maintain", "improve", "develop", "create")):
            responsibilities.append(line[:140])

        # Check for seniority signals
        for signal in _SENIORITY_SIGNALS:
            if signal in line:
                seniority_signals.append(signal)

    # If no required/preferred found, extract all words as required
    if not required and not preferred:
        required = set(extract_words(job_description))

    # Extract domain keywords (common tech terms)
    all_words = set(extract_words(job_description))
    domain_keywords = all_words - required - preferred

    return JDAnalysis(
        required_skills=required,
        preferred_skills=preferred,
        responsibilities=responsibilities[:10],
        domain_keywords=domain_keywords,
        seniority_signals=list(set(seniority_signals))[:5],
    )
