"""Data models for pipeline steps."""

from dataclasses import dataclass
from typing import List, Set, Dict, Optional
from backend.models import Experience, Skill


@dataclass(frozen=True)
class JDAnalysis:
    """Structured analysis of job description requirements."""

    required_skills: Set[str]
    preferred_skills: Set[str]
    responsibilities: List[str]
    domain_keywords: Set[str]
    seniority_signals: List[str]


@dataclass(frozen=True)
class SkillMatch:
    """Represents how a profile skill matches a JD requirement."""

    profile_skill: Skill
    jd_requirement: str
    match_type: str  # "exact", "synonym", "related", "covers"
    confidence: float  # 0.0 to 1.0
    explanation: str  # Why this match was made


@dataclass(frozen=True)
class SkillMapping:
    """Mapping of profile skills to JD requirements."""

    matched_skills: List[SkillMatch]
    selected_skills: List[Skill]  # Skills to include in CV
    coverage_gaps: List[str]  # JD requirements not covered


@dataclass(frozen=True)
class SelectionResult:
    """Result of content selection from profile."""

    experiences: List[Experience]
    selected_indices: Dict[str, List[int]]  # Maps experience_id -> [project_indices, highlight_indices]


@dataclass(frozen=True)
class AdaptedContent:
    """Content after adaptation for JD."""

    experiences: List[Experience]
    adaptation_notes: Dict[str, str]  # Maps content_id -> what was changed


@dataclass(frozen=True)
class CoverageSummary:
    """Summary of how CV covers JD requirements."""

    covered_requirements: List[str]
    partially_covered: List[str]
    gaps: List[str]
    skill_justifications: Dict[str, str]  # skill_name -> why included
