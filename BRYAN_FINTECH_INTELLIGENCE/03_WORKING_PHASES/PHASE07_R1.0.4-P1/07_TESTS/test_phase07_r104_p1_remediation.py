#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_phase07_r104_p1_remediation.py
===================================
Validation Suite for Phase 07 R1.0.4-P1 Targeted Critical Remediation:
  P07-P1-TEST-01: Different financial inputs produce different editorial conclusions.
  P07-P1-TEST-02: No contradictory evidence produces counterEvidence = [].
  P07-P1-TEST-03: Removing payment demand downgrades/removes opportunity.
  P07-P1-TEST-04: Sports-only input produces zero payment opportunities.
  P07-P1-TEST-05: Historical executionId cannot be normalized into current live provenance.
  P07-P1-TEST-06: Missing retrievedAt timestamp cannot become valid live retrieval.
"""

import os
import sys
import copy
import json
import unittest

THIS_DIR = os.path.abspath(os.path.dirname(__file__))
PHASE07_ROOT = os.path.abspath(os.path.join(THIS_DIR, ".."))
SRC_DIR = os.path.join(PHASE07_ROOT, "02_SOURCE_CODE")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from phase07_dynamic_news_engine import Phase07DynamicNewsEngine
from phase07_editorial_intelligence_engine import Phase07EditorialIntelligenceEngine
from market_pulse_discovery import MarketPulseDiscoveryEngine


class TestPhase07R104P1RemediationSuite:
    def __init__(self):
        self.runtime_config = {
            "executionId": "EXEC-20261111-P1-TEST",
            "editionDate": "2026-11-11",
            "editionId": "ED-20261111-D01"
        }

    # -------------------------------------------------------------------------
    # TEST 01: Different Financial Inputs Produce Different Editorial Conclusions
    # -------------------------------------------------------------------------
    def test_01_different_financial_inputs_produce_different_conclusions(self):
        dataset_a = [
            {
                "eventId": "EVT-FX-01",
                "headline": "Ngân hàng Nhà nước bán 4 tỷ USD can thiệp để ổn định tỷ giá liên ngân hàng",
                "summary": "Quy mô can thiệp nhằm hạ nhiệt tỷ giá USD/VND đang chịu áp lực từ đồng USD quốc tế.",
                "researchDomain": "State Bank of Vietnam policy",
                "primarySource": "Thời báo Ngân hàng",
                "url": "https://thoibaonganhang.vn/nhnn-ban-usd.htm",
                "publicationDate": "2026-11-11",
                "sourceVerificationStatus": "VERIFIED"
            }
        ]
        dataset_b = [
            {
                "eventId": "EVT-RETAIL-01",
                "headline": "Doanh số thanh toán quét mã QR bán lẻ tăng trưởng 120% trong mùa mua sắm cuối năm",
                "summary": "Người tiêu dùng ưu tiên sử dụng mã VietQR tại các siêu thị và cửa hàng tiện lợi.",
                "researchDomain": "Cashless payments & VietQR",
                "primarySource": "VnEconomy",
                "url": "https://vneconomy.vn/qr-ban-le-tang-truong.htm",
                "publicationDate": "2026-11-11",
                "sourceVerificationStatus": "VERIFIED"
            }
        ]

        eng_a = Phase07EditorialIntelligenceEngine(
            verified_news=dataset_a,
            audited_facts_bundle={},
            audited_market_pulse=[],
            runtime_config=self.runtime_config
        )
        theses_a = eng_a.generate_core_theses()["theses"]

        eng_b = Phase07EditorialIntelligenceEngine(
            verified_news=dataset_b,
            audited_facts_bundle={},
            audited_market_pulse=[],
            runtime_config=self.runtime_config
        )
        theses_b = eng_b.generate_core_theses()["theses"]

        assert len(theses_a) > 0 and len(theses_b) > 0
        assert theses_a[0]["centralArgument"] != theses_b[0]["centralArgument"]
        assert "bán 4 tỷ USD" in theses_a[0]["centralArgument"] or "tỷ giá" in theses_a[0]["centralArgument"]
        assert "120%" in theses_b[0]["centralArgument"] or "quét mã QR" in theses_b[0]["centralArgument"] or "bán lẻ" in theses_b[0]["centralArgument"]

    # -------------------------------------------------------------------------
    # TEST 02: No Contradictory Evidence Produces counterEvidence = []
    # -------------------------------------------------------------------------
    def test_02_no_contradictory_evidence_produces_empty_counter_evidence(self):
        consistent_events = [
            {
                "eventId": "EVT-TOUR-01",
                "headline": "Lượng khách quốc tế đến Việt Nam tháng 10 đạt hơn 1,4 triệu lượt",
                "summary": "Tăng trưởng tích cực từ các thị trường trọng điểm Hàn Quốc, Trung Quốc và Nhật Bản.",
                "researchDomain": "Consumer spending & retail",
                "primarySource": "Cục Du lịch Quốc gia",
                "url": "https://vietnamtourism.gov.vn/khach-quoc-te-t10.htm",
                "publicationDate": "2026-11-11",
                "sourceVerificationStatus": "VERIFIED"
            },
            {
                "eventId": "EVT-TOUR-02",
                "headline": "Doanh thu dịch vụ lưu trú và lữ hành 10 tháng tăng 18,5% so với cùng kỳ",
                "summary": "Sự phục hồi mạnh mẽ của ngành du lịch thúc đẩy chi tiêu tiêu dùng tại các điểm đến.",
                "researchDomain": "Consumer spending & retail",
                "primarySource": "Tổng cục Thống kê",
                "url": "https://gso.gov.vn/doanh-thu-du-lich.htm",
                "publicationDate": "2026-11-11",
                "sourceVerificationStatus": "VERIFIED"
            }
        ]

        ed_eng = Phase07EditorialIntelligenceEngine(
            verified_news=consistent_events,
            audited_facts_bundle={},
            audited_market_pulse=[],
            runtime_config=self.runtime_config
        )
        theses = ed_eng.generate_core_theses()["theses"]
        assert len(theses) > 0
        for th in theses:
            # Without opposing/contradictory events, counterEvidence must strictly be []
            assert th["counterEvidence"] == [], f"Expected empty counterEvidence, got {th['counterEvidence']}"

    # -------------------------------------------------------------------------
    # TEST 03: Removing Payment Demand Downgrades/Removes Opportunity
    # -------------------------------------------------------------------------
    def test_03_removing_payment_demand_downgrades_or_removes_opportunity(self):
        # Case A: Logistics with explicit payment adoption keywords
        event_with_pay = [
            {
                "eventId": "EVT-JT-01",
                "headline": "J&T Cargo hợp tác triển khai SmartPOS và thu hộ COD không tiền mặt trên toàn mạng lưới",
                "summary": "Shipper sử dụng mã VietQR động để thu hộ tiền hàng.",
                "researchDomain": "Logistics & freight",
                "primarySource": "Báo Đầu tư",
                "url": "https://baodautu.vn/jt-smartpos.htm",
                "publicationDate": "2026-11-11",
                "sourceVerificationStatus": "VERIFIED"
            }
        ]
        ed_a = Phase07EditorialIntelligenceEngine(
            verified_news=event_with_pay, audited_facts_bundle={}, audited_market_pulse=[], runtime_config=self.runtime_config
        )
        radars_a = ed_a.generate_payment_radar_signals()["signals"]
        assert len(radars_a) >= 1
        assert radars_a[0]["opportunityType"] == "VERIFIED_OPPORTUNITY"
        assert radars_a[0]["confidence"] == "HIGH"
        assert "SCALE" in radars_a[0]["recommendedNextAction"]

        # Case B: Logistics freight expansion WITHOUT payment demand evidence
        event_without_pay = [
            {
                "eventId": "EVT-JT-02",
                "headline": "J&T Cargo mở rộng 5 trung tâm trung chuyển hàng nặng tại miền Bắc",
                "summary": "Đầu tư nâng cấp đội xe tải lớn để phục vụ vận tải hàng pallet công nghiệp.",
                "researchDomain": "Logistics & freight",
                "primarySource": "Báo Đầu tư",
                "url": "https://baodautu.vn/jt-trung-tam.htm",
                "publicationDate": "2026-11-11",
                "sourceVerificationStatus": "VERIFIED"
            }
        ]
        ed_b = Phase07EditorialIntelligenceEngine(
            verified_news=event_without_pay, audited_facts_bundle={}, audited_market_pulse=[], runtime_config=self.runtime_config
        )
        radars_b = ed_b.generate_payment_radar_signals()["signals"]
        assert len(radars_b) >= 1
        # Downgraded to POTENTIAL_OPPORTUNITY and VALIDATE
        assert radars_b[0]["opportunityType"] == "POTENTIAL_OPPORTUNITY"
        assert radars_b[0]["confidence"] == "MEDIUM"
        assert "VALIDATE" in radars_b[0]["recommendedNextAction"]

    # -------------------------------------------------------------------------
    # TEST 04: Sports-Only Input Produces Zero Payment Opportunities
    # -------------------------------------------------------------------------
    def test_04_sports_only_produces_zero_payment_opportunities(self):
        sports_events = [
            {
                "eventId": "EVT-SPORT-01",
                "headline": "Đội tuyển bóng đá nam quốc gia giành vé vào vòng chung kết Asian Cup",
                "summary": "Chiến thắng thuyết phục 3-0 trước đối thủ trong trận đấu trên sân Mỹ Đình.",
                "researchDomain": "Sports & Entertainment",
                "primarySource": "Thể thao 247",
                "url": "https://thethao247.vn/tuyen-vn-asian-cup.htm",
                "publicationDate": "2026-11-11",
                "sourceVerificationStatus": "VERIFIED"
            }
        ]
        ed_sports = Phase07EditorialIntelligenceEngine(
            verified_news=sports_events,
            audited_facts_bundle={},
            audited_market_pulse=[],
            runtime_config=self.runtime_config
        )
        res = ed_sports.generate_payment_radar_signals()
        signals = res["signals"]
        active_opps = [s for s in signals if s.get("opportunityType") in ("VERIFIED_OPPORTUNITY", "EMERGING_OPPORTUNITY", "POTENTIAL_OPPORTUNITY")]
        assert len(active_opps) == 0, f"Expected 0 active payment opportunities from sports news, got {len(active_opps)}"

        # Verify decision cards and 5 questions handle zero opportunities honestly
        dec_res = ed_sports.generate_decision_cards(theses=[], chains=[], radar_signals=[])
        assert dec_res["totalDecisionCards"] == 0
        q5 = dec_res["fiveQuestionsExecutiveSynthesis"]
        assert "Chưa ghi nhận cơ hội thanh toán" in q5["question3_cashlessPaymentOpportunities"]
        assert "Không có hành động thương mại" in q5["question5_bryanNextActions"]

    # -------------------------------------------------------------------------
    # TEST 05: Historical executionId Cannot Be Normalized into Current Live Provenance
    # -------------------------------------------------------------------------
    def test_05_historical_execution_id_cannot_be_normalized_into_current_live_provenance(self):
        historical_ledger = [
            {
                "executionId": "EXEC-20261108-OLD",
                "originalUrl": "https://cafef.vn/article-old.chn",
                "canonicalUrl": "https://cafef.vn/article-old.chn",
                "statusCode": 200,
                "responseSha256": "1111111111111111111111111111111111111111111111111111111111111111",
                "retrievedAt": "2026-11-08T10:00:00+07:00"
            }
        ]
        current_execution_id = "EXEC-20261111-CURRENT"
        norm = Phase07DynamicNewsEngine._normalize_retrieval_ledger(historical_ledger, execution_id=current_execution_id)
        assert len(norm) == 1
        rec = norm[0]
        # Must preserve original historical executionId, NOT overwrite with current_execution_id
        assert rec["executionId"] == "EXEC-20261108-OLD"
        assert rec["retrievalStatus"] == "HISTORICAL_PROVENANCE_MISMATCH"
        assert rec["sourceVerificationStatus"] == "UNVERIFIED"

    # -------------------------------------------------------------------------
    # TEST 06: Missing retrievedAt Timestamp Cannot Become Valid Live Retrieval
    # -------------------------------------------------------------------------
    def test_06_missing_retrieved_at_cannot_become_valid_live_retrieval(self):
        missing_ts_ledger = [
            {
                "executionId": "EXEC-20261111-CURRENT",
                "originalUrl": "https://cafef.vn/article-no-ts.chn",
                "canonicalUrl": "https://cafef.vn/article-no-ts.chn",
                "statusCode": 200,
                "responseSha256": "2222222222222222222222222222222222222222222222222222222222222222",
                "retrievedAt": None  # Missing timestamp
            }
        ]
        norm = Phase07DynamicNewsEngine._normalize_retrieval_ledger(missing_ts_ledger, execution_id="EXEC-20261111-CURRENT")
        assert len(norm) == 1
        rec = norm[0]
        # Must NOT fabricate retrievedAt from current system clock
        assert rec["retrievedAt"] is None
        assert rec["retrievalStatus"] == "TIMESTAMP_MISSING"
        assert rec["sourceVerificationStatus"] == "UNVERIFIED"

    # -------------------------------------------------------------------------
    # TEST 07: Credit Growth vs Bad Debt Surge Pivots Thesis, Counter-Evidence & Decisions
    # -------------------------------------------------------------------------
    def test_07_credit_growth_vs_bad_debt_surge_pivots_thesis_counter_evidence_and_decisions(self):
        """
        Validates User Image Mandate:
        'Ví dụ, khi dữ liệu chuyển từ tăng trưởng tín dụng mạnh sang nợ xấu tăng nhanh,
         hệ thống phải thay đổi luận điểm, counter-evidence và mức độ rủi ro tương ứng.
         Không được chỉ thay headline mà giữ nguyên kết luận.'
        """
        # Scenario A: Strong Credit Growth
        dataset_growth = [
            {
                "eventId": "EVT-CREDIT-GROWTH-01",
                "headline": "Tín dụng toàn hệ thống ngân hàng bứt phá tăng trưởng mạnh 16%, mặt bằng lãi suất cho vay hạ nhiệt kích thích sản xuất",
                "summary": "Dòng vốn tín dụng chảy mạnh vào các lĩnh vực ưu tiên và sản xuất kinh doanh phục vụ mùa vụ cuối năm.",
                "researchDomain": "Banking & credit growth",
                "primarySource": "Thời báo Ngân hàng",
                "url": "https://thoibaonganhang.vn/tin-dung-tang-truong-16.htm",
                "publicationDate": "2026-11-11",
                "sourceVerificationStatus": "VERIFIED"
            }
        ]
        facts_growth = {
            "uniqueVerifiedFacts": [
                {
                    "factId": "FACT-GROWTH-01",
                    "eventId": "EVT-CREDIT-GROWTH-01",
                    "metricName": "Tăng trưởng tín dụng",
                    "extractedExpression": "tăng trưởng 16%",
                    "verifiedEntity": "Ngân hàng Nhà nước",
                    "isDuplicate": False
                }
            ]
        }

        # Scenario B: Surging Bad Debt / Credit Risk Stress
        dataset_bad_debt = [
            {
                "eventId": "EVT-BAD-DEBT-01",
                "headline": "Nợ xấu ngân hàng tăng nhanh lên 4,55%, áp lực trích lập dự phòng rủi ro đè nặng lợi nhuận các nhà băng",
                "summary": "Tỷ lệ nợ xấu nội bảng và nợ tiềm ẩn tăng mạnh, buộc các tổ chức tín dụng phải gia tăng trích lập dự phòng rủi ro.",
                "researchDomain": "Banking & credit growth",
                "primarySource": "VnEconomy",
                "url": "https://vneconomy.vn/no-xau-tang-nhanh.htm",
                "publicationDate": "2026-11-11",
                "sourceVerificationStatus": "VERIFIED"
            }
        ]
        facts_bad_debt = {
            "uniqueVerifiedFacts": [
                {
                    "factId": "FACT-NPL-01",
                    "eventId": "EVT-BAD-DEBT-01",
                    "metricName": "Tỷ lệ nợ xấu",
                    "extractedExpression": "tăng lên 4,55%",
                    "verifiedEntity": "Hệ thống NHTM",
                    "isDuplicate": False
                }
            ]
        }

        # Execution A: Growth
        eng_growth = Phase07EditorialIntelligenceEngine(
            verified_news=dataset_growth,
            audited_facts_bundle=facts_growth,
            audited_market_pulse=[],
            runtime_config=self.runtime_config
        )
        theses_growth = eng_growth.generate_core_theses()["theses"]
        chains_growth = eng_growth.generate_macro_to_micro_chains()["chains"]
        decisions_growth = eng_growth.generate_decision_cards(theses=theses_growth, chains=chains_growth)["cards"]

        # Execution B: Bad Debt
        eng_bad_debt = Phase07EditorialIntelligenceEngine(
            verified_news=dataset_bad_debt,
            audited_facts_bundle=facts_bad_debt,
            audited_market_pulse=[],
            runtime_config=self.runtime_config
        )
        theses_bad_debt = eng_bad_debt.generate_core_theses()["theses"]
        chains_bad_debt = eng_bad_debt.generate_macro_to_micro_chains()["chains"]
        decisions_bad_debt = eng_bad_debt.generate_decision_cards(theses=theses_bad_debt, chains=chains_bad_debt)["cards"]

        # Assert 1: Core Theses completely pivot
        th_g = theses_growth[0]
        th_d = theses_bad_debt[0]

        assert th_g["centralArgument"] != th_d["centralArgument"]
        assert th_g["whyItMatters"] != th_d["whyItMatters"]
        assert th_g["riskPosture"] == "POSTURE_EXPANSION_GROWTH"
        assert th_d["riskPosture"] == "POSTURE_CREDIT_RISK_STRESS"
        assert th_g["riskLevel"] in ("LOW_RISK", "CONTROLLED_RISK")
        assert th_d["riskLevel"] == "HIGH_RISK"

        # Assert 2: Semantic grounding of Why It Matters & Central Argument
        assert "tăng trưởng" in th_g["centralArgument"].lower()
        assert "mở rộng" in th_g["whyItMatters"].lower() or "vòng quay vốn" in th_g["whyItMatters"].lower()

        assert "nợ xấu" in th_d["centralArgument"].lower() or "dự phòng" in th_d["centralArgument"].lower()
        assert "nợ xấu" in th_d["whyItMatters"].lower() or "dự phòng" in th_d["whyItMatters"].lower()

        # Assert 3: Macro-to-Micro transmission chains adapt to stance
        assert "giải ngân" in chains_growth[0]["bankingImpact"].lower() or "tăng trưởng" in chains_growth[0]["bankingImpact"].lower()
        assert "thu hồi nợ" in chains_bad_debt[0]["bankingImpact"].lower() or "dự phòng" in chains_bad_debt[0]["bankingImpact"].lower()

        # Assert 4: Decision Cards completely pivot from Commercial to Risk Defense
        assert len(decisions_growth) > 0 and len(decisions_bad_debt) > 0
        dec_g = decisions_growth[0]
        dec_d = decisions_bad_debt[0]

        assert dec_g["decisionCategory"] == "COMMERCIAL_OPPORTUNITY"
        assert dec_g["recommendedAction"] == "SCALE"

        assert dec_d["decisionCategory"] == "RISK_DEFENSE"
        assert dec_d["recommendedAction"] == "DEFEND"
        assert "Kiểm soát Rủi ro Tín dụng" in dec_d["title"] or "Nợ xấu" in dec_d["title"]

        # Assert 5: Counter-evidence logic works dynamically across mixed datasets
        mixed_dataset = dataset_growth + dataset_bad_debt
        mixed_facts = {
            "uniqueVerifiedFacts": facts_growth["uniqueVerifiedFacts"] + facts_bad_debt["uniqueVerifiedFacts"]
        }
        eng_mixed = Phase07EditorialIntelligenceEngine(
            verified_news=mixed_dataset,
            audited_facts_bundle=mixed_facts,
            audited_market_pulse=[],
            runtime_config=self.runtime_config
        )
        theses_mixed = eng_mixed.generate_core_theses()["theses"]
        assert len(theses_mixed) > 0
        # When opposing signals are present in the same dataset, counterEvidence must be populated
        assert len(theses_mixed[0]["counterEvidence"]) > 0
        assert theses_mixed[0]["confidenceLevel"] == "MEDIUM"


if __name__ == "__main__":
    t = TestPhase07R104P1RemediationSuite()
    for m in dir(t):
        if m.startswith("test_"):
            getattr(t, m)()
            print(f"[PASS] {m}")
    print("ALL 7 R1.0.4-P1 TESTS PASSED!")
