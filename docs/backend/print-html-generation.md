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

## Theme and Layout Support

The print HTML generator supports both themes (styling) and layouts (structure):

### Themes

All CV themes are supported:
- **classic**: Traditional single-column layout
- **modern**: Clean, contemporary design
- **minimal**: Simple, minimal styling
- **elegant**: Sophisticated, professional design
- **accented**: Two-column layout with accent colors
- And more (see [CV Generation](cv-generation.md))

If no theme is specified, defaults to "classic".

### Layouts

Layouts define the structural arrangement of CV content:

**Print-First Layouts:**
- **classic-two-column**: Traditional two-column layout with sidebar
- **ats-single-column**: ATS-optimized single column format
- **modern-sidebar**: Modern sidebar layout, still printable

**Web-First Layouts:**
- **section-cards-grid**: Card-based grid layout
- **project-case-studies**: Long-scroll case study format
- **portfolio-spa**: Multi-route portfolio layout
- **dark-mode-tech**: Dark mode tech showcase

**Special Layouts:**
- **career-timeline**: Timeline visualization
- **interactive-skills-matrix**: Interactive skills filtering
- **academic-cv**: Academic/research format

If no layout is specified, defaults to "classic-two-column".

Themes and layouts work independently - you can combine any theme with any layout.

## Implementation

The print HTML renderer is located in:
- `backend/cv_generator_docx/print_html_renderer.py`: Main rendering logic
- `backend/cv_generator_docx/templates/print_html/`: HTML templates

## Template Structure

Templates use Jinja2 for rendering:

**Layout Templates:**
- Located in `backend/cv_generator_docx/templates/layouts/`
- Each layout has its own template file (e.g., `01-classic-two-column.html`)
- Layouts use shared components from `layouts/components/`

**Shared Components:**
- `components/header.html`: Header with name, title, contact
- `components/summary.html`: Professional summary section
- `components/experience_item.html`: Experience entry rendering
- `components/education_item.html`: Education entry rendering
- `components/skills_list.html`: Skills section rendering

**Legacy Templates:**
- `print_html/base.html`: Fallback template for theme-based rendering
- `print_html/components/`: Legacy component templates

## HTML Content Rendering

Templates safely render HTML content from CV data:
- `personal_info.summary` - Rendered with `|safe` filter in Jinja2
- `experience[].description` - Rendered with `|safe` filter in Jinja2
- HTML formatting (bold, italic, lists, links) is preserved and displayed
- Plain text length validation ensures content stays within limits

## Output Format

The generated HTML includes:
- Embedded CSS for print styling
- A4 page size specifications
- Print media queries
- Professional typography and spacing

## Related Documentation

- [CV Generation](cv-generation.md) - DOCX generation
- [DOCX Generation](docx-generation.md) - Markdown pipeline details
