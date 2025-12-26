# In-Form AI Assist

The Edit CV page and Profile page include per-field "AI Assist" actions for rich-text fields (summary, role summary, project highlights).

## What It Does

Each rich-text field can show two buttons:

- **AI rewrite**: cleans up phrasing and capitalization using safe, deterministic transformations.
- **AI bullets**: converts sentences into bullets and applies the same rewrites.

This feature is intended as a fast editing helper while you are refining a CV or your master profile.

## When It Appears

- The buttons are shown in **Edit CV** mode (when a `cvId` is present) and on the **Profile** page.
- Implementation detail: Both `CVForm` and `ProfileManager` pass `showAiAssist={true}` into `RichTextarea` components.

## Important Notes

- No job description is required.
- The behavior is heuristics-only (no provider calls).
- Output is still HTML (Quill content). For project highlights, the HTML is converted back into a string array.

Related:
- JD-based draft generation: `docs/ai/overview.md`
- Rich text editor details: `docs/frontend/rich-text-editor.md`
