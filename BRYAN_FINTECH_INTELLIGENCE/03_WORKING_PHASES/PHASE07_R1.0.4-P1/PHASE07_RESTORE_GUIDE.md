# BRYAN FINTECH INTELLIGENCE — PHASE 07 R1.0.1 RESTORE & REPRODUCIBILITY GUIDE

## 1. Verify Archive Checksum
```bash
shasum -a 256 BRYAN_FINTECH_INTELLIGENCE/02_PHASE_BACKUPS/PHASE07_R1.0.1_BACKUP/PHASE07_R1.0.1_BACKUP.zip
```

## 2. Extract into a Clean Directory
```bash
mkdir -p /tmp/restore_phase07_r101
unzip -q BRYAN_FINTECH_INTELLIGENCE/02_PHASE_BACKUPS/PHASE07_R1.0.1_BACKUP/PHASE07_R1.0.1_BACKUP.zip -d /tmp/restore_phase07_r101
cd /tmp/restore_phase07_r101/PHASE07_R1.0.1
```

## 3. Verify All File Checksums
```bash
shasum -a 256 -c PHASE07_SHA256SUMS.txt
```

## 4. Re-run All 63 Automated Tests
```bash
# 1. Run R1.0.1 Targeted Remediation Tests (19 tests)
python3 07_TESTS/test_phase07_r101_remediation.py

# 2. Run Phase 07 Runtime Tests (22 tests)
python3 07_TESTS/test_phase07_runtime.py

# 3. Run Inherited Phase 06 Tests (22 tests)
python3 07_TESTS/test_phase06_intelligence.py
```

## 5. Execute Daily Runtime Orchestrator
```bash
# Offline execution for pilot edition
python3 02_SOURCE_CODE/phase07_daily_runtime_orchestrator.py --mode OFFLINE --date 2026-11-11 --edition ED-20261111-D01 --timestamp 2026-11-11T02:20:00+07:00

# Live execution for current day
python3 02_SOURCE_CODE/phase07_daily_runtime_orchestrator.py --mode LIVE
```
