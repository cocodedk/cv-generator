"""Text adaptation and JD summary building."""

import logging

from backend.services.ai.pipeline.models import JDAnalysis

logger = logging.getLogger(__name__)

# Target limits for LLM (conservative to avoid expansion)
_LLM_TARGET_DESCRIPTION_CHARS = 250
_LLM_TARGET_HIGHLIGHT_CHARS = 200

# Maximum allowed by model validation (from Experience model)
_MAX_DESCRIPTION_CHARS = 300
_MAX_HIGHLIGHT_CHARS = 250


def _build_jd_summary(jd_analysis: JDAnalysis) -> str:
    """Build JD summary string for adaptation context."""
    return f"""
Required Skills: {', '.join(list(jd_analysis.required_skills)[:20])}
Preferred Skills: {', '.join(list(jd_analysis.preferred_skills)[:20])}
Key Responsibilities: {'; '.join(jd_analysis.responsibilities[:5])}
"""


async def _adapt_text(
    llm_client,
    original_text: str,
    jd_summary: str,
    context_type: str,
    additional_context: str,
) -> str:
    """
    Adapt a single piece of text using LLM.

    CRITICAL RULES enforced in prompt:
    - Only rephrase, never add new facts
    - Use JD terminology
    - Preserve all original facts
    """
    if not original_text or not original_text.strip():
        return original_text

    # Use conservative target for LLM, but allow up to model validation limit
    target_chars = _LLM_TARGET_DESCRIPTION_CHARS if "description" in context_type else _LLM_TARGET_HIGHLIGHT_CHARS
    max_chars = _MAX_DESCRIPTION_CHARS if "description" in context_type else _MAX_HIGHLIGHT_CHARS
    length_instruction = f"\n- Aim to keep the rewritten text under {target_chars} characters"

    prompt = f"""Job Description Context:
{jd_summary}{additional_context}

Original {context_type}:
{original_text}

CRITICAL RULES:
- You are ADAPTING existing content, not creating new content
- Every fact in your output must exist in the original text above
- You may rephrase, reorder, and emphasize differently
- You may use terminology from the job description
- You may NOT add new achievements, metrics, or claims
- If the original says "improved performance", do NOT say "improved performance by 30%"
- If unsure, keep original wording{length_instruction}

Return ONLY the reworded text, no explanations."""

    logger.debug(f"LLM adapting {context_type}: original={len(original_text)} chars, target={target_chars}, max={max_chars}")
    adapted = await llm_client.rewrite_text(original_text, prompt)
    adapted = adapted.strip()
    logger.debug(f"LLM response for {context_type}: {len(adapted)} chars - '{adapted[:100]}...'")

    # Validate length - allow up to model validation limit even if over target
    if len(adapted) > max_chars:
        logger.error(
            f"LLM output for {context_type} exceeds model validation limit: {len(adapted)} > {max_chars} "
            f"(target: {target_chars}, original: {len(original_text)} chars)"
        )
        raise ValueError(
            f"LLM output for {context_type} exceeds character limit "
            f"({len(adapted)} > {max_chars})"
        )

    # Validate we didn't lose essential content (simple check)
    if len(adapted) < len(original_text) * 0.3:
        logger.error(
            f"LLM output for {context_type} too short: {len(adapted)} < {len(original_text) * 0.3} "
            f"(original: {len(original_text)} chars)"
        )
        raise ValueError(
            f"LLM output for {context_type} is too short - possible content loss"
        )

    return adapted
