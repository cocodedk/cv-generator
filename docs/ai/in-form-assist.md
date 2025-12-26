# In-Form AI Assist

The Edit CV page and Profile page include per-field "AI Assist" actions for rich-text fields (summary, role summary, project highlights).

## What It Does

Each rich-text field can show two buttons:

- **AI rewrite**: Opens a modal to enter a custom prompt, then uses an LLM to rewrite text based on user instruction (e.g., "Make it more professional", "Make it shorter", "Improve clarity"). Requires LLM configuration.
- **AI bullets**: Converts sentences into bullet points using heuristic-based transformations (no LLM required, works offline).

This feature is intended as a fast editing helper while you are refining a CV or your master profile.

## When It Appears

- The buttons are shown in **Edit CV** mode (when a `cvId` is present) and on the **Profile** page.
- Implementation detail: Both `CVForm` and `ProfileManager` pass `showAiAssist={true}` into `RichTextarea` components.

## Important Notes

- **AI rewrite**: Requires LLM configuration (`AI_ENABLED=true`, `AI_BASE_URL`, `AI_API_KEY`). See [AI Configuration](configuration.md) for setup details.
- **AI bullets**: No job description or LLM configuration required. Uses heuristic-based transformations.
- Output is HTML (TipTap/ProseMirror content). For project highlights, the HTML is converted back into a string array.
- AI rewrite calls `/api/ai/rewrite` endpoint with user's prompt and current text.

Related:
- JD-based draft generation: `docs/ai/overview.md`
- Rich text editor details: `docs/frontend/rich-text-editor.md`
