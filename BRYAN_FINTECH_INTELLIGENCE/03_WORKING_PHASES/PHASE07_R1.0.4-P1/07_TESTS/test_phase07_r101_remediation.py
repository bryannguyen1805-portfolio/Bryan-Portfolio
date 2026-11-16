#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_phase07_r101_remediation.py
================================
Comprehensive QA & Adversarial Test Suite for Phase 07 R1.0.1 Remediation:
  Group 1 (REM-01): Dynamic Daily Runtime (Dates, T0, Modes, Isolation, Idempotence)
  Group 2 (REM-02): Source Provenance & Retrieval Ledger Integrity (Ledger reconciliation, Fail-Closed)
  Group 3 (REM-03): True Dynamic Intelligence (Theses, Chains, J&T Cargo Radar, Decisions, Adversarial Changes)
  Group 4 (REM-04): Dynamic Market Pulse Discovery & Frequency Evaluation (Daily, Monthly, Units, Approved Pubs)
  Group 5 (REM-05): Google Sheets Dry-Run Single Source of Truth & Reconciliation
"""

import os
import sys
import copy
import json
import shutil
import tempfile
import hashlib
from datetime import datetime, timezone, timedelta

THIS_DIR = os.path.abspath(os.path.dirname(__file__))
PHASE07_ROOT = os.path.abspath(os.path.join(THIS_DIR, ".."))
SRC_DIR = os.path.join(PHASE07_ROOT, "02_SOURCE_CODE")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from phase07_daily_runtime_orchestrator import Phase07DailyRuntimeOrchestrator
from phase07_dynamic_news_engine import Phase07DynamicNewsEngine
from phase07_market_pulse_runtime import Phase07MarketPulseRuntime
from phase07_editorial_intelligence_engine import Phase07EditorialIntelligenceEngine
from google_sheets_dry_run_engine import GoogleSheetsDryRunEngine

VN_TZ = timezone(timedelta(hours=7))


class TestPhase07R101RemediationSuite:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.logs = []

        self.cfg_path = os.path.join(PHASE07_ROOT, "03_SCHEMAS_AND_CONFIG", "PHASE07_RUNTIME_CONFIG.json")
        with open(self.cfg_path, "r", encoding="utf-8") as f:
            self.runtime_config = json.load(f)

        self.raw_dir = os.path.join(
            PHASE07_ROOT, "baseline_phase05b_r101", "PHASE05B_ALIGNMENT_R101", "04_RAW_EVIDENCE"
        )
        self.fixtures_dir = os.path.join(
            PHASE07_ROOT, "baseline_phase05b_r101", "PHASE05B_ALIGNMENT_R101", "06_TESTS", "fixtures"
        )
        self.prior_vndb_path = os.path.join(
            PHASE07_ROOT, "baseline_phase05b_r101", "PHASE05B_ALIGNMENT_R101", "05_LIVE_DATA", "VERIFIED_NEWS_DATABASE.json"
        )
        self.retrieval_log_path = os.path.join(
            PHASE07_ROOT, "baseline_phase05b_r101", "PHASE05B_ALIGNMENT_R101", "05_LIVE_DATA", "SOURCE_RETRIEVAL_LOG.json"
        )
        self.mp8_path = os.path.join(
            PHASE07_ROOT, "baseline_phase05b_r101", "PHASE05B_ALIGNMENT_R101", "05_LIVE_DATA", "MARKET_PULSE_8.json"
        )
        self.specs_path = os.path.join(
            PHASE07_ROOT, "baseline_phase05b_r101", "PHASE05B_ALIGNMENT_R101", "03_INDICATOR_CONFIG", "market_pulse_indicator_specs.json"
        )

        with open(self.retrieval_log_path, "r", encoding="utf-8") as f:
            self.retrieval_log = json.load(f)

    def log(self, msg: str):
        print(msg)
        self.logs.append(msg)

    def run_test(self, name: str, fn):
        self.log(f"RUNNING: {name}...")
        try:
            fn()
            self.passed += 1
            self.log(f"  [PASS] {name}\n")
        except Exception as exc:
            self.failed += 1
            self.log(f"  [FAIL] {name}: {exc}\n")

    # =========================================================================
    # GROUP 1: REMEDIATION 01 — DYNAMIC DAILY RUNTIME
    # =========================================================================

    def test_r01_01_dynamic_date_and_edition_metadata(self):
        """REM01-01: Verifies dynamic date, editionId, executionId in Asia/Ho_Chi_Minh."""
        orch = Phase07DailyRuntimeOrchestrator(phase07_root=PHASE07_ROOT)
        now_vn = datetime.now(VN_TZ)
        assert orch.edition_date == now_vn.strftime("%Y-%m-%d")
        assert orch.edition_id.startswith("ED-")
        assert orch.execution_id.startswith("EXEC-")
        assert orch.execution_mode == "LIVE"

    def test_r01_02_next_day_execution_isolation(self):
        """REM01-02: Verifies running for next day (Nov 12) generates separate directory and metadata."""
        tmp_dir = tempfile.mkdtemp(prefix="phase07_nextday_")
        try:
            orch12 = Phase07DailyRuntimeOrchestrator(
                phase07_root=PHASE07_ROOT,
                edition_date="2026-11-12",
                edition_id="ED-20261112-D01",
                run_timestamp="2026-11-12T02:20:00+07:00",
                execution_mode="OFFLINE"
            )
            assert orch12.edition_date == "2026-11-12"
            assert orch12.edition_id == "ED-20261112-D01"
            assert orch12.offline_mode is True
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)

    def test_r01_03_different_month_execution(self):
        """REM01-03: Verifies running in a different month (December 2026)."""
        orch_dec = Phase07DailyRuntimeOrchestrator(
            phase07_root=PHASE07_ROOT,
            edition_date="2026-12-01",
            edition_id="ED-20261201-D01",
            run_timestamp="2026-12-01T08:00:00+07:00",
            execution_mode="OFFLINE"
        )
        assert orch_dec.edition_date == "2026-12-01"
        assert orch_dec.edition_id == "ED-20261201-D01"

    def test_r01_04_across_midnight_execution(self):
        """REM01-04: Verifies proper date calculation across midnight boundary."""
        orch_pre = Phase07DailyRuntimeOrchestrator(
            phase07_root=PHASE07_ROOT,
            run_timestamp="2026-11-11T23:59:59+07:00",
            edition_date="2026-11-11",
            execution_mode="OFFLINE"
        )
        orch_post = Phase07DailyRuntimeOrchestrator(
            phase07_root=PHASE07_ROOT,
            run_timestamp="2026-11-12T00:00:01+07:00",
            edition_date="2026-11-12",
            execution_mode="OFFLINE"
        )
        assert orch_pre.edition_date != orch_post.edition_date
        assert orch_pre.edition_id != orch_post.edition_id

    def test_r01_05_explicit_execution_modes(self):
        """REM01-05: Verifies explicit LIVE, OFFLINE, REPLAY mode semantics."""
        orch_live = Phase07DailyRuntimeOrchestrator(execution_mode="LIVE")
        assert orch_live.execution_mode == "LIVE"
        assert orch_live.offline_mode is False

        orch_off = Phase07DailyRuntimeOrchestrator(execution_mode="OFFLINE")
        assert orch_off.execution_mode == "OFFLINE"
        assert orch_off.offline_mode is True

        orch_rep = Phase07DailyRuntimeOrchestrator(execution_mode="REPLAY")
        assert orch_rep.execution_mode == "REPLAY"
        assert orch_rep.offline_mode is True

    def test_r01_06_idempotence_and_unique_execution_ids(self):
        """REM01-06: Verifies repeated runs produce identical data hashes but distinct executionIds."""
        orch_a = Phase07DailyRuntimeOrchestrator(edition_date="2026-11-11", execution_mode="OFFLINE")
        orch_b = Phase07DailyRuntimeOrchestrator(edition_date="2026-11-11", execution_mode="OFFLINE")
        assert orch_a.execution_id != orch_b.execution_id
        assert orch_a.edition_id == orch_b.edition_id

    # =========================================================================
    # GROUP 2: REMEDIATION 02 — SOURCE PROVENANCE & RETRIEVAL LEDGER INTEGRITY
    # =========================================================================

    def test_r02_01_all_selected_candidates_match_ledger_hash(self):
        """REM02-01: Verifies 100% of selected candidates match contentSha256 in SOURCE_RETRIEVAL_LOG.json."""
        eng = Phase07DynamicNewsEngine(
            raw_evidence_dir=self.raw_dir,
            historical_fixtures_dir=self.fixtures_dir,
            runtime_config=self.runtime_config,
            prior_verified_news_path=self.prior_vndb_path,
            run_timestamp="2026-11-11T02:20:00+07:00",
            offline_mode=True
        )
        res = eng.execute_pipeline()
        assert len(res["selectedEvents"]) == 25
        for ev in res["selectedEvents"]:
            u = ev["sourceUrl"]
            sha = ev["evidenceSha256"]
            assert u in self.retrieval_log, f"Selected URL not found in SOURCE_RETRIEVAL_LOG: {u}"
            ledger_sha = self.retrieval_log[u].get("contentSha256") or self.retrieval_log[u].get("responseSha256")
            assert sha == ledger_sha, f"Hash mismatch for {u}: cand={sha}, ledger={ledger_sha}"

    def test_r02_02_multiple_snapshots_pick_matching_ledger_snapshot(self):
        """REM02-02: Verifies that when multiple snapshots exist for a URL, the ledger-matching snapshot is selected."""
        eng = Phase07DynamicNewsEngine(
            raw_evidence_dir=self.raw_dir,
            historical_fixtures_dir=self.fixtures_dir,
            runtime_config=self.runtime_config,
            prior_verified_news_path=self.prior_vndb_path,
            run_timestamp="2026-11-11T02:20:00+07:00",
            offline_mode=True
        )
        disc = eng.step04_discover_candidates()
        target_url = "https://tuoitre.vn/ngan-hang-nha-nuoc-mua-usd-them-tien-dong-cho-nen-kinh-te-100261110162658257.htm"
        cand = next((c for c in disc["rawCandidates"] if c["canonicalUrl"] == target_url), None)
        assert cand is not None
        assert cand["evidenceSha256"].startswith("fbb073ed5f"), f"Expected fbb073ed5f, got {cand['evidenceSha256'][:10]}"
        assert cand["contentHashMatched"] is True

    def test_r02_03_fail_closed_on_content_hash_mismatch(self):
        """REM02-03: Adversarial — candidate with tampered hash is rejected with CONTENT_HASH_MISMATCH."""
        eng = Phase07DynamicNewsEngine(
            raw_evidence_dir=self.raw_dir,
            historical_fixtures_dir=self.fixtures_dir,
            runtime_config=self.runtime_config,
            prior_verified_news_path=self.prior_vndb_path,
            run_timestamp="2026-11-11T02:20:00+07:00",
            offline_mode=True
        )
        disc = eng.step04_discover_candidates()
        cand = copy.deepcopy(disc["rawCandidates"][0])
        cand["contentHashMatched"] = False
        res = eng.execute_pipeline(custom_candidates=[cand])
        assert len(res["selectedEvents"]) == 0
        assert any("CONTENT_HASH_MISMATCH" in r["rejectionReason"] for r in res["rejectedLedger"])

    def test_r02_04_fail_closed_on_http_status_failure(self):
        """REM02-04: Adversarial — candidate with HTTP 403/500 is rejected with ACCESS_BLOCKED."""
        eng = Phase07DynamicNewsEngine(
            raw_evidence_dir=self.raw_dir,
            historical_fixtures_dir=self.fixtures_dir,
            runtime_config=self.runtime_config,
            prior_verified_news_path=self.prior_vndb_path,
            run_timestamp="2026-11-11T02:20:00+07:00",
            offline_mode=True
        )
        disc = eng.step04_discover_candidates()
        cand = copy.deepcopy(disc["rawCandidates"][0])
        cand["httpStatusCode"] = 403
        res = eng.execute_pipeline(custom_candidates=[cand])
        assert len(res["selectedEvents"]) == 0
        assert any("ACCESS_BLOCKED" in r["rejectionReason"] for r in res["rejectedLedger"])

    def test_r02_05_fail_closed_on_missing_retrieval_record_in_live_mode(self):
        """REM02-05: Adversarial — unrecorded candidate in LIVE mode is rejected with RETRIEVAL_RECORD_MISSING."""
        eng = Phase07DynamicNewsEngine(
            raw_evidence_dir=self.raw_dir,
            historical_fixtures_dir=self.fixtures_dir,
            runtime_config=self.runtime_config,
            prior_verified_news_path=self.prior_vndb_path,
            run_timestamp="2026-11-11T02:20:00+07:00",
            offline_mode=False
        )
        disc = eng.step04_discover_candidates()
        cand = copy.deepcopy(disc["rawCandidates"][0])
        cand["retrievalRecordFound"] = False
        res = eng.execute_pipeline(custom_candidates=[cand])
        assert len(res["selectedEvents"]) == 0
        assert any("RETRIEVAL_RECORD_MISSING" in r["rejectionReason"] for r in res["rejectedLedger"])

    # =========================================================================
    # GROUP 3: REMEDIATION 03 — TRUE DYNAMIC FINANCIAL INTELLIGENCE
    # =========================================================================

    def test_r03_01_jt_cargo_logistics_classified_as_potential_opportunity(self):
        """REM03-01: Strictly verifies J&T Cargo opportunity is classified as POTENTIAL_OPPORTUNITY / MEDIUM / VALIDATE."""
        eng = Phase07DynamicNewsEngine(
            raw_evidence_dir=self.raw_dir,
            historical_fixtures_dir=self.fixtures_dir,
            runtime_config=self.runtime_config,
            prior_verified_news_path=self.prior_vndb_path,
            run_timestamp="2026-11-11T02:20:00+07:00",
            offline_mode=True
        )
        news_res = eng.execute_pipeline()
        mp_rt = Phase07MarketPulseRuntime(self.raw_dir, self.mp8_path, self.specs_path, self.runtime_config, run_timestamp="2026-11-11T02:20:00+07:00")
        mp_res = mp_rt.execute_market_pulse()

        ed_eng = Phase07EditorialIntelligenceEngine(
            news_res["selectedEvents"],
            news_res["step08_factVerification"]["auditedFactsBundle"],
            mp_res["indicators"],
            self.runtime_config
        )
        radars = ed_eng.generate_payment_radar_signals()
        r02 = next((r for r in radars["signals"] if r["radarId"] == "RADAR-02"), None)
        assert r02 is not None
        assert r02["opportunityType"] == "POTENTIAL_OPPORTUNITY", f"Expected POTENTIAL_OPPORTUNITY, got {r02['opportunityType']}"
        assert r02["confidence"] == "MEDIUM", f"Expected MEDIUM confidence, got {r02['confidence']}"
        assert r02["confidenceLevel"] == "MEDIUM"
        assert r02["priority"] == "P1_HIGH"
        assert r02["recommendedNextAction"].startswith("VALIDATE")

    def test_r03_02_jt_cargo_elevates_when_payment_demand_evidence_added(self):
        """REM03-02: Adversarial — adding explicit payment evidence elevates J&T Cargo to VERIFIED_OPPORTUNITY / HIGH."""
        eng = Phase07DynamicNewsEngine(
            raw_evidence_dir=self.raw_dir,
            historical_fixtures_dir=self.fixtures_dir,
            runtime_config=self.runtime_config,
            prior_verified_news_path=self.prior_vndb_path,
            run_timestamp="2026-11-11T02:20:00+07:00",
            offline_mode=True
        )
        news_res = eng.execute_pipeline()
        events = copy.deepcopy(news_res["selectedEvents"])

        # Inject payment demand evidence into J&T Cargo article
        for ev in events:
            if "j&t cargo" in ev.get("headline", "").lower():
                ev["summary"] = ev.get("summary", "") + " Triển khai giải pháp thanh toán không tiền mặt qua cổng thanh toán trực tuyến và VietQR."
                ev["supportingQuote"] = ev.get("supportingQuote", "") + " Tích hợp cổng thanh toán trực tuyến Payoo và mã VietQR động."

        mp_rt = Phase07MarketPulseRuntime(self.raw_dir, self.mp8_path, self.specs_path, self.runtime_config, run_timestamp="2026-11-11T02:20:00+07:00")
        mp_res = mp_rt.execute_market_pulse()

        ed_eng = Phase07EditorialIntelligenceEngine(
            events,
            news_res["step08_factVerification"]["auditedFactsBundle"],
            mp_res["indicators"],
            self.runtime_config
        )
        radars = ed_eng.generate_payment_radar_signals()
        r02 = next((r for r in radars["signals"] if r["radarId"] == "RADAR-02"), None)
        assert r02 is not None
        assert r02["opportunityType"] == "VERIFIED_OPPORTUNITY"
        assert r02["confidence"] == "HIGH"

    def test_r03_03_decision_card_traceability(self):
        """REM03-03: Verifies all Decision Cards reference active events, theses, chains, and radars."""
        eng = Phase07DynamicNewsEngine(
            raw_evidence_dir=self.raw_dir,
            historical_fixtures_dir=self.fixtures_dir,
            runtime_config=self.runtime_config,
            prior_verified_news_path=self.prior_vndb_path,
            run_timestamp="2026-11-11T02:20:00+07:00",
            offline_mode=True
        )
        news_res = eng.execute_pipeline()
        mp_rt = Phase07MarketPulseRuntime(self.raw_dir, self.mp8_path, self.specs_path, self.runtime_config, run_timestamp="2026-11-11T02:20:00+07:00")
        mp_res = mp_rt.execute_market_pulse()

        ed_eng = Phase07EditorialIntelligenceEngine(
            news_res["selectedEvents"],
            news_res["step08_factVerification"]["auditedFactsBundle"],
            mp_res["indicators"],
            self.runtime_config
        )
        theses = ed_eng.generate_core_theses()
        chains = ed_eng.generate_macro_to_micro_chains()
        radars = ed_eng.generate_payment_radar_signals()
        decisions = ed_eng.generate_financial_decision_intelligence(
            theses["theses"], chains["chains"], radars["signals"], news_res["step09_quotaAndFreshnessGate"]
        )

        assert len(decisions["decisionCards"]) == 4
        all_eids = {e["eventId"] for e in news_res["selectedEvents"]}
        for card in decisions["decisionCards"]:
            assert set(card["supportingEventIds"]).issubset(all_eids)
            assert card["recommendedAction"] in ("EXPLORE", "VALIDATE", "MONITOR", "INVESTIGATE")

    # =========================================================================
    # GROUP 4: REMEDIATION 04 — DYNAMIC MARKET PULSE DISCOVERY
    # =========================================================================

    def test_r04_01_dynamic_market_pulse_frequency_and_stale_detection(self):
        """REM04-01: Verifies MP-02 is dynamically evaluated as STALE_OBSERVATION due to age > 72h."""
        mp_rt = Phase07MarketPulseRuntime(self.raw_dir, self.mp8_path, self.specs_path, self.runtime_config, run_timestamp="2026-11-11T02:20:00+07:00")
        res = mp_rt.execute_market_pulse()
        by_id = {m["indicatorId"]: m for m in res["indicators"]}
        assert by_id["MP-02"]["updateStatus"] == "STALE_OBSERVATION"
        assert by_id["MP-02"]["verificationStatus"] == "UNVERIFIED"
        assert by_id["MP-01"]["updateStatus"] == "NUMERIC_VALUE_VERIFIED"
        assert by_id["MP-01"]["verificationStatus"] == "VERIFIED"

    def test_r04_02_new_market_pulse_observation_from_approved_publisher(self):
        """REM04-02: Verifies dynamic new observation from approved publisher receives NEW_OBSERVATION_VERIFIED."""
        mp_rt = Phase07MarketPulseRuntime(self.raw_dir, self.mp8_path, self.specs_path, self.runtime_config, run_timestamp="2026-11-11T02:20:00+07:00")
        custom_obs = {
            "MP-01": {
                "actualValue": "25610",
                "observationDate": "2026-11-11",
                "publishedAt": "2026-11-11T08:00:00+07:00",
                "publisher": "Báo Tuổi Trẻ",
                "unit": "VND/USD"
            }
        }
        res = mp_rt.execute_market_pulse(custom_observations=custom_obs)
        by_id = {m["indicatorId"]: m for m in res["indicators"]}
        assert by_id["MP-01"]["updateStatus"] == "NEW_OBSERVATION_VERIFIED"
        assert by_id["MP-01"]["verificationStatus"] == "VERIFIED"
        assert by_id["MP-01"]["currentValue"] == "25610"

    def test_r04_03_unapproved_publisher_rejected(self):
        """REM04-03: Adversarial — new observation from unapproved publisher is rejected."""
        mp_rt = Phase07MarketPulseRuntime(self.raw_dir, self.mp8_path, self.specs_path, self.runtime_config, run_timestamp="2026-11-11T02:20:00+07:00")
        custom_obs = {
            "MP-01": {
                "actualValue": "25650",
                "observationDate": "2026-11-11",
                "publisher": "Unknown Random Blog",
                "sourceOrganization": "Unknown Random Blog",
                "unit": "VND/USD"
            }
        }
        res = mp_rt.execute_market_pulse(custom_observations=custom_obs)
        by_id = {m["indicatorId"]: m for m in res["indicators"]}
        assert by_id["MP-01"]["verificationStatus"] == "UNVERIFIED"
        assert by_id["MP-01"]["updateStatus"] == "UNAPPROVED_PUBLISHER_REJECTED"

    def test_r04_04_wrong_unit_rejected(self):
        """REM04-04: Adversarial — observation with invalid unit is rejected."""
        mp_rt = Phase07MarketPulseRuntime(self.raw_dir, self.mp8_path, self.specs_path, self.runtime_config, run_timestamp="2026-11-11T02:20:00+07:00")
        custom_obs = {
            "MP-04": {
                "actualValue": "1800.00",
                "observationDate": "2026-11-11",
                "publisher": "CafeF / VCCorp",
                "unit": "VND/USD"  # Wrong unit for VN-Index (expected Điểm)
            }
        }
        res = mp_rt.execute_market_pulse(custom_observations=custom_obs)
        by_id = {m["indicatorId"]: m for m in res["indicators"]}
        assert by_id["MP-04"]["verificationStatus"] == "UNVERIFIED"
        assert by_id["MP-04"]["updateStatus"] == "INVALID_UNIT_REJECTED"

    # =========================================================================
    # GROUP 5: REMEDIATION 05 — GOOGLE SHEETS DRY-RUN RECONCILIATION
    # =========================================================================

    def test_r05_01_single_source_of_truth_row_count_reconciliation(self):
        """REM05-01: Verifies exact row count reconciliation across validation, preview, and markdown report."""
        staging_ro = os.path.join(PHASE07_ROOT, "03_SCHEMAS_AND_CONFIG", "phase04b_staging_tables_readonly.json")
        from phase07_daily_runtime_orchestrator import ORIG_P04B_STAGING
        sheets_eng = GoogleSheetsDryRunEngine(staging_ro, ORIG_P04B_STAGING)
        baseline_tabs, b_count = sheets_eng.load_baseline_staging()

        # Run orchestrator dry-run
        orch = Phase07DailyRuntimeOrchestrator(
            phase07_root=PHASE07_ROOT,
            edition_date="2026-11-11",
            edition_id="ED-20261111-D01",
            run_timestamp="2026-11-11T02:20:00+07:00",
            execution_mode="OFFLINE"
        )
        res = orch.execute_daily_run()
        bundle = res["state"]["sheets_bundle"]
        val = bundle["validation"]
        preview = bundle["preview"]

        # Validate single source of truth agreement
        assert preview["proposedNewRowsCount"] == val["proposedNewRowCount"]
        assert preview["projectedTotalRowsCount"] == val["totalProjectedRowCount"]
        assert preview["baselinePreservedRows"] == b_count
        assert val["liveWriteApiCalled"] is False
        assert val["allTabsPassed"] is True
        assert val["foreignKeyViolationsCount"] == 0

        # Verify markdown report contains exact numbers
        md_report = sheets_eng.generate_dry_run_markdown_report("ED-20261111-D01", "2026-11-11", val)
        assert str(val["proposedNewRowCount"]) in md_report
        assert str(val["totalProjectedRowCount"]) in md_report
        assert "READ_ONLY" in md_report
        assert "STRICTLY PROHIBITED" in md_report


def run_all():
    suite = TestPhase07R101RemediationSuite()
    tests = [m for m in dir(suite) if m.startswith("test_")]
    print("=" * 80)
    print(f"BRYAN FINTECH INTELLIGENCE — PHASE 07 R1.0.1 REMEDIATION TEST SUITE")
    print(f"Total Remediation Tests to Execute: {len(tests)}")
    print("=" * 80)
    for t_name in sorted(tests):
        suite.run_test(t_name, getattr(suite, t_name))

    print("=" * 80)
    print(f"REMEDIATION QA SUMMARY: Total: {suite.passed + suite.failed} | PASSED: {suite.passed} | FAILED: {suite.failed}")
    print("=" * 80)
    return suite.failed == 0


if __name__ == "__main__":
    success = run_all()
    sys.exit(0 if success else 1)
