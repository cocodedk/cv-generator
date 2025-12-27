# Layout 04: Section Cards Grid (Web Presentation)

## Best for
- Publishing on the internet; a “dashboard” feel

## Visual structure
- Top hero (name, tagline, CTAs)
- Grid of cards for sections (skills, projects, experience highlights)
- Deep links from cards to expanded sections below

## Suggested HTML skeleton
- `header` hero
- `nav` quick links (anchors)
- `main`
  - `section` card grid (summary cards)
  - `section` expanded details (full experience, projects)

## Responsive + print behavior
- Mobile: 1-column cards; desktop: 2–3 columns
- Print: not ideal; if supported, switch to single column and remove card shadows

## Reliability notes
- Keep card content short; put detail in expanded sections
- Use anchor links (`id`) for stable navigation

## Styling cues (Tailwind-friendly)
- Card grid: `grid sm:grid-cols-2 lg:grid-cols-3 gap-4`
- Cards: border + subtle shadow (disable in print)
