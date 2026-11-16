# PHASE 07 — R1.0.3 KNOWN LIMITATIONS & OPERATIONAL BOUNDARIES
## Technical Constraints & Environmental Preconditions

- **Release Candidate ID:** `PHASE07_R1.0.3`
- **Release Version:** `1.0.3`
- **Date:** 2026-11-11

---

## 1. Network & Live Retrieval Preconditions
- **Sandboxed Execution Policy:** In standard sandbox mode, network access is restricted. Live web crawling and HTTP retrieval require explicit user approval (`BypassSandbox: true`) or an authorized proxy environment.
- **Fail-Closed Retrieval:** When network access is unavailable in `LIVE` mode, the engine strictly fails closed (`RETRIEVAL_RECORD_MISSING` or `ACCESS_BLOCKED`) and refuses to publish unverified candidates.
- **Offline Snapshot Dependency:** In `OFFLINE` mode, the orchestrator depends on valid pre-staged snapshot fixtures located in `04_RAW_EVIDENCE/`.

## 2. Temporal & Freshness Constraints
- **72-Hour Maximum Age Ceiling:** Articles older than 72 hours from execution timestamp $T_0$ are disqualified as stale. If fewer than 25 events pass the window or 0–24h ratio is under 80%, the Quota Gate blocks publication honestly (`SHORTFALL_GATE_BLOCKED`).
- **Original Publication Timestamp vs. CMS Modified Timestamp:** The engine strictly ranks by the authentic original publication timestamp. Sites that only expose a CMS modified date without original timestamp are subject to fallback hierarchy rules.

## 3. Market Pulse Frequency Bounds
- **Monthly Indicators (MP-02, MP-04, MP-07):** Monthly statistics (e.g. credit growth, inflation, tourist arrivals) are published at monthly intervals by GSO/SBV. When running on intermediate days, the system retains the latest published observation and marks its status frequency-aware (`STALE_OBSERVATION` or `PERIODIC_HISTORICAL`) rather than fabricating interim numbers.

## 4. Google Sheets Staging
- **Dry-Run Mode Exclusivity:** The system produces full Google Sheets payloads (`PHASE07_GOOGLE_SHEETS_PREVIEW.json` and `PHASE07_GOOGLE_SHEETS_VALIDATION.json`) with zero live writes (`liveWriteApiCalled = false`). Live writing requires Google Service Account OAuth2 credentials and explicit safety unlock.

## 5. Production Prohibition
- Automated operating system crontabs, public GitHub push, external email dispatch, and production server deployment are strictly prohibited in this phase.
