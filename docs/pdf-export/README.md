# Long Single-Page PDF Export

This feature generates PDFs with A4 width and dynamic height matching the HTML content - a single continuous page without pagination.

## Quick Reference

- **Output**: Single-page PDF (A4 width, content height)
- **Technology**: Headless Chromium (Playwright/Puppeteer)
- **API**: `POST /export/pdf/long`
- **Height**: Matches HTML content height exactly

## Documentation Structure

- [Overview](01-overview.md) - Feature definition and use cases
- [Architecture](02-architecture.md) - Technical approach and design
- [Implementation](03-implementation.md) - Playwright setup and measurement
- [API Contract](04-api.md) - Endpoint specification
- [CSS Requirements](05-css-requirements.md) - Print CSS rules
- [Testing](06-testing.md) - Test cases and validation
- [Limits & Safety](07-limits-safety.md) - Constraints and error handling

## Related Documentation

- [Print HTML Generation](../backend/print-html-generation.md) - HTML rendering for print
- [CV Generation](../backend/cv-generation.md) - DOCX generation pipeline
