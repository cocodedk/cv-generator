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

## Endpoint: Critique CV (Optional)

`POST /api/ai/critique-cv`

Returns issues only (no rewrites) for the current form payload + JD:

- `issues`: `{severity: "low"|"med"|"high", message: string, field?: string}[]`

## Error Handling

- `400`: invalid JD / invalid payload
- `422`: draft did not validate as `CVData`
- `503`: AI disabled or provider unavailable
