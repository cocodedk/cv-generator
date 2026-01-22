"""Tests for profile endpoints."""
import pytest
from unittest.mock import patch, AsyncMock
from backend.tests.test_api.response_helpers import assert_validation_error_response


@pytest.mark.asyncio
@pytest.mark.api
class TestSaveProfile:
    """Test POST /api/profile endpoint."""

    async def test_save_profile_success(
        self, client, sample_cv_data, mock_neo4j_connection
    ):
        """Test successful profile save."""
        profile_data = {
            "personal_info": sample_cv_data["personal_info"],
            "experience": sample_cv_data["experience"],
            "education": sample_cv_data["education"],
            "skills": sample_cv_data["skills"],
        }
        with patch(
            "backend.database.queries.save_profile", return_value=True
        ) as mock_save, patch(
            "backend.services.cv_file_service.CVFileService.generate_featured_templates",
            new_callable=AsyncMock,
        ):
            response = await client.post("/api/profile", json=profile_data)
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert "message" in data
            call_args = mock_save.call_args
            assert call_args is not None
            assert (
                call_args[0][0]["experience"][0]["projects"][0]["name"]
                == "Internal Platform"
            )

    async def test_save_profile_validation_error(self, client):
        """Test profile save with invalid data."""
        invalid_data = {"personal_info": {"name": ""}}  # Invalid: empty name
        response = await client.post("/api/profile", json=invalid_data)
        error_data = assert_validation_error_response(response)
        # Verify that the error mentions the name field
        assert any("name" in str(error).lower() for error in error_data["detail"])

    async def test_save_profile_server_error(
        self, client, sample_cv_data, mock_neo4j_connection
    ):
        """Test profile save with server error."""
        profile_data = {
            "personal_info": sample_cv_data["personal_info"],
            "experience": sample_cv_data["experience"],
            "education": sample_cv_data["education"],
            "skills": sample_cv_data["skills"],
        }
        with patch(
            "backend.database.queries.save_profile",
            side_effect=Exception("Database error"),
        ):
            response = await client.post("/api/profile", json=profile_data)
            assert response.status_code == 500


@pytest.mark.asyncio
@pytest.mark.api
class TestGetProfile:
    """Test GET /api/profile endpoint."""

    async def test_get_profile_success(self, client, mock_neo4j_connection):
        """Test successful profile retrieval."""
        profile_data = {
            "personal_info": {"name": "John Doe", "email": "john@example.com"},
            "experience": [],
            "education": [],
            "skills": [],
            "updated_at": "2024-01-01T00:00:00",
        }
        with patch("backend.database.queries.get_profile", return_value=profile_data):
            response = await client.get("/api/profile")
            assert response.status_code == 200
            data = response.json()
            assert "personal_info" in data
            assert data["personal_info"]["name"] == "John Doe"

    async def test_get_profile_not_found(self, client, mock_neo4j_connection):
        """Test profile not found."""
        with patch("backend.database.queries.get_profile", return_value=None):
            response = await client.get("/api/profile")
            assert response.status_code == 404

    async def test_get_profile_server_error(self, client, mock_neo4j_connection):
        """Test get profile with server error."""
        with patch(
            "backend.database.queries.get_profile",
            side_effect=Exception("Database error"),
        ):
            response = await client.get("/api/profile")
            assert response.status_code == 500


@pytest.mark.asyncio
@pytest.mark.api
class TestDeleteProfile:
    """Test DELETE /api/profile endpoint."""

    async def test_delete_profile_requires_confirmation_header(
        self, client, mock_neo4j_connection
    ):
        """Test delete requires explicit confirmation header."""
        with patch(
            "backend.database.queries.delete_profile", return_value=True
        ) as mock_delete:
            response = await client.delete("/api/profile")
            assert response.status_code == 400
            assert mock_delete.called is False

    async def test_delete_profile_success(self, client, mock_neo4j_connection):
        """Test successful profile deletion."""
        with patch("backend.database.queries.delete_profile", return_value=True):
            response = await client.delete(
                "/api/profile", headers={"X-Confirm-Delete-Profile": "true"}
            )
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert "message" in data

    async def test_delete_profile_not_found(self, client, mock_neo4j_connection):
        """Test delete non-existent profile."""
        with patch("backend.database.queries.delete_profile", return_value=False):
            response = await client.delete(
                "/api/profile", headers={"X-Confirm-Delete-Profile": "true"}
            )
            assert response.status_code == 404

    async def test_delete_profile_server_error(self, client, mock_neo4j_connection):
        """Test delete profile with server error."""
        with patch(
            "backend.database.queries.delete_profile",
            side_effect=Exception("Database error"),
        ):
            response = await client.delete(
                "/api/profile", headers={"X-Confirm-Delete-Profile": "true"}
            )
            assert response.status_code == 500


@pytest.mark.asyncio
@pytest.mark.api
class TestListProfiles:
    """Test GET /api/profiles endpoint."""

    async def test_list_profiles_success(self, client, mock_neo4j_connection):
        """Test successful profile list retrieval."""
        profiles_data = [
            {"name": "John Doe", "updated_at": "2024-01-01T00:00:00", "language": "en"},
            {"name": "Jane Smith", "updated_at": "2024-01-02T00:00:00", "language": "es"},
        ]
        with patch(
            "backend.database.queries.list_profiles", return_value=profiles_data
        ):
            response = await client.get("/api/profiles")
            assert response.status_code == 200
            data = response.json()
            assert "profiles" in data
            assert len(data["profiles"]) == 2
            assert data["profiles"][0]["name"] == "John Doe"
            assert data["profiles"][0]["updated_at"] == "2024-01-01T00:00:00"
            assert data["profiles"][0]["language"] == "en"
            assert data["profiles"][1]["name"] == "Jane Smith"
            assert data["profiles"][1]["updated_at"] == "2024-01-02T00:00:00"
            assert data["profiles"][1]["language"] == "es"

    async def test_list_profiles_empty(self, client, mock_neo4j_connection):
        """Test profile list when no profiles exist."""
        with patch("backend.database.queries.list_profiles", return_value=[]):
            response = await client.get("/api/profiles")
            assert response.status_code == 200
            data = response.json()
            assert "profiles" in data
            assert len(data["profiles"]) == 0

    async def test_list_profiles_with_null_language(self, client, mock_neo4j_connection):
        """Test profile list with null language values (should fallback to 'en')."""
        profiles_data = [
            {"name": "John Doe", "updated_at": "2024-01-01T00:00:00", "language": None},
            {"name": "Jane Smith", "updated_at": "2024-01-02T00:00:00", "language": "es"},
            {"name": "Bob Wilson", "updated_at": "2024-01-03T00:00:00", "language": None},
        ]
        with patch(
            "backend.database.queries.list_profiles", return_value=profiles_data
        ):
            response = await client.get("/api/profiles")
            assert response.status_code == 200
            data = response.json()
            assert "profiles" in data
            assert len(data["profiles"]) == 3

            # Check that null languages are converted to 'en'
            assert data["profiles"][0]["language"] == "en"  # None -> 'en'
            assert data["profiles"][1]["language"] == "es"  # Kept as 'es'
            assert data["profiles"][2]["language"] == "en"  # None -> 'en'

    async def test_list_profiles_server_error(self, client, mock_neo4j_connection):
        """Test list profiles with server error."""
        with patch(
            "backend.database.queries.list_profiles",
            side_effect=Exception("Database error"),
        ):
            response = await client.get("/api/profiles")
            assert response.status_code == 500


@pytest.mark.asyncio
@pytest.mark.api
class TestGetProfileByUpdatedAt:
    """Test GET /api/profile/{updated_at} endpoint."""

    async def test_get_profile_by_updated_at_success(
        self, client, mock_neo4j_connection
    ):
        """Test successful profile retrieval by updated_at."""
        profile_data = {
            "personal_info": {"name": "John Doe", "email": "john@example.com"},
            "experience": [],
            "education": [],
            "skills": [],
            "updated_at": "2024-01-01T00:00:00",
        }
        with patch(
            "backend.database.queries.get_profile_by_updated_at",
            return_value=profile_data,
        ):
            response = await client.get("/api/profile/2024-01-01T00:00:00")
            assert response.status_code == 200
            data = response.json()
            assert "personal_info" in data
            assert data["personal_info"]["name"] == "John Doe"

    async def test_get_profile_by_updated_at_not_found(
        self, client, mock_neo4j_connection
    ):
        """Test profile retrieval by updated_at when not found."""
        with patch(
            "backend.database.queries.get_profile_by_updated_at", return_value=None
        ):
            response = await client.get("/api/profile/2024-01-01T00:00:00")
            assert response.status_code == 404

    async def test_get_profile_by_updated_at_server_error(
        self, client, mock_neo4j_connection
    ):
        """Test get profile by updated_at with server error."""
        with patch(
            "backend.database.queries.get_profile_by_updated_at",
            side_effect=Exception("Database error"),
        ):
            response = await client.get("/api/profile/2024-01-01T00:00:00")
            assert response.status_code == 500


@pytest.mark.asyncio
@pytest.mark.api
class TestDeleteProfileByUpdatedAt:
    """Test DELETE /api/profile/{updated_at} endpoint."""

    async def test_delete_profile_by_updated_at_requires_confirmation_header(
        self, client, mock_neo4j_connection
    ):
        """Test delete requires explicit confirmation header."""
        with patch(
            "backend.database.queries.delete_profile_by_updated_at",
            return_value=True,
        ) as mock_delete:
            response = await client.delete("/api/profile/2024-01-01T00:00:00")
            assert response.status_code == 400
            assert mock_delete.called is False

    async def test_delete_profile_by_updated_at_success(
        self, client, mock_neo4j_connection
    ):
        """Test successful profile deletion by updated_at."""
        with patch(
            "backend.database.queries.delete_profile_by_updated_at", return_value=True
        ):
            response = await client.delete(
                "/api/profile/2024-01-01T00:00:00",
                headers={"X-Confirm-Delete-Profile": "true"},
            )
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert "message" in data

    async def test_delete_profile_by_updated_at_not_found(
        self, client, mock_neo4j_connection
    ):
        """Test delete non-existent profile by updated_at."""
        with patch(
            "backend.database.queries.delete_profile_by_updated_at", return_value=False
        ):
            response = await client.delete(
                "/api/profile/2024-01-01T00:00:00",
                headers={"X-Confirm-Delete-Profile": "true"},
            )
            assert response.status_code == 404

    async def test_delete_profile_by_updated_at_server_error(
        self, client, mock_neo4j_connection
    ):
        """Test delete profile by updated_at with server error."""
        with patch(
            "backend.database.queries.delete_profile_by_updated_at",
            side_effect=Exception("Database error"),
        ):
            response = await client.delete(
                "/api/profile/2024-01-01T00:00:00",
                headers={"X-Confirm-Delete-Profile": "true"},
            )
            assert response.status_code == 500


@pytest.mark.asyncio
@pytest.mark.api
class TestTranslateProfile:
    """Test POST /api/profile/translate endpoint."""

    async def test_translate_profile_success(
        self, client, sample_cv_data, mock_neo4j_connection
    ):
        """Test successful profile translation."""
        profile_data = {
            "personal_info": sample_cv_data["personal_info"],
            "experience": sample_cv_data["experience"],
            "education": sample_cv_data["education"],
            "skills": sample_cv_data["skills"],
            "language": "en",
        }
        translate_request = {
            "profile_data": profile_data,
            "target_language": "es",
        }
        translated_profile = {
            **profile_data,
            "language": "es",
            "personal_info": {
                **profile_data["personal_info"],
                "summary": "Resumen profesional traducido",
            },
        }

        with patch(
            "backend.services.profile_translation.get_translation_service"
        ) as mock_get_service, patch(
            "backend.app_helpers.routes.profile.get_profile_by_language", return_value=None
        ):
            mock_service = AsyncMock()
            mock_service.translate_profile.return_value = translated_profile
            mock_get_service.return_value = mock_service

            response = await client.post("/api/profile/translate", json=translate_request)
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert "translated_profile" in data
            assert data["translated_profile"]["language"] == "es"
            assert "message" in data

    async def test_translate_profile_ai_not_configured(
        self, client, sample_cv_data, mock_neo4j_connection
    ):
        """Test translation when AI service is not configured."""
        profile_data = {
            "personal_info": sample_cv_data["personal_info"],
            "experience": sample_cv_data["experience"],
            "education": sample_cv_data["education"],
            "skills": sample_cv_data["skills"],
            "language": "en",
        }
        translate_request = {
            "profile_data": profile_data,
            "target_language": "es",
        }

        with patch(
            "backend.services.profile_translation.get_translation_service"
        ) as mock_get_service:
            mock_service = AsyncMock()
            mock_service.translate_profile.side_effect = ValueError("AI service is not configured")
            mock_get_service.return_value = mock_service

            response = await client.post("/api/profile/translate", json=translate_request)
            assert response.status_code == 503
            data = response.json()
            assert "AI translation service is not configured" in data["detail"]

    async def test_translate_profile_validation_error(self, client):
        """Test translation with invalid request data."""
        invalid_request = {
            "profile_data": {"personal_info": {"name": ""}},  # Invalid: empty name
            "target_language": "invalid-language-code",
        }
        response = await client.post("/api/profile/translate", json=invalid_request)
        error_data = assert_validation_error_response(response)
        # Should have multiple validation errors (empty name + invalid language)
        assert len(error_data["detail"]) >= 2

    async def test_translate_profile_server_error(
        self, client, sample_cv_data, mock_neo4j_connection
    ):
        """Test translation with server error."""
        profile_data = {
            "personal_info": sample_cv_data["personal_info"],
            "experience": sample_cv_data["experience"],
            "education": sample_cv_data["education"],
            "skills": sample_cv_data["skills"],
            "language": "en",
        }
        translate_request = {
            "profile_data": profile_data,
            "target_language": "es",
        }

        with patch(
            "backend.services.profile_translation.get_translation_service"
        ) as mock_get_service:
            mock_service = AsyncMock()
            mock_service.translate_profile.side_effect = Exception("Translation service error")
            mock_get_service.return_value = mock_service

            response = await client.post("/api/profile/translate", json=translate_request)
            assert response.status_code == 500


@pytest.mark.asyncio
@pytest.mark.api
class TestSaveProfileCreateNew:
    """Test save profile with create_new parameter."""

    async def test_save_profile_create_new_true(
        self, client, sample_cv_data, mock_neo4j_connection
    ):
        """Test saving profile with create_new=true creates new profile."""
        profile_data = {
            "personal_info": sample_cv_data["personal_info"],
            "experience": sample_cv_data["experience"],
            "education": sample_cv_data["education"],
            "skills": sample_cv_data["skills"],
        }

        with patch("backend.database.queries.create_profile", return_value=True) as mock_create:
            response = await client.post("/api/profile?create_new=true", json=profile_data)
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            mock_create.assert_called_once_with(profile_data)

    async def test_save_profile_create_new_false(
        self, client, sample_cv_data, mock_neo4j_connection
    ):
        """Test saving profile with create_new=false updates existing."""
        profile_data = {
            "personal_info": sample_cv_data["personal_info"],
            "experience": sample_cv_data["experience"],
            "education": sample_cv_data["education"],
            "skills": sample_cv_data["skills"],
        }

        with patch("backend.database.queries.update_profile", return_value=True) as mock_update, \
             patch("backend.database.queries._check_profile_exists", return_value=True):
            response = await client.post("/api/profile?create_new=false", json=profile_data)
            assert response.status_code == 200
            mock_update.assert_called_once_with(profile_data)

    async def test_save_profile_default_behavior(
        self, client, sample_cv_data, mock_neo4j_connection
    ):
        """Test default save behavior when no create_new parameter."""
        profile_data = {
            "personal_info": sample_cv_data["personal_info"],
            "experience": sample_cv_data["experience"],
            "education": sample_cv_data["education"],
            "skills": sample_cv_data["skills"],
        }

        # Test when no profile exists (should create)
        with patch("backend.database.queries.create_profile", return_value=True) as mock_create, \
             patch("backend.database.queries._check_profile_exists", return_value=False):
            response = await client.post("/api/profile", json=profile_data)
            assert response.status_code == 200
            mock_create.assert_called_once_with(profile_data)

        # Test when profile exists (should update)
        with patch("backend.database.queries.update_profile", return_value=True) as mock_update, \
             patch("backend.database.queries._check_profile_exists", return_value=True):
            response = await client.post("/api/profile", json=profile_data)
            assert response.status_code == 200
            mock_update.assert_called_once_with(profile_data)
