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

    def test_generate_file_for_cv_includes_theme(
        self, temp_output_dir, sample_cv_data
    ):
        """Test that generate_file_for_cv passes theme to generator."""
        service = CVFileService(temp_output_dir)
        cv_id = "test-cv-123"
        sample_cv_data["theme"] = "elegant"

        filename = service.generate_file_for_cv(cv_id, sample_cv_data)
        assert filename.startswith("cv_")
        assert filename.endswith(".html")

        # Verify file was created
        output_path = temp_output_dir / filename
        assert output_path.exists()

    def test_generate_file_for_cv_defaults_theme_when_missing(
        self, temp_output_dir, sample_cv_data
    ):
        """Test that generate_file_for_cv defaults theme when missing."""
        service = CVFileService(temp_output_dir)
        cv_id = "test-cv-456"
        # Remove theme from sample data
        if "theme" in sample_cv_data:
            del sample_cv_data["theme"]

        filename = service.generate_file_for_cv(cv_id, sample_cv_data)
        assert filename.startswith("cv_")
        assert filename.endswith(".html")

        # Verify file was created
        output_path = temp_output_dir / filename
        assert output_path.exists()

    def test_generate_file_for_cv_all_themes(self, temp_output_dir, sample_cv_data):
        """Test generate_file_for_cv with all supported themes."""
        service = CVFileService(temp_output_dir)
        themes = [
            "accented",
            "classic",
            "colorful",
            "creative",
            "elegant",
            "executive",
            "minimal",
            "modern",
            "professional",
            "tech",
        ]

        for i, theme in enumerate(themes):
            cv_id = f"test-cv-{i}"
            sample_cv_data["theme"] = theme
            filename = service.generate_file_for_cv(cv_id, sample_cv_data)
            assert filename.startswith("cv_")
            assert filename.endswith(".html")

            # Verify file was created
            output_path = temp_output_dir / filename
            assert output_path.exists()
