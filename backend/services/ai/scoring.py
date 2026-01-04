"""Scoring utilities for matching profile items to a job description."""

from dataclasses import dataclass
from typing import Iterable, List, Sequence, Set, Tuple

from backend.services.ai.target_spec import TargetSpec
from backend.services.ai.text import contains_any, extract_words, word_set


@dataclass(frozen=True)
class Score:
    value: float
    keyword_match: float
    responsibility_match: float
    seniority_match: float
    recency: float
    quality_penalty: float


_SENIORITY_SIGNAL_WORDS = (
    "lead",
    "owned",
    "owner",
    "architect",
    "architecture",
    "mentored",
    "mentor",
    "on-call",
    "incident",
    "stakeholder",
    "roadmap",
)


def _overlap_score(
    item_words: Set[str], required: Set[str], preferred: Set[str]
) -> float:
    if not item_words:
        return 0.0
    required_hits = len(item_words.intersection(required))
    preferred_hits = len(item_words.intersection(preferred))
    denom = max(1, len(required) + len(preferred))
    return min(1.0, (2.0 * required_hits + 1.0 * preferred_hits) / (2.0 * denom))


def _responsibility_overlap(item_text: str, responsibilities: Sequence[str]) -> float:
    if not responsibilities:
        return 0.0
    item_words = set(extract_words(item_text))
    matches = 0
    for resp in responsibilities:
        resp_words = set(extract_words(resp))
        if resp_words and len(item_words.intersection(resp_words)) >= 2:
            matches += 1
    return min(1.0, matches / max(1, len(responsibilities)))


def _quality_penalty(text_parts: Iterable[str]) -> float:
    text = " ".join(text_parts).strip()
    if not text:
        return 0.1
    penalty = 0.0
    if len(text) > 800:
        penalty += 0.15
    if any(len(part) > 240 for part in text_parts):
        penalty += 0.1
    if contains_any(text, ("responsible for", "worked on", "helped", "various")):
        penalty += 0.1
    return min(0.3, penalty)


def score_item(
    *,
    text_parts: List[str],
    technologies: Sequence[str],
    start_date: str,
    spec: TargetSpec,
) -> Score:
    item_words = word_set([*text_parts, *technologies])
    keyword_match = _overlap_score(
        item_words, spec.required_keywords, spec.preferred_keywords
    )
    responsibility_match = _responsibility_overlap(
        " ".join(text_parts), spec.responsibilities
    )
    seniority_match = (
        1.0 if contains_any(" ".join(text_parts), _SENIORITY_SIGNAL_WORDS) else 0.0
    )
    recency = (
        1.0 if start_date >= "2022-01" else 0.85 if start_date >= "2019-01" else 0.7
    )
    quality_penalty = _quality_penalty(text_parts)

    value = (
        0.45 * keyword_match
        + 0.25 * responsibility_match
        + 0.15 * seniority_match
        + 0.15 * recency
        - quality_penalty
    )
    return Score(
        value=max(0.0, round(value, 4)),
        keyword_match=keyword_match,
        responsibility_match=responsibility_match,
        seniority_match=seniority_match,
        recency=recency,
        quality_penalty=quality_penalty,
    )


def top_n_scored(
    items: Sequence[Tuple[float, object]], n: int
) -> List[Tuple[float, object]]:
    return sorted(items, key=lambda pair: pair[0], reverse=True)[:n]
