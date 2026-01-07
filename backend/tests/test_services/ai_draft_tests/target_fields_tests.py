"""Tests for target company and role fields functionality."""

import pytest

from backend.models import ProfileData
from backend.models_ai import AIGenerateCVRequest
from backend.services.ai.draft import generate_cv_draft


@pytest.mark.unit
class TestTargetFields:
    @pytest.mark.asyncio
    async def test_target_company_and_role_included_in_draft(self, sample_cv_data):
        """Test that target_company and target_role from request are included in draft CV."""
        profile_dict = {
            "personal_info": sample_cv_data["personal_info"],
            "experience": sample_cv_data["experience"],
            "education": sample_cv_data["education"],
            "skills": sample_cv_data["skills"],
        }
        profile = ProfileData.model_validate(profile_dict)
        request = AIGenerateCVRequest(
            job_description="We require FastAPI and React. You will build and improve web features.",
            target_company="Google",
            target_role="Senior Developer",
        )

        result = await generate_cv_draft(profile, request)
        assert result.draft_cv.target_company == "Google"
        assert result.draft_cv.target_role == "Senior Developer"

    @pytest.mark.asyncio
    async def test_target_company_and_role_none_when_not_provided(self, sample_cv_data):
        """Test that target_company and target_role are None when not provided in request."""
        profile_dict = {
            "personal_info": sample_cv_data["personal_info"],
            "experience": sample_cv_data["experience"],
            "education": sample_cv_data["education"],
            "skills": sample_cv_data["skills"],
        }
        profile = ProfileData.model_validate(profile_dict)
        request = AIGenerateCVRequest(
            job_description="We require FastAPI and React. You will build and improve web features.",
        )

        result = await generate_cv_draft(profile, request)
        assert result.draft_cv.target_company is None
        assert result.draft_cv.target_role is None
