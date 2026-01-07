"""Tests for POST /api/ai/rewrite endpoint."""

import pytest
from unittest.mock import patch, AsyncMock


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
