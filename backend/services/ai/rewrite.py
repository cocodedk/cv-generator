"""Lightweight, non-LLM rewrites for bullets (safe transformations only)."""

from __future__ import annotations

from typing import List

from backend.models import CVData, Experience, Project


_SAFE_PREFIX_REWRITES = {
    "responsible for ": "",
    "worked on ": "",
    "helped ": "",
}


def rewrite_cv_bullets(cv: CVData) -> CVData:
    rewritten_experiences: List[Experience] = []
    for experience in cv.experience:
        rewritten_projects: List[Project] = []
        for project in (experience.projects or []):
            rewritten_highlights = [_rewrite_highlight(highlight) for highlight in (project.highlights or [])]
            rewritten_projects.append(Project(**project.model_dump(exclude={"highlights"}), highlights=rewritten_highlights))
        rewritten_experiences.append(Experience(**experience.model_dump(exclude={"projects"}), projects=rewritten_projects))

    return CVData(
        personal_info=cv.personal_info,
        experience=rewritten_experiences,
        education=cv.education,
        skills=cv.skills,
        theme=cv.theme,
    )


def _rewrite_highlight(value: str) -> str:
    text = value.strip()
    lowered = text.lower()
    for prefix, replacement in _SAFE_PREFIX_REWRITES.items():
        if lowered.startswith(prefix):
            text = replacement + text[len(prefix) :]
            break
    text = text.strip()
    if text.endswith("."):
        text = text[:-1].strip()
    if text:
        text = text[0].upper() + text[1:]
    return text
