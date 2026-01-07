"""Error handling tests for content selection functionality."""

import pytest
from unittest.mock import AsyncMock, Mock, patch
import httpx

from backend.services.ai.cover_letter_selection import select_relevant_content


class TestErrorHandling:
    """Test error handling in content selection."""

    @pytest.mark.asyncio
    async def test_select_relevant_content_invalid_json(
        self, sample_profile, job_description_django
    ):
        """Test handling of invalid JSON response."""
        mock_llm_client = Mock()
        mock_llm_client.model = "gpt-3.5-turbo"
        mock_llm_client.api_key = "test-key"
        mock_llm_client.base_url = "https://api.test.com"
        mock_llm_client.timeout = 30

        mock_response = {
            "choices": [{"message": {"content": "This is not valid JSON"}}]
        }

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_response_obj = Mock()
            mock_response_obj.json.return_value = mock_response
            mock_response_obj.raise_for_status = Mock()
            mock_client.post = AsyncMock(return_value=mock_response_obj)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client_class.return_value = mock_client

            with pytest.raises(ValueError, match="invalid JSON"):
                await select_relevant_content(
                    profile=sample_profile,
                    job_description=job_description_django,
                    llm_client=mock_llm_client,
                )

    @pytest.mark.asyncio
    async def test_select_relevant_content_http_error(
        self, sample_profile, job_description_django
    ):
        """Test handling of HTTP errors."""
        mock_llm_client = Mock()
        mock_llm_client.model = "gpt-3.5-turbo"
        mock_llm_client.api_key = "test-key"
        mock_llm_client.base_url = "https://api.test.com"
        mock_llm_client.timeout = 30

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_response_obj = Mock()
            mock_response_obj.raise_for_status = Mock(
                side_effect=httpx.HTTPError("API Error")
            )
            mock_client.post = AsyncMock(return_value=mock_response_obj)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client_class.return_value = mock_client

            with pytest.raises(ValueError, match="Failed to select relevant content"):
                await select_relevant_content(
                    profile=sample_profile,
                    job_description=job_description_django,
                    llm_client=mock_llm_client,
                )

    @pytest.mark.asyncio
    async def test_select_relevant_content_malformed_response(self, sample_profile):
        """Test handling of malformed LLM response."""
        mock_llm_client = Mock()
        mock_llm_client.model = "gpt-3.5-turbo"
        mock_llm_client.api_key = "test-key"
        mock_llm_client.base_url = "https://api.test.com"
        mock_llm_client.timeout = 30

        # Mock response with missing choices
        mock_response = {"choices": []}

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_response_obj = Mock()
            mock_response_obj.json.return_value = mock_response
            mock_response_obj.raise_for_status = Mock()
            mock_client.post = AsyncMock(return_value=mock_response_obj)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client_class.return_value = mock_client

            with pytest.raises(ValueError, match="Invalid response from LLM API"):
                await select_relevant_content(
                    profile=sample_profile,
                    job_description="We need a developer.",
                    llm_client=mock_llm_client,
                )
