"""CV draft generator using multi-step AI pipeline."""

from __future__ import annotations

import logging

from backend.models import ProfileData
from backend.models_ai import AIGenerateCVRequest, AIGenerateCVResponse
from backend.services.ai.review import (
    build_evidence_map,
    build_questions,
    build_summary,
)
from backend.services.ai.pipeline.jd_analyzer import analyze_jd
from backend.services.ai.pipeline.skill_relevance_evaluator import evaluate_all_skills
from backend.services.ai.pipeline.content_selector import select_content
from backend.services.ai.pipeline.content_adapter import adapt_content
from backend.services.ai.pipeline.cv_assembler import assemble_cv

logger = logging.getLogger(__name__)


async def generate_cv_draft(
    profile: ProfileData, request: AIGenerateCVRequest
) -> AIGenerateCVResponse:
    """
    Generate CV draft using multi-step AI pipeline.

    Steps:
    1. Analyze JD to extract requirements
    2. Evaluate skills for relevance
    3. Select relevant content from profile
    4. Adapt content for JD
    5. Assemble final CV
    """
    logger.info(f"Starting CV generation pipeline for {len(profile.experience)} experiences, {len(profile.skills)} skills")

    # Step 1: Analyze JD
    logger.info("Step 1: Analyzing job description")
    jd_analysis = await analyze_jd(request.job_description)
    logger.info(
        f"JD Analysis: {len(jd_analysis.required_skills)} required skills, "
        f"{len(jd_analysis.preferred_skills)} preferred skills, "
        f"{len(jd_analysis.responsibilities)} responsibilities"
    )

    # Step 2: Evaluate each skill individually for relevance
    logger.info("Step 2: Evaluating skill relevance")
    skill_mapping = await evaluate_all_skills(
        profile.skills,
        jd_analysis,
        raw_jd=request.job_description,
    )
    logger.info(
        f"Skill mapping: {len(skill_mapping.matched_skills)} matched skills, "
        f"{len(skill_mapping.coverage_gaps)} gaps"
    )

    # Step 3: Select content
    logger.info("Step 3: Selecting relevant content")
    max_experiences = request.max_experiences or 4
    selection_result = select_content(
        profile.experience,
        jd_analysis,
        skill_mapping,
        max_experiences=max_experiences,
    )
    logger.info(f"Selected {len(selection_result.experiences)} experiences")

    # Step 4: Adapt content
    logger.info("Step 4: Adapting content wording")
    adapted_content = await adapt_content(
        selection_result,
        jd_analysis,
        request.additional_context,
    )
    logger.info(
        f"Content adaptation complete: {len(adapted_content.adaptation_notes)} items adapted, "
        f"{len(adapted_content.warnings)} warnings"
    )
    warnings = adapted_content.warnings or []

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

    # Build evidence map
    class SimpleSpec:
        def __init__(self, jd):
            self.required_keywords = jd.required_skills
            self.preferred_keywords = jd.preferred_skills
            self.responsibilities = jd.responsibilities

    spec = SimpleSpec(jd_analysis)
    evidence_map = build_evidence_map(spec, draft_cv.experience)

    return AIGenerateCVResponse(
        draft_cv=draft_cv,
        warnings=warnings,
        questions=questions,
        summary=summary_items,
        evidence_map=evidence_map,
    )
