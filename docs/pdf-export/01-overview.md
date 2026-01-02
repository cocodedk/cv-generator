# Overview: Long Single-Page PDF

## Definition

The long single-page PDF feature generates PDFs with:

- **Exactly 1 page** (no pagination)
- **Width = A4** (210mm / 8.2677 inches)
- **Height = content height** (matches HTML page height exactly)
- **No page breaks** or scaling down
- **Continuous scroll format** (like a web page)

This is essentially a "scroll PDF" - a single tall page that contains all content, with height matching the rendered HTML exactly.

## Use Cases

- **Long-form CVs**: CVs with extensive experience, projects, or publications
- **Portfolio documents**: Showcase work without page breaks interrupting flow
- **Academic CVs**: Research publications and achievements in one continuous document
- **Project case studies**: Detailed project documentation without fragmentation
- **Export for web**: PDFs that mirror web page scrolling behavior

## When NOT to Use

- **Standard A4 CVs**: Use regular print HTML generation for traditional CVs
- **Print-ready documents**: This format may not print well on physical paper (very tall pages)

## Key Characteristics

- Content is **not scaled down** (unless explicitly requested)
- Layout matches web rendering (no print-specific pagination)
- Suitable for digital viewing and sharing
- May require scrolling in PDF viewers
