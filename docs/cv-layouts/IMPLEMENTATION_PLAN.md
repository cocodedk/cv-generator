# Implementation Plan: Selecting and Creating HTML CV Layouts

This plan is a simple, user-friendly guide for choosing a layout and turning it into a working HTML/CSS implementation.

## 1) Choose the right layout

Pick based on how the CV will be used:

- Print/PDF first: start with Layout 01 or 02.
- Web presence / shareable link: start with Layout 04, 07, or 10.
- Storytelling focus: start with Layout 05 or 06.
- Academic focus: start with Layout 09.

If you need both web and print, pick the best web layout and add a print stylesheet rather than forcing a single layout to do everything.

## 2) Validate content fit

Before building, check the content against the layout:

- Long experience list? Avoid heavy card grids.
- Many skills? Consider the matrix layout or a single-column list.
- Lots of projects? Use the case study layout.

If the content does not fit, choose a simpler layout or reduce visual complexity.

## 3) Define a stable HTML structure

Use semantic tags and a consistent section order:

- `header` for name/title/contact
- `main` for the CV body
- `section` for each category
- `article` for each role or project

Keep headings consistent (example: `h2` for section titles, `h3` for entries).

## 4) Create a layout variant

For each new layout:

1. Create a new file in `docs/cv-layouts/` based on the existing naming pattern.
2. Describe:
   - Best for
   - Visual structure
   - Suggested HTML skeleton
   - Responsive + print behavior
   - Reliability notes
   - Styling cues (Tailwind-friendly)

This keeps documentation consistent and easy to scan.

## 5) Build the layout in the UI

Implementation steps (frontend):

- Create a new layout component with a clear, reusable structure.
- Keep layout-specific styles local (avoid global overrides).
- Use utility classes for spacing and typography consistency.
- Ensure sections collapse well when data is missing.

## 6) Add print behavior (if needed)

For print-friendly layouts:

- Add `@media print` rules to remove shadows and colors.
- Avoid absolute positioning for content blocks.
- Use `break-inside: avoid` on role/project items.

## 7) Validate with real content

Use realistic data:

- 2–3 jobs, 2 projects, 10–20 skills
- Long and short summary text
- Optional sections removed

If the layout breaks with real data, simplify it.

## 8) Update the index

When a new layout is added:

- Add it to `docs/cv-layouts/README.md`.
- Keep the list ordered and consistent with numbering.
