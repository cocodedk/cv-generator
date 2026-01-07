"""CV draft generator using multi-step AI pipeline."""

from __future__ import annotations

import logging
from typing import Optional

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
from backend.services.ai.pipeline.context_analyzer import analyze_additional_context
from backend.services.ai.pipeline.content_incorporator import incorporate_context
from backend.services.ai.pipeline.models import ContextAnalysis, ContextIncorporation

logger = logging.getLogger(__name__)


async def generate_cv_draft(
    profile: ProfileData, request: AIGenerateCVRequest
) -> AIGenerateCVResponse:
    """
    Generate CV draft using multi-step AI pipeline.

    Steps:
    0. Analyze additional_context (if provided) to determine how to incorporate it
    1. Analyze JD to extract requirements
    2. Evaluate skills for relevance
    3. Select relevant content from profile
    4. Adapt content for JD
    5. Assemble final CV
    6. Incorporate additional_context content (if applicable)
    """
    logger.info(f"Starting CV generation pipeline for {len(profile.experience)} experiences, {len(profile.skills)} skills")

    # Step 0: Analyze additional_context intelligently
    context_analysis: Optional[ContextAnalysis] = None
    context_incorporation: Optional[ContextIncorporation] = None

    if request.additional_context:
        logger.info("Step 0: Analyzing additional_context")
        context_analysis = await analyze_additional_context(
            request.additional_context,
            request.job_description,
        )
        logger.info(
            f"Context analysis: type={context_analysis.type}, "
            f"placement={context_analysis.placement}"
        )

    # Determine if we should use additional_context as directive
    # Use as directive if: (1) llm_tailor style, OR (2) analysis says it's a directive
    use_directive = (
        (request.style == "llm_tailor" and request.additional_context) or
        (context_analysis and context_analysis.type == "directive")
    )

    # Step 1: Analyze JD
    logger.info("Step 1: Analyzing job description")
    jd_analysis = await analyze_jd(
        request.job_description,
        additional_context=request.additional_context if use_directive else None,
    )
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
        additional_context=request.additional_context if use_directive else None,
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
        additional_context=request.additional_context if use_directive else None,
    )
    logger.info(f"Selected {len(selection_result.experiences)} experiences")

    # Step 4: Adapt content
    logger.info("Step 4: Adapting content wording")
    # For llm_tailor style, pass context as directive; for other styles, use existing behavior
    adapted_content = await adapt_content(
        selection_result,
        jd_analysis,
        request.additional_context if use_directive else (request.additional_context if request.style == "select_and_reorder" else None),
    )
    logger.info(
        f"Content adaptation complete: {len(adapted_content.adaptation_notes)} items adapted, "
        f"{len(adapted_content.warnings)} warnings"
    )
    warnings = adapted_content.warnings or []

    # Step 5: Assemble CV
    # Build context incorporation if needed (for content_statement or achievement types)
    if context_analysis and context_analysis.type in ("content_statement", "achievement", "mixed"):
        from backend.services.ai.pipeline.content_incorporator import _build_incorporation
        context_incorporation = _build_incorporation(
            context_analysis,
            selection_result.experiences,
        )
        logger.info(
            f"Built context incorporation: summary={bool(context_incorporation.summary_update)}, "
            f"highlights={len(context_incorporation.project_highlights)}, "
            f"experiences={len(context_incorporation.experience_updates)}"
        )

    draft_cv, coverage_summary = assemble_cv(
        adapted_content,
        profile.personal_info,
        profile.education,
        profile.skills,
        skill_mapping,
        jd_analysis,
        context_incorporation,
    )

    # Step 6: Incorporate context (if not already incorporated in assembler)
    # Note: Currently incorporation happens in assembler, but keeping this step
    # for potential future enhancements or fallback logic

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
