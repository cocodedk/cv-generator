"""Tests for PUT /api/cv/{cv_id} endpoint - theme operations."""
import pytest
from unittest.mock import patch


@pytest.mark.asyncio
@pytest.mark.api
class TestUpdateCVTheme:
    """Test PUT /api/cv/{cv_id} endpoint - theme operations."""

    async def test_update_cv_saves_theme(
        self, client, sample_cv_data, mock_neo4j_connection
    ):
        """Test that theme is saved when updating CV."""
        sample_cv_data["theme"] = "accented"
        updated_cv = {
            "cv_id": "test-id",
            "personal_info": sample_cv_data["personal_info"],
            "experience": sample_cv_data["experience"],
            "education": sample_cv_data["education"],
            "skills": sample_cv_data["skills"],
            "theme": "accented",
        }
        with patch("backend.database.queries.update_cv") as mock_update:
            mock_update.return_value = True
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
                        call_args = mock_update.call_args
                        assert call_args is not None
                        assert call_args[0][1]["theme"] == "accented"
                        assert mock_generate.called

    async def test_update_cv_preserves_theme(
        self, client, sample_cv_data, mock_neo4j_connection
    ):
        """Test that theme persists after update."""
        sample_cv_data["theme"] = "elegant"
        updated_cv = {
            "cv_id": "test-id",
            "personal_info": {"name": "John Doe"},
            "experience": [],
            "education": [],
            "skills": [],
            "theme": "elegant",
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
                        get_response = await client.get("/api/cv/test-id")
                        assert get_response.status_code == 200
                        data = get_response.json()
                        assert data["theme"] == "elegant"
                        assert mock_generate.called

    async def test_update_cv_regenerates_file_on_theme_change(
        self, client, sample_cv_data, mock_neo4j_connection
    ):
        """Test that updating CV with new theme regenerates the DOCX file."""
        sample_cv_data["theme"] = "modern"
        updated_cv_modern = {
            "cv_id": "test-id",
            "personal_info": {"name": "John Doe"},
            "experience": [],
            "education": [],
            "skills": [],
            "theme": "modern",
        }

        with patch("backend.database.queries.update_cv", return_value=True):
            with patch(
                "backend.database.queries.get_cv_by_id",
                return_value=updated_cv_modern,
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
                        assert mock_generate.called
                        call_args = mock_generate.call_args
                        assert call_args is not None
                        cv_dict = call_args[0][1]
                        assert cv_dict["theme"] == "modern"
                        assert data["filename"].endswith(".docx")
