"""Tests for template utilities."""
import tempfile
import yaml
from pathlib import Path
from backend.cv_generator.template import load_template, validate_template


class TestLoadTemplate:
    """Test load_template function."""

    def test_load_template_valid_yaml(self):
        """Test loading valid YAML template."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            template_data = {
                "personal_info": {"name": "Test User", "email": "test@example.com"}
            }
            yaml.dump(template_data, f)
            temp_path = f.name

        try:
            result = load_template(temp_path)
            assert result["personal_info"]["name"] == "Test User"
            assert result["personal_info"]["email"] == "test@example.com"
        finally:
            Path(temp_path).unlink()

    def test_load_template_missing_file(self):
        """Test loading non-existent file raises FileNotFoundError."""
        import pytest

        with pytest.raises(FileNotFoundError):
            load_template("/nonexistent/path/template.yaml")


class TestValidateTemplate:
    """Test validate_template function."""

    def test_validate_template_valid_structure(self):
        """Test validation with valid template structure."""
        template_data = {
            "personal_info": {"name": "Test User", "email": "test@example.com"}
        }
        assert validate_template(template_data) is True

    def test_validate_template_missing_personal_info(self):
        """Test validation fails when personal_info is missing."""
        template_data = {"experience": []}
        assert validate_template(template_data) is False

    def test_validate_template_empty_dict(self):
        """Test validation fails with empty dictionary."""
        assert validate_template({}) is False

    def test_validate_template_partial_personal_info(self):
        """Test validation passes with partial personal_info."""
        template_data = {"personal_info": {"name": "Test User"}}
        assert validate_template(template_data) is True
