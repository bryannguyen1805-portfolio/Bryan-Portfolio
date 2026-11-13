#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_phase04b_staging.py - Comprehensive Test Suite for Phase 04B Sheets Archival Staging
Validates:
  1. Exact 7-tab schema mapping
  2. Historical edition preservation
  3. Idempotent repeated synchronization
  4. Invalid and duplicate record handling
  5. Correct preview versus published status enforcement
  6. Archive chronological ordering
  7. JSON parity & consistency
  8. Protection of accepted MagSpread UI baseline
  9. No credentials or secrets exposed in client-side code
"""

import os
import sys
import json
import hashlib
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sheets_schema import ALL_TABS, EDITIONS_TAB, NEWS_EVENTS_TAB
from sheets_sync_engine import SheetsSyncEngine

class TestPhase04BStaging(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.engine = SheetsSyncEngine(workspace_root="pilot-output")
        cls.summary = cls.engine.execute_staging_dry_run()
        with open(cls.summary["stagingOutputFile"], "r", encoding="utf-8") as f:
            cls.staged_tables = json.load(f)

    # -------------------------------------------------------------
    # TEST 1: Exact 7-Tab Schema Mapping
    # -------------------------------------------------------------
    def test_01_exact_schema_mapping(self):
        self.assertEqual(len(self.staged_tables), 7)
        expected_names = [t.name for t in ALL_TABS]
        for name in expected_names:
            self.assertIn(name, self.staged_tables)
            tab_val = self.summary["validationResults"][name]
            self.assertEqual(tab_val["status"], "PASS")
            self.assertEqual(tab_val["duplicatePks"], 0)
            self.assertEqual(len(tab_val["missingHeaders"]), 0)

    # -------------------------------------------------------------
    # TEST 2: Historical Edition Preservation
    # -------------------------------------------------------------
    def test_02_historical_edition_preservation(self):
        editions = self.staged_tables["EDITIONS"]
        edition_ids = [e["editionId"] for e in editions]
        # Must include current PILOT25 and historical Pilot 24, Pilot 23
        self.assertIn("EDITION-2026-11-08-PILOT25", edition_ids)
        self.assertIn("EDITION-2026-11-07-PILOT24", edition_ids)
        self.assertIn("EDITION-2026-11-06-PILOT23", edition_ids)
        self.assertGreaterEqual(len(editions), 3)

    # -------------------------------------------------------------
    # TEST 3: Idempotent Repeated Synchronization
    # -------------------------------------------------------------
    def test_03_idempotent_synchronization(self):
        # Run second dry-run synchronization
        summary_2 = self.engine.execute_staging_dry_run()
        self.assertEqual(self.summary["totalStagedRows"], summary_2["totalStagedRows"])
        for tab_name in self.staged_tables:
            count1 = len(self.staged_tables[tab_name])
            count2 = summary_2["validationResults"][tab_name]["rowCount"]
            self.assertEqual(count1, count2)

    # -------------------------------------------------------------
    # TEST 4: Invalid and Duplicate Record Handling
    # -------------------------------------------------------------
    def test_04_duplicate_rejection(self):
        news = self.staged_tables["NEWS_EVENTS"]
        seen_keys = set()
        for ev in news:
            key = (ev["editionId"], ev["eventId"])
            self.assertNotIn(key, seen_keys, f"Duplicate composite key found: {key}")
            seen_keys.add(key)

    # -------------------------------------------------------------
    # TEST 5: Correct Preview vs Published Status Enforcement
    # -------------------------------------------------------------
    def test_05_preview_status_enforced(self):
        editions = self.staged_tables["EDITIONS"]
        pilot25 = next(e for e in editions if e["editionId"] == "EDITION-2026-11-08-PILOT25")
        # Must strictly remain DRAFT or PREVIEW due to 52.38% shortfall in edition-data.json
        self.assertIn(pilot25["publicationStatus"], ["DRAFT_INTERNAL_ONLY", "PREVIEW_ONLY"])
        self.assertNotEqual(pilot25["publicationStatus"], "PUBLISHED")
        self.assertIn("SHORTFALL", pilot25["gateStatus"])

    # -------------------------------------------------------------
    # TEST 6: Archive Chronological Ordering
    # -------------------------------------------------------------
    def test_06_archive_ordering(self):
        editions = self.staged_tables["EDITIONS"]
        dates = [e["editionDate"] for e in editions]
        # Most recent edition (2026-11-08) must be first
        self.assertEqual(dates[0], "2026-11-08")
        self.assertEqual(dates[1], "2026-11-07")
        self.assertEqual(dates[2], "2026-11-06")

    # -------------------------------------------------------------
    # TEST 7: JSON Parity & Consistency
    # -------------------------------------------------------------
    def test_07_json_parity(self):
        with open("pilot-output/edition-data.json", "r", encoding="utf-8") as f:
            ed_json = json.load(f)
        editions = self.staged_tables["EDITIONS"]
        pilot25 = next(e for e in editions if e["editionId"] == "EDITION-2026-11-08-PILOT25")
        self.assertEqual(pilot25["editionNumber"], ed_json["editionNumber"])
        self.assertEqual(pilot25["eligibleCount"], len(ed_json["eligibleNewsList"]))

    # -------------------------------------------------------------
    # TEST 8: Protection of Accepted MagSpread UI Baseline
    # -------------------------------------------------------------
    def test_08_ui_baseline_hashes_untouched(self):
        expected_hashes = {
            "magspread-preview.html": "a7679251c49d4f30485a90e36191eeaf6185313625e264878273b1e79a6577d4",
            "magspread.css": "82d7c64209e3b726d7e0c7cf4e29524ad336c03b151369ff360aba82b6ce49ba",
            "magspread.js": "860a21903aa03ab31ec597d8cff8fcdb028b63b1d8ca10adffb90318dbf2ce6c",
            "edition-data.json": "c95a591a4b695e51f980737d0f5c3a85e498023292c1c62e63daed0bf3dbe67a",
            "edition-data.js": "9d819ad6323ac42e13eabb16c5b5150cf306192739524bd6317d1efbf8f9a694"
        }
        for fname, exp_hash in expected_hashes.items():
            path = os.path.join("pilot-output", fname)
            actual_hash = self.engine.sha256_file(path)
            self.assertEqual(actual_hash, exp_hash, f"Baseline corruption detected in {fname}")

    # -------------------------------------------------------------
    # TEST 9: No Credentials Exposed in Client-Side Files
    # -------------------------------------------------------------
    def test_09_no_secrets_exposed(self):
        client_files = [
            "pilot-output/magspread-preview.html",
            "pilot-output/magspread.js",
            "pilot-output/edition-data.js",
            "pilot-output/edition-data.json"
        ]
        forbidden_patterns = [
            "client_secret", "private_key", "BEGIN PRIVATE KEY",
            "oauth2.googleapis.com", "service_account"
        ]
        for fpath in client_files:
            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read()
                for pat in forbidden_patterns:
                    self.assertNotIn(pat, content, f"Forbidden credential pattern '{pat}' leaked in client file {fpath}")


if __name__ == "__main__":
    unittest.main()
