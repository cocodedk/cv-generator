# Implementation: Playwright PDF Generation

## Playwright Setup

### Required Settings

Launch Chromium with:

- `--no-sandbox` flag if running inside Docker (security consideration)
- Viewport width: **~794px** (A4 width at 96 DPI)
- Disable default header/footer
- Margins: 0 (or controlled via CSS)

### Key PDF Generation Flags

When calling `page.pdf()`:

- `print_background: true` - Include background colors/images
- `display_header_footer: false` - No browser headers/footers
- `prefer_css_page_size: true` - Respect CSS page size (optional)
- `width: "210mm"` - Fixed A4 width
- `height: f"{height_mm}mm"` - Computed height in millimeters

## Measurement Process

### Step 1: Load Content

```python
await page.set_content(html)
```

### Step 2: Wait for Assets

Critical for accurate height measurement:

```python
# Wait for fonts
await page.evaluate("() => document.fonts.ready")

# Wait for images
await page.wait_for_load_state("networkidle")
```

### Step 3: Measure Height

```python
height_px = await page.evaluate("() => document.documentElement.scrollHeight")
height_px += 50  # Padding buffer
```

### Step 4: Convert to Millimeters

```python
height_mm = (height_px / 96) * 25.4
```

### Step 5: Generate PDF

```python
pdf_bytes = await page.pdf(
    width="210mm",
    height=f"{height_mm}mm",
    print_background=True,
    display_header_footer=False
)
```

## Docker Considerations

If running in Docker:

- Ensure Chromium dependencies are installed
- Use `--no-sandbox` flag (understand security implications)
- Consider memory limits for very long documents
