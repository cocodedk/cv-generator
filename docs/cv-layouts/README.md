# HTML CV Layouts (Alternative Looks)

This folder proposes 10 viable HTML layout patterns for alternative CV looks. Each layout is described as a stable, semantic HTML structure with practical notes for responsiveness, print behavior, and Tailwind-friendly styling.

## Plan

- [Implementation Plan](IMPLEMENTATION_PLAN.md) - How to select and create new layouts

## Layouts

1. [Classic Two-Column (Print-First)](01-classic-two-column.md)
2. [ATS-Optimized Single Column (Text-First)](02-ats-single-column.md)
3. [Modern Sidebar + Content (Web-First, Still Printable)](03-modern-sidebar.md)
4. [Section Cards Grid (Web Presentation)](04-section-cards-grid.md)
5. [Career Timeline (Narrative Progression)](05-career-timeline.md)
6. [Project Case Studies (Long-Scroll Story)](06-project-case-studies.md)
7. [Portfolio SPA (Multi-Route Web CV)](07-portfolio-spa.md)
8. [Interactive Skills Matrix (Web + Filtering)](08-interactive-skills-matrix.md)
9. [Academic CV (Publications-First)](09-academic-cv.md)
10. [Dark-Mode Tech Resume (Web Showcase)](10-dark-mode-tech.md)

## How to use these docs
- Pick a layout based on target channel (PDF/print vs web).
- Keep semantic structure stable (headings, lists, articles), and treat visuals as optional.
- If you support both web and print, implement an explicit print mode (route or stylesheet) rather than forcing one layout to do everything.

## Implementation Status

All 10 layouts have been implemented and are available in the CV Generator:

- ✅ Layout templates are located in `backend/cv_generator_docx/templates/layouts/`
- ✅ Shared components are in `backend/cv_generator_docx/templates/layouts/components/`
- ✅ Layout selection is available in the frontend CV form
- ✅ Layouts work independently from themes (you can combine any theme with any layout)
- ✅ All layouts support responsive design and print styles where applicable

See [Print HTML Generation](../backend/print-html-generation.md) for technical details.

## Implementation Notes & Limitations

Some layouts have simplified implementations compared to their documentation:

### Academic CV (Layout 09)
- **Publications section**: Currently shows a placeholder message. The data model does not include a dedicated `publications` field. Add publications manually or extend the data model if needed.

### Portfolio SPA (Layout 07)
- **Navigation**: Uses anchor-based navigation (`#home`, `#experience`, etc.) rather than true client-side SPA routing. This is intentional for static HTML output compatibility.

### Dark Mode Tech (Layout 10)
- **Theme toggle**: Uses CSS `prefers-color-scheme: dark` media query to automatically match the user's system preference. There is no manual toggle button; the theme switches based on OS/browser dark mode setting.

### Interactive Skills Matrix (Layout 08)
- **JavaScript filtering**: Includes client-side JavaScript for filtering skills by category. This functionality is disabled when printing.

### Projects
- Projects are nested under Experience entries (`experience[].projects`). Standalone projects not tied to a specific job position are not currently supported as a top-level section.
