"""Tests for CVFileService."""
from backend.services.cv_file_service import CVFileService


class TestPrepareCVDict:
    """Test prepare_cv_dict method."""

    def test_prepare_cv_dict_with_theme(self, temp_output_dir):
        """Test that theme from cv dict is preserved."""
        service = CVFileService(temp_output_dir)
        cv = {
            "personal_info": {"name": "John Doe"},
            "experience": [],
            "education": [],
            "skills": [],
            "theme": "modern",
        }
        result = service.prepare_cv_dict(cv)
        assert result["theme"] == "modern"
        assert result["personal_info"] == {"name": "John Doe"}

    def test_prepare_cv_dict_defaults_to_classic(self, temp_output_dir):
        """Test that theme defaults to 'classic' when not provided."""
        service = CVFileService(temp_output_dir)
        cv = {
            "personal_info": {"name": "John Doe"},
            "experience": [],
            "education": [],
            "skills": [],
        }
        result = service.prepare_cv_dict(cv)
        assert result["theme"] == "classic"

    def test_prepare_cv_dict_extracts_all_fields(self, temp_output_dir):
        """Test that all fields are correctly extracted."""
        service = CVFileService(temp_output_dir)
        cv = {
            "personal_info": {"name": "Jane Doe", "email": "jane@example.com"},
            "experience": [{"title": "Developer", "company": "Tech Corp"}],
            "education": [{"degree": "BS", "institution": "University"}],
            "skills": [{"name": "Python", "level": "Expert"}],
            "theme": "minimal",
        }
        result = service.prepare_cv_dict(cv)
        assert result["personal_info"] == cv["personal_info"]
        assert result["experience"] == cv["experience"]
        assert result["education"] == cv["education"]
        assert result["skills"] == cv["skills"]
        assert result["theme"] == "minimal"

    def test_prepare_cv_dict_handles_missing_optional_fields(self, temp_output_dir):
        """Test that missing optional fields default to empty collections."""
        service = CVFileService(temp_output_dir)
        cv = {
            "personal_info": {"name": "John Doe"},
        }
        result = service.prepare_cv_dict(cv)
        assert result["experience"] == []
        assert result["education"] == []
        assert result["skills"] == []
        assert result["theme"] == "classic"
