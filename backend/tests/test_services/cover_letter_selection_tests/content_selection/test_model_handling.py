"""Model handling tests for content selection payloads."""

import json
from unittest.mock import AsyncMock, Mock, patch

import pytest

from backend.services.ai.cover_letter_selection import select_relevant_content


class TestModelHandling:
    """Test model-specific payload behavior."""

    @pytest.mark.asyncio
    async def test_reasoning_model_payload_excludes_temperature(
        self, sample_profile, job_description_django
    ):
        """Reasoning models should omit temperature in payload."""
        mock_llm_client = Mock(spec_set=["model", "api_key", "base_url", "timeout"])
        mock_llm_client.model = "o1-mini"
        mock_llm_client.api_key = "test-key"
        mock_llm_client.base_url = "https://api.test.com"
        mock_llm_client.timeout = 30

        mock_response = {
            "choices": [
                {
                    "message": {
                        "content": json.dumps(
                            {
                                "experience_indices": [0],
                                "skill_names": ["Django", "Python"],
                                "key_highlights": [],
                                "relevance_reasoning": "Matches job requirements",
                            }
                        )
                    }
                }
            ]
        }

        captured_payload = {}

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_response_obj = Mock()
            mock_response_obj.json.return_value = mock_response
            mock_response_obj.raise_for_status = Mock()

            async def _post(url, json, headers):
                captured_payload["json"] = json
                return mock_response_obj

            mock_client.post = AsyncMock(side_effect=_post)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client_class.return_value = mock_client

            await select_relevant_content(
                profile=sample_profile,
                job_description=job_description_django,
                llm_client=mock_llm_client,
            )

        assert "temperature" not in captured_payload["json"]
