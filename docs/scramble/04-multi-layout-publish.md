# Save-Time Multi-Layout Generation - Plan

1. On save, trigger HTML generation for every layout using the selected color/theme.
2. Store each output with a stable naming scheme: `{cv_id}/{layout}-{theme}.html`.
3. Persist a manifest (JSON) listing all generated layouts for the CV.
4. Ensure the generator uses the same data snapshot used for the save action.
5. Add a toggle to enable/disable the multi-layout publish feature per CV.

---

## Implementation Notes

- Outputs are written to `CV_SHOWCASE_OUTPUT_DIR` (default: `backend/output/showcase`).
- Scrambling is applied only for showcase outputs; local exports remain unlocked.
- Keys are read from `CV_SHOWCASE_SCRAMBLE_KEY` or generated per CV and stored in
  `CV_SHOWCASE_KEYS_DIR` (default: `backend/output/showcase_keys/{cv_id}.key`).
- The feature can be disabled via `CV_SHOWCASE_ENABLED=false`.
