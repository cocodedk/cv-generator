"""Basic selection tests for content selection functionality."""

import json
import pytest
from unittest.mock import AsyncMock, Mock, patch

from backend.services.ai.cover_letter_selection import (
    select_relevant_content,
    SelectedContent,
)


class TestBasicSelection:
    """Test basic content selection functionality."""

    @pytest.mark.asyncio
    async def test_select_relevant_content_django_job(
        self, sample_profile, job_description_django
    ):
        """Test selection prioritizes Django/Python for Django job."""
        mock_llm_client = Mock()
        mock_llm_client.model = "gpt-3.5-turbo"
        mock_llm_client.api_key = "test-key"
        mock_llm_client.base_url = "https://api.test.com"
        mock_llm_client.timeout = 30

        # Mock LLM response prioritizing Django experience
        mock_response = {
            "choices": [
                {
                    "message": {
                        "content": json.dumps(
                            {
                                "experience_indices": [0],  # Django experience
                                "skill_names": ["Django", "Python", "PostgreSQL"],
                                "key_highlights": [
                                    "Built scalable REST API serving 1M+ requests/day"
                                ],
                                "relevance_reasoning": "Django and Python match job requirements",
                            }
                        )
                    }
                }
            ]
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

            result = await select_relevant_content(
                profile=sample_profile,
                job_description=job_description_django,
                llm_client=mock_llm_client,
            )

            assert isinstance(result, SelectedContent)
            assert result.experience_indices == [0]
            assert "Django" in result.skill_names
            assert "Python" in result.skill_names
            assert "LAMP" not in result.skill_names  # Should not select irrelevant tech

    @pytest.mark.asyncio
    async def test_select_relevant_content_nodejs_job(
        self, sample_profile, job_description_nodejs
    ):
        """Test selection prioritizes Node.js for Node.js job."""
        mock_llm_client = Mock()
        mock_llm_client.model = "gpt-3.5-turbo"
        mock_llm_client.api_key = "test-key"
        mock_llm_client.base_url = "https://api.test.com"
        mock_llm_client.timeout = 30

        # Mock LLM response prioritizing Node.js experience
        mock_response = {
            "choices": [
                {
                    "message": {
                        "content": json.dumps(
                            {
                                "experience_indices": [1],  # Node.js experience
                                "skill_names": ["Node.js", "React", "MongoDB"],
                                "key_highlights": [
                                    "Developed real-time features using WebSockets"
                                ],
                                "relevance_reasoning": "Node.js and React match job requirements",
                            }
                        )
                    }
                }
            ]
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

            result = await select_relevant_content(
                profile=sample_profile,
                job_description=job_description_nodejs,
                llm_client=mock_llm_client,
            )

            assert isinstance(result, SelectedContent)
            assert result.experience_indices == [1]
            assert "Node.js" in result.skill_names
            assert "React" in result.skill_names
            assert "LAMP" not in result.skill_names

    @pytest.mark.asyncio
    async def test_select_relevant_content_json_in_markdown(
        self, sample_profile, job_description_django
    ):
        """Test parsing JSON from markdown code block."""
        mock_llm_client = Mock()
        mock_llm_client.model = "gpt-3.5-turbo"
        mock_llm_client.api_key = "test-key"
        mock_llm_client.base_url = "https://api.test.com"
        mock_llm_client.timeout = 30

        # Mock LLM response with JSON in markdown code block
        json_content = json.dumps(
            {
                "experience_indices": [0],
                "skill_names": ["Django", "Python"],
                "key_highlights": [],
                "relevance_reasoning": "Test",
            }
        )
        mock_response = {
            "choices": [{"message": {"content": f"```json\n{json_content}\n```"}}]
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

            result = await select_relevant_content(
                profile=sample_profile,
                job_description=job_description_django,
                llm_client=mock_llm_client,
            )

            assert result.experience_indices == [0]
            assert "Django" in result.skill_names
