# Layout 09: Academic CV (Publications-First)

## Best for
- Academic/research roles with publications, grants, teaching

## Visual structure
- Single column with a strong TOC (optional)
- Emphasis on lists: publications, talks, teaching, service

## Suggested HTML skeleton
- `header` (name, affiliation, contact)
- `nav` (optional TOC with anchor links)
- `main`
  - `section` Research interests
  - `section` Appointments
  - `section` Publications (`ol` with consistent citation format)
  - `section` Grants / Awards / Teaching / Service

## Responsive + print behavior
- Mobile: TOC collapses
- Print: excellent; keep citations as plain text, avoid multi-column

## Reliability notes
- Use stable numbering for publications (ordered lists)
- Provide DOI/URL as real links; optionally include “Retrieved” dates

## Styling cues (Tailwind-friendly)
- Use tighter leading for long lists; keep headings prominent
- Consider hanging indents for citations (print-friendly)
