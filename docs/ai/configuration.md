# AI Configuration (.env)

AI settings live in the project root `.env` (not committed). Use `.env.example` as a template.

## Environment Variables

- `AI_ENABLED`: `true|false` (feature flag; default `false`)
- `AI_BASE_URL`: OpenAI-compatible base URL (typically ends with `/v1`)
- `AI_API_KEY`: provider API key
- `AI_MODEL`: model name/ID (provider-specific)
- `AI_TEMPERATURE`: `0.0`–`1.0` (default `0.2`)
- `AI_MAX_OUTPUT_TOKENS`: max tokens for the JSON draft
- `AI_REQUEST_TIMEOUT_S`: request timeout in seconds

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
