# Scrambled Personal Info - Frontend Steps

1. Add a UI state flag in the CV view to track lock/unlock.
2. Wrap personal-info fields with a render helper that returns scrambled text when locked.
3. Exempt LinkedIn, GitHub, website from the helper.
4. Implement hover reveal on those fields (CSS or onMouseEnter).
5. Add an "unlock" input: when key matches, set unlocked state.
6. Keep the key in memory only; do not persist in localStorage.

---

## Key Handling Details

### Key Generation

- Generate unlock keys client-side using `crypto.getRandomValues()` (24 bytes → 32-char Base64).
- Display the key once to the author for safekeeping; never show again after initial creation.

### Key Transmission

- Send keys to backend only over TLS.
- Backend stores `SHA256(key)` hash; raw key is never persisted server-side.
- For one-time-use tokens, backend rotates the hash after successful unlock.

### Token Expiry & Rotation

- Tokens may be configured with a TTL (default: 1 hour, max: 24 hours).
- Expired tokens return `401` from backend; frontend should prompt for a new key.
- Authors can regenerate keys from the CV settings page (invalidates previous key).

---

## URL Token Consumption (GitHub Pages)

1. Check `window.location.search` for `?unlock=<token>` on page load.
2. If present, apply client-side decryption using the SHA256-derived offset (see `01-overview.md`).
3. On failure, clear the URL param and show a "key invalid" toast.
4. On success, unlock in memory only; never persist.

---

## Cross-References

- **`01-overview.md`:** Defines the scrambling algorithm and key derivation.
- **`03-backend.md`:** Covers server-side validation, permission checks, and error codes.
- **`05-github-pages-showcase.md`:** Describes unlock mechanisms for published static pages.
