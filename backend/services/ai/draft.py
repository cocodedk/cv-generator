"""Heuristics-first CV draft generator from saved profile + job description."""

from __future__ import annotations

import logging

from backend.models import CVData, ProfileData
from backend.models_ai import AIGenerateCVRequest, AIGenerateCVResponse
from backend.services.ai.review import (
    build_evidence_map,
    build_questions,
    build_summary,
)
from backend.services.ai.rewrite import rewrite_cv_bullets
from backend.services.ai.llm_tailor import llm_tailor_cv
from backend.services.ai.selection import (
    select_education,
    select_experiences,
    select_skills,
)
from backend.services.ai.target_spec import build_target_spec
from backend.services.ai.pipeline.jd_analyzer import analyze_jd
from backend.services.ai.pipeline.skill_mapper import map_skills
from backend.services.ai.pipeline.content_selector import select_content
from backend.services.ai.pipeline.content_adapter import adapt_content
from backend.services.ai.pipeline.cv_assembler import assemble_cv

logger = logging.getLogger(__name__)


async def generate_cv_draft(
    profile: ProfileData, request: AIGenerateCVRequest
) -> AIGenerateCVResponse:
    """
    Generate CV draft using multi-step AI pipeline.

    Uses new pipeline when style is 'llm_tailor', falls back to legacy for other styles.
    """
    # Use new pipeline for llm_tailor style
    if request.style == "llm_tailor":
        return await _generate_with_pipeline(profile, request)

    # Legacy flow for other styles
    return await _generate_legacy(profile, request)


async def _generate_with_pipeline(
    profile: ProfileData, request: AIGenerateCVRequest
) -> AIGenerateCVResponse:
    """Generate CV using the new multi-step pipeline."""

    # Step 1: Analyze JD
    jd_analysis = await analyze_jd(request.job_description)

    # Step 2: Map skills
    skill_mapping = await map_skills(profile.skills, jd_analysis)

    # Step 3: Select content
    max_experiences = request.max_experiences or 4
    selection_result = select_content(
        profile.experience,
        jd_analysis,
        skill_mapping,
        max_experiences=max_experiences,
    )

    # Step 4: Adapt content
    adapted_content = await adapt_content(
        selection_result,
        jd_analysis,
        request.additional_context,
    )

    # Step 5: Assemble CV
    draft_cv, coverage_summary = assemble_cv(
        adapted_content,
        profile.personal_info,
        profile.education,
        profile.skills,
        skill_mapping,
        jd_analysis,
    )

    # Set target company and role from request
    draft_cv.target_company = request.target_company
    draft_cv.target_role = request.target_role

    # Build review metadata
    questions = build_questions(draft_cv.experience)

    # Enhanced summary with coverage info
    summary_items = build_summary(request, draft_cv.experience, draft_cv.skills)
    if coverage_summary.covered_requirements:
        summary_items.append(
            f"Covered {len(coverage_summary.covered_requirements)} JD requirements"
        )
    if coverage_summary.gaps:
        summary_items.append(f"{len(coverage_summary.gaps)} requirements not fully covered")

    # Build evidence map (using legacy function for compatibility)
    class SimpleSpec:
        def __init__(self, jd):
            self.required_keywords = jd.required_skills
            self.preferred_keywords = jd.preferred_skills
            self.responsibilities = jd.responsibilities

    spec = SimpleSpec(jd_analysis)
    evidence_map = build_evidence_map(spec, draft_cv.experience)

    return AIGenerateCVResponse(
        draft_cv=draft_cv,
        warnings=[],
        questions=questions,
        summary=summary_items,
        evidence_map=evidence_map,
    )


async def _generate_legacy(
    profile: ProfileData, request: AIGenerateCVRequest
) -> AIGenerateCVResponse:
    """Legacy CV generation flow for non-llm_tailor styles."""
    spec = build_target_spec(request.job_description)

    max_experiences = request.max_experiences or 4
    selected_experiences, warnings = select_experiences(
        profile.experience, spec, max_experiences
    )
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
        target_company=request.target_company,
        target_role=request.target_role,
    )
    if request.style == "rewrite_bullets":
        draft = rewrite_cv_bullets(draft)

    return AIGenerateCVResponse(
        draft_cv=draft,
        warnings=warnings,
        questions=questions,
        summary=summary,
        evidence_map=evidence_map,
    )
