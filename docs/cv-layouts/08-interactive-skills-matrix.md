# Layout 08: Interactive Skills Matrix (Web + Filtering)

## Best for
- Senior/technical profiles where breadth + depth needs structure

## Visual structure
- Skills displayed as a matrix: domains × proficiency (or years)
- Filters (role, domain, “used recently”) update visible items
- Supporting sections: experience, selected projects

## Suggested HTML skeleton
- `header` (summary + roles targeted)
- `main`
  - `section` Filters (`form` elements)
  - `section` Skills matrix (`table` or grid of lists)
  - `section` Evidence (projects/experience mapping)

## Responsive + print behavior
- Mobile: matrix becomes stacked lists by domain
- Print: optional; replace interactive controls with static legend

## Reliability notes
- If using `table`, use proper `thead/tbody/th` for accessibility
- Don’t encode proficiency only as color; include text labels

## Styling cues (Tailwind-friendly)
- Filters: `flex flex-wrap gap-2`
- Matrix: prefer `grid` for responsiveness unless true table semantics help
