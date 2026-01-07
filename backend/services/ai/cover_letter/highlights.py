"""Highlight extraction utilities."""

from typing import List

from backend.models import ProfileData


def _extract_highlights_used(profile: ProfileData, job_description: str) -> List[str]:
    """Extract which profile highlights were likely used based on JD keywords."""
    highlights = []
    jd_lower = job_description.lower()

    # Check experience highlights
    for exp in profile.experience[:3]:
        for project in exp.projects[:2]:
            for highlight in project.highlights[:2]:
                # Simple keyword matching
                highlight_lower = highlight.lower()
                # Check if any word from JD appears in highlight (partial matches)
                if any(word in highlight_lower for word in jd_lower.split()):
                    highlights.append(highlight)

    return highlights[:5]  # Limit to top 5
