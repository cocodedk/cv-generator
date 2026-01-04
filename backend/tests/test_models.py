"""Tests for Pydantic models."""
import pytest
from pydantic import ValidationError
from backend.models import (
    Address,
    PersonalInfo,
    Project,
    Experience,
    Education,
    Skill,
    CVData,
    CVResponse,
    CVListItem,
    CVListResponse,
)


class TestAddress:
    """Test Address model."""

    def test_valid_address(self):
        """Test creating valid address."""
        address = Address(
            street="123 Main St",
            city="New York",
            state="NY",
            zip="10001",
            country="USA",
        )
        assert address.street == "123 Main St"
        assert address.city == "New York"

    def test_partial_address(self):
        """Test address with partial data."""
        address = Address(city="New York")
        assert address.city == "New York"
        assert address.street is None


class TestPersonalInfo:
    """Test PersonalInfo model."""

    def test_valid_personal_info(self):
        """Test creating valid personal info."""
        info = PersonalInfo(name="John Doe", email="john@example.com")
        assert info.name == "John Doe"
        assert info.email == "john@example.com"

    def test_name_required(self):
        """Test that name is required."""
        with pytest.raises(ValidationError):
            PersonalInfo()

    def test_name_min_length(self):
        """Test name minimum length validation."""
        with pytest.raises(ValidationError):
            PersonalInfo(name="")

    def test_invalid_email(self):
        """Test email validation."""
        with pytest.raises(ValidationError):
            PersonalInfo(name="John Doe", email="invalid-email")

    def test_empty_email_is_allowed(self):
        """Test that empty-string email is treated as missing."""
        info = PersonalInfo(name="John Doe", email="")
        assert info.email is None


class TestExperience:
    """Test Experience model."""

    def test_valid_experience(self):
        """Test creating valid experience."""
        exp = Experience(title="Developer", company="Tech Corp", start_date="2020-01")
        assert exp.title == "Developer"
        assert exp.company == "Tech Corp"
        assert exp.projects == []

    def test_required_fields(self):
        """Test required fields."""
        with pytest.raises(ValidationError):
            Experience(title="Developer")

    def test_end_date_optional(self):
        """Test that end_date is optional."""
        exp = Experience(title="Developer", company="Tech Corp", start_date="2020-01")
        assert exp.end_date is None

    def test_description_accepts_html(self):
        """Test that description can contain HTML formatting."""
        html_desc = "<p>Built <strong>web services</strong> using <em>FastAPI</em>.</p>"
        exp = Experience(
            title="Developer",
            company="Tech Corp",
            start_date="2020-01",
            description=html_desc,
        )
        assert exp.description == html_desc

    def test_description_validates_plain_text_length(self):
        """Test that description validates plain text length (HTML stripped)."""
        # HTML with 50 chars of plain text should pass
        html_short = "<p>" + "x" * 50 + "</p>"
        exp = Experience(
            title="Developer",
            company="Tech Corp",
            start_date="2020-01",
            description=html_short,
        )
        assert exp.description == html_short

        # Plain text over 300 chars should fail
        long_text = "x" * 301
        with pytest.raises(ValidationError) as exc_info:
            Experience(
                title="Developer",
                company="Tech Corp",
                start_date="2020-01",
                description=long_text,
            )
        assert "300" in str(exc_info.value)

    def test_description_strips_html_for_validation(self):
        """Test that HTML tags are stripped when validating length."""
        # HTML with tags that make it look long, but plain text is short
        html_with_tags = "<p><strong><em>" + "x" * 50 + "</em></strong></p>"
        exp = Experience(
            title="Developer",
            company="Tech Corp",
            start_date="2020-01",
            description=html_with_tags,
        )
        assert exp.description == html_with_tags

        # HTML with 301 chars of plain text should fail even with tags
        long_plain = "x" * 301
        html_long = f"<p>{long_plain}</p>"
        with pytest.raises(ValidationError):
            Experience(
                title="Developer",
                company="Tech Corp",
                start_date="2020-01",
                description=html_long,
            )

    def test_description_handles_html_entities(self):
        """Test that HTML entities are decoded when counting plain text length."""
        # &nbsp; should count as 1 character, not 5
        text_with_entities = "x" * 299 + "&nbsp;"
        exp = Experience(
            title="Developer",
            company="Tech Corp",
            start_date="2020-01",
            description=text_with_entities,
        )
        assert exp.description == text_with_entities


class TestProject:
    """Test Project model."""

    def test_valid_project(self):
        project = Project(
            name="Billing Revamp",
            description="Rebuilt the billing pipeline.",
            technologies=["Python", "PostgreSQL"],
            highlights=["Reduced failed charges by 30%"],
        )
        assert project.name == "Billing Revamp"
        assert project.technologies == ["Python", "PostgreSQL"]

    def test_project_name_required(self):
        with pytest.raises(ValidationError):
            Project()


class TestEducation:
    """Test Education model."""

    def test_valid_education(self):
        """Test creating valid education."""
        edu = Education(degree="BS Computer Science", institution="University")
        assert edu.degree == "BS Computer Science"
        assert edu.institution == "University"

    def test_required_fields(self):
        """Test required fields."""
        with pytest.raises(ValidationError):
            Education(degree="BS")


class TestSkill:
    """Test Skill model."""

    def test_valid_skill(self):
        """Test creating valid skill."""
        skill = Skill(name="Python", category="Programming")
        assert skill.name == "Python"
        assert skill.category == "Programming"

    def test_name_required(self):
        """Test that name is required."""
        with pytest.raises(ValidationError):
            Skill()


class TestCVData:
    """Test CVData model."""

    def test_valid_cv_data(self, sample_cv_data):
        """Test creating valid CV data."""
        cv = CVData(**sample_cv_data)
        assert cv.personal_info.name == "John Doe"
        assert len(cv.experience) == 1
        assert len(cv.experience[0].projects) == 1
        assert len(cv.education) == 1
        assert len(cv.skills) == 2

    def test_personal_info_required(self):
        """Test that personal_info is required."""
        with pytest.raises(ValidationError):
            CVData(experience=[], education=[], skills=[])

    def test_empty_lists_default(self):
        """Test that lists default to empty."""
        cv = CVData(personal_info={"name": "John Doe"})
        assert cv.experience == []
        assert cv.education == []
        assert cv.skills == []

    def test_cv_data_with_valid_theme(self):
        """Test CV data with valid theme values."""
        valid_themes = [
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
        for theme in valid_themes:
            cv = CVData(
                personal_info={"name": "John Doe"},
                theme=theme,
            )
            assert cv.theme == theme

    def test_cv_data_without_theme(self):
        """Test that theme defaults to classic when not provided."""
        cv = CVData(personal_info={"name": "John Doe"})
        assert cv.theme == "classic"

    def test_cv_data_with_invalid_theme(self):
        """Test that invalid theme values are accepted (no strict validation)."""
        # Note: Pydantic doesn't enforce enum validation by default for Optional[str]
        # Invalid themes are accepted but may cause issues in CV generation
        cv = CVData(
            personal_info={"name": "John Doe"},
            theme="invalid_theme",
        )
        assert cv.theme == "invalid_theme"


class TestCVResponse:
    """Test CVResponse model."""

    def test_valid_response(self):
        """Test creating valid response."""
        response = CVResponse(cv_id="test-id", filename="cv.html")
        assert response.cv_id == "test-id"
        assert response.filename == "cv.html"
        assert response.status == "success"


class TestCVListItem:
    """Test CVListItem model."""

    def test_valid_list_item(self):
        """Test creating valid list item."""
        item = CVListItem(
            cv_id="test-id",
            created_at="2024-01-01T00:00:00",
            updated_at="2024-01-01T00:00:00",
        )
        assert item.cv_id == "test-id"


class TestCVListResponse:
    """Test CVListResponse model."""

    def test_valid_list_response(self):
        """Test creating valid list response."""
        response = CVListResponse(cvs=[], total=0)
        assert response.cvs == []
        assert response.total == 0
