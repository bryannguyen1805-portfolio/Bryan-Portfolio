#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_phase07_r104_remediation.py
================================
Targeted Remediation & Evidence-Driven Intelligence Test Suite for Phase 07 R1.0.4.
Implements the 15 specialized acceptance tests required by PART 9 of the Master Execution Prompt:
  TEST 01: Collector Ledger Normalization (statusCode -> actualHttpStatusCode, rawRecord preservation)
  TEST 02: Live Candidate Propagation (unbroken chain from live discovery to verification)
  TEST 03: Current Execution Provenance (historical retrieval cannot satisfy current Live gate)
  TEST 04: False Retrieval Success Prevention (fail-closed on missing status/ledger/failed HTTP)
  TEST 05: Snapshot Hash Reconciliation (hash mismatch prevents LIVE_SOURCE_VERIFIED)
  TEST 06: Sports-Only Intelligence (zero financial theses, zero payment radar, zero decision cards)
  TEST 07: Interest Rate Policy Analysis (evidence-grounded causal explanation & explicit uncertainty)
  TEST 08: Contradictory Financial Evidence (opposing facts detected, confidence reflects contradiction)
  TEST 09: Evidence Removal Test (removing payment evidence downgrades/removes opportunity)
  TEST 10: Semantic Relevance Test (semiconductor partnership yields NO tourism claims)
  TEST 11: Direct Payment Adoption Test (merchant payment deployment yields VERIFIED_OPPORTUNITY)
  TEST 12: Verified Entity Propagation (verifiedEntity cleanly propagated, zero None/null entities)
  TEST 13: Eight Actual Market Pulse Searches (real Search Adapter executed across MP-01..MP-08)
  TEST 14: No New Market Observation (frequency-aware retention with LATEST_OBSERVATION_RETAINED)
  TEST 15: Offline, Replay and Publication Integrity (mode isolation, post-T0 cutoff, provenance)
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


class TestPhase07R104RemediationSuite:
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
    # TEST 01: COLLECTOR LEDGER NORMALIZATION
    # -------------------------------------------------------------------------
    def test_01_collector_ledger_normalization(self):
        engine = Phase07DynamicNewsEngine(
            raw_evidence_dir=self.raw_dir,
            historical_fixtures_dir=self.fixtures_dir,
            runtime_config=self.runtime_config,
            prior_verified_news_path=self.prior_news_path,
            offline_mode=True
        )
        collector_fixture = [
            {
                "originalUrl": "https://vneconomy.vn/thi-truong-tai-chinh.htm",
                "canonicalUrl": "https://vneconomy.vn/thi-truong-tai-chinh.htm",
                "statusCode": 200,
                "responseSha256": "a" * 64,
                "retrievedAt": "2026-11-11T10:00:00+07:00",
                "publisher": "VnEconomy",
                "customHeader": "x-collector-v3"
            },
            {
                "originalUrl": "https://cafef.vn/ty-gia-usd.chn",
                "canonicalUrl": "https://cafef.vn/ty-gia-usd.chn",
                "statusCode": 404,
                "responseSha256": "b" * 64,
                "retrievedAt": "2026-11-11T10:05:00+07:00"
            }
        ]

        normalized = engine._normalize_retrieval_ledger(collector_fixture)
        assert len(normalized) == 2

        rec1 = normalized.get("https://vneconomy.vn/thi-truong-tai-chinh.htm")
        assert rec1 is not None
        assert rec1["actualHttpStatusCode"] == 200
        assert rec1["contentSha256"] == "a" * 64
        assert rec1["requestedUrl"] == "https://vneconomy.vn/thi-truong-tai-chinh.htm"
        assert rec1["canonicalUrl"] == "https://vneconomy.vn/thi-truong-tai-chinh.htm"
        assert rec1["retrievedAt"] == "2026-11-11T10:00:00+07:00"
        assert rec1["rawRecord"]["customHeader"] == "x-collector-v3"
        assert rec1["rawRecord"]["statusCode"] == 200

        rec2 = normalized.get("https://cafef.vn/ty-gia-usd.chn")
        assert rec2 is not None
        assert rec2["actualHttpStatusCode"] == 404
        assert rec2["contentSha256"] == "b" * 64

        # Verify missing status is not fabricated as 200
        missing_fixture = [{"canonicalUrl": "https://example.com/no-status", "responseSha256": "c" * 64}]
        norm_missing = engine._normalize_retrieval_ledger(missing_fixture)
        assert norm_missing["https://example.com/no-status"]["actualHttpStatusCode"] is None

        # Verify unsupported structure raises error
        try:
            engine._normalize_retrieval_ledger("INVALID_STRING_LEDGER")
            assert False, "Should have rejected invalid ledger structure"
        except ValueError as err:
            assert "UNSUPPORTED_LEDGER_STRUCTURE" in str(err)

    # -------------------------------------------------------------------------
    # TEST 02: LIVE CANDIDATE PROPAGATION
    # -------------------------------------------------------------------------
    def test_02_live_candidate_propagation(self):
        engine = Phase07DynamicNewsEngine(
            raw_evidence_dir=self.raw_dir,
            historical_fixtures_dir=self.fixtures_dir,
            runtime_config=self.runtime_config,
            prior_verified_news_path=self.prior_news_path,
            offline_mode=False,
            execution_id="EXEC-TEST-02-LIVE"
        )
        live_cands = [
            {
                "canonicalUrl": "https://vneconomy.vn/ngan-hang-nha-nuoc-on-dinh-ty-gia.htm",
                "requestedUrl": "https://vneconomy.vn/ngan-hang-nha-nuoc-on-dinh-ty-gia.htm",
                "title": "Ngân hàng Nhà nước duy trì ổn định tỷ giá tiền đồng",
                "publishedAt": "2026-11-11T09:00:00+07:00",
                "publisher": "VnEconomy",
                "evidenceSha256": "d" * 64
            }
        ]
        retrieval_ledger = [
            {
                "canonicalUrl": "https://vneconomy.vn/ngan-hang-nha-nuoc-on-dinh-ty-gia.htm",
                "requestedUrl": "https://vneconomy.vn/ngan-hang-nha-nuoc-on-dinh-ty-gia.htm",
                "statusCode": 200,
                "responseSha256": "d" * 64,
                "retrievedAt": "2026-11-11T09:15:00+07:00",
                "executionId": "EXEC-TEST-02-LIVE"
            }
        ]

        discovered = engine.step04_discover_candidates(
            live_candidates=live_cands,
            retrieval_ledger=retrieval_ledger
        )
        assert len(discovered) == 1
        cand = discovered[0]
        assert cand["canonicalUrl"] == "https://vneconomy.vn/ngan-hang-nha-nuoc-on-dinh-ty-gia.htm"
        assert cand["retrievalRecordFound"] is True
        assert cand["contentHashMatched"] is True
        assert cand["httpStatusCode"] == 200
        assert cand["retrievalMode"] == "LIVE_SOURCE_VERIFIED"
        assert cand["executionId"] == "EXEC-TEST-02-LIVE"

    # -------------------------------------------------------------------------
    # TEST 03: CURRENT EXECUTION PROVENANCE
    # -------------------------------------------------------------------------
    def test_03_current_execution_provenance(self):
        current_exec_id = "EXEC-20261111-CURRENT"
        engine = Phase07DynamicNewsEngine(
            raw_evidence_dir=self.raw_dir,
            historical_fixtures_dir=self.fixtures_dir,
            runtime_config=self.runtime_config,
            prior_verified_news_path=self.prior_news_path,
            offline_mode=False,
            execution_id=current_exec_id
        )
        historical_cands = [
            {
                "eventId": "EVT-HIST-01",
                "canonicalUrl": "https://cafef.vn/tin-cu-hom-qua.chn",
                "sourceUrl": "https://cafef.vn/tin-cu-hom-qua.chn",
                "headline": "Diễn biến thị trường phiên giao dịch trước đó",
                "publishedAt": "2026-11-10T15:00:00+07:00",
                "publisher": "CafeF",
                "evidenceSha256": "e" * 64,
                "retrievalRecordFound": True,
                "contentHashMatched": True,
                "httpStatusCode": 200,
                "retrievalMode": "LIVE_SOURCE_VERIFIED",
                "executionId": "EXEC-20261110-HISTORICAL-PREV",
                "isHistoricalRecord": True
            }
        ]

        pipeline_res = engine.execute_pipeline(custom_candidates=historical_cands)
        rejected = pipeline_res["rejectedLedger"]
        assert len(rejected) >= 1
        mismatch_rej = next((r for r in rejected if "HISTORICAL_PROVENANCE_MISMATCH" in r.get("rejectionReason", "")), None)
        assert mismatch_rej is not None, "Historical retrieval record must be rejected for current LIVE execution"

    # -------------------------------------------------------------------------
    # TEST 04: FALSE RETRIEVAL SUCCESS PREVENTION
    # -------------------------------------------------------------------------
    def test_04_false_retrieval_success_prevention(self):
        engine = Phase07DynamicNewsEngine(
            raw_evidence_dir=self.raw_dir,
            historical_fixtures_dir=self.fixtures_dir,
            runtime_config=self.runtime_config,
            prior_verified_news_path=self.prior_news_path,
            offline_mode=False,
            execution_id="EXEC-TEST-04"
        )
        test_cands = [
            {
                "eventId": "EVT-MISS-HTTP",
                "canonicalUrl": "https://vneconomy.vn/missing-status.htm",
                "headline": "Sự kiện tài chính thiếu HTTP status",
                "evidenceSha256": "f" * 64,
                "retrievalRecordFound": True,
                "httpStatusCode": None
            },
            {
                "eventId": "EVT-MISS-LEDGER",
                "canonicalUrl": "https://vneconomy.vn/missing-ledger.htm",
                "headline": "Sự kiện tài chính thiếu bản ghi ledger",
                "evidenceSha256": "g" * 64,
                "retrievalRecordFound": False
            },
            {
                "eventId": "EVT-FAILED-RETRIEVAL",
                "canonicalUrl": "https://vneconomy.vn/failed-retrieval.htm",
                "headline": "Sự kiện tài chính kết nối lỗi 503",
                "evidenceSha256": "h" * 64,
                "retrievalRecordFound": True,
                "httpStatusCode": 503,
                "retrievalStatus": "HTTP_ERROR"
            }
        ]

        pipeline_res = engine.execute_pipeline(custom_candidates=test_cands)
        rejected = pipeline_res["rejectedLedger"]
        rej_ids = [r["eventId"] for r in rejected]
        assert "EVT-MISS-HTTP" in rej_ids
        assert "EVT-MISS-LEDGER" in rej_ids
        assert "EVT-FAILED-RETRIEVAL" in rej_ids

        # Ensure none were marked SOURCE_VERIFIED
        assert len(pipeline_res["selectedEvents"]) == 0

    # -------------------------------------------------------------------------
    # TEST 05: SNAPSHOT HASH RECONCILIATION
    # -------------------------------------------------------------------------
    def test_05_snapshot_hash_reconciliation(self):
        engine = Phase07DynamicNewsEngine(
            raw_evidence_dir=self.raw_dir,
            historical_fixtures_dir=self.fixtures_dir,
            runtime_config=self.runtime_config,
            prior_verified_news_path=self.prior_news_path,
            offline_mode=False,
            execution_id="EXEC-TEST-05"
        )
        tampered_cand = [
            {
                "eventId": "EVT-TAMPERED-01",
                "canonicalUrl": "https://cafef.vn/tin-tampered.chn",
                "headline": "Sự kiện tài chính bị can thiệp nội dung snapshot",
                "evidenceSha256": "1111" * 16,
                "retrievalRecordFound": True,
                "contentHashMatched": False,
                "httpStatusCode": 200,
                "retrievalMode": "LIVE_SOURCE_VERIFIED",
                "executionId": "EXEC-TEST-05"
            }
        ]

        pipeline_res = engine.execute_pipeline(custom_candidates=tampered_cand)
        rejected = pipeline_res["rejectedLedger"]
        rej = next((r for r in rejected if r["eventId"] == "EVT-TAMPERED-01"), None)
        assert rej is not None
        assert "CONTENT_HASH_MISMATCH" in rej.get("rejectionReason", "")
        assert len(pipeline_res["selectedEvents"]) == 0

    # -------------------------------------------------------------------------
    # TEST 06: SPORTS-ONLY INTELLIGENCE
    # -------------------------------------------------------------------------
    def test_06_sports_only_intelligence(self):
        sports_event = [
            {
                "eventId": "EVT-FOOTBALL-01",
                "headline": "Đội tuyển Việt Nam giành chiến thắng 2-0 trong trận giao hữu quốc tế",
                "summary": "Hai bàn thắng đẹp mắt trong hiệp hai giúp đội tuyển bóng đá nam có khởi đầu thuận lợi.",
                "researchDomain": "Sports",
                "primarySource": "Báo Thể thao & Văn hóa",
                "url": "https://thethaovanhoa.vn/viet-nam-thang-2-0.htm",
                "publicationDate": "2026-11-11",
                "sourceVerificationStatus": "VERIFIED"
            }
        ]

        ed_eng = Phase07EditorialIntelligenceEngine(
            verified_news=sports_event,
            audited_facts_bundle={},
            audited_market_pulse=[],
            runtime_config=self.runtime_config
        )

        theses = ed_eng.generate_core_theses()["theses"]
        radars = ed_eng.generate_payment_radar_signals()["signals"]
        cards = ed_eng.generate_financial_decision_intelligence()["decisionCards"]

        # Expected: Zero financial theses, zero tourism opportunity, zero payment radar, zero decision cards
        assert len(theses) == 0, f"Expected 0 theses for sports-only input, got {len(theses)}"
        assert len(radars) == 0, f"Expected 0 radar signals for sports-only input, got {len(radars)}"
        assert len(cards) == 0, f"Expected 0 decision cards for sports-only input, got {len(cards)}"

    # -------------------------------------------------------------------------
    # TEST 07: INTEREST RATE POLICY ANALYSIS
    # -------------------------------------------------------------------------
    def test_07_interest_rate_policy_analysis(self):
        policy_event = [
            {
                "eventId": "EVT-RATE-POLICY-01",
                "headline": "Ngân hàng Nhà nước ban hành thông tư quy định trần lãi suất tiền gửi 6 tháng ở mức 5,5%/năm",
                "summary": "Động thái chính sách nhằm kiềm chế đà tăng chi phí vốn và hạ lãi suất cho vay hỗ trợ sản xuất.",
                "researchDomain": "Deposit & lending interest rates",
                "primarySource": "SBV Portal",
                "url": "https://sbv.gov.vn/chinh-sach-lai-suat-2026.htm",
                "publicationDate": "2026-11-11",
                "sourceVerificationStatus": "VERIFIED"
            }
        ]
        facts_bundle = {
            "allAuditedFacts": [
                {
                    "factId": "FACT-RATE-01",
                    "originatingEventId": "EVT-RATE-POLICY-01",
                    "metricName": "Trần lãi suất tiền gửi kỳ hạn dưới 6 tháng",
                    "extractedExpression": "5,5%/năm",
                    "currentValue": 5.5,
                    "unit": "%/năm",
                    "verifiedEntity": "Ngân hàng Nhà nước Việt Nam",
                    "sourceVerificationStatus": "VERIFIED",
                    "isDuplicate": False
                }
            ]
        }

        ed_eng = Phase07EditorialIntelligenceEngine(
            verified_news=policy_event,
            audited_facts_bundle=facts_bundle,
            audited_market_pulse=[],
            runtime_config=self.runtime_config
        )
        theses = ed_eng.generate_core_theses()["theses"]
        assert len(theses) >= 1
        th = theses[0]
        assert "EVT-RATE-POLICY-01" in th["supportingEventIds"]
        assert any("5,5%/năm" in str(v) for v in th["affectedVariables"])
        assert th["confidenceLevel"] in ["HIGH", "MEDIUM", "LOW"]
        assert len(th["causalExplanation"]) > 20
        assert len(th["limitations"]) >= 1

    # -------------------------------------------------------------------------
    # TEST 08: CONTRADICTORY FINANCIAL EVIDENCE
    # -------------------------------------------------------------------------
    def test_08_contradictory_financial_evidence(self):
        contradictory_events = [
            {
                "eventId": "EVT-EXP-01",
                "headline": "Tăng trưởng tín dụng toàn hệ thống bứt phá mạnh mẽ đạt 15,5%",
                "summary": "Dòng vốn ngân hàng chảy mạnh vào các ngành sản xuất kinh doanh và thương mại dịch vụ.",
                "researchDomain": "Banking & credit growth",
                "primarySource": "Thời báo Ngân hàng",
                "url": "https://thoibaonganhang.vn/tin-dung-but-pha.htm",
                "publicationDate": "2026-11-11",
                "sourceVerificationStatus": "VERIFIED"
            },
            {
                "eventId": "EVT-RISK-02",
                "headline": "Áp lực nợ xấu và trích lập dự phòng gia tăng tại các ngân hàng thương mại",
                "summary": "Tỷ lệ nợ xấu tiềm ẩn có xu hướng nhích lên khiến biên lãi thuần NIM chịu áp lực thu hẹp.",
                "researchDomain": "Banking & credit growth",
                "primarySource": "VnEconomy",
                "url": "https://vneconomy.vn/no-xau-tang-nhe.htm",
                "publicationDate": "2026-11-11",
                "sourceVerificationStatus": "VERIFIED"
            }
        ]

        ed_eng = Phase07EditorialIntelligenceEngine(
            verified_news=contradictory_events,
            audited_facts_bundle={},
            audited_market_pulse=[],
            runtime_config=self.runtime_config
        )
        theses = ed_eng.generate_core_theses()["theses"]
        assert len(theses) >= 1
        th = theses[0]
        assert len(th["counterEvidence"]) >= 1
        assert "EVT-RISK-02" in str(th["counterEvidence"]) or "nợ xấu" in str(th["counterEvidence"]).lower()
        assert th["confidenceLevel"] == "MEDIUM"

    # -------------------------------------------------------------------------
    # TEST 09: EVIDENCE REMOVAL TEST
    # -------------------------------------------------------------------------
    def test_09_evidence_removal_test(self):
        payment_evidence_event = [
            {
                "eventId": "EVT-COOP-01",
                "headline": "Co.opmart triển khai thu hộ COD không tiền mặt và tích hợp VietQR trên toàn hệ thống",
                "summary": "100% quầy thu ngân được trang bị SmartPOS và mã QR động kết nối tức thì.",
                "researchDomain": "Cashless payments & VietQR",
                "primarySource": "Saigon Co.op News",
                "url": "https://saigonco-op.com.vn/vietqr.htm",
                "publicationDate": "2026-11-11",
                "sourceVerificationStatus": "VERIFIED"
            }
        ]

        # Case 1: With payment evidence -> VERIFIED_OPPORTUNITY
        ed1 = Phase07EditorialIntelligenceEngine(
            verified_news=payment_evidence_event,
            audited_facts_bundle={},
            audited_market_pulse=[],
            runtime_config=self.runtime_config
        )
        radars1 = ed1.generate_payment_radar_signals()["signals"]
        assert len(radars1) >= 1
        sig1 = radars1[0]
        assert sig1["opportunityType"] in ["VERIFIED_OPPORTUNITY", "EMERGING_OPPORTUNITY"]

        # Case 2: Evidence removed (empty verified_news) -> Signal disappears, no stale opportunity
        ed2 = Phase07EditorialIntelligenceEngine(
            verified_news=[],
            audited_facts_bundle={},
            audited_market_pulse=[],
            runtime_config=self.runtime_config
        )
        radars2 = ed2.generate_payment_radar_signals()["signals"]
        assert len(radars2) == 0

    # -------------------------------------------------------------------------
    # TEST 10: SEMANTIC RELEVANCE TEST
    # -------------------------------------------------------------------------
    def test_10_semantic_relevance_test(self):
        semiconductor_event = [
            {
                "eventId": "EVT-SEMI-JAPAN-01",
                "headline": "Doanh nghiệp công nghệ Việt Nam hợp tác tập đoàn Nhật Bản sản xuất vi mạch bán dẫn",
                "summary": "Hai bên ký kết thỏa thuận thành lập trung tâm thiết kế chip và phát triển công nghệ bán dẫn.",
                "researchDomain": "Corporate & Business Expansion",
                "primarySource": "VnExpress",
                "url": "https://vnexpress.net/ban-dan-viet-nhat.htm",
                "publicationDate": "2026-11-11",
                "sourceVerificationStatus": "VERIFIED"
            }
        ]

        ed_eng = Phase07EditorialIntelligenceEngine(
            verified_news=semiconductor_event,
            audited_facts_bundle={},
            audited_market_pulse=[],
            runtime_config=self.runtime_config
        )
        radars = ed_eng.generate_payment_radar_signals()["signals"]

        # Expected: No tourism opportunity, no VietQR tourism claim, no unrelated event association
        tourism_sig = next((r for r in radars if "du lịch" in r["sector"].lower() or "khách sạn" in r["sector"].lower()), None)
        assert tourism_sig is None, "Semiconductor partnership with Japan must not trigger a tourism opportunity"

    # -------------------------------------------------------------------------
    # TEST 11: DIRECT PAYMENT ADOPTION TEST
    # -------------------------------------------------------------------------
    def test_11_direct_payment_adoption_test(self):
        direct_adopt_event = [
            {
                "eventId": "EVT-LOG-PAY-01",
                "headline": "J&T Cargo hợp tác mở rộng dịch vụ thu hộ COD không tiền mặt và SmartPOS cho shipper",
                "summary": "Triển khai mã VietQR động gắn mã đơn hàng để đối soát doanh thu tự động.",
                "supportingQuote": "Dịch vụ COD không tiền mặt và SmartPOS giúp loại bỏ 100% rủi ro tiền mặt.",
                "researchDomain": "Cashless payments & VietQR",
                "primarySource": "Logistics News",
                "url": "https://logistics.vn/jt-cod.htm",
                "publicationDate": "2026-11-11",
                "sourceVerificationStatus": "VERIFIED"
            }
        ]

        ed_eng = Phase07EditorialIntelligenceEngine(
            verified_news=direct_adopt_event,
            audited_facts_bundle={},
            audited_market_pulse=[],
            runtime_config=self.runtime_config
        )
        radars = ed_eng.generate_payment_radar_signals()["signals"]
        assert len(radars) >= 1
        sig = radars[0]
        assert sig["opportunityType"] == "VERIFIED_OPPORTUNITY"
        assert sig["confidence"] == "HIGH"
        assert "SCALE" in sig["recommendedNextAction"]

    # -------------------------------------------------------------------------
    # TEST 12: VERIFIED ENTITY PROPAGATION
    # -------------------------------------------------------------------------
    def test_12_verified_entity_propagation(self):
        ev = [
            {
                "eventId": "EVT-EVN-01",
                "headline": "Tập đoàn Điện lực Việt Nam (EVN) cần huy động 830.000 tỷ đồng vốn đầu tư",
                "summary": "Khoản vốn phục vụ các dự án truyền tải và nguồn điện trong Quy hoạch điện VIII.",
                "researchDomain": "Corporate & Business Expansion",
                "primarySource": "Báo Đầu tư",
                "url": "https://baodautu.vn/evn-von-dau-tu.htm",
                "publicationDate": "2026-11-11",
                "sourceVerificationStatus": "VERIFIED"
            }
        ]
        facts_bundle = {
            "allAuditedFacts": [
                {
                    "factId": "FACT-EVN-01",
                    "originatingEventId": "EVT-EVN-01",
                    "metricName": "Nhu cầu vốn đầu tư trung dài hạn",
                    "extractedExpression": "830.000 tỷ đồng",
                    "currentValue": 830000,
                    "unit": "tỷ đồng",
                    "verifiedEntity": "Tập đoàn Điện lực Việt Nam (EVN)",
                    "sourceVerificationStatus": "VERIFIED",
                    "isDuplicate": False
                }
            ]
        }

        ed_eng = Phase07EditorialIntelligenceEngine(
            verified_news=ev,
            audited_facts_bundle=facts_bundle,
            audited_market_pulse=[],
            runtime_config=self.runtime_config
        )
        theses = ed_eng.generate_core_theses()["theses"]
        assert len(theses) >= 1
        th = theses[0]
        vars_str = " ".join(th["affectedVariables"])
        assert "Tập đoàn Điện lực Việt Nam (EVN)" in vars_str
        assert "830.000 tỷ đồng" in vars_str
        assert "None:" not in vars_str and "None (" not in vars_str

    # -------------------------------------------------------------------------
    # TEST 13: EIGHT ACTUAL MARKET PULSE SEARCHES
    # -------------------------------------------------------------------------
    def test_13_eight_actual_market_pulse_searches(self):
        disc_engine = MarketPulseDiscoveryEngine(
            raw_evidence_dir=self.raw_dir,
            run_timestamp="2026-11-11T10:00:00+07:00",
            test_mode=False
        )
        res = disc_engine.execute_all_eight_searches(execution_id="EXEC-TEST-13")
        report = res["executionReportTable"]
        assert len(report) == 8, f"Expected 8 canonical searches, got {len(report)}"

        for row in report:
            assert row["indicatorId"] in ["MP-01", "MP-02", "MP-03", "MP-04", "MP-05", "MP-06", "MP-07", "MP-08"]
            assert row["searchExecuted"] == "YES"
            assert row["executedQuery"] is not None and len(row["executedQuery"]) > 0
            assert row["searchProvider"] is not None
            # In sandbox without network, actualRequestStatus must be ACCESS_BLOCKED honestly
            assert row["actualRequestStatus"] in ["SUCCESS", "ACCESS_BLOCKED"]

    # -------------------------------------------------------------------------
    # TEST 14: NO NEW MARKET OBSERVATION
    # -------------------------------------------------------------------------
    def test_14_no_new_market_observation(self):
        disc_engine = MarketPulseDiscoveryEngine(
            raw_evidence_dir=self.raw_dir,
            run_timestamp="2026-11-11T10:00:00+07:00",
            test_mode=True
        )
        prior_obs = {
            "actualValue": 24260.0,
            "currentValue": 24260.0,
            "observationDate": "2026-11-10",
            "unit": "VND"
        }
        res = disc_engine.execute_indicator_search("MP-01", "EXEC-TEST-14", prior_observation=prior_obs)
        ind_res = res["indicatorResult"]
        assert ind_res["actualValue"] == 24260.0
        assert ind_res["observationDate"] == "2026-11-10"
        assert ind_res["updateStatus"] == "LATEST_OBSERVATION_RETAINED"

    # -------------------------------------------------------------------------
    # TEST 15: OFFLINE, REPLAY AND PUBLICATION INTEGRITY
    # -------------------------------------------------------------------------
    def test_15_offline_replay_and_publication_integrity(self):
        tmp_dir = tempfile.mkdtemp(prefix="phase07_r104_t15_")
        try:
            # 15.A: OFFLINE execution cannot obtain LIVE_RETRIEVAL_PASS
            orch_off = Phase07DailyRuntimeOrchestrator(
                edition_date="2026-11-10",
                edition_id="ED-20261110-D01",
                run_timestamp="2026-11-10T22:30:00+07:00",
                execution_mode="OFFLINE"
            )
            res_off = orch_off.execute_daily_run(output_base_dir=tmp_dir)
            assert res_off["executionMode"] == "OFFLINE"
            assert res_off["liveRetrievalReadiness"] == "NOT_APPLICABLE"
            assert res_off["productionStatus"] == "NOT_APPROVED"
            assert res_off["publicationAllowed"] is False

            # 15.B: Historical REPLAY with post-T0 evidence isolates post-cutoff
            engine_rep = Phase07DynamicNewsEngine(
                raw_evidence_dir=self.raw_dir,
                historical_fixtures_dir=self.fixtures_dir,
                runtime_config=self.runtime_config,
                prior_verified_news_path=self.prior_news_path,
                run_timestamp="2026-11-10T12:00:00+07:00",  # T0 = 12:00
                offline_mode=True,
                execution_mode="REPLAY"
            )
            cands_with_post_cutoff = [
                {
                    "eventId": "EVT-POST-T0",
                    "canonicalUrl": "https://vneconomy.vn/post-cutoff.htm",
                    "headline": "Sự kiện thu thập sau T0",
                    "publishedAt": "2026-11-10T10:00:00+07:00",
                    "retrievedAt": "2026-11-10T15:00:00+07:00",  # After T0
                    "evidenceSha256": "9" * 64,
                    "publisher": "VnEconomy"
                }
            ]
            rep_res = engine_rep.execute_pipeline(custom_candidates=cands_with_post_cutoff)
            post_cutoff = rep_res.get("postCutoffEvidence", [])
            assert len(post_cutoff) == 1
            assert post_cutoff[0]["disposition"] == "REJECTED_POST_CUTOFF"
            assert len(rep_res["selectedEvents"]) == 0

            # 15.C: LIVE execution with historical-only retrieval records cannot obtain LIVE_RETRIEVAL_PASS
            orch_live = Phase07DailyRuntimeOrchestrator(
                edition_date="2026-11-10",
                edition_id="ED-20261110-D01",
                run_timestamp="2026-11-10T22:30:00+07:00",
                execution_mode="LIVE"
            )
            # In live mode with offline raw_dir, live retrieval readiness must fail
            res_live = orch_live.execute_daily_run(output_base_dir=tmp_dir)
            assert res_live["liveRetrievalReadiness"] != "LIVE_RETRIEVAL_PASS"
            assert res_live["publicationAllowed"] is False

        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)

    def run_all(self) -> int:
        header = (
            "=" * 80 + "\n"
            "BRYAN FINTECH INTELLIGENCE — PHASE 07 R1.0.4 REMEDIATION TEST SUITE\n"
            f"Execution Timestamp: {datetime.now(VN_TZ).isoformat()}\n"
            "Total Remediation Tests to Execute: 15\n"
            + "=" * 80
        )
        self.log(header)

        tests = [
            ("TEST 01: Collector Ledger Normalization", self.test_01_collector_ledger_normalization),
            ("TEST 02: Live Candidate Propagation", self.test_02_live_candidate_propagation),
            ("TEST 03: Current Execution Provenance", self.test_03_current_execution_provenance),
            ("TEST 04: False Retrieval Success Prevention", self.test_04_false_retrieval_success_prevention),
            ("TEST 05: Snapshot Hash Reconciliation", self.test_05_snapshot_hash_reconciliation),
            ("TEST 06: Sports-Only Intelligence", self.test_06_sports_only_intelligence),
            ("TEST 07: Interest Rate Policy Analysis", self.test_07_interest_rate_policy_analysis),
            ("TEST 08: Contradictory Financial Evidence", self.test_08_contradictory_financial_evidence),
            ("TEST 09: Evidence Removal Test", self.test_09_evidence_removal_test),
            ("TEST 10: Semantic Relevance Test", self.test_10_semantic_relevance_test),
            ("TEST 11: Direct Payment Adoption Test", self.test_11_direct_payment_adoption_test),
            ("TEST 12: Verified Entity Propagation", self.test_12_verified_entity_propagation),
            ("TEST 13: Eight Actual Market Pulse Searches", self.test_13_eight_actual_market_pulse_searches),
            ("TEST 14: No New Market Observation", self.test_14_no_new_market_observation),
            ("TEST 15: Offline, Replay and Publication Integrity", self.test_15_offline_replay_and_publication_integrity),
        ]

        for name, fn in tests:
            self.run_test(name, fn)

        summary = (
            "=" * 80 + "\n"
            f"R1.0.4 REMEDIATION QA SUMMARY: Total: {self.passed + self.failed} | "
            f"PASSED: {self.passed} | FAILED: {self.failed}\n"
            f"STATUS: {'REMEDIATION_PASS' if self.failed == 0 else 'REMEDIATION_FAIL'}\n"
            + "=" * 80
        )
        self.log(summary)
        return self.failed


if __name__ == "__main__":
    suite = TestPhase07R104RemediationSuite()
    sys.exit(suite.run_all())
