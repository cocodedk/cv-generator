# AI API (Planned)

This feature adds a small, isolated API surface that returns validated CV drafts.

## Endpoint: Generate CV Draft

`POST /api/ai/generate-cv`

The backend loads the saved master profile and generates a tailored `CVData` draft.

### Request (JSON)

- `job_description`: string (required)
- `target_role`: string (optional)
- `seniority`: string (optional)
- `style`: `"select_and_reorder" | "rewrite_bullets"` (optional; default select/reorder)
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

## Endpoint: Critique CV (Optional)

`POST /api/ai/critique-cv`

Returns issues only (no rewrites) for the current form payload + JD:

- `issues`: `{severity: "low"|"med"|"high", message: string, field?: string}[]`

## Error Handling

- `400`: invalid JD / invalid payload
- `422`: draft did not validate as `CVData`
- `503`: AI disabled or provider unavailable
