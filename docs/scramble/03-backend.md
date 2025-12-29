# Scrambled Personal Info - Backend/Export Steps

1. Decide if exported HTML/DOCX should be locked by default or fully readable.
2. If locked, apply the same scramble helper in the HTML/DOCX renderer layer.
3. Ensure print-html and download endpoints respect the lock setting.
4. Add an explicit request flag for unlocked exports, and validate it server-side (see below).
5. Document the behavior in API docs so consumers know how to request unlocked output.

---

## Current Implementation

- Scrambling is applied only for showcase HTML generation (GitHub Pages output).
- Unlocking is client-side only via the embedded script; no backend validation endpoint yet.

---

## Server-Side Validation for Unlocked Export

### Required Request Fields

| Field | Type | Description |
|-------|------|-------------|
| `unlocked_export` | boolean | Must be explicitly `true` to request unlocked output. |
| `unlock_key` | string | Base64-encoded 32-char key; sent over TLS only. |

### Validation Steps

1. **Flag Check:** If `unlocked_export` is missing or `false`, return locked output (no key required).
2. **Key Presence:** If `unlocked_export=true` but `unlock_key` is missing/empty → `400 Bad Request`.
3. **Key Verification:** Compute `SHA256(unlock_key)` using **constant-time comparison** against `cv.unlock_key_hash` stored in the database. Mismatch → `401 Unauthorized`.
4. **Permission Check:** Verify the authenticated user is the CV owner OR has explicit `export:unlock` permission on the CV. Failure → `403 Forbidden`.
5. **Lock State Check:** If `cv.is_locked = false`, unlocked export is redundant but allowed. If `cv.is_locked = true` and key mismatches → `409 Conflict` (state mismatch).

### Key Rotation & One-Time Tokens

- Unlock keys may be configured as **one-time-use**; after successful unlock, rotate the key hash.
- Alternatively, keys may have a TTL; server rejects expired keys with `401`.
- See `02-frontend.md` for client-side token generation and expiry handling.

### HTTP Error Codes Summary

| Code | Condition |
|------|-----------|
| `200` | Success; unlocked export returned. |
| `400` | Missing `unlocked_export` flag or `unlock_key`. |
| `401` | Invalid or expired `unlock_key`. |
| `403` | Authenticated user lacks permission. |
| `409` | CV lock state mismatch (e.g., already unlocked). |

### Audit Logging

Log every unlock attempt with: timestamp, user ID, CV ID, success/failure, client IP (masked last octet).

### Example Request

```http
POST /api/cv/abc123/export HTTP/1.1
Content-Type: application/json
Authorization: Bearer <jwt>

{
  "unlocked_export": true,
  "unlock_key": "c2VjcmV0X2tleV9oZXJlXzMyY2hhcnM=",
  "format": "html"
}
```

### Example Response (Success)

```json
{
  "status": "ok",
  "download_url": "/exports/abc123-unlocked.html",
  "key_rotated": true,
  "expires_at": "2025-12-29T12:00:00Z"
}
```

### Example Response (Failure - Bad Key)

```json
{
  "status": "error",
  "code": 401,
  "message": "Invalid or expired unlock key."
}
```
