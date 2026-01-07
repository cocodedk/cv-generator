"""Main content adaptation logic."""

import asyncio
import logging
from typing import Optional

from backend.services.ai.pipeline.models import JDAnalysis, SelectionResult, AdaptedContent
from backend.services.ai.llm_client import get_llm_client
from backend.services.ai.pipeline.content_adapter.task_collection import _collect_adaptation_tasks, _adapt_single_text_item
from backend.services.ai.pipeline.content_adapter.reconstruction import _reconstruct_experience
from backend.services.ai.pipeline.content_adapter.mapping import _build_adapted_text_map

logger = logging.getLogger(__name__)


async def adapt_content(
    selection_result: SelectionResult,
    jd_analysis: JDAnalysis,
    additional_context: Optional[str] = None,
) -> AdaptedContent:
    """
    Adapt wording of selected content to match JD terminology.

    CRITICAL: Only changes wording, never adds new facts or claims.

    Args:
        selection_result: Selected content from profile
        jd_analysis: JD requirements for context
        additional_context: Optional user-provided context to incorporate

    Returns:
        AdaptedContent with reworded content
    """
    llm_client = get_llm_client()

    if llm_client.is_configured():
        return await _adapt_with_llm(
            llm_client, selection_result, jd_analysis, additional_context
        )

    # Without LLM, return content as-is
    return AdaptedContent(
        experiences=selection_result.experiences,
        adaptation_notes={},
        warnings=[],
    )


async def _adapt_with_llm(
    llm_client,
    selection_result: SelectionResult,
    jd_analysis: JDAnalysis,
    additional_context: Optional[str],
) -> AdaptedContent:
    """Use LLM to adapt content wording."""
    from backend.services.ai.pipeline.content_adapter.text_adaptation import _build_jd_summary

    adapted_experiences = []
    adaptation_notes = {}
    warnings = []

    jd_summary = _build_jd_summary(jd_analysis)
    # Treat additional_context as directive when provided
    if additional_context and additional_context.strip():
        context_section = f"""

DIRECTIVE: {additional_context}

Follow this directive when adapting content. The directive should guide how you reword and emphasize content to match the job description. For example, if the directive is "enterprise-focused", use enterprise-oriented terminology and emphasize enterprise-related aspects."""
    else:
        context_section = ""

    logger.info(f"Adapting content for {len(selection_result.experiences)} experiences")

    # Collect all text items that need adaptation
    adaptation_tasks = _collect_adaptation_tasks(selection_result)
    logger.info(f"Collected {len(adaptation_tasks)} text items to adapt - running in parallel")

    # Adapt all text items in parallel
    adaptation_results = await asyncio.gather(
        *[_adapt_single_text_item(llm_client, task, jd_summary, context_section) for task in adaptation_tasks],
        return_exceptions=False
    )

    # Build a lookup map for adapted text
    adapted_text_map = _build_adapted_text_map(adaptation_results, warnings)

    # Reconstruct experiences with adapted content
    for exp_idx, exp in enumerate(selection_result.experiences):
        adapted_experiences.append(_reconstruct_experience(exp, exp_idx, adapted_text_map, adaptation_notes))

    return AdaptedContent(
        experiences=adapted_experiences,
        adaptation_notes=adaptation_notes,
        warnings=warnings,
    )
