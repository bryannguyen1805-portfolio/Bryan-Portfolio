# PHASE 07 — R1.0.2 RESTORATION GUIDE

**Release Candidate:** PHASE07_R1.0.2  
**Date:** 2026-11-11  

---

### Restoration Procedure
1. Locate the backup archive:
   `02_PHASE_BACKUPS/PHASE07_R1.0.2_BACKUP/PHASE07_R1.0.2_BACKUP.zip`
2. Verify package SHA-256 checksum:
   ```bash
   shasum -a 256 02_PHASE_BACKUPS/PHASE07_R1.0.2_BACKUP/PHASE07_R1.0.2_BACKUP.zip
   ```
   Compare output against `PHASE07_R1.0.2_PACKAGE_CHECKSUMS.txt`.
3. Extract archive into a clean destination:
   ```bash
   mkdir -p /path/to/target_restore
   unzip -q 02_PHASE_BACKUPS/PHASE07_R1.0.2_BACKUP/PHASE07_R1.0.2_BACKUP.zip -d /path/to/target_restore
   ```
4. Run automated test suite:
   ```bash
   cd /path/to/target_restore
   python3 07_TESTS/test_phase06_intelligence.py
   python3 07_TESTS/test_phase07_runtime.py
   python3 07_TESTS/test_phase07_r101_remediation.py
   python3 07_TESTS/test_phase07_r102_remediation.py
   ```
   Confirm all 81 tests pass.
