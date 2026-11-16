# PHASE 07 — R1.0.4 CONSOLIDATED TEST REPORT

- **Project:** Bryan FinTech Intelligence — MagSpread Editorial Edition
- **Release ID:** `PHASE07_R1.0.4`
- **Execution Date:** 2026-11-11
- **Total Test Suites:** 6
- **Total Automated Tests:** 113
- **Passed:** 113 (100.0%)
- **Failed:** 0 (0.0%)
- **Status:** **ALL_TESTS_PASS**

---

## 1. Test Suite Breakdown

### Suite 1: Phase 06 Financial Intelligence Baseline (`test_phase06_intelligence.py`)
- P06-TEST-01 to P06-TEST-13: Functional tests (13/13) — PASS
- P06-ADV-14 to P06-ADV-21: Adversarial edge cases (8/8) — PASS
- P06-GOV-22: Release Archiving & Baseline Protection (1/1) — PASS
- **Suite 1 Total: 22/22 Passed (100.0%)**

### Suite 2: Phase 07 Daily Runtime QA Suite (`test_phase07_runtime.py`)
- P07-TEST-01 to P07-TEST-22: End-to-end 20-step pipeline, windowing, deduplication, fact audit, thesis generation, transmission chains, radar, decision cards, crosswalk, schemas, Google Sheets dry-run, step failure propagation, and idempotent execution.
- **Suite 2 Total: 22/22 Passed (100.0%)**

### Suite 3: Phase 07 R1.0.1 Remediation Suite (`test_phase07_r101_remediation.py`)
- Group 1 (REM-01): Dynamic date, isolation, multi-date, midnight transition (6/6) — PASS
- Group 2 (REM-02): Ledger hash matching, multi-snapshot resolution, fail-closed (5/5) — PASS
- Group 3 (REM-03): J&T Cargo potential vs verified opportunity, decision traceability (3/3) — PASS
- Group 4 (REM-04): Dynamic Market Pulse discovery, approved publishers, unit validation (4/4) — PASS
- Group 5 (REM-05): Google Sheets 7-tab row reconciliation (1/1) — PASS
- **Suite 3 Total: 19/19 Passed (100.0%)**

### Suite 4: Phase 07 R1.0.2 Remediation Suite (`test_phase07_r102_remediation.py`)
- TEST-01 to TEST-07: Execution isolation, multi-date, fail-closed on tampered hash/missing records (7/7) — PASS
- TEST-08 to TEST-09: Market Pulse discovery invocation in Step 10 & 8-indicator status (2/2) — PASS
- TEST-10 to TEST-16: Input mutation tests A–G (policy events, contradictory news, sports-only, merchant payment adoption) (7/7) — PASS
- TEST-17 to TEST-18: Google Sheets reconciliation & baseline protection (2/2) — PASS
- **Suite 4 Total: 18/18 Passed (100.0%)**

### Suite 5: Phase 07 R1.0.3 Remediation Suite (`test_phase07_r103_remediation.py`)
- TEST-01 to TEST-05: Collector-to-Ledger adapter, live candidate inclusion, historical snapshot classification, missing ledger fail-closed, offline mode governance (5/5) — PASS
- TEST-06 to TEST-13: Entity binding preservation, input mutations A–G without fallback fabrication (8/8) — PASS
- TEST-14 to TEST-15: Market Pulse 8-indicator search execution & observation retention (2/2) — PASS
- TEST-16 to TEST-17: Execution isolation & release safety governance (2/2) — PASS
- **Suite 5 Total: 17/17 Passed (100.0%)**

### Suite 6: Phase 07 R1.0.4 Targeted Remediation Suite (`test_phase07_r104_remediation.py`)
- TEST 01: Collector Ledger Normalization (dict & list normalization, rawRecord preservation) — PASS
- TEST 02: Live Candidate Propagation (retrieval mode LIVE_SOURCE_VERIFIED, hash match, HTTP 200) — PASS
- TEST 03: Current Execution Provenance (rejection of historical ledger records in LIVE mode) — PASS
- TEST 04: False Retrieval Success Prevention (honest ACCESS_BLOCKED / missing status) — PASS
- TEST 05: Snapshot Hash Reconciliation (matching content SHA-256 from disk) — PASS
- TEST 06: Sports-Only Intelligence (zero fabricated financial theses on non-financial input) — PASS
- TEST 07: Interest Rate Policy Analysis (full thesis schema, causal explanation, limitations) — PASS
- TEST 08: Contradictory Financial Evidence (opposing news captured in counterEvidence & counterEvidenceEventIds) — PASS
- TEST 09: Evidence Removal Test (removal of supporting event downgrades or removes conclusion) — PASS
- TEST 10: Semantic Relevance Test (semiconductor news excluded from tourism opportunity) — PASS
- TEST 11: Direct Payment Adoption Test (cashless adoption elevates signal to VERIFIED_OPPORTUNITY) — PASS
- TEST 12: Verified Entity Propagation (boundEntity / verifiedEntity accurately surfaced) — PASS
- TEST 13: Eight Actual Market Pulse Searches (HTTP queries executed and logged) — PASS
- TEST 14: No New Market Observation (prior value and observation date strictly retained) — PASS
- TEST 15: Offline, Replay, and Publication Integrity (publicationAllowed=False in OFFLINE mode, post-cutoff isolated in REPLAY) — PASS
- **Suite 6 Total: 15/15 Passed (100.0%)**
