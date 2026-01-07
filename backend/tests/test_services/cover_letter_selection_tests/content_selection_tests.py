"""Tests for content selection functionality in cover letter selection."""

import json
import pytest
from unittest.mock import AsyncMock, Mock, patch
import httpx

from backend.models import ProfileData, PersonalInfo, Experience, Project, Skill
from backend.services.ai.cover_letter_selection import (
    select_relevant_content,
    SelectedContent,
)


@pytest.fixture
def sample_profile():
    """Sample profile with multiple experiences and skills."""
    return ProfileData(
        personal_info=PersonalInfo(
            name="Jane Developer",
            title="Senior Software Engineer",
            email="jane@example.com",
        ),
        experience=[
            Experience(
                title="Senior Backend Engineer",
                company="Modern Tech Inc",
                start_date="2022-01",
                end_date="2024-12",
                projects=[
                    Project(
                        name="API Platform",
                        technologies=["Django", "Python", "PostgreSQL"],
                        highlights=[
                            "Built scalable REST API serving 1M+ requests/day",
                            "Led migration to microservices architecture",
                        ],
                    )
                ],
            ),
            Experience(
                title="Full Stack Developer",
                company="Startup Co",
                start_date="2020-01",
                end_date="2021-12",
                projects=[
                    Project(
                        name="Web Application",
                        technologies=["Node.js", "React", "MongoDB"],
                        highlights=[
                            "Developed full-stack web application",
                            "Implemented responsive UI components",
                        ],
                    )
                ],
            ),
            Experience(
                title="Junior Developer",
                company="Small Agency",
                start_date="2018-01",
                end_date="2019-12",
                projects=[
                    Project(
                        name="Portfolio Site",
                        technologies=["HTML", "CSS", "JavaScript"],
                        highlights=[
                            "Built responsive portfolio website",
                            "Optimized performance and SEO",
                        ],
                    )
                ],
            ),
        ],
        education=[],
        skills=[
            Skill(name="Django", category="Backend"),
            Skill(name="Python", category="Programming"),
            Skill(name="PostgreSQL", category="Database"),
            Skill(name="Node.js", category="Backend"),
            Skill(name="React", category="Frontend"),
            Skill(name="MongoDB", category="Database"),
            Skill(name="LAMP", category="Full Stack"),
        ],
    )


@pytest.fixture
def job_description_django():
    """Django-focused job description."""
    return """
    Senior Backend Engineer - Django/Python

    We are looking for an experienced backend engineer to join our team building
    scalable web applications using Django and Python.

    Requirements:
    - 3+ years experience with Django
    - Strong Python skills
    - Experience with PostgreSQL
    - REST API development
    - Microservices architecture

    Nice to have:
    - AWS experience
    - Docker containerization
    """


@pytest.fixture
def job_description_nodejs():
    """Node.js-focused job description."""
    return """
    Full Stack Developer - Node.js/React

    We need a full stack developer experienced with Node.js and React.

    Requirements:
    - Node.js backend development
    - React frontend development
    - MongoDB experience
    - REST API development
    - Real-time features (WebSockets)

    Nice to have:
    - TypeScript experience
    - GraphQL knowledge
    """


class TestSelectRelevantContent:
    """Test LLM-based content selection."""

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
