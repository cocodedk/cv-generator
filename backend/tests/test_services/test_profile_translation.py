"""Tests for profile translation service."""
import pytest
from unittest.mock import AsyncMock, patch
from backend.services.profile_translation import ProfileTranslationService


@pytest.mark.asyncio
class TestProfileTranslationService:
    """Test ProfileTranslationService."""

    def setup_method(self):
        """Set up test instance."""
        self.service = ProfileTranslationService()

    async def test_translate_profile_success(self):
        """Test successful profile translation."""
        profile_data = {
            "personal_info": {
                "name": "John Doe",
                "title": "Software Engineer",
                "summary": "Experienced software engineer with 5 years of experience",
                "email": "john@example.com",
            },
            "experience": [
                {
                    "title": "Senior Developer",
                    "company": "Tech Corp",
                    "description": "Developed web applications",
                    "location": "New York",
                    "projects": [
                        {
                            "name": "E-commerce Platform",
                            "description": "Built a scalable e-commerce platform",
                            "highlights": ["Increased performance by 40%", "Handled 10k users"],
                        }
                    ],
                }
            ],
            "education": [
                {
                    "degree": "Bachelor of Science",
                    "institution": "State University",
                    "field": "Computer Science",
                }
            ],
            "skills": [{"name": "Python", "category": "Programming"}],
            "language": "en",
        }

        with patch.object(self.service, '_translate_text', side_effect=lambda text, target, source, text_type: {
                "Software Engineer": "Ingeniero de Software",
                "Experienced software engineer with 5 years of experience": "Ingeniero de software experimentado con 5 años de experiencia",
                "Senior Developer": "Desarrollador Senior",
                "Developed web applications": "Desarrolló aplicaciones web",
                "New York": "Nueva York",
                "E-commerce Platform": "Plataforma de Comercio Electrónico",
                "Built a scalable e-commerce platform": "Construyó una plataforma de comercio electrónico escalable",
                "Increased performance by 40%": "Aumentó el rendimiento en un 40%",
                "Handled 10k users": "Manejó 10k usuarios",
                "Bachelor of Science": "Licenciatura en Ciencias",
                "Computer Science": "Ciencias de la Computación",
        }.get(text, text)):

            result = await self.service.translate_profile(profile_data, "es", "en")

            assert result["language"] == "es"
            assert result["personal_info"]["title"] == "Ingeniero de Software"
            assert result["personal_info"]["summary"] == "Ingeniero de software experimentado con 5 años de experiencia"
            assert result["experience"][0]["title"] == "Desarrollador Senior"
            assert result["experience"][0]["location"] == "Nueva York"
            assert result["education"][0]["degree"] == "Licenciatura en Ciencias"
            assert result["skills"] == profile_data["skills"]  # Skills unchanged

    async def test_translate_profile_same_language(self):
        """Test translation when source and target languages are the same."""
        profile_data = {
            "personal_info": {"name": "John Doe", "title": "Engineer"},
            "experience": [],
            "education": [],
            "skills": [],
            "language": "en",
        }

        result = await self.service.translate_profile(profile_data, "en", "en")
        assert result == profile_data

    async def test_translate_profile_ai_not_configured(self):
        """Test translation when AI service is not configured."""
        with patch.object(self.service.llm_client, 'is_configured', return_value=False):
            with pytest.raises(ValueError, match="AI service is not configured"):
                await self.service.translate_profile({}, "es", "en")

    async def test_translate_text_success(self):
        """Test successful text translation."""
        with patch.object(self.service.llm_client, 'generate_text', return_value="Hola mundo") as mock_generate:
            result = await self.service._translate_text("Hello world", "es", "en", "greeting")
            assert result == "Hola mundo"
            mock_generate.assert_called_once()

    async def test_translate_text_em_dash_removal(self):
        """Test that em dashes are converted to hyphens."""
        with patch.object(self.service.llm_client, 'generate_text', return_value="Hola—mundo") as mock_generate:
            result = await self.service._translate_text("Hello world", "es", "en", "greeting")
            assert result == "Hola-mundo"
            mock_generate.assert_called_once()

    async def test_translate_text_empty(self):
        """Test translation of empty text."""
        result = await self.service._translate_text("", "es", "en", "summary")
        assert result == ""

    async def test_translate_text_none(self):
        """Test translation of None text."""
        result = await self.service._translate_text(None, "es", "en", "summary")
        assert result is None

    async def test_translate_text_llm_error(self):
        """Test handling of LLM errors during translation."""
        with patch.object(self.service.llm_client, 'generate_text', side_effect=Exception("API error")):
            # Should return original text on error
            result = await self.service._translate_text("Hello world", "es", "en", "greeting")
            assert result == "Hello world"

    def test_create_translation_prompt(self):
        """Test translation prompt creation."""
        prompt = self.service._create_translation_prompt(
            "Hello world", "es", "en", "greeting"
        )

        assert "Spanish" in prompt
        assert "English" in prompt
        assert "Hello world" in prompt
        assert "greeting" in prompt
        assert "em dashes" in prompt
        assert "regular hyphens" in prompt

    async def test_translate_profile_preserves_non_translatable_fields(self):
        """Test that non-translatable fields are preserved exactly."""
        profile_data = {
            "personal_info": {
                "name": "John Doe",
                "email": "john@example.com",
                "phone": "+1234567890",
                "address": {
                    "street": "123 Main St",
                    "city": "New York",
                    "country": "USA"
                },
                "linkedin": "https://linkedin.com/in/johndoe",
                "github": "https://github.com/johndoe",
                "website": "https://johndoe.com",
                "title": "Engineer",
            },
            "experience": [
                {
                    "title": "Developer",
                    "company": "Tech Corp",
                    "start_date": "2020-01",
                    "end_date": "2023-12",
                    "description": "Built apps",
                    "location": "NYC",
                    "projects": [
                        {
                            "name": "Project A",
                            "description": "Description",
                            "url": "https://example.com",
                            "technologies": ["React", "Node.js"],
                            "highlights": ["Achievement 1"],
                        }
                    ],
                }
            ],
            "education": [
                {
                    "degree": "BS",
                    "institution": "University",
                    "year": "2020",
                    "gpa": "3.8",
                    "field": "CS",
                }
            ],
            "skills": [
                {"name": "JavaScript", "category": "Programming", "level": "Expert"},
                {"name": "Python", "category": "Programming"},
            ],
            "language": "en",
        }

        with patch.object(self.service, '_translate_text') as mock_translate:
            mock_translate.return_value = "translated"

            result = await self.service.translate_profile(profile_data, "es", "en")

            # Check that non-translatable fields are unchanged
            assert result["personal_info"]["name"] == "John Doe"
            assert result["personal_info"]["email"] == "john@example.com"
            assert result["personal_info"]["phone"] == "+1234567890"
            assert result["personal_info"]["address"] == profile_data["personal_info"]["address"]
            assert result["personal_info"]["linkedin"] == "https://linkedin.com/in/johndoe"
            assert result["personal_info"]["github"] == "https://github.com/johndoe"
            assert result["personal_info"]["website"] == "https://johndoe.com"

            # Check experience non-translatable fields
            assert result["experience"][0]["start_date"] == "2020-01"
            assert result["experience"][0]["end_date"] == "2023-12"
            assert result["experience"][0]["projects"][0]["url"] == "https://example.com"
            assert result["experience"][0]["projects"][0]["technologies"] == ["React", "Node.js"]

            # Check education non-translatable fields
            assert result["education"][0]["year"] == "2020"
            assert result["education"][0]["gpa"] == "3.8"

            # Skills should be completely unchanged
            assert result["skills"] == profile_data["skills"]

    async def test_translate_profile_complex_nested_structure(self):
        """Test translation with complex nested project structures."""
        profile_data = {
            "personal_info": {"name": "John", "title": "Engineer"},
            "experience": [
                {
                    "title": "Senior Dev",
                    "company": "Company",
                    "description": "Did work",
                    "projects": [
                        {
                            "name": "Project 1",
                            "description": "Built something",
                            "highlights": ["Feature A", "Feature B", "Feature C"],
                        },
                        {
                            "name": "Project 2",
                            "description": "Created thing",
                            "highlights": ["Item 1"],
                        }
                    ],
                },
                {
                    "title": "Junior Dev",
                    "company": "Startup",
                    "description": "Learned stuff",
                    "projects": [],
                }
            ],
            "education": [],
            "skills": [],
            "language": "en",
        }

        translated_texts = {
            "Engineer": "Ingeniero",
            "Senior Dev": "Desarrollador Senior",
            "Did work": "Hizo trabajo",
            "Project 1": "Proyecto 1",
            "Built something": "Construyó algo",
            "Feature A": "Característica A",
            "Feature B": "Característica B",
            "Feature C": "Característica C",
            "Project 2": "Proyecto 2",
            "Created thing": "Creó cosa",
            "Item 1": "Elemento 1",
            "Junior Dev": "Desarrollador Junior",
            "Learned stuff": "Aprendió cosas",
        }

        with patch.object(self.service, '_translate_text') as mock_translate:
            mock_translate.side_effect = lambda text, target, source, text_type: translated_texts.get(text, text)

            result = await self.service.translate_profile(profile_data, "es", "en")

            # Check personal info
            assert result["personal_info"]["title"] == "Ingeniero"

            # Check first experience
            exp1 = result["experience"][0]
            assert exp1["title"] == "Desarrollador Senior"
            assert exp1["description"] == "Hizo trabajo"

            # Check projects in first experience
            proj1 = exp1["projects"][0]
            assert proj1["name"] == "Proyecto 1"
            assert proj1["description"] == "Construyó algo"
            assert proj1["highlights"] == ["Característica A", "Característica B", "Característica C"]

            proj2 = exp1["projects"][1]
            assert proj2["name"] == "Proyecto 2"
            assert proj2["description"] == "Creó cosa"
            assert proj2["highlights"] == ["Elemento 1"]

            # Check second experience
            exp2 = result["experience"][1]
            assert exp2["title"] == "Desarrollador Junior"
            assert exp2["description"] == "Aprendió cosas"
            assert exp2["projects"] == []  # Empty projects should remain empty

    async def test_translate_profile_partial_data(self):
        """Test translation with incomplete profile data."""
        profile_data = {
            "personal_info": {
                "name": "John",
                # Missing title, email, etc.
            },
            "experience": [],  # Empty experience
            "education": [
                {
                    "degree": "BS",
                    "institution": "University",
                    # Missing other fields
                }
            ],
            "skills": [],
            "language": "en",
        }

        with patch.object(self.service, '_translate_text') as mock_translate:
            mock_translate.return_value = "translated"

            result = await self.service.translate_profile(profile_data, "es", "en")

            # Should not crash and preserve structure
            assert result["personal_info"]["name"] == "John"
            assert result["experience"] == []
            assert len(result["education"]) == 1
            assert result["education"][0]["degree"] == "BS"
            assert result["education"][0]["institution"] == "University"
            assert result["skills"] == []
            assert result["language"] == "es"

    async def test_translate_profile_error_handling(self):
        """Test error handling during profile translation."""
        profile_data = {
            "personal_info": {"name": "John", "title": "Engineer"},
            "experience": [{"title": "Dev", "company": "Company", "description": "Work"}],
            "education": [],
            "skills": [],
            "language": "en",
        }

        with patch.object(self.service, 'llm_client') as mock_llm_client:
            mock_llm_client.is_configured.return_value = True

            # Make translation fail for "Work" text
            def mock_generate_text(prompt, system_prompt=None):
                if "Work" in prompt:
                    raise Exception("Translation failed")
                # Return translations for other texts
                translations = {
                    "Engineer": "Ingeniero",
                    "Dev": "Desarrollador",
                }
                for text, translated in translations.items():
                    if text in prompt:
                        return translated
                return "translated"

            mock_llm_client.generate_text = AsyncMock(side_effect=mock_generate_text)

            result = await self.service.translate_profile(profile_data, "es", "en")

            # Should still have successful translations
            assert result["personal_info"]["title"] == "Ingeniero"
            assert result["experience"][0]["title"] == "Desarrollador"
            assert result["experience"][0]["company"] == "Company"  # Company unchanged
            # Failed translation should keep original text
            assert result["experience"][0]["description"] == "Work"
