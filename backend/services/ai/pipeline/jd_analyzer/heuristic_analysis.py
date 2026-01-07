"""Heuristic-based job description analysis."""

from backend.services.ai.pipeline.models import JDAnalysis
from backend.services.ai.pipeline.jd_analyzer.tech_extraction import _extract_tech_terms, _REQUIRED_HINTS, _PREFERRED_HINTS, _SENIORITY_SIGNALS
from backend.services.ai.text import normalize_text


def _analyze_with_heuristics(job_description: str) -> JDAnalysis:
    """Fallback heuristic analysis when LLM is not available."""
    lines = [normalize_text(line) for line in job_description.splitlines() if line.strip()]

    # First, extract tech terms using smart extraction from full JD
    all_tech_terms = _extract_tech_terms(job_description)

    required: set[str] = set()
    preferred: set[str] = set()
    responsibilities: list[str] = []
    seniority_signals: list[str] = []

    # Track which section we're in based on hints
    in_preferred_section = False

    for line in lines:
        line_tech = _extract_tech_terms(line)

        # Check for section markers
        if any(hint in line for hint in _PREFERRED_HINTS):
            in_preferred_section = True

        # Check for required skills (explicit markers)
        if any(hint in line for hint in _REQUIRED_HINTS):
            required.update(line_tech)
            in_preferred_section = False

        # Check for preferred skills (explicit markers or in preferred section)
        elif any(hint in line for hint in _PREFERRED_HINTS) or in_preferred_section:
            preferred.update(line_tech)
        else:
            # Default: add to required if not in preferred section
            required.update(line_tech)

        # Extract responsibilities
        if any(verb in line for verb in ("build", "design", "own", "lead", "deliver", "maintain", "improve", "develop", "create")):
            responsibilities.append(line[:140])

        # Check for seniority signals
        for signal in _SENIORITY_SIGNALS:
            if signal in line:
                seniority_signals.append(signal)

    # If nothing extracted from line-by-line, use all tech terms from full JD
    if not required and not preferred:
        required = all_tech_terms

    # Always add all extracted tech terms to ensure nothing is missed
    # Tech terms not already in required/preferred go to domain_keywords
    domain_keywords = all_tech_terms - required - preferred

    return JDAnalysis(
        required_skills=required,
        preferred_skills=preferred,
        responsibilities=responsibilities[:10],
        domain_keywords=domain_keywords,
        seniority_signals=list(set(seniority_signals))[:5],
    )
