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

## Model Recommendations

For best results with CV tailoring features (especially the `llm_tailor` style):

- **gpt-4o**: Best instruction-following and factual accuracy. Recommended for production use.
- **gpt-4-turbo**: Good balance of capability and cost. Reliable for most use cases.
- **gpt-3.5-turbo**: Fastest and cheapest, but may occasionally add unsolicited details. Suitable for testing.

To upgrade, change `AI_MODEL` in your `.env` file:
```env
AI_MODEL=gpt-4o
```

## CV Generation Styles

The CV generation endpoint supports three styles:

1. **`select_and_reorder`** (default): Uses heuristics to select and reorder experiences/skills based on keyword matching. No LLM required.

2. **`rewrite_bullets`**: Applies simple text cleanup (removes weak prefixes like "responsible for"). No LLM required.

3. **`llm_tailor`**: Uses LLM to intelligently reword bullets, descriptions, and reorder skills to match the job description. **Requires LLM configuration** (`AI_ENABLED=true`). This style:
   - Rewords highlights and descriptions to emphasize JD-relevant skills
   - Reorders skills to prioritize JD-relevant ones
   - Strictly preserves all facts from your master profile (no fabrication)
   - Falls back gracefully if LLM is not configured

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
