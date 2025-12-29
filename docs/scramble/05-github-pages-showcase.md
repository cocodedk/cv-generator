# GitHub Pages Showcase - Plan

1. During CI, download the generated HTML files (or pull from a storage bucket).
2. Build a static `index.html` that lists each CV and links to all layout variants.
3. Publish the `index.html` and the generated HTML files to the Pages branch.
4. Add a simple JSON data file for the index to read (CV name, layout list, paths).
5. Keep the showcase read-only; do not expose edit/delete operations.

---

## Current Implementation

- The app writes a `showcase/index.json` file that the Introduction page reads.
- Each CV has a `manifest.json` stored in `showcase/{cv_id}/`.
- GitHub Pages should publish the `showcase/` directory as static assets.
- For local builds, point `CV_SHOWCASE_OUTPUT_DIR` to `frontend/public/showcase`.
- Public HTML includes an embedded unlock UI and supports `?unlock=<key>`.

---

## Access Control for Locked (Scrambled) CVs

### Default Visibility

- **Locked by default:** All published CVs display scrambled personal info unless the author explicitly embeds an unlock token at publish time.
- Authors may opt-in to publish unlocked by providing the unlock key during the publish workflow.

### Supported Unlock Mechanisms

| Context | Mechanism | Notes |
|---------|-----------|-------|
| Local interactive preview | Hover/temporary reveal | CSS-based; no key required for author's own browser. |
| Published GitHub Pages | URL token parameter | `?unlock=<token>`; short-lived (1–24 hours). |
| Published GitHub Pages | One-time shareable key | Delivered out-of-band (email, DM, Slack); single-use. |
| Published GitHub Pages | Server-side proxy endpoint | Validates ownership via OAuth; proxies unlocked HTML. |

**Clarification: URL Token Parameter vs. One-Time Shareable Key**

- **URL Token Parameter:** These are query-parameter tokens (used as `?unlock=<token>`) that are **time-limited** (validity period: 1–24 hours depending on configuration). They may be single-use or multi-use depending on server-side configuration. The primary enforcement mechanism is **time-based expiration**. Example: `https://example.com/showcase/cv-123.html?unlock=abc123xyz` where the token expires after 2 hours.

- **One-Time Shareable Key:** These are keys delivered **out-of-band** (via email, DM, Slack, etc.) and are intended to be **single-use** (consumed once and then invalidated). They can also be consumed via the same `?unlock=` parameter mechanism, but the enforcement is **usage-based** (single consumption) rather than time-based. Example: A key `def456uvw` is sent via email; after first use at `https://example.com/showcase/cv-123.html?unlock=def456uvw`, subsequent attempts with the same key are rejected.

**Key Distinction:** "One-time" refers to **single-use behavior** (consumption-based enforcement), while "URL token" refers to **time-limited validity** (expiration-based enforcement). Both mechanisms can use the same `?unlock=` URL parameter format, but their expiration/enforcement semantics differ.

### Frontend Token Consumption

1. On page load, check for `?unlock=<token>` in the URL.
2. If present, call backend `/api/validate-token` (if server proxy is used) or apply client-side decryption.
3. **Keys must NOT be persisted** in the public HTML, `localStorage`, or cookies.
4. After validation, display unlocked content in memory only; on page refresh, re-validate.
5. Optionally prompt the user for a key if no URL param is present and the CV is locked.

### Brute-Force Protections

| Protection | Requirement |
|------------|-------------|
| Key Entropy | Minimum 128 bits (24-byte Base64 = 192 bits). |
| HMAC-Signed Tokens | Tokens signed with server secret; tamper detection. |
| Token Expiry | Default 1 hour; configurable up to 24 hours. |
| Rate Limiting | Server-side unlock endpoint: 5 attempts/min per IP. |
| Lockout | After 10 failed attempts, require CAPTCHA or block for 15 min. |

---

## Cross-Reference Updates

- **`01-overview.md`:** States that GitHub Pages outputs are locked by default (step 6) and references the key transfer mechanism defined here.
- **`02-frontend.md`:** Describes client-side key handling (step 6: keep key in memory only) and the hover reveal interaction (step 4).
- **`03-backend.md`:** Covers server-side validation of unlock keys and permission checks for export requests.
