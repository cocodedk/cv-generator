# AI CV Drafting (Plan)

This feature generates a CV draft from:
1) your saved master profile, and
2) a pasted job description (JD).

The user stays in control: AI returns a draft + issues/questions, and the UI lets you review before saving.

## UX Flow

1. User fills/saves Profile in the existing Profile page (`/api/profile`).
2. In the CV form, user clicks “Generate from Job Description”.
3. User pastes JD + selects options (target role, length, style).
4. Backend loads the saved master profile (`GET /api/profile` / `queries.get_profile()`).
5. Backend returns a `CVData` draft (validated) + `warnings/questions`.
6. Frontend applies the draft into the existing form (react-hook-form `reset()`).
7. User edits and then saves CV using existing endpoints (`/api/save-cv`, `/api/cv/{id}`).

## How Profile Data Is Used

The profile is treated as the only source of truth for claims. The generator:

- Scores each experience/project/highlight against the job description (keywords + responsibilities + recency).
- Selects the best-matching items and orders them to fit the target role.
- Optionally rewrites bullets, but only using facts present in the profile; otherwise it asks questions.

## Guardrails (Non-negotiable)

- No fabricated facts or metrics (if missing, leave blank + ask).
- Preserve user intent; prefer selecting/reordering over inventing.
- Return structured JSON that validates as `CVData`.
- Provide a “what changed” summary for review (diff-style list, not full rewrite).

## Provider Compatibility

Use an OpenAI-compatible HTTP API (base URL + key + model). See `docs/ai/configuration.md`.
