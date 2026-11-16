#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_phase07_r103_remediation.py
================================
Targeted Remediation & Dynamic Intelligence Test Suite for Phase 07 R1.0.3:
  Test 01: Collector-to-Ledger Normalization (dict mapping URL->rec, ID->rec, list of recs, empty structures)
  Test 02: Live Candidate Inclusion and Exclusion on Evidence Failure
  Test 03: Historical Snapshot Cannot Claim LIVE_SOURCE_VERIFIED
  Test 04: Missing Retrieval Ledger Fails Closed in LIVE Mode (RETRIEVAL_RECORD_MISSING / LIVE_RETRIEVAL_FAILED)
  Test 05: Offline Execution Mode Governance (publicationAllowed = false, liveRetrievalReadiness = NOT_APPLICABLE)
  Test 06: Entity Binding Preservation (verifiedEntity propagated, eliminating "None: 7%")
  Test 07: Input Mutation Test A — Sports-Only Input (Zero Theses, Zero Signals, Zero Cards)
  Test 08: Input Mutation Test B — Interest-Rate Policy Event (Evidence-grounded Thesis)
  Test 09: Input Mutation Test C — Contradictory Events Captured in CounterEvidence
  Test 10: Input Mutation Test D — Direct Payment Adoption Yields VERIFIED_OPPORTUNITY
  Test 11: Input Mutation Test E — Removing Payment Evidence Downgrades to POTENTIAL_OPPORTUNITY
  Test 12: Input Mutation Test F — Market Pulse Observation Mutation Propagates to Radar Signal
  Test 13: Input Mutation Test G — Unrelated Events Produce No Fabricated Relationships
  Test 14: Market Pulse Discovery — All 8 Indicators Execute Queries & Record Provenance
  Test 15: Market Pulse Retention — Missing Observations Retain Previous Values & Dates
  Test 16: Same-Day Execution Isolation & Immutability (executions subdirectories & edition-latest pointer)
  Test 17: Release Governance, Safety Locks & Parent Baseline Protection (Phase 06 & Phase 07 R1.0.2)
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

VN_TZ = timezone(timedelta(hours=7))


class TestPhase07R103RemediationSuite:
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
    # TEST 01: Collector-to-Ledger Normalization
    # -------------------------------------------------------------------------
    def test_01_collector_to_ledger_normalization(self):
        engine = Phase07DynamicNewsEngine(
            raw_evidence_dir=self.raw_dir,
            historical_fixtures_dir=self.fixtures_dir,
            runtime_config=self.runtime_config,
            prior_verified_news_path=self.prior_news_path,
            run_timestamp="2026-11-10T22:30:00+07:00",
            offline_mode=True,
            execution_id="EXEC-TEST-NORM-01"
        )

        # Case 1: Dict mapping canonical URLs to records
        url_dict = {
            "https://sbv.gov.vn/news1": {
                "url": "https://sbv.gov.vn/news1",
                "http_status": 200,
                "retrieved_at": "2026-11-10T10:00:00Z"
            }
        }
        res1 = engine._normalize_retrieval_ledger(url_dict, "EXEC-TEST-NORM-01")
        assert len(res1) == 1
        assert res1[0]["requestedUrl"] == "https://sbv.gov.vn/news1"
        assert res1[0]["actualHttpStatusCode"] == 200
        assert res1[0]["executionId"] == "EXEC-TEST-NORM-01"

        # Case 2: Dict mapping event IDs or hashes to records
        id_dict = {
            "EVT-001": {
                "source_url": "https://gso.gov.vn/data",
                "httpStatus": 200,
                "fetched_at": "2026-11-10T11:00:00Z"
            }
        }
        res2 = engine._normalize_retrieval_ledger(id_dict, "EXEC-TEST-NORM-01")
        assert len(res2) == 1
        assert res2[0]["requestedUrl"] == "https://gso.gov.vn/data"
        assert res2[0]["actualHttpStatusCode"] == 200

        # Case 3: List of records
        rec_list = [
            {"requestedUrl": "https://vietnamnet.vn/fintech", "actualHttpStatusCode": 200}
        ]
        res3 = engine._normalize_retrieval_ledger(rec_list, "EXEC-TEST-NORM-01")
        assert len(res3) == 1
        assert res3[0]["requestedUrl"] == "https://vietnamnet.vn/fintech"

        # Case 4: Empty structures
        assert engine._normalize_retrieval_ledger({}, "EXEC-TEST-NORM-01") == []
        assert engine._normalize_retrieval_ledger([], "EXEC-TEST-NORM-01") == []
        assert engine._normalize_retrieval_ledger(None, "EXEC-TEST-NORM-01") == []

    # -------------------------------------------------------------------------
    # TEST 02: Live Candidate Inclusion and Exclusion on Evidence Failure
    # -------------------------------------------------------------------------
    def test_02_live_candidate_inclusion_and_exclusion(self):
        engine = Phase07DynamicNewsEngine(
            raw_evidence_dir=self.raw_dir,
            historical_fixtures_dir=self.fixtures_dir,
            runtime_config=self.runtime_config,
            prior_verified_news_path=self.prior_news_path,
            run_timestamp="2026-11-10T22:30:00+07:00",
            offline_mode=True
        )
        res = engine.execute_pipeline()
        # All selected events must have passed source verification
        for evt in res["selectedEvents"]:
            assert evt.get("sourceVerificationStatus") in ("SOURCE_VERIFIED", "VERIFIED", "PASS")
            assert len(evt.get("primarySource") or evt.get("publisher", "")) > 0

    # -------------------------------------------------------------------------
    # TEST 03: Historical Snapshot Cannot Claim LIVE_SOURCE_VERIFIED
    # -------------------------------------------------------------------------
    def test_03_historical_snapshot_cannot_claim_live_verified(self):
        engine = Phase07DynamicNewsEngine(
            raw_evidence_dir=self.raw_dir,
            historical_fixtures_dir=self.fixtures_dir,
            runtime_config=self.runtime_config,
            prior_verified_news_path=self.prior_news_path,
            run_timestamp="2026-11-10T22:30:00+07:00",
            offline_mode=True
        )
        res = engine.execute_pipeline()
        ledger = res.get("executionSpecificLedger", [])
        assert len(ledger) > 0
        for rec in ledger:
            assert rec["sourceVerificationStatus"] != "LIVE_SOURCE_VERIFIED"
            assert rec["retrievalMethod"] in ("HISTORICAL_SNAPSHOT_LOADED", "OFFLINE_FIXTURE_INGESTION")

    # -------------------------------------------------------------------------
    # TEST 04: Missing Retrieval Ledger Fails Closed in LIVE Mode
    # -------------------------------------------------------------------------
    def test_04_missing_retrieval_ledger_fails_live_mode(self):
        tmp_dir = tempfile.mkdtemp(prefix="p07_r103_t04_")
        try:
            orch = Phase07DailyRuntimeOrchestrator(
                edition_date="2026-11-10",
                edition_id="ED-20261110-D01",
                run_timestamp="2026-11-10T22:30:00+07:00",
                execution_mode="LIVE"
            )
            # When live collector has no live network credentials / empty ledger, fail-closed
            res = orch.execute_daily_run(output_base_dir=tmp_dir)
            assert res["liveRetrievalReadiness"] in ("RETRIEVAL_RECORD_MISSING", "FAILED_CLOSED", "NOT_APPLICABLE", "LIVE_RETRIEVAL_FAILED")
            assert res["publicationAllowed"] is False
            assert res["productionStatus"] == "NOT_APPROVED"
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)

    # -------------------------------------------------------------------------
    # TEST 05: Offline Execution Mode Governance
    # -------------------------------------------------------------------------
    def test_05_offline_execution_mode_governance(self):
        tmp_dir = tempfile.mkdtemp(prefix="p07_r103_t05_")
        try:
            orch = Phase07DailyRuntimeOrchestrator(
                edition_date="2026-11-10",
                edition_id="ED-20261110-D01",
                run_timestamp="2026-11-10T22:30:00+07:00",
                execution_mode="OFFLINE"
            )
            res = orch.execute_daily_run(output_base_dir=tmp_dir)
            assert res["executionMode"] == "OFFLINE"
            assert res["liveRetrievalReadiness"] == "NOT_APPLICABLE"
            assert res["publicationAllowed"] is False
            assert res["productionStatus"] == "NOT_APPROVED"
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)

    # -------------------------------------------------------------------------
    # TEST 06: Entity Binding Preservation (verifiedEntity propagated)
    # -------------------------------------------------------------------------
    def test_06_entity_binding_preservation(self):
        news_eng = Phase07DynamicNewsEngine(
            raw_evidence_dir=self.raw_dir,
            historical_fixtures_dir=self.fixtures_dir,
            runtime_config=self.runtime_config,
            prior_verified_news_path=self.prior_news_path,
            run_timestamp="2026-11-10T22:30:00+07:00",
            offline_mode=True
        )
        news_res = news_eng.execute_pipeline()
        facts_bundle = news_res["step08_factVerification"]["auditedFactsBundle"]

        ed_eng = Phase07EditorialIntelligenceEngine(
            verified_news=news_res["selectedEvents"],
            audited_facts_bundle=facts_bundle,
            audited_market_pulse=[],
            runtime_config=self.runtime_config
        )
        theses = ed_eng.generate_core_theses()["theses"]
        cards = ed_eng.generate_decision_cards()["cards"]

        # Assert no "None:" or "None : " appears in thesis central arguments or cards
        for th in theses:
            assert "None:" not in th["centralArgument"]
            assert "None : " not in th["centralArgument"]
        for c in cards:
            assert "None:" not in c.get("decisionTitle", "")
            assert "None:" not in c.get("contextEvidence", "")

    # -------------------------------------------------------------------------
    # TEST 07: Input Mutation Test A — Sports-Only Input
    # -------------------------------------------------------------------------
    def test_07_input_mutation_sports_only_input(self):
        sports_events = [
            {
                "eventId": "EVT-SPORTS-01",
                "headline": "Đội tuyển bóng đá nam quốc gia thắng 3-0 vòng loại World Cup",
                "summary": "Trận đấu diễn ra sôi động trên sân vận động Mỹ Đình trước 40.000 khán giả.",
                "researchDomain": "Sports",
                "primarySource": "Báo Thể Thao",
                "url": "https://thethao.vn/bong-da-1",
                "publicationDate": "2026-11-10",
                "sourceVerificationStatus": "VERIFIED"
            },
            {
                "eventId": "EVT-SPORTS-02",
                "headline": "Giải quần vợt quốc tế khởi tranh tại Đà Nẵng",
                "summary": "Các vận động viên hàng đầu khu vực quy tụ tham gia tranh tài.",
                "researchDomain": "Sports",
                "primarySource": "Báo Thể Thao",
                "url": "https://thethao.vn/quan-vot-2",
                "publicationDate": "2026-11-10",
                "sourceVerificationStatus": "VERIFIED"
            }
        ]
        ed_eng = Phase07EditorialIntelligenceEngine(
            verified_news=sports_events,
            audited_facts_bundle={},
            audited_market_pulse=[],
            runtime_config=self.runtime_config
        )
        theses = ed_eng.generate_core_theses()["theses"]
        radar = ed_eng.generate_payment_radar_signals()["signals"]
        cards = ed_eng.generate_decision_cards()["cards"]

        # With sports-only input, system must generate ZERO financial theses, ZERO payment radar signals, ZERO cards
        assert len(theses) == 0, f"Expected 0 theses for sports-only input, got {len(theses)}"
        assert len(radar) == 0, f"Expected 0 radar signals for sports-only input, got {len(radar)}"
        assert len(cards) == 0, f"Expected 0 decision cards for sports-only input, got {len(cards)}"

    # -------------------------------------------------------------------------
    # TEST 08: Input Mutation Test B — Interest-Rate Policy Event
    # -------------------------------------------------------------------------
    def test_08_input_mutation_interest_rate_policy(self):
        rate_events = [
            {
                "eventId": "EVT-RATE-01",
                "headline": "Ngân hàng Nhà nước hạ 0.5% trần lãi suất huy động và bơm thanh khoản",
                "summary": "Quyết định hạ trần lãi suất có hiệu lực từ ngày mai nhằm hỗ trợ tín dụng tăng trưởng.",
                "researchDomain": "State Bank of Vietnam policy",
                "primarySource": "Cổng TTĐT Ngân hàng Nhà nước",
                "url": "https://sbv.gov.vn/chinh-sach-lai-suat",
                "publicationDate": "2026-11-10",
                "sourceVerificationStatus": "VERIFIED"
            }
        ]
        ed_eng = Phase07EditorialIntelligenceEngine(
            verified_news=rate_events,
            audited_facts_bundle={},
            audited_market_pulse=[],
            runtime_config=self.runtime_config
        )
        theses = ed_eng.generate_core_theses()["theses"]
        assert len(theses) >= 1
        policy_th = theses[0]
        assert "hạ 0.5% trần lãi suất" in policy_th["centralArgument"] or "lãi suất" in policy_th["centralArgument"]

    # -------------------------------------------------------------------------
    # TEST 09: Input Mutation Test C — Contradictory Events CounterEvidence
    # -------------------------------------------------------------------------
    def test_09_input_mutation_contradictory_events_counterevidence(self):
        conflicting_events = [
            {
                "eventId": "EVT-GROWTH-01",
                "headline": "Tăng trưởng tín dụng toàn hệ thống đạt 15% vượt mục tiêu",
                "summary": "Dư nợ tín dụng tăng trưởng bứt phá nhờ động lực tiêu dùng cuối năm.",
                "researchDomain": "Monetary policy and banking",
                "primarySource": "SBV",
                "url": "https://sbv.gov.vn/tin-dung",
                "publicationDate": "2026-11-10",
                "sourceVerificationStatus": "VERIFIED"
            },
            {
                "eventId": "EVT-RISK-02",
                "headline": "Nợ xấu và áp lực thanh khoản gia tăng tại các ngân hàng thương mại nhỏ",
                "summary": "Tỷ lệ nợ xấu nội bảng có xu hướng tăng nhẹ gây áp lực trích lập dự phòng rủi ro.",
                "researchDomain": "Monetary policy and banking",
                "primarySource": "VnEconomy",
                "url": "https://vneconomy.vn/no-xau",
                "publicationDate": "2026-11-10",
                "sourceVerificationStatus": "VERIFIED"
            }
        ]
        ed_eng = Phase07EditorialIntelligenceEngine(
            verified_news=conflicting_events,
            audited_facts_bundle={},
            audited_market_pulse=[],
            runtime_config=self.runtime_config
        )
        theses = ed_eng.generate_core_theses()["theses"]
        assert len(theses) >= 1
        for th in theses:
            assert isinstance(th.get("counterEvidence"), list)
            assert len(th["counterEvidence"]) >= 1

    # -------------------------------------------------------------------------
    # TEST 10: Input Mutation Test D — Direct Payment Adoption Yields VERIFIED_OPPORTUNITY
    # -------------------------------------------------------------------------
    def test_10_input_mutation_direct_payment_adoption(self):
        pay_event = [
            {
                "eventId": "EVT-PAY-01",
                "headline": "J&T Cargo hợp tác triển khai thanh toán số và thu hộ COD qua VietQR",
                "summary": "100% shipper được trang bị mã QR động và ví điện tử để loại bỏ tiền mặt khi giao hàng.",
                "researchDomain": "Payment technology",
                "primarySource": "J&T Cargo Press",
                "url": "https://jtcargo.vn/news/qr",
                "publicationDate": "2026-11-10",
                "sourceVerificationStatus": "VERIFIED"
            }
        ]
        ed_eng = Phase07EditorialIntelligenceEngine(
            verified_news=pay_event,
            audited_facts_bundle={},
            audited_market_pulse=[],
            runtime_config=self.runtime_config
        )
        radars = ed_eng.generate_payment_radar_signals()["signals"]
        logistics_sig = next((r for r in radars if "Logistics" in r["sector"]), None)
        assert logistics_sig is not None
        assert logistics_sig["opportunityType"] == "VERIFIED_OPPORTUNITY"
        assert logistics_sig["confidence"] == "HIGH"
        assert "SCALE" in logistics_sig["recommendedNextAction"]

    # -------------------------------------------------------------------------
    # TEST 11: Input Mutation Test E — Removing Payment Evidence Downgrades
    # -------------------------------------------------------------------------
    def test_11_input_mutation_removing_payment_evidence(self):
        no_pay_event = [
            {
                "eventId": "EVT-LOG-01",
                "headline": "J&T Cargo mở rộng 50 trung tâm phân phối mới tại miền Trung",
                "summary": "Doanh nghiệp đẩy mạnh hạ tầng kho bãi logistics hàng nặng.",
                "researchDomain": "Logistics and infrastructure",
                "primarySource": "Doanh Nhân Sài Gòn",
                "url": "https://doanhnhansaigon.vn/jt-cargo-kho",
                "publicationDate": "2026-11-10",
                "sourceVerificationStatus": "VERIFIED"
            }
        ]
        ed_eng = Phase07EditorialIntelligenceEngine(
            verified_news=no_pay_event,
            audited_facts_bundle={},
            audited_market_pulse=[],
            runtime_config=self.runtime_config
        )
        radars = ed_eng.generate_payment_radar_signals()["signals"]
        logistics_sig = next((r for r in radars if "Logistics" in r["sector"]), None)
        if logistics_sig:
            assert logistics_sig["opportunityType"] == "POTENTIAL_OPPORTUNITY"
            assert logistics_sig["confidence"] == "MEDIUM"
            assert "VALIDATE" in logistics_sig["recommendedNextAction"]

    # -------------------------------------------------------------------------
    # TEST 12: Input Mutation Test F — Market Pulse Observation Mutation
    # -------------------------------------------------------------------------
    def test_12_input_mutation_market_pulse_mutation(self):
        news_eng = Phase07DynamicNewsEngine(
            raw_evidence_dir=self.raw_dir,
            historical_fixtures_dir=self.fixtures_dir,
            runtime_config=self.runtime_config,
            prior_verified_news_path=self.prior_news_path,
            run_timestamp="2026-11-10T22:30:00+07:00",
            offline_mode=True
        )
        news_res = news_eng.execute_pipeline()

        custom_mp = [
            {
                "indicatorId": "MP-03",
                "indicatorName": "Lãi suất huy động 12 tháng cao nhất",
                "currentValue": 9.15,
                "unit": "%/năm",
                "observationDate": "2026-11-10",
                "verificationStatus": "VERIFIED"
            }
        ]
        ed_eng = Phase07EditorialIntelligenceEngine(
            verified_news=news_res["selectedEvents"],
            audited_facts_bundle=news_res["step08_factVerification"]["auditedFactsBundle"],
            audited_market_pulse=custom_mp,
            runtime_config=self.runtime_config
        )
        radars = ed_eng.generate_payment_radar_signals()["signals"]
        rate_radar = next((r for r in radars if "Bán lẻ Giá trị cao" in r["sector"]), None)
        assert rate_radar is not None
        assert "9.15%/năm" in rate_radar["marketSignal"]

    # -------------------------------------------------------------------------
    # TEST 13: Input Mutation Test G — Unrelated Events Produce No Fabrication
    # -------------------------------------------------------------------------
    def test_13_input_mutation_unrelated_events_no_fabrication(self):
        unrelated = [
            {
                "eventId": "EVT-LIFESTYLE-01",
                "headline": "Xu hướng trồng cây xanh trong văn phòng được giới trẻ yêu thích",
                "summary": "Không gian xanh giúp thanh lọc không khí và giảm stress cho nhân viên văn phòng.",
                "researchDomain": "Lifestyle",
                "primarySource": "Tạp chí Đời sống",
                "url": "https://doisong.vn/cay-xanh",
                "publicationDate": "2026-11-10",
                "sourceVerificationStatus": "VERIFIED"
            }
        ]
        ed_eng = Phase07EditorialIntelligenceEngine(
            verified_news=unrelated,
            audited_facts_bundle={},
            audited_market_pulse=[],
            runtime_config=self.runtime_config
        )
        theses = ed_eng.generate_core_theses()["theses"]
        radars = ed_eng.generate_payment_radar_signals()["signals"]
        cards = ed_eng.generate_decision_cards()["cards"]

        assert len(theses) == 0
        assert len(radars) == 0
        assert len(cards) == 0

    # -------------------------------------------------------------------------
    # TEST 14: Market Pulse Discovery — All 8 Indicators Execute Queries & Record Provenance
    # -------------------------------------------------------------------------
    def test_14_market_pulse_all_8_indicators_discovery_queries(self):
        disc_engine = MarketPulseDiscoveryEngine(
            raw_evidence_dir=self.raw_dir,
            run_timestamp="2026-11-10T22:30:00+07:00",
            test_mode=True
        )
        for iid in ["MP-01", "MP-02", "MP-03", "MP-04", "MP-05", "MP-06", "MP-07", "MP-08"]:
            res = disc_engine.discover_and_evaluate(iid, [])
            assert res is not None
            assert res["indicatorId"] == iid

        inds_log = disc_engine.discovery_log.get("indicators", {})
        assert len(inds_log) == 8, f"Expected 8 indicators in discovery log, got {len(inds_log)}"
        for iid, ilog in inds_log.items():
            assert "actualExecutedQuery" in ilog
            assert len(ilog["actualExecutedQuery"]) > 0
            assert "searchProvider" in ilog
            assert "searchTimestamp" in ilog
            assert "searchQueries" in ilog

    # -------------------------------------------------------------------------
    # TEST 15: Market Pulse Retention — Missing Observations Retain Previous Values & Dates
    # -------------------------------------------------------------------------
    def test_15_market_pulse_retention_missing_observations(self):
        mp_rt = Phase07MarketPulseRuntime(
            raw_evidence_dir=self.raw_dir,
            baseline_mp8_path=self.mp8_path,
            canonical_specs_path=self.specs_path,
            runtime_config=self.runtime_config,
            run_timestamp="2026-11-10T22:30:00+07:00",
            offline_mode=True
        )
        res = mp_rt.execute_market_pulse(custom_observations={})
        inds = {i["indicatorId"]: i for i in res["indicators"]}
        with open(self.mp8_path, "r", encoding="utf-8") as f:
            prior_mp = {i["indicatorId"]: i for i in json.load(f)}

        for iid, ind in inds.items():
            prior = prior_mp[iid]
            if ind.get("updateStatus") in ("STALE_OBSERVATION", "QUALITATIVE_UPDATE_ONLY", "NUMERIC_VALUE_VERIFIED"):
                ind_val = ind.get("actualValue") if ind.get("actualValue") is not None else ind.get("currentValue")
                prior_val = prior.get("actualValue") if prior.get("actualValue") is not None else prior.get("currentValue")
                assert ind_val == prior_val
                assert ind["observationDate"] == prior["observationDate"]

    # -------------------------------------------------------------------------
    # TEST 16: Same-Day Execution Isolation & Immutability
    # -------------------------------------------------------------------------
    def test_16_same_day_execution_isolation(self):
        tmp_dir = tempfile.mkdtemp(prefix="p07_r103_t16_")
        try:
            date_str = "2026-11-10"
            t0_str = "2026-11-10T22:30:00+07:00"
            exec_id_1 = "EXEC-20261110-223000-C101"
            exec_id_2 = "EXEC-20261110-224500-C102"

            orch1 = Phase07DailyRuntimeOrchestrator(
                edition_date=date_str,
                edition_id="ED-20261110-D01",
                run_timestamp=t0_str,
                execution_id=exec_id_1,
                execution_mode="OFFLINE"
            )
            res1 = orch1.execute_daily_run(output_base_dir=tmp_dir)
            assert res1["overallRuntimeStatus"] == "PASS"

            exec_dir_1 = os.path.join(tmp_dir, "06_DAILY_EDITIONS", "daily-editions", date_str, "executions", exec_id_1)
            assert os.path.isdir(exec_dir_1)
            manifest_1 = os.path.join(exec_dir_1, "edition-manifest.json")
            with open(manifest_1, "rb") as f:
                h1_before = hashlib.sha256(f.read()).hexdigest()

            orch2 = Phase07DailyRuntimeOrchestrator(
                edition_date=date_str,
                edition_id="ED-20261110-D01",
                run_timestamp=t0_str,
                execution_id=exec_id_2,
                execution_mode="OFFLINE"
            )
            res2 = orch2.execute_daily_run(output_base_dir=tmp_dir)
            assert res2["overallRuntimeStatus"] == "PASS"

            exec_dir_2 = os.path.join(tmp_dir, "06_DAILY_EDITIONS", "daily-editions", date_str, "executions", exec_id_2)
            assert os.path.isdir(exec_dir_2)

            with open(manifest_1, "rb") as f:
                h1_after = hashlib.sha256(f.read()).hexdigest()
            assert h1_before == h1_after, "Run 1 directory was modified by Run 2!"

            pointer_path = os.path.join(tmp_dir, "06_DAILY_EDITIONS", "daily-editions", date_str, "edition-latest.json")
            assert os.path.exists(pointer_path)
            with open(pointer_path, "r", encoding="utf-8") as f:
                ptr = json.load(f)
            assert ptr["latestExecutionId"] == exec_id_2
            assert ptr["status"] == "VALIDATED"
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)

    # -------------------------------------------------------------------------
    # TEST 17: Release Governance, Safety Locks & Parent Baseline Protection
    # -------------------------------------------------------------------------
    def test_17_release_governance_and_parent_baseline(self):
        # 1. Verify Phase 06 baseline archive SHA-256
        p06_archive = os.path.join(
            PHASE07_ROOT, "..", "..", "01_ACCEPTED_PHASES", "PHASE06_R1.0.0", "PHASE06_R1.0.0_ACCEPTED_RELEASE.zip"
        )
        if os.path.exists(p06_archive):
            with open(p06_archive, "rb") as f:
                p06_sha = hashlib.sha256(f.read()).hexdigest()
            expected_p06_sha = "d2f8672ff07bad36c9811906f69977a6d716de73d6685d874bd6a5ca53510bc9"
            assert p06_sha == expected_p06_sha, f"PHASE06 baseline corrupted! Got {p06_sha}"

        # 2. Verify Phase 07 R1.0.2 remediation baseline backup SHA-256
        p07_r102_backup = os.path.join(
            PHASE07_ROOT, "..", "..", "02_PHASE_BACKUPS", "PHASE07_R1.0.2_REMEDIATION_BASELINE", "PHASE07_R1.0.2_BACKUP.zip"
        )
        if os.path.exists(p07_r102_backup):
            with open(p07_r102_backup, "rb") as f:
                p07_r102_sha = hashlib.sha256(f.read()).hexdigest()
            expected_r102_sha = "b08214c8badf28e639e460f933db4a48ae22ab964508ccac4b62adea06f5b6aa"
            assert p07_r102_sha == expected_r102_sha, f"PHASE07 R1.0.2 baseline backup corrupted! Got {p07_r102_sha}"

        # 3. Verify all production safety locks are strictly False
        locks = self.runtime_config.get("productionSafetyLocks", {})
        assert all(v is False for v in locks.values()), f"Found enabled safety lock: {locks}"
        assert locks.get("productionDeployAllowed") is False
        assert locks.get("gitPushAllowed") is False
        assert locks.get("cronScheduleAllowed") is False
        assert locks.get("emailDistributionAllowed") is False
        assert locks.get("googleSheetsLiveWriteAllowed") is False

    def run_all(self) -> int:
        self.log("=" * 80)
        self.log("BRYAN FINTECH INTELLIGENCE — PHASE 07 R1.0.3 REMEDIATION TEST SUITE")
        self.log(f"Execution Timestamp: {datetime.now(VN_TZ).isoformat()}")
        self.log(f"Total Remediation Tests to Execute: 17")
        self.log("=" * 80)

        self.run_test("TEST-01: Collector-to-Ledger Normalization", self.test_01_collector_to_ledger_normalization)
        self.run_test("TEST-02: Live Candidate Inclusion and Exclusion on Evidence Failure", self.test_02_live_candidate_inclusion_and_exclusion)
        self.run_test("TEST-03: Historical Snapshot Cannot Claim LIVE_SOURCE_VERIFIED", self.test_03_historical_snapshot_cannot_claim_live_verified)
        self.run_test("TEST-04: Missing Retrieval Ledger Fails Closed in LIVE Mode", self.test_04_missing_retrieval_ledger_fails_live_mode)
        self.run_test("TEST-05: Offline Execution Mode Governance", self.test_05_offline_execution_mode_governance)
        self.run_test("TEST-06: Entity Binding Preservation", self.test_06_entity_binding_preservation)
        self.run_test("TEST-07: Input Mutation Test A — Sports-Only Input", self.test_07_input_mutation_sports_only_input)
        self.run_test("TEST-08: Input Mutation Test B — Interest-Rate Policy Event", self.test_08_input_mutation_interest_rate_policy)
        self.run_test("TEST-09: Input Mutation Test C — Contradictory Events CounterEvidence", self.test_09_input_mutation_contradictory_events_counterevidence)
        self.run_test("TEST-10: Input Mutation Test D — Direct Payment Adoption Yields VERIFIED_OPPORTUNITY", self.test_10_input_mutation_direct_payment_adoption)
        self.run_test("TEST-11: Input Mutation Test E — Removing Payment Evidence Downgrades", self.test_11_input_mutation_removing_payment_evidence)
        self.run_test("TEST-12: Input Mutation Test F — Market Pulse Observation Mutation", self.test_12_input_mutation_market_pulse_mutation)
        self.run_test("TEST-13: Input Mutation Test G — Unrelated Events Produce No Fabrication", self.test_13_input_mutation_unrelated_events_no_fabrication)
        self.run_test("TEST-14: Market Pulse Discovery — All 8 Indicators Execute Queries & Record Provenance", self.test_14_market_pulse_all_8_indicators_discovery_queries)
        self.run_test("TEST-15: Market Pulse Retention — Missing Observations Retain Previous Values & Dates", self.test_15_market_pulse_retention_missing_observations)
        self.run_test("TEST-16: Same-Day Execution Isolation & Immutability", self.test_16_same_day_execution_isolation)
        self.run_test("TEST-17: Release Governance, Safety Locks & Parent Baseline Protection", self.test_17_release_governance_and_parent_baseline)

        self.log("=" * 80)
        self.log(f"R1.0.3 REMEDIATION QA SUMMARY: Total: 17 | PASSED: {self.passed} | FAILED: {self.failed}")
        status = "REMEDIATION_PASS" if self.failed == 0 else "REMEDIATION_FAIL"
        self.log(f"STATUS: {status}")
        self.log("=" * 80)
        return 0 if self.failed == 0 else 1


if __name__ == "__main__":
    suite = TestPhase07R103RemediationSuite()
    code = suite.run_all()
    sys.exit(code)
