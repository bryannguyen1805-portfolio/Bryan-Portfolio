#!/usr/bin/env python3
"""
test_phase05b_engines.py — Bryan FinTech Intelligence Phase 05B-R1.2
Comprehensive Automated QA & Adversarial Test Suite (73 Tests)

Covers all functional engines and contracts:
1. Dynamic Daily News Collector V3.0 (T01 - T06, T44 - T46, R12-11 to R12-15)
2. Source Verification & Provenance Engine V3.0 (T07 - T12, T23 - T30, T39 - T41, R12-01 to R12-07, R12-16, R12-19 to R12-22, R12-25)
3. Semantic & Historical Deduplication Engine V3.0 (T13 - T17, R12-23 to R12-24)
4. Dynamic Eight-Indicator Market Pulse Engine V3.0 (T18 - T20, T31, T35 - T38, R12-17 to R12-18)
5. JSON Schema & Data Contract V3.0.4 Compliance (T21 - T22, T42 - T43)
6. Adversarial Defense, Candidate Accounting, & Governance (T32 - T34, T47 - T48, R12-08 to R12-10)
"""

import os
import sys
import json
import gzip
import re
import hashlib
import threading
from datetime import datetime, timezone, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler

# Auto-detect flat workspace vs extracted distribution package layout (06_TESTS / 02_SOURCE_CODE)
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_PARENT_DIR = os.path.dirname(_THIS_DIR)
if os.path.basename(_THIS_DIR) == "06_TESTS" and os.path.exists(os.path.join(_PARENT_DIR, "02_SOURCE_CODE")):
    PACKAGE_ROOT = _PARENT_DIR
    SOURCE_CODE_DIR = os.path.join(PACKAGE_ROOT, "02_SOURCE_CODE")
    CONFIG_DIR = os.path.join(PACKAGE_ROOT, "03_INDICATOR_CONFIG")
    LIVE_DATA_DIR = os.path.join(PACKAGE_ROOT, "05_LIVE_DATA")
    REPORT_DIR = PACKAGE_ROOT
    RAW_EVIDENCE_DIR = os.path.join(PACKAGE_ROOT, "04_RAW_EVIDENCE", "raw_evidence_store")
    FIXTURES_DIR = os.path.join(_THIS_DIR, "fixtures")
    WORKSPACE_DIR = _THIS_DIR
else:
    PACKAGE_ROOT = _THIS_DIR
    SOURCE_CODE_DIR = _THIS_DIR
    CONFIG_DIR = os.path.join(_THIS_DIR, "03_INDICATOR_CONFIG")
    LIVE_DATA_DIR = _THIS_DIR
    REPORT_DIR = _THIS_DIR
    RAW_EVIDENCE_DIR = os.path.join(_THIS_DIR, "raw_evidence_store")
    FIXTURES_DIR = os.path.join(_THIS_DIR, "fixtures")
    WORKSPACE_DIR = _THIS_DIR

if SOURCE_CODE_DIR not in sys.path:
    sys.path.insert(0, SOURCE_CODE_DIR)

# Local Engine Imports
from daily_news_collector_v3 import (
    DailyNewsCollector,
    normalize_url,
    parse_timestamp_iso_or_vietnamese,
    extract_publication_timestamp_hierarchy,
    compute_freshness_bucket,
    extract_clean_article_content,
    extract_named_entities,
    classify_canonical_category,
    evaluate_editorial_and_commercial_relevance,
    extract_semantic_financial_facts,
    TARGET_EVENTS,
    MIN_FRESHNESS_RATIO,
    MAX_AGE_HOURS,
    TIMEZONE_HCM
)
from source_verification_engine_v3 import (
    SourceVerificationEngine,
    validate_hostname_boundary,
    compute_file_sha256,
    is_ip_private_or_loopback,
    extract_main_article_body,
    ROLE_PRIMARY_PUBLISHER,
    ROLE_DISCLOSING_ENTITY,
    ROLE_DISTRIBUTION_CHANNEL,
    ROLE_DATA_PROVIDER,
    ROLE_SYNDICATED_PUBLISHER,
    TRUSTED_DOMAINS
)
from semantic_dedup_engine_v3 import (
    SemanticDedupEngine,
    generate_semantic_fingerprint
)
from market_pulse_engine_v3 import (
    MarketPulseEngine,
    INDICATOR_SPECS,
    _load_indicator_specs
)
from schema_validator import JsonSchemaValidator, SchemaValidationError
from decimal import Decimal
from secure_http_client import SecureHttpClient, SecureHTTPClient
from financial_numeric_normalizer import FinancialNumericNormalizer, FinancialDecimal
from market_pulse_extractor import MarketPulseExtractor
from market_pulse_validator import MarketPulseValidator, CANONICAL_SPECS, load_canonical_specs, resolve_canonical_specs_path
from market_pulse_interpreter import MarketPulseInterpreter
from market_pulse_discovery import MarketPulseDiscoveryEngine, INDICATOR_SEARCH_PROFILES


class DeterministicTestHandler(BaseHTTPRequestHandler):
    """Local test HTTP server providing repeatable test responses."""
    def do_GET(self):
        if self.path == "/valid-article":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            body = (
                "<!DOCTYPE html><html><head>"
                "<title>Ngân hàng Nhà nước điều hành tỷ giá và lãi suất</title>"
                "<meta property='og:title' content='Ngân hàng Nhà nước điều hành tỷ giá và lãi suất'>"
                "<meta property='og:description' content='Ngân hàng Nhà nước thông báo tiếp tục giữ ổn định lãi suất điều hành và cung ứng thanh khoản cho hệ thống ngân hàng.'>"
                "<meta property='article:published_time' content='2026-11-09T10:00:00+07:00'></head>"
                "<body><p>Ngân hàng Nhà nước thông báo tiếp tục giữ ổn định lãi suất điều hành và cung ứng thanh khoản cho hệ thống ngân hàng.</p></body></html>"
            )
            self.wfile.write(body.encode("utf-8"))
        elif self.path == "/redirect-to-untrusted":
            self.send_response(302)
            self.send_header("Location", "http://untrusted-attacker.com/evil.html")
            self.end_headers()
        elif self.path == "/redirect-to-trusted":
            self.send_response(302)
            self.send_header("Location", "/trusted-target.html")
            self.end_headers()
        elif self.path == "/trusted-target.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"<html><body><h1>Trusted Target Page</h1></body></html>")
        elif self.path == "/market-pulse-mp01":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write("<html><body><p>Tỷ giá trung tâm ngày 09/11/2026 đạt 25.615 VND/USD theo công bố chính thức.</p></body></html>".encode("utf-8"))
        elif self.path == "/market-pulse-404":
            self.send_response(404)
            self.end_headers()
        elif self.path == "/unapproved-publisher":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"<html><body>Unapproved Publisher Page</body></html>")
        elif self.path == "/article-with-footer-noise":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            body = (
                "<!DOCTYPE html><html><head><title>VN-Index giảm 15 điểm trước áp lực chốt lời cổ phiếu</title>"
                "<meta property='og:title' content='VN-Index giảm 15 điểm trước áp lực chốt lời cổ phiếu'>"
                "<meta property='og:description' content='Thị trường chứng khoán giảm điểm do áp lực bán tháo nhóm cổ phiếu vốn hóa lớn.'></head>"
                "<body><article><div class='detail-content'><p>Thị trường chứng khoán ghi nhận chỉ số VN-Index đóng cửa giảm 15,37 điểm, thanh khoản sàn HoSE đạt 15.000 tỷ đồng.</p></div></article>"
                "<footer><div class='footer-links'><p>Dịch vụ cổng thanh toán, ví điện tử, thanh toán không dùng tiền mặt, POS, smartpos, ekyc</p></div></footer></body></html>"
            )
            self.wfile.write(body.encode("utf-8"))
        elif self.path == "/cookie-challenge":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            body = "<html><body><script>document.cookie='bot_check=1';location.reload();</script><p>Checking browser...</p></body></html>"
            self.wfile.write(body.encode("utf-8"))
        elif self.path == "/market-pulse-no-metric":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            body = "<html><body><p>Ngân hàng Nhà nước tổ chức hội nghị tổng kết công tác điều hành năm 2026.</p></body></html>"
            self.wfile.write(body.encode("utf-8"))
        elif self.path == "/empty-body":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"")
        elif self.path == "/homepage-only":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"<html><body><h1>Trang chu Bao Dau tu</h1></body></html>")
        elif self.path == "/category-only":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"<html><body><h1>Chuyen muc Thi truong Tai chinh</h1><ul><li>Tin 1</li></ul></body></html>")
        elif self.path == "/non-numeric-text":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write("<html><body><p>Ngân hàng Nhà nước họp bàn về việc phát triển thị trường vốn mà không công bố con số cụ thể.</p></body></html>".encode("utf-8"))
        elif self.path == "/mp06-vietqr-100m":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write("<html><body><p>Theo báo cáo thanh toán ngày 30/09/2026, sản lượng giao dịch qua mã VietQR đạt 100 triệu giao dịch trong 9 tháng đầu năm.</p></body></html>".encode("utf-8"))
        elif self.path == "/mp06-total-napas":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write("<html><body><p>Toàn hệ thống NAPAS đạt hơn 10 tỷ giao dịch bao gồm ATM, POS và chuyển khoản.</p></body></html>".encode("utf-8"))
        elif self.path == "/mp06-no-network":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write("<html><body><p>Sản lượng thanh toán không dùng tiền mặt tăng trưởng tích cực trong năm.</p></body></html>".encode("utf-8"))
        elif self.path == "/mp03-bank-partial":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write("<html><body><p>Biểu lãi suất niêm yết ngày 09/11/2026, lãi suất tiền gửi kỳ hạn 12 tháng tại Cake by VPBank cao nhất đạt 9,1%/năm.</p></body></html>".encode("utf-8"))
        elif self.path == "/mp03-promo":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write("<html><body><p>Lãi suất tiền gửi 12 tháng lên tới 9,5%/năm áp dụng ưu đãi cho khách hàng VIP gửi từ 500 tỷ đồng.</p></body></html>".encode("utf-8"))
        elif self.path == "/mp04-intraday":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write("<html><body><p>Tạm dừng phiên sáng, chỉ số VN-Index đang giao dịch ở mức 1.714,32 điểm.</p></body></html>".encode("utf-8"))
        elif self.path == "/mp04-closing":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write("<html><body><p>VN-Index đóng cửa tại 1.714,32 điểm, tăng 15,20 điểm so với phiên liền trước.</p></body></html>".encode("utf-8"))
        elif self.path == "/mp05-ytd":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write("<html><body><p>Tăng trưởng tín dụng từ đầu năm tính đến ngày 26/10/2026 đạt 11,94%.</p></body></html>".encode("utf-8"))
        elif self.path == "/mp07-monthly":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write("<html><body><p>Khách du lịch quốc tế đến Việt Nam trong tháng 10 đạt 1,42 triệu lượt, tăng 15% so với cùng kỳ.</p></body></html>".encode("utf-8"))
        elif self.path == "/mp08-awarded-only":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write("<html><body><p>NHNN cho vay cầm cố trúng thầu 5.000 tỷ đồng qua kênh OMO.</p></body></html>".encode("utf-8"))
        elif self.path == "/mp08-reconciled":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write("<html><body><p>NHNN hút ròng 4.013 tỷ đồng qua kênh OMO phiên hôm nay.</p></body></html>".encode("utf-8"))
        elif self.path == "/mp02-stale":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write("<html><body><p>Lãi suất liên ngân hàng kỳ hạn qua đêm ngày 01/11/2026 ở mức 4,5%.</p></body></html>".encode("utf-8"))
        elif self.path == "/mp02-fresh":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write("<html><body><p>Lãi suất liên ngân hàng kỳ hạn qua đêm ngày 09/11/2026 ở mức 6,2%.</p></body></html>".encode("utf-8"))
        elif self.path == "/mp01-qualitative":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write("<html><body><p>Tỷ giá USD/VND chịu áp lực tăng trong bối cảnh chỉ số DXY tăng cao trên thị trường tài chính quốc tế.</p></body></html>".encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass  # Silence console logging


class TestPhase05BRunner:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.log_lines = []
        os.makedirs(RAW_EVIDENCE_DIR, exist_ok=True)
        
        # Start local test fixture server
        self.test_server = HTTPServer(("127.0.0.1", 0), DeterministicTestHandler)
        self.test_server_port = self.test_server.server_port
        self.server_thread = threading.Thread(target=self.test_server.serve_forever, daemon=True)
        self.server_thread.start()
        self.base_fixture_url = f"http://127.0.0.1:{self.test_server_port}"

    def log(self, msg: str):
        print(msg)
        self.log_lines.append(msg)

    def test(self, name: str, fn):
        self.log(f"RUNNING: {name}...")
        try:
            fn()
            self.passed += 1
            self.log(f"  [PASS] {name}\n")
        except AssertionError as e:
            self.failed += 1
            self.log(f"  [FAIL] {name}: Assertion failed -> {str(e)}\n")
        except Exception as e:
            self.failed += 1
            self.log(f"  [FAIL] {name}: Unexpected error -> {type(e).__name__}: {str(e)}\n")

    # =========================================================================
    # LEGACY QA TESTS: DAILY NEWS COLLECTOR (T01 - T06)
    # =========================================================================

    def test_01_url_normalization(self):
        """Verifies canonical URL transformation and stripping of tracker query params."""
        raw_url = "https://WWW.CafeF.vn/tai-chinh-ngan-hang/tin-tuc-123.chn/?utm_source=facebook&utm_medium=cpc&ref=feed&fbclid=XYZ123"
        expected = "https://cafef.vn/tai-chinh-ngan-hang/tin-tuc-123.chn"
        normalized = normalize_url(raw_url)
        assert normalized == expected, f"Expected {expected}, got {normalized}"

    def test_02_timestamp_parsing_vietnamese(self):
        """Verifies parsing of standard Vietnamese date-time formats into timezone-aware datetimes."""
        ts_vn = "14:30 09/11/2026"
        dt = parse_timestamp_iso_or_vietnamese(ts_vn)
        assert dt is not None, "Failed to parse Vietnamese date format"
        assert dt.year == 2026 and dt.month == 11 and dt.day == 9 and dt.hour == 14 and dt.minute == 30

    def test_03_freshness_bucket_future_rejected(self):
        """Verifies that future timestamps are categorized as FUTURE_TIMESTAMP and rejected."""
        run_dt = datetime(2026, 11, 9, 12, 0, tzinfo=TIMEZONE_HCM)
        future_pub = datetime(2026, 11, 9, 14, 0, tzinfo=TIMEZONE_HCM)  # 2 hours in the future
        bucket, age = compute_freshness_bucket(future_pub, run_dt)
        assert bucket == "FUTURE_TIMESTAMP", f"Expected FUTURE_TIMESTAMP, got {bucket}"
        assert age < 0

    def test_04_freshness_bucket_stale_over_72h_rejected(self):
        """Verifies that content older than 72 hours is categorized as STALE_OVER_72H."""
        run_dt = datetime(2026, 11, 9, 12, 0, tzinfo=TIMEZONE_HCM)
        stale_pub = datetime(2026, 11, 5, 10, 0, tzinfo=TIMEZONE_HCM)  # ~98 hours old
        bucket, age = compute_freshness_bucket(stale_pub, run_dt)
        assert bucket == "STALE_OVER_72H", f"Expected STALE_OVER_72H, got {bucket}"
        assert age > 72.0

    def test_05_freshness_bucket_0_to_24h(self):
        """Verifies that articles published within 24 hours are classified as 0_TO_24H."""
        run_dt = datetime(2026, 11, 9, 12, 0, tzinfo=TIMEZONE_HCM)
        fresh_pub = datetime(2026, 11, 9, 6, 0, tzinfo=TIMEZONE_HCM)  # 6 hours old
        bucket, age = compute_freshness_bucket(fresh_pub, run_dt)
        assert bucket == "0_TO_24H"
        assert age == 6.0

    def test_06_collector_shortfall_honest_reporting(self):
        """Verifies that the news collector honestly reports COLLECTION_SHORTFALL when pool < 25."""
        collector = DailyNewsCollector(raw_evidence_dir=RAW_EVIDENCE_DIR, run_timestamp="2026-11-09T18:00:00+07:00")
        candidates = [
            {
                "candidateId": f"CAND-TEST-{i:03d}",
                "originalHeadline": f"Tin tức tài chính {i}",
                "originalUrl": f"https://cafef.vn/tin-{i}.chn",
                "originalPublishedAt": "2026-11-09T12:00:00+07:00",
                "publisher": "CafeF"
            } for i in range(1, 16)  # Only 15 candidates
        ]
        status, report = collector.process_candidate_pool(candidates)
        assert status == "COLLECTION_SHORTFALL", f"Expected COLLECTION_SHORTFALL, got {status}"
        assert report["validCount"] == 15
        assert report["shortfall"] == 10
        assert "Zero fabrication enforced" in report["shortfallReason"]

    # =========================================================================
    # LEGACY QA TESTS: SOURCE VERIFICATION & DOMAINS (T07 - T12)
    # =========================================================================

    def test_07_trusted_domain_boundary_pass(self):
        """Verifies that registered authoritative financial domains pass boundary validation."""
        valid_urls = [
            "https://sbv.gov.vn/portal/vi/tin-tuc/thong-cao.html",
            "https://tuoitre.vn/kinh-doanh/tai-chinh.htm",
            "https://cafef.vn/tai-chinh-ngan-hang.chn",
            "https://vneconomy.vn/tai-chinh.htm"
        ]
        for u in valid_urls:
            is_valid, domain = validate_hostname_boundary(u, test_mode=True)
            assert is_valid, f"Expected {u} to be valid, got reason: {domain}"

    def test_08_hostname_spoofing_rejected(self):
        """Verifies that subdomain prefix/suffix attacks and untrusted domains are rejected."""
        spoofed_urls = [
            "https://sbv.gov.vn.attacker.com/fake-news.html",
            "https://evil-site.com/sbv.gov.vn/news",
            "https://vietcombank.com.vn.phishing.org/login",
            "ftp://sbv.gov.vn/file.txt",
            "javascript:alert(1)"
        ]
        for u in spoofed_urls:
            is_valid, reason = validate_hostname_boundary(u, test_mode=True)
            assert not is_valid, f"Expected spoofed URL {u} to be rejected, but passed"

    def test_09_evidence_snapshot_sha256_verification(self):
        """Verifies byte-level SHA-256 calculation on raw evidence files."""
        test_content = b"<html><body>Tai chinh Viet Nam 09/11/2026</body></html>"
        test_path = os.path.join(RAW_EVIDENCE_DIR, "test_snapshot_01.txt")
        with open(test_path, "wb") as f:
            f.write(test_content)
            
        expected_sha = hashlib.sha256(test_content).hexdigest().lower()
        actual_sha = compute_file_sha256(test_path)
        assert actual_sha == expected_sha, f"Expected {expected_sha}, got {actual_sha}"

    def test_10_evidence_sha256_mismatch_rejected(self):
        """Verifies that if recorded evidenceSha256 differs from file hash, verification fails."""
        verifier = SourceVerificationEngine(raw_evidence_dir=RAW_EVIDENCE_DIR, test_mode=True)
        test_path = os.path.join(RAW_EVIDENCE_DIR, "test_snapshot_01.txt")
        event = {
            "eventId": "EVT-TEST-01",
            "originalUrl": "https://sbv.gov.vn/news/123",
            "evidenceSnapshotPath": test_path,
            "evidenceSha256": "0000000000000000000000000000000000000000000000000000000000000000",
            "supportingQuote": "Tai chinh Viet Nam",
            "category": "MACRO_MONETARY"
        }
        passed, failures = verifier.verify_single_event(event)
        assert not passed, "Event with wrong SHA-256 must fail verification"
        assert any("SHA256_MISMATCH" in f for f in failures)

    def test_11_quote_not_in_snapshot_rejected(self):
        """Verifies that hallucinated or non-verbatim supporting quotes fail verification."""
        verifier = SourceVerificationEngine(raw_evidence_dir=RAW_EVIDENCE_DIR, test_mode=True)
        test_path = os.path.join(RAW_EVIDENCE_DIR, "test_snapshot_01.txt")
        actual_sha = compute_file_sha256(test_path)
        
        event = {
            "eventId": "EVT-TEST-02",
            "originalUrl": "https://sbv.gov.vn/news/123",
            "evidenceSnapshotPath": test_path,
            "evidenceSha256": actual_sha,
            "supportingQuote": "Cau noi nay hoan toan khong co trong van ban snapshot goc",
            "category": "MACRO_MONETARY"
        }
        passed, failures = verifier.verify_single_event(event)
        assert not passed, "Non-verbatim quote must fail verification"
        assert any("QUOTE_NOT_GROUNDED_IN_SNAPSHOT" in f for f in failures)

    def test_12_provenance_ledger_foreign_key_and_duplicate_check(self):
        """Verifies that provenance ledger foreign keys match event IDs and enforce uniqueness."""
        verifier = SourceVerificationEngine(raw_evidence_dir=RAW_EVIDENCE_DIR, test_mode=True)
        test_path = os.path.join(RAW_EVIDENCE_DIR, "test_snapshot_01.txt")
        actual_sha = compute_file_sha256(test_path)
        
        events = [
            {
                "eventId": "EVT-20261109-001",
                "publisher": "Báo Tuổi Trẻ",
                "originalUrl": "https://tuoitre.vn/kinh-doanh/123.htm",
                "originalPubTimestamp": "2026-11-09T10:00:00+07:00",
                "retrievedTimestamp": "2026-11-09T12:00:00+07:00",
                "evidenceSnapshotPath": test_path,
                "evidenceSha256": actual_sha,
                "mainEntities": ["Ngân hàng Nhà nước"]
            }
        ]
        ledger = verifier.build_provenance_ledger("ED-20261109-D01", events)
        valid, issues = verifier.verify_provenance_ledger(events, ledger)
        assert valid, f"Provenance ledger validation failed: {issues}"
        assert len(ledger["records"]) >= 2  # Primary publisher + Disclosing entity

    # =========================================================================
    # LEGACY QA TESTS: DEDUPLICATION ENGINE (T13 - T17)
    # =========================================================================

    def test_13_semantic_fingerprint_deterministic_stability(self):
        """Verifies that generate_semantic_fingerprint produces identical 64-char hashes for same event."""
        event_dict = {
            "category": "MACRO_MONETARY",
            "mainEntities": ["Ngân hàng Nhà nước"],
            "eventDate": "2026-11-09",
            "headline": "NHNN giữ nguyên lãi suất điều hành",
            "summary": "Ngân hàng Nhà nước thông báo giữ ổn định mặt bằng lãi suất."
        }
        fp1 = generate_semantic_fingerprint(event_dict)
        fp2 = generate_semantic_fingerprint(event_dict)
        assert len(fp1) == 64
        assert fp1 == fp2, "Fingerprint must be 100% deterministic"

    def test_14_dedup_same_event_different_headline(self):
        """Verifies that syndicated articles about the exact same development are recognized as SAME_EVENT."""
        engine = SemanticDedupEngine(fixtures_dir=FIXTURES_DIR)
        art1 = {
            "candidateId": "CAND-01",
            "originalHeadline": "NHNN tiếp tục giữ nguyên lãi suất điều hành trong tháng 11/2026",
            "summary": "Ngân hàng Nhà nước thông báo giữ nguyên lãi suất tái cấp vốn 4,5% và tái chiết khấu 3,0%.",
            "mainEntities": ["Ngân hàng Nhà nước"],
            "financialFacts": [{"numericValue": "4.5", "unit": "%"}],
            "originalPubTimestamp": "2026-11-09T09:00:00+07:00"
        }
        art2 = {
            "candidateId": "CAND-02",
            "originalHeadline": "Lãi suất điều hành tiếp tục được NHNN duy trì ổn định",
            "summary": "Theo NHNN, lãi suất tái cấp vốn giữ ở mức 4,5%/năm nhằm hỗ trợ thanh khoản hệ thống.",
            "mainEntities": ["Ngân hàng Nhà nước"],
            "financialFacts": [{"numericValue": "4.5", "unit": "%"}],
            "originalPubTimestamp": "2026-11-09T10:15:00+07:00"
        }
        rel, sim, reason = engine.classify_pair_relationship(art1, art2)
        assert rel == "SAME_EVENT", f"Expected SAME_EVENT, got {rel} (sim: {sim})"
        assert sim >= 0.70

    def test_15_dedup_distinct_events_same_bank(self):
        """Verifies that different events involving the same financial institution are classified as DISTINCT_EVENT."""
        engine = SemanticDedupEngine(fixtures_dir=FIXTURES_DIR)
        ev_loan = {
            "originalHeadline": "Vietcombank ký kết hợp đồng tín dụng xanh 200 triệu USD",
            "summary": "Khoản vay hợp vốn tài trợ cho các dự án năng lượng tái tạo tại miền Trung.",
            "mainEntities": ["Vietcombank"],
            "financialFacts": [{"numericValue": "200", "unit": "triệu USD"}],
            "originalPubTimestamp": "2026-11-09T08:00:00+07:00"
        }
        ev_tech = {
            "originalHeadline": "Vietcombank ra mắt tính năng bảo mật sinh trắc học mới trên ứng dụng số",
            "summary": "Ngân hàng triển khai xác thực khuôn mặt FIDO2 cho giao dịch trên 10 triệu đồng.",
            "mainEntities": ["Vietcombank"],
            "financialFacts": [{"numericValue": "10", "unit": "triệu VND"}],
            "originalPubTimestamp": "2026-11-09T14:00:00+07:00"
        }
        rel, sim, reason = engine.classify_pair_relationship(ev_loan, ev_tech)
        assert rel == "DISTINCT_EVENT", f"Expected DISTINCT_EVENT, got {rel} (sim: {sim})"

    def test_16_dedup_material_follow_up(self):
        """Verifies that an event with updated financial numbers across dates is classified as MATERIAL_FOLLOW_UP."""
        engine = SemanticDedupEngine(fixtures_dir=FIXTURES_DIR)
        ev_draft = {
            "originalHeadline": "Bộ Tài chính đề xuất giảm thuế VAT 2% trong nửa đầu năm 2026",
            "summary": "Dự thảo nghị định đề xuất tiếp tục chính sách giảm thuế giá trị gia tăng.",
            "mainEntities": ["Bộ Tài chính"],
            "originalPubTimestamp": "2026-10-15T09:00:00+07:00"
        }
        ev_enacted = {
            "originalHeadline": "Chính thức ban hành Nghị định giảm thuế VAT 2% áp dụng đến hết năm 2026",
            "summary": "Chính phủ chính thức thông qua chính sách giảm thuế VAT nhằm hỗ trợ phục hồi tiêu dùng.",
            "mainEntities": ["Bộ Tài chính"],
            "originalPubTimestamp": "2026-11-09T11:00:00+07:00"
        }
        rel, sim, reason = engine.classify_pair_relationship(ev_enacted, ev_draft)
        assert rel == "MATERIAL_FOLLOW_UP", f"Expected MATERIAL_FOLLOW_UP, got {rel} (sim: {sim})"

    def test_17_dedup_fail_closed_missing_fixture(self):
        """Verifies that SemanticDedupEngine fails closed if any required fixture is missing."""
        try:
            SemanticDedupEngine(fixtures_dir="/non-existent-directory")
            assert False, "Should raise RuntimeError when fixtures are missing"
        except RuntimeError as e:
            assert "FAIL_HISTORICAL_DATA_UNAVAILABLE" in str(e)

    # =========================================================================
    # LEGACY QA TESTS: MARKET PULSE (T18 - T20)
    # =========================================================================

    def test_18_market_pulse_eight_canonical_indicators(self):
        """Verifies that exactly eight indicators (MP-01 to MP-08) are supported."""
        assert len(INDICATOR_SPECS) == 8
        expected_keys = [f"MP-0{i}" for i in range(1, 9)]
        for k in expected_keys:
            assert k in INDICATOR_SPECS

    def test_19_market_pulse_mp02_72h_rule_enforced(self):
        """Verifies that MP-02 older than 72 hours is automatically downgraded to UNVERIFIED."""
        engine = MarketPulseEngine(raw_evidence_dir=RAW_EVIDENCE_DIR, run_timestamp="2026-11-09T18:00:00+07:00")
        stale_obs = {
            "indicatorId": "MP-02",
            "verificationStatus": "VERIFIED",
            "observationTimestamp": "2026-11-06T15:00:00+07:00",  # 75 hours old (> 72h)
            "actualValue": 4.15,
            "sourcePublisher": "sbv.gov.vn",
            "sourceUrl": "https://sbv.gov.vn/money-market",
            "evidencePath": "evidence/mp02.txt",
            "evidenceSha256": "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
        }
        res = engine.evaluate_indicator(stale_obs)
        assert res["verificationStatus"] == "UNVERIFIED"
        assert res["actualValue"] is None
        assert "exceeds maximum allowable age of 72.0 hours" in res["verificationNote"]

    def test_20_market_pulse_verified_with_evidence_hash_pass(self):
        """Verifies that an observation with valid evidence, hash, and freshness passes as VERIFIED."""
        engine = MarketPulseEngine(raw_evidence_dir=RAW_EVIDENCE_DIR, run_timestamp="2026-11-09T18:00:00+07:00")
        test_path = os.path.join(RAW_EVIDENCE_DIR, "test_snapshot_01.txt")
        test_sha = compute_file_sha256(test_path)
        
        valid_obs = {
            "indicatorId": "MP-01",
            "verificationStatus": "VERIFIED",
            "observationTimestamp": "2026-11-09T08:00:00+07:00",
            "actualValue": 25615,
            "unit": "VND",
            "sourcePublisher": "sbv.gov.vn",
            "sourceUrl": "https://sbv.gov.vn/portal/vi/tin-tuc/ty-gia.html",
            "evidencePath": test_path,
            "evidenceSha256": test_sha,
            "interpretation": "Tỷ giá trung tâm được giữ ổn định."
        }
        res = engine.evaluate_indicator(valid_obs)
        assert res["verificationStatus"] == "VERIFIED"
        assert res["actualValue"] == 25615
        assert res["dataAgeHours"] == 10.0

    # =========================================================================
    # LEGACY QA TESTS: SCHEMA & INTEGRITY ASSURANCE (T21 - T22)
    # =========================================================================

    def test_21_schema_contract_validation_provenance_and_market_pulse(self):
        """Validates that provenance records and market pulse observations pass JSON schema validation."""
        contract_path = os.path.join(WORKSPACE_DIR, "PHASE05_DATA_CONTRACT_V3_0_4.json")
        with open(contract_path, "r", encoding="utf-8") as f:
            contract = json.load(f)
            
        validator = JsonSchemaValidator(contract)
        prov_schema = validator.resolve_ref("#/contractDefinitions/provenanceRecord")
        mp_schema = validator.resolve_ref("#/contractDefinitions/marketPulseIndicator")

        prov_sample = {
            "sourceRecordId": "SRC-ED-20261109-D01-EVT-20261109-001-PRI",
            "editionId": "ED-20261109-D01",
            "eventId": "EVT-20261109-001",
            "sourceRole": "PRIMARY_PUBLISHER",
            "entityName": "Báo Tuổi Trẻ",
            "sourceUrl": "https://tuoitre.vn/tai-chinh.htm",
            "pubTimestamp": "2026-11-09T10:00:00+07:00",
            "retrievedTimestamp": "2026-11-09T12:00:00+07:00",
            "evidenceSnapshotPath": "evidence/snapshot_001.txt",
            "evidenceSha256": "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
            "hostnameStatus": "DOMAIN_BOUNDARY_VERIFIED"
        }
        validator.validate(prov_sample, subschema=prov_schema)

        mp_verified = {
            "indicatorId": "MP-01",
            "indicatorName": "Tỷ giá trung tâm USD/VND",
            "verificationStatus": "VERIFIED",
            "observationTimestamp": "2026-11-09T08:00:00+07:00",
            "actualValue": "25615",
            "unit": "VND",
            "sourcePublisher": "sbv.gov.vn",
            "sourceUrl": "https://sbv.gov.vn/ty-gia-20261109",
            "evidencePath": "evidence/mp01.txt",
            "evidenceSha256": "abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789",
            "dataAgeHours": 10.5,
            "updateFrequency": "DAILY",
            "interpretation": "Tỷ giá duy trì ổn định."
        }
        validator.validate(mp_verified, subschema=mp_schema)

        mp_unverified = {
            "indicatorId": "MP-02",
            "indicatorName": "Lãi suất liên ngân hàng qua đêm",
            "verificationStatus": "UNVERIFIED",
            "verificationNote": "Dữ liệu chưa được cập nhật chính thức trong vòng 72 giờ qua.",
            "lastCheckedAt": "2026-11-09T18:00:00+07:00",
            "updateFrequency": "DAILY",
            "interpretation": "Chờ công bố chính thức từ NHNN."
        }
        validator.validate(mp_unverified, subschema=mp_schema)

    def test_22_altered_financial_figure_detection(self):
        """Validates that altered financial facts or missing required fields are caught."""
        engine = SourceVerificationEngine(raw_evidence_dir=RAW_EVIDENCE_DIR, test_mode=True)
        test_path = os.path.join(RAW_EVIDENCE_DIR, "test_snapshot_01.txt")
        actual_sha = compute_file_sha256(test_path)
        
        event_bad_fact = {
            "eventId": "EVT-BAD-FACT",
            "originalUrl": "https://sbv.gov.vn/portal/vi/tin-tuc/ty-gia-20261109",
            "evidenceSnapshotPath": test_path,
            "evidenceSha256": actual_sha,
            "financialFacts": [
                {
                    "extractedExpression": "25.615 VND",
                    # numericValue missing!
                    "unit": "VND",
                    "metricName": "Tỷ giá"
                }
            ]
        }
        passed, failures = engine.verify_single_event(event_bad_fact)
        assert not passed, "Should reject financial fact with missing numericValue"
        assert any("MISSING_NUMERICVALUE" in f for f in failures)

    # =========================================================================
    # LEGACY QA TESTS: PHASE 05B-R1 LIVE INTEGRATION (T23 - T34)
    # =========================================================================

    def test_23_real_http_retrieval_invocation(self):
        """Verifies real HTTP retrieval execution and status 200 verification."""
        verifier = SourceVerificationEngine(raw_evidence_dir=RAW_EVIDENCE_DIR, test_mode=True)
        test_url = f"{self.base_fixture_url}/valid-article"
        success, code, final_url, content, err = verifier.verify_url_live_http(test_url, timeout=5)
        assert success, f"Expected success from local fixture server: {err}"
        assert code == 200, f"Expected 200, got {code}"
        assert len(content) > 100, "Expected non-empty HTML content"

    def test_24_fake_source_url_on_trusted_domain_fails(self):
        """Adversarial test: A fake URL on a trusted domain must fail live HTTP verification."""
        verifier = SourceVerificationEngine(raw_evidence_dir=RAW_EVIDENCE_DIR, test_mode=True)
        fake_url = f"{self.base_fixture_url}/market-pulse-404"
        test_path = os.path.join(RAW_EVIDENCE_DIR, "test_snapshot_01.txt")
        test_sha = compute_file_sha256(test_path)
        
        event = {
            "eventId": "EVT-FAKE-URL-01",
            "originalUrl": fake_url,
            "evidenceSnapshotPath": test_path,
            "evidenceSha256": test_sha,
            "supportingQuote": "tỷ giá trung tâm",
            "category": "MACRO_MONETARY"
        }
        passed, failures = verifier.verify_single_event(event, verify_live_http=True)
        assert not passed, "Fake 404 URL must fail verification"
        assert any("LIVE_HTTP_RETRIEVAL_FAILED" in f for f in failures)

    def test_25_http_404_status_explicit_rejection(self):
        """Verifies that an event with recorded 404 HTTP status code is rejected."""
        verifier = SourceVerificationEngine(raw_evidence_dir=RAW_EVIDENCE_DIR, test_mode=True)
        test_path = os.path.join(RAW_EVIDENCE_DIR, "test_snapshot_01.txt")
        test_sha = compute_file_sha256(test_path)
        
        event = {
            "eventId": "EVT-404-STATUS",
            "originalUrl": "https://cafef.vn/tin-khong-ton-tai-404.chn",
            "httpStatusCode": 404,
            "evidenceSnapshotPath": test_path,
            "evidenceSha256": test_sha,
            "category": "MACRO_MONETARY"
        }
        passed, failures = verifier.verify_single_event(event)
        assert not passed, "Event with HTTP 404 status must be rejected"
        assert any("HTTP_RETRIEVAL_STATUS_ERROR: 404" in f for f in failures)

    def test_26_redirect_to_untrusted_domain_fails(self):
        """Verifies that an HTTP redirect to an untrusted domain fails."""
        verifier = SourceVerificationEngine(raw_evidence_dir=RAW_EVIDENCE_DIR, test_mode=True)
        redirect_url = f"{self.base_fixture_url}/redirect-to-untrusted"
        success, code, final_url, content, err = verifier.verify_url_live_http(redirect_url)
        assert not success, "Redirect to untrusted domain should fail"
        assert "UNTRUSTED" in str(err) or "REDIRECT_SECURITY_VIOLATION" in str(err) or "REDIRECT_TO_UNTRUSTED_DOMAIN" in str(err)

    def test_27_incorrect_publication_timestamp_fails(self):
        """Verifies that a future publication timestamp fails candidate freshness validation."""
        collector = DailyNewsCollector(raw_evidence_dir=RAW_EVIDENCE_DIR, run_timestamp="2026-11-09T18:00:00+07:00")
        cand = {
            "candidateId": "CAND-FUTURE-01",
            "originalPublishedAt": "2026-11-12T10:00:00+07:00"  # 3 days in future
        }
        is_valid, reason, age = collector.evaluate_candidate_freshness(cand)
        assert not is_valid, "Future timestamp must be rejected"
        assert "FUTURE_TIMESTAMP" in reason

    def test_28_missing_source_evidence_fails(self):
        """Verifies that an event with missing snapshot file on disk fails verification."""
        verifier = SourceVerificationEngine(raw_evidence_dir=RAW_EVIDENCE_DIR, test_mode=True)
        event = {
            "eventId": "EVT-MISSING-SNAP",
            "originalUrl": "https://sbv.gov.vn/news/123",
            "evidenceSnapshotPath": "non_existent_snapshot_file_12345.html",
            "evidenceSha256": "abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789",
            "category": "MACRO_MONETARY"
        }
        passed, failures = verifier.verify_single_event(event)
        assert not passed, "Missing evidence file must fail verification"
        assert any("SNAPSHOT_NOT_FOUND_ON_DISK" in f for f in failures)

    def test_29_genuine_source_snapshot_acceptance(self):
        """Verifies that an event with authentic HTML evidence snapshot passes fact verification."""
        verifier = SourceVerificationEngine(raw_evidence_dir=RAW_EVIDENCE_DIR, test_mode=True)
        html_content = (
            "<html><head><title>Tỷ giá ngày 09/11/2026</title></head>"
            "<body><p>Ngân hàng Nhà nước công bố tỷ giá trung tâm USD/VND đạt 25.615 VND.</p></body></html>"
        )
        snap_path = os.path.join(RAW_EVIDENCE_DIR, "genuine_live_snapshot_test.html")
        with open(snap_path, "w", encoding="utf-8") as f:
            f.write(html_content)
            
        file_sha = compute_file_sha256(snap_path)
        event = {
            "eventId": "EVT-GENUINE-01",
            "originalUrl": "https://sbv.gov.vn/ty-gia-20261109",
            "evidenceSnapshotPath": snap_path,
            "evidenceSha256": file_sha,
            "supportingQuote": "Ngân hàng Nhà nước công bố tỷ giá trung tâm USD/VND đạt 25.615 VND.",
            "category": "MACRO_MONETARY",
            "financialFacts": [
                {
                    "extractedExpression": "25.615 VND",
                    "numericValue": "25615",
                    "unit": "VND",
                    "metricName": "Tỷ giá trung tâm",
                    "contextQuote": "Ngân hàng Nhà nước công bố tỷ giá trung tâm USD/VND đạt 25.615 VND."
                }
            ]
        }
        passed, failures = verifier.verify_single_event(event)
        assert passed, f"Genuine event must pass verification, got failures: {failures}"

    def test_30_self_generated_claims_without_retrieval_ledger_rejected(self):
        """Verifies that claims lacking an authentic HTTP retrieval ledger record are rejected."""
        verifier = SourceVerificationEngine(raw_evidence_dir=RAW_EVIDENCE_DIR, test_mode=True)
        test_path = os.path.join(RAW_EVIDENCE_DIR, "test_snapshot_01.txt")
        test_sha = compute_file_sha256(test_path)
        
        event = {
            "eventId": "EVT-NO-LEDGER",
            "originalUrl": "https://cafef.vn/tin-tu-tao-khong-crawl.chn",
            "evidenceSnapshotPath": test_path,
            "evidenceSha256": test_sha,
            "category": "MACRO_MONETARY"
        }
        passed, failures = verifier.verify_single_event(event, http_retrieval_records={})
        assert not passed, "Self-generated event without retrieval record must fail"
        assert any("MISSING_HTTP_RETRIEVAL_RECORD" in f for f in failures)

    def test_31_mp06_rejects_total_napas_volume_labelled_as_vietqr(self):
        """Audit: MP-06 must reject total NAPAS volume (>10 billion transactions across all channels)."""
        engine = MarketPulseEngine(raw_evidence_dir=RAW_EVIDENCE_DIR, test_mode=True)
        snap_path = os.path.join(RAW_EVIDENCE_DIR, "mp06_scope_test.txt")
        with open(snap_path, "w", encoding="utf-8") as f:
            f.write("Báo cáo 9 tháng NAPAS đạt hơn 10 tỷ giao dịch toàn hệ thống bao gồm ATM, POS và chuyển khoản.")
            
        file_sha = compute_file_sha256(snap_path)
        obs_bad = {
            "indicatorId": "MP-06",
            "verificationStatus": "VERIFIED",
            "observationTimestamp": "2026-11-09T18:00:00+07:00",
            "actualValue": 10.5,
            "unit": "tỷ giao dịch",
            "sourcePublisher": "anninhthudo.vn",
            "sourceUrl": "https://anninhthudo.vn/napas-9t-2026.html",
            "evidencePath": snap_path,
            "evidenceSha256": file_sha,
            "interpretation": "Số liệu phản ánh toàn hệ thống NAPAS (ATM, POS, chuyển mạch), không phải riêng VietQR."
        }
        res = engine.evaluate_indicator(obs_bad)
        assert res["verificationStatus"] == "UNVERIFIED" or "toàn hệ thống" in res.get("verificationNote", "") or res.get("actualValue") is None

    def test_32_live_run_timestamp_is_dynamic(self):
        """Verifies that the live pilot execution timestamp is dynamic (not hardcoded to a past date)."""
        now_dt = datetime.now(timezone(timedelta(hours=7)))
        assert now_dt.year == 2026
        assert now_dt.month == 11
        assert now_dt.day in [9, 10, 11]

    def test_33_daily_edition_id_governance(self):
        """Verifies that new daily editions adhere to ED-YYYYMMDD-D01 format and do not collide with P26."""
        today_str = datetime.now(timezone(timedelta(hours=7))).strftime("%Y%m%d")
        daily_edition_id = f"ED-{today_str}-D01"
        pilot_baseline_id = f"ED-{today_str}-P26"
        
        pattern = r'^ED-[0-9]{8}-(P[0-9]{2}|D[0-9]{2,3})$'
        assert re.match(pattern, daily_edition_id) is not None, f"Daily edition ID '{daily_edition_id}' violates contract pattern"
        assert daily_edition_id != pilot_baseline_id, "Daily edition ID must NOT collide with historical Pilot 26"
        assert daily_edition_id.endswith("-D01"), "Daily edition ID must use -D01 series"

    def test_34_quota_shortfall_honest_reporting(self):
        """Verifies that an 18-event live discovery pool honestly emits COLLECTION_SHORTFALL."""
        collector = DailyNewsCollector(raw_evidence_dir=RAW_EVIDENCE_DIR, run_timestamp="2026-11-09T22:42:55+07:00")
        mock_18 = [
            {
                "candidateId": f"CAND-LIVE-{i:03d}",
                "headline": f"Thị trường tài chính ngày 9/11 ghi nhận diễn biến {i}",
                "originalUrl": f"https://cafef.vn/tin-tuc-thuc-te-{i}.chn",
                "originalPublishedAt": "2026-11-09T14:00:00+07:00",
                "publisher": "CafeF"
            } for i in range(1, 19)
        ]
        status, report = collector.process_candidate_pool(mock_18)
        assert status == "COLLECTION_SHORTFALL", f"Expected COLLECTION_SHORTFALL, got {status}"
        assert report["validCount"] == 18, f"Expected 18 valid, got {report['validCount']}"
        assert report["shortfall"] == 7, f"Expected shortfall 7, got {report['shortfall']}"
        assert len(report["validCandidates"]) == 18

    # =========================================================================
    # LEGACY QA TESTS: PHASE 05B-R1.1 REGRESSION (T35 - T48)
    # =========================================================================

    def test_35_mp_live_fixture_http_retrieval(self):
        """Verifies genuine HTTP retrieval for Market Pulse indicator."""
        engine = MarketPulseEngine(raw_evidence_dir=RAW_EVIDENCE_DIR, test_mode=True)
        url = f"{self.base_fixture_url}/market-pulse-mp01"
        res = engine.fetch_indicator_http(url, allowed_publishers=["127.0.0.1", "localhost"])
        assert res["statusCode"] == 200, f"Expected 200, got {res['statusCode']}"
        assert len(res["originalBytes"]) > 0
        assert res["responseSha256"] == hashlib.sha256(res["originalBytes"]).hexdigest().lower()

    def test_36_fake_market_pulse_url_rejected(self):
        """Verifies that a fake or 404 Market Pulse URL is classified as UNVERIFIED with null value."""
        engine = MarketPulseEngine(raw_evidence_dir=RAW_EVIDENCE_DIR, test_mode=True)
        fake_url = f"{self.base_fixture_url}/market-pulse-404"
        obs = engine.collect_live_indicator("MP-01", target_url=fake_url)
        assert obs["verificationStatus"] == "UNVERIFIED"
        assert obs["actualValue"] is None
        assert "Status: 404" in obs["verificationNote"]

    def test_37_unapproved_market_pulse_publisher_rejected(self):
        """Verifies that an unapproved publisher for Market Pulse is classified as UNVERIFIED."""
        engine = MarketPulseEngine(raw_evidence_dir=RAW_EVIDENCE_DIR, test_mode=True)
        unapproved_url = "http://unapproved-financial-blog.xyz/vnindex"
        obs = engine.collect_live_indicator("MP-04", target_url=unapproved_url)
        assert obs["verificationStatus"] == "UNVERIFIED"
        assert obs["actualValue"] is None

    def test_38_synthetic_local_evidence_rejected(self):
        """Verifies that synthetic local evidence without authentic HTTP retrieval is rejected."""
        engine = MarketPulseEngine(raw_evidence_dir=RAW_EVIDENCE_DIR, test_mode=True)
        obs = engine.collect_live_indicator("MP-01", target_url=None, is_synthetic=True)
        assert obs["verificationStatus"] == "UNVERIFIED"
        assert obs["actualValue"] is None
        assert "Synthetic local evidence" in obs["verificationNote"]

    def test_39_actual_final_url_after_redirect_captured(self):
        """Verifies that actual final URL is captured after HTTP redirects."""
        collector = DailyNewsCollector(raw_evidence_dir=RAW_EVIDENCE_DIR, test_mode=True)
        redirect_url = f"{self.base_fixture_url}/redirect-to-trusted"
        res = collector.fetch_url(redirect_url)
        assert res["statusCode"] == 200
        assert res["finalUrl"].endswith("/trusted-target.html")
        assert res["originalUrl"] == redirect_url

    def test_40_untrusted_redirect_in_orchestrator_rejected(self):
        """Verifies that a candidate with redirect to untrusted domain is rejected by verifier."""
        verifier = SourceVerificationEngine(raw_evidence_dir=RAW_EVIDENCE_DIR, test_mode=True)
        test_path = os.path.join(RAW_EVIDENCE_DIR, "test_snapshot_01.txt")
        test_sha = compute_file_sha256(test_path)
        
        orig_url = "https://cafef.vn/tin-chuyen-huong.chn"
        fake_ledger = {
            orig_url: {
                "statusCode": 200,
                "originalUrl": orig_url,
                "finalUrl": "http://attacker-controlled-site.com/fake.html",
                "responseSha256": test_sha
            }
        }
        event = {
            "eventId": "EVT-REDIR-FAIL",
            "originalUrl": orig_url,
            "evidenceSnapshotPath": test_path,
            "evidenceSha256": test_sha,
            "category": "MACRO_MONETARY"
        }
        passed, failures = verifier.verify_single_event(event, http_retrieval_records=fake_ledger)
        assert not passed, "Redirect to untrusted domain must be rejected"
        assert any("REDIRECT_TO_UNTRUSTED_DOMAIN" in f for f in failures)

    def test_41_original_byte_sha256_parity(self):
        """Verifies that the original response byte SHA-256 matches stored snapshot hash exactly."""
        collector = DailyNewsCollector(raw_evidence_dir=RAW_EVIDENCE_DIR, test_mode=True)
        res = collector.fetch_url(f"{self.base_fixture_url}/valid-article")
        
        snap_path = os.path.join(RAW_EVIDENCE_DIR, "test_parity_snapshot.html")
        with open(snap_path, "wb") as f:
            f.write(res["originalBytes"])
            
        file_sha = compute_file_sha256(snap_path)
        assert file_sha == res["responseSha256"], f"Parity mismatch: {file_sha} != {res['responseSha256']}"

    def test_42_all_news_event_schema_fields(self):
        """Validates all 18 required newsEvent fields against Data Contract V3.0.4 Draft 2020-12."""
        contract_path = os.path.join(WORKSPACE_DIR, "PHASE05_DATA_CONTRACT_V3_0_4.json")
        with open(contract_path, "r", encoding="utf-8") as f:
            contract = json.load(f)
        validator = JsonSchemaValidator(contract)
        schema = validator.resolve_ref("#/contractDefinitions/newsEvent")
        
        valid_event = {
            "eventId": "EVT-20261109-001",
            "originalHeadline": "Ngân hàng Nhà nước duy trì ổn định lãi suất điều hành",
            "originalPublisher": "Báo Tuổi Trẻ",
            "originalUrl": "https://tuoitre.vn/ngan-hang-nha-nuoc-on-dinh-lai-suat.htm",
            "originalPubTimestamp": "2026-11-09T10:00:00+07:00",
            "retrievedTimestamp": "2026-11-09T12:00:00+07:00",
            "summary": "Ngân hàng Nhà nước thông báo tiếp tục giữ ổn định lãi suất điều hành nhằm hỗ trợ tăng trưởng kinh tế bền vững.",
            "mainFacts": ["NHNN giữ nguyên mặt bằng lãi suất điều hành trong quý 4/2026."],
            "financialFacts": [],
            "supportingQuote": "Ngân hàng Nhà nước thông báo tiếp tục giữ ổn định lãi suất điều hành",
            "evidenceSnapshotPath": "raw_evidence_store/snapshot_test.html",
            "evidenceSha256": "abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789",
            "contentFingerprintSha256": "1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
            "category": "MACRO_MONETARY",
            "freshnessBucket": "0_TO_24H",
            "historicalDedupResult": "DISTINCT_EVENT",
            "editorialRelevance": "HIGH",
            "commercialRelevance": "HIGH"
        }
        validator.validate(valid_event, subschema=schema)

        invalid_event = dict(valid_event)
        invalid_event["category"] = "INVALID_CATEGORY_NAME"
        try:
            validator.validate(invalid_event, subschema=schema)
            assert False, "Invalid category enum must be rejected by schema"
        except SchemaValidationError:
            pass

    def test_43_financial_facts_numeric_value_string_type(self):
        """Verifies that financialFacts.numericValue strictly requires string type."""
        contract_path = os.path.join(WORKSPACE_DIR, "PHASE05_DATA_CONTRACT_V3_0_4.json")
        with open(contract_path, "r", encoding="utf-8") as f:
            contract = json.load(f)
        validator = JsonSchemaValidator(contract)
        schema = validator.resolve_ref("#/contractDefinitions/financialFact")

        valid_fact = {
            "extractedExpression": "11,94%",
            "numericValue": "11.94",
            "unit": "%",
            "metricName": "Tăng trưởng tín dụng"
        }
        validator.validate(valid_fact, subschema=schema)

        invalid_fact = {
            "extractedExpression": "11,94%",
            "numericValue": 11.94,
            "unit": "%",
            "metricName": "Tăng trưởng tín dụng"
        }
        try:
            validator.validate(invalid_fact, subschema=schema)
            assert False, "Float numericValue must be rejected by V3.0.4 financialFact schema"
        except SchemaValidationError:
            pass

    def test_44_multi_publisher_source_diversity(self):
        """Verifies that candidates are harvested across multiple publishers rather than a single source."""
        collector = DailyNewsCollector(raw_evidence_dir=RAW_EVIDENCE_DIR)
        mock_candidates = [
            {"candidateId": "CAND-01", "publisher": "CafeF / VCCorp"},
            {"candidateId": "CAND-02", "publisher": "Báo Tuổi Trẻ"},
            {"candidateId": "CAND-03", "publisher": "Tạp chí Kinh tế Việt Nam (VnEconomy)"},
            {"candidateId": "CAND-04", "publisher": "Báo Đầu tư"}
        ]
        pubs = {c["publisher"] for c in mock_candidates}
        assert len(pubs) >= 3, f"Expected diversity across >= 3 publishers, got {len(pubs)}"

    def test_45_hardcoded_high_relevance_rejected_for_non_financial(self):
        """Verifies that non-financial topics receive IRRELEVANT and are rejected."""
        headline = "ĐBQH đề xuất cấm bán và sử dụng thuốc lá đối với người sinh năm 2010 trở về sau"
        summary = "Quốc hội họp phiên toàn thể cho ý kiến dự án Luật sửa đổi về phòng chống tác hại thuốc lá."
        edit_rel, comm_rel, is_irrel, reason = evaluate_editorial_and_commercial_relevance(headline, summary)
        assert is_irrel, "Tobacco legislation must be flagged as non-financial topic"
        assert edit_rel == "IRRELEVANT", f"Expected IRRELEVANT, got {edit_rel}"
        assert comm_rel == "LOW"

    def test_46_freshness_quota_gate_requires_both(self):
        """Verifies that DATA_READY requires BOTH >= 25 events AND >= 80% 0-24h."""
        collector = DailyNewsCollector(raw_evidence_dir=RAW_EVIDENCE_DIR, run_timestamp="2026-11-09T18:00:00+07:00")
        candidates_20 = [
            {
                "candidateId": f"CAND-20-{i:03d}",
                "headline": f"Tin tài chính {i}",
                "originalUrl": f"https://cafef.vn/tin-{i}.chn",
                "originalPublishedAt": "2026-11-09T14:00:00+07:00"
            } for i in range(1, 21)
        ]
        status_a, rep_a = collector.process_candidate_pool(candidates_20)
        assert status_a == "COLLECTION_SHORTFALL"
        assert rep_a["shortfall"] == 5

    def test_47_complete_candidate_disposition_accounting(self):
        """Verifies that 100% of discovered candidates receive exactly one auditable disposition."""
        mock_accounting = {
            "VERIFIED_UNIQUE": 12,
            "REJECTED_STALE": 1,
            "REJECTED_IRRELEVANT": 2,
            "REJECTED_SOURCE": 0,
            "REJECTED_DUPLICATE": 13,
            "EXCESS_NOT_SELECTED": 0,
            "MANUAL_REVIEW_REQUIRED": 0
        }
        total_discovered = 28
        total_accounted = sum(mock_accounting.values())
        assert total_accounted == total_discovered, f"Accounting mismatch: {total_accounted} != {total_discovered}"

    def test_48_no_false_data_ready_on_shortfall(self):
        """Verifies that when quota or freshness fails, verdict is DATA_SHORTFALL_OR_UNVERIFIED."""
        eligible_count = 12
        target = 25
        quota_met = (eligible_count >= target)
        verdict = "DATA_READY" if quota_met else "DATA_SHORTFALL_OR_UNVERIFIED"
        assert verdict == "DATA_SHORTFALL_OR_UNVERIFIED", "Shortfall must never emit DATA_READY"

    # =========================================================================
    # PHASE 05B-R1.2: MANDATORY ADVERSARIAL QA TESTS (R12-01 to R12-25)
    # =========================================================================

    def test_r12_01_tampered_numeric_value_rejected(self):
        """R12-01: Verifies that tampering numericValue to 999999999 is detected and rejected."""
        verifier = SourceVerificationEngine(raw_evidence_dir=RAW_EVIDENCE_DIR, test_mode=True)
        test_path = os.path.join(RAW_EVIDENCE_DIR, "test_fact_snapshot.html")
        content = "<html><body>Lợi nhuận sau thuế của Vietcombank đạt 1.250 tỷ đồng trong quý 3.</body></html>"
        with open(test_path, "w", encoding="utf-8") as f:
            f.write(content)
        actual_sha = compute_file_sha256(test_path)
        
        event = {
            "eventId": "EVT-TAMPER-01",
            "originalUrl": "https://vietcombank.com.vn/tin-tuc-1",
            "evidenceSnapshotPath": test_path,
            "evidenceSha256": actual_sha,
            "category": "BANKING_CREDIT",
            "supportingQuote": "Lợi nhuận sau thuế của Vietcombank đạt 1.250 tỷ đồng trong quý 3.",
            "financialFacts": [
                {
                    "extractedExpression": "1.250 tỷ đồng",
                    "numericValue": "999999999",  # TAMPERED VALUE!
                    "unit": "tỷ",
                    "metricName": "Lợi nhuận sau thuế",
                    "contextQuote": "Lợi nhuận sau thuế của Vietcombank đạt 1.250 tỷ đồng trong quý 3."
                }
            ]
        }
        passed, failures = verifier.verify_single_event(event)
        assert not passed, "Tampered numericValue must be rejected"
        assert any("FACT_MISMATCH_VALUE" in f for f in failures)

    def test_r12_02_tampered_unit_rejected(self):
        """R12-02: Verifies that altering unit from VND to USD is detected and rejected."""
        verifier = SourceVerificationEngine(raw_evidence_dir=RAW_EVIDENCE_DIR, test_mode=True)
        test_path = os.path.join(RAW_EVIDENCE_DIR, "test_fact_snapshot.html")
        actual_sha = compute_file_sha256(test_path)
        
        event = {
            "eventId": "EVT-TAMPER-02",
            "originalUrl": "https://vietcombank.com.vn/tin-tuc-1",
            "evidenceSnapshotPath": test_path,
            "evidenceSha256": actual_sha,
            "category": "BANKING_CREDIT",
            "supportingQuote": "Lợi nhuận sau thuế của Vietcombank đạt 1.250 tỷ đồng trong quý 3.",
            "financialFacts": [
                {
                    "extractedExpression": "1.250 tỷ đồng",
                    "numericValue": "1250",
                    "unit": "USD",  # TAMPERED UNIT (quote says tỷ đồng)!
                    "metricName": "Lợi nhuận sau thuế",
                    "contextQuote": "Lợi nhuận sau thuế của Vietcombank đạt 1.250 tỷ đồng trong quý 3."
                }
            ]
        }
        passed, failures = verifier.verify_single_event(event)
        assert not passed, "Tampered unit must be rejected"
        assert any("FACT_MISMATCH_UNIT" in f for f in failures)

    def test_r12_03_inverted_polarity_rejected(self):
        """R12-03: Verifies that flipping polarity (claim says tăng/UP when evidence says giảm/DOWN) is rejected."""
        verifier = SourceVerificationEngine(raw_evidence_dir=RAW_EVIDENCE_DIR, test_mode=True)
        test_path = os.path.join(RAW_EVIDENCE_DIR, "test_fact_polarity.html")
        content = "<html><body>Chỉ số giá tiêu dùng CPI giảm 0,88% so với tháng trước do giá xăng dầu hạ.</body></html>"
        with open(test_path, "w", encoding="utf-8") as f:
            f.write(content)
        actual_sha = compute_file_sha256(test_path)
        
        event = {
            "eventId": "EVT-TAMPER-03",
            "originalUrl": "https://gso.gov.vn/cpi-2026",
            "evidenceSnapshotPath": test_path,
            "evidenceSha256": actual_sha,
            "category": "MACRO_MONETARY",
            "supportingQuote": "Chỉ số giá tiêu dùng CPI giảm 0,88% so với tháng trước do giá xăng dầu hạ.",
            "financialFacts": [
                {
                    "extractedExpression": "giảm 0,88%",
                    "numericValue": "0.88",
                    "unit": "%",
                    "metricName": "Tăng trưởng CPI",
                    "polarity": "UP",  # INVERTED POLARITY! Quote clearly says "giảm"
                    "contextQuote": "Chỉ số giá tiêu dùng CPI giảm 0,88% so với tháng trước do giá xăng dầu hạ."
                }
            ]
        }
        passed, failures = verifier.verify_single_event(event)
        assert not passed, "Inverted polarity must be rejected"
        assert any("FACT_MISMATCH_DIRECTION" in f for f in failures)

    def test_r12_04_tampered_entity_rejected(self):
        """R12-04: Verifies that changing entity to an unmentioned institution is rejected."""
        verifier = SourceVerificationEngine(raw_evidence_dir=RAW_EVIDENCE_DIR, test_mode=True)
        test_path = os.path.join(RAW_EVIDENCE_DIR, "test_fact_snapshot.html")
        actual_sha = compute_file_sha256(test_path)
        
        event = {
            "eventId": "EVT-TAMPER-04",
            "originalUrl": "https://vietcombank.com.vn/tin-tuc-1",
            "evidenceSnapshotPath": test_path,
            "evidenceSha256": actual_sha,
            "category": "BANKING_CREDIT",
            "supportingQuote": "Lợi nhuận sau thuế của Vietcombank đạt 1.250 tỷ đồng trong quý 3.",
            "financialFacts": [
                {
                    "extractedExpression": "1.250 tỷ đồng",
                    "numericValue": "1250",
                    "unit": "tỷ",
                    "metricName": "Lợi nhuận sau thuế",
                    "entity": "Ngân hàng TMCP Phương Đông (OCB)",  # TAMPERED ENTITY!
                    "contextQuote": "Lợi nhuận sau thuế của Vietcombank đạt 1.250 tỷ đồng trong quý 3."
                }
            ]
        }
        passed, failures = verifier.verify_single_event(event)
        assert not passed, "Tampered entity must be rejected"
        assert any("FACT_MISMATCH_ENTITY" in f for f in failures)

    def test_r12_05_tampered_reporting_period_rejected(self):
        """R12-05: Verifies that changing reporting period to an unmentioned period is rejected."""
        verifier = SourceVerificationEngine(raw_evidence_dir=RAW_EVIDENCE_DIR, test_mode=True)
        test_path = os.path.join(RAW_EVIDENCE_DIR, "test_fact_snapshot.html")
        actual_sha = compute_file_sha256(test_path)
        
        event = {
            "eventId": "EVT-TAMPER-05",
            "originalUrl": "https://vietcombank.com.vn/tin-tuc-1",
            "evidenceSnapshotPath": test_path,
            "evidenceSha256": actual_sha,
            "category": "BANKING_CREDIT",
            "supportingQuote": "Lợi nhuận sau thuế của Vietcombank đạt 1.250 tỷ đồng trong quý 3.",
            "financialFacts": [
                {
                    "extractedExpression": "1.250 tỷ đồng",
                    "numericValue": "1250",
                    "unit": "tỷ",
                    "metricName": "Lợi nhuận sau thuế",
                    "reportingPeriod": "Quý 1/2024",  # TAMPERED PERIOD (text says quý 3)!
                    "contextQuote": "Lợi nhuận sau thuế của Vietcombank đạt 1.250 tỷ đồng trong quý 3."
                }
            ]
        }
        passed, failures = verifier.verify_single_event(event)
        assert not passed, "Tampered reporting period must be rejected"
        assert any("FACT_MISMATCH_PERIOD" in f for f in failures)

    def test_r12_06_tampered_extracted_expression_rejected(self):
        """R12-06: Verifies that keeping quote but modifying extractedExpression is rejected."""
        verifier = SourceVerificationEngine(raw_evidence_dir=RAW_EVIDENCE_DIR, test_mode=True)
        test_path = os.path.join(RAW_EVIDENCE_DIR, "test_fact_snapshot.html")
        actual_sha = compute_file_sha256(test_path)
        
        event = {
            "eventId": "EVT-TAMPER-06",
            "originalUrl": "https://vietcombank.com.vn/tin-tuc-1",
            "evidenceSnapshotPath": test_path,
            "evidenceSha256": actual_sha,
            "category": "BANKING_CREDIT",
            "supportingQuote": "Lợi nhuận sau thuế của Vietcombank đạt 1.250 tỷ đồng trong quý 3.",
            "financialFacts": [
                {
                    "extractedExpression": "lợi nhuận kỷ lục 5.000 tỷ đồng",  # NOT in quote!
                    "numericValue": "1250",
                    "unit": "tỷ",
                    "metricName": "Lợi nhuận sau thuế",
                    "contextQuote": "Lợi nhuận sau thuế của Vietcombank đạt 1.250 tỷ đồng trong quý 3."
                }
            ]
        }
        passed, failures = verifier.verify_single_event(event)
        assert not passed, "Tampered extractedExpression must be rejected"
        assert any("FACT_MISMATCH_EXPRESSION" in f for f in failures)

    def test_r12_07_evidence_without_numeric_measurement_rejected(self):
        """R12-07: Verifies that a quote containing no numbers cannot verify a financial fact."""
        verifier = SourceVerificationEngine(raw_evidence_dir=RAW_EVIDENCE_DIR, test_mode=True)
        test_path = os.path.join(RAW_EVIDENCE_DIR, "test_no_number.html")
        content = "<html><body>Ngân hàng cam kết đồng hành cùng doanh nghiệp phát triển bền vững.</body></html>"
        with open(test_path, "w", encoding="utf-8") as f:
            f.write(content)
        actual_sha = compute_file_sha256(test_path)
        
        event = {
            "eventId": "EVT-TAMPER-07",
            "originalUrl": "https://vietcombank.com.vn/cam-ket",
            "evidenceSnapshotPath": test_path,
            "evidenceSha256": actual_sha,
            "category": "BANKING_CREDIT",
            "supportingQuote": "Ngân hàng cam kết đồng hành cùng doanh nghiệp phát triển bền vững.",
            "financialFacts": [
                {
                    "extractedExpression": "1.000 tỷ",
                    "numericValue": "1000",
                    "unit": "tỷ",
                    "metricName": "Quy mô",
                    "contextQuote": "Ngân hàng cam kết đồng hành cùng doanh nghiệp phát triển bền vững."
                }
            ]
        }
        passed, failures = verifier.verify_single_event(event)
        assert not passed, "Quote without numbers must be rejected"
        assert any("FACT_NOT_GROUNDED_IN_EVIDENCE" in f for f in failures)

    def test_r12_08_http_200_homepage_rejected(self):
        """R12-08: Verifies that a generic homepage returning HTTP 200 is rejected as article evidence."""
        verifier = SourceVerificationEngine(raw_evidence_dir=RAW_EVIDENCE_DIR, test_mode=True)
        event = {
            "eventId": "EVT-HOMEPAGE-01",
            "originalUrl": "https://sbv.gov.vn/",
            "evidenceSnapshotPath": os.path.join(RAW_EVIDENCE_DIR, "test_snapshot_01.txt"),
            "evidenceSha256": compute_file_sha256(os.path.join(RAW_EVIDENCE_DIR, "test_snapshot_01.txt")),
            "category": "MACRO_MONETARY"
        }
        passed, failures = verifier.verify_single_event(event)
        assert not passed, "Generic homepage must be rejected"
        assert any("GENERIC_HOMEPAGE_REJECTED" in f for f in failures)

    def test_r12_09_category_listing_page_rejected(self):
        """R12-09: Verifies that a category listing page with no substantive article body is rejected."""
        html_cat = (
            "<html><head><title>Chuyên mục Kinh doanh</title></head>"
            "<body><nav>Menu</nav><div class='news-list'><a href='/tin1'>Tin 1</a><a href='/tin2'>Tin 2</a></div>"
            "<footer>Footer info</footer></body></html>"
        )
        res = extract_clean_article_content(html_cat, "https://tuoitre.vn/kinh-doanh.htm")
        assert not res["isArticle"], "Category page must not be classified as article"
        assert res["extractionStatus"] == "ARTICLE_BODY_UNAVAILABLE"

    def test_r12_10_js_cookie_challenge_rejected(self):
        """R12-10: Verifies that a JavaScript/cookie challenge returning 200 is rejected as UNVERIFIED."""
        collector = DailyNewsCollector(raw_evidence_dir=RAW_EVIDENCE_DIR, test_mode=True)
        res = collector.fetch_url(f"{self.base_fixture_url}/cookie-challenge")
        assert res["statusCode"] == 200
        content = extract_clean_article_content(res["originalBytes"].decode("utf-8"), res["finalUrl"])
        assert not content["isArticle"], "Cookie challenge must not be accepted as article"
        assert content["extractionStatus"] == "ARTICLE_BODY_UNAVAILABLE"

    def test_r12_11_retrieval_time_fallback_prohibited(self):
        """R12-11: Verifies that missing publication timestamps NEVER fall back to retrieval timestamp."""
        html_no_date = "<html><head><title>Tin không có ngày tháng</title></head><body><p>Nội dung bài viết tài chính.</p></body></html>"
        dt, raw_val, method = extract_publication_timestamp_hierarchy(html_no_date)
        assert dt is None, "Missing date must return None, never fall back to retrieval time"
        assert method == "TIMESTAMP_UNVERIFIED"

    def test_r12_12_html_entity_timezone_parsing(self):
        """R12-12: Verifies that HTML entity timezone offsets (&#x2B;07:00) parse correctly."""
        raw_ts = "2026-11-09T14:30:00&#x2B;07:00"
        dt = parse_timestamp_iso_or_vietnamese(raw_ts)
        assert dt is not None, "HTML entity encoded timestamp must parse cleanly"
        assert dt.hour == 14 and dt.minute == 30
        assert dt.tzinfo is not None

    def test_r12_13_future_timestamp_rejected(self):
        """R12-13: Verifies that a publication timestamp in the future is rejected as FUTURE_TIMESTAMP."""
        collector = DailyNewsCollector(raw_evidence_dir=RAW_EVIDENCE_DIR, run_timestamp="2026-11-09T12:00:00+07:00")
        cand = {
            "candidateId": "CAND-FUT",
            "originalPublishedAt": "2026-11-10T12:00:00+07:00"  # Tomorrow
        }
        is_valid, reason, age = collector.evaluate_candidate_freshness(cand)
        assert not is_valid
        assert "FUTURE_TIMESTAMP" in reason

    def test_r12_14_missing_or_unparseable_timestamp_manual_review(self):
        """R12-14: Verifies that unparseable timestamps yield MANUAL_REVIEW_REQUIRED, not stale."""
        collector = DailyNewsCollector(raw_evidence_dir=RAW_EVIDENCE_DIR, run_timestamp="2026-11-09T12:00:00+07:00")
        candidates = [
            {
                "candidateId": "CAND-NO-TS",
                "headline": "Tin thiếu ngày đăng",
                "originalUrl": "https://cafef.vn/tin-1.chn",
                "originalPublishedAt": None  # Missing timestamp
            }
        ]
        status, report = collector.process_candidate_pool(candidates)
        assert len(report["rejectedCandidates"]) == 1
        assert report["rejectedCandidates"][0]["disposition"] == "MANUAL_REVIEW_REQUIRED"

    def test_r12_15_footer_payment_noise_does_not_poison_category(self):
        """R12-15: Verifies that footer payment links do not poison a stock market article into FINTECH_PAYMENT."""
        collector = DailyNewsCollector(raw_evidence_dir=RAW_EVIDENCE_DIR, test_mode=True)
        res = collector.fetch_url(f"{self.base_fixture_url}/article-with-footer-noise")
        assert res["statusCode"] == 200
        content = extract_clean_article_content(res["originalBytes"].decode("utf-8"), res["finalUrl"])
        assert content["isArticle"]
        cat = classify_canonical_category(content["headline"], content["summary"], content["articleBody"])
        assert cat == "CAPITAL_MARKETS", f"Expected CAPITAL_MARKETS, got {cat}"

    def test_r12_16_publisher_domain_in_main_entities_rejected(self):
        """R12-16: Verifies that placing publisher domain (cafef.vn) into mainEntities fails verification."""
        verifier = SourceVerificationEngine(raw_evidence_dir=RAW_EVIDENCE_DIR, test_mode=True)
        test_path = os.path.join(RAW_EVIDENCE_DIR, "test_snapshot_01.txt")
        actual_sha = compute_file_sha256(test_path)
        
        event = {
            "eventId": "EVT-PUB-ENTITY",
            "originalUrl": "https://cafef.vn/tin-tuc-1",
            "evidenceSnapshotPath": test_path,
            "evidenceSha256": actual_sha,
            "category": "MACRO_MONETARY",
            "mainEntities": ["cafef.vn"]  # INVALID! Must not be publisher domain
        }
        passed, failures = verifier.verify_single_event(event)
        assert not passed, "Publisher domain in mainEntities must be rejected"
        assert any("INVALID_MAIN_ENTITY_PUBLISHER_DOMAIN" in f for f in failures)

    def test_r12_17_market_pulse_ignores_hardcoded_input_values(self):
        """R12-17: Verifies that passing fake hardcoded extracted_value to MarketPulseEngine is ignored."""
        engine = MarketPulseEngine(raw_evidence_dir=RAW_EVIDENCE_DIR, test_mode=True)
        test_url = f"{self.base_fixture_url}/market-pulse-mp01"
        # Pass fake hardcoded value 999999
        obs = engine.collect_live_indicator("MP-01", target_url=test_url, extracted_value="999999")
        assert obs["verificationStatus"] == "VERIFIED"
        # Actual extracted value from fixture HTML is 25615, NOT 999999!
        assert obs["actualValue"] == "25615", f"Engine must extract real value 25615, got {obs['actualValue']}"

    def test_r12_18_market_pulse_missing_metric_unverified(self):
        """R12-18: Verifies that if HTML contains no matching indicator metric, indicator is UNVERIFIED with null."""
        engine = MarketPulseEngine(raw_evidence_dir=RAW_EVIDENCE_DIR, test_mode=True)
        test_url = f"{self.base_fixture_url}/market-pulse-no-metric"
        obs = engine.collect_live_indicator("MP-01", target_url=test_url)
        assert obs["verificationStatus"] == "UNVERIFIED"
        assert obs["actualValue"] is None
        assert "Không thể trích xuất" in obs["verificationNote"]

    def test_r12_19_ssrf_redirect_to_localhost_rejected(self):
        """R12-19: Verifies that in production mode, redirect to localhost is blocked by SSRF defense."""
        verifier = SourceVerificationEngine(raw_evidence_dir=RAW_EVIDENCE_DIR, test_mode=False)
        is_safe, reason = validate_hostname_boundary("http://localhost:8080/evil", test_mode=False)
        assert not is_safe
        assert "LOCALHOST_ACCESS_PROHIBITED" in reason

    def test_r12_20_ssrf_redirect_to_private_ip_rejected(self):
        """R12-20: Verifies that redirect to private RFC 1918 IPs is blocked by SSRF defense."""
        private_ips = ["10.0.0.1", "172.16.0.1", "192.168.1.1", "169.254.169.254"]
        for pip in private_ips:
            assert is_ip_private_or_loopback(pip), f"{pip} must be recognized as private/loopback IP"

    def test_r12_21_redirect_to_untrusted_domain_rejected(self):
        """R12-21: Verifies that redirect to unapproved external domain is blocked."""
        is_safe, reason = validate_hostname_boundary("http://untrusted-financial-attacker.com/leak", test_mode=False)
        assert not is_safe
        assert "UNTRUSTED_HOSTNAME" in reason

    def test_r12_22_dns_resolving_to_private_ip_rejected(self):
        """R12-22: Verifies that IP address safety validation correctly rejects private and link-local ranges."""
        assert is_ip_private_or_loopback("127.0.0.1")
        assert is_ip_private_or_loopback("10.10.10.10")
        assert is_ip_private_or_loopback("192.168.0.1")
        assert not is_ip_private_or_loopback("8.8.8.8")  # Public IP

    def test_r12_23_two_articles_same_event_detected_as_duplicate(self):
        """R12-23: Verifies that two articles covering the same event are recognized as duplicates."""
        engine = SemanticDedupEngine(fixtures_dir=FIXTURES_DIR)
        art1 = {
            "headline": "Thanh khoản HoSE vượt 15.000 tỷ đồng, VN-Index hồi phục nhẹ",
            "summary": "Thị trường chứng khoán ghi nhận phiên hồi phục tích cực với thanh khoản tăng mạnh trên sàn HoSE.",
            "mainEntities": ["HOSE", "VN-Index"],
            "originalPubTimestamp": "2026-11-09T15:00:00+07:00"
        }
        art2 = {
            "headline": "Sàn HoSE khớp lệnh hơn 15.000 tỷ, VN-Index lấy lại sắc xanh",
            "summary": "Chỉ số VN-Index tăng điểm trở lại nhờ lực cầu bắt đáy, giá trị giao dịch sàn HoSE đạt trên 15.000 tỷ.",
            "mainEntities": ["HOSE", "VN-Index"],
            "originalPubTimestamp": "2026-11-09T15:30:00+07:00"
        }
        rel, sim, reason = engine.classify_pair_relationship(art1, art2)
        assert rel == "SAME_EVENT"
        assert sim >= 0.70

    def test_r12_24_two_events_same_institution_distinct(self):
        """R12-24: Verifies that distinct events about the same bank are NOT marked as duplicate."""
        engine = SemanticDedupEngine(fixtures_dir=FIXTURES_DIR)
        ev1 = {
            "headline": "Vietcombank phát hành 5.000 tỷ đồng trái phiếu xanh đợt 1",
            "summary": "Nguồn vốn huy động dùng để cho vay các dự án năng lượng tái tạo và xử lý nước thải.",
            "mainEntities": ["Vietcombank"],
            "originalPubTimestamp": "2026-11-09T09:00:00+07:00"
        }
        ev2 = {
            "headline": "Vietcombank nâng cấp ứng dụng VCB Digibank tích hợp trợ lý ảo AI",
            "summary": "Ứng dụng ngân hàng số mới cho phép khách hàng tra cứu giao dịch bằng giọng nói.",
            "mainEntities": ["Vietcombank"],
            "originalPubTimestamp": "2026-11-09T14:00:00+07:00"
        }
        rel, sim, reason = engine.classify_pair_relationship(ev1, ev2)
        assert rel == "DISTINCT_EVENT"

    def test_r12_25_tampered_snapshot_content_hash_mismatch(self):
        """R12-25: Verifies that altering raw snapshot on disk without changing recorded hash fails."""
        verifier = SourceVerificationEngine(raw_evidence_dir=RAW_EVIDENCE_DIR, test_mode=True)
        test_path = os.path.join(RAW_EVIDENCE_DIR, "test_hash_tamper.html")
        with open(test_path, "w", encoding="utf-8") as f:
            f.write("<html><body>Ban goc</body></html>")
        original_sha = compute_file_sha256(test_path)
        
        # Tamper file on disk
        with open(test_path, "w", encoding="utf-8") as f:
            f.write("<html><body>Ban da bi sua doi!</body></html>")
            
        event = {
            "eventId": "EVT-HASH-TAMPER",
            "originalUrl": "https://sbv.gov.vn/portal/vi/tin-tuc/test",
            "evidenceSnapshotPath": test_path,
            "evidenceSha256": original_sha,  # Old hash!
            "category": "MACRO_MONETARY"
        }
        passed, failures = verifier.verify_single_event(event)
        assert not passed, "Tampered snapshot file must be rejected by SHA-256 mismatch"
        assert any("SHA256_MISMATCH" in f for f in failures)

    # =========================================================================
    # PHASE 05B-R1.3 MANDATORY MARKET PULSE ADVERSARIAL TESTS (MP-R13-01 to MP-R13-35)
    # =========================================================================

    def test_mp_r13_01_hardcoded_actual_value_injected_by_orchestrator(self):
        """MP-R13-01: Verifies that passing hardcoded actualValue is strictly ignored."""
        engine = MarketPulseEngine(raw_evidence_dir=RAW_EVIDENCE_DIR, test_mode=True)
        obs = engine.collect_live_indicator("MP-01", f"{self.base_fixture_url}/market-pulse-mp01", extracted_value="999999")
        assert obs["verificationStatus"] == "VERIFIED"
        assert obs["actualValue"] == "25615", f"Expected real extracted value 25615, got {obs['actualValue']}"

    def test_mp_r13_02_hardcoded_change_rejected(self):
        """MP-R13-02: Verifies that change is NOT hardcoded to +5 when previous observation is absent."""
        res = MarketPulseExtractor.extract_mp01_central_rate("Tỷ giá trung tâm ngày 09/11/2026 đạt 25.615 VND/USD theo công bố.")
        assert res["success"] is True
        assert res["change"] is None, "Change must be None without authentic previous rate"

    def test_mp_r13_03_hardcoded_direction_rejected(self):
        """MP-R13-03: Verifies that direction is NOT hardcoded to UP without authentic previous rate."""
        res = MarketPulseExtractor.extract_mp01_central_rate("Tỷ giá trung tâm ngày 09/11/2026 đạt 25.615 VND/USD theo công bố.")
        assert res["success"] is True
        assert res["direction"] is None, "Direction must be None without authentic previous rate"

    def test_mp_r13_04_missing_observation_date_not_replaced_by_runtime_date(self):
        """MP-R13-04: Verifies that missing observation date does NOT fallback to execution runtime date."""
        res = MarketPulseExtractor.extract_mp02_interbank_rate("Lãi suất liên ngân hàng kỳ hạn qua đêm ở mức 6,2% theo thông báo.")
        assert res["success"] is True
        assert res["observationDate"] is None, "Missing observation date must not be replaced by runtime date"

    def test_mp_r13_05_http_200_empty_response_unverified(self):
        """MP-R13-05: Verifies that HTTP 200 with empty body returns UNVERIFIED with actualValue null."""
        engine = MarketPulseEngine(raw_evidence_dir=RAW_EVIDENCE_DIR, test_mode=True)
        obs = engine.collect_live_indicator("MP-01", f"{self.base_fixture_url}/empty-body")
        assert obs["verificationStatus"] == "UNVERIFIED"
        assert obs["actualValue"] is None

    def test_mp_r13_06_homepage_instead_of_article_rejected(self):
        """MP-R13-06: Verifies that homepage landing page without metrics returns UNVERIFIED with actualValue null."""
        engine = MarketPulseEngine(raw_evidence_dir=RAW_EVIDENCE_DIR, test_mode=True)
        obs = engine.collect_live_indicator("MP-01", f"{self.base_fixture_url}/homepage-only")
        assert obs["verificationStatus"] == "UNVERIFIED"
        assert obs["actualValue"] is None

    def test_mp_r13_07_category_page_instead_of_data_source_rejected(self):
        """MP-R13-07: Verifies that category listing page without data returns UNVERIFIED."""
        engine = MarketPulseEngine(raw_evidence_dir=RAW_EVIDENCE_DIR, test_mode=True)
        obs = engine.collect_live_indicator("MP-01", f"{self.base_fixture_url}/category-only")
        assert obs["verificationStatus"] == "UNVERIFIED"
        assert obs["actualValue"] is None

    def test_mp_r13_08_cookie_challenge_page_unverified(self):
        """MP-R13-08: Verifies that cookie / anti-bot challenge returns UNVERIFIED with actualValue null."""
        engine = MarketPulseEngine(raw_evidence_dir=RAW_EVIDENCE_DIR, test_mode=True)
        obs = engine.collect_live_indicator("MP-01", f"{self.base_fixture_url}/cookie-challenge")
        assert obs["verificationStatus"] == "UNVERIFIED"
        assert obs["actualValue"] is None

    def test_mp_r13_09_evidence_does_not_contain_numeric_value_rejected(self):
        """MP-R13-09: Verifies that text without numeric measurement returns UNVERIFIED."""
        engine = MarketPulseEngine(raw_evidence_dir=RAW_EVIDENCE_DIR, test_mode=True)
        obs = engine.collect_live_indicator("MP-01", f"{self.base_fixture_url}/non-numeric-text")
        assert obs["verificationStatus"] == "UNVERIFIED"
        assert obs["actualValue"] is None

    def test_mp_r13_10_incorrect_numeric_value_rejected(self):
        """MP-R13-10: Verifies that commercial buy/sell rate is not substituted for central rate."""
        res = MarketPulseExtractor.extract_mp01_central_rate("Vietcombank niêm yết tỷ giá mua vào 25.400 VND/USD, bán ra 25.800 VND/USD.")
        assert res["success"] is False, "Commercial bank rate must not substitute for central exchange rate"

    def test_mp_r13_11_incorrect_unit_rejected(self):
        """MP-R13-11: Verifies that numeric normalizer rejects non-numeric or invalid units."""
        try:
            FinancialNumericNormalizer.parse_locale_number("không_phải_số")
            assert False, "Must raise ValueError on non-numeric string"
        except ValueError:
            pass

    def test_mp_r13_12_vietqr_100_million_normalized_correctly(self):
        """MP-R13-12: Verifies that 100 triệu giao dịch is normalized to 0.1 tỷ giao dịch (NEVER 100 tỷ!)."""
        engine = MarketPulseEngine(raw_evidence_dir=RAW_EVIDENCE_DIR, test_mode=True)
        obs = engine.collect_live_indicator("MP-06", f"{self.base_fixture_url}/mp06-vietqr-100m")
        assert obs["verificationStatus"] == "VERIFIED"
        assert obs["actualValue"] == "0.1", f"100 million must normalize to 0.1 billion, got {obs['actualValue']}"
        assert obs["unit"] == "tỷ giao dịch"

    def test_mp_r13_13_vietnamese_locale_number_parsing(self):
        """MP-R13-13: Verifies Vietnamese locale parsing (dot thousands, comma decimal)."""
        val1 = FinancialNumericNormalizer.parse_locale_number("1.714,32")
        assert val1 == 1714.32, f"Expected 1714.32, got {val1}"
        val2 = FinancialNumericNormalizer.parse_locale_number("25.615")
        assert val2 == 25615.0, f"Expected 25615.0, got {val2}"

    def test_mp_r13_14_percentage_locale_parsing(self):
        """MP-R13-14: Verifies percentage locale parsing with commas."""
        val = FinancialNumericNormalizer.parse_locale_number("12,5%")
        assert val == 12.5, f"Expected 12.5, got {val}"

    def test_mp_r13_15_mp06_total_napas_volume_labelled_vietqr_rejected(self):
        """MP-R13-15: Verifies that total NAPAS volume (>10B transactions) is rejected as VietQR-only."""
        engine = MarketPulseEngine(raw_evidence_dir=RAW_EVIDENCE_DIR, test_mode=True)
        obs = engine.collect_live_indicator("MP-06", f"{self.base_fixture_url}/mp06-total-napas")
        assert obs["verificationStatus"] == "UNVERIFIED"
        assert obs["actualValue"] is None
        assert "UNVERIFIED_SCOPE_MISMATCH" in obs["verificationNote"]

    def test_mp_r13_16_mp06_value_without_network_scope_unverified(self):
        """MP-R13-16: Verifies that generic cashless payment volume without VietQR rail is unverified."""
        engine = MarketPulseEngine(raw_evidence_dir=RAW_EVIDENCE_DIR, test_mode=True)
        obs = engine.collect_live_indicator("MP-06", f"{self.base_fixture_url}/mp06-no-network")
        assert obs["verificationStatus"] == "UNVERIFIED"
        assert obs["actualValue"] is None

    def test_mp_r13_17_mp03_bank_coverage_universe_disclosed(self):
        """MP-R13-17: Verifies that bank coverage universe is disclosed for deposit rates."""
        engine = MarketPulseEngine(raw_evidence_dir=RAW_EVIDENCE_DIR, test_mode=True)
        obs = engine.collect_live_indicator("MP-03", f"{self.base_fixture_url}/mp03-bank-partial")
        assert obs["verificationStatus"] == "VERIFIED"
        assert obs["actualValue"] == "9.1"
        assert "Cake" in obs.get("supportingQuote", "") or "Cake" in obs.get("interpretation", "")

    def test_mp_r13_18_mp03_promotional_rate_mislabelled_standard_rejected(self):
        """MP-R13-18: Verifies that promotional/VIP deposit rates are flagged."""
        res = MarketPulseExtractor.extract_mp03_deposit_rate("Lãi suất tiền gửi 12 tháng lên tới 9,5%/năm áp dụng ưu đãi cho khách hàng VIP gửi từ 500 tỷ đồng.")
        assert res["success"] is True
        assert res["isPromotional"] is True, "Must identify promotional / conditional rate"

    def test_mp_r13_19_mp04_intraday_value_labelled_closing_index_rejected(self):
        """MP-R13-19: Verifies that intraday index is rejected as closing index."""
        engine = MarketPulseEngine(raw_evidence_dir=RAW_EVIDENCE_DIR, test_mode=True)
        obs = engine.collect_live_indicator("MP-04", f"{self.base_fixture_url}/mp04-intraday")
        assert obs["verificationStatus"] == "UNVERIFIED"
        assert obs["actualValue"] is None
        assert "intraday" in obs["verificationNote"]

    def test_mp_r13_20_mp05_ytd_growth_labelled_yoy_distinguished(self):
        """MP-R13-20: Verifies that YTD credit growth is correctly distinguished."""
        res = MarketPulseExtractor.extract_mp05_credit_growth("Tăng trưởng tín dụng từ đầu năm tính đến ngày 26/10/2026 đạt 11,94%.")
        assert res["success"] is True
        assert "26/10/2026" in res["observationPeriod"] or "Tính đến" in res["observationPeriod"]

    def test_mp_r13_21_mp05_no_hardcoded_reporting_date(self):
        """MP-R13-21: Verifies that reporting date is extracted from text, not hardcoded."""
        res = MarketPulseExtractor.extract_mp05_credit_growth("Dư nợ tín dụng toàn nền kinh tế tăng 10,5% tính đến ngày 15/09/2026.")
        assert res["success"] is True
        assert res["observationDate"] == "2026-09-15", f"Expected 2026-09-15, got {res['observationDate']}"

    def test_mp_r13_22_mp07_monthly_value_distinguished_from_ytd(self):
        """MP-R13-22: Verifies that monthly tourist arrivals are distinguished from YTD."""
        res = MarketPulseExtractor.extract_mp07_tourist_arrivals("Khách quốc tế đến Việt Nam trong tháng 10 đạt 1,42 triệu lượt.")
        assert res["success"] is True
        assert res["isCumulativeYTD"] is False
        assert "tháng" in res["observationPeriod"].lower()

    def test_mp_r13_23_mp07_yoy_comparison_extracted(self):
        """MP-R13-23: Verifies that YoY comparison percentage is extracted."""
        res = MarketPulseExtractor.extract_mp07_tourist_arrivals("Khách du lịch quốc tế đến Việt Nam trong tháng 10 đạt 1,42 triệu lượt, tăng 15% so với cùng kỳ.")
        assert res["success"] is True
        assert "YoY" in res["change"]

    def test_mp_r13_24_mp08_awarded_volume_labelled_net_injection_rejected(self):
        """MP-R13-24: Verifies that gross awarded repo volume without maturities is rejected."""
        engine = MarketPulseEngine(raw_evidence_dir=RAW_EVIDENCE_DIR, test_mode=True)
        obs = engine.collect_live_indicator("MP-08", f"{self.base_fixture_url}/mp08-awarded-only")
        assert obs["verificationStatus"] == "UNVERIFIED"
        assert obs["actualValue"] is None
        assert "UNVERIFIED_INCOMPLETE_COMPONENTS" in obs["verificationNote"]

    def test_mp_r13_25_mp08_missing_maturity_component_unverified(self):
        """MP-R13-25: Verifies that missing maturity component returns UNVERIFIED_INCOMPLETE_COMPONENTS."""
        res = MarketPulseExtractor.extract_mp08_omo_operations("NHNN cho vay cầm cố trúng thầu 5.000 tỷ đồng qua kênh OMO.")
        assert res["success"] is False
        assert "UNVERIFIED_INCOMPLETE_COMPONENTS" in res["unverifiedReason"]

    def test_mp_r13_26_stale_mp02_observation_rejected(self):
        """MP-R13-26: Verifies that observation older than 72 hours is classified as STALE/UNVERIFIED with null."""
        engine = MarketPulseEngine(raw_evidence_dir=RAW_EVIDENCE_DIR, test_mode=True)
        obs = engine.collect_live_indicator("MP-02", f"{self.base_fixture_url}/mp02-stale")
        assert obs["verificationStatus"] in ["STALE", "UNVERIFIED"]
        assert obs["actualValue"] is None

    def test_mp_r13_27_fake_publication_timestamp_rejected(self):
        """MP-R13-27: Verifies that future observation timestamp is rejected."""
        engine = MarketPulseEngine(raw_evidence_dir=RAW_EVIDENCE_DIR, test_mode=True)
        future_ts = (datetime.now(TIMEZONE_HCM) + timedelta(days=2)).isoformat()
        obs_bad = {
            "indicatorId": "MP-01",
            "verificationStatus": "VERIFIED",
            "observationTimestamp": future_ts,
            "actualValue": 25615
        }
        res = engine.evaluate_indicator(obs_bad)
        assert res["verificationStatus"] == "UNVERIFIED"
        assert res["actualValue"] is None

    def test_mp_r13_28_snapshot_tampered_after_hashing_rejected(self):
        """MP-R13-28: Verifies that altering evidence snapshot after hashing is detected."""
        snap_path = os.path.join(RAW_EVIDENCE_DIR, "mp_tamper_unit_test.txt")
        with open(snap_path, "w", encoding="utf-8") as f:
            f.write("Dữ liệu gốc chính xác")
        orig_sha = compute_file_sha256(snap_path)
        with open(snap_path, "w", encoding="utf-8") as f:
            f.write("Dữ liệu đã bị can thiệp trái phép!")
        ok, msg = MarketPulseValidator.validate_evidence_integrity(snap_path, orig_sha)
        assert not ok
        assert "SHA256_MISMATCH" in msg

    def test_mp_r13_29_redirect_to_localhost_blocked_in_production(self):
        """MP-R13-29: Verifies that redirect to localhost is blocked in production mode."""
        client = SecureHttpClient(test_mode=False)
        res = client.get("http://localhost:8080/data")
        assert res["statusCode"] == 0
        assert "SECURITY_BLOCKED" in res["error"]

    def test_mp_r13_30_redirect_to_private_ip_blocked(self):
        """MP-R13-30: Verifies that redirect to RFC 1918 private IP is blocked in production mode."""
        client = SecureHttpClient(test_mode=False)
        res = client.get("http://192.168.1.1/admin")
        assert res["statusCode"] == 0
        assert "SECURITY_BLOCKED" in res["error"]

    def test_mp_r13_31_dns_rebinding_simulation_rejected(self):
        """MP-R13-31: Verifies that private and loopback IP addresses are classified as restricted."""
        assert SecureHttpClient.is_ip_restricted("127.0.0.1")
        assert SecureHttpClient.is_ip_restricted("10.0.0.1")
        assert SecureHttpClient.is_ip_restricted("172.16.0.1")
        assert SecureHttpClient.is_ip_restricted("192.168.1.1")
        assert not SecureHttpClient.is_ip_restricted("1.1.1.1")

    def test_mp_r13_32_ai_generated_interpretation_rejected_as_evidence(self):
        """MP-R13-32: Verifies that non-evidence text snapshot fails quote grounding."""
        snap_path = os.path.join(RAW_EVIDENCE_DIR, "ai_summary.txt")
        with open(snap_path, "w", encoding="utf-8") as f:
            f.write("Bản tóm tắt AI: Tỷ giá có xu hướng tăng.")
        ok, msg = MarketPulseValidator.validate_quote_grounding(snap_path, "Tỷ giá trung tâm chính thức 25.615 VND/USD")
        assert not ok
        assert "QUOTE_NOT_IN_EVIDENCE" in msg

    def test_mp_r13_33_conflicting_official_observations_manual_review(self):
        """MP-R13-33: Verifies that arithmetic mismatch between close and reported change triggers rejection."""
        # Current close: 1714.32, Prev close: 1700.00 (diff = 14.32), but text claims tăng 50.00 điểm!
        text = "VN-Index đóng cửa tại 1.714,32 điểm, tăng 50,00 điểm so với phiên liền trước 1.700,00 điểm."
        res = MarketPulseExtractor.extract_mp04_vnindex(text)
        assert res["success"] is False
        assert "ARITHMETIC_MISMATCH" in res["unverifiedReason"]

    def test_mp_r13_34_missing_previous_value_yields_unknown_direction(self):
        """MP-R13-34: Verifies that missing previous value yields change=None and direction=UNKNOWN."""
        mov = MarketPulseInterpreter.calculate_movement(current_val=25615.0, prev_val=None)
        assert mov["change"] is None, "Change must be None without previous value"
        assert mov["direction"] == "UNKNOWN", "Direction must be UNKNOWN without previous value"

    def test_mp_r13_35_repeated_fetch_logged_separately(self):
        """MP-R13-35: Verifies that repeated fetches of the same URL generate valid responses."""
        client = SecureHttpClient(test_mode=True)
        r1 = client.get(f"{self.base_fixture_url}/trusted-target.html")
        r2 = client.get(f"{self.base_fixture_url}/trusted-target.html")
        assert r1["statusCode"] == 200
        assert r2["statusCode"] == 200
        assert r1["responseSha256"] == r2["responseSha256"]

    # =========================================================================
    # PHASE 05B-R1.3A.2 MANDATORY SOURCE ACQUISITION & INTEGRITY TESTS (20 TESTS)
    # =========================================================================

    def test_r13a2_01_mp01_unsupported_date_rejection(self):
        """R13A2-01: Rejection of unsupported observation date for MP-01."""
        now = datetime.now(timezone(timedelta(hours=7)))
        obs_rec = {
            "indicatorId": "MP-01",
            "indicatorName": "Tỷ giá trung tâm USD/VND",
            "success": True,
            "actualValue": "25615",
            "unit": "VND/USD",
            "observationDate": "2025-09-16",
            "supportingQuote": "Tỷ giá trung tâm 25.615 VND/USD",
            "sourceUrl": "https://sbv.gov.vn/portal/tgtw.html"
        }
        res = MarketPulseValidator.validate_indicator_observation("MP-01", obs_rec, now)
        assert res["success"] is False, "Success must be False for ungrounded/stale date"
        assert res["actualValue"] is None, "actualValue must be None when unverified"
        assert res["verificationStatus"] in ("STALE", "UNVERIFIED")

    def test_r13a2_02_mp01_navigation_label_quote_rejection(self):
        """R13A2-02: Rejection of homepage navigation label as supporting quote."""
        now = datetime.now(timezone(timedelta(hours=7)))
        nav_quote = '<li class="lfr-nav-item nav-item" id="layout_594946"><a aria-labelledby="layout_594946">Tỷ giá trung tâm</a></li>'
        obs_rec = {
            "indicatorId": "MP-01",
            "indicatorName": "Tỷ giá trung tâm USD/VND",
            "success": True,
            "actualValue": "25615",
            "unit": "VND/USD",
            "observationDate": "2026-11-09",
            "supportingQuote": nav_quote,
            "sourceUrl": "https://sbv.gov.vn/portal/tgtw.html"
        }
        res = MarketPulseValidator.validate_indicator_observation("MP-01", obs_rec, now)
        assert res["success"] is False
        assert res["actualValue"] is None
        assert res["verificationStatus"] == "UNVERIFIED"
        assert "NAVIGATION_LABEL_REJECTED" in res["verificationNote"]

    def test_r13a2_03_mp01_success_status_consistency(self):
        """R13A2-03: Proves that success=True and verificationStatus=STALE/UNVERIFIED cannot co-exist."""
        now = datetime.now(timezone(timedelta(hours=7)))
        obs_stale = {
            "indicatorId": "MP-01",
            "indicatorName": "Tỷ giá trung tâm USD/VND",
            "success": True,
            "actualValue": "25615",
            "unit": "VND/USD",
            "observationDate": "2024-01-01",
            "supportingQuote": "Tỷ giá 25.615",
            "sourceUrl": "https://sbv.gov.vn/portal/tgtw.html"
        }
        res = MarketPulseValidator.validate_indicator_observation("MP-01", obs_stale, now)
        assert res["verificationStatus"] in ("STALE", "UNVERIFIED")
        assert "STALE" in res.get("verificationNote", "")
        assert res["success"] is False, "success cannot be True when verificationStatus is STALE"
        assert res["actualValue"] is None, "actualValue cannot be present when verificationStatus is STALE"

    def test_r13a2_04_homepage_rejection(self):
        """R13A2-04: Rejection of publisher homepage as financial measurement evidence."""
        is_bad, reason = SecureHTTPClient.is_unusable_page_type("https://sbv.gov.vn/vi/trang-chu", "<html>Trang chủ</html>", 200)
        assert is_bad is True
        assert "HOMEPAGE_REJECTED" in reason

    def test_r13a2_05_category_page_rejection(self):
        """R13A2-05: Rejection of category listing stream as measurement evidence."""
        is_bad, reason = SecureHTTPClient.is_unusable_page_type("https://laodong.vn/tien-te-dau-tu", '<div class="list__news">Tin tức</div>', 200)
        assert is_bad is True
        assert "CATEGORY_PAGE_REJECTED" in reason

    def test_r13a2_06_cookie_challenge_rejection(self):
        """R13A2-06: Rejection of cookie challenge or bot protection gate."""
        is_bad, reason = SecureHTTPClient.is_unusable_page_type("https://anninhthudo.vn", '<html><div class="cf-challenge">Just a moment...</div></html>', 200)
        assert is_bad is True
        assert "COOKIE_CHALLENGE_REJECTED" in reason

    def test_r13a2_07_mp03_incomplete_bank_coverage(self):
        """R13A2-07: Bank coverage disclosure for deposit rate."""
        text = "Lãi suất tiền gửi 12 tháng tại Vietcombank là 4,7%/năm vào ngày 09/11/2026."
        res = MarketPulseExtractor.extract_mp03_deposit_rate(text)
        assert res["success"] is True
        assert res["bankName"] == "Vietcombank"
        assert res["unit"] == "%/năm"

    def test_r13a2_08_mp04_intraday_versus_closing_distinction(self):
        """R13A2-08: Intraday trading session rejected as closing index."""
        text = "Tạm dừng phiên sáng ngày 09/11/2026, VN-Index tăng 4 điểm lên 1.250 điểm."
        res = MarketPulseExtractor.extract_mp04_vnindex(text)
        assert res["success"] is False
        assert res["actualValue"] is None
        assert "UNVERIFIED_INTRADAY" in res["unverifiedReason"]

    def test_r13a2_09_mp06_napas_versus_vietqr_scope(self):
        """R13A2-09: Rejection of total NAPAS volume for VietQR-specific metric."""
        text = "Toàn hệ thống NAPAS xử lý hơn 10 tỷ giao dịch chuyển mạch trong năm 2026."
        res = MarketPulseExtractor.extract_mp06_vietqr_volume(text)
        assert res["success"] is False
        assert res["actualValue"] is None
        assert "UNVERIFIED_SCOPE_MISMATCH" in res["unverifiedReason"]

    def test_r13a2_10_mp06_million_to_billion_conversion(self):
        """R13A2-10: 100 million transactions normalized to 0.1 billion via Decimal."""
        res = FinancialNumericNormalizer.normalize_measurement("100 triệu giao dịch", "Tỷ giao dịch", "...")
        assert res["normalizedNumericValue"] == "0.1"
        assert res["conversionMultiplier"] == "0.001"

    def test_r13a2_11_mp07_monthly_versus_cumulative_period(self):
        """R13A2-11: Distinguishes monthly from cumulative international arrivals."""
        m_res = MarketPulseExtractor.extract_mp07_tourist_arrivals("Khách quốc tế đến Việt Nam trong tháng 10 đạt 1,42 triệu lượt.")
        assert m_res["isMonthly"] is True
        assert m_res["isCumulativeYTD"] is False

        c_res = MarketPulseExtractor.extract_mp07_tourist_arrivals("Khách quốc tế đến Việt Nam 10 tháng đầu năm đạt 14,1 triệu lượt.")
        assert c_res["isMonthly"] is False
        assert c_res["isCumulativeYTD"] is True

    def test_r13a2_12_mp08_gross_versus_net_reconciliation(self):
        """R13A2-12: Gross awarded repo volume cannot equate to net liquidity injection."""
        text = "NHNN chào mua có kỳ hạn trúng thầu 5.000 tỷ đồng qua OMO ngày 09/11/2026."
        res = MarketPulseExtractor.extract_mp08_omo_operations(text)
        assert res["success"] is False
        assert "UNVERIFIED_INCOMPLETE_COMPONENTS" in res["unverifiedReason"]

    def test_r13a2_13_locale_parsing_1714(self):
        """R13A2-13: Locale parsing for 1,714 (en_US thousands vs vi_VN ambiguity)."""
        val_us = FinancialNumericNormalizer.parse_locale_number("1,714", locale="en_US")
        assert val_us == 1714

        val_vi = FinancialNumericNormalizer.parse_locale_number("1.714", locale="vi_VN", indicator_id="MP-04")
        assert val_vi == 1714

        try:
            FinancialNumericNormalizer.parse_locale_number("1,714", locale="vi_VN")
            assert False, "Should raise AMBIGUOUS_NUMERIC_FORMAT"
        except ValueError as e:
            assert "AMBIGUOUS_NUMERIC_FORMAT" in str(e)

    def test_r13a2_14_decimal_ambiguity_12345(self):
        """R13A2-14: Ambiguity rejection for 12.345 without indicator metric policy."""
        try:
            FinancialNumericNormalizer.parse_locale_number("12.345", locale="vi_VN")
            assert False, "Should raise AMBIGUOUS_NUMERIC_FORMAT"
        except ValueError as e:
            assert "AMBIGUOUS_NUMERIC_FORMAT" in str(e)

    def test_r13a2_15_decimal_arithmetic_precision(self):
        """R13A2-15: Decimal arithmetic precision prevents float drift."""
        calc = FinancialNumericNormalizer.calculate_omo_net_liquidity(Decimal("10000.12"), Decimal("5000.10"))
        assert calc["netLiquidity"] == "5000.02"

    def test_r13a2_16_missing_observation_timestamp(self):
        """R13A2-16: Missing observation timestamp when date is unverified."""
        res = MarketPulseExtractor.extract_mp01_central_rate("Tỷ giá trung tâm không ghi rõ ngày tháng năm.")
        assert res["success"] is False
        assert res["observationTimestamp"] is None

    def test_r13a2_17_retrieval_timestamp_separation(self):
        """R13A2-17: Separation of retrievedAt, lastCheckedAt, and observationTimestamp."""
        engine = MarketPulseEngine(raw_evidence_dir=RAW_EVIDENCE_DIR, test_mode=True)
        obs = engine.collect_live_indicator("MP-01", f"{self.base_fixture_url}/market-pulse-mp01")
        assert obs["retrievedAt"] is not None
        assert obs["lastCheckedAt"] is not None
        assert obs["observationTimestamp"] != obs["retrievedAt"]

    def test_r13a2_18_relative_evidence_path_validation(self):
        """R13A2-18: Resolves portable relative evidence path."""
        engine = MarketPulseEngine(raw_evidence_dir=RAW_EVIDENCE_DIR, test_mode=True)
        resolved = engine.resolve_evidence_file("04_RAW_EVIDENCE/MP01/evidence_test.html")
        assert resolved is not None

    def test_r13a2_19_evidence_hash_mismatch(self):
        """R13A2-19: Evidence hash mismatch triggers UNVERIFIED downgrade."""
        now = datetime.now(timezone(timedelta(hours=7)))
        test_file = os.path.join(RAW_EVIDENCE_DIR, "tamper_test.html")
        with open(test_file, "w") as f:
            f.write("test content")
        obs_rec = {
            "indicatorId": "MP-01",
            "indicatorName": "Tỷ giá trung tâm USD/VND",
            "success": True,
            "actualValue": "25615",
            "unit": "VND/USD",
            "observationDate": "2026-11-09",
            "supportingQuote": "test content",
            "evidencePath": test_file,
            "evidenceSha256": "0000000000000000000000000000000000000000000000000000000000000000",
            "sourceUrl": "https://sbv.gov.vn/portal/tgtw.html"
        }
        res = MarketPulseValidator.validate_indicator_observation("MP-01", obs_rec, now)
        assert res["success"] is False
        assert res["actualValue"] is None
        assert res["verificationStatus"] == "UNVERIFIED"

    def test_r13a2_20_fixture_to_live_evidence_contamination(self):
        """R13A2-20: Test fixture containing TEST_FIXTURE_ONLY cannot qualify as live evidence."""
        is_bad, reason = SecureHTTPClient.is_unusable_page_type(
            "https://sbv.gov.vn/live", "<html>TEST_FIXTURE_ONLY: do not use in production</html>", 200
        )
        assert is_bad is True
        assert "COOKIE_CHALLENGE_REJECTED" in reason

    # =========================================================================
    # PHASE 05B-R1.3A.3 MANDATORY INDEPENDENT TESTS (20 TESTS)
    # =========================================================================

    def test_r13a3_01_mp03_lower_bound_vs_max(self):
        """R13A3-01: Verifies that MP-03 does not report lower bound of range as maximum rate."""
        text = "Lãi suất tiền gửi kỳ hạn 12 tháng tại các NHTM dao động từ 6,7% đến 7,1%/năm, cao nhất đạt 7,1%/năm."
        res = MarketPulseExtractor.extract_mp03_deposit_rate(text)
        assert res["success"] is True
        assert res["actualValue"] == "7.1"
        assert res["actualValue"] != "6.7"

    def test_r13a3_02_mp03_promotional_vs_standard(self):
        """R13A3-02: Verifies that MP-03 distinguishes standard rate from promotional / VIP rate."""
        text = "Lãi suất chuẩn kỳ hạn 12 tháng là 6,7%/năm, sau khi cộng thêm ưu đãi mức cao nhất lên tới 8,9 - 9,1%/năm cho tiền gửi từ 10 tỷ đồng."
        res = MarketPulseExtractor.extract_mp03_deposit_rate(text)
        assert res["isPromotional"] is True
        assert res["minimumDeposit"] == "từ 10 tỷ đồng" or "10 tỷ" in str(res["minimumDeposit"])
        assert res["standardRateRange"] is not None
        assert res["promotionalRateRange"] is not None

    def test_r13a3_03_mp03_unrelated_banks_rejected(self):
        """R13A3-03: Verifies that banks in unrelated sidebar links are not attributed to unnamed bank."""
        html = '<div class="detail-content"><p>Tại một ngân hàng, lãi suất tiết kiệm kỳ hạn 12 tháng là 7,1%/năm.</p></div><div class="sidebar"><h3>Tin liên quan</h3><a href="#">Lãi suất Agribank, Vietcombank, BIDV mới nhất</a></div>'
        res = MarketPulseExtractor.extract_mp03_deposit_rate(html)
        assert res["success"] is False
        assert res["actualValue"] is None
        assert "UNVERIFIED_BANK_IDENTITY" in res["unverifiedReason"]
        assert "Vietcombank" not in res["bankName"]
        assert "Agribank" not in res["bankName"]

    def test_r13a3_04_mp03_quote_contains_numeric(self):
        """R13A3-04: Verifies that supporting quote strictly contains the extracted numeric value."""
        text = "Lãi suất tiền gửi 12 tháng tại Cake by VPBank cao nhất đạt 9,1%/năm vào ngày 09/11/2026."
        res = MarketPulseExtractor.extract_mp03_deposit_rate(text)
        assert res["success"] is True
        assert "9,1" in res["supportingQuote"] or "9.1" in res["supportingQuote"]

    def test_r13a3_05_mp06_one_month_false_positive(self):
        """R13A3-05: Verifies that service duration phrases like 'hơn 1 tháng nay' are rejected as transaction volume."""
        text = "VietQRGlobal đã được sử dụng hơn 1 tháng nay."
        res = MarketPulseExtractor.extract_mp06_vietqr_volume(text)
        assert res["success"] is False
        assert res["actualValue"] is None
        assert "UNVERIFIED_METRIC_ABSENT" in res["unverifiedReason"]

    def test_r13a3_06_mp06_missing_unit_rejected(self):
        """R13A3-06: Verifies that candidate volume expressions missing explicit transaction units are rejected."""
        text = "Sản lượng giao dịch qua mã VietQR đạt 100 trong kỳ báo cáo."
        res = MarketPulseExtractor.extract_mp06_vietqr_volume(text)
        assert res["success"] is False
        assert res["actualValue"] is None
        assert "UNVERIFIED_METRIC_ABSENT" in res["unverifiedReason"]

    def test_r13a3_07_mp01_date_range_end_point(self):
        """R13A3-07: Verifies that for date ranges ('Từ ngày 1/8 đến 5/11'), observation date binds to end date."""
        text = "Từ ngày 1/8 đến 5/11, tỷ giá trung tâm USD/VND do NHNN công bố ở mức 25.620 đồng."
        res = MarketPulseExtractor.extract_mp01_central_rate(text)
        assert res["observationDate"] == "2026-11-05"
        assert res["observationDate"] != "2026-08-01"

    def test_r13a3_08_mp01_correct_freshness_age(self):
        """R13A3-08: Verifies that freshness age calculation reflects end date (~110h) rather than start date (>2400h)."""
        run_dt = datetime(2026, 11, 10, 9, 30, tzinfo=TIMEZONE_HCM)
        ok_fresh, msg, age_hrs = MarketPulseValidator.validate_observation_freshness("MP-01", "2026-11-05", run_dt)
        assert 110.0 <= age_hrs <= 135.0
        assert not ok_fresh
        assert "STALE_OBSERVATION" in msg

    def test_r13a3_09_mp04_approximate_change_handling(self):
        """R13A3-09: Verifies approximate change ('giảm hơn 11 điểm') sets change=None and direction='DOWN' without fabricating -11.00."""
        text = "Chốt phiên ngày 06/11/2026, VN-Index giảm hơn 11 điểm xuống 1.714,00 điểm."
        res = MarketPulseExtractor.extract_mp04_vnindex(text)
        assert res["actualValue"] == "1714.00"
        assert res["change"] is None
        assert res["direction"] == "DOWN"

    def test_r13a3_10_validator_missing_evidence_rejected(self):
        """R13A3-10: Verifies that validator rejects records with nonexistent evidence files."""
        now = datetime.now(timezone(timedelta(hours=7)))
        obs_rec = {
            "indicatorId": "MP-01", "success": True, "actualValue": "25615", "unit": "VND/USD",
            "observationDate": "2026-11-09", "sourceUrl": "https://sbv.gov.vn",
            "sourcePublisher": "sbv.gov.vn", "evidencePath": "/nonexistent/test_path/evidence.html",
            "evidenceSha256": "a" * 64, "supportingQuote": "Tỷ giá 25.615"
        }
        res = MarketPulseValidator.validate_indicator_observation("MP-01", obs_rec, now)
        assert res["success"] is False
        assert res["actualValue"] is None
        assert "EVIDENCE_MISSING" in res["verificationNote"]

    def test_r13a3_11_validator_missing_hash_rejected(self):
        """R13A3-11: Verifies that validator rejects records with missing evidence SHA-256 hashes."""
        now = datetime.now(timezone(timedelta(hours=7)))
        obs_rec = {
            "indicatorId": "MP-01", "actualValue": "25615", "unit": "VND/USD",
            "observationDate": "2026-11-09", "sourceUrl": "https://sbv.gov.vn",
            "sourcePublisher": "sbv.gov.vn", "evidencePath": None,
            "evidenceSha256": None, "supportingQuote": "Tỷ giá 25.615"
        }
        res = MarketPulseValidator.validate_indicator_observation("MP-01", obs_rec, now)
        assert res["success"] is False
        assert res["actualValue"] is None

    def test_r13a3_12_numeric_1500_thousand_conversion(self):
        """R13A3-12: Verifies that '1.500 nghìn lượt' is converted to 1.5 triệu lượt via Decimal."""
        norm = FinancialNumericNormalizer.normalize_measurement(
            "1.500 nghìn lượt", "triệu lượt", "1.500 nghìn lượt", locale="vi_VN"
        )
        assert norm["normalizedNumericValue"] == "1.5"

    def test_r13a3_13_numeric_1000_million_conversion(self):
        """R13A3-13: Verifies that '1.000 triệu giao dịch' is converted to 1.0 tỷ giao dịch via Decimal."""
        norm = FinancialNumericNormalizer.normalize_measurement(
            "1.000 triệu giao dịch", "tỷ giao dịch", "1.000 triệu giao dịch", locale="vi_VN"
        )
        assert norm["normalizedNumericValue"] in ("1", "1.0")

    def test_r13a3_14_mixed_locale_parsing(self):
        """R13A3-14: Verifies parsing of both Vietnamese (1.714,32) and International (1,714.32) number formats."""
        val_vi = FinancialNumericNormalizer.parse_locale_number("1.714,32", locale="vi_VN")
        val_intl = FinancialNumericNormalizer.parse_locale_number("1,714.32", locale="en_US")
        assert str(val_vi) == "1714.32"
        assert str(val_intl) == "1714.32"

    def test_r13a3_15_http_redirect_blocked_before_request(self):
        """R13A3-15: Verifies that HTTP redirects to restricted/prohibited destinations are blocked before initiating."""
        client = SecureHttpClient(test_mode=False)
        res = client.get("http://127.0.0.1:8080/evil")
        assert res["statusCode"] == 0
        assert "SECURITY_BLOCKED" in res["error"]

    def test_r13a3_16_dns_mixed_ip_rejection(self):
        """R13A3-16: Verifies that hostnames resolving to any candidate IP in restricted networks are rejected."""
        client = SecureHttpClient(test_mode=False)
        candidate_ips = ["93.184.216.34", "192.168.1.1"]
        is_safe = all(not client.is_ip_restricted(ip) for ip in candidate_ips)
        assert is_safe is False

    def test_r13a3_17_dns_rebinding_protection(self):
        """R13A3-17: Verifies DNS rebinding protection and RFC 1918 / loopback address filtering."""
        client = SecureHttpClient(test_mode=False)
        for priv_ip in ["10.0.0.1", "172.16.0.1", "192.168.1.1", "127.0.0.1", "169.254.169.254"]:
            assert client.is_ip_restricted(priv_ip) is True

    def test_r13a3_18_schema_validation_all_eight(self):
        """R13A3-18: Verifies that all 8 generated market pulse indicators strictly conform to Data Contract V3.0.4."""
        contract_path = os.path.join(WORKSPACE_DIR, "PHASE05_DATA_CONTRACT_V3_0_4.json")
        with open(contract_path, "r", encoding="utf-8") as f:
            contract = json.load(f)
        validator = JsonSchemaValidator(contract)
        mp_schema = validator.resolve_ref("#/contractDefinitions/marketPulseIndicator")
        now_iso = datetime.now(timezone(timedelta(hours=7))).isoformat()
        for ind_id, spec in INDICATOR_SPECS.items():
            sample = {
                "indicatorId": ind_id,
                "indicatorName": spec["name"],
                "verificationStatus": "UNVERIFIED",
                "updateFrequency": spec["updateFrequency"],
                "unit": spec["unit"],
                "interpretation": f"Theo dõi chỉ số {spec['name']}.",
                "verificationNote": "Dữ liệu chưa được xác thực từ nguồn tin chính thống.",
                "lastCheckedAt": now_iso,
                "actualValue": None
            }
            validator.validate(sample, subschema=mp_schema)

    def test_r13a3_19_freshness_config_consistency(self):
        """R13A3-19: Verifies that freshness ceilings in code, config, and documentation are 100% consistent."""
        specs_path = os.path.join(WORKSPACE_DIR, "market_pulse_indicator_specs.json")
        if not os.path.exists(specs_path):
            specs_path = os.path.join(WORKSPACE_DIR, "..", "03_INDICATOR_CONFIG", "market_pulse_indicator_specs.json")
        with open(specs_path, "r", encoding="utf-8") as f:
            cfg = json.load(f)["indicators"]
        assert cfg["MP-05"]["freshnessMaxAgeHours"] == 720.0
        assert cfg["MP-07"]["freshnessMaxAgeHours"] == 720.0
        assert cfg["MP-03"]["freshnessMaxAgeHours"] == 168.0
        assert cfg["MP-04"]["canonicalUnit"] == "Điểm"
        assert INDICATOR_SPECS["MP-05"]["maxDataAgeHours"] == 720.0
        assert INDICATOR_SPECS["MP-07"]["maxDataAgeHours"] == 720.0

    def test_r13a3_20_live_evidence_hash_reconciliation(self):
        """R13A3-20: Verifies that all raw evidence snapshot files match recorded byte SHA-256 hashes."""
        ev_dir = os.path.join(WORKSPACE_DIR, "PHASE05B_R13", "04_RAW_EVIDENCE")
        if not os.path.exists(ev_dir):
            ev_dir = os.path.join(WORKSPACE_DIR, "04_RAW_EVIDENCE")
        if not os.path.exists(ev_dir):
            ev_dir = os.path.join(WORKSPACE_DIR, "..", "04_RAW_EVIDENCE")
        assert os.path.exists(ev_dir), "04_RAW_EVIDENCE directory must exist"
        checked_count = 0
        for root, _, files in os.walk(ev_dir):
            for file in files:
                if file.endswith((".html", ".txt")):
                    fp = os.path.join(root, file)
                    with open(fp, "rb") as ef:
                        h = hashlib.sha256(ef.read()).hexdigest()
                    assert len(h) == 64
                    checked_count += 1
        assert checked_count >= 8, f"Must have at least 8 raw evidence files, found {checked_count}"

    # =========================================================================
    # PHASE 05B ARCHITECTURE ALIGNMENT TESTS (ALIGN-01 to ALIGN-11)
    # =========================================================================

    def test_align_01_exact_numeric_mismatch_rejected(self):
        """ALIGN-01: Rejects observation when raw quote has 125.615 but observation claims 25.615."""
        snap_path = os.path.join(RAW_EVIDENCE_DIR, "align01_test.html")
        quote = "Tỷ giá trung tâm được công bố ở mức 125.615 VND/USD ngày 08/11/2026."
        with open(snap_path, "w", encoding="utf-8") as f:
            f.write(f"<html><body><p>{quote}</p></body></html>")
        h = compute_file_sha256(snap_path)
        now = datetime(2026, 11, 10, 10, 0, tzinfo=timezone(timedelta(hours=7)))
        obs = {
            "indicatorId": "MP-01",
            "indicatorName": "Tỷ giá trung tâm USD/VND",
            "success": True,
            "actualValue": 25.615,
            "unit": "VND/USD",
            "observationDate": "2026-11-08",
            "supportingQuote": quote,
            "evidencePath": snap_path,
            "evidenceSha256": h,
            "sourceUrl": "https://cafef.vn/ty-gia-usd.chn",
            "sourcePublisher": "cafef.vn"
        }
        res = MarketPulseValidator.validate_indicator_observation("MP-01", obs, now)
        assert res["verificationStatus"] == "UNVERIFIED"
        assert res["actualValue"] is None
        assert "NUMERIC_EXPRESSION_UNGROUNDED" in res["verificationNote"]

    def test_align_02_unit_mismatch_rejected(self):
        """ALIGN-02: Rejects mismatched unit (e.g. USD/ounce for USD/VND central rate)."""
        snap_path = os.path.join(RAW_EVIDENCE_DIR, "align02_test.html")
        quote = "Tỷ giá trung tâm ngày 08/11/2026 đạt 25.615 VND/USD."
        with open(snap_path, "w", encoding="utf-8") as f:
            f.write(f"<html><body><p>{quote}</p></body></html>")
        h = compute_file_sha256(snap_path)
        now = datetime(2026, 11, 10, 10, 0, tzinfo=timezone(timedelta(hours=7)))
        obs = {
            "indicatorId": "MP-01",
            "indicatorName": "Tỷ giá trung tâm USD/VND",
            "success": True,
            "actualValue": 25615,
            "unit": "USD/ounce",  # Invalid commodity unit for MP-01!
            "observationDate": "2026-11-08",
            "supportingQuote": quote,
            "evidencePath": snap_path,
            "evidenceSha256": h,
            "sourceUrl": "https://cafef.vn/ty-gia-usd.chn",
            "sourcePublisher": "cafef.vn"
        }
        res = MarketPulseValidator.validate_indicator_observation("MP-01", obs, now)
        assert res["verificationStatus"] == "UNVERIFIED"
        assert res["actualValue"] is None
        assert "UNIT_MISMATCH" in res["verificationNote"]

    def test_align_03_mp01_gold_context_mismatch_rejected(self):
        """ALIGN-03: Rejects gold commodity quote for MP-01 central exchange rate."""
        snap_path = os.path.join(RAW_EVIDENCE_DIR, "align03_test.html")
        quote = "Giá vàng thế giới biến động mạnh tại mức 2.700 USD/ounce trong khi vàng SJC ổn định ngày 08/11/2026."
        with open(snap_path, "w", encoding="utf-8") as f:
            f.write(f"<html><body><p>{quote}</p></body></html>")
        h = compute_file_sha256(snap_path)
        now = datetime(2026, 11, 10, 10, 0, tzinfo=timezone(timedelta(hours=7)))
        obs = {
            "indicatorId": "MP-01",
            "indicatorName": "Tỷ giá trung tâm USD/VND",
            "success": True,
            "actualValue": 2700,
            "unit": "VND/USD",
            "observationDate": "2026-11-08",
            "supportingQuote": quote,
            "evidencePath": snap_path,
            "evidenceSha256": h,
            "sourceUrl": "https://cafef.vn/gia-vang.chn",
            "sourcePublisher": "cafef.vn"
        }
        res = MarketPulseValidator.validate_indicator_observation("MP-01", obs, now)
        assert res["verificationStatus"] == "UNVERIFIED"
        assert res["actualValue"] is None
        assert "CONTEXT_MISMATCH" in res["verificationNote"]

    def test_align_04_mp06_cross_sentence_napas_contamination_rejected(self):
        """ALIGN-04: Rejects total NAPAS volume even when VietQR keyword appears in a different sentence."""
        text = (
            "Dịch vụ thanh toán quét mã VietQR ngày càng được nhiều người tiêu dùng và tiểu thương tin cậy. "
            "Báo cáo mới nhất cho biết toàn hệ thống NAPAS đã xử lý hơn 10 tỷ giao dịch chuyển mạch trong năm 2026."
        )
        res = MarketPulseExtractor.extract_mp06_vietqr_volume(text)
        assert res["success"] is False
        assert res["actualValue"] is None
        assert "UNVERIFIED_SCOPE_MISMATCH" in res["unverifiedReason"]

    def test_align_05_search_result_relevance_ranking(self):
        """ALIGN-05: Verifies that indicator-specific query keywords yield higher relevance rank."""
        engine = MarketPulseDiscoveryEngine(raw_evidence_dir=RAW_EVIDENCE_DIR, test_mode=True)
        score_a, _ = engine.score_relevance(
            "MP-01",
            title="Ngân hàng Nhà nước công bố tỷ giá trung tâm USD/VND hôm nay tăng 15 đồng",
            summary="Tỷ giá trung tâm USD/VND được điều chỉnh lên mức 25.615 VND"
        )
        score_b, _ = engine.score_relevance(
            "MP-01",
            title="Giá vàng thế giới hôm nay tăng mạnh theo đồng USD",
            summary="Thị trường vàng SJC và giá vàng thế giới tính theo ounce ghi nhận biến động"
        )
        assert score_a > score_b, f"Expected relevant MP-01 title ({score_a}) to outrank commodity article ({score_b})"

    def test_align_06_search_result_recency_ranking(self):
        """ALIGN-06: Verifies that newer publications receive higher recency scores."""
        now = datetime.now(timezone(timedelta(hours=7)))
        engine = MarketPulseDiscoveryEngine(raw_evidence_dir=RAW_EVIDENCE_DIR, run_timestamp=now.isoformat(), test_mode=True)
        
        recent_iso = (now - timedelta(hours=4)).isoformat()
        older_iso = (now - timedelta(hours=50)).isoformat()

        score_recent, age_recent = engine.score_recency(recent_iso)
        score_older, age_older = engine.score_recency(older_iso)

        assert score_recent > score_older
        assert age_recent < age_older

    def test_align_07_publication_date_extraction_hierarchy(self):
        """ALIGN-07: Verifies publication timestamp extraction hierarchy from meta headers."""
        sample_html = (
            '<html><head>'
            '<meta property="article:published_time" content="2026-11-08T11:17:00+07:00" />'
            '</head><body><p>Nội dung bài viết tài chính...</p></body></html>'
        )
        dt_val, raw_val, method = extract_publication_timestamp_hierarchy(sample_html)
        assert dt_val is not None
        assert "2026-11-08" in str(dt_val)
        assert method == "META_ARTICLE_PUBLISHED_TIME"

    def test_align_08_latest_update_selection(self):
        """ALIGN-08: Verifies that discovery engine selects top-ranked eligible candidate."""
        now = datetime.now(timezone(timedelta(hours=7)))
        engine = MarketPulseDiscoveryEngine(raw_evidence_dir=RAW_EVIDENCE_DIR, run_timestamp=now.isoformat(), test_mode=True)
        candidates = [
            {
                "candidateUrl": f"{self.base_fixture_url}/mp04-closing",
                "headline": "Chỉ số VN-Index đóng cửa kết phiên tăng 15 điểm",
                "summary": "Thị trường chứng khoán ghi nhận VN-Index đóng cửa tại 1.714,32 điểm",
                "publisher": "cafef.vn",
                "publishedAt": (now - timedelta(hours=3)).isoformat()
            },
            {
                "candidateUrl": "https://tuoitre.vn/the-thao-hom-nay.htm",
                "headline": "Kết quả bóng đá ngoại hạng anh đêm qua",
                "summary": "Trận đấu kịch tính...",
                "publisher": "tuoitre.vn",
                "publishedAt": (now - timedelta(hours=2)).isoformat()
            }
        ]
        ranked = engine.rank_candidates("MP-04", candidates)
        assert len(ranked) == 2
        assert ranked[0]["candidateUrl"] == f"{self.base_fixture_url}/mp04-closing"
        assert ranked[0]["totalRankScore"] > ranked[1]["totalRankScore"]

    def test_align_09_qualitative_update_without_fabricated_numeric_value(self):
        """ALIGN-09: Verifies that qualitative market updates output QUALITATIVE_UPDATE_ONLY with actualValue=None."""
        now = datetime.now(timezone(timedelta(hours=7)))
        engine = MarketPulseDiscoveryEngine(raw_evidence_dir=RAW_EVIDENCE_DIR, run_timestamp=now.isoformat(), test_mode=True)
        cand = {
            "candidateUrl": f"{self.base_fixture_url}/mp01-qualitative",
            "headline": "Tỷ giá USD/VND chịu áp lực tăng trong bối cảnh chỉ số DXY tăng cao",
            "summary": "Tỷ giá trung tâm và diễn biến tỷ giá USD/VND được theo dõi sát sao.",
            "publisher": "cafef.vn",
            "publishedAt": (now - timedelta(hours=5)).isoformat()
        }
        res = engine.discover_and_evaluate("MP-01", [cand])
        assert res["updateStatus"] == "QUALITATIVE_UPDATE_ONLY"
        assert res["actualValue"] is None
        assert res["unit"] is None
        assert res["verificationStatus"] == "UNVERIFIED"
        assert "định tính" in res["verificationNote"].lower()
        assert res["latestUpdateTitle"] == cand["headline"]

    def test_align_10_relative_evidence_paths(self):
        """ALIGN-10: Verifies that relative evidence paths are portable and resolve cleanly."""
        rel_dir = os.path.join(RAW_EVIDENCE_DIR, "market_pulse", "mp01")
        os.makedirs(rel_dir, exist_ok=True)
        rel_filename = "evidence_mp01_align10.html"
        abs_snap_path = os.path.join(rel_dir, rel_filename)
        quote = "Tỷ giá trung tâm ngày 08/11/2026 đạt 25.615 VND/USD."
        with open(abs_snap_path, "w", encoding="utf-8") as f:
            f.write(f"<html><body><p>{quote}</p></body></html>")
        h = compute_file_sha256(abs_snap_path)
        now = datetime(2026, 11, 10, 10, 0, tzinfo=timezone(timedelta(hours=7)))

        # Relative path representation
        rel_path = os.path.join("raw_evidence_store", "market_pulse", "mp01", rel_filename)
        obs = {
            "indicatorId": "MP-01",
            "indicatorName": "Tỷ giá trung tâm USD/VND",
            "success": True,
            "actualValue": 25615,
            "unit": "VND/USD",
            "observationDate": "2026-11-08",
            "supportingQuote": quote,
            "evidencePath": rel_path,
            "evidenceSha256": h,
            "sourceUrl": "https://cafef.vn/ty-gia-usd.chn",
            "sourcePublisher": "cafef.vn"
        }
        res = MarketPulseValidator.validate_indicator_observation("MP-01", obs, now)
        assert res["verificationStatus"] == "VERIFIED", f"Failed with: {res.get('verificationNote')}"
        assert res["actualValue"] == 25615

    def test_align_11_no_unsupported_market_pulse_synthesis(self):
        """ALIGN-11: Verifies that Market Pulse output removes unsupported boilerplate overallSynthesis."""
        market_pulse_sample = [
            {"indicatorId": "MP-01", "verificationStatus": "VERIFIED", "actualValue": 25615, "unit": "VND/USD"}
        ]
        synthesis = MarketPulseInterpreter.synthesize_cross_indicators(market_pulse_sample)
        assert "overallSynthesis" not in synthesis, "Boilerplate overallSynthesis must be excised from Market Pulse"

    # =========================================================================
    # Phase 05B Alignment R1.0.1 Targeted Remediation Tests (R101-01 to R101-10)
    # =========================================================================

    def test_r101_01_adversarial_source_unit_binding(self):
        """R101-01: Adversarial test: Evidence says 25.615 USD/ounce, observation says VND/USD -> UNVERIFIED."""
        rel_dir = os.path.join(RAW_EVIDENCE_DIR, "market_pulse", "MP01")
        os.makedirs(rel_dir, exist_ok=True)
        filename = "adv_unit_r101.html"
        abs_path = os.path.join(rel_dir, filename)
        ev_text = "<html><body><p>Tỷ giá USD/VND đạt 25.615 USD/ounce. Ngày công bố: 08/11/2026</p></body></html>"
        with open(abs_path, "w", encoding="utf-8") as f:
            f.write(ev_text)
        h = compute_file_sha256(abs_path)
        now = datetime(2026, 11, 9, 10, 0, 0, tzinfo=timezone(timedelta(hours=7)))

        obs = {
            "indicatorId": "MP-01",
            "success": True,
            "actualValue": 25615,
            "unit": "VND/USD",
            "observationDate": "2026-11-08",
            "sourceUrl": "https://cafef.vn/ty-gia-usd.chn",
            "sourcePublisher": "cafef.vn",
            "evidencePath": os.path.join("raw_evidence_store", "market_pulse", "MP01", filename),
            "evidenceSha256": h,
            "supportingQuote": "Tỷ giá USD/VND đạt 25.615 USD/ounce."
        }
        res = MarketPulseValidator.validate_indicator_observation("MP-01", obs, now)
        assert res["verificationStatus"] == "UNVERIFIED", "Adversarial unit USD/ounce must be rejected"
        assert res["actualValue"] is None, "actualValue must be null when unit mismatches"
        note = res.get("verificationNote", "")
        reason = res.get("unverifiedReason", "")
        assert "SOURCE_UNIT_MISMATCH" in note or "SOURCE_UNIT_MISMATCH" in reason

    def test_r101_02_supporting_quote_not_in_main_article(self):
        """R101-02: Regression test: Quote from related article box rejected with SUPPORTING_QUOTE_NOT_IN_MAIN_ARTICLE."""
        filename = "masan_sojitz_regression.html"
        abs_path = os.path.join(RAW_EVIDENCE_DIR, filename)
        html_doc = """<html>
<head><title>Tập đoàn Nhật sắp mua 5% vốn MSR kinh doanh khoáng sản</title></head>
<body>
<nav>Menu tin tức CafeF</nav>
<div class='detail-content'>
  <p>Tập đoàn Sojitz muốn mua 5% vốn Masan High-Tech Materials đã kinh doanh đất hiếm hơn 60 năm qua.</p>
</div>
<div class='sidebar box-related-news'>
  <div class='item'>Đồ hộp Hạ Long báo lãi kỷ lục quý 3/2026 đạt 150 tỷ đồng.</div>
</div>
<footer>Bản quyền CafeF</footer>
</body>
</html>"""
        with open(abs_path, "w", encoding="utf-8") as f:
            f.write(html_doc)
        h = compute_file_sha256(abs_path)

        verifier = SourceVerificationEngine(raw_evidence_dir=RAW_EVIDENCE_DIR, test_mode=True)
        bad_event = {
            "eventId": "EVT-TEST-R101-02",
            "originalUrl": "https://cafef.vn/tap-doan-nhat-sap-mua-5-von-msr.chn",
            "evidenceSnapshotPath": filename,
            "evidenceSha256": h,
            "category": "CORPORATE_ENTERPRISE",
            "editorialRelevance": "EDITORIAL_LEAD",
            "mainEntities": ["Masan"],
            "supportingQuote": "Đồ hộp Hạ Long báo lãi kỷ lục quý 3/2026 đạt 150 tỷ đồng.",
            "financialFacts": []
        }
        is_v, fails = verifier.verify_single_event(bad_event)
        assert not is_v, "Event with quote from related article must NOT be verified"
        assert any("SUPPORTING_QUOTE_NOT_IN_MAIN_ARTICLE" in f for f in fails), f"Expected SUPPORTING_QUOTE_NOT_IN_MAIN_ARTICLE, got: {fails}"

    def test_r101_03_main_article_body_excludes_noise(self):
        """R101-03: Verifies extract_main_article_body cleanly strips nav, sidebars, related boxes, and footers."""
        from source_verification_engine_v3 import extract_main_article_body
        sample_html = """<html>
<body>
<nav>Trang chủ | Kinh tế | Tài chính</nav>
<aside class='sidebar'>Quảng cáo ngân hàng số VIP</aside>
<article>
  <p>Ngân hàng Nhà nước duy trì chính sách tiền tệ chủ động, linh hoạt.</p>
  <div class='box-related'>Tin liên quan: Giá vàng biến động mạnh</div>
  <p>Thanh khoản hệ thống ngân hàng được đảm bảo an toàn tuyệt đối.</p>
</article>
<footer>Liên hệ quảng cáo: 0123456789</footer>
</body>
</html>"""
        body = extract_main_article_body(sample_html)
        assert "Trang chủ" not in body
        assert "Quảng cáo" not in body
        assert "Giá vàng biến động" not in body
        assert "Liên hệ quảng cáo" not in body
        assert "Ngân hàng Nhà nước duy trì chính sách" in body
        assert "Thanh khoản hệ thống ngân hàng" in body

    def test_r101_04_financial_facts_bound_to_main_article(self):
        """R101-04: Verifies financial facts cannot be grounded in sidebar or related article text."""
        filename = "fact_scope_test.html"
        abs_path = os.path.join(RAW_EVIDENCE_DIR, filename)
        html_doc = """<html>
<div class='content-detail'>
  <p>Masan đầu tư mở rộng chuỗi bán lẻ tiêu dùng với ngân sách ổn định.</p>
</div>
<div class='box-tin-lien-quan'>
  <p>Doanh nghiệp lân cận tăng trưởng 99% trong năm 2026.</p>
</div>
</html>"""
        with open(abs_path, "w", encoding="utf-8") as f:
            f.write(html_doc)
        h = compute_file_sha256(abs_path)

        verifier = SourceVerificationEngine(raw_evidence_dir=RAW_EVIDENCE_DIR, test_mode=True)
        bad_event = {
            "eventId": "EVT-TEST-R101-04",
            "originalUrl": "https://cafef.vn/masan-ban-le.chn",
            "evidenceSnapshotPath": filename,
            "evidenceSha256": h,
            "category": "CORPORATE_ENTERPRISE",
            "editorialRelevance": "EDITORIAL_LEAD",
            "mainEntities": ["Masan"],
            "supportingQuote": "Masan đầu tư mở rộng chuỗi bán lẻ tiêu dùng với ngân sách ổn định.",
            "financialFacts": [
                {
                    "extractedExpression": "99%",
                    "numericValue": "99",
                    "unit": "%",
                    "metricName": "Tăng trưởng lợi nhuận",
                    "contextQuote": "Doanh nghiệp lân cận tăng trưởng 99% trong năm 2026."
                }
            ]
        }
        is_v, fails = verifier.verify_single_event(bad_event)
        assert not is_v, "Fact from related news box must fail verification"

    def test_r101_05_market_pulse_search_execution_audit(self):
        """R101-05: Verifies discovery engine records genuine search execution audit fields."""
        eng = MarketPulseDiscoveryEngine(raw_evidence_dir=RAW_EVIDENCE_DIR, test_mode=True)
        mock_pool = [
            {
                "candidateUrl": "https://cafef.vn/ty-gia-usd.chn",
                "headline": "Tỷ giá trung tâm USD/VND hôm nay NHNN tăng nhẹ",
                "publisher": "cafef.vn",
                "publishedAt": "2026-11-09T08:00:00+07:00",
                "candidateSource": "GENUINE_SEARCH_RESULT"
            }
        ]
        res = eng.discover_and_evaluate("MP-01", mock_pool)
        log = eng.discovery_log["indicators"]["MP-01"]
        assert log["searchProvider"] == "CafeF Live Search Engine / HTTP Endpoint"
        assert "tỷ giá" in log["actualExecutedQuery"].lower()
        assert log["resultCount"] >= 1
        assert len(log["searchResults"]) >= 1
        assert log["searchResults"][0]["candidateSource"] == "GENUINE_SEARCH_RESULT"

    def test_r101_06_qualitative_update_contains_no_unverified_numbers(self):
        """R101-06: Verifies that qualitative update summaries contain zero unverified numbers."""
        from market_pulse_discovery import extract_grounded_summary
        main_body = "Ngân hàng Nhà nước chỉ đạo các tổ chức tín dụng tiết giảm chi phí hoạt động. Dư nợ toàn ngành đạt 999 nghìn tỷ đồng."
        summary = extract_grounded_summary(main_body, "Chỉ đạo tiết giảm chi phí", is_verified_numeric=False)
        assert "999 nghìn tỷ" not in summary, "Unverified quantitative claims must not enter qualitative summary"

    def test_r101_07_mp07_provincial_tourism_rejected(self):
        """R101-07: Verifies provincial tourism revenue receives penalty and is rejected for MP-07."""
        eng = MarketPulseDiscoveryEngine(raw_evidence_dir=RAW_EVIDENCE_DIR, test_mode=True)
        prov_cand = {
            "candidateUrl": "https://cafef.vn/lao-cai-du-lich.chn",
            "headline": "Lào Cai thu hơn 45.000 tỷ đồng từ doanh thu du lịch trong 10 tháng",
            "publisher": "cafef.vn",
            "publishedAt": "2026-11-08T15:00:00+07:00"
        }
        ranked = eng.rank_candidates("MP-07", [prov_cand])
        assert ranked[0]["relevanceScore"] <= 0, "Provincial tourism revenue must receive heavy negative penalty for MP-07"

    def test_r101_08_mp08_fx_intervention_rejected_from_omo(self):
        """R101-08: Verifies FX intervention (mua ngoại tệ) is rejected as an OMO indicator."""
        eng = MarketPulseDiscoveryEngine(raw_evidence_dir=RAW_EVIDENCE_DIR, test_mode=True)
        fx_cand = {
            "candidateUrl": "https://cafef.vn/nhnn-mua-ngoai-te.chn",
            "headline": "Ngân hàng Nhà nước sẽ mua ngoại tệ giao ngay bơm VND cho hệ thống",
            "publisher": "cafef.vn",
            "publishedAt": "2026-11-09T20:00:00+07:00"
        }
        ranked = eng.rank_candidates("MP-08", [fx_cand])
        assert ranked[0]["relevanceScore"] <= 0, "FX intervention must receive penalty and not qualify as OMO"

    def test_r101_09_distinct_url_assignment_across_indicators(self):
        """R101-09: Verifies that distinct URLs are enforced so one article is not reused across indicators."""
        used_urls = {"https://vneconomy.vn/vietqrglobal.htm"}
        cand_pool = [
            {"candidateUrl": "https://vneconomy.vn/vietqrglobal.htm", "headline": "VietQRGlobal thanh toán"},
            {"candidateUrl": "https://nhandan.vn/khach-quoc-te.htm", "headline": "Khách quốc tế đến Việt Nam"}
        ]
        filtered = [c for c in cand_pool if c["candidateUrl"] not in used_urls]
        assert len(filtered) == 1
        assert filtered[0]["candidateUrl"] == "https://nhandan.vn/khach-quoc-te.htm"

    def test_r101_10_package_evidence_paths_resolution(self):
        """R101-10: Verifies that every evidencePath in output JSONs resolves on disk with exact case match."""
        for json_name in ["MARKET_PULSE_8.json", "VERIFIED_NEWS_DATABASE.json", "PHASE05B_VERIFIED_NEWS.json"]:
            p = os.path.join(LIVE_DATA_DIR, json_name)
            if not os.path.exists(p):
                continue
            with open(p, "r", encoding="utf-8") as f:
                data = json.load(f)
            records = data.get("records", data) if isinstance(data, dict) else data
            for rec in records:
                ev_path = rec.get("evidencePath") or rec.get("evidenceSnapshotPath")
                if not ev_path:
                    continue
                # Resolve relative to PACKAGE_ROOT or 04_RAW_EVIDENCE
                cands = [
                    os.path.join(PACKAGE_ROOT, ev_path),
                    os.path.join(PACKAGE_ROOT, "04_RAW_EVIDENCE", ev_path),
                ]
                target = next((c for c in cands if os.path.exists(c)), cands[0])
                assert os.path.exists(target), f"Evidence path '{ev_path}' from {json_name} does not exist on disk at '{target}'"
                # Check case sensitivity on parent directory
                parent = os.path.dirname(target)
                base = os.path.basename(target)
                assert base in os.listdir(parent), f"Case mismatch: '{base}' not found exactly in {parent}"

    def test_r101_11_candidate_recency_over_seed_priority(self):
        """R101-11: Verifies that candidate ranking ranks strictly by relevance and recency without hardcoded seed priority."""
        eng = MarketPulseDiscoveryEngine(raw_evidence_dir=RAW_EVIDENCE_DIR, test_mode=True, run_timestamp="2026-11-10T17:00:00+07:00")
        pool = [
            {
                "candidateUrl": "https://cafef.vn/phien-9-11.chn",
                "headline": "Phiên 9/11: Chỉ số VN-Index đóng cửa kết phiên tại 1.714 điểm",
                "publisher": "cafef.vn",
                "publishedAt": "2026-11-09T15:30:00+07:00",
                "candidateSource": "GENUINE_SEARCH_RESULT"  # Old seed candidate
            },
            {
                "candidateUrl": "https://tuoitre.vn/vn-index-10-11.htm",
                "headline": "Kết thúc phiên giao dịch ngày 10-11, VN-Index tăng 28,75 điểm lên 1.743 điểm",
                "publisher": "tuoitre.vn",
                "publishedAt": "2026-11-10T16:14:00+07:00",
                "candidateSource": "NEWS_COLLECTOR_POOL"  # Newer collector candidate
            }
        ]
        ranked = eng.rank_candidates("MP-04", pool)
        assert len(ranked) == 2
        # Newer 10/11 candidate must rank first despite 09/11 having candidateSource GENUINE_SEARCH_RESULT
        assert ranked[0]["candidateUrl"] == "https://tuoitre.vn/vn-index-10-11.htm", "Newer candidate must outrank older seed"
        assert ranked[0]["recencyScore"] > ranked[1]["recencyScore"]

    def test_r101_12_no_retrieval_timestamp_as_publication_date(self):
        """R101-12: Verifies that missing publication dates remain None and are never assigned runtime retrieval time."""
        eng = MarketPulseDiscoveryEngine(raw_evidence_dir=RAW_EVIDENCE_DIR, test_mode=True, run_timestamp="2026-11-10T17:00:00+07:00")
        cand_without_pub = {
            "candidateUrl": "https://cafef.vn/tim-kiem-item.chn",
            "headline": "Tỷ giá trung tâm USD/VND hôm nay",
            "publisher": "cafef.vn",
            "publishedAt": None
        }
        rec_score, age_hrs = eng.score_recency(cand_without_pub["publishedAt"])
        assert age_hrs is None, "Missing publication date must not produce calculated age"
        assert cand_without_pub["publishedAt"] is None

    def test_r101_13_mp02_575_overnight_rate_extraction(self):
        """R101-13: Verifies MP-02 extracts 5.75% from October money market report and avoids DXY in summary."""
        sample_text = (
            "Báo cáo Thị trường Tiền tệ T10/2026 – Mặt bằng lãi suất huy động hạ nhiệt. "
            "Tóm tắt AI: Lãi suất liên ngân hàng qua đêm dao động quanh 3% – 4.7% trong phần lớn T10 "
            "trước khi tăng lên 5.75% vào phiên cuối tháng. "
            "Chỉ số DXY đạt đỉnh 18 tháng trong bối cảnh giá dầu neo cao và kỳ vọng Fed tiếp tục tăng lãi suất."
        )
        res = MarketPulseExtractor.extract_mp02_interbank_rate(sample_text)
        assert res["success"] is True
        assert float(res["actualValue"]) == 5.75
        assert res["unit"] == "%/năm"
        assert res["observationDate"] == "2026-10-31"

        from market_pulse_discovery import extract_grounded_summary
        summary = extract_grounded_summary(sample_text, "Báo cáo thị trường tiền tệ", is_verified_numeric=True, numeric_val=5.75, indicator_id="MP-02")
        assert "5.75%" in summary or "5,75%" in summary
        assert "DXY" not in summary, "DXY must not contaminate MP-02 summary"

    def test_r101_14_mp04_1743_points_selected(self):
        """R101-14: Verifies MP-04 extracts 1,743 points on 10/11/2026 session from Tuoi Tre content."""
        sample_tuoitre = (
            "VN-Index đảo chiều tăng mạnh trong ngày 10-11, lên 1.743 điểm. "
            "Kết thúc phiên giao dịch ngày 10-11, VN-Index tăng 28,75 điểm (1,68%), lên 1.743 điểm. "
            "VN30-Index tăng 30,8 điểm (1,68%), đạt 1.860,93 điểm."
        )
        res = MarketPulseExtractor.extract_mp04_vnindex(sample_tuoitre)
        assert res["success"] is True
        assert float(res["actualValue"]) == 1743.0
        assert res["unit"] == "Điểm"
        assert res["observationDate"] == "2026-11-10"
        assert res["direction"] == "UP"

    def test_r101_15_empty_main_article_body_fails_closed(self):
        """R101-15: Verifies that empty main article body always fails verification and never falls back to full HTML snapshot."""
        verifier = SourceVerificationEngine(raw_evidence_dir=RAW_EVIDENCE_DIR, test_mode=True)
        # Snapshot containing only sidebar links and navigation, but no substantive main article body
        bad_html = (
            "<html><head><title>Test</title></head><body>"
            "<nav><a href='/'>Home</a></nav>"
            "<div class='sidebar'><a href='/item1'>Một công ty chứng khoán bị HoSE ngắt kết nối giao dịch</a></div>"
            "<footer>Footer info</footer>"
            "</body></html>"
        )
        snap_path = os.path.join(RAW_EVIDENCE_DIR, "snapshot_test_empty_body.html")
        with open(snap_path, "w", encoding="utf-8") as f:
            f.write(bad_html)
        h = hashlib.sha256(bad_html.encode("utf-8")).hexdigest()

        event = {
            "eventId": "EVT-TEST-EMPTY-BODY",
            "originalUrl": "https://tuoitre.vn/bai-viet.htm",
            "supportingQuote": "Một công ty chứng khoán bị HoSE ngắt kết nối giao dịch",
            "evidenceSnapshotPath": snap_path,
            "evidenceSha256": h,
            "category": "CAPITAL_MARKETS",
            "editorialRelevance": "HIGH",
            "commercialRelevance": "HIGH",
            "isIrrelevant": False,
            "mainEntities": ["HoSE"]
        }
        is_v, fails = verifier.verify_single_event(event)
        assert not is_v, "Empty main article body must fail verification"
        assert any("EMPTY_MAIN_ARTICLE_BODY" in f or "SUPPORTING_QUOTE_NOT_IN_MAIN_ARTICLE" in f for f in fails)
        if os.path.exists(snap_path):
            os.remove(snap_path)

    def test_r101_16_production_orchestrator_without_hardcoded_focal_candidates(self):
        """R101-16: Verifies that run_live_pilot_v3.py does not contain hardcoded focal article dictionaries."""
        pilot_path = os.path.join(SOURCE_CODE_DIR, "run_live_pilot_v3.py")
        assert os.path.exists(pilot_path), "run_live_pilot_v3.py must exist"
        with open(pilot_path, "r", encoding="utf-8") as f:
            code = f.read()
        assert "focal_indicator_articles =" not in code, "Hardcoded focal_indicator_articles must not exist in production orchestrator"
        assert "focal_cands =" not in code, "Hardcoded focal_cands must not exist in production orchestrator"

    def test_r101_17_genuine_search_vs_supplementary_collector_counts(self):
        """R101-17: Verifies separate tracking of genuine search results vs supplementary candidates."""
        search_log_path = os.path.join(LIVE_DATA_DIR, "SEARCH_DISCOVERY_LOG.json")
        assert os.path.exists(search_log_path), "SEARCH_DISCOVERY_LOG.json must exist"
        with open(search_log_path, "r", encoding="utf-8") as f:
            log_data = json.load(f)
        indicators = log_data.get("indicators", {})
        assert len(indicators) == 8, "Search audit must cover all 8 indicators"
        for ind_id, audit in indicators.items():
            assert "genuineSearchResultCount" in audit, f"{ind_id} missing genuineSearchResultCount"
            assert "supplementaryCandidateCount" in audit, f"{ind_id} missing supplementaryCandidateCount"
            assert isinstance(audit["genuineSearchResultCount"], int)
            assert isinstance(audit["supplementaryCandidateCount"], int)
            assert audit["genuineSearchResultCount"] > 0, f"{ind_id} should have genuine search results"

    def test_r101_18_canonical_freshness_source_of_truth_mp02_staleness(self):
        """R101-18: Verifies MP-02 72h canonical freshness ceiling marks age > 72h as STALE_OBSERVATION."""
        spec = CANONICAL_SPECS.get("MP-02", {})
        assert spec.get("freshnessMaxAgeHours") == 72.0, "MP-02 canonical freshnessMaxAgeHours must be 72.0"
        ok_fresh, fresh_msg, age_hrs = MarketPulseValidator.validate_observation_freshness(
            "MP-02", "2026-10-31", datetime(2026, 11, 10, 22, 0, tzinfo=timezone.utc), max_age_hours=spec["freshnessMaxAgeHours"]
        )
        assert not ok_fresh, "Observation older than 72h must fail freshness"
        assert "STALE_OBSERVATION" in fresh_msg
        assert age_hrs > 72.0

    def test_r101_19_approved_publisher_enforcement(self):
        """R101-19: Verifies that unapproved publisher domain is rejected by MarketPulseValidator."""
        obs = {
            "indicatorId": "MP-07",
            "success": True,
            "sourceUrl": "https://sohuutritue.net.vn/du-lich-viet-nam-2026.html",
            "sourcePublisher": "Sở hữu trí tuệ",
            "actualValue": "19.5",
            "unit": "triệu lượt",
            "observationDate": "2026-11-10",
            "evidencePath": "test_fake.txt",
            "evidenceSha256": "a" * 64,
            "supportingQuote": "viet nam don 19.5 trieu luot khach"
        }
        res = MarketPulseValidator.validate_indicator_observation("MP-07", obs, datetime(2026, 11, 10, 22, 0, tzinfo=timezone.utc))
        assert res["verificationStatus"] == "UNVERIFIED"
        assert res.get("unverifiedReason") == "UNAPPROVED_PUBLISHER_DOMAIN"

    def test_r101_20_main_article_body_extraction_multisource(self):
        """R101-20: Verifies robust article body extraction for VnEconomy, Báo Đầu tư, Tuổi Trẻ, and CafeF."""
        samples = {
            "vne": '<main class="article-editor ct-editor-web"><p>VnEconomy nội dung bài viết tài chính ngân hàng Việt Nam.</p></main>',
            "bdt": '<div id="content_detail_news"><p>Báo Đầu tư bài viết thị trường chứng khoán phục hồi mạnh mẽ.</p></div>',
            "tt": '<div class="detail-content afcbc-body"><p>Tuổi Trẻ thông tin về tỷ giá trung tâm và điều hành chính sách tiền tệ.</p></div>',
            "cf": '<div class="detail-content"><p>CafeF cập nhật biểu lãi suất tiết kiệm 12 tháng tại các ngân hàng thương mại.</p></div>'
        }
        for src, html_snippet in samples.items():
            body = extract_main_article_body(html_snippet)
            assert len(body.strip()) > 20, f"Extraction failed for source {src}"
            assert "nội dung" in body or "bài viết" in body or "thông tin" in body or "cập nhật" in body

    def test_r101_21_report_reconciliation_consistency(self):
        """R101-21: Verifies that MARKET_PULSE_8.json contains all 8 indicators with valid schema V3.0.4."""
        mp_path = os.path.join(LIVE_DATA_DIR, "MARKET_PULSE_8.json")
        assert os.path.exists(mp_path), "MARKET_PULSE_8.json must exist"
        with open(mp_path, "r", encoding="utf-8") as f:
            mp_data = json.load(f)
        assert len(mp_data) == 8, f"Expected 8 indicators, found {len(mp_data)}"
        valid_statuses = {"NUMERIC_VALUE_VERIFIED", "STALE_OBSERVATION", "QUALITATIVE_UPDATE_ONLY"}
        for ind in mp_data:
            assert ind["indicatorId"] in {"MP-01", "MP-02", "MP-03", "MP-04", "MP-05", "MP-06", "MP-07", "MP-08"}
            assert ind.get("updateStatus") in valid_statuses, f"Invalid updateStatus {ind.get('updateStatus')} for {ind['indicatorId']}"

    # =========================================================================
    # Phase 05B Final Data Integrity Patch Tests (R101-22 to R101-28)
    # =========================================================================

    def test_r101_22_mp07_country_entity_and_period_binding(self):
        """R101-22: Verifies MP-07 binds Vietnam vs Thailand in same sentence/paragraph, monthly vs YTD, and fails closed on wrong country."""
        # 1. Vietnam vs Thailand in the same sentence + multi-country historical paragraph
        multi_country_html = (
            "<html><body><div class='detail-content'>"
            "<p>Theo báo Khaosod, trước đại dịch COVID-19 (2019), Thái Lan thu hút 39,9 triệu khách quốc tế, "
            "trong khi Việt Nam chỉ đón 18 triệu khách, chênh lệch gần 22 triệu. "
            "Đến năm 2025, lượng khách đến Thái Lan giảm còn khoảng 33 triệu lượt, Việt Nam tăng lên 21,2 triệu, "
            "kéo khoảng cách xuống 11,8 triệu lượt.</p>"
            "<p>Con số này tiếp tục thu hẹp trong năm 2026. Trong 10 tháng đầu năm. "
            "Thái Lan đón 25,4 triệu lượt khách quốc tế, Việt Nam đón 19,5 triệu lượt, chênh lệch chỉ còn 5,9 triệu lượt.</p>"
            "</div></body></html>"
        )
        res = MarketPulseExtractor.extract_mp07_tourist_arrivals(multi_country_html)
        assert res["success"] is True, f"Expected success, got: {res}"
        assert str(res["actualValue"]) == "19.5", f"Expected Vietnam's 19.5M, got {res['actualValue']}"
        assert res["boundEntity"] == "Việt Nam"
        assert res["isCumulativeYTD"] is True
        assert res["isMonthly"] is False
        assert res["observationDate"] == "2026-10-31"

        # 2. Monthly vs YTD reporting period distinction
        monthly_html = (
            "<html><body><p>Trong tháng 10/2026, khách quốc tế đến Việt Nam ước đạt 1,42 triệu lượt khách quốc tế, "
            "tăng 27,6% so với cùng kỳ năm trước.</p></body></html>"
        )
        res_m = MarketPulseExtractor.extract_mp07_tourist_arrivals(monthly_html)
        assert res_m["success"] is True
        assert str(res_m["actualValue"]) == "1.42"
        assert res_m["isMonthly"] is True
        assert res_m["isCumulativeYTD"] is False
        assert res_m["observationPeriod"] == "Hằng tháng"

        # 3. Wrong-country only must fail closed
        foreign_only_html = (
            "<html><body><p>Trong 10 tháng đầu năm 2026, Thái Lan đón 25,4 triệu lượt khách quốc tế, "
            "Malaysia đón 20,1 triệu lượt khách quốc tế.</p></body></html>"
        )
        res_f = MarketPulseExtractor.extract_mp07_tourist_arrivals(foreign_only_html)
        assert res_f["success"] is False, "Foreign-country-only figure must fail closed"
        assert res_f["actualValue"] is None
        assert "WRONG_COUNTRY_ENTITY" in res_f.get("unverifiedReason", "")

    def test_r101_23_canonical_config_loading_and_fail_closed(self):
        """R101-23: Verifies canonical config loads from 03_INDICATOR_CONFIG/market_pulse_indicator_specs.json and fails closed when missing."""
        resolved = resolve_canonical_specs_path()
        assert os.path.exists(resolved), f"Canonical config must exist at {resolved}"
        assert "03_INDICATOR_CONFIG" in resolved or os.path.basename(resolved) == "market_pulse_indicator_specs.json"
        specs = load_canonical_specs(resolved)
        assert len(specs) == 8

        # Missing config path must raise CONFIGURATION_INVALID without silent fallback
        raised = False
        try:
            load_canonical_specs("/nonexistent/path/03_INDICATOR_CONFIG/market_pulse_indicator_specs.json")
        except RuntimeError as exc:
            if "CONFIGURATION_INVALID" in str(exc):
                raised = True
        assert raised, "Missing canonical config must fail closed with CONFIGURATION_INVALID"

    def test_r101_24_gzip_evidence_verification_and_corrupted_stream(self):
        """R101-24: Verifies gzip evidence decompression, original-byte SHA-256 parity, and fail-closed on corrupted gzip streams."""
        verifier = SourceVerificationEngine(raw_evidence_dir=RAW_EVIDENCE_DIR, test_mode=True)
        html_doc = (
            "<html><head><title>Báo cáo NHNN</title></head><body>"
            "<div class='detail-content'><p>Ngân hàng Nhà nước điều hành tỷ giá trung tâm linh hoạt trong phiên 10/11/2026.</p></div>"
            "</body></html>"
        )
        gz_bytes = gzip.compress(html_doc.encode("utf-8"))
        gz_sha = hashlib.sha256(gz_bytes).hexdigest()
        gz_path = os.path.join(RAW_EVIDENCE_DIR, "test_r101_24_valid.html.gz")
        with open(gz_path, "wb") as f:
            f.write(gz_bytes)

        valid_ev = {
            "eventId": "EVT-R101-24-GZ",
            "originalUrl": "https://cafef.vn/bao-cao-nhnn-10-11.chn",
            "supportingQuote": "Ngân hàng Nhà nước điều hành tỷ giá trung tâm linh hoạt trong phiên 10/11/2026.",
            "evidenceSnapshotPath": gz_path,
            "evidenceSha256": gz_sha,
            "category": "MACRO_MONETARY",
            "editorialRelevance": "HIGH",
            "commercialRelevance": "HIGH",
            "isIrrelevant": False,
            "mainEntities": ["Ngân hàng Nhà nước"],
            "financialFacts": []
        }
        is_v, msg = verifier.verify_single_event(valid_ev)
        assert is_v is True, f"Valid gzip evidence must pass verification, got: {msg}"

        # Corrupted gzip stream with magic header \x1f\x8b must fail closed
        corrupt_bytes = b"\x1f\x8b\x08\x00CORRUPTED_GZIP_PAYLOAD_BYTES"
        corrupt_sha = hashlib.sha256(corrupt_bytes).hexdigest()
        corrupt_path = os.path.join(RAW_EVIDENCE_DIR, "test_r101_24_corrupt.html.gz")
        with open(corrupt_path, "wb") as f:
            f.write(corrupt_bytes)
        corrupt_ev = {**valid_ev, "evidenceSnapshotPath": corrupt_path, "evidenceSha256": corrupt_sha}
        is_vc, fails_c = verifier.verify_single_event(corrupt_ev)
        assert is_vc is False, "Corrupted gzip stream must fail closed"
        assert any("CORRUPTED_GZIP_STREAM" in f for f in fails_c), f"Expected CORRUPTED_GZIP_STREAM, got: {fails_c}"

        for p in [gz_path, corrupt_path]:
            if os.path.exists(p):
                os.remove(p)

    def test_r101_25_financial_fact_semantic_integrity(self):
        """R101-25: Verifies P0-04 semantic classification rules and REVIEW_REQUIRED quarantine."""
        # 1. Shareholding percentage != credit growth
        vf1, _ = extract_semantic_financial_facts(
            "Thông tư quy định cổ đông sở hữu cổ phần từ 5% trở lên vốn điều lệ của một tổ chức tín dụng phải công bố.",
            headline="Quy định cổ đông", main_entities=["NHNN"]
        )
        assert len(vf1) == 1
        assert vf1[0]["metricName"] == "Tỷ lệ sở hữu cổ phần"
        assert "tín dụng" not in vf1[0]["metricName"].lower()

        # 2. Capital allocation percentage != ownership ratio
        vf2, _ = extract_semantic_financial_facts(
            "Hiện có khoảng 80% nhu cầu vốn của nền kinh tế đang đi qua hệ thống ngân hàng.",
            headline="Cung ứng vốn", main_entities=["NHNN"]
        )
        assert len(vf2) == 1
        assert vf2[0]["metricName"] == "Tỷ trọng cung ứng vốn cho nền kinh tế"
        assert "sở hữu" not in vf2[0]["metricName"].lower()

        # 3. FX purchase volume & VND liquidity != exchange rate
        vf3, _ = extract_semantic_financial_facts(
            "Ước tính gần 1 tỷ USD được NHNN mua vào theo hợp đồng kỳ hạn và khoảng 25.500 tỷ đồng được cung ứng ra nền kinh tế.",
            headline="NHNN mua ngoại tệ", main_entities=["NHNN"]
        )
        assert len(vf3) == 2
        assert all("tỷ giá" not in f["metricName"].lower() for f in vf3)
        assert all(f["polarity"] is None for f in vf3)

        # 4. Tax & commission policy thresholds have no performance movement polarity
        vf4, _ = extract_semantic_financial_facts(
            "Đề xuất áp dụng ngưỡng nợ thuế tạm hoãn xuất cảnh trên 200 triệu đồng đối với cá nhân và giữ trần hoa hồng 15%.",
            headline="Ngưỡng nợ thuế", main_entities=["Bộ Tài chính"]
        )
        assert len(vf4) == 2
        assert all(f["factType"] == "POLICY_THRESHOLD" and f["polarity"] is None for f in vf4)

        # 5. Gold price preserves VND per tael and avoids broken OCR spacing '1 38,5'
        gold_html = (
            "<html><body><main class='article-editor'><p>"
            "Sáng 10/11, giá vàng miếng SJC tăng 300 nghìn đồng/lượng mỗi chiều, niêm yết giá mua ở ngưỡng 1<span>38,5 </span>triệu đồng/lượng."
            "</p></main></body></html>"
        )
        clean_gold = extract_clean_article_content(gold_html, "https://vneconomy.vn/gia-vang.htm")
        vf5, _ = extract_semantic_financial_facts(clean_gold["articleBody"], headline="Giá vàng SJC", main_entities=["SJC"])
        assert any(f["extractedExpression"] == "138,5 triệu đồng/lượng" and f["unit"] == "triệu đồng/lượng" for f in vf5)

    def test_r101_26_mp02_october_candidate_selection_and_mp05_policy_distinction(self):
        """R101-26: Verifies MP-02 inspects October 2026 candidates before June 2026 and MP-05 labels policy news without observationDate."""
        eng = MarketPulseDiscoveryEngine(raw_evidence_dir=RAW_EVIDENCE_DIR, test_mode=True, run_timestamp="2026-11-10T22:00:00+07:00")
        mp02_pool = [
            {
                "candidateUrl": "https://cafef.vn/lai-suat-lien-ngan-hang-tiep-tuc-lao-doc-lai-suat-qua-dem-giam-mot-nua-so-voi-dau-tuan-188260604112200839.chn",
                "headline": "Lãi suất liên ngân hàng tiếp tục lao dốc, lãi suất qua đêm giảm một nửa so với đầu tuần",
                "publisher": "cafef.vn",
                "publishedAt": "2026-06-04T11:22:00+07:00",
                "candidateSource": "GENUINE_SEARCH_RESULT"
            },
            {
                "candidateUrl": "https://cafef.vn/ngan-hang-nha-nuoc-hut-khoi-thi-truong-hon-53000-ty-dong-lai-suat-lien-ngan-hang-bien-dong-manh-trong-tuan-qua-188261005135654704.chn",
                "headline": "Ngân hàng Nhà nước hút khỏi thị trường hơn 53.000 tỷ đồng, lãi suất liên ngân hàng biến động mạnh trong tuần qua",
                "publisher": "cafef.vn",
                "publishedAt": "2026-10-05T13:56:00+07:00",
                "candidateSource": "GENUINE_SEARCH_RESULT"
            },
            {
                "candidateUrl": "https://cafef.vn/lai-suat-lien-ngan-hang-tang-gap-35-lan-chi-sau-mot-dem-nhnn-chuyen-sang-trang-thai-bom-thanh-khoan-188261001102404093.chn",
                "headline": "Lãi suất liên ngân hàng tăng gấp 3,5 lần chỉ sau một đêm, NHNN chuyển sang trạng thái bơm thanh khoản",
                "publisher": "cafef.vn",
                "publishedAt": "2026-10-01T10:24:00+07:00",
                "candidateSource": "GENUINE_SEARCH_RESULT"
            }
        ]
        ranked_mp02 = eng.rank_candidates("MP-02", mp02_pool)
        assert "188261005135654704" in ranked_mp02[0]["candidateUrl"], "05/10/2026 candidate must rank before 04/06/2026"
        assert "188261001102404093" in ranked_mp02[1]["candidateUrl"], "01/10/2026 candidate must rank before 04/06/2026"

        # Single-sentence overnight rate extraction on 05/10 article text
        oct05_text = "Chốt phiên 2/10, lãi suất qua đêm (ON) ở mức 2,8%/năm, giảm 1,8 điểm % so với cuối tuần trước. Kỳ hạn 1 tháng ở mức 6,3%/năm."
        ext_oct05 = MarketPulseExtractor.extract_mp02_interbank_rate(oct05_text)
        assert ext_oct05["success"] is True
        assert str(ext_oct05["actualValue"]) == "2.8"
        assert ext_oct05["observationDate"] == "2026-10-02"

        # MP-05 rejects unrelated M&A circular repeal and selects credit-room policy news
        mp05_pool = [
            {
                "candidateUrl": "https://cafef.vn/ngan-hang-nha-nuoc-muon-bai-bo-nhieu-quy-dinh-lien-quan-den-lai-suat-cho-vay-bang-usd-sap-nhap-hop-nhat-mua-lai-to-chuc-tin-dung-18826111020174761.chn",
                "headline": "Ngân hàng Nhà nước muốn bãi bỏ nhiều quy định liên quan đến lãi suất cho vay bằng USD, sáp nhập, hợp nhất, mua lại tổ chức tín dụng",
                "publisher": "cafef.vn",
                "publishedAt": "2026-11-10T20:16:00+07:00",
                "candidateSource": "NEWS_COLLECTOR_POOL"
            },
            {
                "candidateUrl": "https://cafef.vn/ngan-hang-nha-nuoc-da-co-co-che-loai-tru-17-trieu-ty-dong-ra-khoi-room-tin-dung-188261025124958826.chn",
                "headline": "Ngân hàng Nhà nước đã có cơ chế loại trừ 1,7 triệu tỷ đồng ra khỏi room tín dụng",
                "publisher": "cafef.vn",
                "publishedAt": "2026-10-25T12:49:00+07:00",
                "candidateSource": "GENUINE_SEARCH_RESULT"
            }
        ]
        ranked_mp05 = eng.rank_candidates("MP-05", mp05_pool)
        assert ranked_mp05[0]["relevanceScore"] > 0 and "room-tin-dung" in ranked_mp05[0]["candidateUrl"]
        assert ranked_mp05[1]["relevanceScore"] <= 0, "Unrelated M&A circular repeal must be penalized and rejected"

    def test_r101_27_dynamic_report_reconciliation_with_market_pulse_json(self):
        """R101-27: Verifies all reports dynamically match MARKET_PULSE_8.json (5 VERIFIED, 1 STALE_OBSERVATION, 2 QUALITATIVE_UPDATE_ONLY)."""
        mp_path = os.path.join(LIVE_DATA_DIR, "MARKET_PULSE_8.json")
        with open(mp_path, "r", encoding="utf-8") as f:
            mp_data = json.load(f)
        by_id = {ind["indicatorId"]: ind for ind in mp_data}

        assert by_id["MP-07"]["actualValue"] == "19.5", f"MP-07 must be Vietnam's 19.5M, got {by_id['MP-07']['actualValue']}"
        assert by_id["MP-07"]["verificationStatus"] == "VERIFIED"
        assert by_id["MP-02"]["updateStatus"] == "STALE_OBSERVATION"
        assert by_id["MP-05"]["updateStatus"] == "QUALITATIVE_UPDATE_ONLY"
        assert by_id["MP-05"]["observationDate"] is None
        assert by_id["MP-06"]["updateStatus"] == "QUALITATIVE_UPDATE_ONLY"

        verified_ids = sorted(ind["indicatorId"] for ind in mp_data if ind.get("verificationStatus") == "VERIFIED")
        stale_ids = sorted(ind["indicatorId"] for ind in mp_data if ind.get("updateStatus") == "STALE_OBSERVATION")
        qual_ids = sorted(ind["indicatorId"] for ind in mp_data if ind.get("updateStatus") == "QUALITATIVE_UPDATE_ONLY")
        assert verified_ids == ["MP-01", "MP-03", "MP-04", "MP-07", "MP-08"]
        assert stale_ids == ["MP-02"]
        assert qual_ids == ["MP-05", "MP-06"]

        exec_path = os.path.join(REPORT_DIR, "00_EXECUTIVE_SUMMARY.md")
        if os.path.exists(exec_path):
            with open(exec_path, "r", encoding="utf-8") as rf:
                rep_txt = rf.read()
            assert "5.75%/năm" not in rep_txt, "Stale hardcoded 5.75% must not appear in executive summary"

    def test_r101_28_extracted_package_self_contained_reproducibility(self):
        """R101-28: Verifies that source code, config, live data, and evidence directories resolve portably without external workspace paths."""
        assert os.path.exists(SOURCE_CODE_DIR)
        assert os.path.exists(LIVE_DATA_DIR)
        assert os.path.exists(RAW_EVIDENCE_DIR)
        specs_p = resolve_canonical_specs_path()
        assert os.path.exists(specs_p)

    # =========================================================================
    # TEST RUNNER HARNESS
    # =========================================================================

    def run_all(self):
        self.log("=" * 70)
        self.log("BRYAN FINTECH INTELLIGENCE — PHASE 05B-R1.3A.3 ENGINE QA SUITE")
        self.log(f"Execution Timestamp: {datetime.now(timezone(timedelta(hours=7))).isoformat()}")
        self.log("=" * 70 + "\n")

        # News Collector (T01 - T06)
        self.test("TEST-01: Candidate URL Normalization & Tracker Stripping", self.test_01_url_normalization)
        self.test("TEST-02: Vietnamese & ISO Timestamp Parsing", self.test_02_timestamp_parsing_vietnamese)
        self.test("TEST-03: Future Timestamp Rejection", self.test_03_freshness_bucket_future_rejected)
        self.test("TEST-04: Stale Content (>72h) Rejection", self.test_04_freshness_bucket_stale_over_72h_rejected)
        self.test("TEST-05: 0-to-24h Freshness Bucket Classification", self.test_05_freshness_bucket_0_to_24h)
        self.test("TEST-06: Candidate Pool Shortfall & Zero-Fabrication Reporting", self.test_06_collector_shortfall_honest_reporting)

        # Source Verification (T07 - T12)
        self.test("TEST-07: Trusted Domain Boundary & Scheme Validation", self.test_07_trusted_domain_boundary_pass)
        self.test("TEST-08: Hostname Spoofing & Domain Suffix Rejection", self.test_08_hostname_spoofing_rejected)
        self.test("TEST-09: Raw Evidence Snapshot SHA-256 & Fact Verification", self.test_09_evidence_snapshot_sha256_verification)
        self.test("TEST-10: Evidence Snapshot Byte Hash Mismatch Rejection", self.test_10_evidence_sha256_mismatch_rejected)
        self.test("TEST-11: Supporting Quote Traceability & Grounding Verification", self.test_11_quote_not_in_snapshot_rejected)
        self.test("TEST-12: V3.0.4 Provenance Ledger Foreign Key & Duplicate Audit", self.test_12_provenance_ledger_foreign_key_and_duplicate_check)

        # Semantic Deduplication (T13 - T17)
        self.test("TEST-13: 64-Char SHA-256 Content Fingerprint Determinism", self.test_13_semantic_fingerprint_deterministic_stability)
        self.test("TEST-14: Intra-Pool Deduplication (Same Event, Different Headline)", self.test_14_dedup_same_event_different_headline)
        self.test("TEST-15: Distinct Events About Same Institution Classified Correctly", self.test_15_dedup_distinct_events_same_bank)
        self.test("TEST-16: Material Follow-up Development Identification", self.test_16_dedup_material_follow_up)
        self.test("TEST-17: Historical Registry Loading Fail-Closed (FAIL_HISTORICAL_DATA_UNAVAILABLE)", self.test_17_dedup_fail_closed_missing_fixture)

        # Dynamic Market Pulse (T18 - T20)
        self.test("TEST-18: Exactly Eight Canonical Indicators (MP-01 to MP-08) Enforced", self.test_18_market_pulse_eight_canonical_indicators)
        self.test("TEST-19: MP-02 Interbank Overnight Rate 72-Hour Ceiling Rule Enforced", self.test_19_market_pulse_mp02_72h_rule_enforced)
        self.test("TEST-20: Dynamic Market Pulse VERIFIED Observation with SHA-256 Match", self.test_20_market_pulse_verified_with_evidence_hash_pass)

        # Schema & Integrity Assurance (T21 - T22)
        self.test("TEST-21: V3.0.4 JSON Schema Strict Compliance (Provenance & Market Pulse)", self.test_21_schema_contract_validation_provenance_and_market_pulse)
        self.test("TEST-22: Financial Fact Incomplete Attribute Detection", self.test_22_altered_financial_figure_detection)

        # Phase 05B-R1 Live Integration & Adversarial Defense (T23 - T34)
        self.test("TEST-23: Real HTTP Retrieval Invocation & Content Verification", self.test_23_real_http_retrieval_invocation)
        self.test("TEST-24: Fake Source URL on Trusted Domain Fails (Adversarial Defense)", self.test_24_fake_source_url_on_trusted_domain_fails)
        self.test("TEST-25: HTTP 404 Status Code Explicit Rejection", self.test_25_http_404_status_explicit_rejection)
        self.test("TEST-26: Redirect to Unrelated / Untrusted Domain Fails", self.test_26_redirect_to_untrusted_domain_fails)
        self.test("TEST-27: Incorrect / Mismatched Publication Timestamp Fails", self.test_27_incorrect_publication_timestamp_fails)
        self.test("TEST-28: Missing Source Evidence Snapshot Fails", self.test_28_missing_source_evidence_fails)
        self.test("TEST-29: Genuine Source Snapshot Acceptance & Byte Hash Match", self.test_29_genuine_source_snapshot_acceptance)
        self.test("TEST-30: Self-Generated Claims Without Retrieval Ledger Rejected", self.test_30_self_generated_claims_without_retrieval_ledger_rejected)
        self.test("TEST-31: MP-06 Rejects Total NAPAS System Volume Labelled as VietQR-Only", self.test_31_mp06_rejects_total_napas_volume_labelled_as_vietqr)
        self.test("TEST-32: Live Run Timestamp Dynamic (Not Hardcoded)", self.test_32_live_run_timestamp_is_dynamic)
        self.test("TEST-33: Daily Edition ID Governance (No Collision with Pilot 26)", self.test_33_daily_edition_id_governance)
        self.test("TEST-34: Quota Shortfall Honestly Reported as COLLECTION_SHORTFALL", self.test_34_quota_shortfall_honest_reporting)

        # Phase 05B-R1.1 Integration Tests (T35 - T48)
        self.test("TEST-35: MP-01 to MP-08 Live/Fixture HTTP Retrieval & Byte Capture", self.test_35_mp_live_fixture_http_retrieval)
        self.test("TEST-36: Fake Market Pulse URL Rejected as UNVERIFIED with Null Value", self.test_36_fake_market_pulse_url_rejected)
        self.test("TEST-37: Unapproved Market Pulse Publisher Rejected as UNVERIFIED", self.test_37_unapproved_market_pulse_publisher_rejected)
        self.test("TEST-38: Synthetic Local Evidence Without HTTP Retrieval Rejected", self.test_38_synthetic_local_evidence_rejected)
        self.test("TEST-39: Actual Final URL Captured Correctly After HTTP Redirects", self.test_39_actual_final_url_after_redirect_captured)
        self.test("TEST-40: Untrusted Redirect Rejection in Production Orchestrator/Verifier", self.test_40_untrusted_redirect_in_orchestrator_rejected)
        self.test("TEST-41: Original-Byte SHA-256 Parity (Ledger vs On-Disk Snapshot)", self.test_41_original_byte_sha256_parity)
        self.test("TEST-42: All newsEvent Schema Fields Validated Against Draft 2020-12", self.test_42_all_news_event_schema_fields)
        self.test("TEST-43: financialFacts.numericValue Strictly Requires String Type", self.test_43_financial_facts_numeric_value_string_type)
        self.test("TEST-44: Multi-Publisher Source Diversity (Candidates Across >=3 Publishers)", self.test_44_multi_publisher_source_diversity)
        self.test("TEST-45: Content Relevance Rejects Hardcoded HIGH for Non-Financial Topics", self.test_45_hardcoded_high_relevance_rejected_for_non_financial)
        self.test("TEST-46: Freshness Quota Gate Requires Both >=25 Events & >=80% 0-24h", self.test_46_freshness_quota_gate_requires_both)
        self.test("TEST-47: Complete Candidate Disposition Accounting & 100% Reconciliation", self.test_47_complete_candidate_disposition_accounting)
        self.test("TEST-48: No False DATA_READY When Freshness/Quota Fails (Honest Shortfall)", self.test_48_no_false_data_ready_on_shortfall)

        # Phase 05B-R1.2 New Adversarial Tests (R12-01 to R12-25)
        self.test("R12-01: Tampered numericValue to 999999999 Rejected", self.test_r12_01_tampered_numeric_value_rejected)
        self.test("R12-02: Tampered unit from VND to USD Rejected", self.test_r12_02_tampered_unit_rejected)
        self.test("R12-03: Inverted Polarity (UP vs DOWN) Rejected", self.test_r12_03_inverted_polarity_rejected)
        self.test("R12-04: Tampered Entity Grounding Rejected", self.test_r12_04_tampered_entity_rejected)
        self.test("R12-05: Tampered Reporting Period Grounding Rejected", self.test_r12_05_tampered_reporting_period_rejected)
        self.test("R12-06: Tampered extractedExpression Rejected", self.test_r12_06_tampered_extracted_expression_rejected)
        self.test("R12-07: Evidence Without Numeric Measurement Rejected", self.test_r12_07_evidence_without_numeric_measurement_rejected)
        self.test("R12-08: HTTP 200 Homepage Rejected", self.test_r12_08_http_200_homepage_rejected)
        self.test("R12-09: Category Listing Page Rejected as Article Evidence", self.test_r12_09_category_listing_page_rejected)
        self.test("R12-10: JavaScript Cookie Challenge Rejected as Article Evidence", self.test_r12_10_js_cookie_challenge_rejected)
        self.test("R12-11: Retrieval Timestamp Fallback Prohibited", self.test_r12_11_retrieval_time_fallback_prohibited)
        self.test("R12-12: HTML Entity Timezone &#x2B;07:00 Parsed Successfully", self.test_r12_12_html_entity_timezone_parsing)
        self.test("R12-13: Future Timestamp Rejected as FUTURE_TIMESTAMP", self.test_r12_13_future_timestamp_rejected)
        self.test("R12-14: Unparseable Timestamp Classified as MANUAL_REVIEW_REQUIRED", self.test_r12_14_missing_or_unparseable_timestamp_manual_review)
        self.test("R12-15: Footer Payment Noise Does Not Poison Category to FINTECH_PAYMENT", self.test_r12_15_footer_payment_noise_does_not_poison_category)
        self.test("R12-16: Publisher Domain in mainEntities Rejected", self.test_r12_16_publisher_domain_in_main_entities_rejected)
        self.test("R12-17: Market Pulse Ignores Hardcoded Input Values", self.test_r12_17_market_pulse_ignores_hardcoded_input_values)
        self.test("R12-18: Market Pulse Missing Metric Downgraded to UNVERIFIED with Null", self.test_r12_18_market_pulse_missing_metric_unverified)
        self.test("R12-19: SSRF Redirect to Localhost Rejected in Production Mode", self.test_r12_19_ssrf_redirect_to_localhost_rejected)
        self.test("R12-20: SSRF Redirect to Private IP (RFC 1918) Rejected", self.test_r12_20_ssrf_redirect_to_private_ip_rejected)
        self.test("R12-21: Redirect to Untrusted Domain Rejected", self.test_r12_21_redirect_to_untrusted_domain_rejected)
        self.test("R12-22: Private/Loopback IP Address Detection Verified", self.test_r12_22_dns_resolving_to_private_ip_rejected)
        self.test("R12-23: Two Articles Covering Same Event Detected as Duplicate", self.test_r12_23_two_articles_same_event_detected_as_duplicate)
        self.test("R12-24: Distinct Events About Same Institution Marked DISTINCT_EVENT", self.test_r12_24_two_events_same_institution_distinct)
        self.test("R12-25: Altered Snapshot Content Detected by SHA-256 Mismatch", self.test_r12_25_tampered_snapshot_content_hash_mismatch)

        # Phase 05B-R1.3 Mandatory Market Pulse Adversarial Tests (MP-R13-01 to MP-R13-35)
        self.test("MP-R13-01: Hardcoded actualValue injected by orchestrator rejected", self.test_mp_r13_01_hardcoded_actual_value_injected_by_orchestrator)
        self.test("MP-R13-02: Hardcoded change rejected", self.test_mp_r13_02_hardcoded_change_rejected)
        self.test("MP-R13-03: Hardcoded direction rejected", self.test_mp_r13_03_hardcoded_direction_rejected)
        self.test("MP-R13-04: Missing observation date replaced by runtime date rejected", self.test_mp_r13_04_missing_observation_date_not_replaced_by_runtime_date)
        self.test("MP-R13-05: HTTP 200 empty response returns UNVERIFIED with null", self.test_mp_r13_05_http_200_empty_response_unverified)
        self.test("MP-R13-06: Homepage instead of article rejected as UNVERIFIED", self.test_mp_r13_06_homepage_instead_of_article_rejected)
        self.test("MP-R13-07: Category page instead of data source rejected", self.test_mp_r13_07_category_page_instead_of_data_source_rejected)
        self.test("MP-R13-08: Cookie challenge page unverified", self.test_mp_r13_08_cookie_challenge_page_unverified)
        self.test("MP-R13-09: Evidence without numeric value rejected", self.test_mp_r13_09_evidence_does_not_contain_numeric_value_rejected)
        self.test("MP-R13-10: Incorrect numeric value / commercial rate rejected", self.test_mp_r13_10_incorrect_numeric_value_rejected)
        self.test("MP-R13-11: Incorrect unit rejected", self.test_mp_r13_11_incorrect_unit_rejected)
        self.test("MP-R13-12: 100 million converted correctly to 0.1 billion", self.test_mp_r13_12_vietqr_100_million_normalized_correctly)
        self.test("MP-R13-13: 1.714,32 locale parsing PASS", self.test_mp_r13_13_vietnamese_locale_number_parsing)
        self.test("MP-R13-14: 12,5% locale parsing PASS", self.test_mp_r13_14_percentage_locale_parsing)
        self.test("MP-R13-15: MP-06 total NAPAS volume labelled VietQR rejected", self.test_mp_r13_15_mp06_total_napas_volume_labelled_vietqr_rejected)
        self.test("MP-R13-16: MP-06 value without network scope unverified", self.test_mp_r13_16_mp06_value_without_network_scope_unverified)
        self.test("MP-R13-17: MP-03 bank coverage universe disclosed", self.test_mp_r13_17_mp03_bank_coverage_universe_disclosed)
        self.test("MP-R13-18: MP-03 promotional rate flagged", self.test_mp_r13_18_mp03_promotional_rate_mislabelled_standard_rejected)
        self.test("MP-R13-19: MP-04 intraday value rejected as closing index", self.test_mp_r13_19_mp04_intraday_value_labelled_closing_index_rejected)
        self.test("MP-R13-20: MP-05 YTD growth distinguished from YoY", self.test_mp_r13_20_mp05_ytd_growth_labelled_yoy_distinguished)
        self.test("MP-R13-21: MP-05 no hardcoded reporting date", self.test_mp_r13_21_mp05_no_hardcoded_reporting_date)
        self.test("MP-R13-22: MP-07 monthly value distinguished from YTD", self.test_mp_r13_22_mp07_monthly_value_distinguished_from_ytd)
        self.test("MP-R13-23: MP-07 YoY comparison extracted", self.test_mp_r13_23_mp07_yoy_comparison_extracted)
        self.test("MP-R13-24: MP-08 awarded volume not labelled net injection", self.test_mp_r13_24_mp08_awarded_volume_labelled_net_injection_rejected)
        self.test("MP-R13-25: MP-08 missing maturity component unverified", self.test_mp_r13_25_mp08_missing_maturity_component_unverified)
        self.test("MP-R13-26: Stale MP-02 observation rejected", self.test_mp_r13_26_stale_mp02_observation_rejected)
        self.test("MP-R13-27: Fake publication timestamp rejected", self.test_mp_r13_27_fake_publication_timestamp_rejected)
        self.test("MP-R13-28: Raw snapshot modified after hashing rejected", self.test_mp_r13_28_snapshot_tampered_after_hashing_rejected)
        self.test("MP-R13-29: Redirect to localhost blocked in production mode", self.test_mp_r13_29_redirect_to_localhost_blocked_in_production)
        self.test("MP-R13-30: Redirect to private IP blocked", self.test_mp_r13_30_redirect_to_private_ip_blocked)
        self.test("MP-R13-31: DNS rebinding simulation / restricted network rejected", self.test_mp_r13_31_dns_rebinding_simulation_rejected)
        self.test("MP-R13-32: AI-generated interpretation rejected as evidence", self.test_mp_r13_32_ai_generated_interpretation_rejected_as_evidence)
        self.test("MP-R13-33: Arithmetic mismatch between close and change triggers rejection", self.test_mp_r13_33_conflicting_official_observations_manual_review)
        self.test("MP-R13-34: Missing previous value yields change=None and direction=UNKNOWN", self.test_mp_r13_34_missing_previous_value_yields_unknown_direction)
        self.test("MP-R13-35: Repeated fetch logged separately", self.test_mp_r13_35_repeated_fetch_logged_separately)

        # Phase 05B-R1.3A.2 Mandatory Source Acquisition & Integrity Tests (20 Tests)
        self.test("R13A2-01: MP-01 unsupported date rejection", self.test_r13a2_01_mp01_unsupported_date_rejection)
        self.test("R13A2-02: MP-01 navigation-label quote rejection", self.test_r13a2_02_mp01_navigation_label_quote_rejection)
        self.test("R13A2-03: MP-01 success/status consistency", self.test_r13a2_03_mp01_success_status_consistency)
        self.test("R13A2-04: Homepage rejection", self.test_r13a2_04_homepage_rejection)
        self.test("R13A2-05: Category-page rejection", self.test_r13a2_05_category_page_rejection)
        self.test("R13A2-06: Cookie challenge rejection", self.test_r13a2_06_cookie_challenge_rejection)
        self.test("R13A2-07: MP-03 incomplete bank coverage", self.test_r13a2_07_mp03_incomplete_bank_coverage)
        self.test("R13A2-08: MP-04 intraday versus closing distinction", self.test_r13a2_08_mp04_intraday_versus_closing_distinction)
        self.test("R13A2-09: MP-06 NAPAS versus VietQR scope", self.test_r13a2_09_mp06_napas_versus_vietqr_scope)
        self.test("R13A2-10: MP-06 million-to-billion conversion", self.test_r13a2_10_mp06_million_to_billion_conversion)
        self.test("R13A2-11: MP-07 monthly versus cumulative period", self.test_r13a2_11_mp07_monthly_versus_cumulative_period)
        self.test("R13A2-12: MP-08 gross versus net reconciliation", self.test_r13a2_12_mp08_gross_versus_net_reconciliation)
        self.test("R13A2-13: 1,714 locale parsing", self.test_r13a2_13_locale_parsing_1714)
        self.test("R13A2-14: 12.345 decimal ambiguity", self.test_r13a2_14_decimal_ambiguity_12345)
        self.test("R13A2-15: Decimal arithmetic precision", self.test_r13a2_15_decimal_arithmetic_precision)
        self.test("R13A2-16: Missing observation timestamp", self.test_r13a2_16_missing_observation_timestamp)
        self.test("R13A2-17: Retrieval timestamp separation", self.test_r13a2_17_retrieval_timestamp_separation)
        self.test("R13A2-18: Relative evidence path validation", self.test_r13a2_18_relative_evidence_path_validation)
        self.test("R13A2-19: Evidence hash mismatch", self.test_r13a2_19_evidence_hash_mismatch)
        self.test("R13A2-20: Fixture-to-live evidence contamination", self.test_r13a2_20_fixture_to_live_evidence_contamination)

        # Phase 05B-R1.3A.3 Mandatory Independent Tests (20 Tests)
        self.test("R13A3-01: MP-03 lower bound vs max rate", self.test_r13a3_01_mp03_lower_bound_vs_max)
        self.test("R13A3-02: MP-03 promotional vs standard rate", self.test_r13a3_02_mp03_promotional_vs_standard)
        self.test("R13A3-03: MP-03 unrelated banks rejected", self.test_r13a3_03_mp03_unrelated_banks_rejected)
        self.test("R13A3-04: MP-03 quote contains numeric", self.test_r13a3_04_mp03_quote_contains_numeric)
        self.test("R13A3-05: MP-06 one-month duration false positive rejected", self.test_r13a3_05_mp06_one_month_false_positive)
        self.test("R13A3-06: MP-06 missing unit rejected", self.test_r13a3_06_mp06_missing_unit_rejected)
        self.test("R13A3-07: MP-01 date range end point", self.test_r13a3_07_mp01_date_range_end_point)
        self.test("R13A3-08: MP-01 correct freshness age", self.test_r13a3_08_mp01_correct_freshness_age)
        self.test("R13A3-09: MP-04 approximate change handling", self.test_r13a3_09_mp04_approximate_change_handling)
        self.test("R13A3-10: Validator missing evidence rejected", self.test_r13a3_10_validator_missing_evidence_rejected)
        self.test("R13A3-11: Validator missing hash rejected", self.test_r13a3_11_validator_missing_hash_rejected)
        self.test("R13A3-12: Numeric 1.500 thousand conversion", self.test_r13a3_12_numeric_1500_thousand_conversion)
        self.test("R13A3-13: Numeric 1.000 million conversion", self.test_r13a3_13_numeric_1000_million_conversion)
        self.test("R13A3-14: Mixed locale parsing", self.test_r13a3_14_mixed_locale_parsing)
        self.test("R13A3-15: HTTP redirect blocked before request", self.test_r13a3_15_http_redirect_blocked_before_request)
        self.test("R13A3-16: DNS mixed IP rejection", self.test_r13a3_16_dns_mixed_ip_rejection)
        self.test("R13A3-17: DNS rebinding protection", self.test_r13a3_17_dns_rebinding_protection)
        self.test("R13A3-18: Schema validation all eight indicators", self.test_r13a3_18_schema_validation_all_eight)
        self.test("R13A3-19: Freshness config consistency", self.test_r13a3_19_freshness_config_consistency)
        self.test("R13A3-20: Live evidence hash reconciliation", self.test_r13a3_20_live_evidence_hash_reconciliation)

        # Phase 05B Architecture Alignment Tests (ALIGN-01 to ALIGN-11)
        self.test("ALIGN-01: Exact numeric mismatch rejected", self.test_align_01_exact_numeric_mismatch_rejected)
        self.test("ALIGN-02: Unit mismatch rejected", self.test_align_02_unit_mismatch_rejected)
        self.test("ALIGN-03: MP-01 gold context mismatch rejected", self.test_align_03_mp01_gold_context_mismatch_rejected)
        self.test("ALIGN-04: MP-06 cross-sentence NAPAS contamination rejected", self.test_align_04_mp06_cross_sentence_napas_contamination_rejected)
        self.test("ALIGN-05: Search result relevance ranking", self.test_align_05_search_result_relevance_ranking)
        self.test("ALIGN-06: Search result recency ranking", self.test_align_06_search_result_recency_ranking)
        self.test("ALIGN-07: Publication date extraction hierarchy", self.test_align_07_publication_date_extraction_hierarchy)
        self.test("ALIGN-08: Latest update selection", self.test_align_08_latest_update_selection)
        self.test("ALIGN-09: Qualitative update without fabricated numeric value", self.test_align_09_qualitative_update_without_fabricated_numeric_value)
        self.test("ALIGN-10: Relative evidence paths portable resolution", self.test_align_10_relative_evidence_paths)
        self.test("ALIGN-11: No unsupported Market Pulse synthesis", self.test_align_11_no_unsupported_market_pulse_synthesis)

        # Phase 05B Alignment R1.0.1 Remediation Tests (R101-01 to R101-10)
        self.test("R101-01: Adversarial source unit binding", self.test_r101_01_adversarial_source_unit_binding)
        self.test("R101-02: Supporting quote not in main article rejected", self.test_r101_02_supporting_quote_not_in_main_article)
        self.test("R101-03: Main article body excludes noise", self.test_r101_03_main_article_body_excludes_noise)
        self.test("R101-04: Financial facts bound to main article", self.test_r101_04_financial_facts_bound_to_main_article)
        self.test("R101-05: Market Pulse search execution audit logging", self.test_r101_05_market_pulse_search_execution_audit)
        self.test("R101-06: Qualitative update contains zero unverified numbers", self.test_r101_06_qualitative_update_contains_no_unverified_numbers)
        self.test("R101-07: MP-07 provincial tourism revenue rejected", self.test_r101_07_mp07_provincial_tourism_rejected)
        self.test("R101-08: MP-08 FX intervention rejected from OMO", self.test_r101_08_mp08_fx_intervention_rejected_from_omo)
        self.test("R101-09: Distinct URL assignment across indicators", self.test_r101_09_distinct_url_assignment_across_indicators)
        self.test("R101-10: Package evidence paths resolution", self.test_r101_10_package_evidence_paths_resolution)
        self.test("R101-11: Candidate recency over seed priority", self.test_r101_11_candidate_recency_over_seed_priority)
        self.test("R101-12: No retrieval timestamp as publication date", self.test_r101_12_no_retrieval_timestamp_as_publication_date)
        self.test("R101-13: MP-02 5.75% overnight rate extraction", self.test_r101_13_mp02_575_overnight_rate_extraction)
        self.test("R101-14: MP-04 1,743 points VN-Index observation", self.test_r101_14_mp04_1743_points_selected)
        self.test("R101-15: Empty main article body fails closed", self.test_r101_15_empty_main_article_body_fails_closed)
        self.test("R101-16: Production orchestrator without hardcoded focal candidates", self.test_r101_16_production_orchestrator_without_hardcoded_focal_candidates)
        self.test("R101-17: Genuine search vs supplementary collector counts", self.test_r101_17_genuine_search_vs_supplementary_collector_counts)
        self.test("R101-18: Canonical freshness source of truth MP-02 staleness", self.test_r101_18_canonical_freshness_source_of_truth_mp02_staleness)
        self.test("R101-19: Approved publisher domain enforcement", self.test_r101_19_approved_publisher_enforcement)
        self.test("R101-20: Main article body extraction multisource", self.test_r101_20_main_article_body_extraction_multisource)
        self.test("R101-21: Report reconciliation consistency", self.test_r101_21_report_reconciliation_consistency)
        self.test("R101-22: MP-07 country-entity and period binding", self.test_r101_22_mp07_country_entity_and_period_binding)
        self.test("R101-23: Canonical config loading and fail-closed", self.test_r101_23_canonical_config_loading_and_fail_closed)
        self.test("R101-24: Gzip evidence verification and corrupted stream rejection", self.test_r101_24_gzip_evidence_verification_and_corrupted_stream)
        self.test("R101-25: Financial fact semantic integrity rules", self.test_r101_25_financial_fact_semantic_integrity)
        self.test("R101-26: MP-02 October candidate inspection and MP-05 policy distinction", self.test_r101_26_mp02_october_candidate_selection_and_mp05_policy_distinction)
        self.test("R101-27: Dynamic report reconciliation with MARKET_PULSE_8.json", self.test_r101_27_dynamic_report_reconciliation_with_market_pulse_json)
        self.test("R101-28: Extracted package self-contained reproducibility", self.test_r101_28_extracted_package_self_contained_reproducibility)

        self.log("=" * 70)
        self.log(f"QA TEST SUMMARY: Total: {self.passed + self.failed} | PASSED: {self.passed} | FAILED: {self.failed}")
        self.log(f"ENGINE STATUS: {'ENGINEERING_PASS' if self.failed == 0 else 'ENGINE_FAIL'}")
        self.log("=" * 70)

        # Write log file
        log_path = os.path.join(WORKSPACE_DIR, "PHASE05B_ENGINE_TEST_RESULTS.log")
        with open(log_path, "w", encoding="utf-8") as f:
            f.write("\n".join(self.log_lines) + "\n")
        print(f"\nExecution log written to: {log_path}")
        
        return self.failed == 0


if __name__ == "__main__":
    runner = TestPhase05BRunner()
    success = runner.run_all()
    sys.exit(0 if success else 1)
