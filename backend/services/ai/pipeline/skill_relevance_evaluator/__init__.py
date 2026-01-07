"""Skill relevance evaluation package."""

# Re-export main functionality for backward compatibility
from backend.services.ai.pipeline.skill_relevance_evaluator.evaluation import evaluate_all_skills
from backend.services.ai.pipeline.skill_relevance_evaluator.matching import _match_skills_in_raw_jd, _match_skills_to_requirements, _skill_in_raw_jd
from backend.services.ai.pipeline.skill_relevance_evaluator.llm_evaluation import _evaluate_skill_with_error_handling
from backend.services.ai.pipeline.skill_relevance_evaluator.parsing import evaluate_skill_relevance, parse_relevance_response, _heuristic_skill_check
from backend.services.ai.pipeline.skill_relevance_evaluator.processing import _process_llm_evaluation_results

__all__ = [
    "evaluate_all_skills",
    "_match_skills_in_raw_jd",
    "_match_skills_to_requirements",
    "_skill_in_raw_jd",
    "_evaluate_skill_with_error_handling",
    "evaluate_skill_relevance",
    "parse_relevance_response",
    "_heuristic_skill_check",
    "_process_llm_evaluation_results",
]
