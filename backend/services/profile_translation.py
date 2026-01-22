"""Profile translation service using AI."""
import asyncio
import logging
from typing import Dict, Any, List, Optional
from backend.services.ai.llm_client import get_llm_client

logger = logging.getLogger(__name__)

# Fields that should NOT be translated
NON_TRANSLATABLE_FIELDS = {
    "name", "email", "phone", "address", "linkedin", "github", "website",
    "start_date", "end_date", "year", "gpa", "technologies", "url", "company"
}

# Skills should not be translated
NON_TRANSLATABLE_SECTIONS = {"skills"}


class ProfileTranslationService:
    """Service for translating profile content using AI."""

    def __init__(self):
        self.llm_client = get_llm_client()

    async def translate_profile(
        self, profile_data: Dict[str, Any], target_language: str, source_language: str = "en"
    ) -> Dict[str, Any]:
        """
        Translate a profile to the target language.

        Args:
            profile_data: The profile data to translate
            target_language: ISO 639-1 language code for target language
            source_language: ISO 639-1 language code for source language (default: en)

        Returns:
            Translated profile data with same structure
        """
        if not self.llm_client.is_configured():
            raise ValueError("AI service is not configured")

        if target_language == source_language:
            logger.info(f"Source and target languages are the same ({target_language}), returning original profile")
            return profile_data

        translated_profile = profile_data.copy()

        # Translate personal info
        translated_profile["personal_info"] = await self._translate_personal_info(
            profile_data.get("personal_info", {}), target_language, source_language
        )

        # Translate experience
        translated_profile["experience"] = await self._translate_experience_list(
            profile_data.get("experience", []), target_language, source_language
        )

        # Translate education
        translated_profile["education"] = await self._translate_education_list(
            profile_data.get("education", []), target_language, source_language
        )

        # Skills are not translated
        translated_profile["skills"] = profile_data.get("skills", [])

        # Update language field
        translated_profile["language"] = target_language

        return translated_profile

    async def _translate_personal_info(
        self, personal_info: Dict[str, Any], target_language: str, source_language: str
    ) -> Dict[str, Any]:
        """Translate personal info fields."""
        translated = personal_info.copy()

        # Only translate title and summary
        if personal_info.get("title"):
            translated["title"] = await self._translate_text(
                personal_info["title"], target_language, source_language, "professional title"
            )

        if personal_info.get("summary"):
            translated["summary"] = await self._translate_text(
                personal_info["summary"], target_language, source_language, "professional summary"
            )

        return translated

    async def _translate_experience_list(
        self, experience_list: List[Dict[str, Any]], target_language: str, source_language: str
    ) -> List[Dict[str, Any]]:
        """Translate experience entries."""
        if not experience_list:
            return []
        tasks = [
            self._translate_experience(experience, target_language, source_language)
            for experience in experience_list
        ]
        return await asyncio.gather(*tasks)

    async def _translate_experience(
        self, experience: Dict[str, Any], target_language: str, source_language: str
    ) -> Dict[str, Any]:
        """Translate a single experience entry."""
        translated = experience.copy()

        # Translate translatable fields
        if experience.get("title"):
            translated["title"] = await self._translate_text(
                experience["title"], target_language, source_language, "job title"
            )

        # Company names are proper nouns and should not be translated

        if experience.get("description"):
            translated["description"] = await self._translate_text(
                experience["description"], target_language, source_language, "job description"
            )

        if experience.get("location"):
            translated["location"] = await self._translate_text(
                experience["location"], target_language, source_language, "location"
            )

        # Translate projects
        if experience.get("projects"):
            translated["projects"] = await self._translate_projects(
                experience["projects"], target_language, source_language
            )

        return translated

    async def _translate_projects(
        self, projects: List[Dict[str, Any]], target_language: str, source_language: str
    ) -> List[Dict[str, Any]]:
        """Translate project entries."""
        translated_list = []
        for project in projects:
            translated_proj = project.copy()

            if project.get("name"):
                translated_proj["name"] = await self._translate_text(
                    project["name"], target_language, source_language, "project name"
                )

            if project.get("description"):
                translated_proj["description"] = await self._translate_text(
                    project["description"], target_language, source_language, "project description"
                )

            if project.get("highlights"):
                translated_proj["highlights"] = [
                    await self._translate_text(highlight, target_language, source_language, "project highlight")
                    for highlight in project["highlights"]
                ]

            translated_list.append(translated_proj)
        return translated_list

    async def _translate_education(
        self, education: Dict[str, Any], target_language: str, source_language: str
    ) -> Dict[str, Any]:
        """Translate a single education entry."""
        translated_edu = education.copy()

        if education.get("degree"):
            degree = education["degree"]
            # Don't translate degree abbreviations (short, all caps, no spaces)
            if len(degree.strip()) <= 4 and degree.strip().isupper() and ' ' not in degree:
                translated_edu["degree"] = degree
            else:
                translated_edu["degree"] = await self._translate_text(
                    degree, target_language, source_language, "degree"
                )

        # Institution names are proper nouns and must be preserved
        if education.get("institution"):
            translated_edu["institution"] = education["institution"]

        if education.get("field"):
            translated_edu["field"] = await self._translate_text(
                education["field"], target_language, source_language, "field of study"
            )

        return translated_edu

    async def _translate_education_list(
        self, education_list: List[Dict[str, Any]], target_language: str, source_language: str
    ) -> List[Dict[str, Any]]:
        """Translate education entries."""
        if not education_list:
            return []
        tasks = [
            self._translate_education(education, target_language, source_language)
            for education in education_list
        ]
        return await asyncio.gather(*tasks)

    async def _translate_text(
        self, text: str, target_language: str, source_language: str, text_type: str
    ) -> str:
        """
        Translate a single text using AI.

        Args:
            text: The text to translate
            target_language: Target language code
            source_language: Source language code
            text_type: Type of text (e.g., "job title", "summary") for context

        Returns:
            Translated text
        """
        if not text or not text.strip():
            return text

        # Create translation prompt
        prompt = self._create_translation_prompt(text, target_language, source_language, text_type)

        try:
            translated_text = await self.llm_client.generate_text(prompt)
            # Clean up the response - remove any extra formatting
            translated_text = translated_text.strip()
            # Remove em dashes as requested
            translated_text = translated_text.replace("—", "-").replace("–", "-")
            return translated_text
        except Exception as e:
            logger.error(f"Failed to translate text: {e}")
            # Return original text if translation fails
            return text

    def _create_translation_prompt(
        self, text: str, target_language: str, source_language: str, text_type: str
    ) -> str:
        """Create a translation prompt for the LLM."""
        language_names = {
            "en": "English",
            "es": "Spanish",
            "fr": "French",
            "de": "German",
            "it": "Italian",
            "pt": "Portuguese",
            "nl": "Dutch",
            "ru": "Russian",
            "zh": "Chinese",
            "ja": "Japanese",
            "ko": "Korean",
            "ar": "Arabic",
            "da": "Danish",
            "sv": "Swedish",
            "no": "Norwegian",
        }

        source_name = language_names.get(source_language, source_language.upper())
        target_name = language_names.get(target_language, target_language.upper())

        return f"""Translate the following {text_type} from {source_name} to {target_name}.

IMPORTANT INSTRUCTIONS:
- Maintain the same professional tone and style as the original
- Keep the same level of formality and vocabulary
- Do not add or remove information
- Do not use em dashes (—) or en dashes (–), use regular hyphens (-) instead
- Return ONLY the translated text, no explanations or additional content

Original text:
{text}

Translated text:"""


# Singleton instance
_translation_service: Optional[ProfileTranslationService] = None


def get_translation_service() -> ProfileTranslationService:
    """Get or create translation service instance."""
    global _translation_service
    if _translation_service is None:
        _translation_service = ProfileTranslationService()
    return _translation_service
