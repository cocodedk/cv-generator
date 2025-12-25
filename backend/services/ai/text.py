"""Text helpers for AI heuristics."""

import re
from typing import Iterable, List, Set


_WORD_RE = re.compile(r"[a-zA-Z][a-zA-Z0-9.+#/-]*")


def normalize_text(value: str) -> str:
    return value.lower().strip()


def extract_words(text: str) -> List[str]:
    return [normalize_text(word) for word in _WORD_RE.findall(text)]


def word_set(parts: Iterable[str]) -> Set[str]:
    words: Set[str] = set()
    for part in parts:
        words.update(extract_words(part))
    return words


def contains_any(text: str, needles: Iterable[str]) -> bool:
    lowered = normalize_text(text)
    return any(needle in lowered for needle in needles)
