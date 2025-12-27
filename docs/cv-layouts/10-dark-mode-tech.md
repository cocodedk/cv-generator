# Layout 10: Dark-Mode Tech Resume (Web Showcase)

## Best for
- Developer-facing audiences; personal site and sharing

## Visual structure
- Dark theme with code-like typography accents (subtle)
- Sections: about, experience, projects, open-source, writing

## Suggested HTML skeleton
- `header` (name + theme toggle)
- `main` (sections with anchor nav)
- `footer` (links)

## Responsive + print behavior
- Mobile: anchor nav becomes drawer or top chips
- Print: switch to light theme automatically with `@media print`

## Reliability notes
- Ensure color contrast meets WCAG in dark mode
- Don’t rely on syntax highlighting to convey meaning

## Styling cues (Tailwind-friendly)
- Use CSS variables for theme tokens; Tailwind `dark:` for variants
- Keep animations minimal; respect `prefers-reduced-motion`
