# Layout 03: Modern Sidebar + Content (Web-First, Still Printable)

## Best for
- A modern look with strong personal branding (photo optional)

## Visual structure
- Persistent sidebar (left) with sticky sections on desktop
- Main scroll content on the right

## Suggested HTML skeleton
- `main` (two columns)
  - `aside` (profile, contact, skills, highlights)
  - `article` (experience, projects, education)

## Responsive + print behavior
- Mobile: sidebar collapses to accordion or top stack
- Print: turn off `position: sticky`, remove background fills

## Reliability notes
- Ensure sidebar content is accessible without relying on icons
- Keep sidebar width bounded; long skill lists should wrap cleanly

## Styling cues (Tailwind-friendly)
- Desktop: `md:grid md:grid-cols-[280px_1fr]`
- Sidebar: `md:sticky md:top-6`
- Use a muted background for sidebar (disable on print)
