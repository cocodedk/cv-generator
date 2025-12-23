"""Tests for CV CRUD endpoints."""
import pytest
from unittest.mock import patch, Mock
from backend.database import queries


@pytest.mark.asyncio
@pytest.mark.api
class TestGenerateCV:
    """Test POST /api/generate-cv endpoint."""

    async def test_generate_cv_success(
        self, client, sample_cv_data, mock_neo4j_connection, temp_output_dir
    ):
        """Test successful CV generation."""
        import backend.app

        original_output_dir = backend.app.output_dir
        backend.app.output_dir = temp_output_dir
        try:
            with patch("backend.app.queries.create_cv", return_value="test-cv-id"):
                with patch("backend.app.queries.set_cv_filename", return_value=True):
                    with patch(
                        "backend.cv_generator.generator.CVGenerator.generate"
                    ) as mock_gen:
                        mock_gen.return_value = str(temp_output_dir / "cv_test.odt")
                        response = await client.post(
                            "/api/generate-cv", json=sample_cv_data
                        )
                        assert response.status_code == 200
                        data = response.json()
                        assert data["cv_id"] == "test-cv-id"
                        assert data["status"] == "success"
                        assert "filename" in data
        finally:
            backend.app.output_dir = original_output_dir

    async def test_generate_cv_validation_error(self, client):
        """Test CV generation with invalid data."""
        invalid_data = {"personal_info": {"name": ""}}  # Invalid: empty name
        response = await client.post("/api/generate-cv", json=invalid_data)
        assert response.status_code == 422

    async def test_generate_cv_server_error(
        self, client, sample_cv_data, mock_neo4j_connection
    ):
        """Test CV generation with server error."""
        with patch(
            "backend.app.queries.create_cv", side_effect=Exception("Database error")
        ):
            response = await client.post("/api/generate-cv", json=sample_cv_data)
            assert response.status_code == 500


@pytest.mark.asyncio
@pytest.mark.api
class TestSaveCV:
    """Test POST /api/save-cv endpoint."""

    async def test_save_cv_success(self, client, sample_cv_data, mock_neo4j_connection):
        """Test successful CV save."""
        with patch("backend.app.queries.create_cv", return_value="test-cv-id"):
            response = await client.post("/api/save-cv", json=sample_cv_data)
            assert response.status_code == 200
            data = response.json()
            assert data["cv_id"] == "test-cv-id"
            assert data["status"] == "success"

    async def test_save_cv_validation_error(self, client):
        """Test CV save with invalid data."""
        invalid_data = {"personal_info": {}}  # Missing required name
        response = await client.post("/api/save-cv", json=invalid_data)
        assert response.status_code == 422


@pytest.mark.asyncio
@pytest.mark.api
class TestGetCV:
    """Test GET /api/cv/{cv_id} endpoint."""

    async def test_get_cv_success(self, client, mock_neo4j_connection):
        """Test successful CV retrieval."""
        cv_data = {
            "cv_id": "test-id",
            "personal_info": {"name": "John Doe"},
            "experience": [],
            "education": [],
            "skills": [],
        }
        with patch("backend.app.queries.get_cv_by_id", return_value=cv_data):
            response = await client.get("/api/cv/test-id")
            assert response.status_code == 200
            data = response.json()
            assert data["cv_id"] == "test-id"

    async def test_get_cv_not_found(self, client, mock_neo4j_connection):
        """Test CV not found."""
        with patch("backend.app.queries.get_cv_by_id", return_value=None):
            response = await client.get("/api/cv/non-existent")
            assert response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.api
class TestListCVs:
    """Test GET /api/cvs endpoint."""

    async def test_list_cvs_success(self, client, mock_neo4j_connection):
        """Test successful CV listing."""
        list_data = {
            "cvs": [
                {
                    "cv_id": "id1",
                    "created_at": "2024-01-01T00:00:00",
                    "updated_at": "2024-01-01T00:00:00",
                    "person_name": "John Doe",
                }
            ],
            "total": 1,
        }
        with patch("backend.app.queries.list_cvs", return_value=list_data):
            response = await client.get("/api/cvs")
            assert response.status_code == 200
            data = response.json()
            assert data["total"] == 1
            assert len(data["cvs"]) == 1

    async def test_list_cvs_with_pagination(self, client, mock_neo4j_connection):
        """Test CV listing with pagination."""
        list_data = {"cvs": [], "total": 0}
        with patch("backend.app.queries.list_cvs", return_value=list_data):
            response = await client.get("/api/cvs?limit=10&offset=0")
            assert response.status_code == 200

    async def test_list_cvs_with_search(self, client, mock_neo4j_connection):
        """Test CV listing with search."""
        list_data = {"cvs": [], "total": 0}
        with patch("backend.app.queries.list_cvs", return_value=list_data):
            response = await client.get("/api/cvs?search=John")
            assert response.status_code == 200


@pytest.mark.asyncio
@pytest.mark.api
class TestUpdateCV:
    """Test PUT /api/cv/{cv_id} endpoint."""

    async def test_update_cv_success(
        self, client, sample_cv_data, mock_neo4j_connection
    ):
        """Test successful CV update."""
        with patch("backend.app.queries.update_cv", return_value=True):
            response = await client.put("/api/cv/test-id", json=sample_cv_data)
            assert response.status_code == 200
            data = response.json()
            assert data["cv_id"] == "test-id"
            assert data["status"] == "success"

    async def test_update_cv_not_found(
        self, client, sample_cv_data, mock_neo4j_connection
    ):
        """Test update non-existent CV."""
        with patch("backend.app.queries.update_cv", return_value=False):
            response = await client.put("/api/cv/non-existent", json=sample_cv_data)
            assert response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.api
class TestDeleteCV:
    """Test DELETE /api/cv/{cv_id} endpoint."""

    async def test_delete_cv_success(self, client, mock_neo4j_connection):
        """Test successful CV deletion."""
        with patch("backend.app.queries.delete_cv", return_value=True):
            response = await client.delete("/api/cv/test-id")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"

    async def test_delete_cv_not_found(self, client, mock_neo4j_connection):
        """Test delete non-existent CV."""
        with patch("backend.app.queries.delete_cv", return_value=False):
            response = await client.delete("/api/cv/non-existent")
            assert response.status_code == 404
