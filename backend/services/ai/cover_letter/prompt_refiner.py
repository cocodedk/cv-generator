"""Prompt refinement utilities for cover letter generation."""

from __future__ import annotations

import logging

from backend.services.ai.llm_client import LLMClient

logger = logging.getLogger(__name__)


def _build_prompt_refiner_request(base_prompt: str, llm_instructions: str) -> str:
    """Build a prompt that asks the LLM to rewrite the base prompt with overrides."""
    return f"""You are an expert prompt engineer.

TASK:
- Rewrite the BASE PROMPT so that it fully incorporates the USER INSTRUCTIONS.
- Treat USER INSTRUCTIONS as mandatory overrides for any conflicting requirements.
- Preserve all non-conflicting requirements from the base prompt.
- Output ONLY the revised prompt text. No commentary, no markdown.

BASE PROMPT:
<<<
{base_prompt}
>>>

USER INSTRUCTIONS:
<<<
{llm_instructions}
>>>
"""


def _strip_code_fences(text: str) -> str:
    """Remove markdown code fences if present."""
    if not text.startswith("```"):
        return text
    lines = text.split("\n")
    fence_indices = [i for i, line in enumerate(lines) if line.strip().startswith("```")]
    if len(fence_indices) >= 2:
        start = fence_indices[0] + 1
        end = fence_indices[1]
        return "\n".join(lines[start:end]).strip()
    if len(fence_indices) == 1:
        return "\n".join(lines[fence_indices[0] + 1 :]).strip()
    return text


async def refine_cover_letter_prompt(
    base_prompt: str,
    llm_instructions: str,
    llm_client: LLMClient,
) -> str:
    """Use the LLM to refine the base prompt with user instructions."""
    refiner_prompt = _build_prompt_refiner_request(
        base_prompt=base_prompt, llm_instructions=llm_instructions
    )

    refined_prompt = await llm_client.generate_text(
        refiner_prompt,
        system_prompt=(
            "You are a precise prompt optimizer. "
            "Return only the revised prompt text."
        ),
    )
    refined_prompt = _strip_code_fences(refined_prompt.strip())

    if not refined_prompt:
        raise ValueError("Prompt refinement returned empty output")

    return refined_prompt
