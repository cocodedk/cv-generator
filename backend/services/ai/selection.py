"""Selection logic for education."""

from __future__ import annotations

from typing import List, Tuple

from backend.models import Education
from backend.services.ai.scoring import score_item, top_n_scored


def select_education(
    education: List[Education], spec, max_education: int
) -> List[Education]:
    """Select most relevant education entries based on JD spec."""
    if not education:
        return []
    scored: List[Tuple[float, Education]] = []
    for edu in education:
        score = score_item(
            text_parts=[edu.degree, edu.institution, edu.field or ""],
            technologies=[],
            start_date="2020-01",
            spec=spec,
        ).value
        scored.append((score, edu))
    return [edu for _, edu in top_n_scored(scored, max_education)]
