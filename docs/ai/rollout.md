# AI Rollout Plan

Ship this in phases to keep behavior predictable and testable.

## Phase 1: Heuristics Draft (No LLM)

- Add “Generate from JD” UI and `POST /api/ai/generate-cv`.
- Backend selects/reorders profile items using deterministic scoring:
  - keyword overlap (JD ↔ skills/technologies)
  - recency weighting
  - length limits (trim long highlights)
- Output is always valid `CVData`.

## Phase 2: LLM Draft (Behind Flag)

- Enable provider calls when `AI_ENABLED=true`.
- LLM returns strict JSON for `draft_cv` plus `warnings/questions/summary`.
- Validate JSON into existing `CVData` model; reject on schema mismatch.
- Enforce “no invented metrics”: if numbers appear, require a user-confirmed source.

## Phase 3: Critique + Diff UX

- Add `POST /api/ai/critique-cv` for “review-only” feedback.
- Show a change summary and let users selectively apply sections.

## Phase 4: Persistence (Optional)

- Store job description + generation metadata linked to the CV for regeneration/comparisons.
