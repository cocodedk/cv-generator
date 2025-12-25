"""Tests for AI drafting endpoints."""

import pytest
from unittest.mock import patch


@pytest.mark.asyncio
@pytest.mark.api
class TestGenerateCvDraft:
    """Test POST /api/ai/generate-cv endpoint."""

    async def test_generate_cv_draft_success(self, client, sample_cv_data, mock_neo4j_connection):
        profile_data = {
            "personal_info": sample_cv_data["personal_info"],
            "experience": sample_cv_data["experience"],
            "education": sample_cv_data["education"],
            "skills": sample_cv_data["skills"],
            "updated_at": "2024-01-01T00:00:00",
        }
        with patch("backend.database.queries.get_profile", return_value=profile_data):
            response = await client.post(
                "/api/ai/generate-cv",
                json={
                    "job_description": "We require FastAPI and React. You will build and improve web features.",
                    "target_role": "Full-stack Engineer",
                    "seniority": "Senior",
                    "style": "select_and_reorder",
                    "max_experiences": 4,
                },
            )
            assert response.status_code == 200
            data = response.json()
            assert "draft_cv" in data
            assert data["draft_cv"]["personal_info"]["name"] == "John Doe"
            assert data["draft_cv"]["experience"]
            skill_names = {skill["name"] for skill in data["draft_cv"]["skills"]}
            assert "React" in skill_names

    async def test_generate_cv_draft_profile_missing(self, client, mock_neo4j_connection):
        with patch("backend.database.queries.get_profile", return_value=None):
            response = await client.post(
                "/api/ai/generate-cv",
                json={"job_description": "We require FastAPI and React."},
            )
            assert response.status_code == 404
