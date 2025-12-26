# AI Configuration

AI settings are configured via environment variables. For Docker setups, these must be set in both `.env` and `docker-compose.yml`.

## Setup Steps

1. **Add variables to `.env` file** (in project root):
   ```env
   AI_ENABLED=true
   AI_BASE_URL=https://api.openai.com/v1
   AI_API_KEY=your-api-key-here
   AI_MODEL=gpt-3.5-turbo
   AI_TEMPERATURE=0.7
   AI_REQUEST_TIMEOUT_S=30
   ```

2. **Restart Docker containers** to pick up new environment variables:
   ```bash
   docker-compose down
   docker-compose up -d
   ```

   **Note**: The `docker-compose.yml` file has been updated to pass these variables to the container. If you're using an older version, you may need to add them manually to the `environment` section of the `app` service.

## Environment Variables

- `AI_ENABLED`: `true|false` (feature flag; default `false`)
- `AI_BASE_URL`: OpenAI-compatible base URL (typically ends with `/v1`)
- `AI_API_KEY`: provider API key
- `AI_MODEL`: model name/ID (provider-specific, default `gpt-3.5-turbo`)
- `AI_TEMPERATURE`: `0.0`–`1.0` (default `0.7`)
- `AI_REQUEST_TIMEOUT_S`: request timeout in seconds (default `30`)

## OpenAI-Compatible Examples

- OpenAI: `AI_BASE_URL=https://api.openai.com/v1`
- OpenRouter: `AI_BASE_URL=https://openrouter.ai/api/v1`
- Groq: `AI_BASE_URL=https://api.groq.com/openai/v1`
- Together: `AI_BASE_URL=https://api.together.xyz/v1`
- Local vLLM: `AI_BASE_URL=http://localhost:8001/v1`

If your provider supports only a different API shape, add a small adapter in the backend service layer rather than changing the rest of the app.

## Privacy Notes

- Prefer not sending email/phone/address to third-party providers; redact in the backend prompt builder if needed.
- Never log the job description or full profile payload at INFO level.
