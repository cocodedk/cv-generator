"""Main JD analysis logic."""

import logging
from typing import Optional

from backend.services.ai.pipeline.models import JDAnalysis
from backend.services.ai.llm_client import get_llm_client
from backend.services.ai.pipeline.jd_analyzer.llm_analysis import _analyze_with_llm
from backend.services.ai.pipeline.jd_analyzer.heuristic_analysis import _analyze_with_heuristics

logger = logging.getLogger(__name__)


async def analyze_jd(
    job_description: str, additional_context: Optional[str] = None
) -> JDAnalysis:
    """
    Analyze job description to extract structured requirements.

    Uses LLM if available for better understanding, falls back to heuristics.

    Args:
        job_description: The job description text
        additional_context: Optional directive to guide analysis (e.g., "enterprise-focused")

    Returns:
        JDAnalysis with extracted requirements
    """
    logger.info(f"Analyzing JD ({len(job_description)} chars)")
    llm_client = get_llm_client()

    if llm_client.is_configured():
        try:
            result = await _analyze_with_llm(llm_client, job_description, additional_context)
            logger.info(
                f"JD Analysis result: {len(result.required_skills)} required, "
                f"{len(result.preferred_skills)} preferred, {len(result.responsibilities)} responsibilities"
            )
            return result
        except Exception as e:
            logger.warning(f"LLM analysis failed, falling back to heuristics: {e}")

    # Fallback to heuristics when LLM not configured or fails
    logger.info("Using heuristic JD analysis (LLM not available)")
    result = _analyze_with_heuristics(job_description)
    logger.info(
        f"JD Analysis result (heuristics): {len(result.required_skills)} required, "
        f"{len(result.preferred_skills)} preferred, {len(result.responsibilities)} responsibilities"
    )
    return result
