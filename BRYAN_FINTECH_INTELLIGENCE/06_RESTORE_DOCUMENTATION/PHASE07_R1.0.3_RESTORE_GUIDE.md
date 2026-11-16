# PHASE 07 — R1.0.3 DISASTER RECOVERY & RESTORE GUIDE
## Step-by-Step Restoration in a Clean Environment

- **Release Candidate ID:** `PHASE07_R1.0.3`
- **Release Version:** `1.0.3`
- **Parent Accepted Release:** `PHASE06_R1.0.0`
- **Date:** 2026-11-11

---

## 1. Prerequisites
- Python 3.9+ (Python 3.10+ recommended)
- Standard Unix utilities (`unzip`, `sha256sum` or `shasum -a 256`)
- Clean target directory with write permissions

---

## 2. Restoration Procedure

### Step 1: Verify Archive Integrity Before Extraction
```bash
# Verify the backup ZIP against its official recorded hash
shasum -a 256 02_PHASE_BACKUPS/PHASE07_R1.0.3_BACKUP/PHASE07_R1.0.3_BACKUP.zip
# Or verify release candidate
shasum -a 256 04_RELEASE_CANDIDATES/PHASE07_R1.0.3/PHASE07_R1.0.3_RELEASE_CANDIDATE.zip
```

### Step 2: Extract Archive into Destination Workspace
```bash
mkdir -p /path/to/target/PHASE07_R1.0.3
unzip -q 02_PHASE_BACKUPS/PHASE07_R1.0.3_BACKUP/PHASE07_R1.0.3_BACKUP.zip -d /path/to/target/PHASE07_R1.0.3
cd /path/to/target/PHASE07_R1.0.3
```

### Step 3: Verify Internal SHA-256 Manifest
```bash
shasum -a 256 -c PHASE07_R1.0.3_SHA256SUMS.txt
```

### Step 4: Execute Complete Automated Test Battery
```bash
python3 -c "
import subprocess, sys
suites = [
    '07_TESTS/test_phase06_intelligence.py',
    '07_TESTS/test_phase07_runtime.py',
    '07_TESTS/test_phase07_r101_remediation.py',
    '07_TESTS/test_phase07_r102_remediation.py',
    '07_TESTS/test_phase07_r103_remediation.py'
]
for s in suites:
    ret = subprocess.run([sys.executable, s]).returncode
    if ret != 0:
        print(f'FAILED: {s}')
        sys.exit(1)
print('ALL 98 TESTS PASSED!')
"
```

### Step 5: Execute Test Run of Daily Orchestrator
```bash
python3 02_SOURCE_CODE/phase07_daily_runtime_orchestrator.py \
  --mode OFFLINE \
  --date 2026-11-10 \
  --edition ED-20261110-D01 \
  --timestamp 2026-11-10T22:30:00+07:00
```
Expected output:
```
================================================================================
PHASE 07 DAILY RUNTIME ORCHESTRATOR: PASS
Edition: ED-20261110-D01 (2026-11-10) | Publication Allowed: False
Steps Passed: 20/20
================================================================================
```
Restoration is confirmed 100% operational.
