# Print HTML Generation

The CV Generator can render CV data into browser-printable HTML format optimized for A4 printing.

## Overview

Print HTML generation creates HTML documents that are:
- Optimized for A4 page size
- Print-ready with proper page breaks
- Styled for professional appearance
- Compatible with all modern browsers

## Use Cases

- Preview CV before generating DOCX
- Print directly from browser
- Share as HTML file
- Generate PDF via browser print-to-PDF

## API Endpoints

- `POST /api/render-print-html` - Render from CV data payload
- `GET /api/cv/{cv_id}/print-html` - Render from existing CV

See [API Endpoints](api-endpoints.md) for details.

## Theme Support

All CV themes are supported:
- **classic**: Traditional single-column layout
- **modern**: Clean, contemporary design
- **minimal**: Simple, minimal styling
- **elegant**: Sophisticated, professional design
- **accented**: Two-column layout with accent colors

If no theme is specified, defaults to "classic".

## Implementation

The print HTML renderer is located in:
- `backend/cv_generator_docx/print_html_renderer.py`: Main rendering logic
- `backend/cv_generator_docx/templates/print_html/`: HTML templates

## Template Structure

Templates use Jinja2 for rendering:
- `base.html`: Main template structure
- `components/`: Reusable component templates
  - `experience_item.html`: Experience entry rendering
  - `education_item.html`: Education entry rendering
  - `skills_list.html`: Skills section rendering

## Output Format

The generated HTML includes:
- Embedded CSS for print styling
- A4 page size specifications
- Print media queries
- Professional typography and spacing

## Related Documentation

- [CV Generation](cv-generation.md) - DOCX generation
- [DOCX Generation](docx-generation.md) - Markdown pipeline details
