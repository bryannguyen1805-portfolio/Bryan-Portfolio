# PHASE 07 — R1.0.3 LIVE PROVENANCE & SOURCE INTEGRITY AUDIT
## Verification of Candidate Provenance & Fail-Closed Boundaries

- **Project:** Bryan FinTech Intelligence — MagSpread Editorial Edition
- **Release Candidate ID:** `PHASE07_R1.0.3`
- **Release Version:** `1.0.3`
- **Date:** 2026-11-11

---

## 1. Audit Scope

This audit examines the end-to-end evidence pipeline from raw candidate discovery through source verification, SHA-256 integrity, HTTP status verification, and publication timestamp attribution.

---

## 2. Key Architectural Checks & Implementations

### 2.1 Collector-to-Ledger Normalization Adapter
- **Implementation:** `Phase07DynamicNewsEngine._normalize_retrieval_ledger(live_ledger, execution_id)`
- **Capabilities Verified:**
  - Standardizes `{canonicalUrl: recordDict}` -> Normalized record with URL key.
  - Standardizes `{eventId: recordDict}` -> Normalized record with internal URL lookup.
  - Standardizes `[recordDict, ...]` -> Normalized record list.
  - Handles empty dict `{}` or empty list `[]` without raising `TypeError` or `KeyError`.
- **Field Normalization:** `requestedUrl`, `canonicalUrl`, `finalUrl`, `actualHttpStatusCode`, `executionId`, `retrievalMethod`, `responseContentType`, `contentSha256`, `retrievedAt`.

### 2.2 Execution-Specific Provenance Ledger
- In both LIVE and OFFLINE runs, an execution-specific ledger tracks every candidate's retrieval context.
- **Fail-Closed Boundary:** In LIVE mode:
  - If a candidate's canonical URL is missing from the retrieval ledger -> `REJECTED_SOURCE_UNVERIFIED (RETRIEVAL_RECORD_MISSING)`.
  - If the snapshot SHA-256 does not match `contentSha256` in the retrieval ledger -> `REJECTED_SOURCE_UNVERIFIED (CONTENT_HASH_MISMATCH)`.
  - If the HTTP response status code is missing or not 200 -> `REJECTED_SOURCE_UNVERIFIED (HTTP_STATUS_MISSING or ACCESS_BLOCKED)`.
- **Honest Mode Attribution:**
  - Historical snapshots loaded from fixtures are tagged `HISTORICAL_SNAPSHOT_LOADED` with status `OFFLINE_EVIDENCE`.
  - Under no circumstances can an offline snapshot claim `LIVE_SOURCE_VERIFIED`.

### 2.3 Publication Timestamp vs. CMS Update Timestamp
- The engine enforces a strict temporal hierarchy (`extract_publication_timestamp_hierarchy`):
  1. Original publication timestamp (`article:published_time`, `datePublished`) determines article age and 0–24h freshness ratio.
  2. CMS update timestamp (`article:modified_time`, `dateModified`) is stored separately in `cmsUpdateTimestamp` for change tracking only and is never used to artificially freshen stale news.
  3. Retrieval timestamp reflects the execution time $T_0$.

---

## 3. Audit Conclusion

The source provenance and verification subsystem strictly enforces cryptographic integrity, fail-closed security, and transparent execution tracking.
