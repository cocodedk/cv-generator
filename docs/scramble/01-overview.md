# Scrambled Personal Info - Overview

1. Decide which fields are scrambled (all personal fields except LinkedIn, GitHub, website).
2. Define a single scrambling toggle state for the CV view (locked/unlocked).
3. Pick a scrambling method (see Scrambling Algorithm below).
4. Provide two unlock paths: hover reveal and key-based reveal.
5. Ensure the original data is never altered at rest; only the rendered output is scrambled.
6. Local generation is always unlocked; only GitHub Pages outputs are locked by default.

---

## Scrambling Algorithm

**Algorithm Name:** Deterministic Character Rotation with Key-Derived Offset (DCR-KDO)

### Character-Level Rules

| Character Type | Transformation | Notes |
|----------------|----------------|-------|
| Lowercase a–z | Rotate by offset mod 26 | Preserves case |
| Uppercase A–Z | Rotate by offset mod 26 | Preserves case |
| Digits 0–9 | Rotate by offset mod 10 | Wraps within digits |
| Whitespace | Preserved as-is | Spaces, tabs, newlines |
| Punctuation | Preserved as-is | `.,!?@#$%^&*()-_=+` etc. |
| Unicode (non-ASCII) | Preserved as-is | No substitution required |

### Reversibility Mechanism

- **Key Format:** 32-character Base64-encoded string (24 bytes entropy).
- **Offset Derivation:** `offset = SHA256(key)[0..3] mod 26` (first 4 bytes as uint32).
- **Unicode Handling:** Non-ASCII chars are preserved; no lookup map required.

### Examples

| Original | Scrambled (offset=7) | Reversal (offset=−7) |
|----------|----------------------|----------------------|
| `John Doe` | `Qvou Kvl` | `John Doe` |
| `alice@mail.com` | `hspjl@thps.jvt` | `alice@mail.com` |
| `+45 12345678` | `+45 89012345` | `+45 12345678` |
| `東京` | `東京` | `東京` |
| `123 Main St.` | `890 Thpu Za.` | `123 Main St.` |

---

## Frontend/Backend Integration

### Input/Output Formats

- **Input:** Plain UTF-8 string of the personal-info field value.
- **Output:** Scrambled UTF-8 string (non-ASCII preserved as-is).

### Key Exchange & Storage

- Showcase keys are read from `CV_SHOWCASE_SCRAMBLE_KEY` or generated per CV and stored
  in `CV_SHOWCASE_KEYS_DIR` (local only).
- Keys are not persisted in public output or `showcase/index.json`.

### Example API Payload

```json
POST /api/cv/{id}/export
{
  "unlocked_export": true,
  "unlock_key": "c2VjcmV0X2tleV9oZXJlXzMyY2hhcnM=",
  "format": "html"
}
```

Response (success):

```json
{
  "status": "ok",
  "download_url": "/exports/cv-123-unlocked.html",
  "expires_at": "2025-12-29T12:00:00Z"
}
```

### Security Considerations

1. **HTTPS Requirement:** The `/api/cv/{id}/export` endpoint **must** be served over HTTPS in production. Unlock keys transmitted over unencrypted connections are vulnerable to interception.

2. **Authentication/Authorization:** The export endpoint requires proper authentication and authorization. Only authorized users (e.g., CV owners, authenticated users with appropriate roles, or users with valid API tokens) should be permitted to call this endpoint. Implement role-based access control (RBAC) or token-based authentication as appropriate.

3. **Server-Side Key Validation:** The server **must** validate that the provided `unlock_key` matches the CV's stored key before generating unlocked content. Mismatched keys should be rejected with appropriate HTTP status codes (e.g., `403 Forbidden` or `401 Unauthorized`). Never trust client-provided keys without server-side verification.

4. **Logging Restrictions:** The `unlock_key` value **must NOT** be logged in plaintext. If logging is necessary for debugging or audit purposes, log only a hash or truncated version of the key. Sensitive keys in logs pose a security risk if log files are compromised.

5. **Key Lifecycle Management:**
   - Use short-lived or rotating keys when possible
   - Implement key expiry mechanisms (e.g., keys expire after 24 hours)
   - Consider single-use keys for sensitive exports
   - Rotate keys periodically to limit exposure window

6. **Alternative Transmission Methods:** Consider more secure alternatives for key transmission:
   - Encrypted headers instead of request body
   - Pre-signed download URLs with embedded, time-limited tokens
   - Server-side proxy endpoints that validate ownership before serving unlocked content
   - Out-of-band key delivery (email, secure messaging) with separate authentication
