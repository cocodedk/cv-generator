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

### Line Break Support

The component properly handles line breaks created by:
- **Enter key**: Creates new paragraphs (`<p>text</p><p>new paragraph</p>`)
- **Shift+Enter**: Creates line breaks within paragraphs (`<p>text<br>new line</p>`)

The component includes safeguards to prevent race conditions and HTML normalization issues that could cause formatting to be lost:
- Active editing state tracking prevents updates during user input
- HTML normalization handles TipTap's internal format differences
- Enhanced comparison logic ensures content is preserved correctly
- HTML formatting preservation: When profiles are reloaded, HTML formatting (bold, italic, line breaks) is preserved by requiring both plain text AND HTML to match before skipping updates

See [Profile Line Breaks Investigation](../troubleshooting/profile-line-breaks-investigation.md) and [Profile HTML Formatting Lost Investigation](../troubleshooting/profile-html-formatting-lost.md) for technical details.

## Validation

The component enforces max length by:
1. Stripping HTML tags to get plain text
2. Counting plain text characters
3. Preventing input if limit exceeded
4. Displaying character count with error styling when exceeded

## AI Assist (Edit CV)

When enabled via the `showAiAssist` prop, RichTextarea shows two helper actions:

- **AI rewrite**: Opens a modal to enter a custom prompt, then uses an LLM to rewrite text based on user instruction (e.g., "Make it more professional", "Make it shorter", "Improve clarity"). Requires LLM configuration (see [AI Configuration](../ai/configuration.md)).
- **AI bullets**: Converts sentences into bullet points using heuristic-based transformations (no LLM required, works offline)

**AI Rewrite Modal**:
- Prompt input textarea with placeholder examples
- Cancel and Rewrite buttons
- Loading state during LLM API call
- Error display if rewrite fails
- Converts plain text LLM response back to HTML for editor

This is an in-form helper intended to speed up editing. AI rewrite requires LLM configuration, while AI bullets works without any external services.
For the JD-based draft flow, see `docs/ai/overview.md`.

See [Backend Models](../backend/models.md) for server-side validation details.
