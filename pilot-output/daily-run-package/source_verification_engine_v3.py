#!/usr/bin/env python3
"""
source_verification_engine_v3.py — Bryan FinTech Intelligence Phase 05B-R1.2
Independent Source Provenance & Financial Fact Verification Engine

P0 & P1 Critical Remediation:
- Eliminates numeric tampering vulnerability: validates claimed numeric values, units,
  polarity/direction, entities, reporting periods, and expressions against raw evidence.
- Defends against SSRF, DNS rebinding, and redirect boundary attacks.
- Enforces strict foreign keys and V3.0.4 provenance contract ledger assembly.
"""

import os
import sys
import json
import gzip
import re
import html
import socket
import ipaddress
import hashlib
from urllib.parse import urlparse
import urllib.request
import urllib.error

# Source Roles conforming to Data Contract V3.0.4
ROLE_PRIMARY_PUBLISHER = "PRIMARY_PUBLISHER"
ROLE_DISCLOSING_ENTITY = "DISCLOSING_ENTITY"
ROLE_DISTRIBUTION_CHANNEL = "DISTRIBUTION_CHANNEL"
ROLE_DATA_PROVIDER = "DATA_PROVIDER"
ROLE_SYNDICATED_PUBLISHER = "SYNDICATED_PUBLISHER"

VALID_SOURCE_ROLES = {
    ROLE_PRIMARY_PUBLISHER,
    ROLE_DISCLOSING_ENTITY,
    ROLE_DISTRIBUTION_CHANNEL,
    ROLE_DATA_PROVIDER,
    ROLE_SYNDICATED_PUBLISHER
}

ROLE_ABBREVIATIONS = {
    ROLE_PRIMARY_PUBLISHER: "PRI",
    ROLE_DISCLOSING_ENTITY: "DIS",
    ROLE_DISTRIBUTION_CHANNEL: "DST",
    ROLE_DATA_PROVIDER: "DAT",
    ROLE_SYNDICATED_PUBLISHER: "SYN"
}

VALID_CANONICAL_CATEGORIES = {
    "MACRO_MONETARY",
    "BANKING_CREDIT",
    "FINTECH_PAYMENT",
    "CAPITAL_MARKETS",
    "CORPORATE_ENTERPRISE",
    "GLOBAL_MACRO"
}

# Authoritative & Credible Domain Registry
TRUSTED_DOMAINS = {
    # Government & Regulatory
    "sbv.gov.vn": "Ngân hàng Nhà nước Việt Nam",
    "gso.gov.vn": "Tổng cục Thống kê Việt Nam (NSO)",
    "nso.gov.vn": "Tổng cục Thống kê Việt Nam (NSO)",
    "mof.gov.vn": "Bộ Tài chính Việt Nam",
    "hsx.vn": "Sở Giao dịch Chứng khoán TP.HCM (HoSE)",
    "hnx.vn": "Sở Giao dịch Chứng khoán Hà Nội (HNX)",
    "napas.com.vn": "Công ty Cổ phần Thanh toán Quốc gia Việt Nam (NAPAS)",
    
    # Financial Newsrooms & Press
    "tuoitre.vn": "Báo Tuổi Trẻ",
    "thanhnien.vn": "Báo Thanh Niên",
    "tienphong.vn": "Báo Tiền Phong",
    "vneconomy.vn": "Tạp chí Kinh tế Việt Nam (VnEconomy)",
    "baodautu.vn": "Báo Đầu tư",
    "vietstock.vn": "Vietstock Finance",
    "cafef.vn": "CafeF / VCCorp",
    "cafebiz.vn": "CafeBiz / VCCorp",
    "chinhphu.vn": "Cổng Thông tin điện tử Chính phủ",
    "vietnamnet.vn": "Báo VietNamNet",
    "tapchicongthuong.vn": "Tạp chí Công Thương",
    "bnews.vn": "Ban tin Kinh tế TTXVN (Bnews)",
    "vietnamplus.vn": "Báo điện tử VietnamPlus (TTXVN)",
    "nguoiquansat.vn": "Tạp chí Người Quan Sát",
    "daibieunhandan.vn": "Báo Đại biểu Nhân dân",
    "nhandan.vn": "Báo Nhân Dân",
    "thoibaotaichinhvietnam.vn": "Thời báo Tài chính Việt Nam",
    "tapchikinhtetaichinh.vn": "Tạp chí Kinh tế và Tài chính",
    "cand.com.vn": "Báo Công an Nhân dân",
    "congluan.vn": "Báo Nhà báo & Công luận",
    "laodong.vn": "Báo Lao Động",
    "anninhthudo.vn": "Báo An ninh Thủ đô",
    "fili.vn": "Fili / Vietstock",
    "doanhnhantrevietnam.vn": "Tạp chí Doanh nhân Trẻ",
    "infographics.vn": "Thông tấn xã Việt Nam Infographics",
    "doanhnghiephoinhap.vn": "Tạp chí Doanh nghiệp & Hội nhập",
    
    # Commercial Banks & Institutions
    "vietcombank.com.vn": "Ngân hàng TMCP Ngoại thương Việt Nam (Vietcombank)",
    "bidv.com.vn": "Ngân hàng TMCP Đầu tư và Phát triển Việt Nam (BIDV)",
    "vietinbank.vn": "Ngân hàng TMCP Công Thương Việt Nam (VietinBank)",
    "techcombank.com.vn": "Ngân hàng TMCP Kỹ thương Việt Nam (Techcombank)",
    "vpbank.com.vn": "Ngân hàng TMCP Việt Nam Thịnh Vượng (VPBank)",
    "mbbank.com.vn": "Ngân hàng TMCP Quân đội (MB)",
    "pgbank.com.vn": "Ngân hàng TMCP Thịnh vượng và Phát triển (PGBank)",
    "lpbank.com.vn": "Ngân hàng TMCP Lộc Phát Việt Nam (LPBank)",
    "ocb.com.vn": "Ngân hàng TMCP Phương Đông (OCB)",
    "hdbank.com.vn": "Ngân hàng TMCP Phát triển TP.HCM (HDBank)",
    "acb.com.vn": "Ngân hàng TMCP Á Châu (ACB)",
    "cake.vn": "Ngân hàng số Cake by VPBank"
}

GENERIC_HOMEPAGES = {
    "https://sbv.gov.vn", "https://sbv.gov.vn/",
    "https://www.sbv.gov.vn", "https://www.sbv.gov.vn/",
    "https://gso.gov.vn", "https://gso.gov.vn/",
    "https://hsx.vn", "https://hsx.vn/",
    "https://hnx.vn", "https://hnx.vn/",
    "https://cafef.vn", "https://cafef.vn/",
    "https://vietstock.vn", "https://vietstock.vn/",
    "https://vneconomy.vn", "https://vneconomy.vn/",
    "https://tuoitre.vn", "https://tuoitre.vn/",
    "https://baodautu.vn", "https://baodautu.vn/"
}


def is_ip_private_or_loopback(ip_str: str) -> bool:
    """Checks if an IP string is loopback, private, link-local, or reserved."""
    try:
        ip = ipaddress.ip_address(ip_str)
        return (ip.is_private or ip.is_loopback or ip.is_link_local or
                ip.is_multicast or ip.is_reserved or ip.is_unspecified)
    except ValueError:
        return True


def compute_file_sha256(filepath: str) -> str:
    """Computes byte-exact SHA-256 hash of a file on disk."""
    if not os.path.exists(filepath):
        return None
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest().lower()


def validate_hostname_boundary(url: str, test_mode: bool = False) -> tuple:
    """
    Validates URL scheme, hostname, anti-spoofing, and SSRF/DNS rebinding defense.
    Returns (is_valid: bool, reason_or_domain: str)
    """
    if not url:
        return False, "EMPTY_URL"
    try:
        parsed = urlparse(url.strip())
        if parsed.scheme not in ["http", "https"]:
            return False, f"INVALID_SCHEME: {parsed.scheme}"
            
        hostname = (parsed.hostname or "").lower()
        if not hostname:
            return False, "MISSING_HOSTNAME"
            
        # Test mode exception
        if test_mode and hostname in ["localhost", "127.0.0.1", "::1"]:
            return True, "localhost"
            
        # Reject localhost in production
        if hostname in ["localhost", "127.0.0.1", "::1"]:
            return False, "LOCALHOST_ACCESS_PROHIBITED"

        # Check against trusted domains (exact match or proper subdomain)
        matched_domain = None
        for trusted in TRUSTED_DOMAINS:
            if hostname == trusted or hostname.endswith("." + trusted):
                matched_domain = trusted
                break
                
        if not matched_domain:
            return False, f"UNTRUSTED_HOSTNAME: {hostname}"

        # SSRF: Resolve DNS and check if IP is private or loopback
        if not test_mode:
            try:
                addr_info = socket.getaddrinfo(hostname, None)
                for entry in addr_info:
                    ip_str = entry[4][0]
                    if is_ip_private_or_loopback(ip_str):
                        return False, f"SSRF_PROTECTION_BLOCKED_PRIVATE_IP: {ip_str}"
            except socket.gaierror as e:
                return False, f"DNS_RESOLUTION_FAILED: {str(e)}"
            except Exception as e:
                return False, f"IP_VALIDATION_ERROR: {str(e)}"

        return True, matched_domain
    except Exception as e:
        return False, f"URL_PARSE_ERROR: {str(e)}"


class BoundaryRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Enforces zero-trust domain boundaries and SSRF defenses on all HTTP redirects."""
    def __init__(self, test_mode: bool = False):
        self.test_mode = test_mode
        super().__init__()

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        is_valid, reason = validate_hostname_boundary(newurl, test_mode=self.test_mode)
        if not is_valid:
            raise urllib.error.HTTPError(
                newurl, 302,
                f"REDIRECT_SECURITY_VIOLATION: {reason}",
                headers, fp
            )
        return super().redirect_request(req, fp, code, msg, headers, newurl)


# -----------------------------------------------------------------------------
# Deep Numeric Grounding and Fact Tampering Detection Utilities
# -----------------------------------------------------------------------------

def extract_numeric_variants(raw_str: str) -> set:
    """Generates set of normalized float/integer string representations for a number."""
    if not raw_str:
        return set()
    s = str(raw_str).strip()
    is_neg = s.startswith("-")
    if is_neg:
        s = s[1:].strip()
        
    variants = set()
    
    # Raw clean digits
    digits_only = re.sub(r'[\.,]', '', s)
    if digits_only:
        variants.add(f"-{digits_only}" if is_neg else digits_only)
        
    # Standard decimal float interpretation
    # 1. Period as decimal, comma as thousands
    s1 = s.replace(",", "")
    try:
        f1 = float(s1)
        v1 = f"{-f1:.4f}" if is_neg else f"{f1:.4f}"
        v1_clean = v1.rstrip("0").rstrip(".")
        variants.add(v1_clean)
        variants.add(str(int(f1)) if f1.is_integer() else v1_clean)
    except ValueError:
        pass
        
    # 2. Comma as decimal, period as thousands (Vietnamese standard)
    s2 = s.replace(".", "").replace(",", ".")
    try:
        f2 = float(s2)
        v2 = f"{-f2:.4f}" if is_neg else f"{f2:.4f}"
        v2_clean = v2.rstrip("0").rstrip(".")
        variants.add(v2_clean)
        variants.add(str(int(f2)) if f2.is_integer() else v2_clean)
    except ValueError:
        pass
        
    return variants


def parse_quote_numbers(quote_text: str) -> list:
    """
    Extracts all numeric tokens from text and associates them with nearby unit and direction words.
    """
    if not quote_text:
        return []
    results = []
    pattern = r'(?P<sign>[+-])?\s*(?P<num>\b\d{1,3}(?:[.,]\d{3})*(?:[.,]\d+)?|\b\d+(?:[.,]\d+)?)'
    for m in re.finditer(pattern, quote_text):
        full_num = m.group(0).strip()
        raw_num = m.group('num').strip()
        sign = m.group('sign') or ""
        signed_num = f"{sign}{raw_num}"
        
        start, end = m.span()
        ctx_before = quote_text[max(0, start - 40):start].lower()
        ctx_after = quote_text[end:min(len(quote_text), end + 40)].lower()
        ctx_full = f"{ctx_before} {ctx_after}"
        
        # Detect direction (word-bounded so 'kỳ hạn' never matches 'hạ')
        down_pat = r'(?:\b(?:giảm|hạ|rơi|sụt|bán ròng|hút ròng|lỗ|âm|thấp hơn)\b|^\s*-)'
        up_pat = r'(?:\b(?:tăng|vọt|leo|mua ròng|bơm ròng|báo lãi|cao hơn)\b|^\s*\+)'

        direction = "UNKNOWN"
        if re.search(down_pat, ctx_full, re.I) or sign == "-":
            direction = "DOWN"
        elif re.search(up_pat, ctx_full, re.I) or sign == "+" or (re.search(r'\blãi\b', ctx_full, re.I) and "lãi suất" not in ctx_full):
            direction = "UP"
            
        # Detect unit phrase immediately attached to number
        u_match = re.match(r'^\s*([%/\$a-zA-Zà-ỹ]+(?:\s+[%/\$a-zA-Zà-ỹ]+)?)', ctx_after)
        imm = u_match.group(1).lower() if u_match else ""

        unit = "UNKNOWN"
        if "điểm %" in imm or "điểm phần trăm" in imm or "điểm %" in ctx_after[:20] or "điểm phần trăm" in ctx_after[:25]:
            unit = "điểm %"
        elif "triệu đồng/lượng" in imm or "triệu đồng/lượng" in ctx_after[:25]:
            unit = "triệu đồng/lượng"
        elif "đồng/lượng" in imm or "đồng/lượng" in ctx_after[:25]:
            unit = "đồng/lượng"
        elif "tỷ đồng" in imm or "tỷ vnd" in imm:
            unit = "tỷ đồng"
        elif "triệu usd" in imm or "triệu đô" in imm:
            unit = "triệu USD"
        elif "đồng/usd" in imm or "vnd/usd" in imm:
            unit = "đồng/USD"
        elif "tỷ" in imm:
            unit = "tỷ"
        elif "triệu" in imm:
            unit = "triệu"
        elif "usd" in imm or "$" in imm or "đô" in imm:
            unit = "USD"
        elif "vnd" in imm or "đồng" in imm:
            unit = "VND"
        elif "%" in imm or "phần trăm" in imm:
            unit = "%"
        elif "điểm" in imm:
            unit = "điểm"
        else:
            # Fallback to local 20-char context window
            if "tỷ đồng" in ctx_after[:25] or "tỷ vnd" in ctx_after[:25]:
                unit = "tỷ đồng"
            elif "triệu usd" in ctx_after[:25] or "triệu đô" in ctx_after[:25]:
                unit = "triệu USD"
            elif "đồng/usd" in ctx_after[:20] or "vnd/usd" in ctx_after[:20]:
                unit = "đồng/USD"
            elif "tỷ" in ctx_after[:15]:
                unit = "tỷ"
            elif "triệu" in ctx_after[:15]:
                unit = "triệu"
            elif "usd" in ctx_after[:15] or "$" in ctx_after[:15] or "đô" in ctx_after[:15]:
                unit = "USD"
            elif "vnd" in ctx_after[:15] or "đồng" in ctx_after[:15]:
                unit = "VND"
            elif "%" in ctx_after[:15]:
                unit = "%"
            elif "điểm" in ctx_after[:15]:
                unit = "điểm"
            
        variants = extract_numeric_variants(signed_num)
        results.append({
            "raw": full_num,
            "variants": variants,
            "unit": unit,
            "direction": direction,
            "ctx_after": ctx_after,
            "context": ctx_full
        })
    return results


def extract_main_article_body(html_text: str) -> str:
    """
    Extracts the main article body text from raw HTML snapshot.
    Strictly excludes:
    - Head, navigation menus, headers, footers (<head>, <nav>, <header>, <footer>, <aside>)
    - Related article widgets, stream boxes ('tin liên quan', 'tin cùng chuyên mục', 'bài viết khác', etc.)
    - Sidebars, advertisements, social widgets, comment sections
    Returns clean normalized main article text.
    """
    if not html_text:
        return ""
    import html as html_module
    text = html_module.unescape(html_text)

    # 1. Remove head and non-content tags and photo captions
    text = re.sub(r'<(head|script|style|nav|header|footer|aside|noscript|iframe|figure|figcaption)[^>]*>.*?</\1>', ' ', text, flags=re.I | re.DOTALL)

    # 2. Remove sidebar, related news, banner, ads, comment containers
    noise_pattern = (
        r'<(div|section|aside|ul|ol)[^>]+(?:class|id)=[\"\'][^\"\']*'
        r'(?:sidebar|footer|nav|banner|ads|comment|social|related|tin-lien-quan|tin-cung-chuyen-muc|'
        r'tin-khac|bai-viet-khac|tinkhac|box-category|box-related|box-tin-lien-quan|cookie|tag|VCSortableInPreviewMode)[^\"\']*[\"\'][^>]*>.*?</\1>'
    )
    for _ in range(3):
        text = re.sub(noise_pattern, ' ', text, flags=re.I | re.DOTALL)

    def _extract_balanced_tag(html_str: str, start_pat: str, tag_name: str = 'div') -> str:
        m = re.search(start_pat, html_str, re.I)
        if not m:
            return ""
        start_pos = m.end()
        depth = 1
        tag_re = re.compile(rf'<(/?{tag_name}\b[^>]*)>', re.I)
        for tm in tag_re.finditer(html_str, start_pos):
            t_str = tm.group(1).lower()
            if t_str.startswith("/"):
                depth -= 1
                if depth == 0:
                    return html_str[start_pos:tm.start()]
            elif not t_str.endswith("/"):
                depth += 1
        return html_str[start_pos:]

    # 3. Look for explicit article containers using balanced tag matching
    article_html = ""

    # A. VnEconomy: <main class="...article-editor...">
    c_main = _extract_balanced_tag(text, r'<main[^>]+class=[\"\'][^\"\']*article-editor[^\"\']*[\"\'][^>]*>', 'main')
    if c_main and len(re.sub(r'<[^>]+>', ' ', c_main).strip()) > 80:
        article_html = c_main

    # B. Báo Đầu tư: <div id="content_detail_news">
    if not article_html:
        c_bdt = _extract_balanced_tag(text, r'<div[^>]+id=[\"\']content_detail_news[\"\'][^>]*>', 'div')
        if c_bdt and len(re.sub(r'<[^>]+>', ' ', c_bdt).strip()) > 80:
            article_html = c_bdt

    # C. Safe <article> container (excluding item/card/sidebar)
    if not article_html:
        for m_art in re.finditer(r'<article\b([^>]*)>(.*?)</article>', text, re.I | re.DOTALL):
            art_attrs = m_art.group(1).lower()
            if any(bad in art_attrs for bad in ['box-category', 'item', 'sidebar', 'card', 'related']):
                continue
            art_content = m_art.group(2)
            if len(re.sub(r'<[^>]+>', ' ', art_content).strip()) > 80:
                article_html = art_content
                break

    # D. Common article classes (Tuổi Trẻ, CafeF, etc.)
    if not article_html:
        class_pats = [
            r'<div[^>]+class=[\"\'][^\"\']*(?:detail-content|content-detail|detail__cmain|detail-cmain|singular-content|content-news|article-body|maincontent|baiviet-noidung|article__body|cms-body)[^\"\']*[\"\'][^>]*>',
            r'<div[^>]+id=[\"\'](?:main-content|article-content|content-detail|main-detail|abody)[\"\'][^>]*>'
        ]
        for cp in class_pats:
            c_html = _extract_balanced_tag(text, cp, 'div')
            if c_html and len(re.sub(r'<[^>]+>', ' ', c_html).strip()) > 80:
                article_html = c_html
                break

    if article_html:
        # Strip nested related widgets and photo blocks if any were inside the container
        article_html = re.sub(
            r'<(div|section|ul|figure|figcaption)[^>]+(?:class|id)=[\"\'][^\"\']*(?:related|tin-lien-quan|box-tin-lien-quan|tin-cung-chuyen-muc|tin-khac|bai-viet-khac|VCSortableInPreviewMode|PhotoCMS_Caption)[^\"\']*[\"\'][^>]*>.*?</\1>',
            ' ', article_html, flags=re.I | re.DOTALL
        )
        article_html = re.sub(r'(?<=\d)</?(?:span|b|strong|i|em|u|font)\b[^>]*>(?=\d)', '', article_html, flags=re.I)
        clean_text = re.sub(r'<[^>]+>', ' ', article_html)
    else:
        # Fallback to <p> tags only (never fall back to raw full HTML snapshot)
        paragraphs = re.findall(r'<p[^>]*>(.*?)</p>', text, re.I | re.DOTALL)
        clean_p = []
        for p in paragraphs:
            p_low = p.lower()
            if any(term in p_low for term in ["tin liên quan", "bài viết liên quan", "xem thêm", "đọc thêm", "tin cùng chuyên mục", "watchlist mới nhất"]):
                continue
            p = re.sub(r'(?<=\d)</?(?:span|b|strong|i|em|u|font)\b[^>]*>(?=\d)', '', p, flags=re.I)
            pt = re.sub(r'<[^>]+>', ' ', p).strip()
            if re.search(r'\|\s*\d{1,2}[-/]\d{1,2}[-/]\d{4}.*[AP]M\s*\|', pt):
                continue
            if len(pt) > 20:
                clean_p.append(pt)
        if clean_p:
            clean_text = " ".join(clean_p)
        else:
            # Fallback for plain text or simple fixture without <p> tags
            body_match = re.search(r'<body[^>]*>(.*?)</body>', text, re.I | re.DOTALL)
            raw_cand = body_match.group(1) if body_match else text
            clean_text = re.sub(r'<[^>]+>', ' ', raw_cand).strip()

    return " ".join(clean_text.split())


class SourceVerificationEngine:
    """
    Zero-Trust Source Verification & Financial Fact Integrity Engine V3.0 (Phase 05B-R1.2)
    Audits live URLs, raw snapshots, byte SHA-256 parity, and detects all fact tampering.
    """

    def __init__(self, raw_evidence_dir: str, http_timeout: int = 10, test_mode: bool = False):
        self.raw_evidence_dir = raw_evidence_dir
        os.makedirs(raw_evidence_dir, exist_ok=True)
        self.http_timeout = http_timeout
        self.test_mode = test_mode
        self.redirect_handler = BoundaryRedirectHandler(test_mode=self.test_mode)
        self.opener = urllib.request.build_opener(self.redirect_handler)

    def resolve_snapshot_path(self, snapshot_path: str) -> str:
        """Resolves relative snapshot filename to full absolute path."""
        if not snapshot_path:
            return None
        if os.path.isabs(snapshot_path) and os.path.exists(snapshot_path):
            return snapshot_path
        
        cand = os.path.join(self.raw_evidence_dir, os.path.basename(snapshot_path))
        if os.path.exists(cand):
            return cand
            
        if os.path.exists(snapshot_path):
            return os.path.abspath(snapshot_path)
            
        return None

    def verify_financial_facts(self, fin_facts: list, snapshot_text: str, event: dict, main_article_body: str = None) -> list:
        """
        Deep Financial Fact Verification:
        Enforces CLAIM -> SOURCE SENTENCE -> EXTRACTED EXPRESSION -> NORMALIZED VALUE -> UNIT -> POLARITY -> PERIOD -> ENTITY.
        Detects tampering with numericValue, unit, polarity, entity, reportingPeriod, and expression.
        Returns list of failure messages (empty if all facts valid).
        """
        failures = []
        if not isinstance(fin_facts, list):
            return ["FINANCIAL_FACTS_MUST_BE_ARRAY"]
            
        norm_snapshot = " ".join(snapshot_text.split()).lower()
        clean_snap_raw = re.sub(r'(?<=\d)</?(?:span|b|strong|i|em|u|font)\b[^>]*>(?=\d)', '', snapshot_text, flags=re.I)
        norm_clean_snapshot = " ".join(html.unescape(re.sub(r'<[^>]+>', ' ', clean_snap_raw)).split()).lower()
        norm_main_lower = " ".join(main_article_body.split()).lower() if main_article_body else ""
        
        if not norm_main_lower and fin_facts:
            failures.append("EMPTY_MAIN_ARTICLE_BODY: Main article body is empty or unavailable.")
        
        for idx, fact in enumerate(fin_facts):
            if not isinstance(fact, dict):
                failures.append(f"FINANCIAL_FACT_{idx}_MUST_BE_OBJECT")
                continue
                
            # 1. Required attribute check
            for req in ["extractedExpression", "numericValue", "unit", "metricName"]:
                if req not in fact or fact[req] is None:
                    failures.append(f"FINANCIAL_FACT_{idx}_MISSING_{req.upper()}")
                    
            # 2. String numericValue enforcement
            num_val_raw = fact.get("numericValue")
            if num_val_raw is not None and not isinstance(num_val_raw, str):
                failures.append(f"FINANCIAL_FACT_{idx}_NUMERIC_VALUE_MUST_BE_STRING")
                continue

            # 3. Context quote check
            cq = fact.get("contextQuote") or event.get("supportingQuote") or ""
            if not cq:
                failures.append(f"FINANCIAL_FACT_{idx}_MISSING_CONTEXT_QUOTE")
                continue
                
            norm_cq = " ".join(cq.split())
            if norm_main_lower and norm_cq.lower() not in norm_main_lower:
                failures.append(f"FINANCIAL_FACT_{idx}_CONTEXT_QUOTE_NOT_IN_MAIN_ARTICLE: '{cq[:40]}...'")
                continue

            # 4. Extracted expression grounding
            expr = fact.get("extractedExpression", "")
            if expr and " ".join(expr.split()).lower() not in norm_cq.lower():
                failures.append(f"FACT_MISMATCH_EXPRESSION: Extracted expression '{expr}' not found in context quote.")

            # 5. Numeric value grounding & tampering detection
            claimed_variants = extract_numeric_variants(num_val_raw)
            quote_numbers = parse_quote_numbers(cq)
            
            if not quote_numbers:
                failures.append(f"FACT_NOT_GROUNDED_IN_EVIDENCE: Context quote contains no numeric measurements to verify fact {idx}.")
                continue

            matched_num = None
            for qn in quote_numbers:
                if claimed_variants.intersection(qn["variants"]):
                    matched_num = qn
                    break
                    
            if not matched_num:
                failures.append(f"FACT_MISMATCH_VALUE: Claimed numeric value '{num_val_raw}' not found in evidence quote.")
                continue

            # 6. Unit compatibility check
            claimed_unit = fact.get("unit", "").lower().strip()
            ctx_after = matched_num.get("ctx_after", "")
            quote_unit = matched_num.get("unit", "").lower()
            
            # Explicit unit conflicts:
            # Conflict A: USD vs VND / đồng
            if ("usd" in claimed_unit or "$" in claimed_unit or "đô" in claimed_unit) and not ("vnd" in claimed_unit or "đồng" in claimed_unit):
                if ("đồng" in quote_unit or "vnd" in quote_unit or ("đồng" in ctx_after[:20] and "usd" not in quote_unit)):
                    failures.append(f"FACT_MISMATCH_UNIT: Claimed unit '{claimed_unit}' incompatible with evidence currency (VND/đồng).")
            elif ("vnd" in claimed_unit or "đồng" in claimed_unit) and not ("usd" in claimed_unit or "$" in claimed_unit or "đô" in claimed_unit):
                if ("usd" in quote_unit or "$" in quote_unit) and not ("đồng" in quote_unit or "vnd" in quote_unit or "đồng/usd" in ctx_after[:20] or "vnd/usd" in ctx_after[:20]):
                    failures.append(f"FACT_MISMATCH_UNIT: Claimed unit '{claimed_unit}' incompatible with evidence currency (USD).")
            # Conflict B: tỷ vs triệu
            elif "tỷ" in claimed_unit and ("triệu" in quote_unit and "tỷ" not in quote_unit):
                failures.append(f"FACT_MISMATCH_UNIT: Claimed unit '{claimed_unit}' incompatible with evidence unit (triệu).")
            elif "triệu" in claimed_unit and ("tỷ" in quote_unit and "triệu" not in quote_unit):
                failures.append(f"FACT_MISMATCH_UNIT: Claimed unit '{claimed_unit}' incompatible with evidence unit (tỷ).")
            # Conflict C: % vs điểm (excluding composite unit "điểm %")
            elif quote_unit != "điểm %" and "điểm %" not in claimed_unit:
                if "%" in claimed_unit and ("điểm" in quote_unit and "%" not in quote_unit):
                    failures.append(f"FACT_MISMATCH_UNIT: Claimed unit '{claimed_unit}' incompatible with evidence unit (điểm).")
                elif "điểm" in claimed_unit and ("%" in quote_unit and "điểm" not in quote_unit):
                    failures.append(f"FACT_MISMATCH_UNIT: Claimed unit '{claimed_unit}' incompatible with evidence unit (%).")

            # 6.1 P0-04 Semantic Integrity Checks
            metric_low = fact.get("metricName", "").lower()
            cq_low = norm_cq.lower()
            if metric_low.startswith("chỉ số tài chính") or fact.get("verificationStatus") == "REVIEW_REQUIRED":
                failures.append(f"FACT_AMBIGUOUS_CLASSIFICATION_REVIEW_REQUIRED: Metric '{fact.get('metricName')}' is ambiguous and cannot be published as a verified financial fact.")
            if ("dư nợ tín dụng" in metric_low or "tăng trưởng tín dụng" in metric_low) and ("sở hữu cổ phần" in cq_low or "vốn điều lệ" in cq_low):
                failures.append("FACT_SEMANTIC_MISMATCH_SHAREHOLDING_AS_CREDIT_GROWTH: Shareholding percentage cannot be classified as credit growth.")
            if ("tỷ lệ sở hữu" in metric_low or "vốn điều lệ" in metric_low) and ("nhu cầu vốn của nền kinh tế" in cq_low or "cung ứng vốn" in cq_low):
                failures.append("FACT_SEMANTIC_MISMATCH_CAPITAL_ALLOCATION_AS_OWNERSHIP: Capital allocation share cannot be classified as ownership ratio.")
            if "tỷ giá" in metric_low and any(u in claimed_unit for u in ["tỷ usd", "triệu usd", "tỷ đồng", "triệu đồng"]):
                failures.append("FACT_SEMANTIC_MISMATCH_VOLUME_AS_EXCHANGE_RATE: Foreign-currency or liquidity volume cannot be classified as an exchange-rate observation.")
            if fact.get("factType") == "POLICY_THRESHOLD" and (fact.get("polarity") in ("UP", "DOWN")):
                failures.append("FACT_SEMANTIC_MISMATCH_POLICY_THRESHOLD_POLARITY: Policy threshold must not carry performance movement polarity.")

            # 7. Direction / Polarity compatibility check
            claimed_polarity = fact.get("polarity") or fact.get("direction")
            if not claimed_polarity and fact.get("factType") != "POLICY_THRESHOLD":
                mn = fact.get("metricName", "").lower()
                if "giảm" in mn or "hút ròng" in mn or "bán ròng" in mn or "lỗ" in mn:
                    claimed_polarity = "DOWN"
                elif "tăng" in mn or "bơm ròng" in mn or "mua ròng" in mn or "báo lãi" in mn or ("lãi" in mn and "lãi suất" not in mn):
                    claimed_polarity = "UP"

            if claimed_polarity and matched_num["direction"] != "UNKNOWN":
                if claimed_polarity.upper() == "UP" and matched_num["direction"] == "DOWN":
                    failures.append(f"FACT_MISMATCH_DIRECTION: Polarity mismatch: claim asserts increase/UP but quote indicates decrease/DOWN.")
                elif claimed_polarity.upper() == "DOWN" and matched_num["direction"] == "UP":
                    failures.append(f"FACT_MISMATCH_DIRECTION: Polarity mismatch: claim asserts decrease/DOWN but quote indicates increase/UP.")

            # 8. Entity grounding check
            entity = fact.get("entity")
            if entity and entity.lower() not in norm_snapshot and entity.lower() not in norm_clean_snapshot:
                failures.append(f"FACT_MISMATCH_ENTITY: Entity '{entity}' not mentioned in evidence snapshot.")

            # 9. Reporting period check
            period = fact.get("reportingPeriod") or fact.get("observationPeriod")
            if period and period.lower() not in norm_snapshot and period.lower() not in norm_clean_snapshot:
                failures.append(f"FACT_MISMATCH_PERIOD: Reporting period '{period}' not found in evidence snapshot.")

        return failures

    def verify_single_event(self, event: dict, provenance_records: list = None,
                            verify_live_http: bool = False,
                            http_retrieval_records: dict = None) -> tuple:
        """
        Validates a single candidate event according to Data Contract V3.0.4:
        1. URL domain boundary & SSRF protection
        2. Generic homepage rejection
        3. Real HTTP retrieval verification and redirect boundary audit
        4. Response byte SHA-256 parity between retrieval ledger and stored snapshot
        5. Raw evidence snapshot existence and byte-exact SHA-256 match
        6. Verbatim supporting quote presence in snapshot
        7. Financial facts extraction integrity (tampering defense & grounding)
        8. Category validation (enum conformity)
        9. Editorial relevance validation (non-irrelevant)
        10. Main entities verification (not publisher domain)
        Returns (is_verified: bool, failures: list)
        """
        event_id = event.get("eventId", "UNKNOWN_EVENT")
        failures = []

        # 1. URL Domain Boundary
        orig_url = event.get("originalUrl")
        if not orig_url:
            failures.append("MISSING_ORIGINAL_URL")
        else:
            if orig_url in GENERIC_HOMEPAGES:
                failures.append(f"GENERIC_HOMEPAGE_REJECTED: {orig_url}")
            is_valid_orig, orig_reason = validate_hostname_boundary(orig_url, test_mode=self.test_mode)
            if not is_valid_orig:
                failures.append(f"ORIGINAL_URL_INVALID: {orig_reason}")

        synd_url = event.get("syndicatedUrl")
        if synd_url:
            is_valid_synd, synd_reason = validate_hostname_boundary(synd_url, test_mode=self.test_mode)
            if not is_valid_synd:
                failures.append(f"SYNDICATED_URL_INVALID: {synd_reason}")

        # Check recorded HTTP status if event includes retrieval metadata
        if "httpStatusCode" in event and event["httpStatusCode"] != 200:
            failures.append(f"HTTP_RETRIEVAL_STATUS_ERROR: {event['httpStatusCode']}")

        # 2. Live HTTP Verification (when enabled)
        if verify_live_http and orig_url:
            success, code, final_url, live_text, err = self.verify_url_live_http(orig_url)
            if not success:
                failures.append(f"LIVE_HTTP_RETRIEVAL_FAILED: {err} (URL: {orig_url})")
            else:
                quote = event.get("supportingQuote")
                if quote:
                    norm_quote = " ".join(quote.split())
                    norm_live = " ".join(live_text.split())
                    if norm_quote not in norm_live:
                        failures.append(f"QUOTE_NOT_IN_LIVE_RETRIEVED_PAGE: '{quote[:50]}...'")

        # 3. HTTP Retrieval Ledger Audit (Production Verification Path)
        ledger_rec = None
        if http_retrieval_records is not None and orig_url:
            ledger_rec = http_retrieval_records.get(orig_url)
            if not ledger_rec:
                failures.append(f"MISSING_HTTP_RETRIEVAL_RECORD: URL '{orig_url}' was never retrieved")
            elif ledger_rec.get("statusCode") != 200:
                failures.append(f"HTTP_RETRIEVAL_FAILED: URL '{orig_url}' returned status {ledger_rec.get('statusCode')}")
            else:
                final_u = ledger_rec.get("finalUrl", orig_url)
                valid_f, r_f = validate_hostname_boundary(final_u, test_mode=self.test_mode)
                if not valid_f:
                    failures.append(f"REDIRECT_TO_UNTRUSTED_DOMAIN: {r_f} ({final_u})")

        # 4. Raw Snapshot Verification
        snapshot_filename = event.get("evidenceSnapshotPath")
        if not snapshot_filename:
            failures.append("MISSING_EVIDENCE_SNAPSHOT_PATH")
            return False, failures

        full_snapshot_path = self.resolve_snapshot_path(snapshot_filename)
        if not full_snapshot_path:
            failures.append(f"SNAPSHOT_NOT_FOUND_ON_DISK: {snapshot_filename}")
            return False, failures

        # Byte SHA-256 validation
        actual_sha256 = compute_file_sha256(full_snapshot_path)
        expected_sha256 = event.get("evidenceSha256", "").lower()

        if not expected_sha256:
            failures.append("MISSING_EVIDENCE_SHA256")
        elif actual_sha256 != expected_sha256:
            failures.append(f"SHA256_MISMATCH: expected {expected_sha256[:12]}... got {actual_sha256[:12]}...")

        # Parity check between retrieval ledger and on-disk snapshot
        if ledger_rec and ledger_rec.get("responseSha256"):
            ledger_sha = ledger_rec.get("responseSha256", "").lower()
            if ledger_sha != actual_sha256:
                failures.append(f"LEDGER_RESPONSE_SHA256_MISMATCH: ledger {ledger_sha[:10]} != disk {actual_sha256[:10]}")

        # Read snapshot content for quote and fact verification (handling gzip transparently and failing closed on corruption)
        snapshot_text = ""
        try:
            with open(full_snapshot_path, "rb") as f:
                raw_bytes = f.read()
            if raw_bytes[:2] == b'\x1f\x8b':
                try:
                    snapshot_text = gzip.decompress(raw_bytes).decode("utf-8", errors="replace")
                except Exception as gz_err:
                    failures.append(f"CANNOT_READ_SNAPSHOT: CORRUPTED_GZIP_STREAM ({str(gz_err)})")
                    return False, failures
            else:
                snapshot_text = raw_bytes.decode("utf-8", errors="replace")
        except Exception as e:
            failures.append(f"CANNOT_READ_SNAPSHOT: {str(e)}")
            return False, failures

        # 5. Supporting Quote Traceability: Must belong to extracted main article body!
        quote = event.get("supportingQuote")
        main_body_text = extract_main_article_body(snapshot_text)
        norm_main_body = " ".join(main_body_text.split()) if main_body_text else ""
        norm_snapshot = " ".join(snapshot_text.split())
        clean_snap_raw = re.sub(r'(?<=\d)</?(?:span|b|strong|i|em|u|font)\b[^>]*>(?=\d)', '', snapshot_text, flags=re.I)
        norm_clean_snapshot = " ".join(html.unescape(re.sub(r'<[^>]+>', ' ', clean_snap_raw)).split())

        if not norm_main_body or len(norm_main_body.strip()) == 0:
            failures.append("EMPTY_MAIN_ARTICLE_BODY: Main article body could not be extracted from snapshot.")
        if quote:
            norm_quote = " ".join(quote.split())
            if norm_quote not in norm_snapshot and norm_quote not in norm_clean_snapshot:
                failures.append(f"QUOTE_NOT_GROUNDED_IN_SNAPSHOT: '{quote[:60]}...'")
            elif norm_quote not in norm_main_body:
                failures.append(
                    f"SUPPORTING_QUOTE_NOT_IN_MAIN_ARTICLE: Supporting quote '{quote[:60]}...' is not found within the extracted main article body."
                )

        # 6. Deep Financial Facts Verification
        fin_facts = event.get("financialFacts", [])
        fact_failures = self.verify_financial_facts(fin_facts, snapshot_text, event, main_article_body=norm_main_body)
        failures.extend(fact_failures)

        # 7. Category Enum Conformity
        cat = event.get("category")
        if not cat:
            failures.append("MISSING_CATEGORY")
        elif cat not in VALID_CANONICAL_CATEGORIES:
            failures.append(f"INVALID_CATEGORY_ENUM: '{cat}'. Must be one of {sorted(list(VALID_CANONICAL_CATEGORIES))}")

        # 8. Editorial Relevance Validation
        edit_rel = event.get("editorialRelevance")
        if edit_rel == "IRRELEVANT" or event.get("isIrrelevant", False):
            failures.append("REJECTED_IRRELEVANT: Non-financial topic rejected")

        # 9. Main Entities Check (Must not be publisher domain)
        main_entities = event.get("mainEntities", [])
        if main_entities:
            for ent in main_entities:
                if ent in TRUSTED_DOMAINS or ent in ["cafef.vn", "tuoitre.vn", "thanhnien.vn", "vneconomy.vn", "baodautu.vn"]:
                    failures.append(f"INVALID_MAIN_ENTITY_PUBLISHER_DOMAIN: '{ent}' cannot be mainEntity.")

        # 10. Provenance Record Parity (if provided)
        if provenance_records:
            matching_records = [p for p in provenance_records if p.get("eventId") == event_id]
            if not matching_records:
                failures.append(f"NO_PROVENANCE_RECORDS_FOR_EVENT_{event_id}")
            else:
                for p in matching_records:
                    if p.get("sourceRole") not in VALID_SOURCE_ROLES:
                        failures.append(f"INVALID_SOURCE_ROLE_{p.get('sourceRole')}")

        if failures:
            return False, failures
        return True, "VERIFIED"

    def verify_url_live_http(self, url: str, timeout: int = 8) -> tuple:
        """Executes active live HTTP GET request with redirect validation."""
        if not url:
            return False, 0, "", "", "EMPTY_URL"
        try:
            parsed = urlparse(url)
            if parsed.scheme not in ["http", "https"]:
                return False, 0, "", "", f"INVALID_SCHEME: {parsed.scheme}"
            if url in GENERIC_HOMEPAGES:
                return False, 0, url, "", f"GENERIC_HOMEPAGE_REJECTED: {url}"
            is_valid, domain_reason = validate_hostname_boundary(url, test_mode=self.test_mode)
            if not is_valid:
                return False, 0, url, "", f"UNTRUSTED_DOMAIN: {domain_reason}"

            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) BryanFinTechVerifier/3.0",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
            }
            req = urllib.request.Request(url, headers=headers)
            with self.opener.open(req, timeout=timeout) as resp:
                code = resp.getcode()
                final_url = resp.geturl()
                
                is_valid_final, final_reason = validate_hostname_boundary(final_url, test_mode=self.test_mode)
                if not is_valid_final:
                    return False, code, final_url, "", f"REDIRECT_TO_UNTRUSTED_DOMAIN: {final_reason} ({final_url})"
                    
                content_bytes = resp.read()
                try:
                    content_text = content_bytes.decode("utf-8")
                except UnicodeDecodeError:
                    content_text = content_bytes.decode("latin-1", errors="replace")
                    
                return True, code, final_url, content_text, None
        except urllib.error.HTTPError as e:
            return False, e.code, url, "", f"HTTP_ERROR_{e.code}: {e.reason}"
        except urllib.error.URLError as e:
            return False, 0, url, "", f"NETWORK_OR_URL_ERROR: {e.reason}"
        except Exception as e:
            return False, 0, url, "", f"RETRIEVAL_EXCEPTION: {str(e)}"

    def build_provenance_record(self, edition_id: str, event_id: str, source_role: str,
                                entity_name: str, source_url: str, pub_timestamp: str,
                                retrieved_timestamp: str, evidence_path: str,
                                evidence_sha256: str) -> dict:
        """
        Constructs a single deterministic provenance record strictly conforming to V3.0.4.
        ID format: SRC-{editionId}-{eventId}-{roleAbbr}
        """
        role_abbr = ROLE_ABBREVIATIONS.get(source_role, "SRC")
        source_record_id = f"SRC-{edition_id}-{event_id}-{role_abbr}"
        
        if source_role == ROLE_DISCLOSING_ENTITY:
            hostname_status = "OFFICIAL_DISCLOSURE"
        elif source_role == ROLE_DATA_PROVIDER:
            hostname_status = "LICENSED_DATA_FEED"
        else:
            hostname_status = "DOMAIN_BOUNDARY_VERIFIED"
        
        record = {
            "sourceRecordId": source_record_id,
            "editionId": edition_id,
            "eventId": event_id,
            "sourceRole": source_role,
            "entityName": entity_name,
            "sourceUrl": source_url,
            "pubTimestamp": pub_timestamp,
            "retrievedTimestamp": retrieved_timestamp,
            "evidenceSnapshotPath": evidence_path,
            "evidenceSha256": evidence_sha256.lower(),
            "hostnameStatus": hostname_status
        }
        return record

    def build_provenance_ledger(self, edition_id: str, verified_events: list) -> dict:
        """
        Builds the complete immutable provenance ledger strictly adhering to Data Contract V3.0.4.
        Note: V3.0.4 provenanceLedger disallows additionalProperties.
        """
        records = []
        for event in verified_events:
            event_id = event["eventId"]
            pub_name = event.get("publisher", "Unknown Publisher")
            orig_url = event.get("originalUrl", "")
            pub_ts = event.get("originalPubTimestamp", "")
            ret_ts = event.get("retrievedTimestamp", "")
            ev_path = event.get("evidenceSnapshotPath", "")
            ev_sha = event.get("evidenceSha256", "")

            # 1. Primary Publisher Record
            pri_rec = self.build_provenance_record(
                edition_id=edition_id,
                event_id=event_id,
                source_role=ROLE_PRIMARY_PUBLISHER,
                entity_name=pub_name,
                source_url=orig_url,
                pub_timestamp=pub_ts,
                retrieved_timestamp=ret_ts,
                evidence_path=ev_path,
                evidence_sha256=ev_sha
            )
            records.append(pri_rec)

            # 2. Disclosing Entity Record (if official institution recognized)
            main_entities = event.get("mainEntities", [])
            disclosing_entity = None
            for ent in main_entities:
                if ent in ["NHNN", "SBV", "Ngân hàng Nhà nước", "Bộ Tài chính", "GSO", "NSO", "HSX", "HNX", "NAPAS"]:
                    disclosing_entity = ent
                    break
                    
            if disclosing_entity:
                dis_rec = self.build_provenance_record(
                    edition_id=edition_id,
                    event_id=event_id,
                    source_role=ROLE_DISCLOSING_ENTITY,
                    entity_name=disclosing_entity,
                    source_url=orig_url,
                    pub_timestamp=pub_ts,
                    retrieved_timestamp=ret_ts,
                    evidence_path=ev_path,
                    evidence_sha256=ev_sha
                )
                records.append(dis_rec)

        ledger = {
            "editionId": edition_id,
            "records": records
        }
        return ledger

    def verify_provenance_ledger(self, verified_events: list, provenance_ledger: dict) -> tuple:
        """Audits foreign key integrity, uniqueness, and completeness of provenance ledger."""
        records = provenance_ledger.get("records", [])
        issues = []
        
        seen_ids = set()
        for r in records:
            rid = r.get("sourceRecordId")
            if not rid:
                issues.append("RECORD_MISSING_ID")
            elif rid in seen_ids:
                issues.append(f"DUPLICATE_RECORD_ID: {rid}")
            seen_ids.add(rid)

        event_ids = {e["eventId"] for e in verified_events}
        for r in records:
            eid = r.get("eventId")
            if eid not in event_ids:
                issues.append(f"ORPHAN_PROVENANCE_RECORD: {r.get('sourceRecordId')} points to missing {eid}")

        for eid in event_ids:
            matching = [r for r in records if r.get("eventId") == eid]
            if not matching:
                issues.append(f"EVENT_MISSING_PROVENANCE: {eid}")
            has_pri = any(r.get("sourceRole") == ROLE_PRIMARY_PUBLISHER for r in matching)
            if not has_pri:
                issues.append(f"EVENT_{eid}_MISSING_PRIMARY_PUBLISHER_RECORD")

        if issues:
            return False, issues
        return True, "PROVENANCE_LEDGER_VALID"
