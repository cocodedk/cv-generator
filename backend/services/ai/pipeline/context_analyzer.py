"""Step 0: Analyze additional_context to determine how to incorporate it intelligently."""

import json
import logging
import re
from typing import Optional
from backend.services.ai.pipeline.models import ContextAnalysis
from backend.services.ai.llm_client import get_llm_client

logger = logging.getLogger(__name__)


async def analyze_additional_context(
    additional_context: str,
    job_description: str,
) -> Optional[ContextAnalysis]:
    """
    Intelligently analyze additional_context to determine how to incorporate it.

    Uses LLM to determine:
    - Type: directive, content_statement, achievement, or mixed
    - Placement: summary, project_highlight, experience_description, or adaptation_guidance
    - Suggested text: How to phrase it for the CV
    - Reasoning: Why this placement

    Args:
        additional_context: User-provided additional context
        job_description: Full job description for context

    Returns:
        ContextAnalysis if additional_context is provided, None otherwise
    """
    if not additional_context or not additional_context.strip():
        return None

    llm_client = get_llm_client()
    if not llm_client.is_configured():
        logger.warning("LLM not configured, cannot analyze additional_context intelligently")
        # Fallback: treat as directive if it contains directive-like keywords
        if any(keyword in additional_context.lower() for keyword in ["make", "emphasize", "focus", "tailor"]):
            return ContextAnalysis(
                type="directive",
                placement="adaptation_guidance",
                suggested_text=additional_context,
                reasoning="Fallback: detected directive keywords"
            )
        # Otherwise treat as content statement
        return ContextAnalysis(
            type="content_statement",
            placement="summary",
            suggested_text=additional_context,
            reasoning="Fallback: default to summary placement"
        )

    try:
        return await _analyze_with_llm(llm_client, additional_context, job_description)
    except Exception as e:
        logger.warning(f"Failed to analyze additional_context with LLM: {e}, using fallback")
        # Fallback to content_statement in summary
        return ContextAnalysis(
            type="content_statement",
            placement="summary",
            suggested_text=additional_context,
            reasoning=f"Fallback after LLM error: {str(e)}"
        )


async def _analyze_with_llm(
    llm_client,
    additional_context: str,
    job_description: str,
) -> ContextAnalysis:
    """Use LLM to analyze additional_context."""
    prompt = f"""Analyze this additional context provided by the user for CV generation:

Additional Context: {additional_context}
Job Description: {job_description}

Determine:
1. Type:
   - "directive" if it's guidance on how to adapt content (e.g., "make it enterprise-focused")
   - "content_statement" if it's a statement to add (e.g., "I am willing to create demos")
   - "achievement" if it's a fact/achievement (e.g., "Rated top 2%")
   - "mixed" if it contains multiple types

2. Best placement:
   - "summary" for general statements about willingness/availability
   - "project_highlight" for project-specific achievements
   - "experience_description" for role-specific info
   - "adaptation_guidance" for directives that should guide rewording

3. Suggested integration: How to naturally incorporate this into the CV

Return JSON:
{{
  "type": "directive|content_statement|achievement|mixed",
  "placement": "summary|project_highlight|experience_description|adaptation_guidance",
  "suggested_text": "How to phrase this for the CV",
  "reasoning": "Why this placement"
}}"""

    logger.debug(f"Analyzing additional_context: {additional_context[:100]}...")
    response = await llm_client.rewrite_text("", prompt)
    logger.debug(f"LLM response for context analysis: {response[:200]}...")

    # Extract JSON from response (handle markdown code blocks)
    json_match = re.search(r'\{[\s\S]*\}', response)
    if json_match:
        try:
            data = json.loads(json_match.group())
            return ContextAnalysis(
                type=data.get("type", "content_statement"),
                placement=data.get("placement", "summary"),
                suggested_text=data.get("suggested_text", additional_context),
                reasoning=data.get("reasoning", "LLM analysis")
            )
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from LLM response: {e}")
            raise ValueError(f"Invalid JSON response from LLM: {e}")

    raise ValueError("No JSON found in LLM response")
