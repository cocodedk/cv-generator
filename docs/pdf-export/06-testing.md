# Testing: Long Single-Page PDF

## Test Cases

### 1. Short Content (1 Screen)

**Input**: HTML with minimal content (fits on one screen)

**Expected**:
- PDF has exactly 1 page
- Height matches content (not full A4 height)
- No clipping or overflow
- Width is exactly 210mm

### 2. Long Content (10+ Screens)

**Input**: HTML with extensive content (multiple screens of scrolling)

**Expected**:
- PDF has exactly 1 page (no pagination)
- Height matches full content height
- No clipping at bottom
- All content visible and readable

### 3. Images and Webfonts

**Input**: HTML with external images and custom fonts

**Expected**:
- Height calculated after all assets load
- Images render correctly
- Fonts apply correctly
- No layout shift during measurement

### 4. Very Long Content

**Input**: HTML that generates PDF taller than 10 meters

**Expected**:
- PDF height matches HTML content height exactly
- All content visible and readable
- No clipping or truncation
- PDF generation completes successfully

### 5. Invalid HTML

**Input**: Malformed HTML or empty content

**Expected**:
- Returns 500 error
- Error message describes the rendering failure
- No crash or hanging process

## Validation Checks

- **Page count**: Must be exactly 1
- **Width**: Must be 210mm (±1mm tolerance)
- **Height**: Must match measured content height (±5mm tolerance)
- **Content visibility**: All content must be visible, no clipping
- **Asset loading**: Images and fonts must render correctly

## Performance Testing

- **Short document** (< 1000px height): Should complete in < 5 seconds
- **Medium document** (1000-5000px): Should complete in < 15 seconds
- **Long document** (5000-10000px): Should complete in < 30 seconds

## Edge Cases

- Empty HTML
- HTML with only whitespace
- HTML with very wide content (should wrap, not overflow)
- HTML with fixed positioning (may cause measurement issues)
