"""Step 4: Adapt content wording to match JD while preserving all facts."""

import logging
from typing import List, Dict, Optional
from backend.models import Experience, Project
from backend.services.ai.pipeline.models import JDAnalysis, SelectionResult, AdaptedContent
from backend.services.ai.llm_client import get_llm_client

logger = logging.getLogger(__name__)

_MAX_DESCRIPTION_CHARS = 280
_MAX_HIGHLIGHT_CHARS = 200


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
        try:
            return await _adapt_with_llm(
                llm_client, selection_result, jd_analysis, additional_context
            )
        except Exception as e:
            logger.warning(f"LLM adaptation failed, using original content: {e}")

    # Without LLM, return content as-is
    return AdaptedContent(
        experiences=selection_result.experiences,
        adaptation_notes={},
    )


async def _adapt_with_llm(
    llm_client,
    selection_result: SelectionResult,
    jd_analysis: JDAnalysis,
    additional_context: Optional[str],
) -> AdaptedContent:
    """Use LLM to adapt content wording."""

    adapted_experiences: List[Experience] = []
    adaptation_notes: Dict[str, str] = {}

    jd_summary = f"""
Required Skills: {', '.join(list(jd_analysis.required_skills)[:20])}
Preferred Skills: {', '.join(list(jd_analysis.preferred_skills)[:20])}
Key Responsibilities: {'; '.join(jd_analysis.responsibilities[:5])}
"""

    context_section = f"\nAdditional Context: {additional_context}" if additional_context else ""

    for exp in selection_result.experiences:
        # Adapt experience description
        adapted_description = exp.description
        if exp.description:
            adapted_description = await _adapt_text(
                llm_client,
                exp.description,
                jd_summary,
                "experience description",
                context_section,
            )
            if adapted_description != exp.description:
                adaptation_notes[f"{exp.company}_description"] = "Reworded to match JD terminology"

        # Adapt projects
        adapted_projects: List[Project] = []
        for project in exp.projects:
            # Adapt project description
            adapted_proj_desc = project.description
            if project.description:
                adapted_proj_desc = await _adapt_text(
                    llm_client,
                    project.description,
                    jd_summary,
                    "project description",
                    context_section,
                )

            # Adapt highlights
            adapted_highlights: List[str] = []
            for highlight in project.highlights:
                adapted_hl = await _adapt_text(
                    llm_client,
                    highlight,
                    jd_summary,
                    "bullet point",
                    context_section,
                )
                adapted_highlights.append(adapted_hl)

            adapted_projects.append(
                Project(
                    name=project.name,
                    description=adapted_proj_desc,
                    highlights=adapted_highlights,
                    technologies=project.technologies,  # Never change technologies
                    url=project.url,
                )
            )

        adapted_experiences.append(
            Experience(
                title=exp.title,
                company=exp.company,
                start_date=exp.start_date,
                end_date=exp.end_date,
                description=adapted_description,
                location=exp.location,
                projects=adapted_projects,
            )
        )

    return AdaptedContent(
        experiences=adapted_experiences,
        adaptation_notes=adaptation_notes,
    )


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

    max_chars = _MAX_DESCRIPTION_CHARS if "description" in context_type else _MAX_HIGHLIGHT_CHARS
    length_instruction = f"\n- Keep the rewritten text under {max_chars} characters (CRITICAL)"

    prompt = f"""Job Description Context:
{jd_summary[:2000]}{additional_context}

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

    try:
        adapted = await llm_client.rewrite_text(original_text, prompt)
        adapted = adapted.strip()

        # Validate length
        if len(adapted) > max_chars + 20:
            logger.warning(f"Adapted {context_type} exceeds limit, using original")
            return original_text

        # Validate we didn't lose essential content (simple check)
        if len(adapted) < len(original_text) * 0.3:
            logger.warning(f"Adapted {context_type} too short, using original")
            return original_text

        return adapted
    except Exception as e:
        logger.error(f"Failed to adapt {context_type}: {e}")
        return original_text  # Fallback to original
