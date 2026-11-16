# PHASE 07 — R1.0.4 LIVE PROVENANCE AUDIT

- **Release ID:** `PHASE07_R1.0.4`
- **Audit Date:** 2026-11-11
- **Auditor:** Independent QA Lead & Senior Data Engineer

---

## 1. Audit Scope & Verification Findings

### WS-01.1: Collector-to-Ledger Normalization
- Handled via `Phase07DynamicNewsEngine._normalize_retrieval_ledger(live_ledger, execution_id)` returning `NormalizedLedger`.
- Maps:
  - `statusCode` → `actualHttpStatusCode`
  - `responseSha256` → `contentSha256`
  - `originalUrl` → `requestedUrl`
  - `canonicalUrl` → `canonicalUrl`
  - `retrievedAt` → `retrievedAt`
- Preserves full incoming record in `rawRecord`.
- Rejects invalid data structures with `UNSUPPORTED_LEDGER_STRUCTURE`.

### WS-01.2: Live Candidate Discovery Propagation
- When `live_candidates` are provided, `step04_discover_candidates` propagates them directly into `rawCandidates`.
- If hash matches retrieval ledger and HTTP status is 200, `retrievalMode` is set to `LIVE_SOURCE_VERIFIED`.
- If hash mismatches or status is non-200, candidate is marked `LIVE_SOURCE_UNVERIFIED` and rejected in Step 05.

### WS-01.3: Current Execution Provenance
- In LIVE mode, retrieval records must match the current run's `executionId`.
- Prior runs' retrieval records are rejected with `HISTORICAL_PROVENANCE_MISMATCH`.

### WS-01.4: Post-T0 Cutoff Segregation
- In REPLAY mode, candidates with `retrievedAt > run_dt` are placed in `postCutoffEvidence` with disposition `REJECTED_POST_CUTOFF` and written to `POST_CUTOFF_EVIDENCE.json`.
