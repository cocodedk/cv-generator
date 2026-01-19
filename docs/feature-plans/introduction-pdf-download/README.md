# Plan: Introduction Template PDF Downloads

## Goal
- Allow users to download the long single-page PDF for each template shown on `/#introduction`.
- Use the same PDF generation pipeline as CV form/list downloads.
- PDFs are pre-generated on each profile update so downloads are immediate.
- PDFs are stored as static assets so they work on GitHub Pages.
- PDF filenames include the profile owner name and stay human-readable (no opaque IDs).

## Background
- The introduction page loads `templates/index.json` from `frontend/public/templates`.
- Featured templates are generated from the latest profile via `CVFileService.generate_featured_templates`.
- CV form/list PDF downloads call `POST /api/cv/{cv_id}/export-pdf/long` and return a long single-page PDF.

## Proposed Approach
1. Extend featured template generation to output both HTML and PDF assets.
2. Store PDFs under `frontend/public/templates/pdfs/` and include `pdf_file` in `templates/index.json`.
3. Use descriptive filenames that include the profile owner name (e.g. `jane-doe-modern-sidebar-professional.pdf`).
4. Update the introduction page to download the static PDF file when present.
5. (Optional) Keep a backend on-demand PDF endpoint as a fallback if a PDF is missing.

## Backend Plan
- Update `CVFileService.generate_featured_templates` to also generate PDFs:
  - Generate HTML as today.
  - Generate PDF bytes using `PDFService.generate_long_pdf(render_print_html(cv_dict))`.
  - Build a safe `owner_slug` from `profile_name` (lowercase, hyphenated, ASCII-only; fallback to `profile`).
  - Write HTML to `frontend/public/templates/{owner_slug}-{layout}-{theme}.html`.
  - Write PDF to `frontend/public/templates/pdfs/{owner_slug}-{layout}-{theme}.pdf`.
  - Add `pdf_file` (and updated `file`) to each template entry in `index.json`.
- Trigger PDF generation whenever the profile is updated:
  - In `backend/app_helpers/routes/profile.py`, run featured asset generation after save.
  - Consider running PDF generation in a background task to avoid blocking the response.
- Extend `/api/generate-templates` to generate PDFs as well (for manual refresh).
- (Optional fallback) Add `/api/templates/export-pdf/long?layout=...&theme=...` for on-demand generation if a PDF is missing.

## Static Assets for GitHub Pages
- PDFs live under `frontend/public/templates/pdfs/` so they are included in the Vite build and served by GitHub Pages.
- `templates/index.json` provides both the HTML preview file and the PDF file for each template.
- Filenames include the profile owner name for clarity when shared as direct URLs.

## Frontend Plan
- Update `frontend/src/components/Introduction.tsx`:
  - Add "Download PDF" button next to "View Full" and in the preview modal.
  - Use the `pdf_file` from `templates/index.json` as the download href.
  - Set the `download` attribute to a readable name (e.g. `{profile_name} - {template.name}.pdf`).
  - Track per-template loading state in case a fallback API call is needed.
- Update `frontend/src/App.tsx` to pass `onError` (and optional `onSuccess`) into `Introduction`.
- (Optional fallback) Add a helper in `frontend/src/app_helpers/` to call the on-demand endpoint when `pdf_file` is missing.

## UX Notes
- Only show download controls when templates are loaded (current behavior).
- If no profile/templates exist, keep the existing empty-state messaging.

## Tests
- Backend: add tests that generated `index.json` includes `pdf_file` and files exist.
- Backend: add tests that filenames include the expected `owner_slug`.
- Frontend: add a component test that renders the download link when `pdf_file` is present.

## Open Questions
- Do we need an on-demand PDF endpoint, or is pre-generation sufficient?
- How should GitHub Pages builds get access to the latest profile data for regeneration?
