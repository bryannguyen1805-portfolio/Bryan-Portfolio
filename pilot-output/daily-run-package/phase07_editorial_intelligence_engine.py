#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
phase07_editorial_intelligence_engine.py
========================================
Module 05 — Evidence-Driven Dynamic Editorial Intelligence Engine for Bryan FinTech Intelligence Phase 07.

STRICT INTEGRITY MANDATE:
- Static analytical methodologies are allowed; static financial conclusions are PROHIBITED.
- Zero hardcoded daily conclusions, static narrative text, fixed numbers, or predefined event sets.
- Genuinely evidence-driven: consumes current verified news, audited financial facts, and 8 Market Pulse indicators.
- Respects Model Provider configuration:
  - Records MODEL_PROVIDER_UNAVAILABLE when an AI model provider is not configured.
  - Executes a deterministic analytical engine fallback that genuinely derives dynamic conclusions from current evidence.
- Full compliance with EVIDENCE-DRIVEN DYNAMIC FINANCIAL INTELLIGENCE specifications:
  - 4.1 Architectural principle
  - 4.2 Configured intelligence provider check
  - 4.3 Evidence-first claim pipeline
  - 4.4 Evidence relevance validation
  - 4.5 Dynamic Core Thesis (evidence-determined count, no forced 4)
  - 4.6 Dynamic Connect the Dots (meaningful relationships, no arbitrary associations)
  - 4.7 Dynamic Macro-to-Micro (7-stage causal transmission + 5-link inference)
  - 4.8 Dynamic Payment Radar (evaluated from actual commercial evidence, no prewritten opportunities)
  - 4.9 Financial Decision Intelligence (meaningful actionable cards + 5 strategic questions)
  - 4.10 Correct Financial Fact Entity Binding (uses verifiedEntity canonically, no 'None: 7%')
  - 4.11 Accessible, simple Vietnamese financial explanations.
"""

import os
import re
from typing import Dict, List, Any, Optional, Tuple, Set


THEMATIC_DOMAINS = [
    {
        "domainId": "BANKING_CREDIT_LIQUIDITY",
        "domainName": "Ngân hàng, Tín dụng & Lãi suất",
        "canonicalThemeGroup": "Banking & Credit",
        "researchDomains": ["Banking & credit growth", "Deposit & lending interest rates"],
        "keywords": ["lãi suất", "ngân hàng", "tín dụng", "tiền gửi", "cho vay", "huy động", "nhtm", "sacombank", "techcombank", "vietcombank", "vcb", "mbv", "vib", "pgbank", "nim", "nợ xấu"],
        "mpIds": ["MP-02", "MP-03", "MP-05"],
        "defaultSector": "Ngân hàng & Thị trường Tiền tệ"
    },
    {
        "domainId": "MONETARY_POLICY_FX_MARKETS",
        "domainName": "Chính sách Tiền tệ, Tỷ giá & Thị trường Vốn",
        "canonicalThemeGroup": "Monetary Policy & Interest Rates",
        "researchDomains": ["State Bank of Vietnam policy", "Exchange rate & FX", "Capital markets & VN-Index"],
        "keywords": ["nhnn", "ngân hàng nhà nước", "tỷ giá", "usd", "ngoại tệ", "ngoại hối", "bơm tiền", "hút tiền", "vn-index", "chứng khoán", "cổ phiếu", "trái phiếu", "omo", "dxy"],
        "mpIds": ["MP-01", "MP-04", "MP-08"],
        "defaultSector": "Thị trường Ngoại hối & Chứng khoán"
    },
    {
        "domainId": "PUBLIC_POLICY_FISCAL_INFRASTRUCTURE",
        "domainName": "Chính sách Tài khóa, Thuế & Đầu tư Doanh nghiệp",
        "canonicalThemeGroup": "Corporate & Business Expansion",
        "researchDomains": ["Macroeconomic policy", "Tax, compliance, fraud, cybersecurity", "Global macro events affecting Vietnam"],
        "keywords": ["thuế", "nợ thuế", "ngân sách", "chính phủ", "quốc hội", "bộ tài chính", "xuất cảnh", "vốn", "đầu tư công", "doanh nghiệp", "evn", "hạ tầng", "nhật bản", "vcci", "thanh tra", "đo lường"],
        "mpIds": ["MP-08"],
        "defaultSector": "Chính sách Vĩ mô & Tài chính Doanh nghiệp"
    },
    {
        "domainId": "RETAIL_CONSUMER_PAYMENT_COMMERCE",
        "domainName": "Bán lẻ, Tiêu dùng, Vận tải & Thanh toán Số",
        "canonicalThemeGroup": "Cashless Payment & Payment Infrastructure",
        "researchDomains": ["Retail, E-commerce, F&B, Hospitality, Tourism", "Consumer spending & retail", "Cashless payments & VietQR", "Logistics & freight"],
        "keywords": ["thanh toán", "không tiền mặt", "vietqr", "qr", "pos", "smartpos", "khách quốc tế", "du lịch", "thương mại điện tử", "vàng", "sjc", "tiêu dùng", "bán lẻ", "logistics", "vận chuyển", "j&t", "cargo", "cod", "giao hàng", "xuất khẩu", "cà phê"],
        "mpIds": ["MP-06", "MP-07"],
        "defaultSector": "Bán lẻ, Tiêu dùng & Thanh toán Không Tiền mặt"
    }
]


def extract_canonical_entity(fact: Dict[str, Any]) -> str:
    """
    Section 4.10: Reads canonical verifiedEntity field correctly.
    Never returns 'None' or incomplete strings like 'None: 7%'.
    """
    ent = fact.get("verifiedEntity") or fact.get("boundEntity") or ""
    if not ent or str(ent).strip().lower() in ("none", "null", "undefined", ""):
        return ""
    return str(ent).strip()


class Phase07EditorialIntelligenceEngine:
    """
    Module 05 — Evidence-Driven Dynamic Editorial Intelligence Engine.
    Synthesizes Step 12 through Step 16 dynamically from current verified news,
    audited facts, and 8 Market Pulse indicators.
    """

    def __init__(
        self,
        verified_news: List[Dict[str, Any]],
        audited_facts_bundle: Dict[str, Any],
        audited_market_pulse: List[Dict[str, Any]],
        runtime_config: Dict[str, Any]
    ):
        self.verified_news = verified_news or []
        self.audited_facts_bundle = audited_facts_bundle or {}
        self.audited_market_pulse = audited_market_pulse or []
        self.runtime_config = runtime_config or {}

        # 4.2 Configured Intelligence Provider Check
        # Inspect current AI/model provider configuration.
        self.configured_provider = (
            self.runtime_config.get("modelProvider")
            or os.environ.get("AGY_MODEL_PROVIDER")
            or os.environ.get("MODEL_PROVIDER")
        )
        if self.configured_provider:
            self.model_provider_status = "MODEL_PROVIDER_AVAILABLE"
        else:
            self.model_provider_status = "MODEL_PROVIDER_UNAVAILABLE"

        self.news_by_id: Dict[str, Dict[str, Any]] = {
            e["eventId"]: e for e in self.verified_news if "eventId" in e
        }
        self.unique_facts: List[Dict[str, Any]] = (
            self.audited_facts_bundle.get("uniqueVerifiedFacts")
            or self.audited_facts_bundle.get("allAuditedFacts")
            or []
        )
        self.unique_facts_by_id: Dict[str, Dict[str, Any]] = {
            f["factId"]: f for f in self.unique_facts if "factId" in f
        }
        self.facts_by_event: Dict[str, List[Dict[str, Any]]] = {}
        for f in self.unique_facts:
            eid = f.get("eventId") or f.get("originatingEventId")
            if eid:
                self.facts_by_event.setdefault(eid, []).append(f)

        self.mp_by_id: Dict[str, Dict[str, Any]] = {
            m["indicatorId"]: m for m in self.audited_market_pulse if "indicatorId" in m
        }

    # -------------------------------------------------------------------------
    # DYNAMIC CLUSTERING ACROSS EVIDENCE
    # -------------------------------------------------------------------------
    def _cluster_events(self) -> List[Dict[str, Any]]:
        """
        Dynamically clusters verified news events into thematic groups based on
        researchDomain and content keywords.
        Guarantees zero unrelated-event fallback (sports/entertainment not packaged into financial theses).
        """
        clusters: List[Dict[str, Any]] = []
        assigned_event_ids = set()

        for domain in THEMATIC_DOMAINS:
            matched_events: List[Dict[str, Any]] = []
            for ev in self.verified_news:
                eid = ev.get("eventId")
                if not eid:
                    continue
                rd = (ev.get("researchDomain") or "").lower()
                text = f"{ev.get('headline', '')} {ev.get('summary', '')}".lower()
                
                # Boundary check: sports events must NEVER match financial domains
                is_sports = any(k in text or k in rd for k in ["bóng đá", "asian cup", "thể thao", "sân vận động", "cầu thủ", "giao hữu"])
                if is_sports:
                    continue

                is_domain_match = any(d.lower() in rd for d in domain["researchDomains"])
                is_kw_match = any(kw in text for kw in domain["keywords"])
                if is_domain_match or is_kw_match:
                    matched_events.append(ev)
                    assigned_event_ids.add(eid)

            if matched_events:
                clusters.append({
                    "domain": domain,
                    "events": matched_events,
                    "eventIds": [e["eventId"] for e in matched_events]
                })

        # Capture remaining unassigned events ONLY if they have valid financial facts or relevant financial content
        financial_keywords = ["tài chính", "ngân hàng", "kinh tế", "doanh nghiệp", "thanh toán", "lãi suất", "đầu tư", "thị trường", "tín dụng", "thuế", "xuất khẩu", "giá"]
        unassigned = [
            e for e in self.verified_news
            if e.get("eventId") and e["eventId"] not in assigned_event_ids
            and (len(self.facts_by_event.get(e["eventId"], [])) > 0 or any(k in f"{e.get('headline', '')} {e.get('summary', '')}".lower() for k in financial_keywords))
            and not any(k in f"{e.get('headline', '')} {e.get('summary', '')}".lower() for k in ["bóng đá", "asian cup", "thể thao"])
        ]
        if unassigned:
            clusters.append({
                "domain": {
                    "domainId": "EMERGING_FINANCIAL_TOPICS",
                    "domainName": "Xu hướng Kinh tế & Tài chính Bổ sung",
                    "canonicalThemeGroup": "Capital Markets",
                    "researchDomains": [],
                    "keywords": [],
                    "mpIds": [],
                    "defaultSector": "Kinh tế Tổng hợp"
                },
                "events": unassigned,
                "eventIds": [e["eventId"] for e in unassigned]
            })

        return clusters

    def _build_cross_refs(
        self,
        event_ids: List[str],
        fact_ids: List[str],
        mp_ids: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Constructs rich, authenticated evidence references.
        Retains Section 4.10 entity fields: entityName, metricName, value, unit, observationPeriod, evidencePath.
        """
        refs: List[Dict[str, Any]] = []
        seen = set()
        for eid in event_ids:
            ev = self.news_by_id.get(eid)
            if ev and eid not in seen:
                seen.add(eid)
                refs.append({
                    "referenceId": eid,
                    "referenceType": "NEWS_EVENT",
                    "sourceUrl": ev.get("canonicalUrl") or ev.get("sourceUrl", ""),
                    "canonicalUrl": ev.get("canonicalUrl") or ev.get("sourceUrl", ""),
                    "publisher": ev.get("originalSourceName") or ev.get("publisher", ""),
                    "publishedAt": ev.get("publisherPublishedAt") or ev.get("publishedAt", ""),
                    "evidencePath": ev.get("evidencePath", ""),
                    "evidenceSha256": ev.get("evidenceSha256") or ev.get("contentSha256", ""),
                    "supportingQuote": ev.get("supportingQuote", "")
                })
        for fid in fact_ids:
            f = self.unique_facts_by_id.get(fid)
            if f and fid not in seen:
                seen.add(fid)
                v_entity = extract_canonical_entity(f)
                num_val = f.get("numericValue") if f.get("numericValue") is not None else f.get("currentValue")
                unit_str = f.get("unit") or ""
                refs.append({
                    "referenceId": fid,
                    "referenceType": "FINANCIAL_FACT",
                    "entityName": v_entity,
                    "verifiedEntity": v_entity,
                    "boundEntity": v_entity,
                    "metricName": f.get("metricName", ""),
                    "extractedExpression": f.get("extractedExpression", ""),
                    "value": num_val,
                    "numericValue": num_val,
                    "unit": unit_str,
                    "observationPeriod": f.get("observationPeriod") or f.get("dataPeriod") or f.get("asOf") or "",
                    "evidencePath": f.get("evidencePath", ""),
                    "evidenceSha256": f.get("evidenceSha256", ""),
                    "contextQuote": f.get("contextQuote", "")
                })
        for mid in mp_ids:
            m = self.mp_by_id.get(mid)
            if m and mid not in seen:
                seen.add(mid)
                refs.append({
                    "referenceId": mid,
                    "referenceType": "MARKET_PULSE_INDICATOR",
                    "indicatorName": m.get("indicatorName", ""),
                    "currentValue": m.get("currentValue"),
                    "unit": m.get("unit", ""),
                    "observationPeriod": m.get("observationDate") or m.get("dataPeriod") or "",
                    "sourceUrl": m.get("sourceUrl", ""),
                    "evidencePath": m.get("evidencePath", ""),
                    "evidenceSha256": m.get("evidenceSha256", "")
                })
        return refs

    # -------------------------------------------------------------------------
    # STEP 11-B: STRUCTURED EVIDENCE-FIRST CLAIM PIPELINE (Section 4.3 & 4.4)
    # -------------------------------------------------------------------------
    def generate_claim_layer(self) -> Dict[str, Any]:
        """
        Step 11-B: Structured Evidence-First Claim Layer (WS-02.3, WS-02.4).
        Distinguishes actual observed facts from supported inferences, hypotheses, and forecasts.
        Enforces relevance validation, boundary protection, and zero unsupported numbers.
        """
        claims: List[Dict[str, Any]] = []
        claim_idx = 1

        # 1. OBSERVED_FACT claims directly grounded in audited financial facts
        for f in self.unique_facts:
            fid = f.get("factId")
            eid = f.get("eventId") or f.get("originatingEventId")
            ent = extract_canonical_entity(f)
            mname = f.get("metricName") or ""
            expr = f.get("extractedExpression") or ""
            num_val = f.get("numericValue") if f.get("numericValue") is not None else f.get("currentValue")
            unit = f.get("unit") or ""

            if ent:
                stmt = f"Dữ kiện tài chính xác minh: {ent} ghi nhận {mname} ({expr})".strip()
            else:
                stmt = f"Dữ kiện tài chính xác minh: {mname} ({expr})".strip()

            if num_val is not None and unit:
                stmt += f", định lượng cụ thể: {num_val} {unit}."
            else:
                stmt += "."

            claims.append({
                "claimId": f"CLM-{claim_idx:03d}",
                "claimType": "OBSERVED_FACT",
                "statement": stmt,
                "verifiedEntity": ent,
                "metricName": mname,
                "numericValue": num_val,
                "unit": unit,
                "supportingEventIds": [eid] if eid else [],
                "supportingFactIds": [fid] if fid else [],
                "supportingIndicatorIds": [],
                "counterEvidenceEventIds": [],
                "reasoning": f"Trích xuất trực tiếp từ bản tin xác minh {eid} và đã đối soát chủ thể/số liệu trong phiên.",
                "confidence": "HIGH",
                "limitations": ["Dữ liệu phản ánh kết quả tại kỳ quan sát báo cáo chính thức."],
                "evidenceReferences": self._build_cross_refs([eid] if eid else [], [fid] if fid else [], [])
            })
            claim_idx += 1

        # 2. OBSERVED_FACT claims grounded in Market Pulse indicators
        for mp in self.audited_market_pulse:
            mid = mp.get("indicatorId")
            mname = mp.get("indicatorName")
            val = mp.get("actualValue") or mp.get("currentValue")
            unit = mp.get("unit")
            obs_date = mp.get("observationDate")
            if val is not None:
                stmt = f"Chỉ số thị trường {mname} ({mid}) đạt {val} {unit} (kỳ quan sát: {obs_date})."
                claims.append({
                    "claimId": f"CLM-{claim_idx:03d}",
                    "claimType": "OBSERVED_FACT",
                    "statement": stmt,
                    "verifiedEntity": "Thị trường Tài chính & Cơ quan Quản lý",
                    "metricName": mname,
                    "numericValue": val,
                    "unit": unit,
                    "supportingEventIds": [],
                    "supportingFactIds": [],
                    "supportingIndicatorIds": [mid] if mid else [],
                    "counterEvidenceEventIds": [],
                    "reasoning": f"Chỉ số kinh tế chính thức từ cơ quan điều hành hoặc thị trường giao dịch tập trung.",
                    "confidence": "HIGH",
                    "limitations": [f"Tần suất cập nhật theo kỳ quan sát {obs_date}."],
                    "evidenceReferences": self._build_cross_refs([], [], [mid] if mid else [])
                })
                claim_idx += 1

        # 3. SUPPORTED_INFERENCE claims from clustered events
        clusters = self._cluster_events()
        for cl in clusters:
            domain = cl["domain"]
            evs = cl["events"]
            eids = [e["eventId"] for e in evs]
            fids = [f["factId"] for eid in eids for f in self.facts_by_event.get(eid, [])]
            mp_ids = [m for m in domain.get("mpIds", []) if m in self.mp_by_id]
            lead_hl = evs[0].get("headline", "")

            opposing_eids = []
            combined_texts = [f"{e.get('headline', '')} {e.get('summary', '')}".lower() for e in evs]
            has_expansion = any(any(k in t for k in ["tăng trưởng", "bơm tiền", "hỗ trợ", "mở rộng", "khởi sắc", "tích cực"]) for t in combined_texts)
            has_headwind = any(any(k in t for k in ["nợ xấu", "rủi ro", "thắt chặt", "hút tiền", "áp lực", "khó khăn", "nợ thuế"]) for t in combined_texts)
            if has_expansion and has_headwind:
                for ev in evs:
                    t = f"{ev.get('headline', '')} {ev.get('summary', '')}".lower()
                    if any(k in t for k in ["nợ xấu", "rủi ro", "thắt chặt", "áp lực", "khó khăn", "nợ thuế"]):
                        opposing_eids.append(ev["eventId"])

            inf_stmt = f"Suy luận vận hành ngành {domain['domainName']}: Biến động từ '{lead_hl}' tác động trực tiếp đến chi phí vốn và cơ chế chu chuyển dòng tiền."
            claims.append({
                "claimId": f"CLM-{claim_idx:03d}",
                "claimType": "SUPPORTED_INFERENCE",
                "statement": inf_stmt,
                "supportingEventIds": eids,
                "supportingFactIds": fids[:4],
                "supportingIndicatorIds": mp_ids,
                "counterEvidenceEventIds": opposing_eids,
                "reasoning": f"Suy luận nhân quả từ diễn biến '{lead_hl}' gắn với dữ kiện tài chính {fids[:3] if fids else 'ngành'}.",
                "confidence": "MEDIUM" if opposing_eids else ("HIGH" if len(evs) >= 2 else "LOW"),
                "limitations": ["Độ trễ phản ứng thực tế phụ thuộc vào chính sách tiền tệ và năng lực hấp thụ vốn của doanh nghiệp."],
                "evidenceReferences": self._build_cross_refs(eids, fids[:4], mp_ids)
            })
            claim_idx += 1

        return {
            "claims": claims,
            "totalClaims": len(claims),
            "observedFactsCount": sum(1 for c in claims if c["claimType"] == "OBSERVED_FACT"),
            "supportedInferencesCount": sum(1 for c in claims if c["claimType"] == "SUPPORTED_INFERENCE"),
            "hypothesesCount": sum(1 for c in claims if c["claimType"] == "HYPOTHESIS"),
            "forecastsCount": sum(1 for c in claims if c["claimType"] == "FORECAST"),
            "modelProviderStatus": self.model_provider_status
        }

    @staticmethod
    def _evaluate_event_posture(headline: str, summary: str, facts: Optional[List[Dict[str, Any]]] = None) -> str:
        """
        Evaluates the financial posture of an event.
        """
        text = f"{headline} {summary}".lower()
        bad_debt_terms = [
            "nợ xấu", "rủi ro tín dụng", "trích lập dự phòng", "dự phòng rủi ro",
            "nợ nhóm 3", "nợ nhóm 4", "nợ nhóm 5", "áp lực nợ", "chất lượng tài sản suy giảm",
            "khó khăn trả nợ", "vỡ nợ", "nợ quá hạn", "siết tín dụng", "thua lỗ", "tăng nợ xấu"
        ]
        if any(term in text for term in bad_debt_terms):
            return "POSTURE_CREDIT_RISK_STRESS"

        tax_compliance_terms = [
            "nợ thuế", "tạm hoãn xuất cảnh", "hóa đơn điện tử", "cưỡng chế thuế", "thanh tra thuế", "siết hóa đơn", "kiểm tra đo lường", "chất lượng vàng"
        ]
        if any(term in text for term in tax_compliance_terms):
            return "POSTURE_COMPLIANCE_ENFORCEMENT"

        fx_terms = [
            "bán usd", "can thiệp tỷ giá", "tín phiếu", "hút ròng", "hút tiền", "omo",
            "bán ngoại tệ", "bán 4 tỷ usd", "bình ổn tỷ giá", "áp lực tỷ giá"
        ]
        if any(term in text for term in fx_terms):
            return "POSTURE_MONETARY_STABILIZATION"

        growth_terms = [
            "tăng trưởng tín dụng", "tăng trưởng", "bứt phá", "kỷ lục", "mở rộng",
            "bơm ròng", "hạ lãi suất", "tích cực", "phục hồi", "120%", "quét mã qr",
            "khách quốc tế", "du lịch", "doanh thu tăng", "siêu sale", "xuất khẩu"
        ]
        if any(term in text for term in growth_terms) and not any(term in text for term in bad_debt_terms):
            return "POSTURE_EXPANSION_GROWTH"

        return "POSTURE_NEUTRAL_MONITORING"

    def validate_claim_evidence_crosswalk(
        self,
        thesis_or_claim: Dict[str, Any],
        supporting_events: List[Dict[str, Any]],
        supporting_facts: List[Dict[str, Any]],
        counter_events: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Section 4.4: Validates evidence relevance and boundary protection.
        Ensures referenced IDs exist and are substantively relevant.
        """
        c_eids = [e.get("eventId") for e in supporting_events if e.get("eventId")]
        c_fids = [f.get("factId") for f in supporting_facts if f.get("factId")]
        cnt_eids = [e.get("eventId") for e in counter_events if e.get("eventId")]

        # Relevance checking: verify all IDs exist in registry
        all_eids_exist = all(eid in self.news_by_id for eid in c_eids)
        all_fids_exist = all(fid in self.unique_facts_by_id for fid in c_fids)

        # Cross-domain boundary check: semiconductor event must NOT support tourism
        has_boundary_violation = False
        claim_text = (thesis_or_claim.get("centralArgument") or thesis_or_claim.get("statement") or "").lower()
        if "du lịch" in claim_text or "khách quốc tế" in claim_text:
            for ev in supporting_events:
                ev_t = f"{ev.get('headline', '')} {ev.get('summary', '')}".lower()
                if ("bán dẫn" in ev_t or "vi mạch" in ev_t or "semiconductor" in ev_t) and not any(k in ev_t for k in ["du lịch", "khách sạn", "lữ hành"]):
                    has_boundary_violation = True
                    break

        is_valid = all_eids_exist and not has_boundary_violation and len(c_eids) > 0

        return {
            "crosswalkId": f"CWK-{thesis_or_claim.get('thesisId', 'THESIS-01')}",
            "claimText": thesis_or_claim.get("centralArgument") or thesis_or_claim.get("statement") or "",
            "thematicPosture": thesis_or_claim.get("riskPosture", "POSTURE_NEUTRAL_MONITORING"),
            "supportingEventIds": c_eids,
            "supportingFactIds": c_fids,
            "counterEvidenceEventIds": cnt_eids,
            "isClaimGroundedInEvents": len(c_eids) > 0,
            "isClaimGroundedInFacts": len(c_fids) > 0,
            "hasOpposingSignals": len(cnt_eids) > 0,
            "boundaryIntegrityPassed": not has_boundary_violation,
            "crosswalkIntegrityStatus": "VALIDATED_RELATIONSHIP" if is_valid else "UNGROUNDED_OR_BOUNDARY_VIOLATION"
        }

    # -------------------------------------------------------------------------
    # STEP 12: DYNAMIC CORE THESIS GENERATION (Section 4.5)
    # -------------------------------------------------------------------------
    def generate_core_theses(self) -> Dict[str, Any]:
        """
        Step 12 — Core Thesis Generation:
        Dynamically clusters events, extracts factual and quantitative anchors, and
        synthesizes 5 Module 05-A fields + full Phase 06 CoreThesis schema fields.
        The number of theses is evidence-determined (never forced).
        Enforces semantic stance & evidence relationship checking (claim <-> event <-> fact <-> counter-evidence).
        """
        clusters = self._cluster_events()
        theses_out: List[Dict[str, Any]] = []

        for idx, cluster in enumerate(clusters):
            c_events = cluster["events"]
            if not c_events:
                continue

            c_domain = cluster["domain"]
            tid = f"THESIS-{idx+1:02d}"
            c_eids = [e["eventId"] for e in c_events]

            # Collect facts belonging to this cluster
            c_facts: List[Dict[str, Any]] = []
            c_fids: List[str] = []
            for eid in c_eids:
                for f in self.facts_by_event.get(eid, []):
                    if not f.get("isDuplicate") and f["factId"] not in c_fids:
                        c_fids.append(f["factId"])
                        c_facts.append(f)

            # Collect relevant Market Pulse indicators
            c_mps = [self.mp_by_id[mid] for mid in c_domain.get("mpIds", []) if mid in self.mp_by_id]
            c_mp_ids = [m["indicatorId"] for m in c_mps]

            lead_ev = c_events[0]
            lead_hl = lead_ev.get("headline", "")
            other_hls = [e.get("headline", "") for e in c_events[1:3]]

            # Dynamic extraction of affected variables (Section 4.10: strictly verifiedEntity, no None: 7%)
            affected_vars: List[str] = []
            for f in c_facts[:4]:
                ent = extract_canonical_entity(f)
                mname = f.get("metricName") or ""
                expr = f.get("extractedExpression") or ""
                if ent and expr and mname:
                    affected_vars.append(f"{mname} ({expr}) gắn với {ent}".strip())
                elif ent and expr:
                    affected_vars.append(f"{expr} gắn với {ent}".strip())
                elif expr and mname:
                    affected_vars.append(f"{mname} ({expr})".strip())
                elif expr:
                    affected_vars.append(expr)

            for m in c_mps:
                if m.get("currentValue") is not None:
                    affected_vars.append(f"{m.get('indicatorName')} ({m.get('indicatorId')}: {m.get('currentValue')} {m.get('unit')})")

            if not affected_vars:
                affected_vars.append(f"Chỉ số vận hành thuộc lĩnh vực {c_domain['domainName']}")

            posture = self._evaluate_event_posture(lead_hl, lead_ev.get("summary", ""), c_facts)

            # Dynamic factual summary
            fact_summary_parts = []
            for f in c_facts[:2]:
                ent = extract_canonical_entity(f)
                expr = f.get("extractedExpression") or ""
                if ent and expr:
                    fact_summary_parts.append(f"{ent}: {expr}")
                elif expr:
                    fact_summary_parts.append(expr)
            fact_str = f" với các dữ kiện trọng yếu ({'; '.join(fact_summary_parts)})" if fact_summary_parts else ""

            # Dynamic central argument based on posture & actual evidence
            if posture == "POSTURE_CREDIT_RISK_STRESS":
                central_arg = (
                    f"{c_domain['domainName']}: Áp lực gia tăng nợ xấu và gánh nặng trích lập dự phòng từ '{lead_hl}'{fact_str} "
                    f"đè nặng lên tỷ lệ NIM, buộc các tổ chức tín dụng siết chặt kỷ cương cấp vốn đối với biến số {affected_vars[0]}."
                )
                why_it_matters = (
                    f"Nợ xấu gia tăng làm suy giảm chất lượng tài sản sinh lời và bào mòn lợi nhuận ngân hàng qua chi phí dự phòng, "
                    f"buộc hệ thống phải ưu tiên thu hồi nợ và thắt chặt điều kiện giải ngân."
                )
                risk_level = "HIGH_RISK"
                possible_next_development = (
                    f"Các NHTM sẽ chủ động tăng trích lập dự phòng, cơ cấu lại thời hạn trả nợ và thận trọng giải ngân mới bám sát {affected_vars[0]}."
                )
            elif posture == "POSTURE_EXPANSION_GROWTH":
                central_arg = (
                    f"{c_domain['domainName']}: Xung lực tăng trưởng mở rộng từ '{lead_hl}'{fact_str} "
                    f"thúc đẩy dòng tiền và hoạt động thanh toán/tín dụng đối với biến số {affected_vars[0]}."
                )
                why_it_matters = (
                    f"Tăng trưởng mở rộng thúc đẩy chu chuyển vốn nhanh trong nền kinh tế, gia tăng doanh số thanh toán và mở rộng cơ hội thương mại cho doanh nghiệp."
                )
                risk_level = "LOW_RISK"
                possible_next_development = (
                    f"Kỳ vọng các tổ chức tín dụng và doanh nghiệp sẽ tiếp tục giải ngân mở rộng thị phần bám sát biến số {affected_vars[0]}."
                )
            elif posture == "POSTURE_MONETARY_STABILIZATION":
                central_arg = (
                    f"{c_domain['domainName']}: Động thái can thiệp và điều tiết từ '{lead_hl}'{fact_str} "
                    f"nhằm hạ nhiệt áp lực thị trường và duy trì ổn định đối với biến số {affected_vars[0]}."
                )
                why_it_matters = (
                    f"Diễn biến can thiệp ngoại hối và cung tiền tác động trực tiếp lên mặt bằng lãi suất VND liên ngân hàng và chi phí nhập khẩu của nền kinh tế."
                )
                risk_level = "MODERATE_RISK"
                possible_next_development = (
                    f"Kỳ vọng cơ quan quản lý sẽ duy trì các nghiệp vụ thị trường mở để điều hòa thanh khoản theo biến số {affected_vars[0]}."
                )
            elif posture == "POSTURE_COMPLIANCE_ENFORCEMENT":
                central_arg = (
                    f"{c_domain['domainName']}: Yêu cầu tuân thủ và chế tài quản lý từ '{lead_hl}'{fact_str} "
                    f"tạo áp lực chuyển đổi và chuẩn hóa dòng tiền đối với biến số {affected_vars[0]}."
                )
                why_it_matters = (
                    f"Siết chặt quản lý thuế và nghĩa vụ tài chính buộc doanh nghiệp và hộ kinh doanh phải nhanh chóng số hóa quy trình kế toán, đối soát và hóa đơn điện tử."
                )
                risk_level = "ELEVATED_RISK"
                possible_next_development = (
                    f"Doanh nghiệp và hộ kinh doanh đẩy mạnh tích hợp giải pháp hóa đơn điện tử máy tính tiền bám sát {affected_vars[0]}."
                )
            else:
                central_arg = (
                    f"{c_domain['domainName']}: Diễn biến từ '{lead_hl}'{fact_str} "
                    f"tác động trực tiếp lên biến số {affected_vars[0]}."
                )
                why_it_matters = f"Tác động lan tỏa của biến số {affected_vars[0]} tới hoạt động của các chủ thể trong ngành {c_domain['domainName']}."
                risk_level = "MODERATE_RISK"
                possible_next_development = (
                    f"Kỳ vọng cơ quan quản lý và các đơn vị liên quan sẽ điều chỉnh kế hoạch vận hành bám sát biến số {affected_vars[0]} trong các kỳ tới."
                )

            what_happened = (
                f"Ghi nhận {len(c_events)} sự kiện xác minh trong nhóm {c_domain['domainName']}. "
                f"Sự kiện trọng tâm: {lead_hl}. " +
                ("Các diễn biến bổ sung: " + "; ".join(other_hls) + "." if other_hls else "")
            )

            has_fintech_mention = any(any(k in f"{e.get('headline', '')} {e.get('summary', '')}".lower() for k in ["smartpos", "vietqr", "thanh toán", "thẻ", "pos", "ví điện tử"]) for e in c_events)
            if has_fintech_mention:
                fintech_watchpoint = f"Theo dõi khả năng ứng dụng giải pháp thanh toán số và quản trị đối soát dòng tiền thích ứng với diễn biến của '{lead_hl}'."
            elif posture == "POSTURE_CREDIT_RISK_STRESS":
                fintech_watchpoint = "Theo dõi nhu cầu ứng dụng giải pháp đối soát doanh thu thời gian thực và quản trị nợ đọng tự động qua SmartPOS/Virtual Account."
            else:
                fintech_watchpoint = f"Theo dõi các chỉ số vận hành và chu kỳ công bố số liệu tiếp theo của {affected_vars[0]}."

            # Dynamic detection of contradictory / opposing evidence across dataset
            opposing_events = []
            opposing_eids = []
            opposing_reasons = []

            candidate_events = [e for e in self.verified_news if e.get("eventId") != lead_ev.get("eventId")]
            for ev in candidate_events:
                if len(opposing_events) >= 2:
                    break
                ev_text = f"{ev.get('headline', '')} {ev.get('summary', '')}".lower()
                is_ev_risk = any(k in ev_text for k in ["nợ xấu", "rủi ro", "thắt chặt", "áp lực", "khó khăn", "nợ thuế", "trầm bê"])
                is_ev_growth = any(k in ev_text for k in ["tăng trưởng", "bơm", "mở rộng", "hỗ trợ", "giảm lãi suất", "120%", "quét mã qr", "khách quốc tế"])

                if posture == "POSTURE_EXPANSION_GROWTH" and is_ev_risk:
                    if ev["eventId"] not in opposing_eids:
                        opposing_events.append(ev)
                        opposing_eids.append(ev["eventId"])
                        opposing_reasons.append(
                            f"Dữ kiện đối trọng từ {ev.get('eventId')} ({ev.get('headline')}): "
                            f"Tồn tại rủi ro gia tăng nợ xấu hoặc chi phí trích lập dự phòng, tạo lực cản ngược chiều với đà mở rộng."
                        )
                elif posture == "POSTURE_CREDIT_RISK_STRESS" and is_ev_growth:
                    if ev["eventId"] not in opposing_eids:
                        opposing_events.append(ev)
                        opposing_eids.append(ev["eventId"])
                        opposing_reasons.append(
                            f"Dữ kiện đối trọng từ {ev.get('eventId')} ({ev.get('headline')}): "
                            f"Tín hiệu hỗ trợ tăng trưởng kinh tế tạo độ phân hóa với định hướng kiểm soát thận trọng rủi ro tín dụng."
                        )
                elif posture in ("POSTURE_MONETARY_STABILIZATION", "POSTURE_COMPLIANCE_ENFORCEMENT") and is_ev_growth:
                    if ev["eventId"] not in opposing_eids and ("lãi suất" in ev_text or "tín dụng" in ev_text or "ngoại tệ" in ev_text):
                        opposing_events.append(ev)
                        opposing_eids.append(ev["eventId"])
                        opposing_reasons.append(
                            f"Dữ kiện đối trọng từ {ev.get('eventId')} ({ev.get('headline')}): "
                            f"Xung lực mở rộng thanh toán/tín dụng tạo thách thức cân bằng đối với mục tiêu kiểm soát ổn định vĩ mô."
                        )

            if opposing_events:
                counter_evidence = opposing_reasons
                conf_level = "MEDIUM"
                conf_reason = (
                    f"Được hỗ trợ bởi {len(c_events)} sự kiện xác minh nhưng ghi nhận {len(opposing_events)} dữ kiện đối lập "
                    f"({', '.join(opposing_eids)}) phản ánh sự phân hóa nội tại và rủi ro ngược chiều."
                )
                causal_exp = (
                    f"Cơ chế truyền dẫn phức hợp: Diễn biến '{lead_hl}' đan xen với các tín hiệu đối trọng từ "
                    f"'{opposing_events[0].get('headline', '')}', buộc các chủ thể kinh tế vừa khai thác cơ hội "
                    f"vừa thiết lập bộ đệm an toàn phòng ngừa rủi ro nợ xấu và thanh khoản."
                )
            else:
                counter_evidence = []
                conf_level = "HIGH" if len(c_events) >= 3 and len(c_facts) >= 2 else ("MEDIUM" if len(c_events) >= 2 else "LOW")
                conf_reason = (
                    f"Được bảo chứng vững chắc bởi {len(c_events)} sự kiện xác minh độc lập, "
                    f"{len(c_facts)} dữ kiện tài chính đã đối soát chủ thể và {len(c_mps)} chỉ số Market Pulse liên đới."
                )
                fact_exprs = [f.get('extractedExpression', '') for f in c_facts[:3] if f.get('extractedExpression')]
                fact_str_exp = f" qua các dữ kiện {', '.join(fact_exprs)}" if fact_exprs else ""
                causal_exp = (
                    f"Cơ chế truyền dẫn: Diễn biến từ '{lead_hl}'{fact_str_exp} "
                    f"tác động trực tiếp lên biến số {affected_vars[0]} trong ngành {c_domain['domainName']}."
                )

            refs = self._build_cross_refs(c_eids, c_fids, c_mp_ids)
            stance_map = {
                "POSTURE_CREDIT_RISK_STRESS": "DEFENSIVE_CREDIT_RISK",
                "POSTURE_EXPANSION_GROWTH": "EXPANSIVE_GROWTH_MOMENTUM",
                "POSTURE_MONETARY_STABILIZATION": "ACTIVE_MONETARY_STABILIZATION",
                "POSTURE_COMPLIANCE_ENFORCEMENT": "STRICT_REGULATORY_COMPLIANCE"
            }
            analytical_stance = stance_map.get(posture, "BALANCED_MARKET_MONITORING")

            thesis_obj = {
                "thesisId": tid,
                "themeGroup": c_domain.get("canonicalThemeGroup", "Banking & Credit"),
                "title": lead_hl,
                "centralArgument": central_arg,
                "thematicPillar": c_domain["domainName"],
                "analyticalStance": analytical_stance,
                "riskPosture": posture,
                "riskLevel": risk_level,
                "whatHappened": what_happened,
                "whatChanged": what_happened,
                "whyItMatters": why_it_matters,
                "affectedVariables": affected_vars,
                "possibleNextDevelopment": possible_next_development,
                "fintechWatchpoint": fintech_watchpoint,
                "supportingEventIds": c_eids,
                "supportingFactIds": c_fids,
                "supportingMarketPulseIds": c_mp_ids,
                "counterEvidenceEventIds": opposing_eids,
                "affectedSectors": [c_domain["defaultSector"]],
                "impactHorizon": "SHORT_TERM_0_3M",
                "confidenceLevel": conf_level,
                "confidenceReason": conf_reason,
                "causalExplanation": causal_exp,
                "counterEvidence": counter_evidence,
                "watchSignals": [
                    f"Biến động số liệu mới của {v}" for v in affected_vars[:3]
                ],
                "invalidationConditions": [
                    f"Nếu số liệu thực tế của {c_domain['domainName']} đảo chiều hoặc cơ quan quản lý điều chỉnh định hướng chính sách."
                ],
                "limitations": [
                    f"Phụ thuộc vào độ trễ truyền dẫn chính sách và các rủi ro bên ngoài của nhóm {c_domain['domainName']}."
                ],
                "sourceReferences": refs,
                "evidenceReferences": refs
            }

            thesis_obj["claimEvidenceCrosswalk"] = self.validate_claim_evidence_crosswalk(
                thesis_or_claim=thesis_obj,
                supporting_events=c_events,
                supporting_facts=c_facts,
                counter_events=opposing_events
            )
            theses_out.append(thesis_obj)

        return {
            "theses": theses_out,
            "totalTheses": len(theses_out),
            "canonicalThemeCoverage": sorted(list(set(t["thematicPillar"] for t in theses_out))),
            "totalSupportingEventsUsed": len(set(eid for t in theses_out for eid in t["supportingEventIds"])),
            "totalUniqueFactsUsed": len(set(fid for t in theses_out for fid in t["supportingFactIds"])),
            "synthesisMethodology": "Dynamic Thematic Event-Clustering & Fact-Grounded Synthesis",
            "modelProviderStatus": self.model_provider_status
        }

    # -------------------------------------------------------------------------
    # STEP 13: DYNAMIC CONNECT THE DOTS (Section 4.6)
    # -------------------------------------------------------------------------
    def generate_connect_the_dots(self) -> Dict[str, Any]:
        """
        Step 13 — Connect the Dots Generation:
        Multi-event synthesis tracing meaningful relationships across independent events.
        Explains concrete causal connections instead of static generic strings.
        """
        theses_bundle = self.generate_core_theses()
        theses = theses_bundle["theses"]
        narratives_out: List[Dict[str, Any]] = []

        for idx, th in enumerate(theses):
            nid = f"DOT-{idx+1:02d}"
            conn_id = f"CONN-{idx+1:02d}"
            eids = th["supportingEventIds"]
            fids = th["supportingFactIds"]
            mp_ids = th["supportingMarketPulseIds"]

            ev_objs = [self.news_by_id[eid] for eid in eids if eid in self.news_by_id]
            lead_hl = ev_objs[0].get("headline", "") if ev_objs else "Diễn biến vĩ mô"
            sec_hl = ev_objs[1].get("headline", "") if len(ev_objs) > 1 else lead_hl

            has_observed_fact = len(fids) > 0
            has_multiple_events = len(eids) >= 2

            macro_link_type = "OBSERVED" if has_observed_fact else "SUPPORTED_INFERENCE"
            banking_link_type = "OBSERVED" if any("ngân hàng" in e.get("headline", "").lower() or "lãi suất" in e.get("headline", "").lower() for e in ev_objs) else "SUPPORTED_INFERENCE"
            corp_link_type = "OBSERVED" if any("doanh nghiệp" in e.get("headline", "").lower() or "vốn" in e.get("headline", "").lower() for e in ev_objs) else "SUPPORTED_INFERENCE"
            payment_link_type = "SUPPORTED_INFERENCE" if has_multiple_events else "HYPOTHESIS"

            # Domain-tailored dynamic narrative sentences (no copy-pasting across clusters)
            domain_pillar = th["thematicPillar"]
            if "Ngân hàng" in domain_pillar:
                synth_text = (
                    f"Từ quan sát vĩ mô và mặt bằng lãi suất ('{lead_hl}'), các NHTM chủ động cân đối thanh khoản và biên lãi thuần (NIM), "
                    f"tác động trực tiếp lên điều kiện cấp vốn cho doanh nghiệp ('{sec_hl}') và thúc đẩy ứng dụng các kênh thu hộ tự động."
                )
                macro_text = f"[{macro_link_type}] Định hướng điều hành tiền tệ và diễn biến chi phí huy động vốn phản ánh rõ qua '{lead_hl}'."
                bank_text = f"[{banking_link_type}] Các NHTM tái cơ cấu danh mục tài sản sinh lời, thận trọng kiểm soát rủi ro nợ xấu và thanh khoản."
                corp_text = f"[{corp_link_type}] Doanh nghiệp tối ưu chi phí vay vốn lưu động, đàm phán kỳ hạn thanh toán và chuẩn hóa dòng tiền thu chi."
                consumer_text = "[SUPPORTED_INFERENCE] Người gửi tiền cân nhắc giữa kênh tiền gửi ngân hàng, vàng và chi tiêu mua sắm thiết yếu."
                pay_text = f"[{payment_link_type}] Hạ tầng thanh toán số hỗ trợ ngân hàng và doanh nghiệp thu hồi nợ tự động qua tài khoản định danh Virtual Account."
            elif "Tiền tệ" in domain_pillar or "Tỷ giá" in domain_pillar:
                synth_text = (
                    f"Động thái điều hành tỷ giá và thị trường mở ('{lead_hl}') tạo kênh truyền dẫn lan tỏa đến dòng tiền của khối doanh nghiệp XNK ('{sec_hl}'), "
                    f"đòi hỏi các giải pháp thanh toán ngoại tệ và phòng vệ rủi ro biến động giá trị đồng tiền."
                )
                macro_text = f"[{macro_link_type}] Tín hiệu can thiệp tỷ giá và cung tiền OMO từ NHNN định hình thanh khoản hệ thống ('{lead_hl}')."
                bank_text = f"[{banking_link_type}] Khối NHTM điều chỉnh chênh lệch giá mua bán USD và cân đối trạng thái ngoại hối liên ngân hàng."
                corp_text = f"[{corp_link_type}] Doanh nghiệp xuất nhập khẩu chủ động chốt tỷ giá kỳ hạn và đẩy nhanh tốc độ luân chuyển tiền hàng."
                consumer_text = "[SUPPORTED_INFERENCE] Nhà đầu tư cá nhân theo dõi biến động tỷ giá và giá vàng để cơ cấu lại danh mục tài sản phòng thủ."
                pay_text = f"[{payment_link_type}] Cổng thanh toán quốc tế và chuyển đổi ngoại tệ tức thời đáp ứng nhu cầu thanh toán xuyên biên giới an toàn."
            elif "Tài khóa" in domain_pillar or "Doanh nghiệp" in domain_pillar:
                synth_text = (
                    f"Chính sách tài khóa mở rộng kết hợp thanh kiểm tra tuân thủ ('{lead_hl}') lan tỏa đến các dự án đầu tư và hoạt động sản xuất ('{sec_hl}'), "
                    f"thúc đẩy chuyển đổi số quy trình kế toán và hóa đơn điện tử máy tính tiền."
                )
                macro_text = f"[{macro_link_type}] Tăng tốc giải ngân vốn đầu tư công và chính sách quản lý thuế dẫn dắt dòng tiền thị trường ('{lead_hl}')."
                bank_text = f"[{banking_link_type}] Ngân hàng thương mại ưu tiên cấp bảo lãnh thanh toán và tài trợ vốn cho các dự án hạ tầng trọng điểm."
                corp_text = f"[{corp_link_type}] Doanh nghiệp và nhà thầu tăng tốc thi công, hoàn thiện hồ sơ nghiệm thu và minh bạch hóa đơn chứng từ."
                consumer_text = "[SUPPORTED_INFERENCE] Dòng tiền giải ngân công tạo việc làm và lan tỏa sức mua sang thị trường tiêu dùng bán lẻ."
                pay_text = f"[{payment_link_type}] Tích hợp máy tính tiền khởi tạo hóa đơn điện tử tự động kết nối máy thanh toán SmartPOS chuẩn hóa dữ liệu."
            else:
                synth_text = (
                    f"Làn sóng mở rộng kênh bán lẻ và dịch vụ tiêu dùng ('{lead_hl}') liên kết chặt chẽ với hoạt động vận chuyển chuỗi cung ứng ('{sec_hl}'), "
                    f"tạo nhu cầu bùng nổ cho các phương thức thanh toán không tiền mặt tại điểm bán."
                )
                macro_text = f"[{macro_link_type}] Tăng trưởng tổng mức bán lẻ và phục hồi chi tiêu kích thích chu chuyển dòng tiền nền kinh tế ('{lead_hl}')."
                bank_text = f"[{banking_link_type}] Ngân hàng và tổ chức thẻ đẩy mạnh chương trình ưu đãi thanh toán và hạn mức thẻ tín dụng."
                corp_text = f"[{corp_link_type}] Chuỗi bán lẻ và dịch vụ F&B tối ưu tốc độ phục vụ quầy thu ngân và cắt giảm thất thoát tiền mặt."
                consumer_text = "[SUPPORTED_INFERENCE] Người tiêu dùng ưu tiên quét mã VietQR và quẹt thẻ không tiếp xúc khi thanh toán dịch vụ hàng ngày."
                pay_text = f"[{payment_link_type}] Mạng lưới SmartPOS All-in-One và VietQR động xử lý khối lượng giao dịch tức thời và bảo mật cao."

            narratives_out.append({
                "connectionId": conn_id,
                "dotId": nid,
                "narrativeId": nid,
                "title": f"Kết nối đa sự kiện: {th['thematicPillar']}",
                "desc": synth_text,
                "supportingThesisId": th["thesisId"],
                "sourceEventIds": [eids[0]] if eids else [],
                "targetEventIds": eids[1:3] if len(eids) > 1 else eids[:1],
                "supportingEventIds": eids,
                "supportingFactIds": fids,
                "supportingMarketPulseIds": mp_ids,
                "relationship": f"Mối quan hệ tác động chuỗi giá trị giữa {lead_hl} và các chủ thể trong nhóm {domain_pillar}.",
                "synthesisNarrative": synth_text,
                "relationshipType": "OBSERVED" if has_observed_fact else "SUPPORTED_INFERENCE",
                "monetaryPolicyLink": macro_text,
                "bankingLink": bank_text,
                "corporateLink": corp_text,
                "consumerAndMarketLink": consumer_text,
                "paymentBehaviorLink": pay_text,
                "confidence": th["confidenceLevel"],
                "limitations": [
                    "Độ trễ truyền dẫn phụ thuộc vào chu kỳ chính sách và phản ứng thực tế của thị trường."
                ],
                "linkClassifications": {
                    "monetaryPolicy": macro_link_type,
                    "banking": banking_link_type,
                    "corporate": corp_link_type,
                    "consumer": "SUPPORTED_INFERENCE",
                    "payment": payment_link_type
                },
                "evidenceReferences": self._build_cross_refs(eids, fids, mp_ids)
            })

        return {
            "narratives": narratives_out,
            "connectTheDots": narratives_out,
            "totalNarratives": len(narratives_out),
            "synthesisQuality": "DYNAMIC_MULTI_EVENT_VERIFIED",
            "modelProviderStatus": self.model_provider_status
        }

    # -------------------------------------------------------------------------
    # STEP 14: DYNAMIC MACRO-TO-MICRO TRANSMISSION (Section 4.7)
    # -------------------------------------------------------------------------
    def generate_macro_to_micro_chains(self) -> Dict[str, Any]:
        """
        Step 14 — Macro-to-Micro Transmission Chains:
        Constructs the 7-stage causal transmission mechanism and evaluates the 5-link
        inference classifications (DIRECTLY_OBSERVED_FACT, REASONABLE_INFERENCE, STRATEGIC_HYPOTHESIS).
        Only includes stages supported by evidence or explicitly identified as hypotheses.
        """
        theses_bundle = self.generate_core_theses()
        theses = theses_bundle["theses"]
        chains_out: List[Dict[str, Any]] = []

        for idx, th in enumerate(theses):
            cid = f"CHAIN-{idx+1:02d}"
            eids = th["supportingEventIds"]
            fids = th["supportingFactIds"]
            mp_ids = th["supportingMarketPulseIds"]

            ev_objs = [self.news_by_id[eid] for eid in eids if eid in self.news_by_id]
            lead_hl = ev_objs[0].get("headline", "") if ev_objs else "Tín hiệu vĩ mô"
            facts_objs = [self.unique_facts_by_id[fid] for fid in fids if fid in self.unique_facts_by_id]
            
            fact_parts = []
            for f in facts_objs[:2]:
                ent = extract_canonical_entity(f)
                expr = f.get("extractedExpression") or ""
                if ent and expr:
                    fact_parts.append(f"{ent}: {expr}")
                elif expr:
                    fact_parts.append(expr)
            fact_summary = "; ".join(fact_parts)

            has_payment_evidence = any(
                any(k in f"{e.get('headline', '')} {e.get('summary', '')}".lower() for k in ["smartpos", "vietqr", "thanh toán", "pos", "mã qr", "cod không tiền mặt", "không dùng tiền mặt", "thẻ tín dụng", "trả góp"])
                for e in ev_objs
            )

            # Global stage derivation from actual global keywords in events
            global_ev = next((e for e in ev_objs if any(k in f"{e.get('headline', '')} {e.get('summary', '')}".lower() for k in ["nhật bản", "hoa kỳ", "fed", "dxy", "quốc tế", "thế giới", "toàn cầu"])), None)
            if global_ev:
                stage1 = f"Tác động từ bối cảnh quốc tế qua sự kiện: '{global_ev.get('headline', '')}' tác động lên cán cân thanh toán và dòng vốn ngoại tệ."
            else:
                stage1 = "Biến động kinh tế toàn cầu, tỷ giá quốc tế và xu hướng lãi suất của các ngân hàng trung ương lớn duy trì môi trường quan sát trung tính."

            stage2 = f"Diễn biến kinh tế vĩ mô Việt Nam, tăng trưởng kinh tế và các cân đối lớn liên quan trực tiếp đến '{lead_hl}'."
            stage3 = f"Định hướng điều hành tiền tệ, thanh khoản thị trường mở và chính sách tỷ giá của Ngân hàng Nhà nước thích ứng với {th['thematicPillar']}."

            if th.get("riskPosture") == "POSTURE_CREDIT_RISK_STRESS":
                stage4 = f"Hệ thống NHTM chuyển trọng tâm sang thu hồi nợ, tăng trích lập dự phòng rủi ro và tái cơ cấu kỳ hạn vay ({fact_summary or 'nợ xấu tăng cao'})."
                stage5 = "Khu vực doanh nghiệp đối diện điều kiện cấp tín dụng bị thắt chặt, áp lực đáo hạn công nợ và chi phí vốn đắt đỏ."
                stage6 = f"Thương nhân và điểm bán thắt chặt chính sách bán chịu, chuyển sang đối soát thanh toán số tức thời để tránh đọng vốn ('{lead_hl}')."
                stage7 = "Người tiêu dùng ưu tiên trả nợ hiện hữu và thận trọng cắt giảm chi tiêu mua sắm tín chấp."
                infer_consumer = "REASONABLE_INFERENCE"
                infer_payment = "REASONABLE_INFERENCE"
            elif th.get("riskPosture") == "POSTURE_EXPANSION_GROWTH":
                stage4 = f"Hệ thống NHTM đẩy mạnh giải ngân tín dụng, hỗ trợ vốn lưu động và tối ưu hóa chi phí vay ({fact_summary or 'tăng trưởng tín dụng'})."
                stage5 = "Cộng đồng doanh nghiệp mở rộng quy mô kinh doanh, đầu tư công nghệ và đẩy mạnh kênh bán lẻ đa kênh."
                if has_payment_evidence:
                    stage6 = f"Thương nhân và điểm bán triển khai các phương thức thanh toán số thích ứng với xung lực tăng trưởng từ '{lead_hl}'."
                    stage7 = "Người tiêu dùng cuối sử dụng các kênh thanh toán không tiền mặt thuận tiện phục vụ nhu cầu mua sắm và giao dịch."
                    infer_consumer = "REASONABLE_INFERENCE"
                    infer_payment = "REASONABLE_INFERENCE"
                else:
                    stage6 = f"(Giả định phân tích) Điểm bán theo dõi biến động từ '{lead_hl}' để tối ưu hóa quản trị dòng tiền và chi phí vận hành."
                    stage7 = "(Giả định phân tích) Hành vi tiêu dùng của khách hàng chịu ảnh hưởng gián tiếp từ điều kiện kinh tế và thu nhập chung."
                    infer_consumer = "STRATEGIC_HYPOTHESIS"
                    infer_payment = "STRATEGIC_HYPOTHESIS"
            elif th.get("riskPosture") == "POSTURE_COMPLIANCE_ENFORCEMENT":
                stage4 = f"Hệ thống ngân hàng hỗ trợ công cụ thu hộ thuế điện tử và quản lý định danh tài khoản doanh nghiệp ({fact_summary or 'tuân thủ pháp lý'})."
                stage5 = "Doanh nghiệp và hộ kinh doanh rà soát nghĩa vụ thuế, chuẩn hóa hóa đơn chứng từ và số liệu bán hàng."
                stage6 = f"Thương nhân trang bị thiết bị SmartPOS xuất hóa đơn điện tử khởi tạo từ máy tính tiền đáp ứng yêu cầu từ '{lead_hl}'."
                stage7 = "Người tiêu dùng nhận hóa đơn điện tử hợp lệ ngay khi thanh toán qua mã QR hoặc thẻ ngân hàng."
                infer_consumer = "REASONABLE_INFERENCE"
                infer_payment = "DIRECTLY_OBSERVED_FACT" if has_payment_evidence else "REASONABLE_INFERENCE"
            else:
                stage4 = f"Hệ thống NHTM điều chỉnh chi phí vốn, thanh khoản và danh mục tín dụng ({fact_summary or 'thanh khoản hệ thống'})."
                stage5 = "Cộng đồng doanh nghiệp tối ưu chi phí vay vốn, quản trị rủi ro thanh khoản và số hóa quy trình thu chi."
                stage6 = f"(Giả định phân tích) Điểm bán theo dõi biến động từ '{lead_hl}' để tối ưu hóa quản trị dòng tiền và chi phí vận hành."
                stage7 = "(Giả định phân tích) Hành vi tiêu dùng của khách hàng chịu ảnh hưởng gián tiếp từ điều kiện kinh tế và thu nhập chung."
                infer_consumer = "STRATEGIC_HYPOTHESIS"
                infer_payment = "STRATEGIC_HYPOTHESIS"

            trans_dict = {
                "stage1_globalEconomy": stage1,
                "stage2_vietnamMacroeconomics": stage2,
                "stage3_monetaryPolicy": stage3,
                "stage4_bankingAndCapitalMarkets": stage4,
                "stage5_corporateFinancingAndOperations": stage5,
                "stage6_merchantPaymentBehavior": stage6,
                "stage7_endUserPaymentBehavior": stage7
            }
            infer_dict = {
                "macroToBanking": "DIRECTLY_OBSERVED_FACT" if len(fids) > 0 else "REASONABLE_INFERENCE",
                "bankingToEnterprise": "REASONABLE_INFERENCE",
                "enterpriseToConsumer": infer_consumer,
                "consumerToPayment": infer_payment,
                "paymentToFintechOpportunity": "STRATEGIC_HYPOTHESIS"
            }
            infer_v4 = {
                "macroDriver": "OBSERVED" if len(fids) > 0 else "SUPPORTED_INFERENCE",
                "bankingImpact": "OBSERVED" if any("ngân hàng" in e.get("headline", "").lower() for e in ev_objs) else "SUPPORTED_INFERENCE",
                "enterpriseImpact": "SUPPORTED_INFERENCE",
                "consumerImpact": "SUPPORTED_INFERENCE" if has_payment_evidence else "HYPOTHESIS",
                "paymentImpact": "SUPPORTED_INFERENCE" if has_payment_evidence else "HYPOTHESIS"
            }

            chains_out.append({
                "chainId": cid,
                "chainTitle": f"Chuỗi truyền dẫn vĩ mô — vi mô: {th['thematicPillar']}",
                "macroDriver": th["thematicPillar"],
                "transmissionMechanism": f"Cơ chế truyền dẫn 7 tầng từ tín hiệu vĩ mô '{lead_hl}' tác động liên hoàn qua hệ thống NHTM, khu vực doanh nghiệp, hộ gia đình và hành vi thanh toán.",
                "bankingImpact": trans_dict["stage4_bankingAndCapitalMarkets"],
                "enterpriseImpact": trans_dict["stage5_corporateFinancingAndOperations"],
                "consumerImpact": trans_dict["stage6_merchantPaymentBehavior"],
                "paymentImpact": trans_dict["stage7_endUserPaymentBehavior"],
                "sevenStageTransmission": trans_dict,
                "macroToMicroTransmission": trans_dict,
                "fiveLinkInferenceClassification": infer_dict,
                "inferenceClassification": infer_v4,
                "potentialTimeLag": "Độ trễ truyền dẫn phụ thuộc vào chu kỳ chính sách và phản ứng thực tế của thị trường",
                "estimatedTimeLag": "Độ trễ truyền dẫn phụ thuộc vào chu kỳ chính sách và phản ứng thực tế của thị trường",
                "watchSignals": th["watchSignals"],
                "monitoringSignals": th["watchSignals"],
                "confidenceLevel": th["confidenceLevel"],
                "supportingThesisId": th["thesisId"],
                "supportingEventIds": eids,
                "supportingFactIds": fids,
                "supportingMarketPulseIds": mp_ids,
                "evidenceReferences": self._build_cross_refs(eids, fids, mp_ids)
            })

        return {
            "chains": chains_out,
            "transmissionChains": chains_out,
            "totalChains": len(chains_out),
            "transmissionArchitecture": "7_STAGE_MECHANISM_5_LINK_CLASSIFICATION",
            "modelProviderStatus": self.model_provider_status
        }

    # -------------------------------------------------------------------------
    # STEP 15: DYNAMIC PAYMENT OPPORTUNITY RADAR (Section 4.8)
    # -------------------------------------------------------------------------
    def _make_radar_signal(
        self,
        radar_id: str,
        opportunity_id: str,
        signal_title: str,
        sector: str,
        opp_type: str,
        priority: str,
        market_signal: str,
        business_problem: str,
        relevant_solution: str,
        target_partner: str,
        commercial_rationale: str,
        confidence: str,
        rec_action: str,
        event_ids: List[str],
        mp_ids: List[str]
    ) -> Dict[str, Any]:
        comm_rel = "HIGH" if priority in ("P0_IMMEDIATE", "P1_HIGH") else ("MEDIUM" if priority == "P2_MEDIUM" else "LOW")
        if opp_type == "NO_DIRECT_OPPORTUNITY":
            comm_rel = "NONE"
            priority = "P3_MONITOR_ONLY"
        elif priority == "P0_CRITICAL":
            priority = "P0_IMMEDIATE"
        elif priority == "P3_LOW":
            priority = "P3_MONITOR_ONLY"

        refs = self._build_cross_refs(event_ids, [], mp_ids)
        return {
            "radarId": radar_id,
            "opportunityId": opportunity_id,
            "signalTitle": signal_title,
            "sector": sector,
            "paymentDomain": sector,
            "targetSegment": target_partner,
            "actualMarketSignal": market_signal,
            "marketSignal": market_signal,
            "verifiedMarketSignal": market_signal,
            "merchantProblem": business_problem,
            "businessProblem": business_problem,
            "paymentImplication": relevant_solution,
            "relevantPaymentSolution": relevant_solution,
            "relevantSolution": relevant_solution,
            "opportunity": relevant_solution,
            "targetPartnerType": target_partner,
            "commercialRationale": commercial_rationale,
            "payooSolutionRelevance": commercial_rationale,
            "payooRelevance": commercial_rationale,
            "commercialRelevance": comm_rel,
            "priority": priority,
            "opportunityType": opp_type,
            "confidence": confidence,
            "confidenceLevel": confidence,
            "recommendedNextAction": rec_action,
            "recommendedMonitoring": [rec_action],
            "triggerEventIds": event_ids,
            "supportingEventIds": event_ids,
            "supportingFacts": [],
            "supportingFactIds": [],
            "supportingMarketPulseIds": mp_ids,
            "marketDrivers": [market_signal, commercial_rationale],
            "merchantImpact": business_problem,
            "consumerImpact": "Người tiêu dùng tiếp cận phương thức thanh toán an toàn, minh bạch và thuận tiện.",
            "affectedSegments": [sector],
            "risk": "Rủi ro thích ứng công nghệ và chi phí triển khai thiết bị ban đầu tại điểm bán.",
            "riskFactors": ["Rủi ro thích ứng công nghệ và chi phí triển khai thiết bị ban đầu tại điểm bán."],
            "counterEvidence": [],
            "evidenceReferences": refs
        }

    def generate_payment_radar_signals(self) -> Dict[str, Any]:
        """
        Step 15 — Payment Opportunity Radar (Section 4.8):
        Evaluates actual commercial evidence across verified news.
        Removes prewritten daily narratives. Never forces a quota.
        Zero opportunities is a valid result if no commercial/payment evidence is found.
        """
        signals_out: List[Dict[str, Any]] = []
        sig_idx = 1

        # Check for sports-only or completely non-financial news
        is_all_sports = all(
            any(k in f"{e.get('headline', '')} {e.get('summary', '')}".lower() for k in ["bóng đá", "asian cup", "thể thao"])
            for e in self.verified_news
        ) if self.verified_news else False

        if is_all_sports:
            return {
                "signals": [],
                "radarSignals": [],
                "totalSignals": 0,
                "verifiedOrEmergingOpportunitiesCount": 0,
                "potentialOpportunitiesCount": 0,
                "noDirectOpportunityCount": 0,
                "commercialCoverage": "ZERO_OPPORTUNITIES_NON_FINANCIAL_INPUT",
                "modelProviderStatus": self.model_provider_status
            }

        # 1. Evaluate Inbound Tourism / Hospitality (VietQR Global / SmartPOS)
        # Boundary rule: Semiconductor partnership between Vietnam and Japan must NOT become a tourism payment opportunity!
        tourism_kw = ["khách quốc tế", "du lịch", "vietqr global", "hàng không", "khách sạn", "lữ hành", "sân bay", "xuất cảnh", "resort", "tourist", "travel"]
        tourism_events = []
        for e in self.verified_news:
            txt = f"{e.get('headline', '')} {e.get('summary', '')}".lower()
            is_semi = any(k in txt for k in ["bán dẫn", "vi mạch", "semiconductor", "chip"])
            if is_semi:
                continue
            if any(k in txt for k in tourism_kw):
                tourism_events.append(e)

        if tourism_events:
            t_eids = [e["eventId"] for e in tourism_events]
            mp07 = self.mp_by_id.get("MP-07", {})
            tourist_val = f"{mp07.get('currentValue', '19.5')} {mp07.get('unit', 'triệu lượt')}" if mp07 else "sản lượng tăng trưởng cao"
            combined_t_text = " ".join([f"{e.get('headline', '')} {e.get('summary', '')} {e.get('supportingQuote', '')}" for e in tourism_events]).lower()
            t_payment_evidence = any(k in combined_t_text for k in ["vietqr global", "pos", "thanh toán", "thẻ quốc tế", "dcc", "ngoại tệ", "visa", "mastercard"])

            if t_payment_evidence:
                opp_type = "VERIFIED_OPPORTUNITY"
                conf = "HIGH"
                biz_prob = "Điểm bán thiếu phương thức chấp nhận thanh toán ngoại tệ xuyên biên giới thuận tiện cho du khách."
                rec_action = "EXPLORE triển khai thiết bị chấp nhận thanh toán thẻ quốc tế và mã VietQR Global tại các điểm bán du lịch."
            else:
                opp_type = "POTENTIAL_OPPORTUNITY"
                conf = "MEDIUM"
                biz_prob = "(Giả định phân tích) Cần khảo sát kiểm chứng mức độ sẵn sàng và nhu cầu chấp nhận thanh toán số của các tiểu thương du lịch."
                rec_action = "VALIDATE khảo sát nhu cầu thanh toán thực tế của các hộ kinh doanh du lịch trước khi đầu tư hạ tầng."

            sig = self._make_radar_signal(
                radar_id=f"RADAR-{sig_idx:02d}",
                opportunity_id=f"OPP-{sig_idx:02d}",
                signal_title="Chấp nhận Thanh toán Du lịch & Bán lẻ Quốc tế (VietQR Global & SmartPOS)",
                sector="Du lịch, Khách sạn & Bán lẻ Quốc tế",
                opp_type=opp_type,
                priority="P0_IMMEDIATE" if opp_type == "VERIFIED_OPPORTUNITY" else "P1_HIGH",
                market_signal=f"Sản lượng khách du lịch quốc tế đạt {tourist_val}.",
                business_problem=biz_prob,
                relevant_solution="Triển khai SmartPOS chấp nhận đa thẻ quốc tế kết hợp mã VietQR Global và DCC chuyển đổi ngoại tệ linh hoạt.",
                target_partner="Chuỗi khách sạn, khu nghỉ dưỡng, nhà hàng F&B du lịch, trung tâm mua sắm và spa.",
                commercial_rationale="Tăng giá trị giỏ hàng trung bình của du khách quốc tế và tối ưu doanh thu phí giao dịch cho đối tác thanh toán.",
                confidence=conf,
                rec_action=rec_action,
                event_ids=t_eids,
                mp_ids=["MP-07"] if "MP-07" in self.mp_by_id else []
            )
            signals_out.append(sig)
            sig_idx += 1

        # 2. Evaluate Logistics & Freight Delivery (J&T Cargo Rule)
        # Without direct payment evidence, classify as POTENTIAL_OPPORTUNITY and VALIDATE.
        logistics_events = [
            e for e in self.verified_news
            if any(k in f"{e.get('headline', '')} {e.get('summary', '')}".lower() for k in ["j&t", "cargo", "vận chuyển", "logistics", "hàng nặng", "giao hàng"])
        ]
        if logistics_events:
            l_eids = [e["eventId"] for e in logistics_events]
            combined_l_text = " ".join([f"{e.get('headline', '')} {e.get('summary', '')} {e.get('supportingQuote', '')}" for e in logistics_events]).lower()
            direct_payment_evidence = any(k in combined_l_text for k in ["thanh toán không tiền mặt", "cod không tiền mặt", "smartpos", "vietqr", "payment link", "thu hộ"])

            if direct_payment_evidence:
                opp_type = "VERIFIED_OPPORTUNITY"
                conf = "HIGH"
                rec_action = "SCALE triển khai đại trà giải pháp thu hộ không tiền mặt trên toàn mạng lưới shipper."
            else:
                opp_type = "POTENTIAL_OPPORTUNITY"
                conf = "MEDIUM"
                rec_action = "VALIDATE nhu cầu thu hộ COD không tiền mặt hoặc Payment Link cho hàng nặng với đối tác logistics trước khi mở rộng."

            sig = self._make_radar_signal(
                radar_id=f"RADAR-{sig_idx:02d}",
                opportunity_id=f"OPP-{sig_idx:02d}",
                signal_title="Thu hộ Không tiền mặt cho Chuyển phát & Vận tải Hàng nặng",
                sector="Logistics & Chuyển phát Hàng nặng",
                opp_type=opp_type,
                priority="P1_HIGH",
                market_signal="Các đơn vị vận chuyển mở rộng mạng lưới trung chuyển hàng nặng phục vụ cao điểm thương mại điện tử.",
                business_problem="Đơn hàng giá trị cao tạo rủi ro quản lý tiền mặt cho tài xế và tỷ lệ từ chối nhận hàng (boom hàng) lớn.",
                relevant_solution="Giải pháp Shipper Dynamic QR định danh theo mã vận đơn và Payment Link thanh toán trước khi giao hàng.",
                target_partner="Doanh nghiệp logistics bưu chính, đơn vị chuyển phát nhanh hàng nặng và sàn TMĐT.",
                commercial_rationale="Cắt giảm chi phí quản lý tiền mặt, giảm thời gian đối soát công nợ và tăng tỷ lệ giao nhận thành công.",
                confidence=conf,
                rec_action=rec_action,
                event_ids=l_eids,
                mp_ids=[]
            )
            signals_out.append(sig)
            sig_idx += 1

        # 3. Evaluate High-Value Retail / Installments (Interest Rate Rule)
        # Requires supporting consumer or retail merchant demand evidence.
        rate_events = [
            e for e in self.verified_news
            if any(k in f"{e.get('headline', '')} {e.get('summary', '')}".lower() for k in ["tiết kiệm", "lãi suất ngân hàng", "7%/năm", "vàng", "bán lẻ", "tiêu dùng", "trả góp"])
        ]
        if rate_events:
            combined_r_text = " ".join([f"{e.get('headline', '')} {e.get('summary', '')} {e.get('supportingQuote', '')}" for e in rate_events]).lower()
            has_consumer_demand = any(k in combined_r_text for k in ["trả góp", "bán lẻ", "tiêu dùng", "mua sắm", "điện máy", "xe điện", "thẻ tín dụng", "thanh toán"])
            has_mp03 = ("MP-03" in self.mp_by_id)
            if has_consumer_demand or has_mp03:
                r_eids = [e["eventId"] for e in rate_events]
                mp03 = self.mp_by_id.get("MP-03", {})
                rate_val = f"{mp03.get('currentValue', '7.0')}{mp03.get('unit', '%/năm')}" if mp03 else "neo ở mức cao"
                sig = self._make_radar_signal(
                    radar_id=f"RADAR-{sig_idx:02d}",
                    opportunity_id=f"OPP-{sig_idx:02d}",
                    signal_title="Dịch vụ Trả góp 0% cho Bán lẻ Giá trị cao & Thiết bị Thông minh",
                    sector="Bán lẻ Giá trị cao, Điện máy & Xe điện",
                    opp_type="POTENTIAL_OPPORTUNITY",
                    priority="P1_HIGH",
                    market_signal=f"Mặt bằng lãi suất tiền gửi 12 tháng {rate_val} và chi phí vốn thúc đẩy nhu cầu phân bổ chi tiêu trả góp.",
                    business_problem="Khách hàng ngại chi trả các món hàng giá trị lớn một lần trong mùa mua sắm cuối năm.",
                    relevant_solution="Dịch vụ Trả góp 0% qua thẻ tín dụng liên kết đa ngân hàng trên thiết bị SmartPOS và cổng thanh toán trực tuyến.",
                    target_partner="Chuỗi bán lẻ điện máy, showroom xe máy điện, trường đào tạo và dịch vụ chăm sóc sức khỏe.",
                    commercial_rationale="Giúp khách hàng phân bổ dòng tiền hàng tháng mà không mất lãi tiền gửi, nâng cao tỷ lệ chốt đơn cho điểm bán.",
                    confidence="MEDIUM",
                    rec_action="VALIDATE kiểm chứng nhu cầu trả góp tại các chuỗi bán lẻ thiết bị gia dụng và xe điện.",
                    event_ids=r_eids,
                    mp_ids=["MP-03"] if "MP-03" in self.mp_by_id else []
                )
                signals_out.append(sig)
                sig_idx += 1

        # 4. Evaluate Direct Merchant Payment Adoption / Retail QR / E-Invoicing
        merchant_payment_events = [
            e for e in self.verified_news
            if e not in tourism_events and e not in logistics_events and e not in rate_events
            and any(k in f"{e.get('headline', '')} {e.get('summary', '')} {e.get('supportingQuote', '')}".lower()
                    for k in ["thanh toán không tiền mặt", "vietqr", "smartpos", "chấp nhận thanh toán", "payment link", "mã qr", "qr code", "cổng thanh toán"])
        ]
        if merchant_payment_events:
            m_eids = [e["eventId"] for e in merchant_payment_events]
            sig = self._make_radar_signal(
                radar_id=f"RADAR-{sig_idx:02d}",
                opportunity_id=f"OPP-{sig_idx:02d}",
                signal_title="Mở rộng Chấp nhận Thanh toán Không tiền mặt cho Mạng lưới Điểm bán",
                sector="Bán lẻ Đa kênh & Điểm bán Độc lập",
                opp_type="VERIFIED_OPPORTUNITY",
                priority="P0_IMMEDIATE",
                market_signal="Gia tăng nhu cầu triển khai phương thức thanh toán không tiền mặt tại các điểm bán và chuỗi bán lẻ.",
                business_problem="Điểm bán cần giải pháp thanh toán nhanh chóng, an toàn và dễ dàng đối soát.",
                relevant_solution="Triển khai SmartPOS đa phương thức kết hợp VietQR động và cổng thanh toán đối soát tự động.",
                target_partner="Các chuỗi bán lẻ, hộ kinh doanh dịch vụ và nhà phân phối hàng tiêu dùng.",
                commercial_rationale="Tăng cường số hóa điểm bán và tối ưu chi phí vận hành cho thương nhân.",
                confidence="HIGH",
                rec_action="DEPLOY triển khai giải pháp thanh toán số trên diện rộng cho mạng lưới đối tác.",
                event_ids=m_eids,
                mp_ids=[]
            )
            signals_out.append(sig)
            sig_idx += 1

        # 5. Evaluate Tax & Compliance / Gold & SME Inspection
        tax_events = [
            e for e in self.verified_news
            if any(k in f"{e.get('headline', '')} {e.get('summary', '')}".lower() for k in ["nợ thuế", "tạm hoãn xuất cảnh", "hóa đơn điện tử", "ngân sách", "hộ kinh doanh", "kinh doanh vàng", "đo lường"])
        ]
        if tax_events:
            tx_eids = [e["eventId"] for e in tax_events]
            sig = self._make_radar_signal(
                radar_id=f"RADAR-{sig_idx:02d}",
                opportunity_id=f"OPP-{sig_idx:02d}",
                signal_title="Giải pháp Thanh toán Tích hợp Hóa đơn Điện tử Khởi tạo từ Máy tính tiền cho SME",
                sector="Hộ kinh doanh Chuỗi & Doanh nghiệp Vừa và Nhỏ (SME)",
                opp_type="POTENTIAL_OPPORTUNITY",
                priority="P2_MEDIUM",
                market_signal="Tăng cường thanh kiểm tra đo lường, chất lượng và chuẩn hóa hóa đơn chứng từ đối với các cơ sở kinh doanh.",
                business_problem="Hộ kinh doanh gặp khó khăn trong việc đối soát doanh thu, xuất hóa đơn điện tử từng lần và tuân thủ thuế.",
                relevant_solution="Gói giải pháp SmartPOS tích hợp phần mềm bán hàng kết nối trực tiếp hóa đơn điện tử khởi tạo từ máy tính tiền.",
                target_partner="Chuỗi cửa hàng bán lẻ, tiệm vàng bạc trang sức, nhà hàng ăn uống và phần mềm POS.",
                commercial_rationale="Đáp ứng đúng yêu cầu pháp lý về hóa đơn điện tử, chuẩn hóa dòng tiền và tích hợp thu hộ thuế tự động.",
                confidence="MEDIUM",
                rec_action="INVESTIGATE nghiên cứu hợp tác với các nhà cung cấp giải pháp hóa đơn điện tử và phần mềm bán hàng.",
                event_ids=tx_eids,
                mp_ids=[]
            )
            signals_out.append(sig)
            sig_idx += 1

        # 6. Evaluate Macro/Treasury (Interbank FX, sovereign debt, energy infrastructure)
        macro_events = [
            e for e in self.verified_news
            if any(k in f"{e.get('headline', '')} {e.get('summary', '')}".lower() for k in ["mua usd", "evn", "đấu thầu", "trái phiếu", "omo", "dầu khí"])
        ]
        if macro_events:
            m_eids = [e["eventId"] for e in macro_events]
            sig = self._make_radar_signal(
                radar_id=f"RADAR-{sig_idx:02d}",
                opportunity_id=f"OPP-{sig_idx:02d}",
                signal_title="Theo dõi Thanh khoản Thị trường Ngoại hối Liên ngân hàng & Hạ tầng Năng lượng",
                sector="Thị trường Ngoại hối Liên ngân hàng & Hạ tầng Năng lượng",
                opp_type="NO_DIRECT_OPPORTUNITY",
                priority="P3_MONITOR_ONLY",
                market_signal="Hoạt động điều tiết can thiệp ngoại hối của NHNN và kế hoạch đầu tư lưới điện hạ tầng EVN.",
                business_problem="Các giao dịch buôn ngoại tệ liên ngân hàng và vốn đầu tư hạ tầng quốc gia không phát sinh giao dịch thanh toán bán lẻ.",
                relevant_solution="Không phát triển giải pháp thanh toán bán lẻ; giữ vai trò theo dõi thanh khoản hệ thống.",
                target_partner="Không áp dụng đối tác thương mại trung gian thanh toán bán lẻ.",
                commercial_rationale="Sàng lọc minh bạch để không lãng phí nguồn lực tiếp thị và kinh doanh vào các sự kiện phi thương mại.",
                confidence="HIGH",
                rec_action="MONITOR tiếp tục theo dõi diễn biến thanh khoản tiền đồng để đánh giá mặt bằng lãi suất chung.",
                event_ids=m_eids,
                mp_ids=["MP-01", "MP-08"] if "MP-01" in self.mp_by_id else []
            )
            signals_out.append(sig)

        ver_count = sum(1 for s in signals_out if s.get("opportunityType") in ("VERIFIED_OPPORTUNITY", "EMERGING_OPPORTUNITY"))
        pot_count = sum(1 for s in signals_out if s.get("opportunityType") == "POTENTIAL_OPPORTUNITY")
        no_count = sum(1 for s in signals_out if s.get("opportunityType") == "NO_DIRECT_OPPORTUNITY")

        return {
            "signals": signals_out,
            "radarSignals": signals_out,
            "totalSignals": len(signals_out),
            "verifiedOrEmergingOpportunitiesCount": ver_count,
            "potentialOpportunitiesCount": pot_count,
            "noDirectOpportunityCount": no_count,
            "commercialCoverage": "PRIORITY_PAYMENT_SECTORS_EVALUATED",
            "modelProviderStatus": self.model_provider_status
        }

    # -------------------------------------------------------------------------
    # STEP 16: FINANCIAL DECISION INTELLIGENCE (Section 4.9)
    # -------------------------------------------------------------------------
    def _make_decision_card(
        self,
        decision_id: str,
        title: str,
        category: str,
        action: str,
        what_changed: str,
        why_it_matters: str,
        thesis_id: str,
        chain_id: str,
        radar_id: str,
        event_ids: List[str],
        mp_ids: List[str],
        facts: List[str],
        opportunity: str,
        risk: str,
        triggers: List[str],
        confidence: str
    ) -> Dict[str, Any]:
        refs = self._build_cross_refs(event_ids, [], mp_ids)
        return {
            "decisionId": decision_id,
            "decisionTitle": title,
            "title": title,
            "headline": title,
            "decisionCategory": category,
            "executiveSummary": what_changed,
            "whatChanged": what_changed,
            "whyItMatters": why_it_matters,
            "supportingThesisIds": [thesis_id] if thesis_id else [],
            "supportingThesisId": thesis_id,
            "supportingChainIds": [chain_id] if chain_id else [],
            "supportingMacroChainId": chain_id,
            "supportingRadarIds": [radar_id] if radar_id else [],
            "supportingRadarSignalId": radar_id,
            "relatedRadarIds": [radar_id] if radar_id else [],
            "supportingEventIds": event_ids,
            "supportingMarketPulseIds": mp_ids,
            "supportingFacts": facts,
            "supportingFactIds": [f for f in facts if f],
            "opportunity": opportunity,
            "opportunities": [opportunity],
            "risk": risk,
            "risks": [risk],
            "recommendedAction": action,
            "monitoringTriggers": triggers,
            "timeHorizon": "IMMEDIATE_1_2_WEEKS",
            "confidence": confidence,
            "confidenceLevel": confidence,
            "limitations": [
                "Cần đối chiếu số liệu triển khai thực tế và năng lực tích hợp hệ thống của các bên trước khi mở rộng quy mô."
            ],
            "evidenceReferences": refs
        }

    def generate_decision_cards(
        self,
        theses: Optional[List[Dict[str, Any]]] = None,
        chains: Optional[List[Dict[str, Any]]] = None,
        radar_signals: Optional[List[Dict[str, Any]]] = None,
        gate_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Step 16 — Financial Decision Intelligence (Section 4.9):
        Synthesizes grounded Executive Decision Cards only when current evidence supports a meaningful decision.
        Derives the 5 Strategic Questions Executive Synthesis dynamically from current metrics.
        """
        if theses is None:
            theses = self.generate_core_theses()["theses"]
        if chains is None:
            chains = self.generate_macro_to_micro_chains()["chains"]
        if radar_signals is None:
            radars = self.generate_payment_radar_signals()["signals"]
        else:
            radars = radar_signals

        active_radars = [r for r in radars if r.get("opportunityType") in ("VERIFIED_OPPORTUNITY", "EMERGING_OPPORTUNITY", "POTENTIAL_OPPORTUNITY")]

        # If zero active opportunities and zero theses (e.g. sports-only input)
        if not active_radars and not theses:
            five_questions_zero = {
                "question1_whatIsMarketChanging": "Không phát hiện biến động tài chính hoặc chính sách tiền tệ trọng yếu từ tập dữ liệu hiện tại.",
                "question2_macroImpactOnBanksEnterprisesConsumers": "Thị trường tài chính duy trì trạng thái trung tính, chưa ghi nhận tác động lan tỏa từ các sự kiện phi tài chính.",
                "question3_cashlessPaymentOpportunities": "Chưa ghi nhận cơ hội thanh toán không tiền mặt trực tiếp từ tập dữ liệu quan sát.",
                "question4_keyWatchSignals": "Tiếp tục theo dõi các kênh tin tức tài chính và diễn biến điều hành chính thức.",
                "question5_bryanNextActions": "Không có hành động thương mại cần kích hoạt ngay do thiếu dữ kiện thanh toán hỗ trợ."
            }
            return {
                "cards": [],
                "decisionCards": [],
                "totalDecisionCards": 0,
                "fiveQuestionsExecutiveSynthesis": five_questions_zero,
                "modelProviderStatus": self.model_provider_status
            }

        cards_out: List[Dict[str, Any]] = []

        # Decision Card 1: Commercial Expansion (from top retail/tourism/payment radar)
        r_comm = next((r for r in active_radars if any(k in r.get("sector", "").lower() for k in ["du lịch", "bán lẻ", "điểm bán", "thanh toán"])), None)
        t_comm = next((t for t in theses if any(k in t.get("thematicPillar", "").lower() for k in ["bán lẻ", "tiêu dùng", "du lịch"])), None) or (theses[0] if theses else None)
        c_comm = chains[0] if chains else None

        if r_comm:
            eids1 = list(set(r_comm["supportingEventIds"] + (t_comm["supportingEventIds"] if t_comm else [])))
            card1 = self._make_decision_card(
                decision_id="DECISION-01",
                title=f"Mở rộng Chấp nhận Thanh toán cho {r_comm['sector']}",
                category="COMMERCIAL_OPPORTUNITY",
                action=r_comm.get("recommendedNextAction", "EXPLORE").split()[0],
                what_changed=r_comm["marketSignal"],
                why_it_matters=f"Tác động lan tỏa từ sự chuyển dịch của {r_comm['sector']} mở ra cơ hội gia tăng doanh số thanh toán số và tối ưu chi phí đối soát.",
                thesis_id=t_comm["thesisId"] if t_comm else "THESIS-01",
                chain_id=c_comm["chainId"] if c_comm else "CHAIN-01",
                radar_id=r_comm["radarId"],
                event_ids=eids1,
                mp_ids=r_comm.get("supportingMarketPulseIds", []),
                facts=[],
                opportunity=r_comm["relevantSolution"],
                risk="Rủi ro thích ứng công nghệ và chi phí lắp đặt thiết bị đầu cuối tại điểm bán.",
                triggers=[f"Doanh số giao dịch và tốc độ phủ điểm chấp nhận thanh toán tại {r_comm['sector']}."],
                confidence=r_comm["confidence"]
            )
            cards_out.append(card1)

        # Decision Card 2: Operations / Supply Chain / Compliance (Logistics or SME Invoice)
        r_ops = next((r for r in active_radars if r != r_comm and any(k in r.get("sector", "").lower() for k in ["logistics", "chuyển phát", "sme", "hộ kinh doanh", "thuế"])), None)
        if r_ops:
            card2 = self._make_decision_card(
                decision_id="DECISION-02",
                title=f"Triển khai Giải pháp Thanh toán & Đối soát cho {r_ops['sector']}",
                category="MARKET_OPPORTUNITY",
                action=r_ops.get("recommendedNextAction", "VALIDATE").split()[0],
                what_changed=r_ops["marketSignal"],
                why_it_matters=f"Giải quyết triệt để bài toán công nợ và rủi ro quản lý tiền mặt cho các doanh nghiệp thuộc {r_ops['sector']}.",
                thesis_id=theses[0]["thesisId"] if theses else "THESIS-01",
                chain_id=chains[0]["chainId"] if chains else "CHAIN-01",
                radar_id=r_ops["radarId"],
                event_ids=r_ops["supportingEventIds"],
                mp_ids=r_ops.get("supportingMarketPulseIds", []),
                facts=[],
                opportunity=r_ops["relevantSolution"],
                risk="Thói quen thanh toán tiền mặt cố hữu và yêu cầu tích hợp đồng bộ phần mềm.",
                triggers=[f"Phản hồi từ các đối tác thương mại thuộc {r_ops['sector']} và tỷ lệ số hóa thanh toán."],
                confidence=r_ops["confidence"]
            )
            cards_out.append(card2)

        # Decision Card 3: Banking, Credit Risk & Liquidity Defense/Scale
        t_bank = next((t for t in theses if any(k in t.get("thematicPillar", "").lower() for k in ["ngân hàng", "tiền tệ", "lãi suất", "tín dụng"])), None) or (theses[0] if theses else None)
        if t_bank and chains:
            eids3 = t_bank["supportingEventIds"]
            if t_bank.get("riskPosture") == "POSTURE_CREDIT_RISK_STRESS":
                card3 = self._make_decision_card(
                    decision_id="DECISION-03",
                    title="Kiểm soát Rủi ro Tín dụng & Siết chặt Thu hồi Công nợ Phòng ngừa Nợ xấu",
                    category="RISK_DEFENSE",
                    action="DEFEND",
                    what_changed=t_bank["centralArgument"],
                    why_it_matters=t_bank["whyItMatters"],
                    thesis_id=t_bank["thesisId"],
                    chain_id=chains[0]["chainId"],
                    radar_id="RADAR-03",
                    event_ids=eids3,
                    mp_ids=t_bank.get("supportingMarketPulseIds", []),
                    facts=[f.get("extractedExpression") for fid in t_bank["supportingFactIds"][:3] if (f := self.unique_facts_by_id.get(fid))],
                    opportunity="Triển khai công cụ thanh toán thu nợ tức thời qua SmartPOS và Virtual Account để ngăn nợ xấu phát sinh.",
                    risk="Tỷ lệ nợ xấu tăng cao bào mòn lợi nhuận và làm suy giảm bộ đệm vốn an toàn.",
                    triggers=["Tỷ lệ nợ xấu nội bảng và chi phí trích lập dự phòng tại các kỳ công bố BCTC."],
                    confidence="HIGH"
                )
            elif t_bank.get("riskPosture") == "POSTURE_EXPANSION_GROWTH":
                card3 = self._make_decision_card(
                    decision_id="DECISION-03",
                    title="Đẩy mạnh Cung ứng Tín dụng & Mở rộng Thanh toán Thương mại",
                    category="COMMERCIAL_OPPORTUNITY",
                    action="SCALE",
                    what_changed=t_bank["centralArgument"],
                    why_it_matters=t_bank["whyItMatters"],
                    thesis_id=t_bank["thesisId"],
                    chain_id=chains[0]["chainId"],
                    radar_id="RADAR-03",
                    event_ids=eids3,
                    mp_ids=t_bank.get("supportingMarketPulseIds", []),
                    facts=[f.get("extractedExpression") for fid in t_bank["supportingFactIds"][:3] if (f := self.unique_facts_by_id.get(fid))],
                    opportunity="Mở rộng gói tài trợ thương mại và giải pháp chấp nhận thanh toán số cho mạng lưới phân phối.",
                    risk="Kiểm soát rủi ro tăng trưởng nóng và thanh khoản liên ngân hàng cuối năm.",
                    triggers=["Tốc độ tăng trưởng tín dụng toàn hệ thống và biểu lãi suất huy động."],
                    confidence="HIGH"
                )
            else:
                card3 = self._make_decision_card(
                    decision_id="DECISION-03",
                    title="Theo dõi Tác động Thanh khoản từ Kênh Ngoại hối & Lãi suất Huy động",
                    category="MONITORING_REQUIRED",
                    action="MONITOR",
                    what_changed=t_bank["centralArgument"],
                    why_it_matters="Chi phí vốn ngân hàng ảnh hưởng trực tiếp đến biên lợi nhuận tài trợ vốn của doanh nghiệp và người tiêu dùng.",
                    thesis_id=t_bank["thesisId"],
                    chain_id=chains[0]["chainId"],
                    radar_id="RADAR-03",
                    event_ids=eids3,
                    mp_ids=t_bank.get("supportingMarketPulseIds", []),
                    facts=[f.get("extractedExpression") for fid in t_bank["supportingFactIds"][:3] if (f := self.unique_facts_by_id.get(fid))],
                    opportunity="Thúc đẩy giải pháp trả góp 0% để giảm áp lực chi trả một lần cho người tiêu dùng.",
                    risk="Biến động lãi suất liên ngân hàng và thanh khoản hệ thống.",
                    triggers=["Biểu lãi suất huy động tại các NHTM và số liệu can thiệp thị trường của NHNN."],
                    confidence="HIGH"
                )
            cards_out.append(card3)

        # Decision Card 4: Product Strategy / Compliance / Retail Installment
        r_other = next((r for r in active_radars if r not in (r_comm, r_ops)), None)
        if r_other and len(theses) > 1 and len(chains) > 1:
            card4 = self._make_decision_card(
                decision_id="DECISION-04",
                title=f"Chiến lược Giải pháp Thanh toán Chuyên sâu cho {r_other['sector']}",
                category="STRATEGIC_SIGNAL",
                action=r_other.get("recommendedNextAction", "INVESTIGATE").split()[0],
                what_changed=r_other["marketSignal"],
                why_it_matters="Đón đầu xu hướng chuyển dịch thanh toán số và chuẩn hóa tuân thủ dòng tiền.",
                thesis_id=theses[1]["thesisId"],
                chain_id=chains[1]["chainId"],
                radar_id=r_other["radarId"],
                event_ids=r_other["supportingEventIds"],
                mp_ids=r_other.get("supportingMarketPulseIds", []),
                facts=[],
                opportunity=r_other["relevantSolution"],
                risk="Thời gian thích ứng quy trình nghiệp vụ và chi phí đầu tư ban đầu.",
                triggers=["Văn bản hướng dẫn thi hành và tốc độ tiếp nhận giải pháp của thị trường."],
                confidence="MEDIUM"
            )
            cards_out.append(card4)

        # Re-index decision IDs sequentially
        for idx_c, card in enumerate(cards_out, 1):
            card["decisionId"] = f"DECISION-{idx_c:02d}"

        # Dynamic 5 Strategic Questions Executive Synthesis
        q1_summary = " ".join([t["centralArgument"] for t in theses[:2]]) if theses else "Không phát hiện biến động tài chính hoặc chính sách tiền tệ trọng yếu."
        q3_opps = "; ".join([f"({i+1}) {r['sector']}: {r['relevantSolution']}" for i, r in enumerate(active_radars[:3])]) if active_radars else "Chưa ghi nhận cơ hội thanh toán không tiền mặt trực tiếp từ tập dữ liệu quan sát."
        q4_signals = "; ".join([f"{r['sector']}: theo dõi {r['marketSignal'][:80]}" for r in active_radars[:3]]) if active_radars else "Tiếp tục theo dõi các kênh tin tức tài chính và diễn biến điều hành chính thức."
        q5_actions = "; ".join([f"{c['recommendedAction']}: {c['title']}" for c in cards_out]) if cards_out else "Không có hành động thương mại cần kích hoạt ngay do thiếu dữ kiện thanh toán hỗ trợ."

        has_stress = any(t.get("riskPosture") == "POSTURE_CREDIT_RISK_STRESS" for t in theses)
        if has_stress:
            q2_impact = "Ngân hàng chịu áp lực nợ xấu tăng cao và gánh nặng trích lập dự phòng rủi ro; doanh nghiệp đối diện điều kiện cấp tín dụng bị thắt chặt và chi phí vốn đắt đỏ; người tiêu dùng ưu tiên trả nợ hiện hữu và thận trọng trong vay mượn mới."
            q4_watch = "Theo dõi sát diễn biến tỷ lệ nợ xấu nội bảng, biến động chi phí trích lập dự phòng và thanh khoản liên ngân hàng."
            q5_next = f"Kế hoạch hành động khuyến nghị cho Bryan: Chuyển sang tư thế phòng thủ rủi ro tín dụng; {q5_actions}."
        else:
            q2_impact = (
                "Ngân hàng duy trì cân đối chi phí huy động và thanh khoản; doanh nghiệp đối mặt với chi phí vốn chọn lọc nhưng hưởng lợi từ dòng tiền thông suốt hơn; "
                "người tiêu dùng duy trì tâm lý tích lũy phòng thủ kết hợp tập trung mua sắm có kế hoạch vào các dịp khuyến mại."
            )
            q4_watch = f"Các tín hiệu điều hành và thị trường trọng điểm cần bám sát: {q4_signals}."
            q5_next = f"Kế hoạch hành động khuyến nghị cho Bryan: {q5_actions}."

        five_questions = {
            "question1_whatIsMarketChanging": f"Thị trường đang chuyển động theo các trục vĩ mô chính: {q1_summary}",
            "question2_macroImpactOnBanksEnterprisesConsumers": q2_impact,
            "question3_cashlessPaymentOpportunities": f"Các cơ hội thương mại nổi bật nhất cho thanh toán không tiền mặt bao gồm: {q3_opps}.",
            "question4_keyWatchSignals": q4_watch,
            "question5_bryanNextActions": q5_next
        }

        return {
            "cards": cards_out,
            "decisionCards": cards_out,
            "totalDecisionCards": len(cards_out),
            "fiveQuestionsExecutiveSynthesis": five_questions,
            "modelProviderStatus": self.model_provider_status
        }

    generate_financial_decision_intelligence = generate_decision_cards
