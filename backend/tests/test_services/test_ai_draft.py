"""Unit tests for heuristics-based AI drafting."""

import pytest

from backend.models import ProfileData
from backend.models_ai import AIGenerateCVRequest
from backend.services.ai.draft import generate_cv_draft


@pytest.mark.unit
class TestAIDraftGenerator:
    def test_trims_projects_and_highlights(self, sample_cv_data):
        profile_dict = {
            "personal_info": sample_cv_data["personal_info"],
            "experience": [
                {
                    "title": "Engineer",
                    "company": "Example",
                    "start_date": "2023-01",
                    "end_date": "Present",
                    "description": "Built and improved web services.",
                    "location": "Remote",
                    "projects": [
                        {
                            "name": f"Project {i}",
                            "description": "FastAPI and React work",
                            "technologies": ["FastAPI", "React"],
                            "highlights": [f"Did thing {n} for project {i}" for n in range(8)],
                        }
                        for i in range(5)
                    ],
                }
            ],
            "education": sample_cv_data["education"],
            "skills": sample_cv_data["skills"],
        }
        profile = ProfileData.model_validate(profile_dict)
        request = AIGenerateCVRequest(
            job_description="We require FastAPI and React. You will build and improve web features.",
            max_experiences=1,
            style="select_and_reorder",
        )

        result = generate_cv_draft(profile, request)
        assert len(result.draft_cv.experience) == 1
        assert len(result.draft_cv.experience[0].projects) <= 2
        assert all(len(project.highlights) <= 3 for project in result.draft_cv.experience[0].projects)

    def test_rewrite_style_applies_safe_transforms(self, sample_cv_data):
        profile_dict = {
            "personal_info": sample_cv_data["personal_info"],
            "experience": [
                {
                    "title": "Engineer",
                    "company": "Example",
                    "start_date": "2023-01",
                    "end_date": "Present",
                    "projects": [
                        {
                            "name": "API Platform",
                            "technologies": ["FastAPI"],
                            "highlights": ["Responsible for building APIs."],
                        }
                    ],
                }
            ],
            "education": [],
            "skills": [{"name": "FastAPI"}],
        }
        profile = ProfileData.model_validate(profile_dict)
        request = AIGenerateCVRequest(
            job_description="Must have FastAPI. Build APIs.",
            max_experiences=1,
            style="rewrite_bullets",
        )

        result = generate_cv_draft(profile, request)
        highlight = result.draft_cv.experience[0].projects[0].highlights[0]
        assert highlight == "Building APIs"
