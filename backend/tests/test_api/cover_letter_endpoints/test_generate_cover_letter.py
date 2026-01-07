"""Tests for POST /api/ai/generate-cover-letter endpoint."""

import pytest
from unittest.mock import patch, AsyncMock, Mock
from backend.services.ai.cover_letter_selection import SelectedContent


@pytest.mark.asyncio
@pytest.mark.api
class TestGenerateCoverLetter:
    """Test POST /api/ai/generate-cover-letter endpoint."""

    async def test_generate_cover_letter_success(
        self, client, sample_cv_data, mock_neo4j_connection
    ):
        """Test successful cover letter generation."""
        profile_data = {
            "personal_info": sample_cv_data["personal_info"],
            "experience": sample_cv_data["experience"],
            "education": sample_cv_data["education"],
            "skills": sample_cv_data["skills"],
            "updated_at": "2024-01-01T00:00:00",
        }

        mock_llm_client = Mock()
        mock_llm_client.is_configured.return_value = True
        mock_llm_client.model = "gpt-3.5-turbo"
        mock_llm_client.api_key = "test-key"
        mock_llm_client.base_url = "https://api.test.com"
        mock_llm_client.timeout = 30
        mock_llm_client.generate_text = AsyncMock(
            return_value="Dear John Doe,\n\nI am writing to express my interest in the position..."
        )

        selected_content = SelectedContent(
            experience_indices=[],
            skill_names=["Python", "React"],
            key_highlights=[],
            relevance_reasoning="Test",
        )

        with patch(
            "backend.database.queries.get_profile",
            return_value=profile_data,
        ):
            with patch(
                "backend.services.ai.cover_letter.generation.get_llm_client",
                return_value=mock_llm_client,
            ):
                with patch(
                    "backend.services.ai.cover_letter.generation.select_relevant_content",
                    return_value=selected_content,
                ):
                    response = await client.post(
                        "/api/ai/generate-cover-letter",
                        json={
                            "job_description": "We are looking for a Senior Developer with Python and React experience.",
                            "company_name": "Tech Corp",
                            "hiring_manager_name": "John Doe",
                            "company_address": "123 Tech Street\nSan Francisco, CA 94102",
                            "tone": "professional",
                        },
                    )

                    assert response.status_code == 200
                    data = response.json()
                    assert "cover_letter_html" in data
                    assert "cover_letter_text" in data
                    assert "highlights_used" in data
                    assert "selected_experiences" in data
                    assert "selected_skills" in data
                    assert "John Doe" in data["cover_letter_html"]
                    assert "Tech Corp" in data["cover_letter_html"]

    async def test_generate_cover_letter_profile_missing(
        self, client, mock_neo4j_connection
    ):
        """Test cover letter generation when profile is missing."""
        with patch(
            "backend.database.queries.get_profile",
            return_value=None,
        ):
            response = await client.post(
                "/api/ai/generate-cover-letter",
                json={
                    "job_description": "We need a developer.",
                    "company_name": "Tech Corp",
                    "tone": "professional",
                },
            )
            assert response.status_code == 404
            assert "Profile not found" in response.json()["detail"]

    async def test_generate_cover_letter_validation_error(self, client):
        """Test cover letter generation with invalid request."""
        response = await client.post(
            "/api/ai/generate-cover-letter",
            json={
                "job_description": "Short",  # Too short
                "company_name": "Tech Corp",
            },
        )
        assert response.status_code == 422

    async def test_generate_cover_letter_missing_required_fields(self, client):
        """Test cover letter generation with missing required fields."""
        response = await client.post(
            "/api/ai/generate-cover-letter",
            json={
                "job_description": "We need a developer with Python experience.",
                # Missing company_name
            },
        )
        assert response.status_code == 422

    async def test_generate_cover_letter_llm_not_configured(
        self, client, sample_cv_data, mock_neo4j_connection
    ):
        """Test cover letter generation when LLM is not configured."""
        profile_data = {
            "personal_info": sample_cv_data["personal_info"],
            "experience": sample_cv_data["experience"],
            "education": sample_cv_data["education"],
            "skills": sample_cv_data["skills"],
            "updated_at": "2024-01-01T00:00:00",
        }

        mock_llm_client = Mock()
        mock_llm_client.is_configured.return_value = False

        with patch(
            "backend.database.queries.get_profile",
            return_value=profile_data,
        ):
            with patch(
                "backend.services.ai.cover_letter.generation.get_llm_client",
                return_value=mock_llm_client,
            ):
                response = await client.post(
                    "/api/ai/generate-cover-letter",
                    json={
                        "job_description": "We need a developer with Python experience.",
                        "company_name": "Tech Corp",
                        "tone": "professional",
                    },
                )

                assert response.status_code == 400
                data = response.json()
                assert "LLM" in data["detail"] and "configure" in data["detail"].lower()

    async def test_generate_cover_letter_optional_fields(
        self, client, sample_cv_data, mock_neo4j_connection
    ):
        """Test cover letter generation with optional fields omitted."""
        profile_data = {
            "personal_info": sample_cv_data["personal_info"],
            "experience": sample_cv_data["experience"],
            "education": sample_cv_data["education"],
            "skills": sample_cv_data["skills"],
            "updated_at": "2024-01-01T00:00:00",
        }

        mock_llm_client = Mock()
        mock_llm_client.is_configured.return_value = True
        mock_llm_client.model = "gpt-3.5-turbo"
        mock_llm_client.api_key = "test-key"
        mock_llm_client.base_url = "https://api.test.com"
        mock_llm_client.timeout = 30
        mock_llm_client.generate_text = AsyncMock(
            return_value="Dear Hiring Manager,\n\nTest letter."
        )

        selected_content = SelectedContent(
            experience_indices=[],
            skill_names=[],
            key_highlights=[],
            relevance_reasoning="Test",
        )

        with patch(
            "backend.database.queries.get_profile",
            return_value=profile_data,
        ):
            with patch(
                "backend.services.ai.cover_letter.generation.get_llm_client",
                return_value=mock_llm_client,
            ):
                with patch(
                    "backend.services.ai.cover_letter.generation.select_relevant_content",
                    return_value=selected_content,
                ):
                    response = await client.post(
                        "/api/ai/generate-cover-letter",
                        json={
                            "job_description": "We need a developer with Python experience.",
                            "company_name": "Tech Corp",
                            # Optional fields omitted
                        },
                    )

                    assert response.status_code == 200
                    data = response.json()
                    assert "cover_letter_html" in data
