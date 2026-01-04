"""Job description parsing into a simple target spec."""

from dataclasses import dataclass
from typing import List, Set

from backend.services.ai.text import extract_words, normalize_text


@dataclass(frozen=True)
class TargetSpec:
    required_keywords: Set[str]
    preferred_keywords: Set[str]
    responsibilities: List[str]


_REQUIRED_HINTS = ("must", "required", "requirement", "you will", "we need")
_PREFERRED_HINTS = ("nice to have", "plus", "bonus", "preferred")


def build_target_spec(job_description: str) -> TargetSpec:
    lines = [
        normalize_text(line) for line in job_description.splitlines() if line.strip()
    ]
    required: Set[str] = set()
    preferred: Set[str] = set()
    responsibilities: List[str] = []

    for line in lines:
        words = set(extract_words(line))
        if any(hint in line for hint in _REQUIRED_HINTS):
            required.update(words)
        elif any(hint in line for hint in _PREFERRED_HINTS):
            preferred.update(words)
        if any(
            verb in line
            for verb in (
                "build",
                "design",
                "own",
                "lead",
                "deliver",
                "maintain",
                "improve",
            )
        ):
            responsibilities.append(line[:140])

    if not required and not preferred:
        required = set(extract_words(job_description))

    return TargetSpec(
        required_keywords=required,
        preferred_keywords=preferred,
        responsibilities=responsibilities[:10],
    )
