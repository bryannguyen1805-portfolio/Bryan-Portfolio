# PHASE 07 — R1.0.4 KNOWN LIMITATIONS & OPERATIONAL NOTES

- **Release ID:** `PHASE07_R1.0.4`
- **Release Version:** `1.0.4`
- **Release Status:** RELEASE_CANDIDATE
- **Production Status:** NOT_APPROVED (Controlled Engineering Pilot Only)
- **Date:** 2026-11-11

---

## 1. Operational & Sandbox Boundaries

1. **Sandboxed Network Environment:**
   - In sandboxed execution environments, outbound HTTP requests to publisher sites and government portals are blocked by host isolation.
   - The engine logs these attempts honestly as `ACCESS_BLOCKED` and falls back to authenticated raw wire snapshots without fabricating data.

2. **Daily Publication Quota & News Freshness:**
   - The pilot snapshot `ED-20261110-D01` contains 18 verified unique news events (16 in the 0–24h window, 88.9% freshness ratio).
   - Because the 25-event quota is not met, the publication gate correctly sets `publicationAllowed: false` and logs an honest shortfall report. The engine refuses to fabricate events to fill quotas.

3. **Market Pulse Periodic Truth:**
   - MP-02 (Overnight Interbank Rate: 2.8%/năm on 2026-10-02) exceeds the 72.0h freshness window and is retained as `STALE_OBSERVATION` / `UNVERIFIED`.
   - MP-05 (Credit Growth) and MP-06 (VietQR Volume) carry qualitative policy updates (`QUALITATIVE_UPDATE_ONLY`, `actualValue: null`).
   - MP-08 reflects the verified 2026-09-21 OMO operation (47,915 tỷ VND) and retains its original observation date.

4. **Production Deployment Prohibitions:**
   - Production deployment, automated cron scheduling, email dispatch, git push, and Google Sheets live write API remain strictly disabled (`productionStatus: NOT_APPROVED`, all 5 safety locks `False`).
