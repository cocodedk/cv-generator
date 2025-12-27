# Layout 07: Portfolio SPA (Multi-Route Web CV)

## Best for
- Publishing as a complete web presence (not primarily a PDF)

## Visual structure
- App shell with top nav + routed pages:
  - `/` Home (summary + highlights)
  - `/projects` Project list + detail views
  - `/experience` Full timeline
  - `/contact` Links and downloadable PDF

## Suggested HTML skeleton
- `header` app shell nav
- `main` route outlet
- `footer` (social, email, print/PDF link)

## Responsive + print behavior
- Mobile: nav collapses; content stays single column
- Print: optional “print view” route that renders a print-first layout

## Reliability notes
- Ensure every route renders meaningful HTML without JS-only content
- Provide canonical anchors for key sections for sharing

## Styling cues (Tailwind-friendly)
- Use consistent page padding + max width per route
- Prefer lightweight transitions; avoid scroll-jank parallax
