# Layout 05: Career Timeline (Narrative Progression)

## Best for
- Showing growth and transitions clearly (especially 5–15 year careers)

## Visual structure
- Single column with a vertical timeline spine
- Each role is a node with dates, company, title, achievements

## Suggested HTML skeleton
- `main`
  - `section` Experience
    - `ol` (timeline list)
      - `li` (role entry)

## Responsive + print behavior
- Mobile: timeline becomes simple list (hide spine)
- Print: can work; remove background graphics and keep nodes simple

## Reliability notes
- Timeline decorations must not carry meaning (text should stand alone)
- Keep date ranges as text, not only as positioned labels

## Styling cues (Tailwind-friendly)
- Spine: pseudo-element on list container
- Entries: `pl-8` with node marker aligned to spine
