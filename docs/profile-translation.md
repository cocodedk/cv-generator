# Profile Translation Feature

## Overview

The Profile Translation feature allows users to translate their CV profiles to different languages using AI. This feature helps users create CVs in multiple languages for international job applications.

## How It Works

1. **Language Field**: Every profile has a designated language field (ISO 639-1 code) that defaults to English ("en")
2. **AI Translation**: Uses OpenAI-compatible LLM APIs to translate text content
3. **Selective Translation**: Only translates appropriate fields while preserving personal information like names, addresses, and contact details
4. **Tone Preservation**: Maintains the same professional tone and formality as the original text

## Translated Fields

### ✅ Translated Fields
- **Personal Info**: Title, Summary
- **Experience**: Job titles, descriptions, locations
- **Projects**: Names, descriptions, highlights
- **Education**: Degrees, fields of study

### ❌ Non-Translated Fields
- **Personal Info**: Name, email, phone, address, LinkedIn, GitHub, website
- **Experience**: Dates, technologies, company names
- **Education**: Years, GPA, institution names
- **Skills**: All skill-related fields (names, categories, levels)

## API Usage

### Translate Profile Endpoint

```http
POST /api/profile/translate
Content-Type: application/json

{
  "profile_data": {
    "personal_info": {...},
    "experience": [...],
    "education": [...],
    "skills": [...],
    "language": "en"
  },
  "target_language": "es"
}
```

**Response:**
```json
{
  "status": "success",
  "translated_profile": {
    "personal_info": {...},
    "experience": [...],
    "education": [...],
    "skills": [...],
    "language": "es"
  },
  "message": "Profile translated from en to es"
}
```

### Supported Languages

The feature supports the following target languages:

- Spanish (`es`)
- French (`fr`)
- German (`de`)
- Italian (`it`)
- Portuguese (`pt`)
- Dutch (`nl`)
- Russian (`ru`)
- Chinese (`zh`)
- Japanese (`ja`)
- Korean (`ko`)
- Arabic (`ar`)
- Danish (`da`)
- Swedish (`sv`)
- Norwegian (`no`)

## Frontend Usage

### Profile Manager Interface

1. Navigate to the Profile Manager (`#profile` or `#profile-edit/{timestamp}`)
2. Fill in your profile information in the original language
3. In the "Translate Profile" section:
   - Select target language from dropdown
   - Click "Translate" button
4. The profile will be translated and the form will update with translated content
5. Save the profile to persist the translated version

### Important Notes

- Translation requires AI service configuration (OpenAI API key)
- Translation preserves HTML formatting in descriptions
- Em dashes (—) are automatically converted to regular hyphens (-)
- If translation fails, original text is preserved
- Skills are never translated as they are typically language-agnostic

## Configuration

### Environment Variables

The translation feature uses the existing LLM configuration:

```env
AI_ENABLED=true
AI_BASE_URL=https://api.openai.com/v1
AI_API_KEY=your-api-key-here
AI_MODEL=gpt-4  # or other compatible model
AI_TEMPERATURE=0.7
AI_REQUEST_TIMEOUT_S=30
```

## Technical Implementation

### Backend Components

- **`ProfileTranslationService`**: Core translation logic in `backend/services/profile_translation.py`
- **Translation endpoint**: `POST /api/profile/translate` in profile router
- **Database changes**: Added `language` field to Profile nodes

### Frontend Components

- **Language selector**: Dropdown in ProfileManager component
- **Translation button**: Triggers AI translation with loading states
- **API integration**: `translateProfile` function in profile service

### Translation Rules

1. **Field Selection**: Only text fields that benefit from translation are processed
2. **Context Preservation**: Each text field includes context about what type of content it is
3. **Error Handling**: Falls back to original text if translation fails
4. **Formatting**: Removes em dashes, preserves professional tone

## Testing

The feature includes comprehensive tests:

- **API endpoint tests**: Request validation, success/error cases
- **Service tests**: Translation logic, field selection, error handling
- **Integration tests**: Full translation workflow

Run tests with:
```bash
# Backend tests
docker-compose exec app pytest tests/test_services/test_profile_translation.py -v
docker-compose exec app pytest tests/test_api/test_profile_endpoints.py::TestTranslateProfile -v

# Frontend tests (if applicable)
npm run test:frontend
```

## Limitations

1. **AI Dependency**: Requires configured LLM service
2. **Cost**: Each translation consumes API credits
3. **Quality**: Translation quality depends on the underlying AI model
4. **Cultural Adaptation**: May not account for country-specific CV conventions
5. **Technical Terms**: May not perfectly translate highly technical or industry-specific terminology

## Future Enhancements

- **Batch Translation**: Translate multiple profiles at once
- **Language Detection**: Auto-detect source language
- **Custom Prompts**: Allow users to customize translation style
- **Translation Memory**: Cache and reuse translations
- **Quality Assurance**: Add translation review and editing features
