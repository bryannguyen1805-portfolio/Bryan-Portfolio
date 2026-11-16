# PHASE 07 — R1.0.2 KNOWN LIMITATIONS

**Release Candidate:** PHASE07_R1.0.2  
**Date:** 2026-11-11  

---

1. **Controlled Pilot Mode & Offline Fallback**
   In sandbox or network-restricted environments, live web crawlers fall back to verified disk snapshots. All retrieved snapshots are validated against SHA-256 ledgers.

2. **Data Freshness Shortfall Gate**
   The daily orchestrator enforces a 25-event quota and 80% 0–24h freshness requirement. When executed against older snapshot sets without adjusting T0, Step 09 correctly fails-closed (`DATA_SHORTFALL_OR_UNVERIFIED`).

3. **Market Pulse Indicator Staleness (MP-02)**
   MP-02 (Overnight Interbank Rate) observation of 2.8 %/năm (2026-10-02) exceeds the canonical 72.0-hour freshness ceiling and is correctly flagged as `STALE_OBSERVATION` / `UNVERIFIED`.

4. **Qualitative-Only Market Indicators (MP-05 & MP-06)**
   MP-05 (Credit Growth) and MP-06 (VietQR Volume) are published periodically by authorities. In daily runs without new quantitative releases, they are retained as `QUALITATIVE_UPDATE_ONLY` / `UNVERIFIED` with `actualValue: null`.

5. **Historical Operations Disclosure (MP-08)**
   MP-08 reflects the latest verified SBV net injection of 47,915 tỷ VND from 2026-09-21 and is explicitly disclosed with its observation date.

6. **Production Deployment Restrictions**
   Automated cron execution, automatic email transmission, and live Google Sheets API writes remain strictly disabled (`productionStatus: NOT_APPROVED`).
