"""Edge case tests for content selection functionality."""

import json
import pytest
from unittest.mock import AsyncMock, Mock, patch

from backend.models import ProfileData, PersonalInfo, Skill
from backend.services.ai.cover_letter_selection import select_relevant_content


class TestEdgeCases:
    """Test edge cases in content selection."""

    @pytest.mark.asyncio
    async def test_select_relevant_content_case_insensitive_skill_matching(self):
        """Test that skills are matched case-insensitively."""
        # Profile with mixed case skills
        profile_with_mixed_case = ProfileData(
            personal_info=PersonalInfo(name="Test", title="Developer"),
            experience=[],
            education=[],
            skills=[
                Skill(name="PYTHON", category="Programming"),
                Skill(name="django", category="Backend"),
                Skill(name="JavaScript", category="Frontend"),
            ],
        )

        mock_llm_client = Mock()
        mock_llm_client.model = "gpt-3.5-turbo"
        mock_llm_client.api_key = "test-key"
        mock_llm_client.base_url = "https://api.test.com"
        mock_llm_client.timeout = 30

        # LLM returns lowercase versions
        mock_response = {
            "choices": [
                {
                    "message": {
                        "content": json.dumps(
                            {
                                "experience_indices": [],
                                "skill_names": ["python", "django", "javascript"],
                                "key_highlights": [],
                                "relevance_reasoning": "Skills match",
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
                profile=profile_with_mixed_case,
                job_description="We need Python developers.",
                llm_client=mock_llm_client,
            )

            # Should match case-insensitively
            assert len(result.skill_names) == 3
            assert "PYTHON" in result.skill_names or "python" in result.skill_names
