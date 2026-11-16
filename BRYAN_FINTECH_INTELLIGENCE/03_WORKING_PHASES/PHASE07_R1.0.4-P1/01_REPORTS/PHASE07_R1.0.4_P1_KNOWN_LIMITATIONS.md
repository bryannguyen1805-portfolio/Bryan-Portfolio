# PHASE 07 — R1.0.4-P1 KNOWN LIMITATIONS

- **Release Version:** `PHASE07_R1.0.4-P1`
- **Release Status:** `RELEASE_CANDIDATE` (Internal Pilot Baseline)
- **Approved for Production:** `NO`

---

## 1. Documented Known Limitations

1. **Local Pilot Preview vs Production CDN:**
   - `magspread-preview.html` is built as a self-contained local preview embedding the daily edition candidate JSON (`window.EDITION_DATA`). In a production setting, assets would be decoupled and loaded from a secure API or static storage CDN with caching headers.
2. **Sandbox Network Restrictions for Live Market Pulse:**
   - In environments without external network egress (such as secure sandboxes or restricted servers), live HTTP search requests to external publisher search endpoints result in `ACCESS_BLOCKED`. The system handles this gracefully and honestly by logging `ACCESS_BLOCKED` in the search audit and retaining the latest verified observation under frequency-aware rules.
3. **Google Sheets Integration Remains Dry-Run Only:**
   - Live Google Sheets API writes remain strictly disabled (`liveWriteApiCalled: false`). All data staging is validated locally through 7 staging tabs.
4. **Offline Replay vs Live Wire Retargeting:**
   - While the daily runtime dynamically adapts to new inputs and mutations, replaying historical dates relies on authenticated local wire snapshots. Future phases may add automated live wire streaming.
