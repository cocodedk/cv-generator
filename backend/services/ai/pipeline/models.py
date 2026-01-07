"""Data models for pipeline steps."""

from dataclasses import dataclass, field
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
    match_type: str  # "exact", "synonym", "related", "covers", "ecosystem", "responsibility_support", "domain_complement", "category_match"
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
    warnings: List[str] = None  # Issues encountered during adaptation (e.g. char limit overruns)


@dataclass(frozen=True)
class SkillRelevanceResult:
    """Result of AI evaluation for a single skill's relevance to JD."""

    relevant: bool
    relevance_type: str  # "direct", "foundation", "alternative", "related"
    why: str  # Explanation of relevance
    match: str  # Which JD requirement it matches


@dataclass(frozen=True)
class CoverageSummary:
    """Summary of how CV covers JD requirements."""

    covered_requirements: List[str]
    partially_covered: List[str]
    gaps: List[str]
    skill_justifications: Dict[str, str]  # skill_name -> why included


@dataclass(frozen=True)
class ContextAnalysis:
    """Analysis of additional_context to determine how to incorporate it."""

    type: str  # "directive", "content_statement", "achievement", or "mixed"
    placement: str  # "summary", "project_highlight", "experience_description", or "adaptation_guidance"
    suggested_text: str  # How to phrase this for the CV
    reasoning: str  # Why this placement


@dataclass(frozen=True)
class ContextIncorporation:
    """Instructions for incorporating additional_context into CV."""

    summary_update: Optional[str] = None  # Text to add/update in summary
    project_highlights: List[tuple[int, int, str]] = field(default_factory=list)  # List of (exp_idx, proj_idx, highlight_text)
    experience_updates: Dict[int, str] = field(default_factory=dict)  # Maps exp_idx -> updated description text
