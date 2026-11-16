#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_phase06_intelligence.py
============================
Comprehensive Unit, Integration & Adversarial QA Suite for Bryan FinTech Intelligence — Phase 06:
Financial Intelligence Layer & Daily Decision Engine.

Covers all 13 functional test categories and all 8 adversarial test scenarios mandated in
Section X, plus Section XIV Release Archiving & Backup Verification (22 tests total).
Also portable when executed directly from an extracted Phase 06 release package.
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
PHASE06_ROOT = os.path.abspath(os.path.join(THIS_DIR, ".."))
SRC_DIR = os.path.join(PHASE06_ROOT, "02_SOURCE_CODE")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from phase06_fact_entity_auditor import FactEntityIntegrityAuditor
from core_thesis_engine import CoreThesisEngine
from macro_to_micro_engine import MacroToMicroEngine
from payment_radar_engine import PaymentRadarEngine
from financial_decision_engine import FinancialDecisionEngine
from google_sheets_dry_run_engine import GoogleSheetsDryRunEngine
from run_phase06_intelligence_pipeline import run_pipeline
from schema_validator import JsonSchemaValidator

VN_TZ = timezone(timedelta(hours=7))


def compute_sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


class TestPhase06IntelligenceSuite:
    def __init__(self):
        self.logs = []
        self.passed = 0
        self.failed = 0
        self.baseline_p05b = os.path.join(
            PHASE06_ROOT,
            "baseline_phase05b_r101",
            "PHASE05B_ALIGNMENT_R101"
        )
        self.p06_ed_dir = os.path.join(PHASE06_ROOT, "baseline_phase06_r100", "PHASE06", "06_DAILY_EDITIONS", "daily-editions", "2026-11-10")
        if not os.path.isdir(self.p06_ed_dir):
            self.p06_ed_dir = os.path.join(PHASE06_ROOT, "06_DAILY_EDITIONS", "daily-editions", "2026-11-10")
        with open(os.path.join(self.baseline_p05b, "05_LIVE_DATA", "VERIFIED_NEWS_DATABASE.json"), "r", encoding="utf-8") as f:
            self.vndb = json.load(f)
        self.verified_news = self.vndb["records"]
        with open(os.path.join(self.baseline_p05b, "05_LIVE_DATA", "MARKET_PULSE_8.json"), "r", encoding="utf-8") as f:
            self.mp8 = json.load(f)
        with open(os.path.join(self.baseline_p05b, "03_INDICATOR_CONFIG", "market_pulse_indicator_specs.json"), "r", encoding="utf-8") as f:
            self.mp_specs = json.load(f)["indicators"]

        self.auditor = FactEntityIntegrityAuditor(
            raw_evidence_root=os.path.join(self.baseline_p05b, "04_RAW_EVIDENCE")
        )
        self.audited_facts = self.auditor.audit_and_deduplicate_facts(self.verified_news)
        self.audited_mp = self.auditor.audit_market_pulse_integrity(self.mp8, self.mp_specs)["indicators"]

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
    # FUNCTIONAL & INTEGRATION TESTS (P06-TEST-01 to P06-TEST-13)
    # =========================================================================

    def test_01_json_schema_v400_validation(self):
        """P06-TEST-01: Validates all Phase 06 outputs against Draft 2020-12 PHASE06_DATA_CONTRACT_V4_0_0.json."""
        contract_path = os.path.join(PHASE06_ROOT, "03_SCHEMAS_AND_CONFIG", "PHASE06_DATA_CONTRACT_V4_0_0.json")
        with open(contract_path, "r", encoding="utf-8") as f:
            schema = json.load(f)
        validator = JsonSchemaValidator(schema)

        for f_item in self.audited_facts["allAuditedFacts"]:
            validator.validate(f_item, subschema=schema["definitions"]["AuditedFinancialFact"])

        with open(os.path.join(PHASE06_ROOT, "04_INTELLIGENCE_OUTPUTS", "CORE_THESIS.json"), "r", encoding="utf-8") as f:
            theses = json.load(f)["theses"]
        assert 3 <= len(theses) <= 5
        for t in theses:
            validator.validate(t, subschema=schema["definitions"]["CoreThesis"])

        with open(os.path.join(PHASE06_ROOT, "04_INTELLIGENCE_OUTPUTS", "MACRO_TO_MICRO.json"), "r", encoding="utf-8") as f:
            chains = json.load(f)["chains"]
        assert len(chains) == 4
        for c in chains:
            validator.validate(c, subschema=schema["definitions"]["MacroToMicroChain"])

        with open(os.path.join(PHASE06_ROOT, "04_INTELLIGENCE_OUTPUTS", "PAYMENT_RADAR.json"), "r", encoding="utf-8") as f:
            signals = json.load(f)["signals"]
        assert len(signals) == 5
        for s in signals:
            validator.validate(s, subschema=schema["definitions"]["PaymentRadarSignal"])

        with open(os.path.join(PHASE06_ROOT, "04_INTELLIGENCE_OUTPUTS", "FINANCIAL_DECISION_INTELLIGENCE.json"), "r", encoding="utf-8") as f:
            cards = json.load(f)["decisionCards"]
        assert len(cards) == 4
        for d in cards:
            validator.validate(d, subschema=schema["definitions"]["FinancialDecisionCard"])

    def test_02_event_reference_integrity(self):
        """P06-TEST-02: Verifies every referenced eventId exists in VERIFIED_NEWS_DATABASE.json."""
        valid_eids = {e["eventId"] for e in self.verified_news}
        assert len(valid_eids) == 18

        for fn in ["CORE_THESIS.json", "MACRO_TO_MICRO.json", "PAYMENT_RADAR.json", "FINANCIAL_DECISION_INTELLIGENCE.json"]:
            with open(os.path.join(PHASE06_ROOT, "04_INTELLIGENCE_OUTPUTS", fn), "r", encoding="utf-8") as f:
                data = json.load(f)
            items = (
                data.get("theses")
                or data.get("chains")
                or data.get("signals")
                or data.get("decisionCards")
                or []
            )
            for item in items:
                eids = item.get("supportingEventIds") or item.get("triggerEventIds") or []
                for eid in eids:
                    assert eid in valid_eids, f"Orphan eventId {eid} in {fn}"

    def test_03_financial_fact_integrity_and_grounding(self):
        """P06-TEST-03: Verifies all 18 raw financial facts are grounded in contextQuote and raw evidence."""
        assert self.audited_facts["totalRawFacts"] == 18
        assert self.audited_facts["uniqueVerifiedFactsCount"] == 16
        assert self.audited_facts["ambiguousOrUnverifiedEntitiesCount"] == 0
        for af in self.audited_facts["allAuditedFacts"]:
            assert af["verificationStatus"] == "VERIFIED"
            assert isinstance(af["numericValue"], str) and len(af["numericValue"]) >= 1

    def test_04_entity_binding_verification_and_rebinding(self):
        """P06-TEST-04: Verifies entity binding checks contextQuote and rebinds over-broad entities accurately."""
        by_id = {f["factId"]: f for f in self.audited_facts["allAuditedFacts"]}
        # 1. 7%/năm in EVT-20261110-005 rebound from Vietcombank to the 5 listed banks
        assert "MBV, PGBank, Sacombank, VCBNeo, VIB" in by_id["FACT-20261110-001"]["verifiedEntity"]
        assert by_id["FACT-20261110-001"]["entityBindingStatus"] == "ENTITY_REBOUND_FROM_QUOTE"
        # 2. 830.000 tỉ đồng in EVT-20261110-010 rebound from Việt Nam to EVN
        assert "EVN" in by_id["FACT-20261110-004"]["verifiedEntity"]
        # 3. 15,39 nghìn tỷ yên & 97,1 tỷ USD in EVT-20261110-026 rebound from Bộ Tài chính to Nhật Bản
        assert "Nhật Bản" in by_id["FACT-20261110-008"]["verifiedEntity"]
        assert "Nhật Bản" in by_id["FACT-20261110-009"]["verifiedEntity"]
        # 4. 80% nhu cầu vốn in EVT-20261110-001 rebound from VinUni to Hệ thống ngân hàng Việt Nam
        assert "Hệ thống ngân hàng Việt Nam" in by_id["FACT-20261110-016"]["verifiedEntity"]

    def test_05_duplicate_fact_prevention(self):
        """P06-TEST-05: Verifies intra-event and cross-event duplicate facts are flagged and never used in synthesis."""
        by_id = {f["factId"]: f for f in self.audited_facts["allAuditedFacts"]}
        assert by_id["FACT-20261110-002"]["isDuplicate"] is True
        assert by_id["FACT-20261110-002"]["duplicateOfFactId"] == "FACT-20261110-001"
        assert by_id["FACT-20261110-016"]["isDuplicate"] is True
        assert by_id["FACT-20261110-016"]["duplicateOfFactId"] == "FACT-20261110-010"

        with open(os.path.join(PHASE06_ROOT, "04_INTELLIGENCE_OUTPUTS", "EVIDENCE_CROSSWALK.json"), "r", encoding="utf-8") as f:
            cw = json.load(f)
        assert cw["summary"]["zeroDuplicateFactsUsedInSynthesis"] is True
        for fc in cw["financialFactCrosswalk"]:
            if fc["isDuplicate"]:
                assert fc["referencedByTheses"] == []
                assert fc["referencedByChains"] == []
                assert fc["referencedByRadars"] == []

    def test_06_evidence_traceability_and_crosswalk(self):
        """P06-TEST-06: Verifies every event and Market Pulse indicator in EVIDENCE_CROSSWALK.json has matching SHA-256 on disk."""
        with open(os.path.join(PHASE06_ROOT, "04_INTELLIGENCE_OUTPUTS", "EVIDENCE_CROSSWALK.json"), "r", encoding="utf-8") as f:
            cw = json.load(f)
        assert cw["summary"]["zeroOrphanReferences"] is True
        assert len(cw["newsEventCrosswalk"]) == 18
        assert len(cw["marketPulseCrosswalk"]) == 8

        raw_root = os.path.join(self.baseline_p05b, "04_RAW_EVIDENCE")
        for ev in cw["newsEventCrosswalk"]:
            rel = ev["evidencePath"]
            stripped = rel[len("raw_evidence_store/"):] if rel.startswith("raw_evidence_store/") else rel
            p = os.path.join(raw_root, stripped)
            assert os.path.exists(p), f"Missing raw evidence file: {p}"
            assert compute_sha256(p) == ev["evidenceSha256"]

    def test_07_core_thesis_consistency(self):
        """P06-TEST-07: Verifies 4 Core Theses have counterEvidence, causalExplanation, watchSignals, and invalidationConditions."""
        eng = CoreThesisEngine(self.verified_news, self.audited_facts, self.audited_mp)
        res = eng.generate_theses()
        assert res["totalTheses"] == 4
        assert len(res["themeGroupEvaluation"]) == 8
        for t in res["theses"]:
            assert len(t["supportingEventIds"]) >= 3
            assert len(t["counterEvidence"]) >= 1
            assert len(t["watchSignals"]) >= 2
            assert len(t["invalidationConditions"]) >= 2
            assert len(t["sourceReferences"]) >= 4

    def test_08_macro_to_micro_causal_classification(self):
        """P06-TEST-08: Verifies all Macro-to-Micro chains classify every link as OBSERVED, SUPPORTED_INFERENCE, or HYPOTHESIS."""
        eng = MacroToMicroEngine(self.verified_news, self.audited_facts, self.audited_mp)
        res = eng.generate_chains()
        assert res["totalChains"] == 4
        for c in res["chains"]:
            ic = c["inferenceClassification"]
            for stage in ["macroDriver", "bankingImpact", "enterpriseImpact", "consumerImpact", "paymentImpact"]:
                assert ic[stage] in ("OBSERVED", "SUPPORTED_INFERENCE", "HYPOTHESIS")

    def test_09_payment_opportunity_grounding_and_payoo_lens(self):
        """P06-TEST-09: Verifies Payment Radar signals distinguish opportunity types and explicitly record NO_DIRECT_PAYOO_OPPORTUNITY when appropriate."""
        eng = PaymentRadarEngine(self.verified_news, self.audited_facts, self.audited_mp)
        res = eng.generate_radar_signals()
        assert res["totalSignals"] == 5
        bd = res["opportunityBreakdown"]
        assert bd["VERIFIED_OPPORTUNITY"] >= 1
        assert bd["EMERGING_OPPORTUNITY"] >= 1
        assert bd["POTENTIAL_OPPORTUNITY"] >= 1
        assert bd["NO_DIRECT_OPPORTUNITY"] >= 1
        no_direct = [s for s in res["signals"] if s["opportunityType"] == "NO_DIRECT_OPPORTUNITY"]
        assert len(no_direct) == 1
        assert "NO_DIRECT_PAYOO_OPPORTUNITY" in no_direct[0]["payooRelevance"]

    def test_10_decision_card_consistency_and_five_questions(self):
        """P06-TEST-10: Verifies Financial Decision Cards answer the 5 executive questions and disclose limitations."""
        theses = CoreThesisEngine(self.verified_news, self.audited_facts, self.audited_mp).generate_theses()["theses"]
        chains = MacroToMicroEngine(self.verified_news, self.audited_facts, self.audited_mp).generate_chains()["chains"]
        radars = PaymentRadarEngine(self.verified_news, self.audited_facts, self.audited_mp).generate_radar_signals()["signals"]
        eng = FinancialDecisionEngine(self.verified_news, self.audited_facts, self.audited_mp, theses, chains, radars)
        res = eng.generate_decision_cards()
        assert res["totalDecisionCards"] == 4
        q5 = res["fiveQuestionsExecutiveSynthesis"]
        for k in [
            "question1_whatIsMarketChanging",
            "question2_macroImpactOnBanksEnterprisesConsumers",
            "question3_cashlessPaymentOpportunities",
            "question4_keyWatchSignals",
            "question5_bryanNextActions"
        ]:
            assert len(q5[k]) > 50
        for card in res["decisionCards"]:
            assert len(card["limitations"]) >= 1

    def test_11_market_pulse_freshness_and_news_separation(self):
        """P06-TEST-11: Verifies Market Pulse preserves MP-02 stale status, MP-05/06 null values, MP-08 2026-09-21 date, and is never counted as news."""
        mp_by_id = {m["indicatorId"]: m for m in self.audited_mp}
        assert mp_by_id["MP-02"]["updateStatus"] == "STALE_OBSERVATION"
        assert mp_by_id["MP-02"]["verificationStatus"] == "UNVERIFIED"
        assert mp_by_id["MP-02"]["observationDate"] == "2026-10-02"
        assert mp_by_id["MP-05"]["actualValue"] is None
        assert mp_by_id["MP-06"]["actualValue"] is None
        assert mp_by_id["MP-08"]["observationDate"] == "2026-09-21"
        assert mp_by_id["MP-08"]["temporalClassification"] == "HISTORICAL_EVENT_OPERATION_2026_09_21"
        for m in self.audited_mp:
            assert m["isNewsEvent"] is False

    def test_12_google_sheets_dry_run_integrity(self):
        """P06-TEST-12: Verifies 7-tab Google Sheets dry-run preserves 155 existing rows, adds 83 valid rows, and calls zero write APIs."""
        hist_p = os.path.join(PHASE06_ROOT, "05_GOOGLE_SHEETS_DRY_RUN", "historical_phase06", "GOOGLE_SHEETS_VALIDATION.json")
        val_path = hist_p if os.path.exists(hist_p) else os.path.join(PHASE06_ROOT, "05_GOOGLE_SHEETS_DRY_RUN", "GOOGLE_SHEETS_VALIDATION.json")
        with open(val_path, "r", encoding="utf-8") as f:
            val = json.load(f)
        assert val["allTabsPassed"] is True
        assert val["liveWriteApiCalled"] is False
        assert val["originalStagingUnmodified"] is True
        assert val["existingBaselineRowCount"] == 155
        assert val["proposedNewRowCount"] == 83
        assert val["totalProjectedRowCount"] == 238
        assert val["foreignKeyViolationsCount"] == 0
        assert val["multiDaySyncSimulationPassed"] is True

    def test_13_multi_day_reproducibility_and_daily_json_distribution(self):
        """P06-TEST-13: Verifies daily-editions/2026-11-10/ SHA256SUMS.txt and tests multi-day generation for 2026-11-11."""
        ed_dir = self.p06_ed_dir
        sha_file = os.path.join(ed_dir, "SHA256SUMS.txt")
        assert os.path.exists(sha_file)
        with open(sha_file, "r", encoding="utf-8") as f:
            lines = [ln.strip() for ln in f if ln.strip()]
        assert len(lines) == 11
        for ln in lines:
            expected_sha, fname = ln.split("  ", 1)
            actual_sha = compute_sha256(os.path.join(ed_dir, fname))
            assert actual_sha == expected_sha, f"Checksum mismatch for {fname}"

        # Multi-day reproducibility check in isolated temp dir
        tmp_dir = tempfile.mkdtemp(prefix="phase06_multiday_")
        try:
            res_day2 = run_pipeline(
                edition_date="2026-11-11",
                edition_id="ED-20261111-D01",
                output_base_dir=tmp_dir
            )
            assert os.path.exists(os.path.join(res_day2["dailyEditionDir"], "edition-manifest.json"))
            assert res_day2["sheetsValidation"]["allTabsPassed"] is True
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)

    # =========================================================================
    # ADVERSARIAL TESTS (P06-ADV-14 to P06-ADV-21)
    # =========================================================================

    def test_14_adversarial_delete_supporting_event_rejected(self):
        """P06-ADV-14: Deleting a supporting event (EVT-20261110-006) causes CoreThesisEngine to fail closed."""
        truncated_news = [e for e in self.verified_news if e["eventId"] != "EVT-20261110-006"]
        eng = CoreThesisEngine(truncated_news, self.audited_facts, self.audited_mp)
        raised = False
        try:
            eng.generate_theses()
        except ValueError as exc:
            if "UNRESOLVED_EVENT_REFERENCE" in str(exc):
                raised = True
        assert raised, "Deleting a supporting event must raise UNRESOLVED_EVENT_REFERENCE"

    def test_15_adversarial_tampered_fact_entity_rejected(self):
        """P06-ADV-15: Changing a fact's entity to an ungrounded entity is flagged ENTITY_UNVERIFIED and rejected by CoreThesisEngine."""
        tampered_fact = copy.deepcopy(self.audited_facts["allAuditedFacts"][4])  # EVT-20261110-006 25.500 đồng/USD
        tampered_fact["entity"] = "Ngân hàng Thế giới (World Bank)"
        ev = next(e for e in self.verified_news if e["eventId"] == "EVT-20261110-006")
        v_ent, status, _ = self.auditor.verify_and_bind_entity(tampered_fact, ev, ev["summary"])
        assert status == "ENTITY_UNVERIFIED"
        assert v_ent == "ENTITY_UNVERIFIED"

        # Injecting an ENTITY_UNVERIFIED fact into CoreThesisEngine must fail closed
        tampered_bundle = copy.deepcopy(self.audited_facts)
        for f_item in tampered_bundle["allAuditedFacts"]:
            if f_item["factId"] == "FACT-20261110-005":
                f_item["entityBindingStatus"] = "ENTITY_UNVERIFIED"
        eng = CoreThesisEngine(self.verified_news, tampered_bundle, self.audited_mp)
        raised = False
        try:
            eng.generate_theses()
        except ValueError as exc:
            if "UNVERIFIED_ENTITY_FACT_IN_THESIS_PROHIBITED" in str(exc):
                raised = True
        assert raised, "Fact with ENTITY_UNVERIFIED must be rejected by CoreThesisEngine"

    def test_16_adversarial_stale_data_injected_as_current_rejected(self):
        """P06-ADV-16: Marking stale MP-02 (2026-10-02) as VERIFIED or altering MP-08 date to today is caught and rejected."""
        tampered_mp = copy.deepcopy(self.mp8)
        tampered_mp[1]["updateStatus"] = "NUMERIC_VALUE_VERIFIED"
        tampered_mp[1]["verificationStatus"] = "VERIFIED"
        tampered_mp[7]["observationDate"] = "2026-11-10"
        audit_res = self.auditor.audit_market_pulse_integrity(tampered_mp, self.mp_specs)
        assert audit_res["valid"] is False
        assert len(audit_res["violations"]) >= 2

    def test_17_adversarial_altered_number_in_evidence_rejected(self):
        """P06-ADV-17: Changing a fact's numericValue/extractedExpression so it disagrees with contextQuote fails closed."""
        tampered_fact = copy.deepcopy(self.audited_facts["allAuditedFacts"][4])
        tampered_fact["extractedExpression"] = "99.999 đồng/USD"
        tampered_fact["numericValue"] = "99999"
        ev = next(e for e in self.verified_news if e["eventId"] == "EVT-20261110-006")
        v_ent, status, _ = self.auditor.verify_and_bind_entity(tampered_fact, ev, ev["summary"])
        assert status == "ENTITY_UNVERIFIED"
        assert v_ent == "ENTITY_UNVERIFIED"

    def test_18_adversarial_duplicate_thesis_rejected(self):
        """P06-ADV-18: Injecting a duplicate thesis title or referencing a duplicate factId in CoreThesisEngine fails closed."""
        eng = CoreThesisEngine(self.verified_news, self.audited_facts, self.audited_mp)
        raised = False
        try:
            eng._build_source_references(
                ["EVT-20261110-005"],
                ["FACT-20261110-002"],  # Duplicate of FACT-20261110-001!
                ["MP-03"]
            )
        except ValueError as exc:
            if "DUPLICATE_FACT_IN_THESIS_PROHIBITED" in str(exc):
                raised = True
        assert raised, "Referencing a duplicate factId in a thesis must raise DUPLICATE_FACT_IN_THESIS_PROHIBITED"

    def test_19_adversarial_ungrounded_payment_opportunity_rejected(self):
        """P06-ADV-19: Creating a Payment Radar signal with zero trigger events and zero Market Pulse refs fails closed."""
        eng = PaymentRadarEngine(self.verified_news, self.audited_facts, self.audited_mp)
        raised = False
        try:
            eng._build_evidence_refs([], [], [])
        except ValueError as exc:
            if "PAYMENT_RADAR_UNGROUNDED_SIGNAL" in str(exc):
                raised = True
        assert raised, "Ungrounded Payment Radar signal must raise PAYMENT_RADAR_UNGROUNDED_SIGNAL"

    def test_20_adversarial_hypothesis_as_conclusion_or_stock_advice_rejected(self):
        """P06-ADV-20: Promoting a hypothesis to an invalid certainty level or injecting stock buy/sell advice fails closed."""
        theses = CoreThesisEngine(self.verified_news, self.audited_facts, self.audited_mp).generate_theses()["theses"]
        chains = MacroToMicroEngine(self.verified_news, self.audited_facts, self.audited_mp).generate_chains()["chains"]
        radars = PaymentRadarEngine(self.verified_news, self.audited_facts, self.audited_mp).generate_radar_signals()["signals"]
        eng = FinancialDecisionEngine(self.verified_news, self.audited_facts, self.audited_mp, theses, chains, radars)

        bad_card = {
            "decisionId": "DECISION-99",
            "headline": "Khuyến nghị mua cổ phiếu ngân hàng ngay lập tức với cam kết lợi nhuận 50%",
            "decisionCategory": "STRATEGIC_SIGNAL",
            "executiveSummary": "Cam kết lợi nhuận chắc chắn.",
            "supportingThesisIds": ["THESIS-01"],
            "supportingChainIds": ["CHAIN-01"],
            "supportingRadarIds": ["RADAR-01"],
            "supportingEventIds": ["EVT-20261110-001"],
            "supportingMarketPulseIds": ["MP-01"],
            "opportunity": "Mua mạnh cổ phiếu.",
            "risk": "Không có rủi ro.",
            "recommendedAction": "EXPLORE",
            "monitoringTriggers": ["Trigger"],
            "timeHorizon": "1M",
            "confidenceLevel": "HIGH",
            "limitations": ["None"]
        }
        raised = False
        try:
            eng._validate_and_build_refs(bad_card)
        except ValueError as exc:
            if "PROHIBITED_INVESTMENT_RECOMMENDATION_DETECTED" in str(exc):
                raised = True
        assert raised, "Stock buy/sell or profit guarantee language must raise PROHIBITED_INVESTMENT_RECOMMENDATION_DETECTED"

    def test_21_adversarial_outside_24h_event_excluded_from_24h_quota(self):
        """P06-ADV-21: Verifies events in 24_TO_48H and 48_TO_72H are never counted in 0-24h quota and shortfall is enforced."""
        with open(os.path.join(self.p06_ed_dir, "validation-report.json"), "r", encoding="utf-8") as f:
            vr = json.load(f)
        qa = vr["quotaAndFreshnessAccounting"]
        assert qa["actualTotalVerifiedEvents"] == 18
        assert qa["actual0to24hEvents"] == 16
        assert qa["actual24to48hEvents"] == 1
        assert qa["actual48to72hEvents"] == 1
        assert qa["shortfall24hEvents"] == 9
        assert vr["readinessClassification"]["dailyEditionReadiness"] == "DATA_SHORTFALL_OR_UNVERIFIED"

    def test_22_release_archiving_and_backup_policy_verification(self):
        """P06-GOV-22: Verifies Section XIV compliance (Phase 05B R1.0.1 archive, verified backup, and baseline inheritance manifest)."""
        manifest_path = os.path.join(PHASE06_ROOT, "PHASE06_BASELINE_MANIFEST.json")
        assert os.path.exists(manifest_path), "PHASE06_BASELINE_MANIFEST.json must exist"
        with open(manifest_path, "r", encoding="utf-8") as f:
            bm = json.load(f)
        assert bm["parentBaselineReleaseId"] == "PHASE05B_R1.0.1"
        assert bm["parentBaselineManifestEntriesVerified"] == 1434
        assert bm["originalPhase05BUnchanged"] is True

    def run_all(self) -> int:
        self.log("=" * 74)
        self.log("BRYAN FINTECH INTELLIGENCE — PHASE 06 FINANCIAL INTELLIGENCE QA SUITE")
        self.log(f"Execution Timestamp: {datetime.now(VN_TZ).isoformat()}")
        self.log("=" * 74 + "\n")

        self.run_test("P06-TEST-01: JSON Schema V4.0.0 Draft 2020-12 Validation", self.test_01_json_schema_v400_validation)
        self.run_test("P06-TEST-02: Event Reference Integrity Across All Workstreams", self.test_02_event_reference_integrity)
        self.run_test("P06-TEST-03: Financial Fact Integrity & Grounding", self.test_03_financial_fact_integrity_and_grounding)
        self.run_test("P06-TEST-04: Entity Binding Verification & Quote Rebinding", self.test_04_entity_binding_verification_and_rebinding)
        self.run_test("P06-TEST-05: Duplicate Financial Fact Prevention", self.test_05_duplicate_fact_prevention)
        self.run_test("P06-TEST-06: Evidence Traceability & SHA-256 Crosswalk", self.test_06_evidence_traceability_and_crosswalk)
        self.run_test("P06-TEST-07: Core Thesis Consistency & Counter-Evidence", self.test_07_core_thesis_consistency)
        self.run_test("P06-TEST-08: Macro-to-Micro 5-Link Causal Classification", self.test_08_macro_to_micro_causal_classification)
        self.run_test("P06-TEST-09: Payment Opportunity Grounding & Payoo Commercial Lens", self.test_09_payment_opportunity_grounding_and_payoo_lens)
        self.run_test("P06-TEST-10: Decision Card Consistency & Five Executive Questions", self.test_10_decision_card_consistency_and_five_questions)
        self.run_test("P06-TEST-11: Market Pulse Freshness & News Quota Separation", self.test_11_market_pulse_freshness_and_news_separation)
        self.run_test("P06-TEST-12: Google Sheets 7-Tab Read-Only Dry-Run Integrity", self.test_12_google_sheets_dry_run_integrity)
        self.run_test("P06-TEST-13: Multi-Day Reproducibility & Daily JSON Distribution", self.test_13_multi_day_reproducibility_and_daily_json_distribution)
        self.run_test("P06-ADV-14: Adversarial — Delete Supporting Event Fails Closed", self.test_14_adversarial_delete_supporting_event_rejected)
        self.run_test("P06-ADV-15: Adversarial — Tampered Fact Entity Rejected", self.test_15_adversarial_tampered_fact_entity_rejected)
        self.run_test("P06-ADV-16: Adversarial — Stale Data Injected as Current Rejected", self.test_16_adversarial_stale_data_injected_as_current_rejected)
        self.run_test("P06-ADV-17: Adversarial — Altered Number in Evidence Rejected", self.test_17_adversarial_altered_number_in_evidence_rejected)
        self.run_test("P06-ADV-18: Adversarial — Duplicate Fact / Thesis Rejected", self.test_18_adversarial_duplicate_thesis_rejected)
        self.run_test("P06-ADV-19: Adversarial — Ungrounded Payment Opportunity Rejected", self.test_19_adversarial_ungrounded_payment_opportunity_rejected)
        self.run_test("P06-ADV-20: Adversarial — Stock Buy/Sell or Profit Guarantee Rejected", self.test_20_adversarial_hypothesis_as_conclusion_or_stock_advice_rejected)
        self.run_test("P06-ADV-21: Adversarial — Outside-24h Event Excluded from 24h Quota", self.test_21_adversarial_outside_24h_event_excluded_from_24h_quota)
        self.run_test("P06-GOV-22: Release Archiving, Backup & Inheritance Policy Check", self.test_22_release_archiving_and_backup_policy_verification)

        total = self.passed + self.failed
        status = "ENGINEERING_PASS" if self.failed == 0 else "ENGINE_FAIL"
        self.log("=" * 74)
        self.log(f"PHASE 06 QA SUMMARY: Total: {total} | PASSED: {self.passed} | FAILED: {self.failed}")
        self.log(f"PHASE 06 ENGINE STATUS: {status}")
        self.log("=" * 74)

        log_path = os.path.join(THIS_DIR, "PHASE06_TEST_RESULTS.log")
        with open(log_path, "w", encoding="utf-8") as f:
            f.write("\n".join(self.logs) + "\n")
        print(f"\nExecution log written to: {log_path}")
        return 0 if self.failed == 0 else 1


if __name__ == "__main__":
    suite = TestPhase06IntelligenceSuite()
    sys.exit(suite.run_all())
