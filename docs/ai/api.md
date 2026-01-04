# AI API

This feature adds a small, isolated API surface that returns validated CV drafts.

## Endpoint: Generate CV Draft

`POST /api/ai/generate-cv`

The backend loads the saved master profile and generates a tailored `CVData` draft.

### Request (JSON)

- `job_description`: string (required)
- `target_role`: string (optional)
- `seniority`: string (optional)
- `style`: `"select_and_reorder" | "rewrite_bullets" | "llm_tailor"` (optional; default `select_and_reorder`)
  - `select_and_reorder`: Heuristic-based selection and reordering (no LLM required)
  - `rewrite_bullets`: Simple text cleanup (no LLM required)
  - `llm_tailor`: LLM-powered tailoring that rewrites content to match JD (requires LLM configuration)
- `max_experiences`: number (optional)

### Response (JSON)

- `draft_cv`: `CVData` (validated against existing backend model)
- `warnings`: string[]
- `questions`: string[] (missing facts/metrics the user should confirm)
- `summary`: string[] (high-level changes, e.g. “Moved X above Y”)
- `evidence_map` (optional): `{requirement: string, evidence: {path: string, quote: string}[]}[]`

## Selection/Scoring (Implementation Notes)

The generator should be able to explain “why this item is included”:

- Match signals: skill/tech overlap, responsibility overlap, seniority signals, recency.
- Evidence sources: experience/projects/highlights + skills/education from the profile.
- Constraints: page length caps and per-section limits (top N experiences, top M projects, top K bullets).

## Scoring Rubric (Concrete Defaults)

Define a JD “target spec” (keywords + responsibilities), then score each profile item.

**Target spec extraction**
- `required_keywords`: from “must/required” phrases (weight 2.0)
- `preferred_keywords`: from “nice to have/plus” phrases (weight 1.0)
- `responsibilities`: short verb phrases (weight 1.5)

**Item scoring (experience/project/highlight)**
- `keyword_match` (0–1): weighted overlap of item text + technologies vs target keywords
- `responsibility_match` (0–1): overlap of highlight verbs vs target responsibilities
- `seniority_match` (0–1): signals like “led/owned/architected/mentored/on-call”
- `recency` (0.7–1.0): latest role 1.0, older roles decay toward 0.7
- `quality_penalty` (0–0.3): vague claims, very long bullets, duplicate content

**Final score**
- `score = 0.45*keyword_match + 0.25*responsibility_match + 0.15*seniority_match + 0.15*recency - quality_penalty`

**Selection limits (defaults; enforce deterministically)**
- `max_experiences = 4`, `max_projects_per_experience = 2`, `max_highlights_per_project = 3`
- Skills: include only skills that appear in selected items; cap at 12–18.

**Trimming rules**
- Drop lowest-scoring highlights first; never invent new ones.
- If a highlight implies an outcome/metric not present in the profile, add a question instead of a number.

## Endpoint: Rewrite Text

`POST /api/ai/rewrite`

Rewrites text using an LLM based on a user-provided prompt. This endpoint is used by the RichTextarea component's AI rewrite feature.

### Request (JSON)

- `text`: string (required, 1-10000 characters) - The text to rewrite
- `prompt`: string (required, 1-500 characters) - User's instruction for rewriting (e.g., "Make it more professional", "Make it shorter", "Improve clarity")

### Response (JSON)

- `rewritten_text`: string - The rewritten text

### Error Handling

- `400`: Invalid request (missing fields, validation errors)
- `422`: Validation error (text/prompt length out of range)
- `503`: LLM service not configured (missing `AI_ENABLED`, `AI_BASE_URL`, or `AI_API_KEY`)
- `500`: Server error (LLM API failure, network error)

### Rate Limiting

20 requests per minute per IP address.

### Configuration

Requires AI environment variables to be set:
- `AI_ENABLED=true`
- `AI_BASE_URL` (OpenAI-compatible API URL)
- `AI_API_KEY` (API key for the LLM provider)

See [AI Configuration](configuration.md) for details.

## Endpoint: Critique CV (Optional)

`POST /api/ai/critique-cv`

Returns issues only (no rewrites) for the current form payload + JD:

- `issues`: `{severity: "low"|"med"|"high", message: string, field?: string}[]`

## Error Handling

- `400`: invalid JD / invalid payload
- `422`: draft did not validate as `CVData`
- `503`: (future) provider unavailable when provider-backed generation is enabled
