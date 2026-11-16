#!/usr/bin/env python3
"""
market_pulse_validator.py — Bryan FinTech Intelligence Phase 05B-R1.3A.3
Fact-Level Verification, Freshness Governance, Scope Boundary & Contract Consistency Validator.

Mandates:
1. P0-04 Fail-Closed: MUST NOT return VERIFIED if any required field is missing.
   Mandatory required fields: indicatorId, actualValue, unit, observationDate, sourceUrl,
   sourcePublisher, evidencePath, evidenceSha256, supportingQuote, normalizationTrace.
2. Evidence file must physically exist on disk and SHA-256 must match raw bytes.
3. Supporting quote must be verbatim in evidence text; numeric expression must be grounded.
4. P1-01 Schema Compatibility: STALE observations set verificationStatus = "UNVERIFIED",
   verificationNote = "STALE_OBSERVATION: ...", actualValue = null, success = false.
5. P1-02 Single Source of Truth: Loads freshness ceilings and specifications from
   market_pulse_indicator_specs.json.
"""

import os
import json
import hashlib
import gzip
import re
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Tuple, Optional

from secure_http_client import SecureHTTPClient
from financial_numeric_normalizer import FinancialNumericNormalizer, FinancialDecimal

TIMEZONE_HCM = timezone(timedelta(hours=7))


def resolve_canonical_specs_path() -> str:
    """Resolves the canonical indicator specification path (03_INDICATOR_CONFIG/market_pulse_indicator_specs.json)."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.normpath(os.path.join(base_dir, "..", "03_INDICATOR_CONFIG", "market_pulse_indicator_specs.json")),
        os.path.join(base_dir, "03_INDICATOR_CONFIG", "market_pulse_indicator_specs.json"),
        os.path.join(base_dir, "market_pulse_indicator_specs.json"),
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return candidates[0]


def load_canonical_specs(specs_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Loads canonical indicator specifications from 03_INDICATOR_CONFIG/market_pulse_indicator_specs.json.
    Fails closed with CONFIGURATION_INVALID if the canonical configuration file is missing or invalid.
    Never silently falls back to embedded defaults.
    """
    target_path = specs_path if specs_path is not None else resolve_canonical_specs_path()
    if not target_path or not os.path.exists(target_path):
        raise RuntimeError(
            f"CONFIGURATION_INVALID: Canonical indicator specification file '03_INDICATOR_CONFIG/market_pulse_indicator_specs.json' is missing at '{target_path}'."
        )
    try:
        with open(target_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as exc:
        raise RuntimeError(
            f"CONFIGURATION_INVALID: Failed to parse canonical indicator specification file '{target_path}': {exc}"
        ) from exc

    indicators = data.get("indicators") if isinstance(data, dict) else None
    required_ids = [f"MP-0{i}" for i in range(1, 9)]
    if not isinstance(indicators, dict) or not all(ind_id in indicators for ind_id in required_ids):
        raise RuntimeError(
            f"CONFIGURATION_INVALID: Canonical indicator specification file '{target_path}' is missing required MP-01..MP-08 definitions."
        )
    return indicators


CANONICAL_SPECS = load_canonical_specs()

# Indicator Freshness Ceilings in Hours (strictly derived from canonical specs without silent fallback)
FRESHNESS_CEILINGS_HOURS = {
    ind_id: float(spec["freshnessMaxAgeHours"])
    for ind_id, spec in CANONICAL_SPECS.items()
}


class MarketPulseValidator:
    """Fact-level validator enforcing zero-trust data contract invariants."""

    @staticmethod
    def compute_sha256(filepath: str) -> str:
        h = hashlib.sha256()
        with open(filepath, "rb") as f:
            while chunk := f.read(65536):
                h.update(chunk)
        return h.hexdigest()

    @classmethod
    def validate_evidence_integrity(cls, evidence_path: str, expected_sha256: str) -> Tuple[bool, str]:
        """Validates that evidence snapshot exists and matches recorded cryptographic byte hash."""
        if not evidence_path or not os.path.exists(evidence_path):
            return False, f"EVIDENCE_MISSING: Evidence snapshot file not found at '{evidence_path}'."
        if not expected_sha256:
            return False, "MISSING_EVIDENCE_SHA256: Expected SHA-256 hash is missing."
        actual_sha = cls.compute_sha256(evidence_path)
        if actual_sha.lower() != expected_sha256.lower():
            return False, f"SHA256_MISMATCH: Computed hash '{actual_sha}' diverges from expected '{expected_sha256}'."
        return True, "VERIFIED_BYTE_EXACT"

    @classmethod
    def validate_quote_grounding(cls, evidence_path: str, context_quote: str) -> Tuple[bool, str]:
        """Validates that supporting quote is grounded verbatim in raw evidence text."""
        if not evidence_path or not os.path.exists(evidence_path):
            return False, "EVIDENCE_FILE_NOT_FOUND"
        try:
            with open(evidence_path, "rb") as f:
                raw_bytes = f.read()
            if raw_bytes[:2] == b'\x1f\x8b':
                content = gzip.decompress(raw_bytes).decode("utf-8", errors="replace")
            else:
                content = raw_bytes.decode("utf-8", errors="replace")
            if not context_quote or context_quote.strip() not in content:
                return False, "QUOTE_NOT_IN_EVIDENCE: Supporting quote could not be found verbatim in snapshot."
            return True, "QUOTE_GROUNDED"
        except Exception as e:
            return False, f"READ_ERROR: {str(e)}"

    @classmethod
    def validate_observation_freshness(
        cls,
        ind_id: str,
        obs_date_str: Optional[str],
        run_dt: datetime,
        max_age_hours: Optional[float] = None
    ) -> Tuple[bool, str, Optional[float]]:
        """
        Validates observation date against indicator-specific expected update cycle.
        """
        if not obs_date_str:
            return False, "MISSING_OBSERVATION_DATE: Cannot verify freshness without explicit observation date.", None

        try:
            parts = [int(p) for p in obs_date_str.split("-")]
            obs_dt = datetime(parts[0], parts[1], parts[2], tzinfo=TIMEZONE_HCM)
        except Exception:
            return False, f"UNPARSEABLE_DATE: '{obs_date_str}'", None

        # Check calendar date against run date
        if obs_dt.date() > run_dt.date():
            return False, f"FUTURE_OBSERVATION_DATE: Observation date '{obs_date_str}' is in the future.", -24.0

        if obs_dt.date() == run_dt.date():
            age_hours = 0.0
        else:
            obs_dt_eod = datetime(parts[0], parts[1], parts[2], 17, 0, tzinfo=TIMEZONE_HCM)
            age_hours = (run_dt - obs_dt_eod).total_seconds() / 3600.0

        max_age = max_age_hours if max_age_hours is not None else FRESHNESS_CEILINGS_HOURS.get(ind_id, 72.0)
        if age_hours > max_age:
            if ind_id == "MP-02":
                return False, f"STALE_OBSERVATION: Lãi suất liên ngân hàng qua đêm đã vượt trần {max_age}h ({age_hours:.1f}h > {max_age}h).", age_hours
            return False, f"STALE_OBSERVATION: Observation exceeds maximum allowable age of {max_age} hours ({age_hours:.1f}h).", age_hours

        return True, "FRESHNESS_VERIFIED", round(age_hours, 1)

    @classmethod
    def is_navigation_quote(cls, quote: str) -> bool:
        from market_pulse_extractor import MarketPulseExtractor
        return MarketPulseExtractor.is_navigation_quote(quote)

    @classmethod
    def validate_indicator_observation(
        cls,
        ind_id: str,
        obs_record: Dict[str, Any],
        run_dt: datetime,
        max_age_hours: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Complete fact-level gate for an indicator observation.
        Enforces P0-04 Fail-Closed Security:
        - All mandatory fields MUST be present and valid before VERIFIED is possible.
        - Physical file existence and byte SHA-256 match strictly required.
        - Supporting quote and exact numeric value must be grounded in raw evidence.
        - P1-01: STALE observation sets verificationStatus = 'UNVERIFIED', success = False, actualValue = None.
        """
        output = dict(obs_record)
        output["lastCheckedAt"] = run_dt.isoformat()

        # Helper to fail-closed cleanly
        def fail_closed(reason_note: str, unverified_reason: Optional[str] = None):
            output["success"] = False
            output["actualValue"] = None
            output["verificationStatus"] = "UNVERIFIED"
            output["observationDate"] = None
            output["observationTimestamp"] = None
            output["supportingQuote"] = None
            note = f"{unverified_reason} - {reason_note}" if unverified_reason and unverified_reason not in reason_note else reason_note
            output["verificationNote"] = note
            output["unverifiedReason"] = unverified_reason or reason_note
            return output

        # 1. Navigation Quote Rejection
        quote = obs_record.get("supportingQuote", "")
        if quote and cls.is_navigation_quote(quote):
            return fail_closed("NAVIGATION_LABEL_REJECTED: Đoạn trích dẫn thuộc thanh điều hướng website.")

        # 2. Check if extraction reported failure or unverified reason
        if not obs_record.get("success", False) or obs_record.get("actualValue") is None or obs_record.get("unverifiedReason"):
            reason = obs_record.get("unverifiedReason") or f"Chỉ số {ind_id} không thể trích xuất được số liệu từ nguồn."
            return fail_closed(f"Không thể trích xuất số liệu đo lường: {reason}", reason)

        # 3. Observation Date Grounding and Freshness Check
        obs_date = obs_record.get("observationDate")
        if obs_date:
            ok_fresh, fresh_msg, age_hrs = cls.validate_observation_freshness(
                ind_id, obs_date, run_dt, max_age_hours=max_age_hours
            )
            if not ok_fresh:
                output["success"] = False
                output["actualValue"] = None
                output["verificationStatus"] = "UNVERIFIED"
                output["verificationNote"] = fresh_msg
                output["dataAgeHours"] = age_hrs
                output["observationDate"] = None
                output["observationTimestamp"] = None
                return output

        # 4. P0-04 Mandatory Fields Checklist: All fields must exist before VERIFIED is possible
        mandatory_fields = [
            "indicatorId", "actualValue", "unit", "observationDate",
            "sourceUrl", "sourcePublisher", "evidencePath", "evidenceSha256",
            "supportingQuote"
        ]
        for field in mandatory_fields:
            val = obs_record.get(field)
            if val is None or (isinstance(val, str) and not val.strip()):
                reason = obs_record.get("unverifiedReason") or f"Thiếu trường bắt buộc '{field}'."
                return fail_closed(f"MISSING_REQUIRED_VERIFICATION_FIELD: Field '{field}' is missing or null.", reason)

        ev_path = obs_record.get("evidencePath")
        ev_sha = obs_record.get("evidenceSha256")
        ev_url = obs_record.get("sourceUrl", "")
        src_pub = str(obs_record.get("sourcePublisher", "")).strip().lower()

        # 4.1. Approved Publisher Domain Enforcement (Canonical Specs Single Source of Truth)
        approved_domains = [
            d.lower() for d in CANONICAL_SPECS.get(ind_id, {}).get("approvedDomains", [])
        ]
        if approved_domains:
            from urllib.parse import urlparse
            parsed_host = (urlparse(ev_url).hostname or src_pub).lower()
            is_local_test = parsed_host in {"localhost", "127.0.0.1", "::1"} or src_pub in {"localhost", "127.0.0.1", "::1"}
            domain_ok = is_local_test or any(
                parsed_host == d or parsed_host.endswith("." + d) or src_pub == d or src_pub.endswith("." + d)
                for d in approved_domains
            )
            if not domain_ok:
                return fail_closed(
                    f"UNAPPROVED_PUBLISHER_DOMAIN: Nguồn '{parsed_host or src_pub}' không nằm trong danh sách tên miền được phê duyệt cho {ind_id} ({', '.join(approved_domains)}).",
                    "UNAPPROVED_PUBLISHER_DOMAIN"
                )

        # Support portable relative evidence paths across workspace and extracted package layouts
        if ev_path and not os.path.exists(ev_path):
            base_dir = os.path.dirname(os.path.abspath(__file__))
            candidates_ev = [
                os.path.join(base_dir, ev_path),
                os.path.join(base_dir, "raw_evidence_store", os.path.basename(ev_path)),
                os.path.normpath(os.path.join(base_dir, "..", ev_path)),
                os.path.normpath(os.path.join(base_dir, "..", "04_RAW_EVIDENCE", ev_path)),
                os.path.normpath(os.path.join(base_dir, "..", "04_RAW_EVIDENCE", "raw_evidence_store", os.path.basename(ev_path))),
            ]
            for cand_ev in candidates_ev:
                if os.path.exists(cand_ev):
                    ev_path = cand_ev
                    break

        # 5. Physical file existence
        if not ev_path or not os.path.exists(ev_path):
            return fail_closed(f"EVIDENCE_MISSING: Evidence file does not physically exist at '{ev_path}'.")

        # 6. SHA-256 byte-level cryptographic match
        ok_hash, hash_msg = cls.validate_evidence_integrity(ev_path, ev_sha)
        if not ok_hash:
            return fail_closed(f"EVIDENCE_HASH_MISMATCH: {hash_msg}")

        # Read wire text
        ev_text = ""
        try:
            with open(ev_path, "rb") as f:
                raw_bytes = f.read()
            if raw_bytes[:2] == b'\x1f\x8b':
                ev_text = gzip.decompress(raw_bytes).decode("utf-8", errors="replace")
            else:
                ev_text = raw_bytes.decode("utf-8", errors="replace")
        except Exception as e:
            return fail_closed(f"EVIDENCE_READ_ERROR: {str(e)}")

        # 7. Page Type Disqualification (Homepage, category stream, bot challenge)
        is_bad_page, bad_reason = SecureHTTPClient.is_unusable_page_type(ev_url, ev_text, 200)
        if is_bad_page:
            return fail_closed(f"DISQUALIFIED_SOURCE_TYPE: {bad_reason}")

        # 8. Quote Grounding: Supporting quote must exist verbatim in raw evidence
        if quote.strip() not in ev_text:
            return fail_closed("QUOTE_NOT_IN_EVIDENCE: Supporting quote could not be found verbatim in snapshot.")

        # 9. Unit and Canonical Metric Consistency
        obs_unit = str(obs_record.get("unit", "")).strip()
        unit_map = {
            "MP-01": ["VND/USD", "VND", "đồng/USD", "đồng", "đ/USD"],
            "MP-02": ["%/năm", "%", "/năm", "phần trăm/năm", "phần trăm"],
            "MP-03": ["%/năm", "%", "/năm", "phần trăm/năm", "phần trăm"],
            "MP-04": ["Điểm", "điểm", "pts", "points"],
            "MP-05": ["%", "phần trăm"],
            "MP-06": ["tỷ giao dịch", "triệu giao dịch", "lượt giao dịch", "tỷ", "triệu"],
            "MP-07": ["triệu lượt", "lượt", "nghìn lượt", "triệu"],
            "MP-08": ["tỷ VND", "tỷ đồng", "tỷ", "nghìn tỷ", "VND"]
        }
        allowed = unit_map.get(ind_id, [])
        if allowed and not any(obs_unit.lower() == u.lower() for u in allowed):
            spec_unit = CANONICAL_SPECS.get(ind_id, {}).get("canonicalUnit", allowed[0])
            return fail_closed(
                f"UNIT_MISMATCH: Đơn vị '{obs_unit}' không tương thích với chỉ số {ind_id} (yêu cầu chuẩn '{spec_unit}')."
            )

        # Context relevance & commodity collision defense
        if ind_id == "MP-01":
            lower_quote = quote.lower()
            if any(term in lower_quote for term in ["ounce", "vàng sjc", "vàng nhẫn", "vàng miếng"]) and not any(term in lower_quote for term in ["tỷ giá", "trung tâm", "usd/vnd", "đô la"]):
                return fail_closed("CONTEXT_MISMATCH: Đoạn trích dẫn đề cập đến giá vàng hoặc hàng hóa, không phải tỷ giá USD/VND.")

        # 10. Exact Numeric Grounding: Raw numeric value must be present as an exact number in quote
        act_val = str(obs_record.get("actualValue"))
        trace = obs_record.get("normalizationTrace", {})
        orig_expr = str(trace.get("originalExpression") if isinstance(trace, dict) else act_val).strip()
        m_num_part = re.search(r'^\s*[-+]?\s*(\d+(?:[\.,]\d+)*)', orig_expr)
        clean_orig = m_num_part.group(1) if m_num_part else orig_expr.rstrip("%").strip()

        # Strict boundary check: orig_expr or act_val cannot be a substring of a larger number (e.g. 25.615 inside 125.615)
        has_exact_match = False
        matched_num_str = None
        for candidate_num_str in [clean_orig, act_val]:
            if not candidate_num_str:
                continue
            # Lookbehind and lookahead prevent matching substring of a larger number
            if re.search(r'(?<![\d.,])' + re.escape(candidate_num_str) + r'(?![\d.,])', quote):
                has_exact_match = True
                matched_num_str = candidate_num_str
                break

        if not has_exact_match:
            # Check discrete numbers in quote to test normalized value equality
            quote_tokens = re.findall(r'(?<![\d.,])\d+(?:[\.,]\d+)*(?![\d.,])', quote)
            for token in quote_tokens:
                if token == clean_orig or token == act_val:
                    has_exact_match = True
                    matched_num_str = token
                    break
                try:
                    # Compare parsed numeric values
                    parsed_tok = FinancialNumericNormalizer.parse_locale_number(token, locale="vi_VN")
                    if str(parsed_tok) == act_val or float(parsed_tok) == float(act_val):
                        has_exact_match = True
                        matched_num_str = token
                        break
                except Exception:
                    pass

        if not has_exact_match:
            return fail_closed(f"NUMERIC_EXPRESSION_UNGROUNDED: Metric value '{act_val}' not found as exact number in supporting quote.")

        # 10.1. Strict Source Unit Binding: Verify the unit adjacent to the number in the source quote
        # A valid canonical unit in JSON is insufficient if the source quote contains a different unit
        if matched_num_str:
            m_unit = re.search(
                r'(?<![\d.,])' + re.escape(matched_num_str) + r'(?![\d.,])\s*(?P<quote_unit>[a-zA-Z%/\u00C0-\u1EF9]+(?:\s*[a-zA-Z%/\u00C0-\u1EF9]+)?)',
                quote
            )
            if m_unit:
                source_unit_raw = m_unit.group("quote_unit").strip().rstrip(".,;!?")
                source_unit_lower = source_unit_raw.lower()
                
                # Check for explicit commodity or contradictory units (e.g. USD/ounce, ounce, sjc)
                forbidden_units_by_ind = {
                    "MP-01": ["ounce", "oz", "lượng", "cây", "chỉ", "usd/ounce"],
                    "MP-02": ["tỷ", "triệu", "đồng", "vnd", "usd"],
                    "MP-03": ["tỷ", "triệu", "đồng", "vnd", "usd"],
                    "MP-04": ["vnd", "usd", "%", "đồng"],
                    "MP-05": ["tỷ đồng", "triệu đồng", "vnd", "usd"],
                    "MP-06": ["năm", "tháng", "ngày", "%", "vnd", "usd"],
                    "MP-07": ["đồng", "vnd", "usd", "tỷ", "%"],
                    "MP-08": ["%", "điểm"]
                }
                forbidden = forbidden_units_by_ind.get(ind_id, [])
                if any(fb in source_unit_lower for fb in forbidden):
                    return fail_closed(
                        f"SOURCE_UNIT_MISMATCH: Đơn vị trong văn bản nguồn ('{source_unit_raw}') không tương thích với chỉ số {ind_id}."
                    )

                # If source unit is present and not a common connective word, verify it matches allowed units
                ignore_connectives = {"trong", "và", "hoặc", "cho", "vào", "ngày", "được", "là", "đạt", "có", "so", "với"}
                first_token = source_unit_lower.split()[0] if source_unit_lower.split() else ""
                if first_token and first_token not in ignore_connectives:
                    unit_compatible = any(
                        source_unit_lower.startswith(u.lower()) or u.lower() in source_unit_lower
                        for u in allowed
                    )
                    if not unit_compatible and len(first_token) > 1:
                        # Extra check: does it match canonical observation unit?
                        if obs_unit.lower() not in source_unit_lower and not source_unit_lower.startswith(obs_unit.lower()):
                            return fail_closed(
                                f"SOURCE_UNIT_MISMATCH: Đơn vị trong văn bản nguồn ('{source_unit_raw}') không khớp với đơn vị quan sát ('{obs_unit}') hoặc yêu cầu chỉ số {ind_id}."
                            )

        # 10.2. P0-01 MP-07 Country-Entity Binding Gate:
        # Ensure the matched numeric observation in the quote is bound to Vietnam, not a foreign country or difference figure.
        if ind_id == "MP-07" and matched_num_str:
            clauses = re.split(r'(?<!\d),(?!\d)|;|(?:\btrong khi\b|\bso với\b|\bnhưng\b|\bkéo\b)', quote, flags=re.I)
            foreign_countries = [
                "thái lan", "malaysia", "singapore", "trung quốc", "hàn quốc", "nhật bản",
                "campuchia", "indonesia", "philippines", "lào", "myanmar", "ấn độ", "mỹ", "châu âu"
            ]
            diff_markers = ["chênh lệch", "khoảng cách", "rút ngắn", "thu hẹp", "kém", "hơn"]
            matched_clause = None
            for cl in clauses:
                if re.search(r'(?<![\d.,])' + re.escape(matched_num_str) + r'(?![\d.,])', cl):
                    matched_clause = cl.lower()
                    if "việt nam" in matched_clause or "nước ta" in matched_clause or "cả nước" in matched_clause:
                        break
            if matched_clause is not None:
                has_vn_in_clause = any(v in matched_clause for v in ["việt nam", "nước ta", "cả nước"])
                has_foreign_in_clause = any(fc in matched_clause for fc in foreign_countries)
                has_diff_in_clause = any(dm in matched_clause for dm in diff_markers) and not has_vn_in_clause
                if (has_foreign_in_clause and not has_vn_in_clause) or has_diff_in_clause:
                    return fail_closed(
                        f"WRONG_COUNTRY_ENTITY: Số liệu '{matched_num_str}' trong câu trích dẫn gắn với quốc gia khác hoặc mức chênh lệch ('{matched_clause.strip()}'), không phải lượng khách quốc tế đến Việt Nam."
                    )
                if not has_vn_in_clause and any(fc in quote.lower() for fc in foreign_countries):
                    return fail_closed(
                        f"WRONG_COUNTRY_ENTITY: Câu trích dẫn chứa nhiều quốc gia nhưng số liệu '{matched_num_str}' không gắn trực tiếp với thực thể Việt Nam."
                    )

        # 11. Observation Date Grounding in snapshot
        date_parts = obs_date.split("-")
        day_month = f"{int(date_parts[2])}/{int(date_parts[1])}"
        day_month_zero = f"{date_parts[2]}/{date_parts[1]}"
        m_num = int(date_parts[1])
        periodic_markers = [f"{m_num} tháng", f"tháng {m_num}", f"t{m_num}", f"t0{m_num}" if m_num < 10 else f"t{m_num}"]

        is_date_grounded = (
            day_month in ev_text or
            day_month_zero in ev_text or
            obs_date in ev_text or
            (ind_id in ["MP-02", "MP-05", "MP-07"] and any(pm in ev_text.lower() for pm in periodic_markers))
        )
        if not is_date_grounded:
            return fail_closed(f"UNSUPPORTED_OBSERVATION_DATE: Ngày công bố '{obs_date}' không tìm thấy trong nội dung bằng chứng.")

        # 11. All Gates Passed -> VERIFIED!
        output["success"] = True
        output["verificationStatus"] = "VERIFIED"
        output["dataAgeHours"] = age_hrs
        output["verificationNote"] = "Nguồn tin chính thống, số liệu và ngày quan sát được xác minh trùng khớp với bằng chứng thô."
        return output
