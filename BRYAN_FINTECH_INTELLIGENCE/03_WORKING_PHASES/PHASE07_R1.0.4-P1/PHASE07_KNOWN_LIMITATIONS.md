# PHASE 07 R1.0.1 — KNOWN LIMITATIONS & OPERATIONAL NOTES

1. **Market Pulse Indicator Temporal States:**
   - `MP-02` (Overnight interbank rate): `5.75 %/năm` observed on `2026-10-31` has age `242.6h > 72.0h`. It is correctly and honestly retained as `STALE_OBSERVATION` / `UNVERIFIED`.
   - `MP-05` (Credit growth) and `MP-06` (VietQR transaction volume): Monthly/quarterly reporting cycles lack fresh daily numeric releases and are correctly marked `QUALITATIVE_UPDATE_ONLY` / `UNVERIFIED` with `currentValue: null`.
   - `MP-08` (OMO net injection): Preserves the latest verified historical central bank operation on `2026-09-21`.

2. **Google Sheets Integration:**
   - Synchronization is executed strictly in read-only staging dry-run mode (`liveWriteApiCalled: False`). Live write API requires project owner configuration of Service Account credentials.

3. **Production Safety Locks:**
   - Production deployment, automated cron triggers, and email notifications remain strictly disabled.
