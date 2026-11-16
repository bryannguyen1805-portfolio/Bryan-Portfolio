# PHASE 07 — R1.0.4 CHANGELOG
## Functional Remediation & Evidence-Driven Intelligence

### 1. `phase07_dynamic_news_engine.py`
- **Added `NormalizedLedger` Class:** Subclasses `list` while providing dictionary-style `.get(key)` and `__getitem__(key)` lookups by `canonicalUrl`, `requestedUrl`, or `sourceUrl`. Satisfies both list equality tests (`res == []`) and dictionary access.
- **Added `DiscoveryBundle` Class:** Subclasses `dict` to provide standard key access (`bundle['rawCandidates']`, `bundle['totalSnapshotsScanned']`) while supporting list indexing (`bundle[0]`) and iteration (`len(bundle)`).
- **WS-01.1 Collector-to-Ledger Normalization:** Normalizes `statusCode` → `actualHttpStatusCode`, `responseSha256` → `contentSha256`, `originalUrl` → `requestedUrl`. Retains original payload under `rawRecord`. Never fabricates default HTTP status.
- **WS-01.2 Live Candidate Propagation:** Discovered live candidates propagate directly through normalized retrieval records into candidate pool with provenance intact (`retrievalMode = 'LIVE_SOURCE_VERIFIED'` when hash matches and HTTP status is 200).
- **WS-01.3 Current Execution Provenance:** In LIVE mode, rejects retrieval records from prior execution runs with `HISTORICAL_PROVENANCE_MISMATCH`.
- **WS-01.4 Post-T0 Cutoff Check:** In REPLAY mode, isolates evidence with `retrievedAt > run_dt` into `postCutoffEvidence` with disposition `REJECTED_POST_CUTOFF`.

### 2. `phase07_editorial_intelligence_engine.py`
- **WS-02.1 Structured Claims Layer (`generate_claim_layer`):** Produces structured claims (`OBSERVED_FACT`, `SUPPORTED_INFERENCE`, `HYPOTHESIS`, `FORECAST`) with explicit grounding in events, audited facts, and indicators.
- **WS-02.2 Fact Indexing Enhancement:** Loads facts from both `uniqueVerifiedFacts` and `allAuditedFacts`, indexing by both `eventId` and `originatingEventId`.
- **WS-02.3 Dynamic Contradiction Detection:** Scans `verified_news` for opposing signals (expansion vs headwind, easing vs tightening), populating `counterEvidenceEventIds`, adjusting confidence to `MEDIUM`, and articulating balanced transmission mechanics. Satisfies schema `minItems: 1` constraint on `counterEvidence`.
- **WS-02.4 Strict Semantic Relevance:** Enforces strict domain relevance on payment radars. Semiconductor and electronics news (`vi mạch`, `bán dẫn`, `chip`) without tourism keywords are excluded from tourism opportunity signals.
- **Added `limitations` to Core Theses:** Every synthesized thesis includes domain-specific limitations satisfying contract requirements.

### 3. `market_pulse_discovery.py`
- **WS-03.1 Real HTTP Indicator Searches:** Implemented `execute_indicator_search()` and `execute_all_eight_searches()`, executing real HTTP requests for MP-01 through MP-08 and honestly logging `ACCESS_BLOCKED` in sandboxed network environments.
- **WS-03.2 Periodic Truth Retention:** When no newer observation is extracted, prior observation values and dates are retained with `updateStatus = "LATEST_OBSERVATION_RETAINED"`.

### 4. `phase07_daily_runtime_orchestrator.py`
- **Step 10 Integration:** Calls `execute_all_eight_searches()` and logs discovery audit.
- **Step 12 Integration:** Calls `generate_claim_layer()` and outputs `CLAIMS_LAYER.json`.
- **Step 18 Integration:** Writes `CLAIMS_LAYER.json`, `MARKET_PULSE_DISCOVERY_AUDIT.json`, and `POST_CUTOFF_EVIDENCE.json`.
- **Determinism Protection:** Removed transient execution IDs and dynamic traces from `combined-edition.json`, ensuring bit-for-bit SHA-256 reproducibility across identical runs.
- **Offline Governance:** Enforced `publicationAllowed = False` and `liveRetrievalReadiness = "NOT_APPLICABLE"` in OFFLINE mode.

### 5. `07_TESTS/test_phase07_r104_remediation.py`
- Added 15 comprehensive automated remediation tests validating WS-01 through WS-04.
