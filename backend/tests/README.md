# Backend Testing Standards

## API Endpoint Testing

### Error Response Testing

All API tests that expect error responses MUST validate both the HTTP status code AND the response content structure.

#### DO NOT do this (shallow testing):
```python
response = await client.post("/api/endpoint", json=invalid_data)
assert response.status_code == 422  # ❌ Only checks status
```

#### DO this (comprehensive testing):
```python
from backend.tests.test_api.response_helpers import assert_validation_error_response

response = await client.post("/api/endpoint", json=invalid_data)
error_data = assert_validation_error_response(response)  # ✅ Validates status + content
# Optional: Add domain-specific assertions
assert any("field_name" in str(error).lower() for error in error_data["detail"])
```

### Success Response Testing

Success responses should also validate response structure:

```python
from backend.tests.test_api.response_helpers import assert_success_response

response = await client.post("/api/endpoint", json=valid_data)
data = assert_success_response(response)  # ✅ Validates status + content structure
assert "expected_field" in data
```

## Why This Matters

- **Catches serialization bugs**: Tests like the JSON serialization error we fixed would have been caught
- **Validates API contracts**: Ensures responses match expected schemas
- **Prevents regressions**: Comprehensive tests catch edge cases that shallow tests miss
- **Improves reliability**: Better test coverage leads to more stable APIs

## Available Helpers

- `assert_validation_error_response(response, expected_status=422)` - For 422 validation errors
- `assert_success_response(response, expected_status=200)` - For successful responses
- `assert_error_response(response, expected_status, expected_message=None)` - For other error types

## Migration Guide

Existing shallow tests should be updated to use these helpers. The helpers will catch JSON serialization issues and other response format problems that status-only checks miss.
