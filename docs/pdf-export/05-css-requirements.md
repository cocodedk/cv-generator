# CSS Requirements: Print Rules

## Required Print CSS

Even though we're generating a single page, print CSS rules prevent fragmentation and ensure proper rendering.

## Core Print Rules

```css
@media print {
  * {
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }

  /* Prevent page breaking inside common blocks */
  section, article, .block, .card, li {
    break-inside: avoid;
    page-break-inside: avoid;
  }

  /* Remove headers/footers if browser tries */
  @page {
    margin: 0;
  }

  body {
    margin: 0;
  }
}
```

## What These Rules Do

- **Color adjustment**: Preserves background colors and images
- **Break avoidance**: Prevents content from splitting awkwardly (even in single page)
- **Margin control**: Ensures content uses full page width
- **Body reset**: Removes default browser margins

## Layout Considerations

- Use **fixed width** matching A4 (794px at 96 DPI)
- Avoid `height: auto` in `@page` - it won't work for dynamic height
- Don't rely on `page-break: avoid` as the main solution
- Ensure fonts are loaded before measurement

## Font Loading

For accurate height measurement:

```css
@font-face {
  font-family: 'YourFont';
  src: url('font.woff2') format('woff2');
  font-display: block; /* Wait for font before rendering */
}
```

## Image Handling

Ensure images are loaded before measurement:

- Use `loading="eager"` for critical images
- Wait for `networkidle` state in Playwright
- Consider base64 embedding for small images
