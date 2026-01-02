# DOCX Generation (Markdown Pipeline)

The CV generator outputs DOCX files using a Markdown -> Pandoc pipeline:

1) Generate Markdown from structured CV data
2) Convert Markdown -> `.docx`
3) Apply theme styling via a Word template (or programmatic styling)

## Current Implementation

The DOCX pipeline is implemented in:

- `backend/cv_generator/` (Markdown renderer + Pandoc conversion)
- `backend/cv_generator/templates/` (theme templates)

Markdown is written alongside the generated DOCX (same filename, `.md` extension).

Dependencies:
- `pandoc` (system package in Docker image)
- `python-docx` (Python dependency)

### API Endpoints

- `POST /api/generate-cv-docx`
- `GET /api/download-docx/{filename}`
- `POST /api/cv/{cv_id}/generate-docx`

## Option A: Pandoc + Reference DOCX

**Idea**: Keep "style rules" inside a `reference.docx` per theme.

- Generate `cv.md` from the CV JSON/YAML
- Convert with Pandoc:
  - `pandoc cv.md -o cv.docx --reference-doc=themes/classic.docx`

**How themes work**
- Each theme is a `reference.docx` that defines:
  - Fonts (heading/body)
  - Colors (accent, headings)
  - Spacing (before/after paragraphs)
  - List styles (bullets)
  - Table styles (if used for layout)

**Mapping rules**
- Markdown headings -> Word heading styles:
  - `#` -> `Heading 1`, `##` -> `Heading 2`, etc.
- Paragraphs -> `Normal`
- Lists -> `List Bullet` / custom list styles
- For two-column "accented" layouts: use tables in Markdown (or emit raw DOCX structures via a post-step).

## Option B: Programmatic DOCX (Maximum Control)

Use `python-docx` (or similar) to build `.docx` directly from structured data.

Pros
- Precise control over tables, columns, borders, and spacing
- Easier to implement complex layouts (accented sidebar)

Cons
- More code than the Pandoc approach
- You must maintain a style mapping layer in code

## Template Generation

Templates are generated via:

```
python backend/cv_generator/template_builder.py
```

Run this inside the backend Docker container if dependencies were updated.
Regenerate templates if theme tokens or font choices change.

## HTML Content Rendering

Templates safely render HTML content from CV data:
- `personal_info.summary` - Rendered with `|safe` filter in Jinja2
- `experience[].description` - Rendered with `|safe` filter in Jinja2
- HTML tags are preserved and rendered in the final DOCX output
- Plain text length validation ensures content stays within limits

## Theme Evolution

- Reuse theme definitions by mapping theme tokens to template styles.
- Iterate in the DOCX templates when adjusting typography, spacing, or colors.

## When This Helps

- You need reliable layout control (tables, spacing, borders).
- You want theme iteration to happen mostly in a template file (designers can adjust without touching Python).
