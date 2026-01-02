# Architecture: Long Single-Page PDF

## Technical Approach

Not every HTML→PDF engine supports dynamic page height cleanly. The recommended approach uses **headless Chromium** (Playwright/Puppeteer) with custom paper dimensions.

## Why Chromium?

- **WeasyPrint**: Great for print-like PDFs, but "one super tall page" is unreliable
- **Chromium**: Reliable dynamic height measurement and rendering
- **CSS compatibility**: Matches browser rendering exactly

## Architecture Flow

1. **Render HTML** in headless Chromium at fixed viewport width (A4 width)
2. **Wait for assets** (fonts, images) to load completely
3. **Measure content height** (`document.documentElement.scrollHeight`)
4. **Calculate PDF height** in millimeters from pixel measurement
5. **Generate PDF** with custom width + computed height
6. **Return PDF** bytes or error

## Width Mapping

Use **96 DPI** (Chromium's CSS pixel baseline):

- A4 width = 210mm = 8.2677 inches
- Pixels = 8.2677 × 96 ≈ **794px**

Set viewport width to **~794px** (minus margins, depending on CSS).

## Height Calculation

After rendering and asset loading:

1. Measure `document.documentElement.scrollHeight`
2. Add padding buffer: `height += 50px` (avoid last-line clipping)
3. Convert pixels to millimeters:
   - `inches = px / 96`
   - `mm = inches × 25.4`
   - `height_mm = (height_px / 96) × 25.4`

## Component Responsibilities

- **HTML Renderer**: Generates HTML from CV data (reuses print HTML renderer)
- **PDF Generator**: Measures content, calculates dimensions, generates PDF
- **API Handler**: Validates input, handles errors, returns PDF or error response
