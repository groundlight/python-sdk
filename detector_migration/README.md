# Detector account migration

Throwaway scripts for copying detectors and image queries between two Groundlight accounts, and checking migration progress.

Set credentials for both accounts:

- `GROUNDLIGHT_API_TOKEN_SRC` / `GROUNDLIGHT_API_TOKEN_DST`
- `GROUNDLIGHT_ENDPOINT_SRC` / `GROUNDLIGHT_ENDPOINT_DST` (optional)

## Scripts

- **`migrate_detectors.py`** — Copy detectors (by name) and their image queries from source to destination. Skips already-migrated IQs on re-run.
- **`compare_detectors.py`** — Read-only report of which source detectors are fully migrated, partially migrated, or not yet present in the destination account.
