# PHASE 06 — KNOWN LIMITATIONS (`PHASE06_R1.0.0`)

1. **Pilot News Quota Shortfall (`18 / 25` Verified Unique Events, `16 / 25` in `0–24h`):**
   - Snapshot `ED-20261110-D01` contains 18 verified unique news events (16 in `0_TO_24H`, 1 in `24_TO_48H`, 1 in `48_TO_72H`).
   - Because `16 < 25` required for `0–24h` production publication, `dailyEditionReadiness` is strictly classified as `DATA_SHORTFALL_OR_UNVERIFIED` (Internal Pilot / Preview Only).
2. **Market Pulse Indicator Temporal & Qualitative States:**
   - `MP-02` (Overnight interbank rate): `2.8 %/năm` observed on `2026-10-02` (`STALE_OBSERVATION` / `UNVERIFIED`, exceeding the 72.0h ceiling).
   - `MP-05` (System-wide credit growth) and `MP-06` (VietQR transaction volume): `QUALITATIVE_UPDATE_ONLY` / `UNVERIFIED` with `actualValue: null` and `observationDate: null`.
   - `MP-08` (OMO net injection): `47915 tỷ VND` observed on `2026-09-21` (`HISTORICAL_EVENT_OPERATION_2026_09_21`), representing the latest verified historical operation rather than a November 2026 injection.
3. **Google Sheets Live Write API Disabled:**
   - Synchronization with the 7 staging tabs is executed strictly as an in-memory and JSON-preview dry-run (`liveWriteApiCalled: False`).
