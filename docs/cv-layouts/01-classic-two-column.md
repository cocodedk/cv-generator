# Layout 01: Classic Two-Column (Print-First)

## Best for
- Traditional PDF/print exports and recruiters who skim quickly

## Visual structure
- Page grid: `2 columns` (left rail + main content)
- Left rail: contact, links, skills, languages
- Main: summary, experience, projects, education

## Suggested HTML skeleton
- `header` (name, title, contact)
- `main` (CSS Grid)
  - `aside` (rail)
  - `article` (primary content)

## Responsive + print behavior
- Mobile: collapse to single column (rail becomes top section)
- Print: lock to two columns; avoid reflow surprises
  - Use `@media print` to set fixed widths and reduce shadows/colors
  - Use `break-inside: avoid` for entries to prevent awkward splits

## Reliability notes
- Works with semantic headings (`h2` per section, `h3` per role)
- Stable even when sections are missing (rail can shrink)

## Styling cues (Tailwind-friendly)
- Grid: `grid grid-cols-1 md:grid-cols-[240px_1fr] gap-6`
- Rail typography smaller, main slightly larger
- Use subtle section dividers and consistent spacing
