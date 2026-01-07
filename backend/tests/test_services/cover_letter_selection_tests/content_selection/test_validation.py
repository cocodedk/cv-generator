"""Validation tests for content selection functionality."""

import json
import pytest
from unittest.mock import AsyncMock, Mock, patch

from backend.models import ProfileData, PersonalInfo
from backend.services.ai.cover_letter_selection import select_relevant_content


class TestValidation:
    """Test content selection validation functionality."""

    @pytest.mark.asyncio
    async def test_select_relevant_content_validates_indices(
        self, sample_profile, job_description_django
    ):
        """Test that invalid experience indices are filtered out."""
        mock_llm_client = Mock()
        mock_llm_client.model = "gpt-3.5-turbo"
        mock_llm_client.api_key = "test-key"
        mock_llm_client.base_url = "https://api.test.com"
        mock_llm_client.timeout = 30

        # Mock response with invalid indices
        mock_response = {
            "choices": [
                {
                    "message": {
                        "content": json.dumps(
                            {
                                "experience_indices": [
                                    0,
                                    5,
                                    -1,
                                ],  # 5 and -1 are invalid
                                "skill_names": ["Django"],
                                "key_highlights": [],
                                "relevance_reasoning": "Test",
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

            # Should only include valid index [0]
            assert result.experience_indices == [0]

    @pytest.mark.asyncio
    async def test_select_relevant_content_validates_skills(
        self, sample_profile, job_description_django
    ):
        """Test that non-existent skills are filtered out."""
        mock_llm_client = Mock()
        mock_llm_client.model = "gpt-3.5-turbo"
        mock_llm_client.api_key = "test-key"
        mock_llm_client.base_url = "https://api.test.com"
        mock_llm_client.timeout = 30

        # Mock response with non-existent skill
        mock_response = {
            "choices": [
                {
                    "message": {
                        "content": json.dumps(
                            {
                                "experience_indices": [0],
                                "skill_names": ["Django", "NonExistentSkill"],
                                "key_highlights": [],
                                "relevance_reasoning": "Test",
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

            # Should only include existing skill
            assert "Django" in result.skill_names
            assert "NonExistentSkill" not in result.skill_names

    @pytest.mark.asyncio
    async def test_select_relevant_content_empty_profile(self):
        """Test selection with empty profile."""
        empty_profile = ProfileData(
            personal_info=PersonalInfo(name="Test", title="Developer"),
            experience=[],
            education=[],
            skills=[],
        )

        mock_llm_client = Mock()
        mock_llm_client.model = "gpt-3.5-turbo"
        mock_llm_client.api_key = "test-key"
        mock_llm_client.base_url = "https://api.test.com"
        mock_llm_client.timeout = 30

        mock_response = {
            "choices": [
                {
                    "message": {
                        "content": json.dumps(
                            {
                                "experience_indices": [],
                                "skill_names": [],
                                "key_highlights": [],
                                "relevance_reasoning": "No relevant experience found",
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
                profile=empty_profile,
                job_description="We need a developer.",
                llm_client=mock_llm_client,
            )

            assert result.experience_indices == []
            assert result.skill_names == []
            assert result.key_highlights == []
