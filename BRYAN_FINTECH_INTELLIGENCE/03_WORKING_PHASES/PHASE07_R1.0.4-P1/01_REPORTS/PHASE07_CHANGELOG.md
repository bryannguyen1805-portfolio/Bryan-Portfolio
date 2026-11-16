# PHASE 07 R1.0.1 CHANGELOG — TARGETED REMEDIATION
## Bryan FinTech Intelligence

- **Release Candidate:** `PHASE07_R1.0.1`
- **Remediation Baseline:** `PHASE07_R1.0.0` (SHA-256: `a270d954754400f6fdfa7665a83725d8b0a9a5d7b1ccedd74fc9d245ca039756`)
- **Parent Accepted Release:** `PHASE06_R1.0.0` (SHA-256: `d2f8672ff07bad36c9811906f69977a6d716de73d6685d874bd6a5ca53510bc9`)
- **Release Date:** `2026-11-11T10:32:52.481856+07:00`

---

### Remediation Fixes Applied in R1.0.1

1. **REM-01: Dynamic Daily Runtime Orchestrator (`phase07_daily_runtime_orchestrator.py`)**
   - Added `execution_mode: str = "LIVE"` supporting `"LIVE"`, `"OFFLINE"`, and `"REPLAY"`.
   - Replaced static date calculations with dynamic `Asia/Ho_Chi_Minh` (`VN_TZ`) timestamps.
   - Dynamic `executionId` formatted as `EXEC-YYYYMMDD-HHMMSS-<nonce>`.
   - Dynamic `editionId` formatted as `ED-YYYYMMDD-D01`.
   - Strict daily directory isolation: all outputs written to `06_DAILY_EDITIONS/daily-editions/{edition_date}/`.
   - Passed `executionId` and `executionMode` to validation reports, manifests, and step logs.

2. **REM-02: Source Provenance & Retrieval Integrity (`phase07_dynamic_news_engine.py`)**
   - Resolved multi-snapshot collision: grouped snapshots by canonical URL and selected the snapshot matching `SOURCE_RETRIEVAL_LOG.json`'s `contentSha256`.
   - Reconciled selected candidates to achieve **25/25 exact hash matches (100% parity)**.
   - Implemented fail-closed security for `RETRIEVAL_RECORD_MISSING`, `CONTENT_HASH_MISMATCH`, `ACCESS_BLOCKED`, and `OFFLINE_EVIDENCE`.

3. **REM-03: True Dynamic Financial Intelligence (`phase07_editorial_intelligence_engine.py`)**
   - Enforced Evidence-Based Payment Demand Classification Rules for logistics expansions.
   - Reclassified J&T Cargo parcel network expansion without direct payment demand evidence to `POTENTIAL_OPPORTUNITY` / `MEDIUM` confidence / action `VALIDATE`.
   - Preserved elevation logic to `VERIFIED_OPPORTUNITY` when direct payment demand evidence is substantiated.
   - Maintained full evidence traceability for all 4 Decision Cards and 5 Strategic Questions.

4. **REM-04: Dynamic Market Pulse Discovery (`phase07_market_pulse_runtime.py`)**
   - Implemented frequency-aware status determination: `NEW_OBSERVATION_VERIFIED`, `LATEST_OBSERVATION_RETAINED`, `STALE_OBSERVATION` (MP-02 age > 72h), `QUALITATIVE_UPDATE_ONLY` (MP-05, MP-06).
   - Enforced canonical approved publishers/domains validation; rejected unapproved publishers.
   - Enforced canonical units validation; rejected invalid/mismatched units.

5. **REM-05: Google Sheets Dry-Run Reconciliation (`google_sheets_dry_run_engine.py`)**
   - Parameterized `build_mapping_spec` with dynamic edition metadata.
   - Created single canonical source of truth for all dry-run metrics via `generate_dry_run_markdown_report`.
   - Reconciled exact row counts across validation, preview, and report: 155 baseline + 165 proposed = 320 merged rows.
   - Maintained strict read-only execution (`liveWriteApiCalled: False`).

6. **Test Suite Expansion (`07_TESTS/test_phase07_r101_remediation.py`)**
   - Added 19 comprehensive tests validating all 5 remediation groups.
   - All 63 tests (19 remediation + 22 runtime + 22 intelligence) pass with 100% success rate.
