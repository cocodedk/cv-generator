# API Contract: Long Single-Page PDF

## Endpoint

`POST /export/pdf/long`

## Request Body

```json
{
  "html": "<full html content>",
  "format": "A4_WIDTH_LONG",
  "margin_mm": 0
}
```

### Parameters

- **html** (required): Full HTML content to render
- **format** (optional): Format identifier, defaults to "A4_WIDTH_LONG"
- **margin_mm** (optional): Margin in millimeters, defaults to 0

## Response Codes

### Success (200)

Returns PDF bytes with `Content-Type: application/pdf`.

**Headers:**
```
Content-Type: application/pdf
Content-Disposition: attachment; filename="cv_long.pdf"
```

### Server Error (500)

PDF generation failure (rendering error, timeout, etc.).

**Response Body:**
```json
{
  "error": "PDF generation failed",
  "message": "Failed to render PDF: <error details>"
}
```

## Alternative Endpoint (CV-based)

`POST /api/cv/{cv_id}/export-pdf/long`

Generates PDF from existing CV in database.

**Query Parameters:**
- `theme` (optional): CV theme name
- `layout` (optional): CV layout name

Returns same response format as above.
