"""Tests for AI drafting endpoints."""

import pytest
from unittest.mock import patch, AsyncMock


@pytest.mark.asyncio
@pytest.mark.api
class TestGenerateCvDraft:
    """Test POST /api/ai/generate-cv endpoint."""

    async def test_generate_cv_draft_success(
        self, client, sample_cv_data, mock_neo4j_connection
    ):
        profile_data = {
            "personal_info": sample_cv_data["personal_info"],
            "experience": sample_cv_data["experience"],
            "education": sample_cv_data["education"],
            "skills": sample_cv_data["skills"],
            "updated_at": "2024-01-01T00:00:00",
        }
        with patch(
            "backend.app_helpers.routes.ai.queries.get_profile",
            return_value=profile_data,
        ):
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

    async def test_generate_cv_draft_profile_missing(
        self, client, mock_neo4j_connection
    ):
        with patch(
            "backend.app_helpers.routes.ai.queries.get_profile", return_value=None
        ):
            response = await client.post(
                "/api/ai/generate-cv",
                json={"job_description": "We require FastAPI and React."},
            )
            assert response.status_code == 404

    async def test_generate_cv_draft_llm_tailor_style(
        self, client, sample_cv_data, mock_neo4j_connection
    ):
        """Test generate-cv with llm_tailor style."""
        profile_data = {
            "personal_info": sample_cv_data["personal_info"],
            "experience": sample_cv_data["experience"],
            "education": sample_cv_data["education"],
            "skills": sample_cv_data["skills"],
            "updated_at": "2024-01-01T00:00:00",
        }

        from unittest.mock import Mock

        mock_llm_client = Mock()
        mock_llm_client.is_configured.return_value = True
        mock_llm_client.rewrite_text = AsyncMock(return_value="Tailored text")

        with patch(
            "backend.app_helpers.routes.ai.queries.get_profile",
            return_value=profile_data,
        ):
            with patch(
                "backend.services.ai.llm_tailor.get_llm_client",
                return_value=mock_llm_client,
            ):
                response = await client.post(
                    "/api/ai/generate-cv",
                    json={
                        "job_description": "We require FastAPI and React. You will build and improve web features.",
                        "style": "llm_tailor",
                        "max_experiences": 4,
                    },
                )
                assert response.status_code == 200
                data = response.json()
                assert "draft_cv" in data
                assert data["draft_cv"]["personal_info"]["name"] == "John Doe"
                # Verify LLM was called for tailoring
                assert mock_llm_client.rewrite_text.called

    async def test_generate_cv_draft_llm_tailor_fallback(
        self, client, sample_cv_data, mock_neo4j_connection
    ):
        """Test llm_tailor style falls back gracefully when LLM not configured."""
        profile_data = {
            "personal_info": sample_cv_data["personal_info"],
            "experience": sample_cv_data["experience"],
            "education": sample_cv_data["education"],
            "skills": sample_cv_data["skills"],
            "updated_at": "2024-01-01T00:00:00",
        }

        from unittest.mock import Mock

        mock_llm_client = Mock()
        mock_llm_client.is_configured.return_value = False

        with patch(
            "backend.app_helpers.routes.ai.queries.get_profile",
            return_value=profile_data,
        ):
            with patch(
                "backend.services.ai.llm_tailor.get_llm_client",
                return_value=mock_llm_client,
            ):
                response = await client.post(
                    "/api/ai/generate-cv",
                    json={
                        "job_description": "We require FastAPI and React.",
                        "style": "llm_tailor",
                    },
                )
                # Should still succeed, just without LLM tailoring
                assert response.status_code == 200
                assert "draft_cv" in response.json()
                # LLM should not have been called
                mock_llm_client.rewrite_text.assert_not_called()

    async def test_generate_cv_draft_with_additional_context(
        self, client, sample_cv_data, mock_neo4j_connection
    ):
        """Test generate-cv endpoint accepts and uses additional_context."""
        profile_data = {
            "personal_info": sample_cv_data["personal_info"],
            "experience": sample_cv_data["experience"],
            "education": sample_cv_data["education"],
            "skills": sample_cv_data["skills"],
            "updated_at": "2024-01-01T00:00:00",
        }

        with patch(
            "backend.app_helpers.routes.ai.queries.get_profile",
            return_value=profile_data,
        ):
            response = await client.post(
                "/api/ai/generate-cv",
                json={
                    "job_description": "We require FastAPI and React. You will build and improve web features.",
                    "additional_context": "Rated among top 2% of AI coders in 2025",
                    "style": "select_and_reorder",
                },
            )
            assert response.status_code == 200
            data = response.json()
            assert "draft_cv" in data
            # Check that additional_context appears in summary
            summary_text = " ".join(data["summary"])
            assert (
                "top 2%" in summary_text
                or "Additional context provided" in summary_text
            )

    async def test_generate_cv_draft_additional_context_with_llm_tailor(
        self, client, sample_cv_data, mock_neo4j_connection
    ):
        """Test that additional_context is passed to LLM when using llm_tailor style."""
        profile_data = {
            "personal_info": sample_cv_data["personal_info"],
            "experience": sample_cv_data["experience"],
            "education": sample_cv_data["education"],
            "skills": sample_cv_data["skills"],
            "updated_at": "2024-01-01T00:00:00",
        }

        from unittest.mock import Mock

        mock_llm_client = Mock()
        mock_llm_client.is_configured.return_value = True
        mock_llm_client.rewrite_text = AsyncMock(return_value="Tailored text")

        with patch(
            "backend.app_helpers.routes.ai.queries.get_profile",
            return_value=profile_data,
        ):
            with patch(
                "backend.services.ai.llm_tailor.get_llm_client",
                return_value=mock_llm_client,
            ):
                response = await client.post(
                    "/api/ai/generate-cv",
                    json={
                        "job_description": "We require FastAPI and React.",
                        "additional_context": "Rated among top 2% of AI coders in 2025",
                        "style": "llm_tailor",
                    },
                )
                assert response.status_code == 200
                # Verify LLM was called
                assert mock_llm_client.rewrite_text.called
                # Check that additional_context appears in prompts
                call_args_list = mock_llm_client.rewrite_text.call_args_list
                found_context = False
                for call_args in call_args_list:
                    prompt = call_args[0][1]
                    if (
                        "top 2% of AI coders" in prompt
                        or "Additional achievements" in prompt
                    ):
                        found_context = True
                        break
                assert found_context, "Additional context should appear in LLM prompts"


@pytest.mark.asyncio
@pytest.mark.api
class TestAIRewrite:
    """Test POST /api/ai/rewrite endpoint."""

    async def test_rewrite_text_success(self, client):
        """Test successful text rewrite."""
        mock_llm_client = AsyncMock()
        mock_llm_client.rewrite_text = AsyncMock(return_value="Rewritten text from LLM")

        with patch(
            "backend.app_helpers.routes.ai.get_llm_client", return_value=mock_llm_client
        ):
            response = await client.post(
                "/api/ai/rewrite",
                json={
                    "text": "Original text to rewrite",
                    "prompt": "Make it more professional",
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert "rewritten_text" in data
            assert data["rewritten_text"] == "Rewritten text from LLM"
            mock_llm_client.rewrite_text.assert_called_once_with(
                "Original text to rewrite", "Make it more professional"
            )

    async def test_rewrite_text_validation_error(self, client):
        """Test rewrite with invalid request data."""
        response = await client.post(
            "/api/ai/rewrite",
            json={
                "text": "",  # Empty text
                "prompt": "Make it better",
            },
        )
        assert response.status_code == 422

    async def test_rewrite_text_missing_fields(self, client):
        """Test rewrite with missing fields."""
        response = await client.post(
            "/api/ai/rewrite",
            json={
                "text": "Some text",
                # Missing prompt
            },
        )
        assert response.status_code == 422

    async def test_rewrite_text_llm_not_configured(self, client):
        """Test rewrite when LLM is not configured."""
        mock_llm_client = AsyncMock()
        mock_llm_client.rewrite_text = AsyncMock(
            side_effect=ValueError("LLM is not configured")
        )

        with patch(
            "backend.app_helpers.routes.ai.get_llm_client", return_value=mock_llm_client
        ):
            response = await client.post(
                "/api/ai/rewrite",
                json={
                    "text": "Some text",
                    "prompt": "Make it better",
                },
            )

            assert response.status_code == 400
            data = response.json()
            # Check for user-friendly error message
            assert "AI rewrite requires LLM configuration" in data["detail"]

    async def test_rewrite_text_llm_error(self, client):
        """Test rewrite when LLM API returns error."""
        mock_llm_client = AsyncMock()
        mock_llm_client.rewrite_text = AsyncMock(side_effect=Exception("API Error"))

        with patch(
            "backend.app_helpers.routes.ai.get_llm_client", return_value=mock_llm_client
        ):
            response = await client.post(
                "/api/ai/rewrite",
                json={
                    "text": "Some text",
                    "prompt": "Make it better",
                },
            )

            assert response.status_code == 500
            data = response.json()
            # Check for user-friendly error message
            assert (
                "error occurred" in data["detail"].lower()
                or "API Error" in data["detail"]
            )

    async def test_rewrite_text_long_text(self, client):
        """Test rewrite with long text."""
        long_text = "A" * 5000  # Within 10000 char limit
        mock_llm_client = AsyncMock()
        mock_llm_client.rewrite_text = AsyncMock(return_value="Rewritten")

        with patch(
            "backend.app_helpers.routes.ai.get_llm_client", return_value=mock_llm_client
        ):
            response = await client.post(
                "/api/ai/rewrite",
                json={
                    "text": long_text,
                    "prompt": "Make it shorter",
                },
            )

            assert response.status_code == 200
            mock_llm_client.rewrite_text.assert_called_once_with(
                long_text, "Make it shorter"
            )
