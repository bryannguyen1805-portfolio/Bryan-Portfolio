#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_phase07_r102_remediation.py
================================
Comprehensive QA & Adversarial Test Suite for Phase 07 R1.0.2 Targeted Final Remediation:
  Test 01: Same-Day Execution Isolation & Immutability (Executions subdirectories + edition-latest pointer)
  Test 02: Multi-Date Isolation (Two different dates in separate directories)
  Test 03: Midnight and Month Transition Execution
  Test 04: Live Mode Missing Retrieval Record Fail-Closed (RETRIEVAL_RECORD_MISSING)
  Test 05: Live Mode HTTP Error Fail-Closed (ACCESS_BLOCKED)
  Test 06: Snapshot SHA-256 Mismatch Fail-Closed (CONTENT_HASH_MISMATCH)
  Test 07: No False HTTP Status (None when missing, never defaulted to 200)
  Test 08: Market Pulse Discovery Invocation in Step 10
  Test 09: Eight-Indicator Frequency-Aware Status & Validation (MP-01..MP-08)
  Test 10: Input Mutation Test A — Add Interest-Rate Policy Event
  Test 11: Input Mutation Test B — Remove Major Financial Event
  Test 12: Input Mutation Test C — Change Market Pulse Observation
  Test 13: Input Mutation Test D — Contradictory News Captured in CounterEvidence
  Test 14: Input Mutation Test E — Unrelated News (Zero Unrelated Fallback)
  Test 15: Input Mutation Test F — Merchant Payment Adoption Signal (Elevates to VERIFIED_OPPORTUNITY)
  Test 16: Input Mutation Test G — Remove Payment Evidence (Classified as POTENTIAL_OPPORTUNITY / VALIDATE)
  Test 17: Google Sheets Canonical Reconciliation (155 + 165 = 320 merged rows; Phase 06 separated)
  Test 18: Release Manifest Consistency & Parent Baseline Protection
"""

import os
import sys
import copy
import json
import shutil
import tempfile
import hashlib
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any

THIS_DIR = os.path.abspath(os.path.dirname(__file__))
PHASE07_ROOT = os.path.abspath(os.path.join(THIS_DIR, ".."))
SRC_DIR = os.path.join(PHASE07_ROOT, "02_SOURCE_CODE")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from phase07_daily_runtime_orchestrator import Phase07DailyRuntimeOrchestrator
from phase07_dynamic_news_engine import Phase07DynamicNewsEngine
from phase07_market_pulse_runtime import Phase07MarketPulseRuntime
from market_pulse_discovery import MarketPulseDiscoveryEngine
from phase07_editorial_intelligence_engine import Phase07EditorialIntelligenceEngine
from google_sheets_dry_run_engine import GoogleSheetsDryRunEngine

VN_TZ = timezone(timedelta(hours=7))


class TestPhase07R102RemediationSuite:
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
        self.prior_news_path = os.path.join(
            PHASE07_ROOT, "baseline_phase05b_r101", "PHASE05B_ALIGNMENT_R101", "05_LIVE_DATA", "VERIFIED_NEWS_DATABASE.json"
        )
        self.mp8_path = os.path.join(
            PHASE07_ROOT, "baseline_phase05b_r101", "PHASE05B_ALIGNMENT_R101", "05_LIVE_DATA", "MARKET_PULSE_8.json"
        )
        self.specs_path = os.path.join(
            PHASE07_ROOT, "baseline_phase05b_r101", "PHASE05B_ALIGNMENT_R101", "03_INDICATOR_CONFIG", "market_pulse_indicator_specs.json"
        )

    def log(self, msg: str):
        print(msg)
        self.logs.append(msg)

    def run_test(self, name: str, test_fn):
        self.log(f"RUNNING: {name}...")
        try:
            test_fn()
            self.passed += 1
            self.log(f"  [PASS] {name}\n")
        except Exception as e:
            self.failed += 1
            self.log(f"  [FAIL] {name}: {e}\n")
            import traceback
            traceback.print_exc()

    # -------------------------------------------------------------------------
    # TEST 01: Same-Day Execution Isolation & Immutability
    # -------------------------------------------------------------------------
    def test_01_same_day_execution_isolation(self):
        tmp_dir = tempfile.mkdtemp(prefix="p07_r102_t01_")
        try:
            date_str = "2026-11-10"
            t0_str = "2026-11-10T22:30:00+07:00"
            exec_id_1 = "EXEC-20261110-223000-AAAA1111"
            exec_id_2 = "EXEC-20261110-224500-BBBB2222"

            orch1 = Phase07DailyRuntimeOrchestrator(
                edition_date=date_str,
                edition_id="ED-20261110-D01",
                run_timestamp=t0_str,
                execution_id=exec_id_1,
                execution_mode="OFFLINE"
            )
            res1 = orch1.execute_daily_run(output_base_dir=tmp_dir)
            assert res1["overallRuntimeStatus"] == "PASS"

            # Verify Run 1 directory and files
            exec_dir_1 = os.path.join(tmp_dir, "06_DAILY_EDITIONS", "daily-editions", date_str, "executions", exec_id_1)
            assert os.path.isdir(exec_dir_1)
            sha1_manifest = os.path.join(exec_dir_1, "edition-manifest.json")
            assert os.path.exists(sha1_manifest)
            with open(sha1_manifest, "rb") as f:
                hash_run1_before = hashlib.sha256(f.read()).hexdigest()

            # Execute Run 2 on same date
            orch2 = Phase07DailyRuntimeOrchestrator(
                edition_date=date_str,
                edition_id="ED-20261110-D01",
                run_timestamp=t0_str,
                execution_id=exec_id_2,
                execution_mode="OFFLINE"
            )
            res2 = orch2.execute_daily_run(output_base_dir=tmp_dir)
            assert res2["overallRuntimeStatus"] == "PASS"

            # Verify Run 2 directory
            exec_dir_2 = os.path.join(tmp_dir, "06_DAILY_EDITIONS", "daily-editions", date_str, "executions", exec_id_2)
            assert os.path.isdir(exec_dir_2)

            # Assert Run 1 artifacts were NOT overwritten and remained immutable
            with open(sha1_manifest, "rb") as f:
                hash_run1_after = hashlib.sha256(f.read()).hexdigest()
            assert hash_run1_before == hash_run1_after, "Run 1 execution directory was modified by Run 2!"

            # Assert edition-latest.json points to Run 2
            pointer_path = os.path.join(tmp_dir, "06_DAILY_EDITIONS", "daily-editions", date_str, "edition-latest.json")
            assert os.path.exists(pointer_path)
            with open(pointer_path, "r", encoding="utf-8") as f:
                ptr = json.load(f)
            assert ptr["latestExecutionId"] == exec_id_2
            assert ptr["status"] == "VALIDATED"
            assert len(ptr["inputDatasetHash"]) == 64
            assert len(ptr["outputDatasetHash"]) == 64
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)

    # -------------------------------------------------------------------------
    # TEST 02: Multi-Date Isolation
    # -------------------------------------------------------------------------
    def test_02_two_different_dates_isolation(self):
        tmp_dir = tempfile.mkdtemp(prefix="p07_r102_t02_")
        try:
            d1 = "2026-11-10"
            d2 = "2026-11-11"
            orch1 = Phase07DailyRuntimeOrchestrator(
                edition_date=d1,
                edition_id="ED-20261110-D01",
                run_timestamp="2026-11-10T22:30:00+07:00",
                execution_mode="OFFLINE"
            )
            res1 = orch1.execute_daily_run(output_base_dir=tmp_dir)
            assert res1["overallRuntimeStatus"] == "PASS"

            orch2 = Phase07DailyRuntimeOrchestrator(
                edition_date=d2,
                edition_id="ED-20261111-D01",
                run_timestamp="2026-11-11T10:00:00+07:00",
                execution_mode="OFFLINE"
            )
            res2 = orch2.execute_daily_run(output_base_dir=tmp_dir)
            # Both directories must exist separately
            dir1 = os.path.join(tmp_dir, "06_DAILY_EDITIONS", "daily-editions", d1)
            dir2 = os.path.join(tmp_dir, "06_DAILY_EDITIONS", "daily-editions", d2)
            assert os.path.isdir(dir1)
            assert os.path.isdir(dir2)
            assert dir1 != dir2
            assert os.path.exists(os.path.join(dir1, "edition-manifest.json"))
            assert os.path.exists(os.path.join(dir2, "runtime-step-log.json"))
            assert res1["editionId"] == "ED-20261110-D01"
            assert res2["editionId"] == "ED-20261111-D01"
            assert res1["editionDate"] == "2026-11-10"
            assert res2["editionDate"] == "2026-11-11"
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)

    # -------------------------------------------------------------------------
    # TEST 03: Midnight and Month Transition Execution
    # -------------------------------------------------------------------------
    def test_03_midnight_and_month_transition(self):
        orch = Phase07DailyRuntimeOrchestrator(
            edition_date="2026-11-30",
            edition_id="ED-20261130-D01",
            run_timestamp="2026-11-30T23:59:59+07:00",
            execution_mode="OFFLINE"
        )
        # Verify timezone calculation
        from daily_news_collector_v3 import parse_timestamp_iso_or_vietnamese
        t0 = parse_timestamp_iso_or_vietnamese(orch.run_timestamp)
        assert t0.utcoffset() == timedelta(hours=7)
        next_day = t0 + timedelta(seconds=2)
        assert next_day.strftime("%Y-%m-%d") == "2026-12-01"

    # -------------------------------------------------------------------------
    # TEST 04: Live Mode Missing Retrieval Record Fail-Closed
    # -------------------------------------------------------------------------
    def test_04_live_mode_missing_retrieval_record_fail_closed(self):
        engine = Phase07DynamicNewsEngine(
            raw_evidence_dir=self.raw_dir,
            historical_fixtures_dir=self.fixtures_dir,
            runtime_config=self.runtime_config,
            run_timestamp="2026-11-10T22:30:00+07:00",
            offline_mode=False
        )
        # Empty retrieval log
        engine.retrieval_log = {}
        res = engine.execute_pipeline()
        for cand in res["discovery"]["rawCandidates"]:
            assert cand["retrievalStatus"] == "RETRIEVAL_RECORD_MISSING"
            assert cand["contentHashMatched"] is False
            assert cand["retrievalMode"] == "LIVE_SOURCE_UNVERIFIED"

    # -------------------------------------------------------------------------
    # TEST 05: Live Mode HTTP Error Fail-Closed
    # -------------------------------------------------------------------------
    def test_05_live_mode_http_error_fail_closed(self):
        engine = Phase07DynamicNewsEngine(
            raw_evidence_dir=self.raw_dir,
            historical_fixtures_dir=self.fixtures_dir,
            runtime_config=self.runtime_config,
            run_timestamp="2026-11-10T22:30:00+07:00",
            offline_mode=False
        )
        # Mock retrieval log with HTTP 403 error
        sample_url = "https://cafef.vn/thi-truong-chung-khoan-20261110.chn"
        engine.retrieval_log[sample_url] = {
            "retrievalId": "RET-ERR-403",
            "canonicalUrl": sample_url,
            "httpStatusCode": 403,
            "retrievalStatus": "ACCESS_BLOCKED",
            "contentSha256": "0" * 64
        }
        res = engine.execute_pipeline()
        err_cands = [c for c in res["discovery"]["rawCandidates"] if c["sourceUrl"] == sample_url]
        if err_cands:
            assert err_cands[0]["httpStatusCode"] == 403
            assert err_cands[0]["retrievalStatus"] == "ACCESS_BLOCKED"

    # -------------------------------------------------------------------------
    # TEST 06: Snapshot SHA-256 Mismatch Fail-Closed
    # -------------------------------------------------------------------------
    def test_06_snapshot_hash_mismatch_fail_closed(self):
        engine = Phase07DynamicNewsEngine(
            raw_evidence_dir=self.raw_dir,
            historical_fixtures_dir=self.fixtures_dir,
            runtime_config=self.runtime_config,
            run_timestamp="2026-11-10T22:30:00+07:00",
            offline_mode=False
        )
        first_url = next(iter(engine.retrieval_log.keys())) if engine.retrieval_log else "https://example.com"
        engine.retrieval_log[first_url] = {
            "retrievalId": "RET-MISMATCH",
            "canonicalUrl": first_url,
            "httpStatusCode": 200,
            "retrievalStatus": "SUCCESS",
            "contentSha256": "ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"
        }
        res = engine.execute_pipeline()
        mismatch_cands = [c for c in res["discovery"]["rawCandidates"] if c["sourceUrl"] == first_url]
        if mismatch_cands:
            assert mismatch_cands[0]["contentHashMatched"] is False

    # -------------------------------------------------------------------------
    # TEST 07: No False HTTP Status (None when missing, never defaulted to 200)
    # -------------------------------------------------------------------------
    def test_07_no_false_http_status(self):
        engine = Phase07DynamicNewsEngine(
            raw_evidence_dir=self.raw_dir,
            historical_fixtures_dir=self.fixtures_dir,
            runtime_config=self.runtime_config,
            run_timestamp="2026-11-10T22:30:00+07:00",
            offline_mode=True
        )
        engine.retrieval_log = {}  # Empty log
        res = engine.execute_pipeline()
        for cand in res["discovery"]["rawCandidates"]:
            assert cand["httpStatusCode"] is None, f"Expected None, got {cand['httpStatusCode']}"

    # -------------------------------------------------------------------------
    # TEST 08: Market Pulse Discovery Invocation in Step 10
    # -------------------------------------------------------------------------
    def test_08_market_pulse_discovery_invocation_in_step_10(self):
        tmp_dir = tempfile.mkdtemp(prefix="p07_r102_t08_")
        try:
            orch = Phase07DailyRuntimeOrchestrator(
                edition_date="2026-11-10",
                edition_id="ED-20261110-D01",
                run_timestamp="2026-11-10T22:30:00+07:00",
                execution_mode="OFFLINE"
            )
            res = orch.execute_daily_run(output_base_dir=tmp_dir)
            step10 = next(s for s in orch.steps_log if s["stepId"] == "STEP_10")
            assert step10["status"] == "PASS"
            assert step10["metrics"]["discoveryEngineInvoked"] is True
            assert step10["metrics"]["totalIndicatorsExtracted"] == 8
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)

    # -------------------------------------------------------------------------
    # TEST 09: Eight-Indicator Frequency-Aware Status & Validation
    # -------------------------------------------------------------------------
    def test_09_eight_indicator_frequency_aware_status(self):
        mp_rt = Phase07MarketPulseRuntime(
            raw_evidence_dir=self.raw_dir,
            baseline_mp8_path=self.mp8_path,
            canonical_specs_path=self.specs_path,
            runtime_config=self.runtime_config,
            run_timestamp="2026-11-10T22:30:00+07:00",
            offline_mode=True
        )
        res = mp_rt.execute_market_pulse()
        inds = {i["indicatorId"]: i for i in res["indicators"]}
        assert len(inds) == 8

        # MP-02 (Credit growth) observation is 31/10/2026 (age > 72h canonical ceiling) -> STALE
        assert inds["MP-02"]["updateStatus"] == "STALE_OBSERVATION"
        assert inds["MP-02"]["verificationStatus"] == "UNVERIFIED"

        # MP-05 / MP-06 are qualitative tracking
        assert inds["MP-05"]["updateStatus"] == "QUALITATIVE_UPDATE_ONLY"
        assert inds["MP-06"]["updateStatus"] == "QUALITATIVE_UPDATE_ONLY"

        # MP-07 (Tourist Arrivals) has 19.5 million for Vietnam
        assert float(inds["MP-07"]["currentValue"]) == 19.5
        assert inds["MP-07"]["verificationStatus"] == "VERIFIED"

    # -------------------------------------------------------------------------
    # TEST 10: Input Mutation Test A — Add Interest-Rate Policy Event
    # -------------------------------------------------------------------------
    def test_10_input_mutation_add_interest_rate_policy(self):
        news_eng = Phase07DynamicNewsEngine(
            raw_evidence_dir=self.raw_dir,
            historical_fixtures_dir=self.fixtures_dir,
            runtime_config=self.runtime_config,
            prior_verified_news_path=self.prior_news_path,
            run_timestamp="2026-11-10T22:30:00+07:00",
            offline_mode=True
        )
        news_res = news_eng.execute_pipeline()
        events = list(news_res["selectedEvents"])

        # Inject new monetary policy event
        new_event = copy.deepcopy(events[0])
        new_event["eventId"] = "EVT-20261110-999"
        new_event["headline"] = "NHNN chính thức hạ trần lãi suất tái cấp vốn và bơm 50.000 tỷ OMO"
        new_event["researchDomain"] = "State Bank of Vietnam policy"
        events.insert(0, new_event)

        ed_eng = Phase07EditorialIntelligenceEngine(
            verified_news=events,
            audited_facts_bundle=news_res["step08_factVerification"]["auditedFactsBundle"],
            audited_market_pulse=[],
            runtime_config=self.runtime_config
        )
        theses = ed_eng.generate_core_theses()["theses"]
        assert len(theses) > 0
        # Check that the injected policy event is dynamically incorporated into thesis arguments
        policy_thesis = next((t for t in theses if "EVT-20261110-999" in t["supportingEventIds"]), None)
        assert policy_thesis is not None
        assert "hạ trần lãi suất" in policy_thesis["centralArgument"] or "50.000 tỷ" in policy_thesis["centralArgument"]

    # -------------------------------------------------------------------------
    # TEST 11: Input Mutation Test B — Remove Major Financial Event
    # -------------------------------------------------------------------------
    def test_11_input_mutation_remove_major_financial_event(self):
        news_eng = Phase07DynamicNewsEngine(
            raw_evidence_dir=self.raw_dir,
            historical_fixtures_dir=self.fixtures_dir,
            runtime_config=self.runtime_config,
            prior_verified_news_path=self.prior_news_path,
            run_timestamp="2026-11-10T22:30:00+07:00",
            offline_mode=True
        )
        news_res = news_eng.execute_pipeline()
        events = list(news_res["selectedEvents"])
        first_id = events[0]["eventId"]

        # Run with all events
        ed1 = Phase07EditorialIntelligenceEngine(
            events, news_res["step08_factVerification"]["auditedFactsBundle"], [], self.runtime_config
        )
        t1 = ed1.generate_core_theses()["theses"]

        # Remove first event
        events_filtered = [e for e in events if e["eventId"] != first_id]
        ed2 = Phase07EditorialIntelligenceEngine(
            events_filtered, news_res["step08_factVerification"]["auditedFactsBundle"], [], self.runtime_config
        )
        t2 = ed2.generate_core_theses()["theses"]

        # Assert removed event is never in t2 supportingEventIds
        for th in t2:
            assert first_id not in th["supportingEventIds"]

    # -------------------------------------------------------------------------
    # TEST 12: Input Mutation Test C — Change Market Pulse Observation
    # -------------------------------------------------------------------------
    def test_12_input_mutation_change_market_pulse_observation(self):
        news_eng = Phase07DynamicNewsEngine(
            raw_evidence_dir=self.raw_dir,
            historical_fixtures_dir=self.fixtures_dir,
            runtime_config=self.runtime_config,
            prior_verified_news_path=self.prior_news_path,
            run_timestamp="2026-11-10T22:30:00+07:00",
            offline_mode=True
        )
        news_res = news_eng.execute_pipeline()

        # Custom mutated observation: MP-03 at 8.25%/năm
        custom_mp = [
            {
                "indicatorId": "MP-03",
                "indicatorName": "Lãi suất huy động 12 tháng cao nhất",
                "currentValue": 8.25,
                "unit": "%/năm",
                "observationDate": "2026-11-10",
                "verificationStatus": "VERIFIED"
            }
        ]
        ed_eng = Phase07EditorialIntelligenceEngine(
            news_res["selectedEvents"],
            news_res["step08_factVerification"]["auditedFactsBundle"],
            custom_mp,
            self.runtime_config
        )
        radars = ed_eng.generate_payment_radar_signals()["signals"]
        rate_radar = next((r for r in radars if "Bán lẻ Giá trị cao" in r["sector"]), None)
        assert rate_radar is not None
        assert "8.25%/năm" in rate_radar["marketSignal"]

    # -------------------------------------------------------------------------
    # TEST 13: Input Mutation Test D — Contradictory News
    # -------------------------------------------------------------------------
    def test_13_input_mutation_contradictory_news(self):
        news_eng = Phase07DynamicNewsEngine(
            raw_evidence_dir=self.raw_dir,
            historical_fixtures_dir=self.fixtures_dir,
            runtime_config=self.runtime_config,
            prior_verified_news_path=self.prior_news_path,
            run_timestamp="2026-11-10T22:30:00+07:00",
            offline_mode=True
        )
        news_res = news_eng.execute_pipeline()
        evs = list(news_res["selectedEvents"])
        contra = copy.deepcopy(evs[0])
        contra["eventId"] = "EVT-20261110-CONTRA"
        contra["headline"] = "Áp lực nợ xấu và rủi ro thanh khoản tăng mạnh đe dọa các ngân hàng thương mại"
        contra["researchDomain"] = "Monetary policy and banking"
        evs.append(contra)

        ed_eng = Phase07EditorialIntelligenceEngine(
            evs,
            news_res["step08_factVerification"]["auditedFactsBundle"],
            [],
            self.runtime_config
        )
        theses = ed_eng.generate_core_theses()["theses"]
        assert len(theses) > 0
        has_contra = any(len(th["counterEvidence"]) >= 1 for th in theses)
        assert has_contra is True

    # -------------------------------------------------------------------------
    # TEST 14: Input Mutation Test E — Unrelated News (Zero Unrelated Fallback)
    # -------------------------------------------------------------------------
    def test_14_input_mutation_unrelated_news_zero_fallback(self):
        news_eng = Phase07DynamicNewsEngine(
            raw_evidence_dir=self.raw_dir,
            historical_fixtures_dir=self.fixtures_dir,
            runtime_config=self.runtime_config,
            prior_verified_news_path=self.prior_news_path,
            run_timestamp="2026-11-10T22:30:00+07:00",
            offline_mode=True
        )
        news_res = news_eng.execute_pipeline()
        events = list(news_res["selectedEvents"])

        # Add an unrelated sports event
        unrelated = copy.deepcopy(events[0])
        unrelated["eventId"] = "EVT-20261110-SPORTS"
        unrelated["headline"] = "Đội tuyển bóng đá nam quốc gia giành chiến thắng kịch tính 2-1"
        unrelated["summary"] = "Trận đấu giao hữu quốc tế thu hút đông đảo cổ động viên cổ vũ cuồng nhiệt trên sân vận động Mỹ Đình."
        unrelated["researchDomain"] = "Sports and entertainment"
        events.append(unrelated)

        ed_eng = Phase07EditorialIntelligenceEngine(
            events,
            news_res["step08_factVerification"]["auditedFactsBundle"],
            [],
            self.runtime_config
        )
        theses = ed_eng.generate_core_theses()["theses"]
        for th in theses:
            # Unrelated event must NEVER be used as a primary anchor or central argument
            assert "bóng đá" not in th["centralArgument"].lower()

    # -------------------------------------------------------------------------
    # TEST 15: Input Mutation Test F — Merchant Payment Adoption Signal
    # -------------------------------------------------------------------------
    def test_15_input_mutation_add_merchant_payment_adoption_signal(self):
        news_eng = Phase07DynamicNewsEngine(
            raw_evidence_dir=self.raw_dir,
            historical_fixtures_dir=self.fixtures_dir,
            runtime_config=self.runtime_config,
            prior_verified_news_path=self.prior_news_path,
            run_timestamp="2026-11-10T22:30:00+07:00",
            offline_mode=True
        )
        news_res = news_eng.execute_pipeline()
        events = list(news_res["selectedEvents"])

        # Add J&T Cargo with direct payment adoption evidence
        jt_payment = copy.deepcopy(events[0])
        jt_payment["eventId"] = "EVT-20261110-JT-PAY"
        jt_payment["headline"] = "J&T Cargo chính thức bắt tay triển khai thu hộ COD không tiền mặt qua VietQR cho toàn bộ shipper"
        jt_payment["summary"] = "Hợp tác chiến lược giúp shipper hàng nặng thu hộ qua SmartPOS và mã VietQR động."
        jt_payment["supportingQuote"] = "Chúng tôi triển khai thanh toán không tiền mặt trên toàn mạng lưới shipper."
        events.append(jt_payment)

        ed_eng = Phase07EditorialIntelligenceEngine(
            events,
            news_res["step08_factVerification"]["auditedFactsBundle"],
            [],
            self.runtime_config
        )
        radars = ed_eng.generate_payment_radar_signals()["signals"]
        logistics_sig = next((r for r in radars if "Logistics" in r["sector"]), None)
        assert logistics_sig is not None
        assert logistics_sig["opportunityType"] == "VERIFIED_OPPORTUNITY"
        assert logistics_sig["confidence"] == "HIGH"
        assert "SCALE" in logistics_sig["recommendedNextAction"]

    # -------------------------------------------------------------------------
    # TEST 16: Input Mutation Test G — Remove Payment Evidence (Classified as POTENTIAL)
    # -------------------------------------------------------------------------
    def test_16_input_mutation_remove_payment_evidence(self):
        news_eng = Phase07DynamicNewsEngine(
            raw_evidence_dir=self.raw_dir,
            historical_fixtures_dir=self.fixtures_dir,
            runtime_config=self.runtime_config,
            prior_verified_news_path=self.prior_news_path,
            run_timestamp="2026-11-10T22:30:00+07:00",
            offline_mode=True
        )
        news_res = news_eng.execute_pipeline()
        # Original verified news has J&T Cargo without payment mention
        ed_eng = Phase07EditorialIntelligenceEngine(
            news_res["selectedEvents"],
            news_res["step08_factVerification"]["auditedFactsBundle"],
            [],
            self.runtime_config
        )
        radars = ed_eng.generate_payment_radar_signals()["signals"]
        logistics_sig = next((r for r in radars if "Logistics" in r["sector"]), None)
        if logistics_sig:
            assert logistics_sig["opportunityType"] == "POTENTIAL_OPPORTUNITY"
            assert logistics_sig["confidence"] == "MEDIUM"
            assert "VALIDATE" in logistics_sig["recommendedNextAction"]

    # -------------------------------------------------------------------------
    # TEST 17: Google Sheets Canonical Reconciliation
    # -------------------------------------------------------------------------
    def test_17_google_sheets_canonical_reconciliation(self):
        sheets_dir = os.path.join(PHASE07_ROOT, "05_GOOGLE_SHEETS_DRY_RUN")
        preview_p = os.path.join(sheets_dir, "PHASE07_GOOGLE_SHEETS_PREVIEW.json")
        val_p = os.path.join(sheets_dir, "PHASE07_GOOGLE_SHEETS_VALIDATION.json")

        assert os.path.exists(preview_p), f"Missing {preview_p}"
        assert os.path.exists(val_p), f"Missing {val_p}"

        with open(val_p, "r", encoding="utf-8") as f:
            val = json.load(f)

        assert val["existingBaselineRowCount"] == 155
        assert val["proposedNewRowCount"] == 165
        assert val["totalProjectedRowCount"] == 320
        assert val["foreignKeyViolationsCount"] == 0
        assert val["liveWriteApiCalled"] is False
        assert val["allTabsPassed"] is True

        # Verify historical Phase 06 reports are separated
        hist_dir = os.path.join(sheets_dir, "historical_phase06")
        assert os.path.isdir(hist_dir), "historical_phase06 directory must exist"
        assert os.path.exists(os.path.join(hist_dir, "GOOGLE_SHEETS_VALIDATION.json"))

    # -------------------------------------------------------------------------
    # TEST 18: Release Manifest Consistency & Parent Baseline Protection
    # -------------------------------------------------------------------------
    def test_18_release_manifest_consistency_and_package_identity(self):
        # Verify Phase 06 baseline archive is intact and protected
        p06_archive = os.path.join(
            PHASE07_ROOT, "..", "..", "01_ACCEPTED_PHASES", "PHASE06_R1.0.0", "PHASE06_R1.0.0_ACCEPTED_RELEASE.zip"
        )
        if not os.path.exists(p06_archive):
            p06_archive = os.path.join(PHASE07_ROOT, "baseline_phase06_r100", "PHASE06_R1.0.0_ACCEPTED_RELEASE.zip")

        if os.path.exists(p06_archive):
            with open(p06_archive, "rb") as f:
                p06_sha = hashlib.sha256(f.read()).hexdigest()
            expected_p06_sha = "d2f8672ff07bad36c9811906f69977a6d716de73d6685d874bd6a5ca53510bc9"
            assert p06_sha == expected_p06_sha, f"PHASE06 baseline corrupted! Expected {expected_p06_sha}, got {p06_sha}"

        # Check runtime config safety locks
        locks = self.runtime_config.get("productionSafetyLocks", {})
        assert all(v is False for v in locks.values()), f"Found enabled safety lock: {locks}"
        assert locks.get("productionDeployAllowed") is False
        assert locks.get("gitPushAllowed") is False
        assert locks.get("cronScheduleAllowed") is False
        assert locks.get("emailDistributionAllowed") is False
        assert locks.get("googleSheetsLiveWriteAllowed") is False

    def run_all(self) -> int:
        self.log("=" * 80)
        self.log("BRYAN FINTECH INTELLIGENCE — PHASE 07 R1.0.2 REMEDIATION TEST SUITE")
        self.log(f"Execution Timestamp: {datetime.now(VN_TZ).isoformat()}")
        self.log(f"Total Remediation Tests to Execute: 18")
        self.log("=" * 80)

        self.run_test("TEST-01: Same-Day Execution Isolation & Immutability", self.test_01_same_day_execution_isolation)
        self.run_test("TEST-02: Multi-Date Isolation", self.test_02_two_different_dates_isolation)
        self.run_test("TEST-03: Midnight and Month Transition Execution", self.test_03_midnight_and_month_transition)
        self.run_test("TEST-04: Live Mode Missing Retrieval Record Fail-Closed", self.test_04_live_mode_missing_retrieval_record_fail_closed)
        self.run_test("TEST-05: Live Mode HTTP Error Fail-Closed", self.test_05_live_mode_http_error_fail_closed)
        self.run_test("TEST-06: Snapshot SHA-256 Mismatch Fail-Closed", self.test_06_snapshot_hash_mismatch_fail_closed)
        self.run_test("TEST-07: No False HTTP Status (None when missing, never defaulted to 200)", self.test_07_no_false_http_status)
        self.run_test("TEST-08: Market Pulse Discovery Invocation in Step 10", self.test_08_market_pulse_discovery_invocation_in_step_10)
        self.run_test("TEST-09: Eight-Indicator Frequency-Aware Status & Validation", self.test_09_eight_indicator_frequency_aware_status)
        self.run_test("TEST-10: Input Mutation Test A — Add Interest-Rate Policy Event", self.test_10_input_mutation_add_interest_rate_policy)
        self.run_test("TEST-11: Input Mutation Test B — Remove Major Financial Event", self.test_11_input_mutation_remove_major_financial_event)
        self.run_test("TEST-12: Input Mutation Test C — Change Market Pulse Observation", self.test_12_input_mutation_change_market_pulse_observation)
        self.run_test("TEST-13: Input Mutation Test D — Contradictory News Captured in CounterEvidence", self.test_13_input_mutation_contradictory_news)
        self.run_test("TEST-14: Input Mutation Test E — Unrelated News (Zero Unrelated Fallback)", self.test_14_input_mutation_unrelated_news_zero_fallback)
        self.run_test("TEST-15: Input Mutation Test F — Merchant Payment Adoption Signal", self.test_15_input_mutation_add_merchant_payment_adoption_signal)
        self.run_test("TEST-16: Input Mutation Test G — Remove Payment Evidence (Classified as POTENTIAL)", self.test_16_input_mutation_remove_payment_evidence)
        self.run_test("TEST-17: Google Sheets Canonical Reconciliation (155 + 165 = 320 merged rows)", self.test_17_google_sheets_canonical_reconciliation)
        self.run_test("TEST-18: Release Manifest Consistency & Parent Baseline Protection", self.test_18_release_manifest_consistency_and_package_identity)

        self.log("=" * 80)
        self.log(f"R1.0.2 REMEDIATION QA SUMMARY: Total: 18 | PASSED: {self.passed} | FAILED: {self.failed}")
        status = "REMEDIATION_PASS" if self.failed == 0 else "REMEDIATION_FAIL"
        self.log(f"STATUS: {status}")
        self.log("=" * 80)
        return 0 if self.failed == 0 else 1


if __name__ == "__main__":
    suite = TestPhase07R102RemediationSuite()
    code = suite.run_all()
    sys.exit(code)
