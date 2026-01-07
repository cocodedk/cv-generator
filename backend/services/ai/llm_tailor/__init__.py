"""LLM tailoring package."""

# Re-export main functionality for backward compatibility
from backend.services.ai.llm_tailor.tailoring import llm_tailor_cv
from backend.services.ai.llm_tailor.text_tailoring import _tailor_text, _get_max_chars, _strip_html
from backend.services.ai.llm_tailor.skill_reordering import _reorder_skills_for_jd

__all__ = [
    "llm_tailor_cv",
    "_tailor_text",
    "_get_max_chars",
    "_strip_html",
    "_reorder_skills_for_jd",
]
