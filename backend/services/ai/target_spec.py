"""Target specification type for scoring."""

from dataclasses import dataclass
from typing import List, Set


@dataclass(frozen=True)
class TargetSpec:
    """Specification of target job requirements for scoring."""
    required_keywords: Set[str]
    preferred_keywords: Set[str]
    responsibilities: List[str]
