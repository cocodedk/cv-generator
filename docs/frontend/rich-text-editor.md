# Rich Text Editor

The CV Generator uses a rich text editor for textarea fields to allow HTML formatting while maintaining plain text length validation.

## Component

**Location**: `frontend/src/components/RichTextarea.tsx`

Reusable component built on TipTap (ProseMirror) that provides:
- HTML formatting toolbar (bold, italic, underline, strike, headers, lists, links)
- Character counter (counts plain text, excludes HTML tags)
- Max length validation
- Error state styling
- Dark mode support
- Customizable rows/height
- Optional in-form “AI Assist” actions (see below)

## Usage

RichTextarea is used in three places:

1. **Personal Info Summary** (`PersonalInfo.tsx`)
   - 4 rows default height
   - No character limit
   - HTML formatting supported

2. **Experience Description** (`ExperienceItem.tsx`)
   - 10 rows default height
   - 300 character limit (plain text)
   - HTML formatting supported
   - Client-side and server-side validation

3. **Project Highlights** (`ProjectEditor.tsx`)
   - 3 rows default height
   - No character limit
   - HTML formatting supported
   - Converts to/from array format

## HTML Content Handling

- HTML content is preserved in the database
- Templates render HTML safely using Jinja2 `|safe` filter
- Validation counts plain text only (HTML tags stripped)
- HTML entities are decoded when counting characters

## Validation

The component enforces max length by:
1. Stripping HTML tags to get plain text
2. Counting plain text characters
3. Preventing input if limit exceeded
4. Displaying character count with error styling when exceeded

## AI Assist (Edit CV)

When enabled via the `showAiAssist` prop, RichTextarea shows two helper actions:

- **AI rewrite**: light rewrite for clarity (safe, deterministic transformations)
- **AI bullets**: converts sentences into bullet points + applies the same rewrites

This is an in-form helper intended to speed up editing. It does not require a job description.
For the JD-based draft flow, see `docs/ai/overview.md`.

See [Backend Models](../backend/models.md) for server-side validation details.
