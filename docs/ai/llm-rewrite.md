# LLM-Based Text Rewrite

The AI rewrite feature now uses an LLM (Large Language Model) to rewrite text based on user prompts.

## How It Works

1. **User clicks "AI rewrite"** button in any rich text field
2. **Prompt modal appears** asking for rewrite instructions
3. **User enters prompt** (e.g., "Make it more professional", "Make it shorter", "Improve clarity")
4. **Text is sent to LLM** via `/api/ai/rewrite` endpoint
5. **Rewritten text** is returned and placed back in the textarea

## Configuration

Set these environment variables in your `.env` file:

```bash
AI_ENABLED=true
AI_BASE_URL=https://api.openai.com/v1
AI_API_KEY=your-api-key-here
AI_MODEL=gpt-3.5-turbo
AI_TEMPERATURE=0.7
AI_REQUEST_TIMEOUT_S=30
```

### Supported Providers

Any OpenAI-compatible API:
- OpenAI: `AI_BASE_URL=https://api.openai.com/v1`
- OpenRouter: `AI_BASE_URL=https://openrouter.ai/api/v1`
- Groq: `AI_BASE_URL=https://api.groq.com/openai/v1`
- Together: `AI_BASE_URL=https://api.together.xyz/v1`
- Local vLLM: `AI_BASE_URL=http://localhost:8001/v1`

## API Endpoint

### POST `/api/ai/rewrite`

**Request:**
```json
{
  "text": "Text to rewrite",
  "prompt": "User's instruction for rewriting"
}
```

**Response:**
```json
{
  "rewritten_text": "Rewritten text from LLM"
}
```

**Rate Limit:** 20 requests per minute

## Usage Examples

- **Professional tone**: "Make this more professional and formal"
- **Conciseness**: "Make this shorter and more concise"
- **Clarity**: "Improve clarity and readability"
- **Style**: "Rewrite in a more engaging style"
- **Format**: "Convert to bullet points"

## Fallback Behavior

- If LLM is not configured (`AI_ENABLED=false`), the rewrite button will show an error
- The "AI bullets" button still uses heuristic-based transformations (no LLM required)

## Privacy Notes

- Text and prompts are sent to the configured LLM provider
- Ensure your provider's privacy policy meets your requirements
- Consider using local LLM providers for sensitive data
