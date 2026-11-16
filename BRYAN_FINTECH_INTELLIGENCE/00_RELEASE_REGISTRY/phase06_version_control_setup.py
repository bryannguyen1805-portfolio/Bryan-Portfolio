#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
phase06_version_control_setup.py
================================
Implements Section XIV — Mandatory Phase Version Control, Release Archiving & Backup Policy
for Bryan FinTech Intelligence before executing Phase 06 Workstreams A–F.

Responsibilities:
1. Establishes the standard project release directory structure under BRYAN_FINTECH_INTELLIGENCE/:
   - 00_RELEASE_REGISTRY/
   - 01_ACCEPTED_PHASES/
   - 02_PHASE_BACKUPS/
   - 03_WORKING_PHASES/
   - 04_RELEASE_CANDIDATES/
   - 05_RELEASE_MANIFESTS/
   - 06_RESTORE_DOCUMENTATION/
2. Preserves the accepted Phase 05B R1.0.1 package (PHASE05B_ALIGNMENT_R101_TARGETED_REMEDIATION_PACKAGE.zip)
   into 01_ACCEPTED_PHASES/PHASE05B_R1.0.1/ without modifying the original file.
3. Creates a complete backup in 02_PHASE_BACKUPS/PHASE05B_R1.0.1_BACKUP/ and executes the 6-step
   Backup Verification protocol (Section XIV.G).
4. Extracts the accepted Phase 05B R1.0.1 baseline into 03_WORKING_PHASES/PHASE06/baseline_phase05b_r101/
   and initializes the Phase 06 working directory structure.
5. Writes the immutable release manifests, handoff documents, restore guides, and release registry.
"""

import os
import sys
import json
import shutil
import zipfile
import hashlib
from datetime import datetime, timezone, timedelta

VN_TZ = timezone(timedelta(hours=7))
WORKSPACE_ROOT = "/Users/quangtri/Documents/Bryan-Portfolio-Antigravity"
BFI_ROOT = os.path.join(WORKSPACE_ROOT, "BRYAN_FINTECH_INTELLIGENCE")

ORIG_P05B_DIR = os.path.join(
    WORKSPACE_ROOT,
    "pilot-output",
    "phase05-operational-readiness",
    "phase05b-intelligence-engine"
)
ORIG_P05B_ZIP = os.path.join(
    ORIG_P05B_DIR,
    "PHASE05B_ALIGNMENT_R101_TARGETED_REMEDIATION_PACKAGE.zip"
)


def compute_sha256(filepath: str) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def verify_manifest_in_dir(target_dir: str, manifest_path: str) -> dict:
    total = 0
    matched = 0
    mismatches = []
    with open(manifest_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split("  ", 1)
            if len(parts) != 2:
                continue
            expected_sha, rel_path = parts
            total += 1
            abs_p = os.path.join(target_dir, rel_path)
            if not os.path.exists(abs_p):
                mismatches.append({"path": rel_path, "error": "MISSING_FILE"})
                continue
            actual_sha = compute_sha256(abs_p)
            if actual_sha == expected_sha:
                matched += 1
            else:
                mismatches.append({
                    "path": rel_path,
                    "expected": expected_sha,
                    "actual": actual_sha
                })
    return {
        "totalEntries": total,
        "matchedEntries": matched,
        "mismatchCount": len(mismatches),
        "mismatches": mismatches,
        "verified": (total > 0 and matched == total and len(mismatches) == 0)
    }


def main():
    now_iso = datetime.now(VN_TZ).isoformat()
    print("=" * 78)
    print("BRYAN FINTECH INTELLIGENCE — PHASE VERSION CONTROL & BASELINE INHERITANCE")
    print(f"Execution Timestamp: {now_iso}")
    print("=" * 78)

    # 1. Verify original Phase 05B R1.0.1 accepted package exists
    if not os.path.exists(ORIG_P05B_ZIP):
        raise FileNotFoundError(f"Missing accepted Phase 05B baseline zip: {ORIG_P05B_ZIP}")

    orig_zip_sha256 = compute_sha256(ORIG_P05B_ZIP)
    orig_zip_size = os.path.getsize(ORIG_P05B_ZIP)
    print(f"[1] Located Accepted Baseline: {ORIG_P05B_ZIP}")
    print(f"    SHA-256: {orig_zip_sha256} ({orig_zip_size:,} bytes)")

    # 2. Create Standard Project Directory Structure
    std_dirs = [
        "00_RELEASE_REGISTRY",
        "01_ACCEPTED_PHASES/PHASE05B_R1.0.1",
        "02_PHASE_BACKUPS/PHASE05B_R1.0.1_BACKUP",
        "03_WORKING_PHASES/PHASE06",
        "04_RELEASE_CANDIDATES/PHASE06",
        "05_RELEASE_MANIFESTS",
        "06_RESTORE_DOCUMENTATION",
    ]
    for sd in std_dirs:
        os.makedirs(os.path.join(BFI_ROOT, sd), exist_ok=True)
    print("[2] Initialized standard BRYAN_FINTECH_INTELLIGENCE/ directory structure.")

    # 3. Populate 01_ACCEPTED_PHASES/PHASE05B_R1.0.1/
    accepted_dir = os.path.join(BFI_ROOT, "01_ACCEPTED_PHASES", "PHASE05B_R1.0.1")
    accepted_zip = os.path.join(
        accepted_dir,
        "PHASE05B_ALIGNMENT_R101_TARGETED_REMEDIATION_PACKAGE.zip"
    )
    shutil.copy2(ORIG_P05B_ZIP, accepted_zip)

    # Extract into 01_ACCEPTED_PHASES/PHASE05B_R1.0.1/extracted/
    accepted_extracted_root = os.path.join(accepted_dir, "extracted")
    if os.path.exists(accepted_extracted_root):
        shutil.rmtree(accepted_extracted_root)
    os.makedirs(accepted_extracted_root, exist_ok=True)
    with zipfile.ZipFile(accepted_zip, "r") as zf:
        zf.extractall(accepted_extracted_root)

    accepted_pkg_inner = os.path.join(accepted_extracted_root, "PHASE05B_ALIGNMENT_R101")
    manifest_check_accepted = verify_manifest_in_dir(
        accepted_pkg_inner,
        os.path.join(accepted_pkg_inner, "SHA256_MANIFEST.txt")
    )
    if not manifest_check_accepted["verified"]:
        raise RuntimeError(f"Accepted Phase 05B manifest check failed: {manifest_check_accepted}")
    print(f"[3] Archived accepted Phase 05B R1.0.1 in 01_ACCEPTED_PHASES/PHASE05B_R1.0.1/ "
          f"({manifest_check_accepted['matchedEntries']}/{manifest_check_accepted['totalEntries']} SHA-256 verified).")

    # Generate required Phase 05B Release Governance Metadata in 01_ACCEPTED_PHASES/PHASE05B_R1.0.1/
    p05b_release_manifest = {
        "phaseId": "PHASE05B",
        "releaseId": "PHASE05B_R1.0.1",
        "releaseVersion": "1.0.1-FINAL-DATA-INTEGRITY-PATCH",
        "executionId": "PHASE05B_ALIGNMENT_R101_FINAL_PATCH",
        "editionId": "ED-20261110-D01",
        "generatedTimestamp": "2026-11-10T23:32:07+07:00",
        "archivedTimestamp": now_iso,
        "parentBaselineReleaseId": "PHASE05B_R1.3A.3",
        "packageFileName": "PHASE05B_ALIGNMENT_R101_TARGETED_REMEDIATION_PACKAGE.zip",
        "packageSha256": orig_zip_sha256,
        "packageSizeBytes": orig_zip_size,
        "sourceCodeVersion": "3.0.4-r101",
        "dataContractVersion": "3.0.4",
        "testResults": {
            "totalTests": 187,
            "passedTests": 187,
            "failedTests": 0,
            "passRatePercent": 100.0,
            "reproducibleFromExtractedPackage": True
        },
        "releaseStatus": "ACCEPTED_BY_PROJECT_OWNER",
        "readinessClassification": {
            "engineeringReadiness": "ENGINEERING_PASS",
            "liveRetrievalReadiness": "LIVE_RETRIEVAL_PASS",
            "dailyEditionReadiness": "DATA_SHORTFALL_OR_UNVERIFIED",
            "productionApprovalStatus": "NOT_PRODUCTION_APPROVED"
        },
        "knownLimitations": [
            "Verified unique news events count is 18 (16 in 0-24h window, 88.9% freshness ratio), below the 25-event daily publication quota.",
            "MP-02 (Overnight interbank interest rate) latest verified observation is 2.8 %/năm on 2026-10-02 (exceeding the canonical 72.0h ceiling; marked STALE_OBSERVATION / UNVERIFIED).",
            "MP-05 (System-wide credit growth) and MP-06 (VietQR transaction volume) have qualitative policy/industry updates only (QUALITATIVE_UPDATE_ONLY / UNVERIFIED, actualValue: null, observationDate: null).",
            "MP-08 (OMO net liquidity injection) reflects the latest verified operation on 2026-09-21 (47,915 tỷ VND) and must not be represented as a current-day operation.",
            "Production deployment, cron scheduling, and Google Sheets live write API remain strictly disabled."
        ]
    }
    with open(os.path.join(accepted_dir, "PHASE_RELEASE_MANIFEST.json"), "w", encoding="utf-8") as f:
        json.dump(p05b_release_manifest, f, ensure_ascii=False, indent=2)
    with open(os.path.join(BFI_ROOT, "05_RELEASE_MANIFESTS", "PHASE05B_R1.0.1_RELEASE_MANIFEST.json"), "w", encoding="utf-8") as f:
        json.dump(p05b_release_manifest, f, ensure_ascii=False, indent=2)

    # Copy standard release markdown files into 01_ACCEPTED_PHASES/PHASE05B_R1.0.1/
    shutil.copy2(os.path.join(accepted_pkg_inner, "00_EXECUTIVE_SUMMARY.md"),
                 os.path.join(accepted_dir, "PHASE_FINAL_EXECUTION_REPORT.md"))
    shutil.copy2(os.path.join(accepted_pkg_inner, "01_REPORTS", "PHASE05B_R101_FINAL_GO_NO_GO.md"),
                 os.path.join(accepted_dir, "PHASE_GO_NO_GO.md"))
    shutil.copy2(os.path.join(accepted_pkg_inner, "01_REPORTS", "CHANGELOG.md"),
                 os.path.join(accepted_dir, "PHASE_CHANGELOG.md"))
    shutil.copy2(os.path.join(accepted_pkg_inner, "SHA256_MANIFEST.txt"),
                 os.path.join(accepted_dir, "SHA256SUMS.txt"))

    p05b_limitations_md = """# PHASE 05B R1.0.1 — KNOWN LIMITATIONS & ACCEPTANCE CONDITIONS

**Release ID:** `PHASE05B_R1.0.1`  
**Release Status:** `ACCEPTED_BY_PROJECT_OWNER` (Engineering Baseline for Phase 06)  
**Production Status:** `STRICTLY DISABLED` (Not Production Approved)

## 1. Data & Quota Limitations Inherited by Phase 06
1. **News Quota Shortfall (`18 / 25` Verified Unique Events):**
   - Total verified unique events: `18` (`16` within `0-24h` window = `88.9%` freshness; `1` in `24-48h`; `1` in `48-72h`).
   - Because `16 < 25` required for `0-24h` publication, the edition is classified as `DATA_SHORTFALL_OR_UNVERIFIED` (Internal Pilot / Preview Only) and must never be declared a complete production Daily Edition.
2. **Market Pulse Indicator States (`MARKET_PULSE_8.json`):**
   - `MP-01` (`25600 VND/USD`, `2026-11-10`): `NUMERIC_VALUE_VERIFIED` / `VERIFIED`
   - `MP-02` (`2.8 %/năm`, `2026-10-02`): `STALE_OBSERVATION` / `UNVERIFIED` (exceeds 72.0h ceiling; age 942.5h)
   - `MP-03` (`7 %/năm`, `2026-11-10`): `NUMERIC_VALUE_VERIFIED` / `VERIFIED`
   - `MP-04` (`1743.00 Điểm`, `2026-11-10`): `NUMERIC_VALUE_VERIFIED` / `VERIFIED`
   - `MP-05` (`null`, `observationDate: null`): `QUALITATIVE_UPDATE_ONLY` / `UNVERIFIED`
   - `MP-06` (`null`, `observationDate: null`): `QUALITATIVE_UPDATE_ONLY` / `UNVERIFIED`
   - `MP-07` (`19.5 triệu lượt`, `2026-10-31`): `NUMERIC_VALUE_VERIFIED` / `VERIFIED`
   - `MP-08` (`47915 tỷ VND`, `2026-09-21`): `NUMERIC_VALUE_VERIFIED` / `VERIFIED` (historical OMO operation on 21/09/2026; must not be described as current-day liquidity).
"""
    with open(os.path.join(accepted_dir, "PHASE_KNOWN_LIMITATIONS.md"), "w", encoding="utf-8") as f:
        f.write(p05b_limitations_md)

    p05b_handoff_md = """# PHASE 05B R1.0.1 → PHASE 06 HANDOFF DOCUMENT

**From Phase:** `PHASE05B_R1.0.1` (`ACCEPTED_BY_PROJECT_OWNER`)  
**To Phase:** `PHASE06` (`Financial Intelligence Layer & Daily Decision Engine`)  
**Parent Package SHA-256:** `""" + orig_zip_sha256 + """`

## 1. What Was Completed & Accepted in Phase 05B R1.0.1
- Multi-source live HTTP News Collector (`daily_news_collector_v3.py`) with 32 discovered candidates and 100% disposition accounting.
- Byte-exact Source Verification & Gzip Evidence Decompression (`source_verification_engine_v3.py`) with 21/21 verified articles.
- Semantic Deduplication (`semantic_dedup_engine_v3.py`) yielding 18 unique verified news events (`VERIFIED_NEWS_DATABASE.json`).
- Semantic Financial Fact Extraction (`P0-04`) and Country-Entity Binding (`P0-01` for `MP-07` Vietnam 19.5M arrivals).
- Canonical Indicator Configuration (`03_INDICATOR_CONFIG/market_pulse_indicator_specs.json`) with fail-closed validation (`P0-02`).
- 187/187 automated QA tests passing directly from the extracted package (`06_TESTS/test_phase05b_engines.py`).

## 2. Files Inherited by Phase 06 (Read-Only Baseline)
- `05_LIVE_DATA/VERIFIED_NEWS_DATABASE.json` (18 verified unique news events, 18 extracted financial facts)
- `05_LIVE_DATA/MARKET_PULSE_8.json` (8 canonical indicators with preserved `observationDate` and `verificationStatus`)
- `05_LIVE_DATA/PHASE05B_PROVENANCE_LEDGER.json` & `PHASE05B_CANDIDATE_DISPOSITION_LEDGER.json`
- `03_INDICATOR_CONFIG/market_pulse_indicator_specs.json` & `PHASE05_DATA_CONTRACT_V3_0_4.json`
- `04_RAW_EVIDENCE/` (680 raw HTML/Gzip evidence snapshots)

## 3. Protected Files & Boundaries
- Never modify `index.html`, `fintech-intelligence/index.html`, `fintech-intelligence/app.js`, `pilot-output/checkpoint-04-internal-baseline/`, or the archived `PHASE05B_R1.0.1` release.
- Never invoke Google Sheets live write APIs, deploy to production, or activate cron jobs.
"""
    with open(os.path.join(accepted_dir, "PHASE_HANDOFF.md"), "w", encoding="utf-8") as f:
        f.write(p05b_handoff_md)

    p05b_restore_md = """# PHASE 05B R1.0.1 — RESTORE GUIDE

## Verification & Restoration Procedure
1. **Verify Backup Archive Integrity:**
   ```bash
   shasum -a 256 BRYAN_FINTECH_INTELLIGENCE/02_PHASE_BACKUPS/PHASE05B_R1.0.1_BACKUP/PHASE05B_ALIGNMENT_R101_TARGETED_REMEDIATION_PACKAGE.zip
   # Expected: """ + orig_zip_sha256 + """
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
"""
    with open(os.path.join(accepted_dir, "PHASE_RESTORE_GUIDE.md"), "w", encoding="utf-8") as f:
        f.write(p05b_restore_md)
    with open(os.path.join(BFI_ROOT, "06_RESTORE_DOCUMENTATION", "PHASE05B_R1.0.1_RESTORE_GUIDE.md"), "w", encoding="utf-8") as f:
        f.write(p05b_restore_md)

    # 4. Create & Verify Complete Backup in 02_PHASE_BACKUPS/PHASE05B_R1.0.1_BACKUP/
    backup_dir = os.path.join(BFI_ROOT, "02_PHASE_BACKUPS", "PHASE05B_R1.0.1_BACKUP")
    backup_zip = os.path.join(
        backup_dir,
        "PHASE05B_ALIGNMENT_R101_TARGETED_REMEDIATION_PACKAGE.zip"
    )
    shutil.copy2(accepted_zip, backup_zip)
    backup_zip_sha256 = compute_sha256(backup_zip)

    # Test extraction of backup (Section XIV.G)
    backup_test_extract = os.path.join(backup_dir, "verified_extraction")
    if os.path.exists(backup_test_extract):
        shutil.rmtree(backup_test_extract)
    os.makedirs(backup_test_extract, exist_ok=True)

    with zipfile.ZipFile(backup_zip, "r") as zf:
        bad_file = zf.testzip()
        assert bad_file is None, f"Corrupted file in backup zip: {bad_file}"
        zf.extractall(backup_test_extract)

    backup_pkg_inner = os.path.join(backup_test_extract, "PHASE05B_ALIGNMENT_R101")
    backup_manifest_check = verify_manifest_in_dir(
        backup_pkg_inner,
        os.path.join(backup_pkg_inner, "SHA256_MANIFEST.txt")
    )
    assert backup_manifest_check["verified"], f"Backup manifest verification failed: {backup_manifest_check}"

    # Verify critical source files and JSON outputs in backup
    critical_files = [
        "02_SOURCE_CODE/market_pulse_extractor.py",
        "02_SOURCE_CODE/market_pulse_validator.py",
        "02_SOURCE_CODE/market_pulse_discovery.py",
        "02_SOURCE_CODE/daily_news_collector_v3.py",
        "02_SOURCE_CODE/source_verification_engine_v3.py",
        "03_INDICATOR_CONFIG/market_pulse_indicator_specs.json",
        "03_INDICATOR_CONFIG/PHASE05_DATA_CONTRACT_V3_0_4.json",
        "05_LIVE_DATA/MARKET_PULSE_8.json",
        "05_LIVE_DATA/VERIFIED_NEWS_DATABASE.json",
        "06_TESTS/test_phase05b_engines.py"
    ]
    critical_file_hashes = {}
    for cf in critical_files:
        cf_abs = os.path.join(backup_pkg_inner, cf)
        assert os.path.exists(cf_abs), f"Critical file missing in backup: {cf}"
        critical_file_hashes[cf] = compute_sha256(cf_abs)

    # Confirm original accepted release remains unchanged
    orig_after_sha256 = compute_sha256(ORIG_P05B_ZIP)
    assert orig_after_sha256 == orig_zip_sha256 == backup_zip_sha256, "Original or backup SHA-256 mismatch!"

    backup_verification_report = {
        "verifiedAt": now_iso,
        "releaseId": "PHASE05B_R1.0.1",
        "originalArchivePath": ORIG_P05B_ZIP,
        "originalArchiveSha256": orig_after_sha256,
        "originalUnchanged": (orig_after_sha256 == orig_zip_sha256),
        "backupArchivePath": backup_zip,
        "backupArchiveSha256": backup_zip_sha256,
        "archiveOpensCleanly": True,
        "manifestVerification": backup_manifest_check,
        "criticalFilesVerified": critical_file_hashes,
        "verificationStatus": "BACKUP_VERIFIED_PASS"
    }
    with open(os.path.join(backup_dir, "BACKUP_VERIFICATION_REPORT.json"), "w", encoding="utf-8") as f:
        json.dump(backup_verification_report, f, ensure_ascii=False, indent=2)
    print(f"[4] Verified backup in 02_PHASE_BACKUPS/PHASE05B_R1.0.1_BACKUP/ (SHA-256 match: {backup_zip_sha256}).")

    # 5. Extract Accepted Baseline into 03_WORKING_PHASES/PHASE06/
    p06_working_dir = os.path.join(BFI_ROOT, "03_WORKING_PHASES", "PHASE06")
    p06_baseline_dir = os.path.join(p06_working_dir, "baseline_phase05b_r101")
    if os.path.exists(p06_baseline_dir):
        shutil.rmtree(p06_baseline_dir)
    os.makedirs(p06_baseline_dir, exist_ok=True)
    with zipfile.ZipFile(accepted_zip, "r") as zf:
        zf.extractall(p06_baseline_dir)

    # Create Phase 06 modular subdirectories
    p06_subdirs = [
        "01_REPORTS",
        "02_SOURCE_CODE",
        "03_SCHEMAS_AND_CONFIG",
        "04_INTELLIGENCE_OUTPUTS",
        "05_GOOGLE_SHEETS_DRY_RUN",
        "06_DAILY_EDITIONS",
        "07_TESTS",
        "08_CHECKSUMS",
    ]
    for d in p06_subdirs:
        os.makedirs(os.path.join(p06_working_dir, d), exist_ok=True)

    # Also copy Phase 04B 7-tab staging tables (read-only snapshot of the 155 existing records)
    p04b_staging_src = os.path.join(WORKSPACE_ROOT, "pilot-output", "phase04b-sheets-staging", "staging_tables.json")
    p04b_summary_src = os.path.join(WORKSPACE_ROOT, "pilot-output", "phase04b-sheets-staging", "staging_sync_summary.json")
    p04b_schema_src = os.path.join(WORKSPACE_ROOT, "pilot-output", "phase04b-sheets-staging", "sheets_schema.py")
    if os.path.exists(p04b_staging_src):
        shutil.copy2(p04b_staging_src, os.path.join(p06_working_dir, "03_SCHEMAS_AND_CONFIG", "phase04b_staging_tables_readonly.json"))
    if os.path.exists(p04b_summary_src):
        shutil.copy2(p04b_summary_src, os.path.join(p06_working_dir, "03_SCHEMAS_AND_CONFIG", "phase04b_staging_sync_summary_readonly.json"))
    if os.path.exists(p04b_schema_src):
        shutil.copy2(p04b_schema_src, os.path.join(p06_working_dir, "02_SOURCE_CODE", "sheets_schema.py"))

    # Record Phase 06 Baseline Inheritance Manifest
    p06_inheritance_manifest = {
        "phaseId": "PHASE06",
        "phaseName": "Financial Intelligence Layer & Daily Decision Engine",
        "releaseStatus": "IN_PROGRESS",
        "initializedAt": now_iso,
        "parentBaselineReleaseId": "PHASE05B_R1.0.1",
        "parentBaselinePackagePath": accepted_zip,
        "parentBaselineSha256": orig_zip_sha256,
        "parentBaselineManifestEntriesVerified": manifest_check_accepted["matchedEntries"],
        "inheritedEditionId": "ED-20261110-D01",
        "inheritedVerifiedEventsCount": 18,
        "inherited0to24hEventsCount": 16,
        "inheritedMarketPulseIndicatorsCount": 8,
        "inheritedStagingTabsCount": 7,
        "inheritedStagingRecordsCount": 155,
        "originalPhase05BUnchanged": (compute_sha256(ORIG_P05B_ZIP) == orig_zip_sha256)
    }
    with open(os.path.join(p06_working_dir, "PHASE06_BASELINE_MANIFEST.json"), "w", encoding="utf-8") as f:
        json.dump(p06_inheritance_manifest, f, ensure_ascii=False, indent=2)
    with open(os.path.join(BFI_ROOT, "05_RELEASE_MANIFESTS", "PHASE06_BASELINE_MANIFEST.json"), "w", encoding="utf-8") as f:
        json.dump(p06_inheritance_manifest, f, ensure_ascii=False, indent=2)

    # Update Global Release Registry
    registry = {
        "project": "Bryan FinTech Intelligence — MagSpread Editorial Edition",
        "projectDirector": "Bryan Nguyen",
        "lastUpdated": now_iso,
        "releases": [
            p05b_release_manifest,
            {
                "phaseId": "PHASE06",
                "releaseId": "PHASE06_R1.0.0",
                "parentBaselineReleaseId": "PHASE05B_R1.0.1",
                "parentBaselineSha256": orig_zip_sha256,
                "releaseStatus": "IN_PROGRESS",
                "workingDirectory": p06_working_dir
            }
        ]
    }
    with open(os.path.join(BFI_ROOT, "00_RELEASE_REGISTRY", "RELEASE_REGISTRY.json"), "w", encoding="utf-8") as f:
        json.dump(registry, f, ensure_ascii=False, indent=2)

    print(f"[5] Created Phase 06 Working Directory at: {p06_working_dir}")
    print(f"[6] Confirmed original Phase 05B R1.0.1 archive unchanged: {orig_after_sha256 == orig_zip_sha256}")
    print("=" * 78)


if __name__ == "__main__":
    main()
