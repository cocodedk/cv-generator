"""Cover letter generation package."""

# Re-export main functionality for backward compatibility
from backend.services.ai.cover_letter.generation import generate_cover_letter
from backend.services.ai.cover_letter.formatting import _format_profile_summary, _format_as_html, _format_as_text
from backend.services.ai.cover_letter.prompt_builder import _build_cover_letter_prompt
from backend.services.ai.cover_letter.address_utils import _normalize_address, _strip_html_breaks
from backend.services.ai.cover_letter.highlights import _extract_highlights_used
from backend.services.ai.llm_client import get_llm_client
from backend.services.ai.cover_letter_selection import select_relevant_content

__all__ = [
    "generate_cover_letter",
    "_format_profile_summary",
    "_format_as_html",
    "_format_as_text",
    "_build_cover_letter_prompt",
    "_normalize_address",
    "_strip_html_breaks",
    "_extract_highlights_used",
    "get_llm_client",
    "select_relevant_content",
]
