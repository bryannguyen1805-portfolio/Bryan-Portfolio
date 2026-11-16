# PHASE 07 — R1.0.4 RESTORE GUIDE

- **Release ID:** `PHASE07_R1.0.4`
- **Release Version:** `1.0.4`
- **Date:** 2026-11-11

---

## 1. Step-by-Step Restoration Procedure

### Step 1: Extract Backup Archive
```bash
mkdir -p /tmp/phase07_restore
unzip 02_PHASE_BACKUPS/PHASE07_R1.0.4_BACKUP/PHASE07_R1.0.4_BACKUP.zip -d /tmp/phase07_restore
cd /tmp/phase07_restore
```

### Step 2: Verify Checksums
```bash
shasum -a 256 -c PHASE07_R1.0.4_SHA256SUMS.txt
```

### Step 3: Run Consolidated Test Battery
```bash
python3 07_TESTS/test_phase06_intelligence.py
python3 07_TESTS/test_phase07_runtime.py
python3 07_TESTS/test_phase07_r101_remediation.py
python3 07_TESTS/test_phase07_r102_remediation.py
python3 07_TESTS/test_phase07_r103_remediation.py
python3 07_TESTS/test_phase07_r104_remediation.py
```
Expected result: All 113 tests PASS (100.0%).
