"""Skill matching utility functions."""


def _normalize_keyword(word: str) -> str:
    """Normalize keyword for matching."""
    return word.rstrip(".,;:!?")


def _determine_match_type_and_confidence(
    normalized_skill: str, normalized_jd: str, is_required: bool
) -> tuple[str, float]:
    """Determine match type and confidence based on normalized strings."""
    if normalized_skill == normalized_jd:
        match_type = "exact"
        confidence = 0.9 if is_required else 0.7
    elif normalized_skill in normalized_jd or normalized_jd in normalized_skill:
        match_type = "synonym"
        confidence = 0.85 if is_required else 0.65
    else:
        match_type = "ecosystem"
        confidence = 0.75 if is_required else 0.6
    return match_type, confidence
