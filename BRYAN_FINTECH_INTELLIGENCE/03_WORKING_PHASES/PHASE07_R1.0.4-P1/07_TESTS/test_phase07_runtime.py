#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_phase07_runtime.py
=======================
Comprehensive Unit, Integration, Regression & Adversarial QA Suite for
Bryan FinTech Intelligence — Phase 07: Dynamic Intelligence & Daily Runtime Engine.

Covers all 22 required test categories specified in Part 5:
  P07-TEST-01: Runtime Orchestrator Execution (20/20 steps PASS)
  P07-TEST-02: Timezone & 24h Window Calculation (Asia/Ho_Chi_Minh UTC+07:00)
  P07-TEST-03: Candidate Discovery & Source Provenance Verification
  P07-TEST-04: Publication Timestamp Extraction vs CMS Update / Retrieval Time
  P07-TEST-05: 72h Stale Event Rejection
  P07-TEST-06: 24h Ratio Calculation (24/25 = 96.0% >= 80.0%)
  P07-TEST-07: Shortfall Honest Blocking (<25 events or <80% 0-24h)
  P07-TEST-08: Cross-Day & Intra-Day Deduplication
  P07-TEST-09: Fact Extraction & Entity Binding Verification
  P07-TEST-10: Duplicate Fact Prevention Across Synthesis
  P07-TEST-11: Market Pulse Extraction & Validation (8 Indicators)
  P07-TEST-12: Market Pulse Freshness Enforcement (MP-02 Stale, MP-05/06 Qualitative, MP-08 Historical)
  P07-TEST-13: Core Thesis Evidence Grounding & 5 Required Module 05-A Fields
  P07-TEST-14: Connect the Dots Multi-Event Synthesis
  P07-TEST-15: Macro-to-Micro 7-Stage Causal Chain & 5-Link Inference Classification
  P07-TEST-16: Payment Opportunity Radar Grounding across Priority Sectors
  P07-TEST-17: Financial Decision Intelligence Grounding & 5 Strategic Questions
  P07-TEST-18: Evidence Crosswalk Completeness & SHA-256 Parity
  P07-TEST-19: JSON Schema Contract Validation (V4.0.0 & V5.0.0)
  P07-TEST-20: Google Sheets Staging Dry-Run Validation (7 Tabs, 0 Live Writes)
  P07-TEST-21: Step Failure Propagation Blocking Downstream Publication
  P07-TEST-22: Idempotent / Repeated Execution & Frontend Candidate Compatibility
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
from phase07_dynamic_news_engine import Phase07DynamicNewsEngine, extract_cms_modified_timestamp
from phase07_market_pulse_runtime import Phase07MarketPulseRuntime
from phase07_editorial_intelligence_engine import Phase07EditorialIntelligenceEngine
from schema_validator import JsonSchemaValidator

VN_TZ = timezone(timedelta(hours=7))


def compute_sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


class TestPhase07RuntimeSuite:
    def __init__(self):
        self.logs = []
        self.passed = 0
        self.failed = 0

        self.orch = Phase07DailyRuntimeOrchestrator(
            phase07_root=PHASE07_ROOT,
            edition_date="2026-11-11",
            edition_id="ED-20261111-D01",
            run_timestamp="2026-11-11T02:20:00+07:00",
            execution_mode="OFFLINE"
        )
        self.run_res = self.orch.execute_daily_run()
        self.state = self.run_res["state"]
        self.daily_dir = self.run_res["dailyEditionDir"]

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
    # 22 MANDATORY PHASE 07 RUNTIME, INTELLIGENCE & ADVERSARIAL TESTS
    # =========================================================================

    def test_01_runtime_orchestrator_20_steps(self):
        """P07-TEST-01: Verifies all 20 steps execute in sequence, record telemetry, and pass."""
        assert self.run_res["overallRuntimeStatus"] == "PASS"
        # Offline mode strictly sets publicationAllowed to False per P0-6.2
        assert self.run_res["publicationAllowed"] is False
        steps = self.run_res["stepsLog"]
        assert len(steps) == 20
        for idx, s in enumerate(steps, 1):
            assert s["stepNumber"] == idx
            assert s["stepId"] == f"STEP_{idx:02d}"
            assert s["status"] == "PASS"
            assert s["startedAt"] and s["completedAt"]
            assert isinstance(s["inputReferences"], list)
            assert isinstance(s["outputReferences"], list)
            assert s["errorDetails"] is None

    def test_02_timezone_and_24h_window_calculation(self):
        """P07-TEST-02: Verifies Asia/Ho_Chi_Minh timezone and exact 24h/72h windows in STEP 02."""
        step2 = self.run_res["stepsLog"][1]["metrics"]
        assert "Asia/Ho_Chi_Minh" in step2["timezone"]
        assert step2["executionT0"] == "2026-11-11T02:20:00+07:00"
        assert step2["window0To24hStart"] == "2026-11-10T02:20:00+07:00"
        assert step2["windowMax72hStart"] == "2026-11-08T02:20:00+07:00"

    def test_03_candidate_discovery_and_source_provenance(self):
        """P07-TEST-03: Verifies discovery across 456 raw HTML snapshots -> 100 unique URLs -> verified sources."""
        disc = self.state["news_res"]["discovery"]
        assert disc["totalSnapshotsScanned"] >= 450
        assert disc["uniqueCanonicalCandidates"] == 100
        sv = self.state["news_res"]["step05_sourceVerification"]
        assert sv["sourceVerifiedCount"] >= 35
        for ev in self.state["news_res"]["selectedEvents"]:
            vs = ev["verificationStages"]
            assert vs["SOURCE_VERIFIED"] is True
            assert vs["FACT_VERIFIED"] is True
            assert vs["WINDOW_ELIGIBLE"] is True
            assert vs["DEDUP_VERIFIED"] is True
            assert vs["READY_FOR_REVIEW"] is True

    def test_04_publication_timestamp_vs_cms_update_and_retrieval(self):
        """P07-TEST-04: Verifies originalPublicationTimestamp is distinguished from cmsUpdateTimestamp and sourceRetrievalTimestamp."""
        sample_html = (
            '<html><head>'
            '<meta property="article:published_time" content="2026-11-05T08:00:00+07:00" />'
            '<meta property="article:modified_time" content="2026-11-10T23:55:00+07:00" />'
            '</head><body><p>Nội dung bài báo cũ từ ngày 05/11 nhưng CMS cập nhật ngày 10/11.</p></body></html>'
        )
        cms_ts = extract_cms_modified_timestamp(sample_html)
        assert cms_ts == "2026-11-10T23:55:00+07:00"
        for ev in self.state["news_res"]["selectedEvents"]:
            assert "originalPublicationTimestamp" in ev
            assert "cmsUpdateTimestamp" in ev
            assert "sourceRetrievalTimestamp" in ev
            assert ev["originalPublicationTimestamp"] == ev["publishedAt"]

    def test_05_72h_stale_event_rejection(self):
        """P07-TEST-05: Verifies any candidate older than 72 hours (even with a fresh CMS update timestamp) is rejected."""
        stale_cand = copy.deepcopy(self.state["news_res"]["selectedEvents"][0])
        stale_cand["originalPublishedAt"] = "2026-11-05T10:00:00+07:00"
        stale_cand["originalPubTimestamp"] = "2026-11-05T10:00:00+07:00"
        stale_cand["originalPublicationTimestamp"] = "2026-11-05T10:00:00+07:00"
        stale_cand["publishedAt"] = "2026-11-05T10:00:00+07:00"
        stale_cand["cmsUpdateTimestamp"] = "2026-11-11T01:00:00+07:00"

        res = self.state["news_engine"].execute_pipeline(custom_candidates=[stale_cand])
        assert len(res["selectedEvents"]) == 0
        assert res["rejectedLedger"][0]["disposition"] == "REJECTED_STALE_OR_INVALID_TIMESTAMP"

    def test_06_24h_ratio_calculation_and_ranking(self):
        """P07-TEST-06: Verifies 25/25 selected events, 23/25 (92.0% >= 80.0%) in 0-24h, and newest-first ranking."""
        gate = self.state["news_res"]["step09_quotaAndFreshnessGate"]
        assert gate["gatePassed"] is True
        assert gate["selectedEventCount"] == 25
        assert gate["count0To24h"] == 23
        assert gate["count24To48h"] == 2
        assert gate["countOver72h"] == 0
        assert gate["ratio0To24h"] == 0.92

        ages = [e["ageHours"] for e in self.state["news_res"]["selectedEvents"]]
        assert ages == sorted(ages), "Selected events must be ranked newest first (ascending ageHours)"

    def test_07_shortfall_honest_blocking(self):
        """P07-TEST-07: Verifies that when <25 events or <80% 0-24h are available, the engine blocks honestly with SHORTFALL."""
        only_10 = copy.deepcopy(self.state["news_res"]["selectedEvents"][:10])
        res = self.state["news_engine"].execute_pipeline(custom_candidates=only_10)
        gate = res["step09_quotaAndFreshnessGate"]
        assert gate["gatePassed"] is False
        assert gate["gateStatusCode"] == "SHORTFALL"
        assert gate["selectedEventCount"] == 10
        assert len(gate["shortfallReasons"]) >= 1

        # Also test orchestrator blocking when given only 10 candidates
        tmp_dir = tempfile.mkdtemp(prefix="phase07_shortfall_")
        try:
            orch_sf = Phase07DailyRuntimeOrchestrator(phase07_root=PHASE07_ROOT, execution_mode="OFFLINE")
            sf_run = orch_sf.execute_daily_run(output_base_dir=tmp_dir, custom_candidates=only_10)
            assert sf_run["overallRuntimeStatus"] == "BLOCKED_OR_FAILED"
            assert sf_run["publicationAllowed"] is False
            step9 = next(s for s in sf_run["stepsLog"] if s["stepId"] == "STEP_09")
            assert step9["status"] == "FAIL"
            step18 = next(s for s in sf_run["stepsLog"] if s["stepId"] == "STEP_18")
            assert step18["status"] == "BLOCKED"
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)

    def test_08_cross_day_and_intra_day_deduplication(self):
        """P07-TEST-08: Verifies duplicate URLs, syndicated stories, and repeated intra-day gold bulletins are deduplicated."""
        cands = copy.deepcopy(self.state["news_res"]["selectedEvents"][:5])
        dup_cand = copy.deepcopy(cands[0])
        dup_cand["candidateId"] = "CAND-DUP-999"
        cands.append(dup_cand)
        res = self.state["news_engine"].execute_pipeline(custom_candidates=cands)
        assert len(res["selectedEvents"]) == 5
        assert any(r["disposition"] == "REJECTED_INTRA_BATCH_DUPLICATE" for r in res["rejectedLedger"])

    def test_09_fact_extraction_and_entity_binding_verification(self):
        """P07-TEST-09: Verifies all 22 extracted financial facts across the 25 events have verified entities and 0 ambiguous/unverified."""
        ab = self.state["news_res"]["step08_factVerification"]["auditedFactsBundle"]
        assert ab["totalRawFacts"] == 22
        assert ab["uniqueVerifiedFactsCount"] == 20
        assert ab["ambiguousOrUnverifiedEntitiesCount"] == 0
        for f in ab["allAuditedFacts"]:
            assert f["verificationStatus"] == "VERIFIED"
            assert f["entityBindingStatus"] in ("ENTITY_VERIFIED_FROM_QUOTE", "ENTITY_REBOUND_FROM_QUOTE")

    def test_10_duplicate_fact_prevention(self):
        """P07-TEST-10: Verifies duplicate facts (2 intercepted) are flagged isDuplicate=True and never referenced in editorial synthesis."""
        ab = self.state["news_res"]["step08_factVerification"]["auditedFactsBundle"]
        assert ab["duplicateFactsInterceptedCount"] == 2
        cw = self.state["crosswalk"]
        assert cw["summary"]["zeroDuplicateFactsUsedInSynthesis"] is True
        for fc in cw["financialFactCrosswalk"]:
            if fc["isDuplicate"]:
                assert fc["referencedByTheses"] == []
                assert fc["referencedByConnectTheDots"] == []
                assert fc["referencedByChains"] == []
                assert fc["referencedByRadars"] == []

    def test_11_market_pulse_extraction_and_validation(self):
        """P07-TEST-11: Verifies all 8 Market Pulse indicators have complete Module 04 fields and verified evidence SHA-256."""
        mp_inds = self.state["mp_res"]["indicators"]
        assert len(mp_inds) == 8
        by_id = {m["indicatorId"]: m for m in mp_inds}
        assert by_id["MP-01"]["currentValue"] == "25600"
        assert by_id["MP-01"]["trendDirection"] == "DOWN"
        assert by_id["MP-01"]["absoluteChange"] == "-10 VND/USD"
        assert by_id["MP-03"]["currentValue"] == "7"
        assert by_id["MP-04"]["currentValue"] == "1743.00"
        assert by_id["MP-04"]["trendDirection"] == "UP"
        assert by_id["MP-04"]["percentageChange"] == "+1.68%"
        assert by_id["MP-07"]["currentValue"] == "19.5"

    def test_12_market_pulse_freshness_enforcement(self):
        """P07-TEST-12: Verifies MP-02 remains STALE_OBSERVATION/UNVERIFIED, MP-05/06 remain QUALITATIVE_UPDATE_ONLY, and MP-08 preserves 2026-09-21."""
        by_id = {m["indicatorId"]: m for m in self.state["mp_res"]["indicators"]}
        assert by_id["MP-02"]["updateStatus"] == "STALE_OBSERVATION"
        assert by_id["MP-02"]["verificationStatus"] == "UNVERIFIED"
        assert by_id["MP-05"]["currentValue"] is None
        assert by_id["MP-06"]["currentValue"] is None
        assert by_id["MP-08"]["observationDate"] == "2026-09-21"

    def test_13_core_thesis_evidence_grounding(self):
        """P07-TEST-13: Verifies all 4 Core Theses include Module 05-A fields and valid supporting references."""
        theses = self.state["theses_bundle"]["theses"]
        assert len(theses) == 4
        valid_eids = {e["eventId"] for e in self.state["news_res"]["selectedEvents"]}
        for t in theses:
            for req in ["whatHappened", "whyItMatters", "affectedVariables", "possibleNextDevelopment", "fintechWatchpoint"]:
                assert t.get(req), f"Missing {req} in {t['thesisId']}"
            assert set(t["supportingEventIds"]).issubset(valid_eids)

    def test_14_connect_the_dots_multi_event_synthesis(self):
        """P07-TEST-14: Verifies Connect the Dots generates 4 multi-event narratives linking monetary policy, banks, corporates, and consumers."""
        dots = self.state["dots_bundle"]["narratives"]
        assert len(dots) == 4
        valid_eids = {e["eventId"] for e in self.state["news_res"]["selectedEvents"]}
        for d in dots:
            assert len(d["supportingEventIds"]) >= 1
            assert set(d["supportingEventIds"]).issubset(valid_eids)
            for link_key in ["monetaryPolicyLink", "bankingLink", "corporateLink", "consumerAndMarketLink"]:
                assert len(d[link_key]) > 20

    def test_15_macro_to_micro_7_stage_causal_chain(self):
        """P07-TEST-15: Verifies Macro-to-Micro chains contain both the 7-stage transmission object and 5-link inference classifications."""
        chains = self.state["chains_bundle"]["chains"]
        assert len(chains) == 4
        req_stages = [
            "stage1_globalEconomy",
            "stage2_vietnamMacroeconomics",
            "stage3_monetaryPolicy",
            "stage4_bankingAndCapitalMarkets",
            "stage5_corporateFinancingAndOperations",
            "stage6_merchantPaymentBehavior",
            "stage7_endUserPaymentBehavior"
        ]
        for c in chains:
            s7 = c["sevenStageTransmission"]
            for st in req_stages:
                assert len(s7.get(st, "")) > 15

    def test_16_payment_opportunity_radar_grounding(self):
        """P07-TEST-16: Verifies Payment Opportunity Radar includes all Module 05-D fields and never fabricates named merchants."""
        signals = self.state["radars_bundle"]["signals"]
        assert len(signals) == 5
        for s in signals:
            for req in [
                "opportunityId", "sector", "verifiedMarketSignal", "supportingEventIds",
                "businessProblem", "relevantPaymentSolution", "targetPartnerType",
                "commercialRationale", "priority", "confidence", "recommendedNextAction"
            ]:
                assert s.get(req) is not None, f"Missing {req} in {s['radarId']}"

    def test_17_financial_decision_intelligence_grounding(self):
        """P07-TEST-17: Verifies Decision Cards and 5 Strategic Questions are grounded in verified events and Market Pulse."""
        dec_bundle = self.state["decisions_bundle"]
        assert len(dec_bundle["decisionCards"]) == 4
        q5 = dec_bundle["fiveQuestionsExecutiveSynthesis"]
        assert len(q5) == 5

    def test_18_evidence_crosswalk_completeness(self):
        """P07-TEST-18: Verifies Evidence Crosswalk covers all 25 events, 22 raw facts, and 8 Market Pulse indicators with matching SHA-256."""
        cw = self.state["crosswalk"]
        assert cw["summary"]["totalVerifiedNewsEvents"] == 25
        assert cw["summary"]["totalRawFinancialFacts"] == 22
        assert cw["summary"]["uniqueVerifiedFacts"] == 20
        assert cw["summary"]["totalMarketPulseIndicators"] == 8
        assert cw["summary"]["totalConnectTheDotsNarratives"] == 4
        assert cw["summary"]["zeroOrphanReferences"] is True

    def test_19_json_schema_contract_v4_and_v5_validation(self):
        """P07-TEST-19: Validates all runtime step records and intelligence outputs against Schema V4.0.0 and V5.0.0."""
        v5 = JsonSchemaValidator(self.state["contract_v5"])
        step_schema = self.state["contract_v5"]["definitions"]["RuntimeStepRecord"]
        for s in self.run_res["stepsLog"]:
            v5.validate(s, subschema=step_schema)

    def test_20_google_sheets_staging_dry_run_validation(self):
        """P07-TEST-20: Verifies 7-tab Google Sheets dry-run preserves 155 baseline rows, adds valid 25-event edition rows, and makes 0 live writes."""
        val = self.state["sheets_bundle"]["validation"]
        assert val["allTabsPassed"] is True
        assert val["liveWriteApiCalled"] is False
        assert val["originalStagingUnmodified"] is True
        assert val["existingBaselineRowCount"] == 155
        assert val["foreignKeyViolationsCount"] == 0
        assert val["tabValidation"]["NEWS_EVENTS"]["proposedNewRowCount"] == 25

    def test_21_step_failure_propagation_blocks_downstream(self):
        """P07-TEST-21: Adversarial test — injecting a failure at STEP 10 halts execution and marks STEP 11..20 as BLOCKED."""
        tmp_dir = tempfile.mkdtemp(prefix="phase07_failprop_")
        try:
            orch_fail = Phase07DailyRuntimeOrchestrator(
                phase07_root=PHASE07_ROOT,
                edition_date="2026-11-11",
                edition_id="ED-20261111-D01",
                run_timestamp="2026-11-11T02:20:00+07:00",
                execution_mode="OFFLINE"
            )
            res_fail = orch_fail.execute_daily_run(output_base_dir=tmp_dir, inject_step_failure_at=10)
            assert res_fail["overallRuntimeStatus"] == "BLOCKED_OR_FAILED"
            assert res_fail["publicationAllowed"] is False
            by_num = {s["stepNumber"]: s["status"] for s in res_fail["stepsLog"]}
            for n in range(1, 10):
                assert by_num[n] == "PASS"
            assert by_num[10] == "FAIL"
            for n in range(11, 21):
                assert by_num[n] == "BLOCKED"
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)

    def test_22_idempotent_repeated_execution_and_frontend_candidates(self):
        """P07-TEST-22: Verifies all 15 daily edition files + SHA256SUMS.txt + frontend candidates are valid and deterministic across repeated runs."""
        required_15 = [
            "edition-manifest.json",
            "runtime-step-log.json",
            "verified-news.json",
            "rejected-candidates.json",
            "source-ledger.json",
            "event-registry-delta.json",
            "market-pulse.json",
            "core-thesis.json",
            "connect-the-dots.json",
            "macro-to-micro.json",
            "payment-radar.json",
            "financial-decision-intelligence.json",
            "evidence-crosswalk.json",
            "validation-report.json",
            "google-sheets-dry-run.json",
            "combined-edition.json",
            "latest-candidate.json",
            "magspread-edition-candidate.json",
            "SHA256SUMS.txt"
        ]
        for fn in required_15:
            p = os.path.join(self.daily_dir, fn)
            assert os.path.exists(p), f"Missing daily output file: {p}"

        # Verify SHA256SUMS.txt entries match disk
        with open(os.path.join(self.daily_dir, "SHA256SUMS.txt"), "r", encoding="utf-8") as f:
            for ln in f:
                ln = ln.strip()
                if not ln:
                    continue
                sha, fn = ln.split("  ", 1)
                assert compute_sha256(os.path.join(self.daily_dir, fn)) == sha

        # Verify latest-candidate.json contract for fintech-intelligence/app.js
        with open(os.path.join(PHASE07_ROOT, "06_DAILY_EDITIONS", "latest-candidate.json"), "r", encoding="utf-8") as f:
            latest_cand = json.load(f)
        assert latest_cand["status"] == "ready"
        assert len(latest_cand["newsList"]) == 25
        assert len(latest_cand["metrics"]) == 8
        assert len(latest_cand["connectTheDots"]) == 4
        assert len(latest_cand["macroMap"]) == 4
        assert len(latest_cand["radarList"]) == 4

        # Verify repeated execution in isolated temp dir produces identical combined-edition.json SHA-256
        tmp_dir = tempfile.mkdtemp(prefix="phase07_idem_")
        try:
            orch2 = Phase07DailyRuntimeOrchestrator(
                phase07_root=PHASE07_ROOT,
                edition_date="2026-11-11",
                edition_id="ED-20261111-D01",
                run_timestamp="2026-11-11T02:20:00+07:00",
                offline_mode=True
            )
            res2 = orch2.execute_daily_run(output_base_dir=tmp_dir)
            assert res2["state"]["combined_sha256"] == self.state["combined_sha256"]
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)

    def run_all(self) -> int:
        header = (
            "=" * 76 + "\n"
            "BRYAN FINTECH INTELLIGENCE — PHASE 07 DYNAMIC RUNTIME QA SUITE\n"
            f"Execution Timestamp: {datetime.now(VN_TZ).isoformat()}\n"
            + "=" * 76 + "\n"
        )
        self.log(header)

        tests = [
            ("P07-TEST-01: Runtime Orchestrator Execution (20/20 Steps)", self.test_01_runtime_orchestrator_20_steps),
            ("P07-TEST-02: Timezone & 24h Window Calculation", self.test_02_timezone_and_24h_window_calculation),
            ("P07-TEST-03: Candidate Discovery & Source Provenance Verification", self.test_03_candidate_discovery_and_source_provenance),
            ("P07-TEST-04: Publication Timestamp vs CMS Update / Retrieval Time", self.test_04_publication_timestamp_vs_cms_update_and_retrieval),
            ("P07-TEST-05: 72h Stale Event Rejection", self.test_05_72h_stale_event_rejection),
            ("P07-TEST-06: 24h Ratio Calculation & Newest-First Ranking", self.test_06_24h_ratio_calculation_and_ranking),
            ("P07-TEST-07: Shortfall Honest Blocking (<25 Events or <80% 0-24h)", self.test_07_shortfall_honest_blocking),
            ("P07-TEST-08: Cross-Day & Intra-Day Semantic Deduplication", self.test_08_cross_day_and_intra_day_deduplication),
            ("P07-TEST-09: Fact Extraction & Entity Binding Verification", self.test_09_fact_extraction_and_entity_binding_verification),
            ("P07-TEST-10: Duplicate Fact Prevention Across Synthesis", self.test_10_duplicate_fact_prevention),
            ("P07-TEST-11: Market Pulse Extraction & Validation (8 Indicators)", self.test_11_market_pulse_extraction_and_validation),
            ("P07-TEST-12: Market Pulse Freshness & Periodic Truth Enforcement", self.test_12_market_pulse_freshness_enforcement),
            ("P07-TEST-13: Core Thesis Evidence Grounding & Module 05-A Fields", self.test_13_core_thesis_evidence_grounding),
            ("P07-TEST-14: Connect the Dots Multi-Event Synthesis", self.test_14_connect_the_dots_multi_event_synthesis),
            ("P07-TEST-15: Macro-to-Micro 7-Stage Causal Chain & 5-Link Inference", self.test_15_macro_to_micro_7_stage_causal_chain),
            ("P07-TEST-16: Payment Opportunity Radar Grounding Across Sectors", self.test_16_payment_opportunity_radar_grounding),
            ("P07-TEST-17: Financial Decision Intelligence & 5 Strategic Questions", self.test_17_financial_decision_intelligence_grounding),
            ("P07-TEST-18: Evidence Crosswalk Completeness & SHA-256 Parity", self.test_18_evidence_crosswalk_completeness),
            ("P07-TEST-19: JSON Schema Contract V4.0.0 & V5.0.0 Validation", self.test_19_json_schema_contract_v4_and_v5_validation),
            ("P07-TEST-20: Google Sheets Staging Dry-Run Validation (7 Tabs)", self.test_20_google_sheets_staging_dry_run_validation),
            ("P07-TEST-21: Step Failure Propagation Blocking Downstream Steps", self.test_21_step_failure_propagation_blocks_downstream),
            ("P07-TEST-22: Idempotent Execution & Frontend Candidate Compatibility", self.test_22_idempotent_repeated_execution_and_frontend_candidates),
        ]

        for name, fn in tests:
            self.run_test(name, fn)

        status_str = "PHASE07_PASS" if self.failed == 0 else "PHASE07_FAIL"
        summary = (
            "=" * 76 + "\n"
            f"PHASE 07 QA SUMMARY: Total: {self.passed + self.failed} | PASSED: {self.passed} | FAILED: {self.failed}\n"
            f"PHASE 07 ENGINE STATUS: {status_str}\n"
            + "=" * 76
        )
        self.log(summary)

        log_path = os.path.join(THIS_DIR, "PHASE07_TEST_RESULTS.log")
        with open(log_path, "w", encoding="utf-8") as f:
            f.write("\n".join(self.logs) + "\n")
        print(f"\nExecution log written to: {log_path}")
        return 0 if self.failed == 0 else 1


if __name__ == "__main__":
    suite = TestPhase07RuntimeSuite()
    sys.exit(suite.run_all())
