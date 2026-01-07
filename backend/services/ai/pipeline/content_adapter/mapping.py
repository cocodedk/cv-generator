"""Adapted text mapping utilities."""

from typing import Dict, List, Tuple


def _build_adapted_text_map(
    adaptation_results: List[Tuple[str, str, str, str, str, str, str | None]],
    warnings: List[str],
) -> Dict[Tuple[str, str, str, str], Tuple[str, str | None]]:
    """Build lookup map for adapted text."""
    adapted_text_map: Dict[Tuple[str, str, str, str], Tuple[str, str | None]] = {}
    for task_type, exp_idx, proj_idx, hl_idx, original, adapted, error in adaptation_results:
        key = (task_type, exp_idx, proj_idx, hl_idx)
        adapted_text_map[key] = (adapted, error)
        if error:
            warnings.append(error)
    return adapted_text_map
