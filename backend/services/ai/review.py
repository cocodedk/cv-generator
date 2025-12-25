"""Review metadata for generated CV drafts (summary, questions, evidence map)."""

from __future__ import annotations

from typing import List, Optional

from backend.models import Experience, Skill
from backend.models_ai import EvidenceItem, EvidenceMapping, AIGenerateCVRequest
from backend.services.ai.text import normalize_text


def build_summary(request: AIGenerateCVRequest, experiences: List[Experience], skills: List[Skill]) -> List[str]:
    items: List[str] = []
    if request.target_role:
        items.append(f"Target role: {request.target_role}")
    if request.seniority:
        items.append(f"Seniority: {request.seniority}")
    items.append(f"Selected {len(experiences)} experience(s) and {len(skills)} skill(s) for JD match.")
    return items


def build_questions(experiences: List[Experience]) -> List[str]:
    if not experiences:
        return ["Add at least one experience with projects/highlights to tailor against the job description."]

    has_numbers = any(
        any(
            any(any(char.isdigit() for char in highlight) for highlight in project.highlights)
            for project in exp.projects
        )
        for exp in experiences
    )
    if has_numbers:
        return []
    return ["Any measurable outcomes (performance, reliability, cost, adoption) you can add to 1–2 top highlights?"]


def build_evidence_map(spec, experiences: List[Experience]) -> Optional[List[EvidenceMapping]]:
    requirements = list(sorted(spec.required_keywords))[:8]
    if not requirements or not experiences:
        return None

    mappings: List[EvidenceMapping] = []
    for requirement in requirements:
        evidence: List[EvidenceItem] = []
        for exp_index, experience in enumerate(experiences):
            for proj_index, project in enumerate(experience.projects):
                for hl_index, highlight in enumerate(project.highlights):
                    if requirement in normalize_text(highlight):
                        evidence.append(
                            EvidenceItem(
                                path=f"experience[{exp_index}].projects[{proj_index}].highlights[{hl_index}]",
                                quote=highlight[:300],
                            )
                        )
        if evidence:
            mappings.append(EvidenceMapping(requirement=requirement, evidence=evidence[:3]))

    return mappings or None
