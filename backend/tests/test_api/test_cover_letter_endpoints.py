"""Tests for cover letter API endpoints."""

import pytest
from unittest.mock import patch, AsyncMock


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

        from unittest.mock import Mock
        from backend.services.ai.cover_letter_selection import SelectedContent

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
        from unittest.mock import Mock

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

        from unittest.mock import Mock
        from backend.services.ai.cover_letter_selection import SelectedContent

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


@pytest.mark.asyncio
@pytest.mark.api
class TestExportCoverLetterPDF:
    """Test POST /api/ai/cover-letter/pdf endpoint."""

    async def test_export_cover_letter_pdf_success(self, client, pdf_service):
        """Test successful PDF export."""
        html_content = """
        <!DOCTYPE html>
        <html>
        <head><meta charset="UTF-8"></head>
        <body>
            <h1>Cover Letter</h1>
            <p>This is a test cover letter.</p>
        </body>
        </html>
        """

        response = await client.post(
            "/api/ai/cover-letter/pdf",
            json={"html": html_content},
        )

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
        assert "attachment" in response.headers["content-disposition"]
        assert len(response.content) > 0  # PDF should have content

    async def test_export_cover_letter_pdf_empty_html(self, client):
        """Test PDF export with empty HTML."""
        response = await client.post(
            "/api/ai/cover-letter/pdf",
            json={"html": ""},
        )
        assert response.status_code == 422

    async def test_export_cover_letter_pdf_missing_html(self, client):
        """Test PDF export with missing HTML field."""
        response = await client.post(
            "/api/ai/cover-letter/pdf",
            json={},
        )
        assert response.status_code == 422

    async def test_export_cover_letter_pdf_invalid_html(self, client, pdf_service):
        """Test PDF export with invalid HTML (should still attempt to generate)."""
        # Even invalid HTML might generate a PDF (browser will try to render it)
        response = await client.post(
            "/api/ai/cover-letter/pdf",
            json={"html": "<invalid>html"},
        )
        # Should either succeed (browser renders what it can) or fail gracefully
        assert response.status_code in [200, 500]


@pytest.mark.asyncio
@pytest.mark.api
class TestSaveCoverLetter:
    """Test POST /api/cover-letters endpoint."""

    async def test_save_cover_letter_success(self, client, mock_neo4j_connection):
        """Test successful cover letter saving."""
        cover_letter_response = {
            "cover_letter_html": "<p>Test letter</p>",
            "cover_letter_text": "Test letter",
            "highlights_used": [],
            "selected_experiences": [],
            "selected_skills": ["Python"]
        }
        request_data = {
            "job_description": "We need a Python developer.",
            "company_name": "Tech Corp",
            "tone": "professional"
        }

        response = await client.post(
            "/api/cover-letters",
            json={
                "cover_letter_response": cover_letter_response,
                "request_data": request_data
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "cover_letter_id" in data
        assert data["status"] == "success"

    async def test_save_cover_letter_validation_error(self, client, mock_neo4j_connection):
        """Test save cover letter with invalid data."""
        response = await client.post(
            "/api/cover-letters",
            json={
                "cover_letter_response": {},  # Missing required fields
                "request_data": {}  # Missing required fields
            },
        )
        assert response.status_code == 422

    async def test_save_cover_letter_database_error(self, client, mock_neo4j_connection):
        """Test save cover letter with database error."""
        cover_letter_response = {
            "cover_letter_html": "<p>Test letter</p>",
            "cover_letter_text": "Test letter",
            "highlights_used": [],
            "selected_experiences": [],
            "selected_skills": ["Python"]
        }
        request_data = {
            "job_description": "We need a Python developer.",
            "company_name": "Tech Corp",
            "tone": "professional"
        }

        # Patch the session execute_write to raise an exception
        with patch.object(mock_neo4j_connection.session.return_value, 'execute_write') as mock_execute:
            mock_execute.side_effect = Exception("Database connection failed")

            response = await client.post(
                "/api/cover-letters",
                json={
                    "cover_letter_response": cover_letter_response,
                    "request_data": request_data
                },
            )

            assert response.status_code == 500
            data = response.json()
            assert "Failed to save cover letter" in data["detail"]


@pytest.mark.asyncio
@pytest.mark.api
class TestListCoverLetters:
    """Test GET /api/cover-letters endpoint."""

    async def test_list_cover_letters_success(self, client, mock_neo4j_connection):
        """Test successful cover letter listing."""
        with patch("backend.app_helpers.routes.cover_letter.endpoints.list_cover_letters") as mock_list:
            mock_list.return_value = {
                "cover_letters": [],
                "total": 0
            }
            response = await client.get("/api/cover-letters")
            assert response.status_code == 200

    async def test_list_cover_letters_with_pagination(self, client, mock_neo4j_connection):
        """Test cover letter listing with pagination."""
        with patch("backend.app_helpers.routes.cover_letter.endpoints.list_cover_letters") as mock_list:
            mock_list.return_value = {
                "cover_letters": [],
                "total": 0
            }
            response = await client.get("/api/cover-letters?limit=10&offset=5")
            assert response.status_code == 200

    async def test_list_cover_letters_with_search(self, client, mock_neo4j_connection):
        """Test cover letter listing with search."""
        with patch("backend.app_helpers.routes.cover_letter.endpoints.list_cover_letters") as mock_list:
            mock_list.return_value = {
                "cover_letters": [],
                "total": 0
            }
            response = await client.get("/api/cover-letters?search=Tech%20Corp")
            assert response.status_code == 200

    async def test_list_cover_letters_database_error(self, client, mock_neo4j_connection):
        """Test list cover letters with database error."""
        with patch("backend.app_helpers.routes.cover_letter.endpoints.list_cover_letters") as mock_list:
            mock_list.side_effect = Exception("Database error")

            response = await client.get("/api/cover-letters")
            assert response.status_code == 500
            data = response.json()
            assert "Failed to list cover letters" in data["detail"]


@pytest.mark.asyncio
@pytest.mark.api
class TestGetCoverLetter:
    """Test GET /api/cover-letters/{cover_letter_id} endpoint."""

    async def test_get_cover_letter_success(self, client, mock_neo4j_connection):
        """Test successful cover letter retrieval."""
        mock_cover_letter = {
            "cover_letter_id": "test-id",
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00",
            "job_description": "We need a Python developer.",
            "company_name": "Tech Corp",
            "hiring_manager_name": None,
            "company_address": None,
            "tone": "professional",
            "cover_letter_html": "<p>Test letter</p>",
            "cover_letter_text": "Test letter",
            "highlights_used": [],
            "selected_experiences": [],
            "selected_skills": ["Python"]
        }

        with patch("backend.app_helpers.routes.cover_letter.endpoints.get_cover_letter_by_id") as mock_get:
            mock_get.return_value = mock_cover_letter

            response = await client.get("/api/cover-letters/test-id")
            assert response.status_code == 200
            data = response.json()
            assert data["cover_letter_id"] == "test-id"

    async def test_get_cover_letter_not_found(self, client, mock_neo4j_connection):
        """Test getting non-existent cover letter."""
        response = await client.get("/api/cover-letters/non-existent-id")
        assert response.status_code == 404
        data = response.json()
        assert "Cover letter not found" in data["detail"]

    async def test_get_cover_letter_database_error(self, client, mock_neo4j_connection):
        """Test get cover letter with database error."""
        with patch("backend.app_helpers.routes.cover_letter.endpoints.get_cover_letter_by_id") as mock_get:
            mock_get.side_effect = Exception("Database error")

            response = await client.get("/api/cover-letters/test-id")
            assert response.status_code == 500
            data = response.json()
            assert "Failed to get cover letter" in data["detail"]


@pytest.mark.asyncio
@pytest.mark.api
class TestDeleteCoverLetter:
    """Test DELETE /api/cover-letters/{cover_letter_id} endpoint."""

    async def test_delete_cover_letter_success(self, client, mock_neo4j_connection):
        """Test successful cover letter deletion."""
        with patch("backend.app_helpers.routes.cover_letter.endpoints.delete_cover_letter") as mock_delete:
            mock_delete.return_value = True

            response = await client.delete("/api/cover-letters/test-id")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"

    async def test_delete_cover_letter_not_found(self, client, mock_neo4j_connection):
        """Test deleting non-existent cover letter."""
        with patch("backend.app_helpers.routes.cover_letter.endpoints.delete_cover_letter") as mock_delete:
            mock_delete.return_value = False  # Indicates not found

            response = await client.delete("/api/cover-letters/non-existent-id")
            assert response.status_code == 404
            data = response.json()
            assert "Cover letter not found" in data["detail"]

    async def test_delete_cover_letter_database_error(self, client, mock_neo4j_connection):
        """Test delete cover letter with database error."""
        with patch("backend.app_helpers.routes.cover_letter.endpoints.delete_cover_letter") as mock_delete:
            mock_delete.side_effect = Exception("Database error")

            response = await client.delete("/api/cover-letters/test-id")
            assert response.status_code == 500
            data = response.json()
            assert "Failed to delete cover letter" in data["detail"]
