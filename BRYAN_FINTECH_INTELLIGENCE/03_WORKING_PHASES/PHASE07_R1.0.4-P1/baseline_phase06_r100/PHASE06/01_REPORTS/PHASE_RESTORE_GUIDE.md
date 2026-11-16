# PHASE 06 — RESTORE & REPRODUCIBILITY GUIDE

## 1. Verify Phase 06 Backup Archive
```bash
shasum -a 256 BRYAN_FINTECH_INTELLIGENCE/02_PHASE_BACKUPS/PHASE06_R1.0.0_BACKUP/PHASE06_FINANCIAL_INTELLIGENCE_RELEASE_PACKAGE.zip
```

## 2. Extract and Verify All SHA-256 Checksums
```bash
mkdir -p /tmp/restore_phase06
unzip -q BRYAN_FINTECH_INTELLIGENCE/02_PHASE_BACKUPS/PHASE06_R1.0.0_BACKUP/PHASE06_FINANCIAL_INTELLIGENCE_RELEASE_PACKAGE.zip -d /tmp/restore_phase06
cd /tmp/restore_phase06/PHASE06 && shasum -a 256 -c SHA256SUMS.txt
```

## 3. Execute Self-Contained Phase 06 QA Suite (22 Tests)
```bash
python3 /tmp/restore_phase06/PHASE06/07_TESTS/test_phase06_intelligence.py
```

## 4. Re-generate Daily Edition JSON Distribution
```bash
python3 /tmp/restore_phase06/PHASE06/02_SOURCE_CODE/run_phase06_intelligence_pipeline.py
```
