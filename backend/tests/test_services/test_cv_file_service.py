"""Tests for CVFileService."""
import json
import pytest
from unittest.mock import AsyncMock, Mock, patch
from backend.services.cv_file_service import CVFileService
from backend.cv_generator.layouts import LAYOUTS


def build_service(
    temp_output_dir,
    showcase_enabled=False,
    pdf_service=None,
    featured_templates_dir=None,
):
    return CVFileService(
        temp_output_dir,
        temp_output_dir / "showcase",
        temp_output_dir / "showcase_keys",
        showcase_enabled=showcase_enabled,
        pdf_service=pdf_service,
        featured_templates_dir=featured_templates_dir,
    )


class TestPrepareCVDict:
    """Test prepare_cv_dict method."""

    def test_prepare_cv_dict_with_theme(self, temp_output_dir):
        """Test that theme from cv dict is preserved."""
        service = build_service(temp_output_dir, showcase_enabled=False)
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
        service = build_service(temp_output_dir, showcase_enabled=False)
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
        service = build_service(temp_output_dir, showcase_enabled=False)
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
        service = build_service(temp_output_dir, showcase_enabled=False)
        cv = {
            "personal_info": {"name": "John Doe"},
        }
        result = service.prepare_cv_dict(cv)
        assert result["experience"] == []
        assert result["education"] == []
        assert result["skills"] == []
        assert result["theme"] == "classic"

    def test_generate_file_for_cv_includes_theme(self, temp_output_dir, sample_cv_data):
        """Test that generate_file_for_cv passes theme to generator."""
        service = build_service(temp_output_dir, showcase_enabled=False)
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
        service = build_service(temp_output_dir, showcase_enabled=False)
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
        service = build_service(temp_output_dir, showcase_enabled=False)
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


class TestGenerateShowcaseForCV:
    """Test generate_showcase_for_cv method."""

    def test_generate_showcase_disabled_returns_none(
        self, temp_output_dir, sample_cv_data
    ):
        """Test that generate_showcase_for_cv returns None when disabled."""
        service = build_service(temp_output_dir, showcase_enabled=False)
        cv_id = "test-cv-123"
        result = service.generate_showcase_for_cv(cv_id, sample_cv_data)
        assert result is None

    def test_generate_showcase_enabled_generates_files(
        self, temp_output_dir, sample_cv_data
    ):
        """Test that generate_showcase_for_cv generates files when enabled."""
        service = build_service(temp_output_dir, showcase_enabled=True)
        cv_id = "test-cv-123"
        result = service.generate_showcase_for_cv(cv_id, sample_cv_data)
        assert result is not None
        assert result["cv_id"] == cv_id
        assert "layouts" in result
        assert "theme" in result

    def test_generate_showcase_all_layouts_generated(
        self, temp_output_dir, sample_cv_data
    ):
        """Test that all layouts are generated."""
        service = build_service(temp_output_dir, showcase_enabled=True)
        cv_id = "test-cv-123"
        result = service.generate_showcase_for_cv(cv_id, sample_cv_data)
        assert len(result["layouts"]) == len(LAYOUTS)
        layout_names = {layout["layout"] for layout in result["layouts"]}
        assert layout_names == set(LAYOUTS.keys())

    def test_generate_showcase_manifest_created(self, temp_output_dir, sample_cv_data):
        """Test that manifest.json is created with correct structure."""
        service = build_service(temp_output_dir, showcase_enabled=True)
        cv_id = "test-cv-123"
        service.generate_showcase_for_cv(cv_id, sample_cv_data)
        manifest_path = temp_output_dir / "showcase" / cv_id / "manifest.json"
        assert manifest_path.exists()
        manifest_content = json.loads(manifest_path.read_text(encoding="utf-8"))
        assert manifest_content["cv_id"] == cv_id
        assert manifest_content["name"] == sample_cv_data["personal_info"]["name"]
        assert manifest_content["theme"] == sample_cv_data.get("theme", "classic")
        assert "layouts" in manifest_content
        assert "updated_at" in manifest_content

    def test_generate_showcase_index_json_updated(
        self, temp_output_dir, sample_cv_data
    ):
        """Test that index.json is updated."""
        service = build_service(temp_output_dir, showcase_enabled=True)
        cv_id = "test-cv-123"
        service.generate_showcase_for_cv(cv_id, sample_cv_data)
        index_path = temp_output_dir / "showcase" / "index.json"
        assert index_path.exists()
        index_content = json.loads(index_path.read_text(encoding="utf-8"))
        assert "generated_at" in index_content
        assert "cvs" in index_content
        assert len(index_content["cvs"]) == 1
        assert index_content["cvs"][0]["cv_id"] == cv_id

    def test_generate_showcase_key_generation(self, temp_output_dir, sample_cv_data):
        """Test key generation and persistence."""
        service = build_service(temp_output_dir, showcase_enabled=True)
        cv_id = "test-cv-123"
        service.generate_showcase_for_cv(cv_id, sample_cv_data)
        key_path = temp_output_dir / "showcase_keys" / f"{cv_id}.key"
        assert key_path.exists()
        key = key_path.read_text(encoding="utf-8").strip()
        assert len(key) > 0

    def test_generate_showcase_same_cv_uses_same_key(
        self, temp_output_dir, sample_cv_data
    ):
        """Test that same CV ID uses same key on subsequent calls."""
        service = build_service(temp_output_dir, showcase_enabled=True)
        cv_id = "test-cv-123"
        service.generate_showcase_for_cv(cv_id, sample_cv_data)
        key_path = temp_output_dir / "showcase_keys" / f"{cv_id}.key"
        first_key = key_path.read_text(encoding="utf-8").strip()
        # Generate again
        service.generate_showcase_for_cv(cv_id, sample_cv_data)
        second_key = key_path.read_text(encoding="utf-8").strip()
        assert first_key == second_key

    def test_generate_showcase_scrambled_html_files_created(
        self, temp_output_dir, sample_cv_data
    ):
        """Test that scrambled HTML files are created in correct directory structure."""
        service = build_service(temp_output_dir, showcase_enabled=True)
        cv_id = "test-cv-123"
        theme = sample_cv_data.get("theme", "classic")
        service.generate_showcase_for_cv(cv_id, sample_cv_data)
        cv_output_dir = temp_output_dir / "showcase" / cv_id
        assert cv_output_dir.exists()
        # Check that HTML files are created for each layout
        for layout_name in LAYOUTS.keys():
            filename = f"{layout_name}-{theme}.html"
            html_path = cv_output_dir / filename
            assert html_path.exists()
            # Verify HTML contains scramble script
            html_content = html_path.read_text(encoding="utf-8")
            assert "unlockWithKey" in html_content
            # Verify personal info is scrambled (original name should not be in HTML)
            assert sample_cv_data["personal_info"]["name"] not in html_content


class TestGenerateFeaturedTemplates:
    """Test generate_featured_templates method."""

    @pytest.mark.asyncio
    async def test_generate_featured_templates_writes_pdf_files(
        self, temp_output_dir, sample_cv_data
    ):
        """Test that featured templates include owner-named HTML and PDF files."""
        templates_dir = temp_output_dir / "templates"
        pdf_service = Mock()
        pdf_service.generate_long_pdf = AsyncMock(return_value=b"%PDF-1.4 test")
        service = build_service(
            temp_output_dir,
            showcase_enabled=False,
            pdf_service=pdf_service,
            featured_templates_dir=templates_dir,
        )
        with patch("backend.database.queries.get_profile", return_value=sample_cv_data):
            result = await service.generate_featured_templates()

        assert result is not None
        assert result["profile_name"] == "John Doe"
        assert result["templates"]
        expected_slug = service._slugify_owner(sample_cv_data["personal_info"]["name"])
        for template in result["templates"]:
            assert template["file"].startswith(f"{expected_slug}-")
            assert template["pdf_file"].startswith(f"pdfs/{expected_slug}-")
            assert (templates_dir / template["file"]).exists()
            assert (templates_dir / template["pdf_file"]).exists()
        assert pdf_service.generate_long_pdf.await_count == len(result["templates"])

    def test_slugify_owner_fallback(self, temp_output_dir):
        """Test slugify fallback when name is empty or invalid."""
        service = build_service(temp_output_dir, showcase_enabled=False)
        assert service._slugify_owner("") == "profile"
