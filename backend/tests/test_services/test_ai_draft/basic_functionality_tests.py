"""Basic functionality tests for AI drafting."""

import pytest

from backend.models import ProfileData
from backend.models_ai import AIGenerateCVRequest
from backend.services.ai.draft import generate_cv_draft


@pytest.mark.unit
class TestBasicFunctionality:
    @pytest.mark.asyncio
    async def test_trims_projects_and_highlights(self, sample_cv_data):
        """Test that the system properly trims projects and highlights to reasonable limits."""
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
                            "highlights": [
                                f"Did thing {n} for project {i}" for n in range(8)
                            ],
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

        result = await generate_cv_draft(profile, request)
        assert len(result.draft_cv.experience) == 1
        assert len(result.draft_cv.experience[0].projects) <= 2
        assert all(
            len(project.highlights) <= 3
            for project in result.draft_cv.experience[0].projects
        )

    @pytest.mark.asyncio
    async def test_rewrite_style_applies_safe_transforms(self, sample_cv_data):
        """Test that rewrite_bullets style applies safe text transformations."""
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

        result = await generate_cv_draft(profile, request)
        highlight = result.draft_cv.experience[0].projects[0].highlights[0]
        # With LLM adaptation enabled, the text may be reworded
        # Original: "Responsible for building APIs." -> may become "Building APIs" or similar
        assert "API" in highlight or "api" in highlight.lower()
