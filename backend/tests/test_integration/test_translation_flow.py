"""
Integration tests for the complete translation flow
"""
import pytest
from unittest.mock import AsyncMock, patch
from pydantic import ValidationError

from backend.services.profile_translation import ProfileTranslationService
from backend.models.profile import TranslateProfileRequest


@pytest.mark.asyncio
@pytest.mark.integration
class TestTranslationFlowIntegration:
    """Test the complete translation flow from API to service."""

    async def test_full_translation_flow_success(self):
        """Test complete translation flow with mocked LLM."""
        # Sample profile data
        profile_data = {
            "personal_info": {
                "name": "John Doe",
                "title": "Software Engineer",
                "summary": "Experienced developer with 5 years in web development",
                "email": "john@example.com",
            },
            "experience": [
                {
                    "title": "Senior Developer",
                    "company": "Tech Corp",
                    "description": "Led development of web applications using React and Node.js",
                    "location": "New York",
                    "projects": [
                        {
                            "name": "E-commerce Platform",
                            "description": "Built scalable e-commerce platform handling 10k+ users",
                            "highlights": ["Improved performance by 40%", "Reduced load time by 60%"],
                            "technologies": ["React", "Node.js"],
                        }
                    ],
                }
            ],
            "education": [
                {
                    "degree": "Bachelor of Science",
                    "institution": "State University",
                    "field": "Computer Science",
                    "year": "2020",
                }
            ],
            "skills": [
                {"name": "JavaScript", "category": "Programming"},
                {"name": "React", "category": "Frontend"},
            ],
            "language": "en",
        }

        # Expected translated content
        expected_translations = {
            "Software Engineer": "Ingeniero de Software",
            "Experienced developer with 5 years in web development": "Desarrollador experimentado con 5 años en desarrollo web",
            "Senior Developer": "Desarrollador Senior",
            "Led development of web applications using React and Node.js": "Lideró el desarrollo de aplicaciones web usando React y Node.js",
            "New York": "Nueva York",
            "E-commerce Platform": "Plataforma de Comercio Electrónico",
            "Built scalable e-commerce platform handling 10k+ users": "Construyó plataforma de comercio electrónico escalable manejando más de 10k usuarios",
            "Improved performance by 40%": "Mejoró el rendimiento en un 40%",
            "Reduced load time by 60%": "Redujo el tiempo de carga en un 60%",
            "Bachelor of Science": "Licenciatura en Ciencias",
            "Computer Science": "Ciencias de la Computación",
        }

        service = ProfileTranslationService()

        # Mock the LLM client
        with patch.object(service, 'llm_client') as mock_llm_client:
            mock_llm_client.is_configured.return_value = True

            # Mock the generate_text method to return expected translations
            def mock_generate_text(prompt, system_prompt=None):
                # Extract the text to translate from the prompt
                for original, translated in expected_translations.items():
                    if original in prompt:
                        return translated
                # For any other text, return a generic translation
                return "Texto traducido"

            mock_llm_client.generate_text = AsyncMock(side_effect=mock_generate_text)

            # Execute the translation
            result = await service.translate_profile(profile_data, "es", "en")

            # Verify the result structure
            assert result["language"] == "es"
            assert result["personal_info"]["name"] == "John Doe"  # Name unchanged
            assert result["personal_info"]["email"] == "john@example.com"  # Email unchanged
            assert result["personal_info"]["title"] == "Ingeniero de Software"
            assert result["personal_info"]["summary"] == "Desarrollador experimentado con 5 años en desarrollo web"

            # Check experience
            exp = result["experience"][0]
            assert exp["title"] == "Desarrollador Senior"
            assert exp["company"] == "Tech Corp"  # Company unchanged
            assert exp["description"] == "Lideró el desarrollo de aplicaciones web usando React y Node.js"
            assert exp["location"] == "Nueva York"

            # Check project
            proj = exp["projects"][0]
            assert proj["name"] == "Plataforma de Comercio Electrónico"
            assert proj["description"] == "Construyó plataforma de comercio electrónico escalable manejando más de 10k usuarios"
            assert proj["highlights"] == ["Mejoró el rendimiento en un 40%", "Redujo el tiempo de carga en un 60%"]
            assert proj["technologies"] == ["React", "Node.js"]  # Technologies unchanged

            # Check education
            edu = result["education"][0]
            assert edu["degree"] == "Licenciatura en Ciencias"
            assert edu["institution"] == "State University"  # Institution unchanged
            assert edu["field"] == "Ciencias de la Computación"
            assert edu["year"] == "2020"  # Year unchanged

            # Skills unchanged
            assert result["skills"] == profile_data["skills"]

    async def test_translation_flow_with_api_validation(self):
        """Test that the translation API properly validates requests."""
        # Valid request
        valid_request = TranslateProfileRequest(
            profile_data={
                "personal_info": {"name": "John", "title": "Engineer"},
                "experience": [],
                "education": [],
                "skills": [],
                "language": "en",
            },
            target_language="es"
        )
        assert valid_request.target_language == "es"

        # Test with invalid target language - should raise ValidationError
        with pytest.raises(ValidationError) as exc_info:
            TranslateProfileRequest(
                profile_data={
                    "personal_info": {"name": "John", "title": "Engineer"},
                    "experience": [],
                    "education": [],
                    "skills": [],
                    "language": "en",
                },
                target_language="invalid"
            )
        assert "Unsupported target language" in str(exc_info.value)

    async def test_translation_preserves_data_integrity(self):
        """Test that translation preserves all data relationships and structure."""
        # Complex profile with multiple experiences and projects
        complex_profile = {
            "personal_info": {"name": "Jane Smith", "title": "Tech Lead"},
            "experience": [
                {
                    "title": "Senior Engineer",
                    "company": "Big Tech",
                    "description": "Led multiple teams",
                    "location": "San Francisco",
                    "projects": [
                        {"name": "Project A", "description": "Did A", "highlights": ["A1", "A2"]},
                        {"name": "Project B", "description": "Did B", "highlights": ["B1"]},
                    ],
                },
                {
                    "title": "Engineer",
                    "company": "Startup",
                    "description": "Built MVP",
                    "location": "Austin",
                    "projects": [],
                }
            ],
            "education": [
                {"degree": "MS", "institution": "MIT", "field": "CS"},
                {"degree": "BS", "institution": "Stanford", "field": "Engineering"},
            ],
            "skills": [
                {"name": "Python", "level": "Expert"},
                {"name": "Leadership", "level": "Advanced"},
            ],
            "language": "en",
        }

        service = ProfileTranslationService()

        def mock_translate(text, target, source, text_type):
            if text_type == "project highlight":
                return text  # Preserve highlights
            return "translated"

        with patch.object(service, '_translate_text', side_effect=mock_translate) as mock_translate:
            result = await service.translate_profile(complex_profile, "es", "en")

            # Verify structure is preserved
            assert len(result["experience"]) == 2
            assert len(result["experience"][0]["projects"]) == 2
            assert len(result["experience"][1]["projects"]) == 0
            assert len(result["education"]) == 2
            assert len(result["skills"]) == 2

            # Verify all translatable fields were processed
            assert mock_translate.call_count > 10  # Should translate multiple fields

            # Verify non-translatable fields preserved
            assert result["personal_info"]["name"] == "Jane Smith"
            assert result["experience"][0]["company"] == "Big Tech"
            assert result["experience"][0]["projects"][0]["highlights"] == ["A1", "A2"]
            assert result["education"][0]["institution"] == "MIT"
            assert result["skills"][0]["level"] == "Expert"

    async def test_translation_error_recovery(self):
        """Test that translation gracefully handles partial failures."""
        profile_data = {
            "personal_info": {"name": "John", "title": "Engineer", "summary": "Good developer"},
            "experience": [{"title": "Dev", "company": "Corp", "description": "Built things"}],
            "education": [],
            "skills": [],
            "language": "en",
        }

        service = ProfileTranslationService()

        # Mock translation to fail for some texts (return original text)
        def mock_translate(text, target, source, text_type):
            if text_type == "professional summary":
                return text  # Return original text for "failed" translation
            return f"Translated: {text}"

        with patch.object(service, '_translate_text', side_effect=mock_translate):
            result = await service.translate_profile(profile_data, "es", "en")

            # Successful translations should work
            assert result["personal_info"]["title"] == "Translated: Engineer"
            assert result["experience"][0]["title"] == "Translated: Dev"
            assert result["experience"][0]["description"] == "Translated: Built things"

            # Failed translation should keep original text
            assert result["personal_info"]["summary"] == "Good developer"

            # Non-translatable fields preserved
            assert result["personal_info"]["name"] == "John"
            assert result["experience"][0]["company"] == "Corp"
