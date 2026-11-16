# PHASE 07 — R1.0.3 DETAILED CHANGELOG
## Comparative Deltas: PHASE07_R1.0.2 -> PHASE07_R1.0.3

- **Release Candidate ID:** `PHASE07_R1.0.3`
- **Release Version:** `1.0.3`
- **Parent Accepted Release:** `PHASE06_R1.0.0`
- **Remediation Baseline:** `PHASE07_R1.0.2_REMEDIATION_BASELINE`
- **Date:** 2026-11-11

---

## 1. Source Code Modifications (`02_SOURCE_CODE/`)

### 1.1 `phase07_dynamic_news_engine.py`
- **Added `_normalize_retrieval_ledger` Class Method:**
  - Standardized normalization adapter for `live_ledger` whether provided as a dict mapping URLs to records, dict mapping IDs to records, or list of record dicts.
  - Normalizes canonical URLs, HTTP status codes, execution IDs, and provider response IDs.
- **Enhanced Execution-Specific Provenance:**
  - Added `execution_id` parameter to `__init__`.
  - Created authentic `executionSpecificLedger` populated in both LIVE and OFFLINE modes.
  - Prevented historical snapshot fallbacks from claiming `LIVE_SOURCE_VERIFIED`.
  - Fixed candidate attribute binding to ensure `primarySource` is accurately assigned from `pub_name`.
  - Replaced broad exception swallowing with execution-tagged stderr logging.

### 1.2 `phase07_editorial_intelligence_engine.py`
- **Eliminated Unrelated Event Fallbacks:**
  - Removed `if not tourism_events and self.verified_news: tourism_events = [self.verified_news[0]]`.
  - Refined tourism keyword matching to require specific tourism/inbound terms (`khách quốc tế`, `du lịch`, `vietqr global`, `hàng không`, `khách sạn`, `lữ hành`) rather than generic words like `quốc tế` or `hợp tác` alone.
- **Fixed Entity Binding Propagation:**
  - Consumes `f.get("verifiedEntity") or f.get("boundEntity")`, ensuring entity names survive Fact Auditing into editorial intelligence and eliminating any possibility of `None: 7%` string formatting.
- **Evidence-Grounded Payment Opportunity Radar:**
  - Conditioned J&T Cargo / logistics opportunities on explicit payment evidence (`VERIFIED_OPPORTUNITY` / `HIGH` / `SCALE` when payment evidence exists; `POTENTIAL_OPPORTUNITY` / `MEDIUM` / `VALIDATE` when absent).

### 1.3 `market_pulse_discovery.py`
- **Unified 8-Indicator Query Generation:**
  - Standardized search profiles and query generation across all 8 indicators (MP-01 to MP-08).
  - Step 10 records `actualExecutedQuery`, `searchProvider`, `searchTimestamp`, `resultCount`, and `updateStatus` in `discovery_log`.
- **Periodic Truth Retention:**
  - Preserved previous baseline values and original observation dates when no new verified observation is extracted.

### 1.4 `phase07_daily_runtime_orchestrator.py`
- **Execution Mode Governance:**
  - Directly exposes `executionMode`, `liveRetrievalReadiness`, and `productionStatus` in the dictionary returned by `execute_daily_run()`.
  - Strictly enforces `publicationAllowed = false`, `liveRetrievalReadiness = "NOT_APPLICABLE"`, and `productionStatus = "NOT_APPROVED"` in OFFLINE mode.
  - Requires authentic HTTP 200 retrieval records and matching SHA-256 hashes to award `LIVE_RETRIEVAL_PASS` in LIVE mode.
- **Same-Day Isolation:**
  - Automatically isolates each run in `executions/<executionId>/` while maintaining `edition-latest.json` as an atomic pointer.

---

## 2. Test Suite Additions (`07_TESTS/`)

### 2.1 Added `07_TESTS/test_phase07_r103_remediation.py`
- 17 targeted tests verifying:
  - Test 01: Collector-to-Ledger Normalization.
  - Test 02: Live Candidate Inclusion and Exclusion on Evidence Failure.
  - Test 03: Historical Snapshot Cannot Claim LIVE_SOURCE_VERIFIED.
  - Test 04: Missing Retrieval Ledger Fails Closed in LIVE Mode.
  - Test 05: Offline Execution Mode Governance.
  - Test 06: Entity Binding Preservation (`verifiedEntity`).
  - Test 07: Input Mutation Test A — Sports-Only Input.
  - Test 08: Input Mutation Test B — Interest-Rate Policy Event.
  - Test 09: Input Mutation Test C — Contradictory Events CounterEvidence.
  - Test 10: Input Mutation Test D — Direct Payment Adoption Yields VERIFIED_OPPORTUNITY.
  - Test 11: Input Mutation Test E — Removing Payment Evidence Downgrades.
  - Test 12: Input Mutation Test F — Market Pulse Observation Mutation.
  - Test 13: Input Mutation Test G — Unrelated Events Produce No Fabrication.
  - Test 14: Market Pulse Discovery — All 8 Indicators Execute Queries & Record Provenance.
  - Test 15: Market Pulse Retention — Missing Observations Retain Previous Values & Dates.
  - Test 16: Same-Day Execution Isolation & Immutability.
  - Test 17: Release Governance, Safety Locks & Parent Baseline Protection.

---

## 3. Configuration & Schemas (`03_SCHEMAS_AND_CONFIG/`)
- Preserved `PHASE07_RUNTIME_CONFIG.json` with all 5 production safety locks set to `False`.
- Preserved single canonical indicator specification in `03_INDICATOR_CONFIG/market_pulse_indicator_specs.json`.
