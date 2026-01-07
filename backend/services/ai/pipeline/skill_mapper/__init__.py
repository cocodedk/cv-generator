"""Skill mapper package."""

# Re-export main functionality for backward compatibility
from backend.services.ai.pipeline.skill_mapper.mapping import map_skills, _map_with_llm
from backend.services.ai.pipeline.skill_mapper.heuristic_mapping import _map_with_heuristics, _match_skill_to_keywords
from backend.services.ai.pipeline.skill_mapper.match_utils import _normalize_keyword, _determine_match_type_and_confidence

__all__ = [
    "map_skills",
    "_map_with_llm",
    "_map_with_heuristics",
    "_match_skill_to_keywords",
    "_normalize_keyword",
    "_determine_match_type_and_confidence",
]
