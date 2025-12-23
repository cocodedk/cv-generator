"""Tests for PUT /api/cv/{cv_id} endpoint - basic operations."""
import pytest
from unittest.mock import patch


@pytest.mark.asyncio
@pytest.mark.api
class TestUpdateCVBasic:
    """Test PUT /api/cv/{cv_id} endpoint - basic operations."""

    async def test_update_cv_success(
        self, client, sample_cv_data, mock_neo4j_connection
    ):
        """Test successful CV update."""
        updated_cv = {
            "cv_id": "test-id",
            "personal_info": sample_cv_data["personal_info"],
            "experience": sample_cv_data["experience"],
            "education": sample_cv_data["education"],
            "skills": sample_cv_data["skills"],
            "theme": sample_cv_data.get("theme", "classic"),
        }
        with patch("backend.database.queries.update_cv", return_value=True):
            with patch(
                "backend.database.queries.get_cv_by_id", return_value=updated_cv
            ):
                with patch(
                    "backend.database.queries.set_cv_filename", return_value=True
                ):
                    with patch(
                        "backend.services.cv_file_service.CVFileService.generate_file_for_cv",
                        return_value="cv_test.docx",
                    ) as mock_generate:
                        response = await client.put(
                            "/api/cv/test-id", json=sample_cv_data
                        )
                        assert response.status_code == 200
                        data = response.json()
                        assert data["cv_id"] == "test-id"
                        assert data["status"] == "success"
                        assert mock_generate.called
                        assert data["filename"].endswith(".docx")

    async def test_update_cv_not_found(
        self, client, sample_cv_data, mock_neo4j_connection
    ):
        """Test update non-existent CV."""
        with patch("backend.database.queries.update_cv", return_value=False):
            response = await client.put("/api/cv/non-existent", json=sample_cv_data)
            assert response.status_code == 404
