# PHASE 07 — R1.0.4-P1 DISASTER RECOVERY & RESTORE GUIDE

- **Release Version:** `PHASE07_R1.0.4-P1`
- **Release Status:** `RELEASE_CANDIDATE` (Pilot Baseline)
- **Archive Path:** `02_PHASE_BACKUPS/PHASE07_R1.0.4-P1_BACKUP/PHASE07_R1.0.4_P1_BACKUP.zip`

---

## 1. Quick Verification & Restore Procedure

```bash
# 1. Verify ZIP Integrity & Checksum
shasum -a 256 02_PHASE_BACKUPS/PHASE07_R1.0.4-P1_BACKUP/PHASE07_R1.0.4_P1_BACKUP.zip

# 2. Extract Archive into Target Clean Workspace
mkdir -p /tmp/phase07_r104_p1_restored
unzip -q 02_PHASE_BACKUPS/PHASE07_R1.0.4-P1_BACKUP/PHASE07_R1.0.4_P1_BACKUP.zip -d /tmp/phase07_r104_p1_restored

# 3. Verify Internal SHA-256 Manifest
cd /tmp/phase07_r104_p1_restored
shasum -a 256 -c PHASE07_R1.0.4_P1_SHA256SUMS.txt

# 4. Run Complete 7-Suite Automated Quality Assurance Battery (119 Tests)
python3 07_TESTS/test_phase06_intelligence.py
python3 07_TESTS/test_phase07_runtime.py
python3 07_TESTS/test_phase07_r101_remediation.py
python3 07_TESTS/test_phase07_r102_remediation.py
python3 07_TESTS/test_phase07_r103_remediation.py
python3 07_TESTS/test_phase07_r104_remediation.py
python3 07_TESTS/test_phase07_r104_p1_remediation.py

# 5. Launch MagSpread Standalone Pilot Preview
open magspread-preview.html
```
