"""Step 4: Adapt content wording to match JD while preserving all facts."""

# Re-export main functionality for backward compatibility
from backend.services.ai.pipeline.content_adapter.adaptation import adapt_content, _adapt_with_llm
from backend.services.ai.pipeline.content_adapter.task_collection import _collect_adaptation_tasks, _adapt_single_text_item
from backend.services.ai.pipeline.content_adapter.reconstruction import _reconstruct_experience, _reconstruct_project
from backend.services.ai.pipeline.content_adapter.text_adaptation import _adapt_text, _build_jd_summary
from backend.services.ai.pipeline.content_adapter.mapping import _build_adapted_text_map

__all__ = [
    "adapt_content",
    "_adapt_with_llm",
    "_collect_adaptation_tasks",
    "_adapt_single_text_item",
    "_reconstruct_experience",
    "_reconstruct_project",
    "_adapt_text",
    "_build_jd_summary",
    "_build_adapted_text_map",
]
