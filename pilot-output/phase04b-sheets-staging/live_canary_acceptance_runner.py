#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
live_canary_acceptance_runner.py - Real Google Sheets API v4 Live Canary Acceptance Test
Bryan FinTech Intelligence — Phase 04B Controlled Staging
"""

import os
import sys
import json
import time
import base64
import urllib.request
import urllib.error
import urllib.parse
import subprocess
import tempfile
from typing import Tuple, Dict, List, Any, Optional
from datetime import datetime, timezone, timedelta

UTC7 = timezone(timedelta(hours=7))

# Load Schema
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sheets_schema import ALL_TABS, TabSchema

SPREADSHEET_ID = "10MG2RSmh7MtX3x7Ej1u0NFD-rp6rqXXXOhQi11hkvy8"
KEY_PATH = "/Users/quangtri/Downloads/bryan-fintech-intelligence-20e8c57d3173.json"

class GoogleSheetsApiClient:
    def __init__(self, key_path: str, spreadsheet_id: str):
        self.key_path = key_path
        self.spreadsheet_id = spreadsheet_id
        self.token = None
        self.token_expiry = 0
        self.client_email = None
        self.project_id = None
        self._load_key()

    def _load_key(self):
        with open(self.key_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.client_email = data["client_email"]
            self.project_id = data["project_id"]
            self.private_key = data["private_key"]

    @staticmethod
    def _b64url(b: bytes) -> str:
        return base64.urlsafe_b64encode(b).decode("utf-8").rstrip("=")

    def get_token(self) -> str:
        now = int(time.time())
        if self.token and now < self.token_expiry - 60:
            return self.token

        header = json.dumps({"alg": "RS256", "typ": "JWT"}).encode("utf-8")
        payload = json.dumps({
            "iss": self.client_email,
            "scope": "https://www.googleapis.com/auth/spreadsheets https://www.googleapis.com/auth/drive.readonly",
            "aud": "https://oauth2.googleapis.com/token",
            "exp": now + 3600,
            "iat": now
        }).encode("utf-8")

        signing_input = self._b64url(header) + "." + self._b64url(payload)
        with tempfile.NamedTemporaryFile("w", delete=False) as kf:
            kf.write(self.private_key)
            kfp = kf.name

        try:
            p = subprocess.Popen(["openssl", "dgst", "-sha256", "-sign", kfp],
                                 stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            sig, err = p.communicate(signing_input.encode("utf-8"))
            if p.returncode != 0:
                raise RuntimeError(f"OpenSSL signature failed: {err.decode('utf-8')}")
        finally:
            if os.path.exists(kfp):
                os.remove(kfp)

        jwt_token = signing_input + "." + self._b64url(sig)

        post_data = urllib.parse.urlencode({
            "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
            "assertion": jwt_token
        }).encode("utf-8")

        req = urllib.request.Request("https://oauth2.googleapis.com/token", data=post_data,
                                     headers={"Content-Type": "application/x-www-form-urlencoded"})
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            self.token = data["access_token"]
            self.token_expiry = now + int(data.get("expires_in", 3600))
            return self.token

    def request(self, method: str, endpoint: str, body: dict = None, custom_token: str = None) -> Tuple[int, dict]:
        token = custom_token if custom_token else self.get_token()
        url = f"https://sheets.googleapis.com/v4/spreadsheets/{self.spreadsheet_id}{endpoint}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        data = json.dumps(body).encode("utf-8") if body is not None else None
        req = urllib.request.Request(url, data=data, headers=headers, method=method)

        try:
            with urllib.request.urlopen(req) as resp:
                resp_data = json.loads(resp.read().decode("utf-8"))
                return resp.status, resp_data
        except urllib.error.HTTPError as e:
            err_content = e.read().decode("utf-8")
            try:
                err_json = json.loads(err_content)
            except Exception:
                err_json = {"raw": err_content}
            return e.code, err_json

def run_canary_suite():
    print("[CanaryRunner] Initializing Live Google Sheets API Canary Test...")
    client = GoogleSheetsApiClient(KEY_PATH, SPREADSHEET_ID)
    
    results = {
        "executionTimestamp": datetime.now(UTC7).isoformat(),
        "spreadsheetId": SPREADSHEET_ID,
        "serviceAccount": client.client_email,
        "projectId": client.project_id,
        "stages": {}
    }

    # =========================================================
    # STAGE 1: AUTHENTICATION & SPREADSHEET METADATA
    # =========================================================
    print("\n--- STAGE 1: Authentication & Spreadsheet Metadata ---")
    status, meta = client.request("GET", "")
    assert status == 200, f"Spreadsheet metadata request failed: {status} {meta}"
    title = meta.get("properties", {}).get("title")
    expected_title = "Bryan FinTech Intelligence — Archive STAGING"
    print(f"Spreadsheet Title: '{title}'")
    assert title == expected_title, f"Title mismatch! Expected '{expected_title}', got '{title}'"
    
    sheets_meta = meta.get("sheets", [])
    tab_names = [s.get("properties", {}).get("title") for s in sheets_meta]
    sheet_ids = {s.get("properties", {}).get("title"): s.get("properties", {}).get("sheetId") for s in sheets_meta}
    print(f"Discovered {len(tab_names)} sheets: {tab_names}")
    
    expected_tab_names = [tab.name for tab in ALL_TABS]
    for exp in expected_tab_names:
        assert exp in tab_names, f"Missing required tab: {exp}"
    
    results["stages"]["stage1_metadata"] = {
        "status": "PASS",
        "title": title,
        "tabCount": len(tab_names),
        "discoveredTabs": tab_names
    }

    # =========================================================
    # STAGE 2: SCHEMA HEADERS VALIDATION & INITIALIZATION
    # =========================================================
    print("\n--- STAGE 2: Schema Headers Verification ---")
    headers_status = {}
    schema_map = {tab.name: tab for tab in ALL_TABS}
    
    for tab in ALL_TABS:
        status, val_data = client.request("GET", f"/values/{tab.name}!A1:Z1")
        assert status == 200, f"Failed to read headers for {tab.name}: {status}"
        rows = val_data.get("values", [])
        headers = rows[0] if rows else []
        
        expected_headers = tab.headers
        if not headers:
            print(f"Tab '{tab.name}' has empty header row. Writing Schema V1.0 headers ({len(expected_headers)} cols)...")
            write_body = {
                "values": [expected_headers]
            }
            w_status, w_res = client.request("PUT", f"/values/{tab.name}!A1:Z1?valueInputOption=RAW", write_body)
            assert w_status == 200, f"Failed to initialize headers for {tab.name}: {w_status} {w_res}"
            # Re-read to confirm
            _, val_data2 = client.request("GET", f"/values/{tab.name}!A1:Z1")
            headers = val_data2.get("values", [])[0]

        # Verify parity
        assert headers == expected_headers, f"Header mismatch in {tab.name}!\nExpected: {expected_headers}\nGot: {headers}"
        print(f"Tab '{tab.name}': {len(headers)} columns verified matching Schema V1.0 exactly.")
        headers_status[tab.name] = {
            "status": "PASS",
            "columnCount": len(headers),
            "columns": headers
        }

    results["stages"]["stage2_schema_headers"] = {
        "status": "PASS",
        "tabs": headers_status
    }

    # =========================================================
    # STAGE 3: CANARY WRITE TEST (1 ROW PER TAB)
    # =========================================================
    print("\n--- STAGE 3: Controlled Live Write Canary (7 Tabs) ---")
    canary_run_id = f"CANARY_PHASE04B_{datetime.now(UTC7).strftime('%Y%m%d_%H%M%S')}"
    canary_edition_id = f"CANARY_PHASE04B_ED_01"
    canary_event_id = f"CANARY_PHASE04B_EVT_01"
    
    canary_records = {
        "EDITIONS": {
            "editionId": canary_edition_id,
            "editionNumber": "Canary Acceptance Edition",
            "editionDate": "2026-11-09",
            "displayDate": "09/11/2026",
            "cutoffTime": "2026-11-09T01:00:00+07:00",
            "publicationStatus": "PREVIEW_ONLY",
            "gateStatus": "FAIL_SHORTFALL_24H_PREVIEW_ONLY",
            "freshnessRatio": "100.00%",
            "eligibleCount": 1,
            "count0To24h": 1,
            "count24To48h": 0,
            "count48To72h": 0,
            "leadStoryTitle": "Canary Cover Story: Live Sheets API v4 Verification",
            "macroTheme": "Automated Canary Acceptance",
            "archivedAt": "2026-11-09T01:25:00+07:00"
        },
        "NEWS_EVENTS": {
            "editionId": canary_edition_id,
            "eventId": canary_event_id,
            "stt": 1,
            "headline": "Canary Event: Google Sheets Bi-Directional Round-Trip Parity",
            "category": "Fintech & Ngân hàng",
            "tier": 1,
            "sourceName": "Bryan QA Lab",
            "canonicalUrl": "https://bryan.fintech.test/canary-01",
            "originalSourcePublishedAt": "2026-11-09T00:45:00+07:00",
            "timeDeltaFromCutoff": "0.25h",
            "timeWindowBucket": "0–24h",
            "verificationStatus": "VERIFIED",
            "dedupStatus": "UNIQUE_NEW_EVENT",
            "isFollowUp": False,
            "followUpTo": "",
            "evidenceSha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            "verifiedFactSummary": json.dumps({"metric": "canary_latency", "status": "nominal"}, ensure_ascii=False),
            "macroToMicro": "System Testing -> Real REST API -> Staging Verification",
            "fintechImpact": "Guarantees zero production data corruption",
            "prediction": "Live sync ready upon Bryan signoff"
        },
        "EDITORIAL_SECTIONS": {
            "editionId": canary_edition_id,
            "sectionKey": "sec02_coverStory",
            "sectionTitle": "TIÊU ĐIỂM HÔM NAY · CANARY EDITORIAL THESIS",
            "editorialRating": "TEST_PASS",
            "primaryThesis": "Validating real live Sheets synchronization without breaking baselines",
            "transmissionMechanism": "OAuth2 Token -> JSON Serialization -> Google Sheets Append",
            "actionableRecommendations": json.dumps(["Run canary", "Verify cleanup"], ensure_ascii=False),
            "riskFactors": json.dumps(["Credential leak", "Schema drift"], ensure_ascii=False),
            "monitoringChecklist": json.dumps(["HTTP 200", "Parity 100%"], ensure_ascii=False),
            "sectionWordCount": 24,
            "lastEditedAt": "2026-11-09T01:25:00+07:00"
        },
        "MARKET_PULSE_HISTORY": {
            "editionId": canary_edition_id,
            "indicatorId": "CANARY_IND_01",
            "indicatorName": "Canary Test Pulse Indicator",
            "category": "Vĩ mô & Tiền tệ",
            "tier": 1,
            "currentValue": "1.000,00",
            "previousValue": "995,00",
            "changeAbsolute": "+5,00",
            "changePercent": "+0.50%",
            "unit": "Điểm",
            "trendSignal": "UP",
            "sourceAgency": "Bryan QA Lab",
            "measurementDate": "2026-11-09",
            "verificationStatus": "VERIFIED"
        },
        "EVENT_REGISTRY": {
            "eventId": canary_event_id,
            "canonicalUrl": "https://bryan.fintech.test/canary-01",
            "normalizedHeadlineSignature": "canary event google sheets roundtrip",
            "originalTitle": "Canary Event: Google Sheets Bi-Directional Round-Trip Parity",
            "primaryEntity": "Bryan FinTech Lab",
            "eventDate": "2026-11-09",
            "publicationDate": "2026-11-09T00:45:00+07:00",
            "firstDiscoveredInEdition": canary_edition_id,
            "duplicateCount": 0,
            "isFollowUp": False,
            "followUpToEventId": "",
            "lifecycleStatus": "ACTIVE",
            "registeredAt": "2026-11-09T01:25:00+07:00"
        },
        "SOURCE_LEDGER": {
            "collectionRunId": canary_run_id,
            "sourceUrl": "https://bryan.fintech.test/canary-01",
            "sourceDomain": "bryan.fintech.test",
            "sourceChannel": "CANARY_TEST_HARNESS",
            "originalTitle": "Canary Source Web Document",
            "retrievalTimestamp": "2026-11-09T01:25:00+07:00",
            "httpStatus": 200,
            "rawContentSha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            "evidenceSnapshotFile": "canary_snapshot_01.txt",
            "verificationOutcome": "VERIFIED",
            "gateAuditSummary": "CANARY_VERIFIED",
            "associatedEventId": canary_event_id
        },
        "PUBLISH_AUDIT": {
            "auditLogId": f"AUDIT-CANARY-{datetime.now(UTC7).strftime('%Y%m%d%H%M%S')}",
            "editionId": canary_edition_id,
            "action": "STAGING_SYNC",
            "performedBy": "BRYAN_QA_LEAD",
            "gateDecision": "PREVIEW_ONLY_SHORTFALL",
            "freshnessRatioRecorded": "100.00%",
            "verifiedCountRecorded": 1,
            "localJsonChecksum": "c95a591a4b695e51f980737d0f5c3a85e498023292c1c62e63daed0bf3dbe67a",
            "sheetsSyncStatus": "LIVE_CANARY_TEST_ROW",
            "rollbackReferenceCheckpoint": "CHECKPOINT-03-PHASE04A-ACCEPTED",
            "notes": "Controlled canary write for connection verification. Idempotent test row.",
            "timestamp": "2026-11-09T01:25:00+07:00"
        }
    }

    write_results = {}
    for tab_name, rec in canary_records.items():
        tab_schema = schema_map[tab_name]
        row_values = [str(rec.get(h, "")) for h in tab_schema.headers]
        
        # Write to row 2
        body = {"values": [row_values]}
        w_status, w_res = client.request("PUT", f"/values/{tab_name}!A2:Z2?valueInputOption=RAW", body)
        assert w_status == 200, f"Write failed on {tab_name}: {w_status} {w_res}"
        print(f"Canary written to tab '{tab_name}' (Row 2): {w_res.get('updatedCells')} cells updated.")
        write_results[tab_name] = {
            "status": "PASS",
            "updatedCells": w_res.get("updatedCells")
        }

    results["stages"]["stage3_canary_write"] = write_results

    # =========================================================
    # STAGE 4: READ-BACK PARITY VERIFICATION
    # =========================================================
    print("\n--- STAGE 4: Read-Back Value Parity Verification ---")
    readback_results = {}
    for tab_name, orig_rec in canary_records.items():
        tab_schema = schema_map[tab_name]
        status, read_res = client.request("GET", f"/values/{tab_name}!A2:Z2")
        assert status == 200, f"Read-back failed on {tab_name}: {status}"
        rows = read_res.get("values", [])
        assert len(rows) == 1, f"Expected 1 canary row in {tab_name}, got {len(rows)}"
        read_row = rows[0]
        
        # Pad read_row if trailing empty cells were omitted
        expected_cols = tab_schema.headers
        while len(read_row) < len(expected_cols):
            read_row.append("")

        mismatches = []
        for idx, col_name in enumerate(expected_cols):
            expected_val = str(orig_rec.get(col_name, ""))
            actual_val = str(read_row[idx])
            # Handle boolean normalization (Sheets returns TRUE/FALSE)
            if isinstance(orig_rec.get(col_name), bool) or expected_val in ["True", "False", "TRUE", "FALSE"]:
                match = (expected_val.upper() == actual_val.upper())
            else:
                match = (expected_val == actual_val)
            if not match:
                mismatches.append({"col": col_name, "expected": expected_val, "actual": actual_val})

        assert len(mismatches) == 0, f"Value mismatch in {tab_name}: {mismatches}"
        print(f"Tab '{tab_name}': Read-back 100% matched across all {len(expected_cols)} fields.")
        readback_results[tab_name] = {
            "status": "PASS",
            "fieldsVerified": len(expected_cols),
            "mismatchCount": 0
        }

    results["stages"]["stage4_readback_parity"] = readback_results

    # =========================================================
    # STAGE 5: IDEMPOTENCY & DUPLICATE WRITE PREVENTION
    # =========================================================
    print("\n--- STAGE 5: Idempotency & Duplicate Prevention Test ---")
    idempotency_results = {}
    # Simulate an idempotent re-write: Writing same PK to the same location or checking PK existence before append
    for tab_name, rec in canary_records.items():
        tab_schema = schema_map[tab_name]
        pk_cols = tab_schema.primary_key
        
        # Read current table to find PK
        status, all_rows_res = client.request("GET", f"/values/{tab_name}!A1:Z10")
        assert status == 200
        all_vals = all_rows_res.get("values", [])
        headers = all_vals[0]
        pk_indices = [headers.index(pk) for pk in pk_cols]
        
        existing_pks = {}
        for r_idx, row in enumerate(all_vals[1:], start=2):
            pk_tuple = tuple(row[i] if i < len(row) else "" for i in pk_indices)
            existing_pks[pk_tuple] = r_idx

        target_pk = tuple(str(rec[pk]) for pk in pk_cols)
        assert target_pk in existing_pks, f"Canary record not found in {tab_name} during idempotency check"
        target_row_idx = existing_pks[target_pk]
        
        # Idempotent write: update existing row instead of appending duplicate row
        row_values = [str(rec.get(h, "")) for h in tab_schema.headers]
        body = {"values": [row_values]}
        u_status, u_res = client.request("PUT", f"/values/{tab_name}!A{target_row_idx}:Z{target_row_idx}?valueInputOption=RAW", body)
        assert u_status == 200
        
        # Verify row count has NOT increased
        status2, count_check = client.request("GET", f"/values/{tab_name}!A1:Z10")
        assert len(count_check.get("values", [])) == 2, f"Row count increased unexpectedly in {tab_name}!"
        print(f"Tab '{tab_name}': Idempotent overwrite confirmed at Row {target_row_idx}. Total rows remained 2.")
        idempotency_results[tab_name] = {
            "status": "PASS",
            "totalRowsAfterRepeat": 2,
            "duplicateCreated": False
        }

    results["stages"]["stage5_idempotency"] = idempotency_results

    # =========================================================
    # STAGE 6: ERROR & ANOMALY HANDLING TESTS
    # =========================================================
    print("\n--- STAGE 6: Failure & Anomaly Handling Tests ---")
    error_tests = {}
    
    # Test 6.1: Non-existent tab name
    print("Test 6.1: Access non-existent tab...")
    bad_tab_status, bad_tab_res = client.request("GET", "/values/NON_EXISTENT_TAB!A1:Z10")
    assert bad_tab_status == 400, f"Expected HTTP 400 for bad tab, got {bad_tab_status}"
    print(f"Non-existent tab correctly rejected: HTTP {bad_tab_status} ({bad_tab_res.get('error', {}).get('message', '')[:60]}...)")
    error_tests["bad_tab"] = {"status": "PASS", "httpStatus": bad_tab_status}

    # Test 6.2: Invalid access token (Unauthorized)
    print("Test 6.2: Request with invalid OAuth2 token...")
    fake_token = "ya29.invalid_token_canary_security_test"
    auth_err_status, auth_err_res = client.request("GET", "/values/EDITIONS!A1:Z1", custom_token=fake_token)
    assert auth_err_status == 401, f"Expected HTTP 401 for bad token, got {auth_err_status}"
    print(f"Invalid token correctly rejected: HTTP {auth_err_status}")
    error_tests["invalid_token"] = {"status": "PASS", "httpStatus": auth_err_status}

    # Test 6.3: Malformed range syntax
    print("Test 6.3: Malformed range query...")
    range_err_status, range_err_res = client.request("GET", "/values/EDITIONS!A-INVALID:Z")
    assert range_err_status == 400, f"Expected HTTP 400 for malformed range, got {range_err_status}"
    print(f"Malformed range syntax rejected: HTTP {range_err_status}")
    error_tests["malformed_range"] = {"status": "PASS", "httpStatus": range_err_status}

    results["stages"]["stage6_error_handling"] = error_tests

    # =========================================================
    # STAGE 7: CONTROLLED CLEANUP & RESTORATION
    # =========================================================
    print("\n--- STAGE 7: Controlled Cleanup of Canary Rows ---")
    cleanup_results = {}
    
    # We delete row index 1 (which is Row 2 in 1-based index) using batchUpdate DeleteDimensionRequest
    batch_requests = []
    for tab_name in ALL_TABS:
        s_id = sheet_ids[tab_name.name]
        batch_requests.append({
            "deleteDimension": {
                "range": {
                    "sheetId": s_id,
                    "dimension": "ROWS",
                    "startIndex": 1,
                    "endIndex": 2
                }
            }
        })
    
    clean_body = {"requests": batch_requests}
    c_status, c_res = client.request("POST", ":batchUpdate", clean_body)
    assert c_status == 200, f"Batch delete failed: {c_status} {c_res}"
    print(f"Successfully deleted Row 2 across all 7 tabs via atomic batchUpdate.")

    # Read-back verification of pristine state
    for tab in ALL_TABS:
        status, check_data = client.request("GET", f"/values/{tab.name}!A1:Z10")
        assert status == 200
        remaining_rows = check_data.get("values", [])
        assert len(remaining_rows) == 1, f"Expected exactly 1 header row remaining in {tab.name}, found {len(remaining_rows)}"
        assert remaining_rows[0] == tab.headers, f"Header row in {tab.name} altered during cleanup!"
        print(f"Tab '{tab.name}': Cleaned up successfully. Remaining rows: 1 (Header row intact).")
        cleanup_results[tab.name] = {
            "status": "PASS",
            "remainingRows": 1,
            "headerIntact": True
        }

    results["stages"]["stage7_cleanup"] = cleanup_results

    # =========================================================
    # STAGE 8: BASELINE IMMUTABILITY AUDIT
    # =========================================================
    print("\n--- STAGE 8: Baseline Immutability Audit ---")
    import hashlib
    def get_sha256(path):
        with open(path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()

    expected_hashes = {
        "magspread-preview.html": "a7679251c49d4f30485a90e36191eeaf6185313625e264878273b1e79a6577d4",
        "magspread.css": "82d7c64209e3b726d7e0c7cf4e29524ad336c03b151369ff360aba82b6ce49ba",
        "magspread.js": "860a21903aa03ab31ec597d8cff8fcdb028b63b1d8ca10adffb90318dbf2ce6c",
        "edition-data.json": "c95a591a4b695e51f980737d0f5c3a85e498023292c1c62e63daed0bf3dbe67a",
        "edition-data.js": "9d819ad6323ac42e13eabb16c5b5150cf306192739524bd6317d1efbf8f9a694"
    }

    base_results = {}
    for fname, exp_hash in expected_hashes.items():
        fpath = os.path.join("pilot-output", fname)
        cur_hash = get_sha256(fpath)
        assert cur_hash == exp_hash, f"Baseline violation in {fname}!\nExpected: {exp_hash}\nActual: {cur_hash}"
        base_results[fname] = {"sha256": cur_hash, "status": "MATCH_100%"}
        print(f"Baseline {fname}: SHA-256 Verified ({cur_hash[:16]}...)")

    results["stages"]["stage8_baseline_integrity"] = base_results

    # Overall verdict
    results["verdict"] = "LIVE_CANARY_PASS"
    out_path = os.path.join("pilot-output", "phase04b-sheets-staging", "live_canary_execution_summary.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n==========================================================")
    print(f"CANARY SUITE COMPLETE: ALL STAGES PASSED (LIVE_CANARY_PASS)")
    print(f"Summary written to: {out_path}")
    print(f"==========================================================")
    return results

if __name__ == "__main__":
    run_canary_suite()
