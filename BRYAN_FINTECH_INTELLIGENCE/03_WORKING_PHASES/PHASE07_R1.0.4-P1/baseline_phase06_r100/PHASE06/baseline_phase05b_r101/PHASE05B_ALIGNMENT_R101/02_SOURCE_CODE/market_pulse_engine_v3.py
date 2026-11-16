#!/usr/bin/env python3
"""
market_pulse_engine_v3.py — Bryan FinTech Intelligence Phase 05B-R1.3
Dynamic Eight-Indicator Market Pulse Engine (Reconstructed Modular Architecture)

Core Mandates:
1. Strict modular separation of concerns:
   - SecureHttpClient: SSRF, DNS pre-resolution, redirect protection.
   - MarketPulseExtractor: Source-specific measurement, unit, and date extraction.
   - FinancialNumericNormalizer: Vietnamese/international locale parsing and unit conversions.
   - MarketPulseValidator: Fact-level evidence, quote grounding, freshness, and scope validation.
   - MarketPulseInterpreter: Authenticated change/direction calculation & 8-point analysis.
2. Complete excision of hardcoded dates, default changes (+5, +2.94%, +13.8%), and SIDEWAYS directions.
3. MP-06 scope protection: rejects total NAPAS volume labelled as VietQR; converts 100M to 0.1B transactions.
4. MP-02 72h ceiling enforced on actual observation date, not runtime timestamp.
5. MP-03 declared bank universe coverage disclosure.
6. MP-08 OMO net injection component reconciliation.
7. 100% compliance with Data Contract V3.0.4.
"""

import os
import sys
import re
import json
import gzip
import html
import socket
import ipaddress
import hashlib
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse

from secure_http_client import SecureHttpClient, TIMEZONE_HCM
from financial_numeric_normalizer import FinancialNumericNormalizer
from market_pulse_extractor import MarketPulseExtractor
from market_pulse_validator import MarketPulseValidator, CANONICAL_SPECS, load_canonical_specs
from market_pulse_interpreter import MarketPulseInterpreter
from market_pulse_discovery import MarketPulseDiscoveryEngine, INDICATOR_SEARCH_PROFILES

_KEY_MAP = {
    "MP-01": "usdVndCenter",
    "MP-02": "overnightInterbankRate",
    "MP-03": "maxDeposit12M",
    "MP-04": "vnIndex",
    "MP-05": "creditGrowth",
    "MP-06": "vietqrVolume",
    "MP-07": "inboundTourists",
    "MP-08": "omoNetAbsorption",
}


def _load_indicator_specs(specs_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Loads canonical indicator specifications via the single source of truth
    (03_INDICATOR_CONFIG/market_pulse_indicator_specs.json).
    Fails clearly with CONFIGURATION_INVALID if missing or invalid; never silently falls back to embedded defaults.
    """
    indicators = load_canonical_specs(specs_path) if specs_path is not None else CANONICAL_SPECS
    if not indicators or not isinstance(indicators, dict):
        raise RuntimeError(
            "CONFIGURATION_INVALID: Canonical indicator specifications could not be loaded from 03_INDICATOR_CONFIG/market_pulse_indicator_specs.json."
        )
    specs = {}
    for k, v in indicators.items():
        specs[k] = {
            "name": v.get("indicatorName"),
            "key": _KEY_MAP.get(k, k),
            "updateFrequency": v.get("updateFrequency"),
            "unit": v.get("canonicalUnit"),
            "maxDataAgeHours": float(v.get("freshnessMaxAgeHours")),
            "allowedPublishers": list(v.get("approvedDomains", [])),
        }
    return specs


# 8 Canonical Indicator Specifications (Unified Single Source of Truth — No Silent Fallback)
INDICATOR_SPECS = _load_indicator_specs()


def compute_file_sha256(filepath: str) -> Optional[str]:
    """Computes byte-level SHA-256 directly from file on disk."""
    if not os.path.exists(filepath):
        return None
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest().lower()


def parse_iso_or_vietnamese_date(ts_str: str) -> Optional[datetime]:
    """Parses date or datetime string into timezone-aware datetime."""
    if not ts_str:
        return None
    try:
        clean = html.unescape(ts_str.strip())
        if clean.endswith("Z"):
            return datetime.fromisoformat(clean[:-1]).replace(tzinfo=timezone.utc).astimezone(TIMEZONE_HCM)
        dt = datetime.fromisoformat(clean)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=TIMEZONE_HCM)
        return dt.astimezone(TIMEZONE_HCM)
    except ValueError:
        pass

    for fmt in ["%d/%m/%Y %H:%M:%S", "%d/%m/%Y %H:%M", "%d/%m/%Y", "%Y-%m-%d"]:
        try:
            dt = datetime.strptime(ts_str.strip(), fmt)
            dt = dt.replace(tzinfo=TIMEZONE_HCM)
            return dt
        except ValueError:
            continue

    return None


class MarketPulseEngine:
    """
    Modular Dynamic Market Pulse Engine V3.0 (Phase 05B-R1.3)
    Zero-trust collection, extraction, validation, and interpretation.
    """

    def __init__(self, raw_evidence_dir: str, run_timestamp: str = None,
                 http_timeout: int = 10, test_mode: bool = False):
        self.raw_evidence_dir = raw_evidence_dir
        os.makedirs(raw_evidence_dir, exist_ok=True)
        self.http_timeout = http_timeout
        self.test_mode = test_mode
        self.http_retrieval_ledger = {}
        self.http_client = SecureHttpClient(test_mode=self.test_mode)

        if run_timestamp:
            self.run_timestamp = parse_iso_or_vietnamese_date(run_timestamp)
        else:
            self.run_timestamp = datetime.now(TIMEZONE_HCM)

        self.discovery_engine = MarketPulseDiscoveryEngine(
            raw_evidence_dir=self.raw_evidence_dir,
            run_timestamp=self.run_timestamp.isoformat(),
            test_mode=self.test_mode
        )

    def fetch_indicator_http(self, url: str, allowed_publishers: list = None) -> dict:
        """Executes secure HTTP retrieval via SecureHttpClient."""
        return self.http_client.get(url, allowed_publishers, timeout=self.http_timeout)

    def decode_content_text(self, raw_bytes: bytes) -> str:
        """Safely decodes raw wire bytes, handling gzip compression and HTML entities."""
        if not raw_bytes:
            return ""
        if raw_bytes[:2] == b'\x1f\x8b':
            try:
                decomp = gzip.decompress(raw_bytes)
                text = decomp.decode("utf-8", errors="replace")
            except Exception:
                text = raw_bytes.decode("utf-8", errors="replace")
        else:
            text = raw_bytes.decode("utf-8", errors="replace")
        return html.unescape(text)

    def extract_indicator_measurement(self, ind_id: str, html_text: str, source_url: str = "", raw_bytes: bytes = b"") -> dict:
        """Delegates autonomous extraction to MarketPulseExtractor."""
        if ind_id == "MP-01":
            return MarketPulseExtractor.extract_mp01_central_rate(html_text, raw_bytes=raw_bytes)
        elif ind_id == "MP-02":
            return MarketPulseExtractor.extract_mp02_interbank_rate(html_text, raw_bytes=raw_bytes)
        elif ind_id == "MP-03":
            return MarketPulseExtractor.extract_mp03_deposit_rate(html_text, raw_bytes=raw_bytes, source_url=source_url)
        elif ind_id == "MP-04":
            return MarketPulseExtractor.extract_mp04_vnindex(html_text, raw_bytes=raw_bytes)
        elif ind_id == "MP-05":
            return MarketPulseExtractor.extract_mp05_credit_growth(html_text, raw_bytes=raw_bytes)
        elif ind_id == "MP-06":
            return MarketPulseExtractor.extract_mp06_vietqr_volume(html_text, raw_bytes=raw_bytes)
        elif ind_id == "MP-07":
            return MarketPulseExtractor.extract_mp07_tourist_arrivals(html_text, raw_bytes=raw_bytes)
        elif ind_id == "MP-08":
            return MarketPulseExtractor.extract_mp08_omo_operations(html_text, raw_bytes=raw_bytes)
        return {"success": False, "unverifiedReason": f"Không có bộ trích xuất cho {ind_id}."}

    def collect_live_indicator(self, ind_id: str, target_url: str,
                              is_synthetic: bool = False,
                              extracted_value=None,  # Deprecated / ignored
                              obs_date: str = None,   # Deprecated / ignored
                              obs_timestamp: str = None, # Deprecated / ignored
                              interpretation: str = None, # Deprecated / ignored
                              is_total_napas: bool = False, # Deprecated / ignored
                              previous_value: Optional[float] = None) -> dict:
        """
        Executes genuine end-to-end collection, extraction, validation, and interpretation.
        Orchestrator parameter overrides are strictly ignored.
        """
        if ind_id not in INDICATOR_SPECS:
            raise ValueError(f"Unknown indicator ID: {ind_id}")

        spec = INDICATOR_SPECS[ind_id]
        ind_name = spec["name"]
        unit = spec["unit"]
        allowed_publishers = spec["allowedPublishers"]

        # Reject synthetic local evidence
        if is_synthetic or not target_url:
            return {
                "indicatorId": ind_id,
                "indicatorName": ind_name,
                "verificationStatus": "UNVERIFIED",
                "updateFrequency": spec["updateFrequency"],
                "unit": unit,
                "interpretation": f"Theo dõi chỉ số {ind_name}.",
                "verificationNote": "Synthetic local evidence without authentic HTTP retrieval rejected.",
                "lastCheckedAt": self.run_timestamp.isoformat(),
                "observationDate": None,
                "observationTimestamp": None,
                "actualValue": None
            }

        # 1. Fetch over HTTP with security controls
        res = self.fetch_indicator_http(target_url, allowed_publishers)
        self.http_retrieval_ledger[target_url] = {
            "statusCode": res["statusCode"],
            "originalUrl": res["originalUrl"],
            "finalUrl": res["finalUrl"],
            "retrievedAt": res["retrievedAt"],
            "byteLength": len(res.get("originalBytes", b"")),
            "responseSha256": res["responseSha256"],
            "error": res["error"]
        }

        code = res["statusCode"]
        final_url = res["finalUrl"]
        raw_bytes = res["originalBytes"]
        sha256 = res["responseSha256"]

        # Check HTTP Status and retrieval errors
        if code != 200 or not raw_bytes:
            return {
                "indicatorId": ind_id,
                "indicatorName": ind_name,
                "verificationStatus": "UNVERIFIED",
                "updateFrequency": spec["updateFrequency"],
                "unit": unit,
                "interpretation": f"Theo dõi chỉ số {ind_name}.",
                "verificationNote": f"Nguồn dữ liệu không thể truy cập qua HTTP (Status: {code}, Lỗi: {res['error']}).",
                "lastCheckedAt": self.run_timestamp.isoformat(),
                "retrievedAt": res.get("retrievedAt", self.run_timestamp.isoformat()),
                "observationDate": None,
                "observationTimestamp": None,
                "actualValue": None
            }

        # 2. Preserve raw wire bytes to disk under raw_evidence_store/market_pulse/MP-XX/
        ind_dir = os.path.join(self.raw_evidence_dir, "market_pulse", ind_id.replace("-", ""))
        os.makedirs(ind_dir, exist_ok=True)
        snapshot_filename = f"evidence_{ind_id.lower().replace('-', '')}_{sha256[:10]}.html"
        snapshot_path = os.path.join(ind_dir, snapshot_filename)
        with open(snapshot_path, "wb") as sf:
            sf.write(raw_bytes)

        # 3. Decode content text
        content_text = self.decode_content_text(raw_bytes)

        # 4. Extract measurement autonomously from content
        ext_res = self.extract_indicator_measurement(ind_id, content_text, final_url, raw_bytes=raw_bytes)

        parsed_final = urlparse(final_url)
        pub_host = (parsed_final.hostname or "").lower()

        # Build candidate observation dictionary with strict timestamp separation
        obs_record = {
            "indicatorId": ind_id,
            "indicatorName": ind_name,
            "success": ext_res.get("success", False),
            "unverifiedReason": ext_res.get("unverifiedReason"),
            "actualValue": ext_res.get("actualValue"),
            "unit": ext_res.get("unit", unit),
            "updateFrequency": spec["updateFrequency"],
            "observationDate": ext_res.get("observationDate"),
            "observationTimestamp": ext_res.get("observationTimestamp"),
            "publishedAt": ext_res.get("publishedAt"),
            "retrievedAt": res["retrievedAt"],
            "lastCheckedAt": self.run_timestamp.isoformat(),
            "observationPeriod": ext_res.get("observationPeriod") or "Kỳ báo cáo",
            "sourcePublisher": pub_host,
            "sourceUrl": final_url,
            "evidencePath": snapshot_path,
            "evidenceSha256": sha256,
            "supportingQuote": ext_res.get("supportingQuote"),
            "bankName": ext_res.get("bankName"),
            "change": ext_res.get("change"),
            "direction": ext_res.get("direction", "UNKNOWN"),
            "normalizationTrace": ext_res.get("normalizationTrace")
        }

        # 5. Validate observation factually via MarketPulseValidator
        val_res = MarketPulseValidator.validate_indicator_observation(ind_id, obs_record, self.run_timestamp)

        # 6. Ensure strict contract consistency and analytical interpretation
        rel_snapshot_path = os.path.join("raw_evidence_store", "market_pulse", ind_id.replace("-", "").lower(), snapshot_filename)
        val_res["evidencePath"] = rel_snapshot_path
        val_res["publishedAt"] = obs_record.get("publishedAt")
        val_res["publisher"] = pub_host

        if val_res.get("verificationStatus") == "VERIFIED" and val_res.get("actualValue") is not None:
            val_res["success"] = True
            val_res["updateStatus"] = "NUMERIC_VALUE_VERIFIED"
            val_res["latestUpdateTitle"] = f"Cập nhật {ind_name}"
            val_res["latestUpdateSummary"] = val_res.get("supportingQuote") or f"Chỉ số {ind_name} ghi nhận {val_res.get('actualValue')} {val_res.get('unit')}."
            interp = MarketPulseInterpreter.generate_indicator_interpretation(val_res, previous_value)
            val_res["interpretation"] = interp["summary"]
            val_res["analyticalDetails"] = interp
        else:
            val_res["success"] = False
            val_res["actualValue"] = None
            val_res["observationDate"] = None
            val_res["observationTimestamp"] = None
            val_res["change"] = None
            val_res["direction"] = "UNKNOWN"
            val_res["updateStatus"] = "QUALITATIVE_UPDATE_ONLY" if ext_res.get("supportingQuote") else "NO_RECENT_UPDATE_FOUND"
            val_res["latestUpdateTitle"] = f"Theo dõi chỉ số {ind_name}"
            val_res["latestUpdateSummary"] = val_res.get("verificationNote") or f"Diễn biến thị trường {ind_name}."
            val_res["interpretation"] = f"Theo dõi chỉ số {ind_name}."

        return val_res

    def discover_live_indicator(self, ind_id: str, candidate_pool: list = None, previous_value: float = None, search_requests_audit: list = None) -> dict:
        """
        Executes genuine search & scan discovery for an indicator:
        Ranks candidates by relevance and recency, fetches top candidate,
        and returns simplified Market Pulse record.
        """
        if candidate_pool is None:
            candidate_pool = []
        return self.discovery_engine.discover_and_evaluate(ind_id, candidate_pool, previous_value, search_requests_audit=search_requests_audit)

    def resolve_evidence_file(self, evidence_path: str) -> Optional[str]:
        """Resolves relative or absolute path of evidence snapshot."""
        if not evidence_path:
            return None
        if os.path.isabs(evidence_path) and os.path.exists(evidence_path):
            return evidence_path
        # Try relative to raw_evidence_dir
        cand1 = os.path.join(self.raw_evidence_dir, evidence_path)
        if os.path.exists(cand1):
            return cand1
        # Try basename in raw_evidence_dir
        cand2 = os.path.join(self.raw_evidence_dir, os.path.basename(evidence_path))
        if os.path.exists(cand2):
            return cand2
        return evidence_path

    def evaluate_indicator(self, raw_indicator: dict) -> dict:
        """
        Validates an existing indicator dictionary against V3.0.4 contract rules.
        Maintains backwards compatibility for unit tests.
        """
        ind_id = raw_indicator.get("indicatorId")
        if ind_id not in INDICATOR_SPECS:
            raise ValueError(f"Invalid indicator ID '{ind_id}'. Must be one of {list(INDICATOR_SPECS.keys())}")

        spec = INDICATOR_SPECS[ind_id]
        ind_name = raw_indicator.get("indicatorName") or spec["name"]
        status = raw_indicator.get("verificationStatus", "UNVERIFIED")

        output = {
            "indicatorId": ind_id,
            "indicatorName": ind_name,
            "verificationStatus": status,
            "updateFrequency": spec["updateFrequency"],
            "interpretation": raw_indicator.get("interpretation", f"Theo dõi chỉ số {ind_name}.")
        }

        if "unit" in raw_indicator:
            output["unit"] = raw_indicator["unit"]
        elif "unit" in spec:
            output["unit"] = spec["unit"]

        if "observationPeriod" in raw_indicator:
            output["observationPeriod"] = raw_indicator["observationPeriod"]
        if "observationDate" in raw_indicator:
            output["observationDate"] = raw_indicator["observationDate"]
        if "previousValue" in raw_indicator:
            output["previousValue"] = raw_indicator["previousValue"]
        if "change" in raw_indicator:
            output["change"] = raw_indicator["change"]

        if status == "VERIFIED":
            obs_ts_str = raw_indicator.get("observationTimestamp")
            if not obs_ts_str:
                output["verificationStatus"] = "UNVERIFIED"
                output["verificationNote"] = "Downgraded from VERIFIED: missing required observationTimestamp."
                output["lastCheckedAt"] = self.run_timestamp.isoformat()
                output["actualValue"] = None
                return output

            obs_dt = parse_iso_or_vietnamese_date(obs_ts_str)
            if not obs_dt:
                output["verificationStatus"] = "UNVERIFIED"
                output["verificationNote"] = f"Downgraded from VERIFIED: unparseable observationTimestamp '{obs_ts_str}'."
                output["lastCheckedAt"] = self.run_timestamp.isoformat()
                output["actualValue"] = None
                return output

            data_age_hours = (self.run_timestamp - obs_dt).total_seconds() / 3600.0
            if data_age_hours < -0.001:
                output["verificationStatus"] = "UNVERIFIED"
                output["verificationNote"] = f"Downgraded from VERIFIED: observationTimestamp is in the future ({obs_ts_str})."
                output["lastCheckedAt"] = self.run_timestamp.isoformat()
                output["actualValue"] = None
                return output

            max_age = spec.get("maxDataAgeHours")
            if max_age and data_age_hours > max_age:
                output["verificationStatus"] = "UNVERIFIED"
                output["verificationNote"] = f"Downgraded from VERIFIED: observation exceeds maximum allowable age of {max_age} hours (current age: {data_age_hours:.1f} hours)."
                output["lastCheckedAt"] = self.run_timestamp.isoformat()
                output["actualValue"] = None
                return output

            output["dataAgeHours"] = round(data_age_hours, 1)

            for req in ["actualValue", "sourcePublisher", "sourceUrl", "evidencePath", "evidenceSha256"]:
                if req not in raw_indicator or raw_indicator[req] is None:
                    output["verificationStatus"] = "UNVERIFIED"
                    output["verificationNote"] = f"Downgraded from VERIFIED: missing required attribute '{req}'."
                    output["lastCheckedAt"] = self.run_timestamp.isoformat()
                    output["actualValue"] = None
                    return output
                output[req] = raw_indicator[req]

            ev_path = raw_indicator["evidencePath"]
            resolved_ev_path = self.resolve_evidence_file(ev_path)
            if not resolved_ev_path or not os.path.exists(resolved_ev_path):
                output["verificationStatus"] = "UNVERIFIED"
                output["verificationNote"] = f"Downgraded from VERIFIED: evidence file not found at '{ev_path}'."
                output["lastCheckedAt"] = self.run_timestamp.isoformat()
                output["actualValue"] = None
                return output

            actual_sha = compute_file_sha256(resolved_ev_path)
            expected_sha = raw_indicator["evidenceSha256"].lower()
            if actual_sha != expected_sha:
                output["verificationStatus"] = "UNVERIFIED"
                output["verificationNote"] = f"Downgraded from VERIFIED: evidence SHA-256 mismatch (expected '{expected_sha}', computed '{actual_sha}')."
                output["lastCheckedAt"] = self.run_timestamp.isoformat()
                output["actualValue"] = None
                return output

            # MP-06 macroeconomic scope separation check
            if ind_id == "MP-06":
                content_lower = ""
                try:
                    with open(resolved_ev_path, "r", encoding="utf-8", errors="ignore") as ef:
                        content_lower = ef.read().lower()
                except Exception:
                    pass
                interp_lower = str(raw_indicator.get("interpretation", "")).lower()
                try:
                    val_float = float(str(raw_indicator.get("actualValue", "0")).replace(",", ".").split()[0])
                except (ValueError, IndexError):
                    val_float = 0.0
                if "toàn hệ thống" in content_lower or "toàn hệ thống" in interp_lower or "atm" in content_lower or val_float >= 10.0:
                    output["verificationStatus"] = "UNVERIFIED"
                    output["verificationNote"] = "Chuyển sang UNVERIFIED: Số liệu phản ánh tổng sản lượng toàn hệ thống NAPAS (>10 tỷ giao dịch bao gồm ATM, POS, chuyển khoản), không phải riêng sản lượng giao dịch VietQR."
                    output["lastCheckedAt"] = self.run_timestamp.isoformat()
                    output["actualValue"] = None
                    return output

            output["observationTimestamp"] = raw_indicator["observationTimestamp"]
            if "observationPeriod" in raw_indicator:
                output["observationPeriod"] = raw_indicator["observationPeriod"]
            return output

        else:
            note = raw_indicator.get("verificationNote")
            if not note:
                output["verificationNote"] = f"Chỉ số {ind_name} hiện chưa xác thực được nguồn tin chính thống."
            else:
                output["verificationNote"] = note

            last_checked = raw_indicator.get("lastCheckedAt") or self.run_timestamp.isoformat()
            output["lastCheckedAt"] = last_checked
            output["actualValue"] = None
            return output
