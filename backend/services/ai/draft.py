"""Heuristics-first CV draft generator from saved profile + job description."""

from __future__ import annotations

from backend.models import CVData, ProfileData
from backend.models_ai import AIGenerateCVRequest, AIGenerateCVResponse
from backend.services.ai.review import build_evidence_map, build_questions, build_summary
from backend.services.ai.rewrite import rewrite_cv_bullets
from backend.services.ai.llm_tailor import llm_tailor_cv
from backend.services.ai.selection import (
    select_education,
    select_experiences,
    select_skills,
)
from backend.services.ai.target_spec import build_target_spec


async def generate_cv_draft(profile: ProfileData, request: AIGenerateCVRequest) -> AIGenerateCVResponse:
    spec = build_target_spec(request.job_description)

    max_experiences = request.max_experiences or 4
    selected_experiences, warnings = select_experiences(profile.experience, spec, max_experiences)
    selected_education = select_education(profile.education, spec, max_education=2)
    selected_skills = select_skills(profile.skills, spec, selected_experiences)

    questions = build_questions(selected_experiences)
    summary = build_summary(request, selected_experiences, selected_skills)
    evidence_map = build_evidence_map(spec, selected_experiences)

    draft = CVData(
        personal_info=profile.personal_info,
        experience=selected_experiences,
        education=selected_education,
        skills=selected_skills,
        theme="classic",
    )
    if request.style == "llm_tailor":
        draft = await llm_tailor_cv(draft, request.job_description, profile)
    elif request.style == "rewrite_bullets":
        draft = rewrite_cv_bullets(draft)

    return AIGenerateCVResponse(
        draft_cv=draft,
        warnings=warnings,
        questions=questions,
        summary=summary,
        evidence_map=evidence_map,
    )
