# Limits & Safety: Constraints and Error Handling

## Height Behavior

The PDF height **matches the HTML content height exactly** - there is no height limit. The PDF will be as tall as needed to contain all content.

**Note**: Very tall PDFs may:
- Require significant memory during generation
- Create large file sizes
- Be difficult to view in some PDF viewers
- Not be printable on physical printers

However, these are user considerations, not system limitations.

## Error Handling

### Server Error (500)

PDF generation failures (rendering error, timeout, memory issues, etc.).

**Response Body:**
```json
{
  "error": "PDF generation failed",
  "message": "Failed to render PDF: <error details>"
}
```

## Safety Rails

### Memory Protection

- Set Playwright memory limits
- Timeout after reasonable duration (e.g., 60 seconds)
- Clean up browser instances after generation

### Input Validation

- Validate HTML size (reject extremely large HTML)
- Sanitize HTML content
- Check for malicious content patterns

### Resource Cleanup

- Always close browser instances
- Clean up temporary files
- Handle errors gracefully without resource leaks
