# PHASE 06 DISASTER RECOVERY & RESTORE GUIDE

**Release ID:** `PHASE06_R1.0.0`  
**Status:** `ACCEPTED_BY_PROJECT_OWNER`  
**Archive SHA-256:** `d2f8672ff07bad36c9811906f69977a6d716de73d6685d874bd6a5ca53510bc9`  
**Created:** `2026-11-11T01:03:31.767048+07:00`  

---

## 1. Primary Archive Locations

- **Accepted Primary Release:**  
  `BRYAN_FINTECH_INTELLIGENCE/01_ACCEPTED_PHASES/PHASE06_R1.0.0/PHASE06_R1.0.0_ACCEPTED_RELEASE.zip`
- **Permanent Backup:**  
  `BRYAN_FINTECH_INTELLIGENCE/02_PHASE_BACKUPS/PHASE06_R1.0.0_BACKUP/PHASE06_R1.0.0_BACKUP.zip`

---

## 2. Step-by-Step Restoration Procedure

### Step 1: Verify Checksum Prior to Unpacking
```bash
shasum -a 256 BRYAN_FINTECH_INTELLIGENCE/01_ACCEPTED_PHASES/PHASE06_R1.0.0/PHASE06_R1.0.0_ACCEPTED_RELEASE.zip
# Expected: d2f8672ff07bad36c9811906f69977a6d716de73d6685d874bd6a5ca53510bc9
```

### Step 2: Extract to Target Workspace
```bash
unzip -q BRYAN_FINTECH_INTELLIGENCE/01_ACCEPTED_PHASES/PHASE06_R1.0.0/PHASE06_R1.0.0_ACCEPTED_RELEASE.zip -d /tmp/restore_p06
```

### Step 3: Verify 1,502 Manifest Entries
```bash
cd /tmp/restore_p06/PHASE06
shasum -a 256 -c SHA256SUMS.txt | grep -v 'OK$'
# Must output zero lines (100% OK)
```

### Step 4: Re-run Automated QA Test Suite
```bash
python3 /tmp/restore_p06/PHASE06/07_TESTS/test_phase06_intelligence.py
# Must show 22/22 PASSED (100%)
```

### Step 5: Verify Critical JSON Outputs
- `04_INTELLIGENCE_OUTPUTS/AUDITED_FINANCIAL_FACTS.json` (16 unique verified facts)
- `04_INTELLIGENCE_OUTPUTS/CORE_THESIS.json` (4 core theses)
- `04_INTELLIGENCE_OUTPUTS/MACRO_TO_MICRO.json` (4 transmission chains)
- `04_INTELLIGENCE_OUTPUTS/PAYMENT_RADAR.json` (5 radar signals)
- `04_INTELLIGENCE_OUTPUTS/FINANCIAL_DECISION_INTELLIGENCE.json` (4 decision cards)
- `05_GOOGLE_SHEETS_DRY_RUN/GOOGLE_SHEETS_PREVIEW.json` (155 preserved + 83 proposed = 238 rows)
- `06_DAILY_EDITIONS/daily-editions/2026-11-10/combined-edition.json` (sealed edition)
