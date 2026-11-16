# PHASE 07 — R1.0.2 AUTOMATED TEST REPORT

**Project:** Bryan FinTech Intelligence  
**Release ID:** PHASE07_R1.0.2  
**Execution Timestamp:** 2026-11-11T13:55:00+07:00  
**Overall Result:** 81 / 81 TESTS PASSED (100.0%)  

---

## 1. Test Suite Summary

### Suite 1: Phase 06 Baseline Suite (`test_phase06_intelligence.py`)
- **Total Tests:** 22 | **Passed:** 22 | **Failed:** 0
- Validates Draft 2020-12 Schema V4.0.0, event reference integrity, entity rebinding, duplicate fact prevention, evidence crosswalk, Core Thesis consistency, Macro-to-Micro 5-link causal chains, Payment Opportunity Radar grounding, Decision Cards, Market Pulse freshness separation, Google Sheets dry run, and multi-day reproducibility.
- Validates 8 adversarial tests (P06-ADV-14 through P06-GOV-22).

### Suite 2: Phase 07 Runtime Suite (`test_phase07_runtime.py`)
- **Total Tests:** 22 | **Passed:** 22 | **Failed:** 0
- Validates 20-step pipeline orchestration, environment detection, Vietnam clock handling, configuration loading, live news discovery, quality gating (25 events quota, 80% 24h freshness), fact auditing, Market Pulse discovery, Core Theses generation, Connect-the-Dots narratives, Macro-to-Micro chains, Payment Opportunity Radar, Decision Cards, Evidence Crosswalk, Google Sheets staging, step failure propagation, and idempotent execution.

### Suite 3: Phase 07 R1.0.1 Remediation Suite (`test_phase07_r101_remediation.py`)
- **Total Tests:** 19 | **Passed:** 19 | **Failed:** 0
- Validates dynamic date/edition metadata, next-day execution isolation, different-month execution, across-midnight execution, explicit execution modes (LIVE/OFFLINE/REPLAY), SHA-256 hash checking against retrieval ledger, fail-closed on hash mismatch, fail-closed on HTTP status failure, fail-closed on missing retrieval record, J&T Cargo potential opportunity classification, J&T Cargo elevation upon payment evidence, Decision Card traceability, Market Pulse frequency-aware staleness, approved publisher enforcement, wrong unit rejection, and single-source-of-truth Google Sheets row count reconciliation.

### Suite 4: Phase 07 R1.0.2 Remediation Suite (`test_phase07_r102_remediation.py`)
- **Total Tests:** 18 | **Passed:** 18 | **Failed:** 0
- TEST-01: Same-Day Execution Isolation & Immutability (PASS)
- TEST-02: Multi-Date Isolation (PASS)
- TEST-03: Midnight and Month Transition Execution (PASS)
- TEST-04: Live Mode Missing Retrieval Record Fail-Closed (PASS)
- TEST-05: Live Mode HTTP Error Fail-Closed (PASS)
- TEST-06: Snapshot SHA-256 Mismatch Fail-Closed (PASS)
- TEST-07: No False HTTP Status (None when missing, never defaulted to 200) (PASS)
- TEST-08: Market Pulse Discovery Invocation in Step 10 (PASS)
- TEST-09: Eight-Indicator Frequency-Aware Status & Validation (PASS)
- TEST-10: Input Mutation Test A — Add Interest-Rate Policy Event (PASS)
- TEST-11: Input Mutation Test B — Remove Major Financial Event (PASS)
- TEST-12: Input Mutation Test C — Change Market Pulse Observation (PASS)
- TEST-13: Input Mutation Test D — Contradictory News Captured in CounterEvidence (PASS)
- TEST-14: Input Mutation Test E — Unrelated News (Zero Unrelated Fallback) (PASS)
- TEST-15: Input Mutation Test F — Merchant Payment Adoption Signal (PASS)
- TEST-16: Input Mutation Test G — Remove Payment Evidence (Classified as POTENTIAL) (PASS)
- TEST-17: Google Sheets Canonical Reconciliation (155 + 165 = 320 merged rows) (PASS)
- TEST-18: Release Manifest Consistency & Parent Baseline Protection (PASS)
