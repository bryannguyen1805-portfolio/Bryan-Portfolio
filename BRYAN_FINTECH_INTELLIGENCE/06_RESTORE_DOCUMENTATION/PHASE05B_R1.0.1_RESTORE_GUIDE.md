# PHASE 05B R1.0.1 — RESTORE GUIDE

## Verification & Restoration Procedure
1. **Verify Backup Archive Integrity:**
   ```bash
   shasum -a 256 BRYAN_FINTECH_INTELLIGENCE/02_PHASE_BACKUPS/PHASE05B_R1.0.1_BACKUP/PHASE05B_ALIGNMENT_R101_TARGETED_REMEDIATION_PACKAGE.zip
   # Expected: 9d78d2950b1b68f12605a7e2b95804f3b3f5e0409ee227327ce77c18396d3222
   ```
2. **Extract Clean Copy:**
   ```bash
   mkdir -p /tmp/restore_p05b_r101
   unzip -q BRYAN_FINTECH_INTELLIGENCE/02_PHASE_BACKUPS/PHASE05B_R1.0.1_BACKUP/PHASE05B_ALIGNMENT_R101_TARGETED_REMEDIATION_PACKAGE.zip -d /tmp/restore_p05b_r101
   cd /tmp/restore_p05b_r101/PHASE05B_ALIGNMENT_R101 && shasum -a 256 -c SHA256_MANIFEST.txt
   ```
3. **Run Self-Contained QA Suite (187 Tests):**
   ```bash
   python3 /tmp/restore_p05b_r101/PHASE05B_ALIGNMENT_R101/06_TESTS/test_phase05b_engines.py
   ```
