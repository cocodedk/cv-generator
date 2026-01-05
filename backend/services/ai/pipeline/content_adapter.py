"""Step 4: Adapt content wording to match JD while preserving all facts."""

import asyncio
import logging
from typing import List, Dict, Optional, Tuple
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
        return await _adapt_with_llm(
            llm_client, selection_result, jd_analysis, additional_context
        )

    # Without LLM, return content as-is
    return AdaptedContent(
        experiences=selection_result.experiences,
        adaptation_notes={},
        warnings=[],
    )


def _build_jd_summary(jd_analysis: JDAnalysis) -> str:
    """Build JD summary string for adaptation context."""
    return f"""
Required Skills: {', '.join(list(jd_analysis.required_skills)[:20])}
Preferred Skills: {', '.join(list(jd_analysis.preferred_skills)[:20])}
Key Responsibilities: {'; '.join(jd_analysis.responsibilities[:5])}
"""


def _collect_adaptation_tasks(selection_result: SelectionResult) -> List[Tuple[str, str, str, str, str]]:
    """Collect all text items that need adaptation."""
    adaptation_tasks: List[Tuple[str, str, str, str, str]] = []  # (type, exp_idx, proj_idx, hl_idx, text)

    for exp_idx, exp in enumerate(selection_result.experiences):
        logger.debug(f"Collecting adaptation tasks for experience {exp_idx+1}/{len(selection_result.experiences)}: {exp.title} at {exp.company}")

        # Experience description
        if exp.description:
            adaptation_tasks.append(("exp_desc", str(exp_idx), "", "", exp.description))

        # Project descriptions and highlights
        for proj_idx, project in enumerate(exp.projects):
            if project.description:
                adaptation_tasks.append(("proj_desc", str(exp_idx), str(proj_idx), "", project.description))

            for hl_idx, highlight in enumerate(project.highlights):
                adaptation_tasks.append(("highlight", str(exp_idx), str(proj_idx), str(hl_idx), highlight))

    return adaptation_tasks


async def _adapt_single_text_item(
    llm_client,
    task_info: Tuple[str, str, str, str, str],
    jd_summary: str,
    context_section: str,
) -> Tuple[str, str, str, str, str, str, Optional[str]]:
    """Adapt a single text item with error handling."""
    task_type, exp_idx, proj_idx, hl_idx, original_text = task_info
    context_type_map = {
        "exp_desc": "experience description",
        "proj_desc": "project description",
        "highlight": "bullet point",
    }
    context_type = context_type_map.get(task_type, "text")

    try:
        adapted = await _adapt_text(
            llm_client,
            original_text,
            jd_summary,
            context_type,
            context_section,
        )
        return (task_type, exp_idx, proj_idx, hl_idx, original_text, adapted, None)
    except ValueError as e:
        logger.warning(f"Failed to adapt {context_type}: {e}")
        return (task_type, exp_idx, proj_idx, hl_idx, original_text, original_text, str(e))


def _build_adapted_text_map(
    adaptation_results: List[Tuple[str, str, str, str, str, str, Optional[str]]],
    warnings: List[str],
) -> Dict[Tuple[str, str, str, str], Tuple[str, Optional[str]]]:
    """Build lookup map for adapted text."""
    adapted_text_map: Dict[Tuple[str, str, str, str], Tuple[str, Optional[str]]] = {}
    for task_type, exp_idx, proj_idx, hl_idx, original, adapted, error in adaptation_results:
        key = (task_type, exp_idx, proj_idx, hl_idx)
        adapted_text_map[key] = (adapted, error)
        if error:
            warnings.append(error)
    return adapted_text_map


def _reconstruct_project(
    project: Project,
    exp_idx: int,
    proj_idx: int,
    adapted_text_map: Dict[Tuple[str, str, str, str], Tuple[str, Optional[str]]],
) -> Project:
    """Reconstruct a project with adapted content."""
    # Get adapted project description
    adapted_proj_desc = project.description
    proj_desc_key = ("proj_desc", str(exp_idx), str(proj_idx), "")
    if proj_desc_key in adapted_text_map:
        adapted_proj_desc, _ = adapted_text_map[proj_desc_key]
        logger.debug(f"    Project description adapted: {len(project.description)} → {len(adapted_proj_desc)} chars")

    # Get adapted highlights
    adapted_highlights: List[str] = []
    for hl_idx, highlight in enumerate(project.highlights):
        hl_key = ("highlight", str(exp_idx), str(proj_idx), str(hl_idx))
        if hl_key in adapted_text_map:
            adapted_hl, _ = adapted_text_map[hl_key]
            adapted_highlights.append(adapted_hl)
        else:
            adapted_highlights.append(highlight)  # Fallback

    return Project(
        name=project.name,
        description=adapted_proj_desc,
        highlights=adapted_highlights,
        technologies=project.technologies,  # Never change technologies
        url=project.url,
    )


def _reconstruct_experience(
    exp: Experience,
    exp_idx: int,
    adapted_text_map: Dict[Tuple[str, str, str, str], Tuple[str, Optional[str]]],
    adaptation_notes: Dict[str, str],
) -> Experience:
    """Reconstruct an experience with adapted content."""
    logger.debug(f"Reconstructing experience {exp_idx+1}: {exp.title} at {exp.company}")

    # Get adapted description
    adapted_description = exp.description
    desc_key = ("exp_desc", str(exp_idx), "", "")
    if desc_key in adapted_text_map:
        adapted_description, error = adapted_text_map[desc_key]
        if adapted_description != exp.description:
            logger.info(f"  Description adapted: {len(exp.description)} → {len(adapted_description)} chars")
            adaptation_notes[f"{exp.company}_description"] = "Reworded to match JD terminology"

    # Reconstruct projects with adapted content
    adapted_projects: List[Project] = []
    for proj_idx, project in enumerate(exp.projects):
        adapted_projects.append(_reconstruct_project(project, exp_idx, proj_idx, adapted_text_map))

    return Experience(
        title=exp.title,
        company=exp.company,
        start_date=exp.start_date,
        end_date=exp.end_date,
        description=adapted_description,
        location=exp.location,
        projects=adapted_projects,
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
    warnings: List[str] = []

    jd_summary = _build_jd_summary(jd_analysis)
    context_section = f"\nAdditional Context: {additional_context}" if additional_context else ""

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

    logger.debug(f"LLM adapting {context_type}: original={len(original_text)} chars, limit={max_chars}")
    adapted = await llm_client.rewrite_text(original_text, prompt)
    adapted = adapted.strip()
    logger.debug(f"LLM response for {context_type}: {len(adapted)} chars - '{adapted[:100]}...'")

    # Validate length
    if len(adapted) > max_chars + 20:
        logger.error(
            f"LLM output for {context_type} exceeds limit: {len(adapted)} > {max_chars} "
            f"(original: {len(original_text)} chars)"
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
