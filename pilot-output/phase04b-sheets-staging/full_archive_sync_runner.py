#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
full_archive_sync_runner.py - Controlled Full Archive STAGING Synchronization
Bryan FinTech Intelligence — Phase 04B
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
import hashlib
from typing import Tuple, Dict, List, Any, Optional
from datetime import datetime, timezone, timedelta

UTC7 = timezone(timedelta(hours=7))

# Load Schema
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sheets_schema import ALL_TABS, TabSchema

SPREADSHEET_ID = "10MG2RSmh7MtX3x7Ej1u0NFD-rp6rqXXXOhQi11hkvy8"
KEY_PATH = "/Users/quangtri/Downloads/bryan-fintech-intelligence-20e8c57d3173.json"
STAGING_JSON_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "staging_tables.json")

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

        retries = 3
        backoff = 1.0
        for attempt in range(retries):
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
                if e.code in (429, 500, 503) and attempt < retries - 1:
                    time.sleep(backoff)
                    backoff *= 2.0
                    continue
                return e.code, err_json
            except urllib.error.URLError as e:
                if attempt < retries - 1:
                    time.sleep(backoff)
                    backoff *= 2.0
                    continue
                return 0, {"error": str(e.reason)}


def run_full_sync():
    print("=" * 70)
    print("BRYAN FINTECH INTELLIGENCE — PHASE 04B FULL ARCHIVE STAGING SYNC")
    print("=" * 70)

    client = GoogleSheetsApiClient(KEY_PATH, SPREADSHEET_ID)
    summary: Dict[str, Any] = {
        "executionTimestamp": datetime.now(UTC7).isoformat(),
        "spreadsheetId": SPREADSHEET_ID,
        "serviceAccount": client.client_email,
        "projectId": client.project_id,
        "expectedRows": {
            "EDITIONS": 3,
            "NEWS_EVENTS": 21,
            "EDITORIAL_SECTIONS": 5,
            "MARKET_PULSE_HISTORY": 8,
            "EVENT_REGISTRY": 67,
            "SOURCE_LEDGER": 50,
            "PUBLISH_AUDIT": 1,
            "TOTAL": 155
        },
        "stages": {}
    }

    # -------------------------------------------------------------
    # STAGE 1: PRE-SYNC CHECKS & REMOTE SNAPSHOT
    # -------------------------------------------------------------
    print("\n--- STAGE 1: Pre-Sync Safety & Remote Snapshot Check ---")
    status, meta = client.request("GET", "")
    assert status == 200, f"Failed to retrieve spreadsheet metadata: {status} {meta}"
    title = meta.get("properties", {}).get("title")
    expected_title = "Bryan FinTech Intelligence — Archive STAGING"
    assert title == expected_title, f"Spreadsheet title mismatch: expected '{expected_title}', got '{title}'"
    print(f"Verified remote target: '{title}' (ID: {SPREADSHEET_ID})")

    # Load local staging dataset
    with open(STAGING_JSON_PATH, "r", encoding="utf-8") as f:
        local_tables = json.load(f)

    local_total = sum(len(rows) for rows in local_tables.values())
    assert local_total == 155, f"Local dataset row count mismatch: expected 155, got {local_total}"
    print(f"Loaded local staging dataset: {local_total} business rows across {len(local_tables)} tabs.")

    # Schema verification & snapshot remote state
    schema_map = {tab.name: tab for tab in ALL_TABS}
    remote_initial_state = {}
    for tab in ALL_TABS:
        tname = tab.name
        status, val_data = client.request("GET", f"/values/{tname}!A1:Z1000")
        assert status == 200, f"Failed to read remote tab {tname}: {status}"
        remote_rows = val_data.get("values", [])
        assert len(remote_rows) >= 1, f"Tab {tname} has no header row!"
        remote_headers = remote_rows[0]
        assert remote_headers == tab.headers, f"Header mismatch in tab {tname}!"
        remote_initial_state[tname] = {
            "headerColumnCount": len(remote_headers),
            "dataRowCount": len(remote_rows) - 1
        }
        print(f"Tab '{tname}': Remote header verified (97 cols total across tabs). Pre-existing data rows: {len(remote_rows) - 1}")

    summary["stages"]["stage1_pre_sync"] = {
        "status": "PASS",
        "spreadsheetTitle": title,
        "localDatasetRows": local_total,
        "remoteInitialState": remote_initial_state
    }

    # -------------------------------------------------------------
    # STAGE 2: CONTROLLED LIVE WRITE (155 ROWS ACROSS 7 TABS)
    # -------------------------------------------------------------
    print("\n--- STAGE 2: Controlled Live Staging Write (155 Rows) ---")
    sync_write_results = {}
    total_inserted = 0

    for tab in ALL_TABS:
        tname = tab.name
        rows = local_tables[tname]
        expected_count = summary["expectedRows"][tname]
        assert len(rows) == expected_count, f"Mismatch in {tname}: expected {expected_count}, got {len(rows)}"

        matrix = []
        for r in rows:
            row_vals = [str(r.get(h, "")) for h in tab.headers]
            matrix.append(row_vals)

        # Batch write starting at Row 2 using RAW option to preserve financial string formatting and Vietnamese UTF-8
        end_row = 1 + len(matrix)
        range_str = f"{tname}!A2:Z{end_row}"
        body = {"values": matrix}
        w_status, w_res = client.request("PUT", f"/values/{range_str}?valueInputOption=RAW", body)
        assert w_status == 200, f"Write failed for {tname}: {w_status} {w_res}"

        updated_cells = w_res.get("updatedCells", 0)
        updated_rows = w_res.get("updatedRows", 0)
        print(f"Tab '{tname}': Wrote {len(matrix)} rows ({updated_cells} cells updated).")

        sync_write_results[tname] = {
            "attempted": len(rows),
            "inserted": len(matrix),
            "updatedRows": updated_rows,
            "updatedCells": updated_cells,
            "status": "PASS"
        }
        total_inserted += len(matrix)

    assert total_inserted == 155, f"Expected 155 total rows written, got {total_inserted}"
    summary["stages"]["stage2_sync_write"] = {
        "status": "PASS",
        "totalAttempted": 155,
        "totalInserted": total_inserted,
        "perTab": sync_write_results
    }

    # -------------------------------------------------------------
    # STAGE 3: POST-SYNC READ-BACK AUDIT & PARITY VERIFICATION
    # -------------------------------------------------------------
    print("\n--- STAGE 3: Post-Sync Read-Back Audit & Parity Verification ---")
    readback_summary = {}
    total_remote_business_rows = 0

    for tab in ALL_TABS:
        tname = tab.name
        expected_rows = local_tables[tname]
        tab_schema = schema_map[tname]

        status, val_data = client.request("GET", f"/values/{tname}!A1:Z1000")
        assert status == 200, f"Failed to read back {tname}: {status}"
        vals = val_data.get("values", [])
        assert len(vals) == 1 + len(expected_rows), f"Row count mismatch in {tname}: expected {1 + len(expected_rows)}, got {len(vals)}"

        header_row = vals[0]
        data_rows = vals[1:]
        total_remote_business_rows += len(data_rows)

        # Verify field-by-field parity
        mismatches = []
        for r_idx, (local_rec, remote_row) in enumerate(zip(expected_rows, data_rows)):
            while len(remote_row) < len(tab_schema.headers):
                remote_row.append("")

            for c_idx, col_name in enumerate(tab_schema.headers):
                expected_val = str(local_rec.get(col_name, ""))
                actual_val = str(remote_row[c_idx])

                # Normalize boolean
                if isinstance(local_rec.get(col_name), bool) or expected_val in ["True", "False", "TRUE", "FALSE"]:
                    match = (expected_val.upper() == actual_val.upper())
                else:
                    match = (expected_val == actual_val)

                if not match:
                    mismatches.append({
                        "row": r_idx + 2,
                        "col": col_name,
                        "expected": expected_val[:40],
                        "actual": actual_val[:40]
                    })

        assert len(mismatches) == 0, f"Value mismatch in {tname}: {mismatches[:5]}"
        print(f"Tab '{tname}': Read back {len(data_rows)} rows. Parity 100% verified across all {len(tab_schema.headers)} columns.")

        readback_summary[tname] = {
            "remoteDataRows": len(data_rows),
            "columnsVerified": len(tab_schema.headers),
            "mismatchCount": len(mismatches),
            "status": "PASS"
        }

    assert total_remote_business_rows == 155, f"Expected 155 business rows, found {total_remote_business_rows}"
    summary["stages"]["stage3_readback_parity"] = {
        "status": "PASS",
        "totalRemoteBusinessRows": total_remote_business_rows,
        "perTab": readback_summary
    }

    # -------------------------------------------------------------
    # STAGE 4: IDEMPOTENCY VERIFICATION (SECOND FULL SYNC EXECUTION)
    # -------------------------------------------------------------
    print("\n--- STAGE 4: Idempotency Verification (Second Sync Run) ---")
    idempotency_summary = {}

    for tab in ALL_TABS:
        tname = tab.name
        rows = local_tables[tname]
        tab_schema = schema_map[tname]
        pk_cols = tab_schema.primary_key

        # Re-apply exact same batch write
        matrix = [[str(r.get(h, "")) for h in tab_schema.headers] for r in rows]
        end_row = 1 + len(matrix)
        range_str = f"{tname}!A2:Z{end_row}"
        body = {"values": matrix}
        w_status, w_res = client.request("PUT", f"/values/{range_str}?valueInputOption=RAW", body)
        assert w_status == 200

        # Read back to confirm row count and unique primary keys
        status, check_data = client.request("GET", f"/values/{tname}!A1:Z1000")
        assert status == 200
        vals = check_data.get("values", [])
        assert len(vals) == 1 + len(rows), f"Row count changed after repeated write in {tname}!"

        # Primary key uniqueness check
        headers = vals[0]
        pk_indices = [headers.index(pk) for pk in pk_cols]
        seen_pks = set()
        duplicate_pks = []
        for r_idx, r_vals in enumerate(vals[1:], start=2):
            pk_val = tuple(r_vals[i] if i < len(r_vals) else "" for i in pk_indices)
            if pk_val in seen_pks:
                duplicate_pks.append(pk_val)
            seen_pks.add(pk_val)

        assert len(duplicate_pks) == 0, f"Duplicate primary keys in {tname}: {duplicate_pks}"
        print(f"Tab '{tname}': Second write idempotent. Rows remain {len(rows)}. Duplicate PKs: 0.")

        idempotency_summary[tname] = {
            "totalRowsAfterRepeat": len(rows),
            "duplicatePkCount": 0,
            "status": "PASS"
        }

    summary["stages"]["stage4_idempotency"] = {
        "status": "PASS",
        "perTab": idempotency_summary
    }

    # -------------------------------------------------------------
    # STAGE 5: FAULT INJECTION & ERROR SIMULATION
    # -------------------------------------------------------------
    print("\n--- STAGE 5: Failure Handling & Error Simulation ---")
    error_summary = {}

    # 5.1 Invalid Token (Unauthorized 401)
    status_401, res_401 = client.request("GET", "/values/EDITIONS!A1:Z1", custom_token="ya29.invalid_simulated_token")
    assert status_401 == 401
    print(f"Fault 5.1: Invalid token correctly rejected with HTTP {status_401}.")
    error_summary["invalid_token"] = {"status": "PASS", "httpStatus": status_401}

    # 5.2 Invalid Tab (Bad Request 400)
    status_400, res_400 = client.request("GET", "/values/NON_EXISTENT_ARCHIVE!A1:Z10")
    assert status_400 == 400
    print(f"Fault 5.2: Non-existent tab correctly rejected with HTTP {status_400}.")
    error_summary["bad_tab"] = {"status": "PASS", "httpStatus": status_400}

    # 5.3 Malformed Range Syntax
    status_range, res_range = client.request("GET", "/values/EDITIONS!INVALID_SYNTAX")
    assert status_range == 400
    print(f"Fault 5.3: Malformed range correctly rejected with HTTP {status_range}.")
    error_summary["malformed_range"] = {"status": "PASS", "httpStatus": status_range}

    summary["stages"]["stage5_error_handling"] = {
        "status": "PASS",
        "simulations": error_summary
    }

    # -------------------------------------------------------------
    # STAGE 6: FROZEN BASELINE & PUBLICATION GATE AUDIT
    # -------------------------------------------------------------
    print("\n--- STAGE 6: Frozen Baseline & Publication Gate Audit ---")
    def get_sha256(path: str) -> str:
        with open(path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()

    expected_hashes = {
        "magspread-preview.html": "a7679251c49d4f30485a90e36191eeaf6185313625e264878273b1e79a6577d4",
        "magspread.css": "82d7c64209e3b726d7e0c7cf4e29524ad336c03b151369ff360aba82b6ce49ba",
        "magspread.js": "860a21903aa03ab31ec597d8cff8fcdb028b63b1d8ca10adffb90318dbf2ce6c",
        "edition-data.json": "c95a591a4b695e51f980737d0f5c3a85e498023292c1c62e63daed0bf3dbe67a",
        "edition-data.js": "9d819ad6323ac42e13eabb16c5b5150cf306192739524bd6317d1efbf8f9a694"
    }

    baseline_audit = {}
    for fn, exp_hash in expected_hashes.items():
        fpath = os.path.join("pilot-output", fn)
        cur_hash = get_sha256(fpath)
        assert cur_hash == exp_hash, f"Baseline hash mismatch on {fn}!"
        baseline_audit[fn] = {"sha256": cur_hash, "status": "MATCH_100%"}
        print(f"Protected file {fn}: SHA-256 match 100% ({cur_hash[:16]}...)")

    # Publication Gate check on edition-data.json
    with open("pilot-output/edition-data.json", "r", encoding="utf-8") as f:
        ed_data = json.load(f)

    gate = ed_data.get("publicationGateStatus", {})
    news_list = ed_data.get("eligibleNewsList", [])
    c0_24 = sum(1 for e in news_list if e.get("strictCombinedTimeWindow") == "0–24h" or e.get("researchWindowBucket") == "0–24h")
    freshness = (c0_24 / max(1, len(news_list))) * 100

    assert len(news_list) == 21, f"Expected 21 news items, got {len(news_list)}"
    assert c0_24 == 11, f"Expected 11 items in 0-24h, got {c0_24}"
    assert f"{freshness:.2f}%" == "52.38%", f"Expected 52.38% freshness, got {freshness:.2f}%"
    gate_status = gate.get("status") or gate.get("gateStatus")
    assert gate_status == "FAIL_SHORTFALL_24H_PREVIEW_ONLY"
    assert gate.get("publicBadgeLabel") == "PREVIEW — CHƯA XUẤT BẢN"
    print(f"Publication Gate confirmed LOCKED: {gate_status} (Badge: {gate.get('publicBadgeLabel')}, Freshness: 52.38%, 11/21 items).")

    summary["stages"]["stage6_baseline_and_gate"] = {
        "status": "PASS",
        "baselineHashes": baseline_audit,
        "publicationGate": {
            "eligibleCount": len(news_list),
            "count0To24h": c0_24,
            "freshnessRatio": "52.38%",
            "gateStatus": gate_status,
            "publicBadgeLabel": gate.get("publicBadgeLabel"),
            "isLocked": True
        }
    }

    # Final verdict
    summary["verdict"] = "FULL_SYNC_PASS"
    out_summary_path = os.path.join("pilot-output", "phase04b-sheets-staging", "full_sync_execution_summary.json")
    with open(out_summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 70)
    print("FULL ARCHIVE STAGING SYNC COMPLETED SUCCESSFULLY (FULL_SYNC_PASS)")
    print(f"Execution summary saved to: {out_summary_path}")
    print("=" * 70)
    return summary


if __name__ == "__main__":
    run_full_sync()
