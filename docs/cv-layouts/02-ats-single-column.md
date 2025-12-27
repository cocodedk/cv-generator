# Layout 02: ATS-Optimized Single Column (Text-First)

## Best for
- Maximum compatibility with parsers (ATS) and copy/paste workflows

## Visual structure
- One column, minimal decoration
- Dense but readable spacing, consistent headings

## Suggested HTML skeleton
- `header` (name, title, contact links as plain text)
- `main`
  - `section` Summary
  - `section` Skills (bulleted or comma-separated)
  - `section` Experience (reverse-chronological)
  - `section` Education
  - Optional: Projects, Certifications

## Responsive + print behavior
- Mobile: naturally works
- Print: excellent; avoid multi-column and absolute positioning

## Reliability notes
- Prefer real text (no icon-only contact items)
- Avoid tables for layout; use simple blocks and lists
- Dates as plain text; avoid fancy separators that confuse parsing

## Styling cues (Tailwind-friendly)
- Container: `max-w-[750px] mx-auto px-6`
- Headings: high contrast, no decorative underlines that can clip in print
