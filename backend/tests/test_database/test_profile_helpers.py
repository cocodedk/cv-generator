"""Tests for profile helper functions."""
from backend.database.queries.profile_helpers import (
    build_save_params,
    build_address,
    process_profile_record,
)


class TestBuildSaveParams:
    """Test build_save_params function."""

    def test_build_save_params_full_data(self):
        """Test with full profile data."""
        profile_data = {
            "personal_info": {
                "name": "John Doe",
                "email": "john@example.com",
                "phone": "123-456-7890",
                "address": {
                    "street": "123 Main St",
                    "city": "New York",
                    "state": "NY",
                    "zip": "10001",
                    "country": "USA",
                },
                "linkedin": "linkedin.com/in/johndoe",
                "github": "github.com/johndoe",
                "website": "johndoe.com",
                "summary": "Test summary",
            },
            "experience": [{"title": "Developer"}],
            "education": [{"degree": "BS"}],
            "skills": [{"name": "Python"}],
        }

        result = build_save_params(profile_data, "2024-01-01T00:00:00")

        assert result["name"] == "John Doe"
        assert result["email"] == "john@example.com"
        assert result["address_street"] == "123 Main St"
        assert result["address_city"] == "New York"
        assert len(result["experiences"]) == 1
        assert len(result["educations"]) == 1
        assert len(result["skills"]) == 1

    def test_build_save_params_missing_optional_fields(self):
        """Test with missing optional fields."""
        profile_data = {
            "personal_info": {"name": "Jane Doe"},
            "experience": [],
            "education": [],
            "skills": [],
        }

        result = build_save_params(profile_data, "2024-01-01T00:00:00")

        assert result["name"] == "Jane Doe"
        assert result["email"] is None
        assert result["phone"] is None
        assert result["address_street"] is None


class TestBuildAddress:
    """Test build_address function."""

    def test_build_address_all_fields(self):
        """Test with all address fields."""
        person = {
            "address_street": "123 Main St",
            "address_city": "New York",
            "address_state": "NY",
            "address_zip": "10001",
            "address_country": "USA",
        }

        result = build_address(person)

        assert result["street"] == "123 Main St"
        assert result["city"] == "New York"
        assert result["state"] == "NY"
        assert result["zip"] == "10001"
        assert result["country"] == "USA"

    def test_build_address_partial_fields(self):
        """Test with partial address fields."""
        person = {"address_city": "New York", "address_state": "NY"}

        result = build_address(person)

        assert result["city"] == "New York"
        assert result["state"] == "NY"
        assert result["street"] is None

    def test_build_address_empty(self):
        """Test with no address fields."""
        person = {}

        result = build_address(person)

        assert result is None

    def test_build_address_none_values(self):
        """Test with None values in address fields."""
        person = {"address_street": None, "address_city": None}

        result = build_address(person)

        assert result is None


class TestProcessProfileRecord:
    """Test process_profile_record function."""

    def test_process_profile_record_valid(self):
        """Test with valid record."""
        record = {
            "person": {
                "name": "John Doe",
                "email": "john@example.com",
                "address_street": "123 Main St",
                "address_city": "New York",
            },
            "profile": {"updated_at": "2024-01-01T00:00:00"},
            "experiences": [{"title": "Developer"}],
            "educations": [{"degree": "BS"}],
            "skills": [{"name": "Python"}],
        }

        result = process_profile_record(record)

        assert result is not None
        assert result["personal_info"]["name"] == "John Doe"
        assert len(result["experience"]) == 1
        assert len(result["education"]) == 1
        assert len(result["skills"]) == 1

    def test_process_profile_record_none(self):
        """Test with None record."""
        result = process_profile_record(None)
        assert result is None

    def test_process_profile_record_no_person(self):
        """Test with record missing person."""
        record = {"person": None}

        result = process_profile_record(record)
        assert result is None
