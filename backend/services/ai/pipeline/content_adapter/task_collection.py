"""Task collection and parallel adaptation logic."""

import logging
from typing import List, Tuple

from backend.services.ai.pipeline.models import SelectionResult
from backend.services.ai.pipeline.content_adapter.text_adaptation import _adapt_text

logger = logging.getLogger(__name__)


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
) -> Tuple[str, str, str, str, str, str, str | None]:
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
