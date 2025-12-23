"""Tests for PUT /api/cv/{cv_id} endpoint - theme operations."""
import pytest
from unittest.mock import patch


@pytest.mark.asyncio
@pytest.mark.api
class TestUpdateCVTheme:
    """Test PUT /api/cv/{cv_id} endpoint - theme operations."""

    async def test_update_cv_saves_theme(
        self, client, sample_cv_data, mock_neo4j_connection, temp_output_dir
    ):
        """Test that theme is saved when updating CV."""
        from backend.app import app

        original_output_dir = app.state.output_dir
        app.state.output_dir = temp_output_dir
        try:
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
                            "backend.cv_generator.generator.CVGenerator.generate"
                        ) as mock_gen:
                            mock_gen.return_value = str(temp_output_dir / "cv_test.odt")
                            response = await client.put(
                                "/api/cv/test-id", json=sample_cv_data
                            )
                            assert response.status_code == 200
                            # Verify theme was passed to update_cv
                            call_args = mock_update.call_args
                            assert call_args is not None
                            assert call_args[0][1]["theme"] == "accented"
                            # Verify file was regenerated
                            assert mock_gen.called
        finally:
            app.state.output_dir = original_output_dir

    async def test_update_cv_preserves_theme(
        self, client, sample_cv_data, mock_neo4j_connection, temp_output_dir
    ):
        """Test that theme persists after update."""
        from backend.app import app

        original_output_dir = app.state.output_dir
        app.state.output_dir = temp_output_dir
        try:
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
                            "backend.cv_generator.generator.CVGenerator.generate"
                        ) as mock_gen:
                            mock_gen.return_value = str(temp_output_dir / "cv_test.odt")
                            response = await client.put(
                                "/api/cv/test-id", json=sample_cv_data
                            )
                            assert response.status_code == 200
                            # Verify theme was saved
                            get_response = await client.get("/api/cv/test-id")
                            assert get_response.status_code == 200
                            data = get_response.json()
                            assert data["theme"] == "elegant"
                            # Verify file was regenerated
                            assert mock_gen.called
        finally:
            app.state.output_dir = original_output_dir

    async def test_update_cv_regenerates_file_on_theme_change(
        self, client, sample_cv_data, mock_neo4j_connection, temp_output_dir
    ):
        """Test that updating CV with new theme regenerates the ODT file."""
        from backend.app import app

        original_output_dir = app.state.output_dir
        app.state.output_dir = temp_output_dir
        try:
            # Update to modern theme
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
                            "backend.cv_generator.generator.CVGenerator.generate"
                        ) as mock_gen:
                            mock_gen.return_value = str(temp_output_dir / "cv_test.odt")
                            response = await client.put(
                                "/api/cv/test-id", json=sample_cv_data
                            )
                            assert response.status_code == 200
                            data = response.json()
                            # Verify file was regenerated
                            assert mock_gen.called
                            # Verify generator was called with modern theme
                            call_args = mock_gen.call_args
                            assert call_args is not None
                            cv_dict = call_args[0][0]
                            assert cv_dict["theme"] == "modern"
                            assert "filename" in data
        finally:
            app.state.output_dir = original_output_dir
