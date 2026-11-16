# PHASE 07 — R1.0.4-P1 CHANGELOG

- **Release Version:** `PHASE07_R1.0.4-P1`
- **Baseline Version:** `PHASE07_R1.0.4`
- **Parent Accepted Release:** `PHASE06_R1.0.0`
- **Release Date:** 2026-11-11

---

## 1. Dynamic Financial Intelligence Layer
- `phase07_editorial_intelligence_engine.py`:
  - Removed generic boilerplate conclusions in Core Theses; derived `centralArgument`, `whatHappened`, `whyItMatters`, and `causalExplanation` from actual events, audited facts, and financial variables.
  - Set `counterEvidence: []` when no contradictory evidence exists in the observation window.
  - Updated Macro-to-Micro Transmission Chains: conditioned downstream merchant and consumer behavior stages (Stages 6 & 7) on direct payment demand evidence; otherwise labeled as `(Giả định phân tích)` with `HYPOTHESIS` inference classification.
  - Enforced Rule A (Tourism): classified as `POTENTIAL_OPPORTUNITY` / `MEDIUM` / `VALIDATE` when visitor numbers grow without direct cross-border payment acceptance evidence.
  - Enforced Rule B (J&T Cargo): freight expansion classified as `POTENTIAL_OPPORTUNITY` / `MEDIUM` / `VALIDATE` unless explicit cashless COD, SmartPOS, or VietQR evidence is present.
  - Enforced Rule C (Interest Rates): savings rate changes without consumer or retail payment demand evidence classified as macro monitoring, preventing phantom consumer installment opportunities.
  - Non-financial news (sports) produces 0 payment opportunities and 0 commercial decision cards.
  - Dynamic 5 Strategic Questions Executive Synthesis honestly reflects data presence or shortfall.

## 2. Provenance Ledger & Discovery Engine
- `phase07_dynamic_news_engine.py`:
  - In `_normalize_retrieval_ledger`, preserved original historical `executionId` (never overwritten with current execution ID); marked mismatched records as `retrievalStatus = "HISTORICAL_PROVENANCE_MISMATCH"`.
  - Prevented defaulting missing `retrievedAt` timestamps to current clock time; marked missing timestamps as `retrievalStatus = "TIMESTAMP_MISSING"` and `sourceVerificationStatus = "UNVERIFIED"`.
  - In `step04_discover_candidates` and Step 05, rejected candidates with `HISTORICAL_PROVENANCE_MISMATCH` or `TIMESTAMP_MISSING` from live verified pools.

## 3. Market Pulse Discovery Engine
- `market_pulse_discovery.py`:
  - In sandbox/offline execution where network access is restricted, captured `actualRequestStatus: "ACCESS_BLOCKED"` honestly in search audit records and execution tables.
  - Maintained canonical frequency-aware retention of the latest verified observation (`LATEST_OBSERVATION_RETAINED`).

## 4. Standalone MagSpread Pilot Preview
- `magspread-preview.html`:
  - Created standalone HTML preview file in root directory with Dark Theme styling.
  - Added fixed prominent top banner: `PREVIEW — CHƯA XUẤT BẢN` and `BRYAN FINTECH INTELLIGENCE — CONTROLLED PILOT`.
  - Embedded real candidate data (`window.EDITION_DATA`) enabling instant local browser viewing without CORS restrictions or local server requirements.
  - Rendered all 7 editorial sections: 5 Strategic Questions, Market Pulse (8 indicators), Core Theses, Macro-to-Micro Chains (7 stages), Payment Radar, Decision Cards, and 25 Verified News Desk events.

## 5. Automated QA & Verification
- `07_TESTS/test_phase07_r104_p1_remediation.py`:
  - Added 6 dedicated tests covering dynamic editorial synthesis, empty counter-evidence, payment demand removal, sports-only input, historical execution ID preservation, and missing timestamp rejection.
  - Full battery test pass: 119/119 automated tests (100.0%) across all 7 test suites.
