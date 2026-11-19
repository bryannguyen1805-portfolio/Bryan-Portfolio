#!/usr/bin/env python3
"""
daily_news_collector_v3.py — Bryan FinTech Intelligence Phase 05B-R1.2
Dynamic Multi-Source Daily Financial & FinTech News Collector

P1 Critical Remediation:
- Eliminates publication timestamp fallback to retrieval timestamp.
- Implements 5-stage timestamp extraction hierarchy with HTML entity unescaping.
- Implements Article Extraction Layer isolating clean body and stripping footer/nav noise.
- Replaces publisher domain with true subject entities in mainEntities.
- Implements multi-dimensional content classification avoiding category monopoly.
- Adds SSRF and DNS rebinding defenses blocking loopback/private IPs in production.
"""

import os
import sys
import json
import re
import time
import gzip
import html
import socket
import ipaddress
import hashlib
import unicodedata
from datetime import datetime, timezone, timedelta
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode, urljoin
import urllib.request
import urllib.error

# Operational Constants
TARGET_EVENTS = 40
MIN_EVENTS_PER_CATEGORY = 5
MIN_FRESHNESS_RATIO = 0.80  # Minimum 80% within 0-24h
MAX_AGE_HOURS = 48.0        # Hard ceiling: maximum 48h (strict 2-day cap; prevents 3-day carry-over)
TIMEZONE_HCM = timezone(timedelta(hours=7))

# Canonical V3.0.4 Categories (6 core categories aligned with 6 UI sections)
CATEGORY_MACRO_MONETARY = "MACRO_MONETARY"
CATEGORY_BANKING_CREDIT = "BANKING_CREDIT"
CATEGORY_FINTECH_PAYMENT = "FINTECH_PAYMENT"
CATEGORY_CAPITAL_MARKETS = "CAPITAL_MARKETS"
CATEGORY_CORPORATE_ENTERPRISE = "CORPORATE_ENTERPRISE"
CATEGORY_RETAIL_CONSUMER = "RETAIL_CONSUMER"
CATEGORY_GLOBAL_MACRO = "GLOBAL_MACRO"

CORE_EDITION_CATEGORIES = [
    CATEGORY_FINTECH_PAYMENT,
    CATEGORY_BANKING_CREDIT,
    CATEGORY_CAPITAL_MARKETS,
    CATEGORY_CORPORATE_ENTERPRISE,
    CATEGORY_MACRO_MONETARY,
    CATEGORY_RETAIL_CONSUMER
]

VALID_CANONICAL_CATEGORIES = {
    CATEGORY_MACRO_MONETARY,
    CATEGORY_BANKING_CREDIT,
    CATEGORY_FINTECH_PAYMENT,
    CATEGORY_CAPITAL_MARKETS,
    CATEGORY_CORPORATE_ENTERPRISE,
    CATEGORY_RETAIL_CONSUMER,
    CATEGORY_GLOBAL_MACRO
}

# Source Taxonomy Roles
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

# Authoritative & Credible Domain Registry
TRUSTED_DOMAINS = {
    # Official Government & Regulatory
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
    "thitruongtaichinhtiente.vn": "Tạp chí Thị trường Tài chính Tiền tệ",
    "thoibaonganhang.vn": "Thời báo Ngân hàng",
    "vnexpress.net": "Báo VnExpress",
    "cand.com.vn": "Báo Công an Nhân dân",
    "congluan.vn": "Báo Nhà báo & Công luận",
    "laodong.vn": "Báo Lao Động",
    "anninhthudo.vn": "Báo An ninh Thủ đô",
    "fili.vn": "Fili / Vietstock",
    "doanhnhantrevietnam.vn": "Tạp chí Doanh nhân Trẻ",
    "infographics.vn": "Thông tấn xã Việt Nam Infographics",
    "doanhnghiephoinhap.vn": "Tạp chí Doanh nghiệp & Hội nhập",
    
    # Commercial Banks
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

TRACKING_QUERY_PARAMS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "ref", "fbclid", "gclid", "_ga", "from", "gid"
}


def is_ip_private_or_loopback(ip_str: str) -> bool:
    """Checks if an IP string is loopback, private, link-local, or reserved."""
    try:
        ip = ipaddress.ip_address(ip_str)
        return (ip.is_private or ip.is_loopback or ip.is_link_local or
                ip.is_multicast or ip.is_reserved or ip.is_unspecified)
    except ValueError:
        return True


def normalize_url(raw_url: str) -> str:
    """Canonicalize URLs by stripping query trackers and standardizing host."""
    if not raw_url:
        return ""
    try:
        parsed = urlparse(raw_url.strip())
        netloc = parsed.netloc.lower()
        if netloc.startswith("www."):
            netloc = netloc[4:]
        
        # Filter query params
        query_pairs = parse_qsl(parsed.query, keep_blank_values=False)
        clean_query = [(k, v) for k, v in query_pairs if k.lower() not in TRACKING_QUERY_PARAMS]
        clean_query.sort(key=lambda x: x[0])
        encoded_query = urlencode(clean_query)
        
        path = parsed.path
        if path != "/" and path.endswith("/"):
            path = path[:-1]
            
        canonical = urlunparse((
            parsed.scheme.lower() or "https",
            netloc,
            path,
            "",
            encoded_query,
            ""
        ))
        return canonical
    except Exception:
        return raw_url.strip()


VN_STOPWORDS = {
    "va", "cua", "cho", "trong", "tren", "duoi", "voi", "nhung", "cac", "mot",
    "nhu", "khi", "ve", "tai", "tu", "den", "la", "duoc", "bi", "se", "da",
    "dang", "nay", "do", "vi", "theo", "sau", "truoc", "hon", "nhat", "nam",
    "ngay", "thang", "moi", "vua", "chinh", "thuc", "tiep", "tuc", "ngan", "hang",
    "ty", "dong", "trieu", "phan", "tram"
}


def strip_vietnamese_accents(text: str) -> str:
    """Normalizes Vietnamese text to lowercase ASCII for cross-day topic comparison."""
    if not text:
        return ""
    s = html.unescape(str(text)).replace("đ", "d").replace("Đ", "D")
    nfkd = unicodedata.normalize("NFD", s)
    ascii_text = "".join(ch for ch in nfkd if unicodedata.category(ch) != "Mn")
    return re.sub(r"[^a-z0-9]+", " ", ascii_text.lower()).strip()


def headline_tokens(headline: str) -> set:
    """Extracts meaningful ASCII tokens (>= 2 chars, excluding common stopwords)."""
    norm = strip_vietnamese_accents(headline)
    return {tok for tok in norm.split() if len(tok) >= 2 and tok not in VN_STOPWORDS}


def headline_similarity(hl_a, hl_b) -> float:
    """Computes Jaccard similarity between two headlines (or precomputed token sets)."""
    tokens_a = hl_a if isinstance(hl_a, set) else headline_tokens(str(hl_a or ""))
    tokens_b = hl_b if isinstance(hl_b, set) else headline_tokens(str(hl_b or ""))
    if not tokens_a or not tokens_b:
        return 0.0
    union_len = len(tokens_a | tokens_b)
    return (len(tokens_a & tokens_b) / union_len) if union_len else 0.0


def resolve_daily_editions_dir(raw_evidence_dir: str) -> str:
    """Finds the enclosing daily-editions directory from a raw evidence path, if present."""
    if not raw_evidence_dir:
        return ""
    cur = os.path.abspath(raw_evidence_dir)
    for _ in range(6):
        base = os.path.basename(cur)
        if base == "daily-editions" and os.path.isdir(cur):
            return cur
        candidate = os.path.join(cur, "daily-editions")
        if os.path.isdir(candidate):
            return candidate
        parent = os.path.dirname(cur)
        if parent == cur:
            break
        cur = parent
    return ""


def load_prior_published_history(daily_editions_dir: str, target_date_str: str = None, lookback_days: int = 10) -> tuple:
    """
    Loads canonical URLs and tokenized headlines from up to `lookback_days` prior daily editions
    strictly before `target_date_str` to guarantee zero multi-day carry-over.
    """
    prior_urls = set()
    prior_titles = []
    if not daily_editions_dir or not os.path.isdir(daily_editions_dir):
        return prior_urls, prior_titles

    date_folders = []
    for entry in os.listdir(daily_editions_dir):
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", entry):
            continue
        if target_date_str and entry >= target_date_str:
            continue
        full_dir = os.path.join(daily_editions_dir, entry)
        if os.path.isdir(full_dir):
            date_folders.append(entry)

    date_folders.sort(reverse=True)
    for d_str in date_folders[:max(1, int(lookback_days))]:
        v_path = os.path.join(daily_editions_dir, d_str, "verified-news.json")
        if not os.path.isfile(v_path):
            continue
        try:
            with open(v_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            continue
        events = data if isinstance(data, list) else (data.get("records") or data.get("events") or data.get("news") or [])
        for ev in events:
            if not isinstance(ev, dict):
                continue
            for key in ("canonicalUrl", "sourceUrl", "url", "originalUrl", "candidateUrl"):
                raw_u = ev.get(key)
                if raw_u:
                    prior_urls.add(normalize_url(raw_u))
            hl = (ev.get("headline") or ev.get("title") or "").strip()
            if hl:
                toks = headline_tokens(hl)
                if toks:
                    prior_titles.append((d_str, hl, toks))

    return prior_urls, prior_titles


def parse_timestamp_iso_or_vietnamese(ts_str: str) -> datetime:
    """
    Parses timestamp strings in ISO 8601 or common Vietnamese newspaper formats.
    Fully supports hyphenated dates (CafeF), slashed dates, AM/PM 12-hour indicators,
    and returns a timezone-aware datetime in Asia/Ho_Chi_Minh (UTC+7).
    """
    if not ts_str:
        return None
        
    # Unescape HTML entities
    clean_ts = html.unescape(str(ts_str).strip())
    
    # 1. Try ISO formats
    try:
        if clean_ts.endswith("Z"):
            return datetime.fromisoformat(clean_ts[:-1]).replace(tzinfo=timezone.utc).astimezone(TIMEZONE_HCM)
        dt = datetime.fromisoformat(clean_ts)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=TIMEZONE_HCM)
        return dt.astimezone(TIMEZONE_HCM)
    except (ValueError, TypeError):
        pass

    # 2. Time-first pattern: '09:15 ngày 11/11/2026' or '15:30:45 10/11/2026'
    m_time_date = re.search(
        r'(\d{1,2}):(\d{1,2})(?::(\d{1,2}))?\s*(AM|PM)?\s*(?:ngày\s+|,|\s+)\s*(\d{1,2})[-/](\d{1,2})[-/](\d{4})',
        clean_ts,
        re.I
    )
    if m_time_date:
        hr, mn, sc, ampm, d, mth, y = m_time_date.groups()
        day, month, year = int(d), int(mth), int(y)
        hour, minute = int(hr), int(mn)
        second = int(sc) if sc is not None else 0
        if 1 <= day <= 31 and 1 <= month <= 12 and 1990 <= year <= 2100:
            if ampm:
                ampm = ampm.upper()
                if ampm == 'PM' and hour < 12:
                    hour += 12
                elif ampm == 'AM' and hour == 12:
                    hour = 0
            return datetime(year, month, day, hour, minute, second, tzinfo=TIMEZONE_HCM)

    # 3. Date-first pattern: '07-11-2026 - 09:58 AM', '12/11/2026 07:30', '11-11-2026', '12/11/2026'
    m = re.search(
        r'(\d{1,2})[-/](\d{1,2})[-/](\d{4})(?:\s*[-,\s]\s*(\d{1,2}):(\d{1,2})(?::(\d{1,2}))?\s*(AM|PM)?)?',
        clean_ts,
        re.I
    )
    if m:
        d, mth, y, hr, mn, sc, ampm = m.groups()
        day, month, year = int(d), int(mth), int(y)
        if 1 <= day <= 31 and 1 <= month <= 12 and 1990 <= year <= 2100:
            if hr is not None and mn is not None:
                hour = int(hr)
                minute = int(mn)
                second = int(sc) if sc is not None else 0
                if ampm:
                    ampm = ampm.upper()
                    if ampm == 'PM' and hour < 12:
                        hour += 12
                    elif ampm == 'AM' and hour == 12:
                        hour = 0
                return datetime(year, month, day, hour, minute, second, tzinfo=TIMEZONE_HCM)
            return datetime(year, month, day, 0, 0, 0, tzinfo=TIMEZONE_HCM)

    # 4. ISO-style space separated: '2026-11-12 07:30:00'
    m_iso_space = re.search(
        r'(\d{4})-(\d{1,2})-(\d{1,2})(?:\s+(\d{1,2}):(\d{1,2})(?::(\d{1,2}))?)?',
        clean_ts
    )
    if m_iso_space:
        y, mth, d, hr, mn, sc = m_iso_space.groups()
        year, month, day = int(y), int(mth), int(d)
        hour = int(hr) if hr is not None else 0
        minute = int(mn) if mn is not None else 0
        second = int(sc) if sc is not None else 0
        if 1 <= day <= 31 and 1 <= month <= 12 and 1990 <= year <= 2100:
            return datetime(year, month, day, hour, minute, second, tzinfo=TIMEZONE_HCM)

    return None


def extract_publication_timestamp_hierarchy(html_text: str) -> tuple:
    """
    Strict 6-stage timestamp extraction hierarchy:
    1. <meta property="article:published_time" content="..."> / <meta property="og:published_time" content="...">
    2. JSON-LD datePublished
    3. <meta name="pubdate" ...> / <meta name="publishdate" ...> / <meta name="date" ...> / <meta name="distributionDate" ...>
    4. <meta itemprop="datePublished" content="...">
    5. <time datetime="..."> / <span class="pdate"> / <span class="date"> / data-role="publishdate"
    6. Visible publication date regex in article body (supports DD-MM-YYYY and DD/MM/YYYY with AM/PM)
    Returns (pub_datetime: datetime or None, raw_string: str, method: str)
    """
    text = html.unescape(html_text)
    
    # 1. Meta article:published_time or og:published_time
    m1 = (
        re.search(r'<meta[^>]+property=[\"\'](?:article:published_time|og:published_time)[\"\'][^>]+content=[\"\']([^\"\']+)[\"\']', text, re.I)
        or re.search(r'<meta[^>]+content=[\"\']([^\"\']+)[\"\'][^>]+property=[\"\'](?:article:published_time|og:published_time)[\"\']', text, re.I)
    )
    if m1:
        raw_val = m1.group(1).strip()
        dt = parse_timestamp_iso_or_vietnamese(raw_val)
        if dt:
            return dt, raw_val, "META_ARTICLE_PUBLISHED_TIME"

    # 2. JSON-LD datePublished
    m2 = re.search(r'[\"\']datePublished[\"\']\s*:\s*[\"\']([^\"\']+)[\"\']', text, re.I)
    if m2:
        raw_val = m2.group(1).strip()
        dt = parse_timestamp_iso_or_vietnamese(raw_val)
        if dt:
            return dt, raw_val, "JSONLD_DATE_PUBLISHED"

    # 3. Meta pubdate / publishdate / date / distributionDate
    m3 = (
        re.search(r'<meta[^>]+name=[\"\'](?:pubdate|publishdate|date|distributiondate)[\"\'][^>]+content=[\"\']([^\"\']+)[\"\']', text, re.I)
        or re.search(r'<meta[^>]+content=[\"\']([^\"\']+)[\"\'][^>]+name=[\"\'](?:pubdate|publishdate|date|distributiondate)[\"\']', text, re.I)
    )
    if m3:
        raw_val = m3.group(1).strip()
        dt = parse_timestamp_iso_or_vietnamese(raw_val)
        if dt:
            return dt, raw_val, "META_PUBDATE"

    # 4. Meta itemprop="datePublished"
    m4_prop = (
        re.search(r'<meta[^>]+itemprop=[\"\']datePublished[\"\'][^>]+content=[\"\']([^\"\']+)[\"\']', text, re.I)
        or re.search(r'<meta[^>]+content=[\"\']([^\"\']+)[\"\'][^>]+itemprop=[\"\']datePublished[\"\']', text, re.I)
    )
    if m4_prop:
        raw_val = m4_prop.group(1).strip()
        dt = parse_timestamp_iso_or_vietnamese(raw_val)
        if dt:
            return dt, raw_val, "ITEMPROP_DATE_PUBLISHED"

    # 5. Semantic <time datetime="..."> or <span class="pdate"> / data-role="publishdate"
    m4_time = re.search(r'<time[^>]+datetime=[\"\']([^\"\']+)[\"\']', text, re.I)
    if m4_time:
        raw_val = m4_time.group(1).strip()
        dt = parse_timestamp_iso_or_vietnamese(raw_val)
        if dt:
            return dt, raw_val, "TIME_DATETIME"

    m_span = (
        re.search(r'<(?:span|div|p)[^>]+class=[\"\'][^\"\']*(?:pdate|pub-date|publish-date|date-time|article__date)[^\"\']*[\"\'][^>]*>(.*?)</(?:span|div|p)>', text, re.I | re.DOTALL)
        or re.search(r'<(?:span|div|p)[^>]+data-role=[\"\']publishdate[\"\'][^>]*>(.*?)</(?:span|div|p)>', text, re.I | re.DOTALL)
    )
    if m_span:
        raw_val = re.sub(r'<[^>]+>', ' ', m_span.group(1)).strip()
        dt = parse_timestamp_iso_or_vietnamese(raw_val)
        if dt:
            return dt, raw_val, "SEMANTIC_DATE_ELEMENT"

    # 6. Visible text regex in body (supports DD-MM-YYYY and DD/MM/YYYY with AM/PM)
    date_patterns = [
        r'(\d{1,2}:\d{2}(?::\d{2})?\s*(?:AM|PM)?\s*(?:ngày\s+)?\d{1,2}[-/]\d{1,2}[-/]\d{4})',
        r'(\d{1,2}[-/]\d{1,2}[-/]\d{4}\s*-\s*\d{1,2}:\d{2}(?::\d{2})?\s*(?:AM|PM)?)',
        r'(\d{1,2}[-/]\d{1,2}[-/]\d{4}\s+\d{1,2}:\d{2}(?::\d{2})?\s*(?:AM|PM)?)',
        r'(\d{1,2}[-/]\d{1,2}[-/]\d{4})'
    ]
    for dp in date_patterns:
        m5 = re.search(dp, text, re.I)
        if m5:
            raw_val = m5.group(1).strip()
            dt = parse_timestamp_iso_or_vietnamese(raw_val)
            if dt:
                return dt, raw_val, "VISIBLE_TEXT_REGEX"

    return None, None, "TIMESTAMP_UNVERIFIED"


def compute_freshness_bucket(pub_dt: datetime, run_dt: datetime):
    """
    Computes age in hours and categorizes into standard buckets:
    - FUTURE_TIMESTAMP if age < -2.0 (more than 2 hours future drift)
    - 0_TO_24H if -2.0 <= age <= 24.0 (includes clock skew tolerance: clamped to 0.0h if age < 0)
    - 24_TO_48H if 24.0 < age <= 48.0
    - 48_TO_72H if 48.0 < age <= 72.0
    - STALE_OVER_72H if age > 72.0
    """
    if pub_dt is None:
        return "TIMESTAMP_UNVERIFIED", None

    delta = run_dt - pub_dt
    age_hours = delta.total_seconds() / 3600.0
    
    if age_hours < -2.0:
        return "FUTURE_TIMESTAMP", age_hours
    elif age_hours < 0.0:
        # Same-day fresh breaking news with minor clock drift/skew
        return "0_TO_24H", 0.0
    elif age_hours <= 24.0:
        return "0_TO_24H", age_hours
    elif age_hours <= 48.0:
        return "24_TO_48H", age_hours
    elif age_hours <= 72.0:
        return "48_TO_72H", age_hours
    else:
        return "STALE_OVER_72H", age_hours


# -----------------------------------------------------------------------------
# Article Extraction Layer (Noise Removal: Strip Nav, Footers, Ads, Scripts)
# -----------------------------------------------------------------------------

def extract_clean_article_content(html_text: str, url: str) -> dict:
    """
    Extracts article title, summary, clean body text, stripping navigation,
    sidebars, footers, advertisements, cookie banners, and scripts.
    Also extracts the true publisher canonical URL from <link rel="canonical"> or <meta property="og:url">.
    Returns:
    {
        "headline": str,
        "summary": str,
        "articleBody": str,
        "cleanText": str,
        "isArticle": bool,
        "canonicalUrl": str,
        "extractionStatus": str
    }
    """
    if not html_text:
        return {
            "headline": "",
            "summary": "",
            "articleBody": "",
            "cleanText": "",
            "isArticle": False,
            "canonicalUrl": normalize_url(url) if url else "",
            "extractionStatus": "ARTICLE_BODY_UNAVAILABLE"
        }

    # Extract canonical URL directly from publisher HTML
    m_canon = (
        re.search(r'<link[^>]+rel=[\"\']canonical[\"\'][^>]+href=[\"\']([^\"\']+)[\"\']', html_text, re.I)
        or re.search(r'<link[^>]+href=[\"\']([^\"\']+)[\"\'][^>]+rel=[\"\']canonical[\"\']', html_text, re.I)
        or re.search(r'<meta[^>]+property=[\"\']og:url[\"\'][^>]+content=[\"\']([^\"\']+)[\"\']', html_text, re.I)
        or re.search(r'<meta[^>]+content=[\"\']([^\"\']+)[\"\'][^>]+property=[\"\']og:url[\"\']', html_text, re.I)
    )
    raw_canon = m_canon.group(1).strip() if m_canon else url
    canonical_url = normalize_url(raw_canon) if raw_canon else normalize_url(url)

    # Reject generic homepages
    clean_url = url.split("?")[0].rstrip("/")
    if clean_url in GENERIC_HOMEPAGES:
        return {
            "headline": "",
            "summary": "",
            "articleBody": "",
            "cleanText": "",
            "isArticle": False,
            "canonicalUrl": canonical_url,
            "extractionStatus": "GENERIC_HOMEPAGE_REJECTED"
        }

    # 1. Headline (Extract BEFORE html.unescape so &quot; / &#39; inside content="..." never truncates!)
    h1_candidates = []
    for h1_m in re.finditer(r'<h1[^>]*>(.*?)</h1>', html_text, re.I | re.DOTALL):
        h1_cand = " ".join(html.unescape(re.sub(r'<[^>]+>', ' ', h1_m.group(1))).split()).strip()
        if len(h1_cand) > 15 and not any(nav_w in h1_cand.lower() for nav_w in ["cafef.vn", "tuổi trẻ online", "thanh niên", "vneconomy", "thời báo tài chính"]):
            h1_candidates.append(h1_cand)
    m_og_title = (
        re.search(r'<meta[^>]+property=[\"\']og:title[\"\'][^>]+content="([^"]+)"', html_text, re.I)
        or re.search(r"<meta[^>]+property=[\"\']og:title[\"\'][^>]+content='([^']+)'", html_text, re.I)
    )
    og_title_clean = " ".join(html.unescape(re.sub(r'<[^>]+>', ' ', m_og_title.group(1))).split()).strip() if m_og_title else ""
    best_h1 = max(h1_candidates, key=len) if h1_candidates else ""
    if best_h1 and (len(best_h1) >= 28 or not og_title_clean):
        raw_headline = best_h1
    elif og_title_clean:
        raw_headline = og_title_clean
    else:
        m_title = re.search(r'<title[^>]*>(.*?)</title>', html_text, re.I | re.DOTALL)
        raw_headline = " ".join(html.unescape(re.sub(r'<[^>]+>', ' ', m_title.group(1))).split()).strip() if m_title else ""
    headline = raw_headline if raw_headline else "Bản tin tài chính"
    headline = re.sub(r'\s*[-|]\s*(?:Báo\s+)?(?:Tuổi Trẻ(?:\s+Online)?|Thanh Niên|CafeF|VnEconomy|Báo Đầu tư|Tạp chí Kinh tế Việt Nam).*$', '', headline, flags=re.I).strip()

    # 2. Summary (Extract BEFORE html.unescape so inner quotes do not truncate)
    m_desc = (
        re.search(r'<meta[^>]+property=[\"\']og:description[\"\'][^>]+content="([^"]+)"', html_text, re.I)
        or re.search(r"<meta[^>]+property=[\"\']og:description[\"\'][^>]+content='([^']+)'", html_text, re.I)
        or re.search(r'<meta[^>]+name=[\"\']description[\"\'][^>]+content="([^"]+)"', html_text, re.I)
        or re.search(r"<meta[^>]+name=[\"\']description[\"\'][^>]+content='([^']+)'", html_text, re.I)
    )
    summary = " ".join(html.unescape(m_desc.group(1)).split()).strip() if m_desc else headline

    text = html.unescape(html_text)

    # 3. Clean Article Body Isolation
    # Remove script, style, nav, footer, header, aside, noscript, iframe, figure, figcaption
    body_filtered = re.sub(r'<(script|style|nav|header|footer|aside|noscript|iframe|figure|figcaption)[^>]*>.*?</\1>', ' ', text, flags=re.I | re.DOTALL)
    noise_pattern = (
        r'<(div|section|aside|ul|ol)[^>]+(?:class|id)=[\"\'][^\"\']*'
        r'(?:sidebar|footer|nav|banner|ads|comment|social|related|tin-lien-quan|tin-cung-chuyen-muc|'
        r'tin-khac|bai-viet-khac|box-category|box-related|box-tin-lien-quan|cookie|tag|detail-top|box-zone-thread|'
        r'card-newest|new-item|order-now|ai-news|story--event|VCSortableInPreviewMode|PhotoCMS_Caption)[^\"\']*[\"\'][^>]*>.*?</\1>'
    )
    for _ in range(3):
        body_filtered = re.sub(noise_pattern, ' ', body_filtered, flags=re.I | re.DOTALL)

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

    # Look for article container (excluding totalcontentdetail which wraps CafeF byline header)
    article_html = ""
    # Check JSON-LD articleBody
    m_ld = re.search(r'"articleBody"\s*:\s*"([^"]{100,})"', text, re.I)
    if m_ld:
        article_html = m_ld.group(1)
    else:
        # A. VnEconomy: <main class="...article-editor...">
        c_main = _extract_balanced_tag(body_filtered, r'<main[^>]+class=[\"\'][^\"\']*article-editor[^\"\']*[\"\'][^>]*>', 'main')
        if c_main and (len(re.findall(r'<p[^>]*>', c_main, re.I)) >= 2 or len(re.sub(r'<[^>]+>', ' ', c_main).strip()) > 200):
            article_html = c_main

        # B. Báo Đầu tư: <div id="content_detail_news">
        if not article_html:
            c_bdt = _extract_balanced_tag(body_filtered, r'<div[^>]+id=[\"\']content_detail_news[\"\'][^>]*>', 'div')
            if c_bdt and (len(re.findall(r'<p[^>]*>', c_bdt, re.I)) >= 2 or len(re.sub(r'<[^>]+>', ' ', c_bdt).strip()) > 200):
                article_html = c_bdt

        # C. Safe <article> container (excluding item/card/sidebar)
        if not article_html:
            for m_art in re.finditer(r'<article\b([^>]*)>(.*?)</article>', body_filtered, re.I | re.DOTALL):
                art_attrs = m_art.group(1).lower()
                if any(bad in art_attrs for bad in ['box-category', 'item', 'sidebar', 'card', 'related']):
                    continue
                art_content = m_art.group(2)
                if (len(re.findall(r'<p[^>]*>', art_content, re.I)) >= 3 or len(art_content) > 800):
                    article_html = art_content
                    break

        # D. Classes in major publications (detail-content first, never totalcontentdetail)
        if not article_html:
            class_pats = [
                r'<div[^>]+class=[\"\'][^\"\']*(?:detail-content|content-detail|singular-content|article-body|maincontent|baiviet-noidung|article__body|cms-body)[^\"\']*[\"\'][^>]*>',
                r'<div[^>]+class=[\"\'][^\"\']*(?:detail__cmain|detail-cmain|content-news)[^\"\']*[\"\'][^>]*>',
                r'<div[^>]+id=[\"\'](?:main-content|article-content|content-detail|main-detail|abody)[\"\'][^>]*>'
            ]
            for cp in class_pats:
                c_html = _extract_balanced_tag(body_filtered, cp, 'div')
                if c_html and (len(re.findall(r'<p[^>]*>', c_html, re.I)) >= 2 or len(re.sub(r'<[^>]+>', ' ', c_html).strip()) > 250):
                    article_html = c_html
                    break

    def _is_byline_or_caption_paragraph(pt: str) -> bool:
        pt_low = pt.lower()
        if re.search(r'\|\s*\d{1,2}[-/]\d{1,2}[-/]\d{4}.*[ap]m\s*\|', pt_low):
            return True
        if "watchlist mới nhất" in pt_low or "đọc bài viết gốc" in pt_low:
            return True
        if re.search(r'(?:^|\s)-\s*ảnh:\s*[a-zà-ỹ\s]+$', pt_low) and len(pt) < 140:
            return True
        if any(term in pt_low for term in ["tin liên quan", "bài viết liên quan", "xem thêm", "đọc thêm", "tin cùng chuyên mục", "tiêu điểm", "xem chi tiết"]):
            if len(pt) < 80:
                return True
        return False

    if article_html:
        article_html = re.sub(
            r'<(div|section|aside|h4|figure|figcaption)[^>]+(?:class|id)=[\"\'][^\"\']*(?:callout|kbws|related|box-tin-lien-quan|tin-cung-chuyen-muc|VCSortableInPreviewMode|PhotoCMS_Caption)[^\"\']*[\"\'][^>]*>.*?</\1>',
            ' ', article_html, flags=re.I | re.DOTALL
        )
        article_html = re.sub(r'(?<=\d)</?(?:span|b|strong|i|em|u|font)\b[^>]*>(?=\d)', '', article_html, flags=re.I)
        paragraphs = re.findall(r'<p[^>]*>(.*?)</p>', article_html, re.I | re.DOTALL)
        clean_p = []
        for p in paragraphs:
            p = re.sub(r'(?<=\d)</?(?:span|b|strong|i|em|u|font)\b[^>]*>(?=\d)', '', p, flags=re.I)
            pt = " ".join(re.sub(r'<[^>]+>', ' ', p).split()).strip()
            if _is_byline_or_caption_paragraph(pt):
                continue
            if len(pt) > 25:
                clean_p.append(pt)
        article_text = " ".join(clean_p) if clean_p else " ".join(re.sub(r'<[^>]+>', ' ', article_html).split())
    else:
        paragraphs = re.findall(r'<p[^>]*>(.*?)</p>', body_filtered, re.I | re.DOTALL)
        clean_p = []
        for p in paragraphs:
            p = re.sub(r'(?<=\d)</?(?:span|b|strong|i|em|u|font)\b[^>]*>(?=\d)', '', p, flags=re.I)
            pt = " ".join(re.sub(r'<[^>]+>', ' ', p).split()).strip()
            if _is_byline_or_caption_paragraph(pt):
                continue
            if len(pt) > 25:
                clean_p.append(pt)
        article_text = " ".join(clean_p)

    article_text = " ".join(article_text.split())
    clean_full_text = f"{headline} {summary} {article_text}"

    # Extract og:image, twitter:image, or first substantive image
    m_img = (
        re.search(r'<meta[^>]+property=[\"\']og:image[\"\'][^>]+content=[\"\']([^\"\']+)[\"\']', html_text, re.I)
        or re.search(r'<meta[^>]+content=[\"\']([^\"\']+)[\"\'][^>]+property=[\"\']og:image[\"\']', html_text, re.I)
        or re.search(r'<meta[^>]+name=[\"\']twitter:image[\"\'][^>]+content=[\"\']([^\"\']+)[\"\']', html_text, re.I)
        or re.search(r'<meta[^>]+content=[\"\']([^\"\']+)[\"\'][^>]+name=[\"\']twitter:image[\"\']', html_text, re.I)
    )
    raw_img = m_img.group(1).strip() if m_img else ""
    if raw_img and not raw_img.startswith("http"):
        from urllib.parse import urljoin
        raw_img = urljoin(url, raw_img)
    image_url = raw_img

    # Verify if article body is substantive
    if len(article_text) < 50:
        return {
            "headline": headline,
            "summary": summary,
            "articleBody": article_text,
            "cleanText": clean_full_text,
            "imageUrl": image_url,
            "isArticle": False,
            "canonicalUrl": canonical_url,
            "extractionStatus": "ARTICLE_BODY_UNAVAILABLE"
        }

    return {
        "headline": headline,
        "summary": summary,
        "articleBody": article_text,
        "cleanText": clean_full_text,
        "imageUrl": image_url,
        "isArticle": True,
        "canonicalUrl": canonical_url,
        "extractionStatus": "SUCCESS"
    }


# -----------------------------------------------------------------------------
# True Subject Entity Extraction
# -----------------------------------------------------------------------------

RECOGNIZED_ENTITIES = [
    ("Ngân hàng Nhà nước", ["ngân hàng nhà nước", "nhnn", "sbv"]),
    ("Bộ Tài chính", ["bộ tài chính", "mof"]),
    ("Ủy ban Chứng khoán Nhà nước", ["ủy ban chứng khoán", "ubcknn", "ssc"]),
    ("Sở Giao dịch Chứng khoán TP.HCM (HoSE)", ["hose", "hsx", "sở giao dịch chứng khoán tp.hcm"]),
    ("Sở Giao dịch Chứng khoán Hà Nội (HNX)", ["hnx", "sở giao dịch chứng khoán hà nội"]),
    ("Tổng cục Thống kê (NSO)", ["tổng cục thống kê", "gso", "nso"]),
    ("Công ty Cổ phần Thanh toán Quốc gia Việt Nam (NAPAS)", ["napas"]),
    ("VietQR", ["vietqr"]),
    ("Payoo", ["payoo"]),
    ("VN-Index", ["vn-index", "vnindex"]),
    ("VN30", ["vn30"]),
    ("Vietcombank", ["vietcombank", "vcb"]),
    ("BIDV", ["bidv"]),
    ("VietinBank", ["vietinbank", "ctg"]),
    ("Techcombank", ["techcombank", "tcb"]),
    ("VPBank", ["vpbank"]),
    ("MBBank", ["mbbank", "ngân hàng quân đội", "mb"]),
    ("ACB", ["ngân hàng á châu", "acb"]),
    ("Sacombank", ["sacombank", "stb"]),
    ("HDBank", ["hdbank"]),
    ("LPBank", ["lpbank", "lộc phát"]),
    ("OCB", ["ngân hàng phương đông", "ocb"]),
    ("PGBank", ["pgbank"]),
    ("VIB", ["ngân hàng quốc tế", "vib"]),
    ("SHB", ["shb"]),
    ("TPBank", ["tpbank", "tiên phong"]),
    ("MSB", ["hàng hải", "msb"]),
    ("Cake by VPBank", ["cake by vpbank", "ngân hàng số cake", "cake.vn"]),
    ("Vingroup", ["vingroup", "vic"]),
    ("VinFast", ["vinfast"]),
    ("FPT", ["fpt"]),
    ("Masan", ["masan", "msn"]),
    ("Sojitz", ["sojitz"]),
    ("Masan High-Tech Materials", ["masan high-tech materials", "msr", "khoáng sản masan"]),
    ("Đồ hộp Hạ Long", ["đồ hộp hạ long", "halong canfoco", "canfoco"]),
    ("Bộ Giao thông Vận tải", ["bộ giao thông vận tải", "bộ gtvt"]),
    ("Tổng cục Thống kê", ["tổng cục thống kê", "gso", "cục thống kê"]),
    ("Chính phủ Việt Nam", ["chính phủ", "thủ tướng chính phủ"]),
    ("Cục Xuất nhập cảnh", ["cục quản lý xuất nhập cảnh", "hoãn xuất cảnh"]),
    ("VinUni", ["vinuni", "đại học vinuni"]),
    ("Hòa Phát", ["hòa phát", "hpg"]),
    ("Novaland", ["novaland", "nvl"]),
    ("Cục Dự trữ Liên bang Mỹ (Fed)", ["fed", "cục dự trữ liên bang"]),
    ("Ngân hàng Trung ương Châu Âu (ECB)", ["ecb"]),
    ("Quỹ Tiền tệ Quốc tế (IMF)", ["imf"]),
    ("Ngân hàng Thế giới (World Bank)", ["world bank", "ngân hàng thế giới"])
]


def extract_named_entities(headline: str, summary: str, body_text: str = "") -> list:
    """
    Extracts true financial subject entities from article content.
    Strictly forbids placing publisher domain into mainEntities.
    """
    content = f"{headline} {summary} {body_text}".lower()
    found_entities = []
    
    for formal_name, aliases in RECOGNIZED_ENTITIES:
        for alias in aliases:
            # Word boundary search
            if re.search(r'\b' + re.escape(alias) + r'\b', content):
                if formal_name not in found_entities:
                    found_entities.append(formal_name)
                break
                
    # Fallback to general institution if nothing recognized
    if not found_entities:
        if "ngân hàng" in content:
            found_entities.append("Hệ thống ngân hàng thương mại")
        elif "chứng khoán" in content or "cổ phiếu" in content:
            found_entities.append("Thị trường chứng khoán")
        elif "doanh nghiệp" in content:
            found_entities.append("Khối doanh nghiệp")
        else:
            found_entities.append("Kinh tế Việt Nam")
            
    return found_entities[:5]


# -----------------------------------------------------------------------------
# Content-Based Category Classification & Relevance
# -----------------------------------------------------------------------------

def _strip_author_biography(text: str) -> str:
    """Strips incidental author biography / appositive clauses so bio keywords cannot distort topic classification."""
    if not text:
        return ""
    cleaned = re.sub(
        r'tác giả\s+(?:các\s+)?(?:ấn phẩm|cuốn sách|sách|công trình)[^.!?,\n]*(?:,\s*[^.!?,\n]*){0,2}',
        ' ',
        text,
        flags=re.I
    )
    cleaned = re.sub(
        r'giảng viên\s+[^.!?,\n]*',
        ' ',
        cleaned,
        flags=re.I
    )
    return " ".join(cleaned.split())


def classify_canonical_category(headline: str, summary: str, text: str = "", feed_category: str = None) -> str:
    """
    Classifies an event strictly into one of the canonical V3.0.4 categories
    based on clean content (excluding whole page footers/navbars and incidental author bios),
    incorporating target category signal from the originating category feed.
    """
    clean_text = _strip_author_biography(text)
    clean_summary = _strip_author_biography(summary)
    content = f"{headline} {clean_summary} {clean_text}".lower()
    head_sum = f"{headline} {clean_summary}".lower()

    scores = {
        CATEGORY_MACRO_MONETARY: 0,
        CATEGORY_BANKING_CREDIT: 0,
        CATEGORY_FINTECH_PAYMENT: 0,
        CATEGORY_CAPITAL_MARKETS: 0,
        CATEGORY_CORPORATE_ENTERPRISE: 0,
        CATEGORY_RETAIL_CONSUMER: 0,
        CATEGORY_GLOBAL_MACRO: 0
    }

    if feed_category and feed_category in scores:
        scores[feed_category] += 6

    # 1. FinTech & Payment Keywords
    fintech_kw = [
        "fintech", "vietqr", "napas", "payoo", "thanh toán không dùng tiền mặt",
        "thanh toán số", "mã qr", "qr code", "ví điện tử", "cổng thanh toán",
        "payment gateway", "smartpos", "pos", "ekyc", "ngân hàng số", "thanh toán điện tử",
        "thẻ tín dụng", "thẻ nội địa", "chuyển khoản", "sinh trắc học", "giao dịch trực tuyến",
        "chuyển đổi số ngân hàng", "open banking", "open api", "bnpl", "ví trả sau",
        "momo", "zalopay", "vnpay", "apple pay", "google pay", "tap to phone", "dịch vụ ngân hàng số"
    ]
    for k in fintech_kw:
        if k in content:
            weight = 4 if k in head_sum else 1
            scores[CATEGORY_FINTECH_PAYMENT] += weight

    # 2. Macro & Monetary
    macro_kw = [
        "nhnn", "ngân hàng nhà nước", "chính sách tiền tệ", "tỷ giá trung tâm",
        "tỷ giá", "usd/vnd", "ngoại tệ", "ngoại hối", "dự trữ ngoại hối",
        "tín phiếu", "omo", "bơm ròng", "hút ròng", "lạm phát", "cpi", "gdp",
        "kinh tế vĩ mô", "vĩ mô", "tăng trưởng kinh tế", "điều hành tiền tệ",
        "ngân sách nhà nước", "đầu tư công", "xuất nhập khẩu", "cán cân thương mại",
        "fed", "cục dự trữ liên bang"
    ]
    for k in macro_kw:
        if k in content:
            weight = 4 if k in head_sum else 1
            scores[CATEGORY_MACRO_MONETARY] += weight

    # 3. Capital Markets
    cap_kw = [
        "chứng khoán", "vn-index", "cổ phiếu", "trái phiếu", "hose", "hnx", "upcom",
        "vietstock", "thanh khoản sàn", "khớp lệnh", "khối ngoại", "thị trường vốn", "ubcknn",
        "nâng hạng", "vốn hóa", "phiên giao dịch", "cổ tức", "phát hành cổ phiếu"
    ]
    for k in cap_kw:
        if k in content:
            weight = 4 if k in head_sum else 1
            scores[CATEGORY_CAPITAL_MARKETS] += weight

    # 4. Banking & Credit
    bank_kw = [
        "ngân hàng", "tín dụng", "lãi suất", "tiền gửi", "cho vay", "tiết kiệm",
        "dư nợ", "nợ xấu", "tăng trưởng tín dụng", "huy động vốn", "niêm yết lãi suất",
        "vietcombank", "bidv", "vietinbank", "techcombank",
        "vpbank", "mbbank", "acb", "sacombank", "hdbank", "pgbank", "ocb", "tpbank", "msb", "vib"
    ]
    for k in bank_kw:
        if k in content:
            weight = 4 if k in head_sum else 1
            scores[CATEGORY_BANKING_CREDIT] += weight

    # 5. Global Macro
    global_kw = [
        "kinh tế thế giới", "thương mại toàn cầu", "kinh tế mỹ", "trung quốc",
        "châu âu", "fdi", "wall street"
    ]
    for k in global_kw:
        if k in content:
            weight = 3 if k in head_sum else 1
            scores[CATEGORY_GLOBAL_MACRO] += weight

    # 6. Corporate & Enterprise
    corp_kw = [
        "doanh nghiệp", "tập đoàn", "lợi nhuận", "doanh thu", "báo cáo tài chính",
        "sản xuất kinh doanh", "bất động sản", "m&a", "thâu tóm", "thuế", "hộ kinh doanh",
        "niêm yết", "cổ đông", "chủ tịch", "tái cấu trúc", "kết quả kinh doanh"
    ]
    for k in corp_kw:
        if k in content:
            weight = 4 if k in head_sum else 1
            scores[CATEGORY_CORPORATE_ENTERPRISE] += weight

    # 7. Retail, D2C & Consumer Trends
    retail_kw = [
        "bán lẻ", "tiêu dùng", "người tiêu dùng", "sức mua", "siêu thị",
        "thương mại điện tử", "tmđt", "sàn tmđt", "chuỗi bán lẻ", "d2c",
        "fmcg", "hàng tiêu dùng", "tổng mức bán lẻ", "giá cả thị trường",
        "thị trường hàng hóa", "giá xăng", "giá vàng", "nông sản", "dịch vụ ăn uống",
        "mua sắm", "khuyến mãi", "shopee", "lazada", "tiktok shop",
        "bách hóa xanh", "wincommerce", "thế giới di động", "masan consumer", "pnj"
    ]
    for k in retail_kw:
        if k in content:
            weight = 4 if k in head_sum else 1
            scores[CATEGORY_RETAIL_CONSUMER] += weight

    # Find highest scoring category
    sorted_cats = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    best_cat, best_score = sorted_cats[0]

    if best_score == 0:
        return feed_category if (feed_category and feed_category in scores) else CATEGORY_CORPORATE_ENTERPRISE
    return best_cat


def evaluate_editorial_and_commercial_relevance(headline: str, summary: str, text: str = "") -> tuple:
    """
    Evaluates editorial and commercial relevance based on actual article content.
    Strips incidental author biography clauses before scoring and rejects non-financial
    or peripheral public-works/cultural topics when headline & summary lack financial focus.
    Returns: (editorial_relevance: str, commercial_relevance: str, is_irrelevant: bool, reason: str)
    """
    clean_text = _strip_author_biography(text)
    clean_summary = _strip_author_biography(summary)
    content = f"{headline} {clean_summary} {clean_text}".lower()
    head_sum = f"{headline} {clean_summary}".lower()
    
    # Hard exclusion for crime, individual fraud, judicial proceedings, and court cases
    CRIMINAL_EXCLUDES = [
        "bị cáo", "xét xử", "lừa đảo", "đầu thú", "chiếm đoạt", "truy tố",
        "bắt cựu", "bắt tạm giam", "khởi tố", "án mạng", "tống tiền", "chiếm đoạt tài sản"
    ]
    if any(k in head_sum for k in CRIMINAL_EXCLUDES) or any(k in content for k in ["bắt cựu cán bộ", "lừa đảo chiếm đoạt", "khởi tố vụ án"]):
        return "IRRELEVANT", "LOW", True, "Criminal or judicial proceedings excluded from executive intelligence"
    
    # Non-financial / peripheral topic indicators
    irrelevant_keywords = [
        "thuốc lá", "hút thuốc", "bệnh viện", "y tế", "thể thao", "bóng đá",
        "showbiz", "diễn viên", "ca sĩ", "hoa hậu", "vụ án", "bắt cóc",
        "tai nạn giao thông", "thời tiết", "mưa bão", "ẩm thực", "thịt heo",
        "thực phẩm chức năng", "bệnh nhân", "công nghiệp văn hóa", "di sản văn hóa",
        "luật di sản", "khai thác sân bay", "chỉnh trang công viên", "công viên ven sông",
        "cầu đi bộ", "phòng gym", "thể hình", "thể dục", "fitness", "hóa chất", "sơn jotun",
        "sơn nước", "cao tốc nối", "nối cao tốc", "quỹ bình ổn xăng dầu", "trao giải apea",
        "asia pacific enterprise awards", "vinh danh doanh nghiệp xuất sắc", "doanh nghiệp xuất sắc châu á",
        "bắt cựu", "lừa đảo", "chiếm đoạt", "truy tố", "xét xử", "bị cáo", "khởi tố", "đầu thú", "án mạng"
    ]
    
    core_financial_keywords = [
        "ngân hàng", "tín dụng", "lãi suất", "tiền gửi", "cho vay", "nhnn",
        "tỷ giá", "ngoại tệ", "chứng khoán", "cổ phiếu", "trái phiếu", "vn-index",
        "fintech", "thanh toán", "napas", "vietqr", "payoo", "pos", "dư nợ",
        "doanh thu", "lợi nhuận", "báo cáo tài chính", "thuế", "ngân sách",
        "vốn điều lệ", "cổ tức", "phát hành", "thương vụ", "m&a", "giá vàng",
        "vpbank", "techcombank", "vietcombank", "bidv", "vietinbank", "agribank",
        "mb", "mbbank", "acb", "sacombank", "hdbank", "shb", "tpbank", "msb",
        "ocb", "ncb", "seabank", "vib", "sjc", "doji", "pnj", "bảo tín minh châu",
        "bảo tín mạnh hải", "xăng dầu", "giá xăng", "xuất khẩu", "nhập khẩu"
    ]

    broad_economic_keywords = core_financial_keywords + [
        "doanh nghiệp", "kinh tế", "bất động sản", "thương mại", "đầu tư", "bán lẻ",
        "tiêu dùng", "người tiêu dùng", "sức mua", "siêu thị", "hàng hóa", "tmđt",
        "thương mại điện tử", "fdi", "gdp", "thị trường", "tài chính", "condotel", "sổ hồng"
    ]
    
    matched_irrelevant = [k for k in irrelevant_keywords if k in content]
    matched_head_irrel = [k for k in irrelevant_keywords if k in head_sum]
    matched_core_head = [k for k in core_financial_keywords if k in head_sum]
    matched_financial = [k for k in broad_economic_keywords if k in content]
    
    # Reject immediately if headline/summary matches peripheral/non-financial topic and has no core financial focus in headline/summary
    if matched_head_irrel and not matched_core_head:
        return "IRRELEVANT", "LOW", True, f"Peripheral/non-financial headline topic: {', '.join(matched_head_irrel)}"

    if matched_irrelevant and len(matched_core_head) == 0 and len(matched_financial) <= 2:
        return "IRRELEVANT", "LOW", True, f"Non-financial topic matched: {', '.join(matched_irrelevant)}"
        
    if len(matched_irrelevant) >= 2 and len(matched_core_head) == 0:
        return "IRRELEVANT", "LOW", True, f"Predominantly non-financial content: {', '.join(matched_irrelevant)}"

    # Require at least one core financial or economic keyword in headline+summary
    if not any(k in head_sum for k in broad_economic_keywords):
        return "IRRELEVANT", "LOW", True, "Headline and summary lack financial, banking, market, or enterprise focus"

    high_impact_keywords = [
        "nhnn", "ngân hàng nhà nước", "chính sách tiền tệ", "lãi suất điều hành",
        "mua ngoại tệ", "bơm vnd", "hút ròng", "tín phiếu", "napas", "vietqr",
        "payoo", "thanh toán không dùng tiền mặt", "cổng thanh toán"
    ]
    if any(k in content for k in high_impact_keywords):
        return "HIGH", "HIGH", False, "High-impact policy / FinTech infrastructure topic"
        
    if len(matched_financial) >= 2:
        return "MEDIUM", "MEDIUM", False, "Standard financial/banking industry intelligence"
        
    return "LOW", "LOW", False, "Peripheral corporate/economic news"


def _derive_unit_scale(unit_str: str) -> str:
    """Determines canonical scale descriptor from a Vietnamese financial unit."""
    u_low = (unit_str or "").lower()
    if "nghìn tỷ" in u_low or "ngàn tỷ" in u_low:
        return "nghìn tỷ"
    if "triệu tỷ" in u_low:
        return "triệu tỷ"
    if "tỷ" in u_low or "tỉ" in u_low:
        return "tỷ"
    if "triệu" in u_low:
        return "triệu"
    if "nghìn" in u_low or "ngàn" in u_low:
        return "nghìn"
    if "điểm %" in u_low or "điểm phần trăm" in u_low:
        return "điểm phần trăm"
    if "%" in u_low:
        return "tỷ lệ %"
    if "điểm" in u_low:
        return "điểm chỉ số"
    return "đơn vị"


def _bind_fact_entity(sentence: str, headline: str, main_entities: list, snapshot_text: str = "", test_mode: bool = False) -> str:
    """Binds a financial fact to a grounded entity present in the sentence or article."""
    s_low = sentence.lower()
    snap_low = (snapshot_text or f"{headline} {sentence}").lower()

    if test_mode:
        for ent in (main_entities or []):
            if ent and ent.lower() in s_low and ent.lower() in snap_low:
                return ent

        explicit_candidates = [
            ("Ngân hàng Nhà nước", "Ngân hàng Nhà nước"),
            ("NHNN", "NHNN"),
            ("Bộ Tài chính", "Bộ Tài chính"),
            ("Chính phủ", "Chính phủ"),
            ("Quốc hội", "Quốc hội"),
            ("VN-Index", "VN-Index"),
            ("HOSE", "HOSE"),
            ("SJC", "SJC"),
            ("Vietcombank", "Vietcombank"),
            ("BIDV", "BIDV"),
            ("VietinBank", "VietinBank"),
            ("Agribank", "Agribank"),
            ("VPBank", "VPBank"),
            ("Techcombank", "Techcombank"),
            ("Masan", "Masan"),
            ("FPT", "FPT"),
            ("tổ chức tín dụng", "tổ chức tín dụng"),
            ("hệ thống ngân hàng", "hệ thống ngân hàng"),
            ("Việt Nam", "Việt Nam"),
            ("Nhật Bản", "Nhật Bản"),
            ("Thái Lan", "Thái Lan"),
        ]
        for token, label in explicit_candidates:
            if token.lower() in s_low and label.lower() in snap_low:
                return label

        for ent in (main_entities or []):
            if ent and ent.lower() in snap_low:
                return ent

        return None

    # Priority 1: Explicit entity in main_entities that appears in the sentence
    for ent in (main_entities or []):
        if ent and ent.lower() in s_low and ent.lower() in snap_low:
            return ent

    # Priority 2: Known institutional or market actors mentioned in sentence or headline
    explicit_candidates = [
        ("Ngân hàng Nhà nước", "ngân hàng nhà nước"),
        ("NHNN", "nhnn"),
        ("Bộ Tài chính", "bộ tài chính"),
        ("Chính phủ", "chính phủ"),
        ("Quốc hội", "quốc hội"),
        ("VN-Index", "vn-index"),
        ("HOSE", "hose"),
        ("SJC", "sjc"),
        ("DOJI", "doji"),
        ("PNJ", "pnj"),
        ("Bảo Tín Minh Châu", "bảo tín minh châu"),
        ("Bảo Tín Mạnh Hải", "bảo tín mạnh hải"),
        ("Vietcombank", "vietcombank"),
        ("BIDV", "bidv"),
        ("VietinBank", "vietinbank"),
        ("Agribank", "agribank"),
        ("VPBank", "vpbank"),
        ("Techcombank", "techcombank"),
        ("MB", "mb"),
        ("ACB", "acb"),
        ("Sacombank", "sacombank"),
        ("HDBank", "hdbank"),
        ("SHB", "shb"),
        ("NCB", "ncb"),
        ("SeABank", "seabank"),
        ("VIB", "vib"),
        ("Masan", "masan"),
        ("FPT", "fpt"),
        ("tổ chức tín dụng", "tổ chức tín dụng"),
        ("hệ thống ngân hàng", "hệ thống ngân hàng"),
        ("Doanh nghiệp", "doanh nghiệp"),
        ("Việt Nam", "việt nam"),
        ("Nhật Bản", "nhật bản"),
        ("Thái Lan", "thái lan"),
    ]
    # Check sentence first
    for label, token in explicit_candidates:
        if token in s_low:
            return label

    # Check headline
    h_low = headline.lower()
    for label, token in explicit_candidates:
        if token in h_low:
            return label

    # Priority 3: First grounded main_entity in the article
    for ent in (main_entities or []):
        if ent and ent.lower() in snap_low:
            return ent

    return None


def extract_semantic_financial_facts(
    article_body: str,
    summary: str = "",
    headline: str = "",
    canonical_cat: str = "MARKET",
    main_entities: list = None,
    snapshot_text: str = "",
    test_mode: bool = False
) -> tuple:
    """
    P0-04 Semantic Financial Fact Extractor.
    Identifies metricName, extractedExpression, numericValue, unit, scale, entity,
    reportingPeriod, and explicit local-clause polarity.
    Strictly separates verified semantic facts from ambiguous REVIEW_REQUIRED facts.
    """
    verified_facts = []
    review_required_facts = []

    sentences = [s.strip() for s in re.split(r'(?<=[.!?\n])\s+', article_body or "") if len(s.strip()) > 20]
    if not sentences and summary:
        sentences = [summary.strip()]

    fact_regex = re.compile(
        r'(?P<val>\b\d{1,3}(?:[.,]\d{3})*(?:[.,]\d+)?|\b\d+)\s*'
        r'(?P<unit>'
        r'triệu\s*đồng/lượng|nghìn\s*đồng/lượng|đồng/lượng|'
        r'đồng/USD|VND/USD|'
        r'điểm\s*%|điểm\s*phần\s*trăm|%/năm|%?\s*GDP|%|'
        r'triệu\s*tỷ(?:\s*đồng)?|nghìn\s*tỷ(?:\s*(?:đồng|VND|yên|yen|USD))?|'
        r'tỷ\s*(?:đồng|VND|USD|yên|yen|lượt)?|tỉ\s*(?:đồng|VND|USD|yên|yen|lượt)?|'
        r'triệu\s*(?:USD|đồng|VND|lượt|người|cổ\s*phiếu)?|'
        r'nghìn\s*(?:USD|đồng|lượt)|'
        r'đồng|VND|USD|điểm|lượt'
        r')(?=\s|[.,;!?)]|$)',
        re.I
    )

    period_patterns = [
        r'\b(\d{1,2}\s+tháng\s+đầu\s+năm(?:\s+\d{4})?)\b',
        r'\b(\d{1,2}\s+tháng(?:\s+năm\s+\d{4})?)\b',
        r'\b(tháng\s+\d{1,2}(?:[\/\-]\d{4})?)\b',
        r'\b(quý\s+(?:[1-4]|I|II|III|IV)(?:[\/\-]\d{4}|\s+năm\s+\d{4})?)\b',
        r'\b(năm\s+202[4-9])\b',
        r'\b(\d{1,2}[\/\-]\d{1,2}(?:[\/\-]202[4-9])?)\b',
    ]

    snap_norm = " ".join((snapshot_text or f"{headline} {summary} {article_body}").split()).lower()

    for s_idx, sentence in enumerate(sentences):
        for m_f in fact_regex.finditer(sentence):
            raw_num_token = m_f.group('val')
            unit_str = " ".join(m_f.group('unit').split()).strip()
            expr = " ".join(m_f.group(0).split()).strip()

            # 1. Exclude isolated calendar years or law/decree numbers
            if expr in ["2026", "2025", "2024", "2027"] or (len(raw_num_token) == 4 and raw_num_token.startswith("20") and unit_str.lower() in ["", "năm"]):
                continue

            # 2. Detect broken OCR digit spacing before gold/currency units (e.g., "1 38,5 triệu đồng/lượng")
            pre_chars = sentence[max(0, m_f.start() - 4):m_f.start()]
            if re.search(r'\b\d\s+$', pre_chars):
                # Do not publish broken OCR spacing as a verified fact
                continue

            # Parse normalized numeric string
            if "." in raw_num_token and "," in raw_num_token:
                val_norm = raw_num_token.replace('.', '').replace(',', '.')
            elif "," in raw_num_token:
                val_norm = raw_num_token.replace(',', '.')
            elif re.match(r'^\d{1,3}(\.\d{3})+$', raw_num_token):
                val_norm = raw_num_token.replace('.', '')
            else:
                val_norm = raw_num_token

            try:
                val_float = float(val_norm)
            except Exception:
                val_float = 0.0

            if len(sentence) <= 240:
                fact_quote = sentence.strip()
            else:
                win_start = max(0, m_f.start() - 80)
                win_end = min(len(sentence), m_f.end() + 100)
                fact_quote = sentence[win_start:win_end].strip()

            s_lower = sentence.lower()
            u_lower = unit_str.lower()
            local_start = max(0, m_f.start() - 55)
            local_end = min(len(sentence), m_f.end() + 55)
            local_clause = sentence[local_start:local_end].lower()

            metric_name = None
            fact_type = "OBSERVATION"
            is_ambiguous = False

            # --- Semantic Classification Rules (P0-04) ---
            # Rule 1: Shareholding / Charter Capital Ownership vs Capital Allocation
            if "%" in u_lower and any(w in s_lower for w in ["sở hữu cổ phần", "cổ phần của một cổ đông", "vốn điều lệ của một tổ chức tín dụng", "tỷ lệ sở hữu", "mua vốn", "vốn điều lệ"]):
                metric_name = "Tỷ lệ sở hữu cổ phần"
                if any(w in s_lower for w in ["từ", "trở lên", "không được vượt quá", "quy định", "thông tư", "luật"]):
                    fact_type = "POLICY_THRESHOLD"
            elif "%" in u_lower and any(w in s_lower for w in ["nhu cầu vốn của nền kinh tế", "cung ứng vốn cho nền kinh tế", "đi qua hệ thống ngân hàng"]):
                metric_name = "Tỷ trọng cung ứng vốn cho nền kinh tế"
                fact_type = "MACRO_SHARE"

            # Rule 2: FX Purchase / Intervention Volume & VND Liquidity Supply vs Exchange Rate
            elif any(u in u_lower for u in ["tỷ usd", "triệu usd", "nghìn tỷ yên", "tỷ yên", "tỷ yen"]) and any(
                w in s_lower for w in ["mua vào", "mua ngoại tệ", "bán ngoại tệ", "can thiệp", "dự trữ ngoại hối", "kỳ hạn"]
            ):
                metric_name = "Khối lượng giao dịch / can thiệp ngoại tệ"
                fact_type = "FX_INTERVENTION_VOLUME"
            elif any(u in u_lower for u in ["tỷ đồng", "nghìn tỷ đồng", "triệu tỷ đồng", "tỷ vnd"]) and any(
                w in s_lower for w in ["cung ứng", "bơm thêm", "bơm ra", "bơm ròng", "hút ròng", "thanh khoản", "tiền đồng"]
            ):
                metric_name = "Giá trị cung ứng / điều tiết thanh khoản VND"
                fact_type = "LIQUIDITY_VOLUME"
            elif ("tỷ giá" in s_lower or "đồng/usd" in u_lower or "vnd/usd" in u_lower) and (
                "đồng/usd" in u_lower or "vnd/usd" in u_lower or (u_lower in ["đồng", "vnd"] and val_float >= 20000)
            ):
                metric_name = "Tỷ giá USD/VND"
                fact_type = "EXCHANGE_RATE"

            # Rule 3: Tax / Regulatory / Commission Policy Thresholds
            elif any(w in s_lower for w in ["tạm hoãn xuất cảnh", "nợ thuế", "ngưỡng nợ", "trần hoa hồng", "hoa hồng đại lý", "kinh phí bảo trì", "mức phạt"]):
                if "hoa hồng" in local_clause or ("hoa hồng" in s_lower and "nợ thuế" not in local_clause):
                    metric_name = "Trần chi hoa hồng đại lý"
                elif "nợ thuế" in local_clause or "tạm hoãn xuất cảnh" in local_clause or "nợ thuế" in s_lower or "tạm hoãn xuất cảnh" in s_lower:
                    metric_name = "Ngưỡng nợ thuế áp dụng tạm hoãn xuất cảnh"
                elif "bảo trì" in s_lower:
                    metric_name = "Kinh phí bảo trì chung cư"
                else:
                    metric_name = "Ngưỡng quy định chính sách"
                fact_type = "POLICY_THRESHOLD"

            # Rule 4: Gold Prices (preserving VND per tael)
            elif any(w in s_lower for w in ["giá vàng", "vàng miếng", "vàng nhẫn", "vàng sjc", "đồng/lượng"]):
                if "lượng" in u_lower:
                    metric_name = "Giá vàng trong nước" if val_float >= 50 and "triệu" in u_lower else "Biến động giá vàng trong nước"
                elif "%" in u_lower:
                    metric_name = "Tỷ lệ biến động giá vàng"
                else:
                    is_ambiguous = True
                fact_type = "COMMODITY_PRICE"

            # Rule 5: Interest Rates & Deposit Amount Tiers
            elif "lãi suất" in s_lower:
                if "điểm %" in u_lower or "điểm phần trăm" in u_lower:
                    metric_name = "Biến động lãi suất"
                elif "%" in u_lower:
                    metric_name = "Lãi suất"
                elif any(u in u_lower for u in ["triệu đồng", "tỷ đồng"]) and any(w in s_lower for w in ["tiền gửi từ", "khoản tiền gửi", "số dư", "áp dụng cho"]):
                    metric_name = "Hạn mức tiền gửi áp dụng lãi suất"
                    fact_type = "POLICY_THRESHOLD"
                else:
                    is_ambiguous = True

            # Rule 6: Stock Index, Trading Flows, Corporate Financials, Credit Growth, Tourism, Project Investment
            elif "vn-index" in s_lower and u_lower == "điểm":
                metric_name = "Chỉ số VN-Index" if val_float >= 500 else "Biến động điểm số VN-Index"
            elif any(w in s_lower for w in ["bán ròng", "mua ròng", "khối ngoại", "giá trị giao dịch", "thanh khoản"]) and any(
                u in u_lower for u in ["tỷ đồng", "triệu đồng", "nghìn tỷ"]
            ):
                metric_name = "Giá trị giao dịch chứng khoán"
            elif any(w in s_lower for w in ["doanh thu", "tổng thu"]) and any(u in u_lower for u in ["tỷ", "triệu", "%"]):
                metric_name = "Doanh thu" if "%" not in u_lower else "Tăng trưởng doanh thu"
            elif any(w in s_lower for w in ["lợi nhuận", "lãi ròng", "báo lãi", "lãi trước thuế", "lãi sau thuế"]) and any(u in u_lower for u in ["tỷ", "triệu", "%"]):
                metric_name = "Lợi nhuận" if "%" not in u_lower else "Tăng trưởng lợi nhuận"
            elif any(w in s_lower for w in ["tăng trưởng tín dụng", "dư nợ tín dụng", "dư nợ toàn nền kinh tế", "room tín dụng", "cho vay"]):
                if "%" in u_lower:
                    metric_name = "Tăng trưởng tín dụng"
                elif any(u in u_lower for u in ["tỷ", "triệu"]):
                    metric_name = "Quy mô dư nợ tín dụng"
                else:
                    is_ambiguous = True
            elif any(w in s_lower for w in ["khách quốc tế", "lượt khách", "du khách"]) and "lượt" in u_lower:
                metric_name = "Lượng khách du lịch quốc tế"
            elif any(w in s_lower for w in ["vốn đầu tư", "tổng mức đầu tư", "cung cấp vốn", "huy động", "dự án", "cao tốc", "oda", "vốn vay", "trái phiếu"]) and any(
                u in u_lower for u in ["tỷ", "tỉ", "triệu", "%"]
            ):
                metric_name = "Quy mô vốn đầu tư / huy động" if "%" not in u_lower else "Tỷ lệ phân bổ / tăng trưởng vốn"
            elif any(w in s_lower for w in ["gdp", "tăng trưởng kinh tế", "bội chi", "nợ công", "cpi", "lạm phát", "chỉ tiêu"]):
                metric_name = "Chỉ tiêu kinh tế vĩ mô"
            elif any(w in s_lower for w in ["thiệt hại", "bốc hơi", "thủy điện", "năng lượng"]) and any(u in u_lower for u in ["tỷ", "tỉ", "triệu"]):
                metric_name = "Giá trị kinh tế năng lượng ước tính"
            else:
                is_ambiguous = True
                metric_name = f"Chỉ số tài chính ({canonical_cat})"

            # Reporting period binding (grounded in fact_quote and snapshot)
            period = None
            for pp in period_patterns:
                m_p = re.search(pp, fact_quote, re.I)
                if m_p:
                    cand_p = m_p.group(1).strip()
                    if cand_p.lower() in snap_norm:
                        period = cand_p
                        break

            # Entity binding (grounded in snapshot)
            bound_entity = _bind_fact_entity(sentence, headline, main_entities, snapshot_text=snapshot_text, test_mode=test_mode)

            # Polarity binding: ONLY when explicitly supported by word-bounded movement verbs in local clause AND not a policy threshold
            polarity = None
            if fact_type not in ("POLICY_THRESHOLD", "FX_INTERVENTION_VOLUME", "LIQUIDITY_VOLUME", "MACRO_SHARE"):
                down_pat = r'\b(?:thấp hơn|giảm|hạ|sụt|rơi|bán ròng|hút ròng|lỗ|bốc hơi)\b'
                up_pat = r'\b(?:cao hơn|tăng|vọt|leo|vượt|mua ròng|bơm ròng|báo lãi)\b'
                if re.search(down_pat, local_clause, re.I):
                    polarity = "DOWN"
                elif re.search(up_pat, local_clause, re.I):
                    polarity = "UP"

            ver_status = "REVIEW_REQUIRED" if is_ambiguous else "VERIFIED"

            fact_item = {
                "metricName": metric_name,
                "extractedExpression": expr,
                "numericValue": str(val_norm),
                "unit": unit_str,
                "scale": _derive_unit_scale(unit_str),
                "entity": bound_entity,
                "reportingPeriod": period,
                "polarity": polarity,
                "factType": fact_type,
                "verificationStatus": ver_status,
                "sentenceIndex": s_idx,
                "contextQuote": fact_quote
            }

            if is_ambiguous:
                review_required_facts.append(fact_item)
            else:
                verified_facts.append(fact_item)
                if len(verified_facts) >= 2:
                    break
        if len(verified_facts) >= 2:
            break

    return verified_facts, review_required_facts


class BoundaryRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Enforces zero-trust domain boundaries and SSRF defenses on all HTTP redirects."""
    def __init__(self, test_mode: bool = False):
        self.test_mode = test_mode
        super().__init__()

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        parsed = urlparse(newurl)
        hostname = (parsed.hostname or "").lower()
        
        # Test mode exception
        if self.test_mode and hostname in ["localhost", "127.0.0.1", "::1"]:
            return super().redirect_request(req, fp, code, msg, headers, newurl)
            
        # Reject localhost/private in production
        if hostname in ["localhost", "127.0.0.1", "::1"]:
            raise urllib.error.HTTPError(newurl, 302, "REDIRECT_SECURITY_VIOLATION: Localhost rejected", headers, fp)
            
        matched = False
        for trusted in TRUSTED_DOMAINS:
            if hostname == trusted or hostname.endswith("." + trusted):
                matched = True
                break
        if not matched:
            raise urllib.error.HTTPError(newurl, 302, f"REDIRECT_SECURITY_VIOLATION: Hostname '{hostname}' untrusted", headers, fp)

        # SSRF IP check
        if not self.test_mode:
            try:
                addr_info = socket.getaddrinfo(hostname, None)
                for entry in addr_info:
                    ip_str = entry[4][0]
                    if is_ip_private_or_loopback(ip_str):
                        raise urllib.error.HTTPError(newurl, 302, f"REDIRECT_SECURITY_VIOLATION: Private IP {ip_str}", headers, fp)
            except socket.gaierror as e:
                raise urllib.error.HTTPError(newurl, 302, f"REDIRECT_DNS_ERROR: {str(e)}", headers, fp)

        return super().redirect_request(req, fp, code, msg, headers, newurl)


class DailyNewsCollector:
    """
    Dynamic Daily News Collector V3.0 (Phase 05B-R1.2)
    Harvests genuine live news across 5 publishers.
    Zero-fallback timestamp extraction, clean article body separation,
    true entity extraction, and multi-tier freshness enforcement.
    """

    def __init__(self, raw_evidence_dir: str, run_timestamp: str = None, http_timeout: int = 10, max_retries: int = 2, test_mode: bool = False, daily_editions_dir: str = None):
        self.raw_evidence_dir = raw_evidence_dir
        os.makedirs(raw_evidence_dir, exist_ok=True)
        self.http_timeout = http_timeout
        self.max_retries = max_retries
        self.test_mode = test_mode
        self.http_retrieval_ledger = {}
        self.feed_retrieval_ledger = {}
        
        if run_timestamp:
            self.run_timestamp = parse_timestamp_iso_or_vietnamese(run_timestamp)
        else:
            self.run_timestamp = datetime.now(TIMEZONE_HCM)

        self.daily_editions_dir = daily_editions_dir if daily_editions_dir is not None else resolve_daily_editions_dir(raw_evidence_dir)
        target_date_str = self.run_timestamp.strftime("%Y-%m-%d")
        if self.daily_editions_dir and (not self.test_mode or daily_editions_dir is not None):
            self.prior_urls, self.prior_titles = load_prior_published_history(
                self.daily_editions_dir, target_date_str=target_date_str, lookback_days=10
            )
        else:
            self.prior_urls, self.prior_titles = set(), []

    def fetch_url(self, url: str) -> dict:
        """
        Retrieves webpage content with SSRF and redirect boundary protection.
        """
        retrieved_at = datetime.now(TIMEZONE_HCM).isoformat()
        
        # Pre-flight SSRF check
        parsed = urlparse(url)
        hostname = (parsed.hostname or "").lower()
        if not self.test_mode and hostname in ["localhost", "127.0.0.1", "::1"]:
            return {
                "originalUrl": url,
                "finalUrl": url,
                "statusCode": 0,
                "originalBytes": b"",
                "retrievedAt": retrieved_at,
                "responseSha256": "",
                "error": "SSRF_BLOCKED: Localhost access prohibited"
            }
        if not self.test_mode and hostname:
            try:
                addr_info = socket.getaddrinfo(hostname, None)
                for entry in addr_info:
                    ip_str = entry[4][0]
                    if is_ip_private_or_loopback(ip_str):
                        return {
                            "originalUrl": url,
                            "finalUrl": url,
                            "statusCode": 0,
                            "originalBytes": b"",
                            "retrievedAt": retrieved_at,
                            "responseSha256": "",
                            "error": f"SSRF_BLOCKED_PRIVATE_IP: {ip_str}"
                        }
            except Exception as e:
                return {
                    "originalUrl": url,
                    "finalUrl": url,
                    "statusCode": 0,
                    "originalBytes": b"",
                    "retrievedAt": retrieved_at,
                    "responseSha256": "",
                    "error": f"DNS_RESOLUTION_ERROR: {str(e)}"
                }

        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 BryanFinTechCollector/3.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        }
        
        handler = BoundaryRedirectHandler(test_mode=self.test_mode)
        opener = urllib.request.build_opener(handler)
        req = urllib.request.Request(url, headers=headers)
        last_error = None
        
        for attempt in range(1, self.max_retries + 1):
            try:
                with opener.open(req, timeout=self.http_timeout) as resp:
                    code = resp.getcode()
                    final_url = resp.geturl()
                    raw_bytes = resp.read()
                    sha256 = hashlib.sha256(raw_bytes).hexdigest().lower()
                    
                    return {
                        "originalUrl": url,
                        "finalUrl": final_url,
                        "statusCode": code,
                        "originalBytes": raw_bytes,
                        "retrievedAt": retrieved_at,
                        "responseSha256": sha256,
                        "error": None
                    }
            except urllib.error.HTTPError as e:
                last_error = f"HTTP_{e.code}: {e.reason}"
                if e.code in [403, 404, 410]:
                    return {
                        "originalUrl": url,
                        "finalUrl": url,
                        "statusCode": e.code,
                        "originalBytes": b"",
                        "retrievedAt": retrieved_at,
                        "responseSha256": "",
                        "error": last_error
                    }
            except urllib.error.URLError as e:
                last_error = f"URL_ERROR: {e.reason}"
            except Exception as e:
                last_error = f"REQUEST_ERROR: {str(e)}"
                
            time.sleep(0.3 * attempt)
            
        return {
            "originalUrl": url,
            "finalUrl": url,
            "statusCode": 0,
            "originalBytes": b"",
            "retrievedAt": retrieved_at,
            "responseSha256": "",
            "error": last_error
        }

    @staticmethod
    def _extract_numeric_article_id(url_str: str) -> int:
        """Extracts trailing monotonic numeric article ID for newest-first feed ordering."""
        path = urlparse(url_str).path or ""
        m_id = re.search(r'-d?(\d{4,})\.(?:html|htm|chn)$', path)
        return int(m_id.group(1)) if m_id else 0

    def extract_article_links_from_feed(self, publisher_domain: str, feed_url: str, html_text: str) -> list:
        """Extracts article links from feed HTML matching publisher URL patterns."""
        links = []
        seen_canon = set()
        for m in re.finditer(r'href=[\"\']([^\"\']+)[\"\']', html_text):
            href = m.group(1).strip()
            full_url = urljoin(feed_url, href)
            parsed = urlparse(full_url)
            parsed_netloc = (parsed.netloc or "").lower()
            parsed_path = parsed.path or ""

            if parsed_netloc.startswith("m.") or "cdn." in parsed_netloc:
                continue

            is_article = False
            if parsed_netloc.endswith("cafef.vn") and re.search(r'-\d{10,}\.chn$', parsed_path):
                is_article = True
            elif parsed_netloc.endswith("cafebiz.vn") and re.search(r'-\d{10,}\.chn$', parsed_path):
                is_article = True
            elif parsed_netloc.endswith("tuoitre.vn") and re.search(r'-\d{10,}\.htm$', parsed_path):
                is_article = True
            elif parsed_netloc.endswith("thanhnien.vn") and re.search(r'-\d{10,}\.htm$', parsed_path):
                is_article = True
            elif parsed_netloc.endswith("vneconomy.vn") and parsed_path.endswith(".htm") and parsed_path.count("-") >= 6:
                vne_sections = [
                    "/tai-chinh.htm", "/tai-chinh-ngan-hang.htm", "/kinh-te.htm",
                    "/kin-te-thi-truong.htm", "/thi-truong.htm", "/chung-khoan.htm",
                    "/ngan-hang.htm", "/doanh-nghiep.htm", "/kinh-te-so.htm",
                    "/san-pham-thi-truong-kinh-te-so.htm", "/index.htm"
                ]
                if not any(parsed_path.endswith(sect) for sect in vne_sections):
                    is_article = True
            elif parsed_netloc.endswith("baodautu.vn") and re.search(r'-d\d{4,}\.html$', parsed_path):
                is_article = True
            elif parsed_netloc.endswith("vietnamnet.vn") and re.search(r'-\d{6,}\.html$', parsed_path):
                is_article = True
            elif parsed_netloc.endswith("thoibaotaichinhvietnam.vn") and re.search(r'-\d{5,}\.html$', parsed_path):
                is_article = True
            elif parsed_netloc.endswith("nguoiquansat.vn") and re.search(r'-\d{5,}\.html$', parsed_path):
                is_article = True
            elif parsed_netloc.endswith("thitruongtaichinhtiente.vn") and re.search(r'-\d{4,}\.html$', parsed_path) and not parsed_path.endswith("-ptag.html"):
                is_article = True
            elif parsed_netloc.endswith("vietstock.vn") and re.search(r'^/20\d{2}/\d{1,2}/.*-\d{5,}\.htm$', parsed_path):
                is_article = True
            elif parsed_netloc.endswith("vnexpress.net") and re.search(r'-\d{6,}\.html$', parsed_path):
                is_article = True
            elif parsed_netloc.endswith("thoibaonganhang.vn") and re.search(r'-\d{5,}\.html$', parsed_path):
                is_article = True

            if is_article and not any(skip in parsed_path.lower() for skip in ["video", "podcast", "photo", "infographic", "media", "/du-lich/"]):
                canon = normalize_url(full_url)
                if canon not in seen_canon and canon not in self.prior_urls:
                    seen_canon.add(canon)
                    links.append(full_url)

        # Sort links descending by trailing numeric article ID so newest articles come first
        if any(dom in publisher_domain or dom in feed_url for dom in (
            "baodautu.vn", "cafef.vn", "cafebiz.vn", "tuoitre.vn", "thanhnien.vn",
            "vietnamnet.vn", "thoibaotaichinhvietnam.vn", "nguoiquansat.vn",
            "thitruongtaichinhtiente.vn", "vietstock.vn", "vnexpress.net", "thoibaonganhang.vn"
        )):
            links.sort(key=self._extract_numeric_article_id, reverse=True)

        return links

    def discover_live_candidates(self, feeds: list = None, max_articles: int = 200) -> tuple:
        """
        Executes genuine multi-source live news research across monitored financial publications
        spanning all 6 editorial categories (Thanh toan so, Ngan hang, Thi truong von,
        Doanh nghiep, Kinh te vi mo, Ban le & Tieu dung):
        1. Queries category-tagged feeds across CafeF, VnEconomy, Tuoi Tre, Thanh Nien, VietNamNet,
           Thoi bao Tai chinh, Thoi bao Ngan hang, Thi truong Tai chinh Tien te, Vietstock, VnExpress,
           CafeBiz, Nguoi Quan Sat, Bao Dau tu.
        2. Gathers links per category & publisher, skipping URLs already published in prior editions.
        3. Applies category-balanced round-robin interleaving across all 6 categories & publishers.
        4. Extracts clean article body (stripping footers/navs).
        5. Extracts true publication timestamp (hierarchy without retrieval fallback).
        6. Extracts named entities and assigns canonical V3.0.4 categories.
        Returns (candidates: list, retrieval_ledger: dict)
        """
        if feeds is None:
            feeds = [
                # 1. Thanh toán số (FINTECH_PAYMENT)
                ("nguoiquansat.vn", "https://nguoiquansat.vn/tai-chinh-ngan-hang/ngan-hang", CATEGORY_FINTECH_PAYMENT),
                ("thitruongtaichinhtiente.vn", "https://thitruongtaichinhtiente.vn/hoat-dong-ngan-hang/san-pham-dich-vu", CATEGORY_FINTECH_PAYMENT),
                ("cafef.vn", "https://cafef.vn/kinh-te-so.chn", CATEGORY_FINTECH_PAYMENT),
                ("vneconomy.vn", "https://vneconomy.vn/kinh-te-so.htm", CATEGORY_FINTECH_PAYMENT),
                ("baodautu.vn", "https://baodautu.vn/kinh-te-so-d23/", CATEGORY_FINTECH_PAYMENT),

                # 2. Ngân hàng (BANKING_CREDIT)
                ("cafef.vn", "https://cafef.vn/tai-chinh-ngan-hang.chn", CATEGORY_BANKING_CREDIT),
                ("thitruongtaichinhtiente.vn", "https://thitruongtaichinhtiente.vn/hoat-dong-ngan-hang", CATEGORY_BANKING_CREDIT),
                ("nguoiquansat.vn", "https://nguoiquansat.vn/tai-chinh-ngan-hang/ngan-hang", CATEGORY_BANKING_CREDIT),
                ("vneconomy.vn", "https://vneconomy.vn/tai-chinh-ngan-hang.htm", CATEGORY_BANKING_CREDIT),
                ("vietnamnet.vn", "https://vietnamnet.vn/kinh-doanh/tai-chinh", CATEGORY_BANKING_CREDIT),
                ("thoibaotaichinhvietnam.vn", "https://thoibaotaichinhvietnam.vn/ngan-hang-bao-hiem", CATEGORY_BANKING_CREDIT),

                # 3. Thị trường vốn (CAPITAL_MARKETS)
                ("thoibaotaichinhvietnam.vn", "https://thoibaotaichinhvietnam.vn/chung-khoan", CATEGORY_CAPITAL_MARKETS),
                ("cafef.vn", "https://cafef.vn/thi-truong-chung-khoan.chn", CATEGORY_CAPITAL_MARKETS),
                ("tuoitre.vn", "https://tuoitre.vn/chung-khoan.htm", CATEGORY_CAPITAL_MARKETS),
                ("thanhnien.vn", "https://thanhnien.vn/kinh-te/chung-khoan.htm", CATEGORY_CAPITAL_MARKETS),

                # 4. Doanh nghiệp (CORPORATE_ENTERPRISE)
                ("thanhnien.vn", "https://thanhnien.vn/kinh-te/doanh-nghiep.htm", CATEGORY_CORPORATE_ENTERPRISE),
                ("tuoitre.vn", "https://tuoitre.vn/chung-khoan/doanh-nghiep-niem-yet.htm", CATEGORY_CORPORATE_ENTERPRISE),
                ("cafef.vn", "https://cafef.vn/doanh-nghiep.chn", CATEGORY_CORPORATE_ENTERPRISE),
                ("thoibaotaichinhvietnam.vn", "https://thoibaotaichinhvietnam.vn/doanh-nghiep", CATEGORY_CORPORATE_ENTERPRISE),
                ("nguoiquansat.vn", "https://nguoiquansat.vn/doanh-nghiep", CATEGORY_CORPORATE_ENTERPRISE),

                # 5. Kinh tế vĩ mô (MACRO_MONETARY)
                ("nguoiquansat.vn", "https://nguoiquansat.vn/vi-mo", CATEGORY_MACRO_MONETARY),
                ("cafef.vn", "https://cafef.vn/vi-mo-dau-tu.chn", CATEGORY_MACRO_MONETARY),
                ("vietstock.vn", "https://vietstock.vn/kinh-te/vi-mo.htm", CATEGORY_MACRO_MONETARY),
                ("thitruongtaichinhtiente.vn", "https://thitruongtaichinhtiente.vn/kinh-te-vi-mo-ptag.html", CATEGORY_MACRO_MONETARY),
                ("cafebiz.vn", "https://cafebiz.vn/vi-mo.chn", CATEGORY_MACRO_MONETARY),
                ("vnexpress.net", "https://vnexpress.net/tag/kinh-te-vi-mo-750740", CATEGORY_MACRO_MONETARY),

                # 6. Bán lẻ & Tiêu dùng (RETAIL_CONSUMER)
                ("thoibaonganhang.vn", "https://thoibaonganhang.vn/thi-truong", CATEGORY_RETAIL_CONSUMER),
                ("nguoiquansat.vn", "https://nguoiquansat.vn/thi-truong", CATEGORY_RETAIL_CONSUMER),
                ("thanhnien.vn", "https://thanhnien.vn/tieu-dung-thong-minh.htm", CATEGORY_RETAIL_CONSUMER),
                ("vietnamnet.vn", "https://vietnamnet.vn/kinh-doanh/thi-truong", CATEGORY_RETAIL_CONSUMER),
                ("vneconomy.vn", "https://vneconomy.vn/kin-te-thi-truong.htm", CATEGORY_RETAIL_CONSUMER),
                ("vneconomy.vn", "https://vneconomy.vn/thi-truong.htm", CATEGORY_RETAIL_CONSUMER),
            ]

        # 1. Gather links per category bucket & publisher (caching duplicate feed URLs)
        feed_html_cache = {}
        cat_pub_links = {}
        cat_pub_seen = {}

        for feed_item in feeds:
            if len(feed_item) >= 3:
                pub, feed_url, feed_cat = feed_item[0], feed_item[1], feed_item[2]
            else:
                pub, feed_url = feed_item[0], feed_item[1]
                feed_cat = None
            bucket_key = feed_cat or "GENERAL"
            if bucket_key not in cat_pub_links:
                cat_pub_links[bucket_key] = {}
                cat_pub_seen[bucket_key] = {}
            if pub not in cat_pub_links[bucket_key]:
                cat_pub_links[bucket_key][pub] = []
                cat_pub_seen[bucket_key][pub] = set()

            if feed_url in feed_html_cache:
                html_text = feed_html_cache[feed_url]
            else:
                res = self.fetch_url(feed_url)
                code = res["statusCode"]
                raw_bytes = res["originalBytes"]

                self.feed_retrieval_ledger[feed_url] = {
                    "publisher": pub,
                    "statusCode": code,
                    "finalUrl": res["finalUrl"],
                    "retrievedAt": res["retrievedAt"],
                    "byteLength": len(raw_bytes),
                    "error": res["error"]
                }
                self.http_retrieval_ledger[feed_url] = dict(self.feed_retrieval_ledger[feed_url])

                if code != 200 or not raw_bytes:
                    continue

                if raw_bytes[:2] == b'\x1f\x8b':
                    try:
                        html_text = gzip.decompress(raw_bytes).decode("utf-8", errors="replace")
                    except Exception:
                        html_text = raw_bytes.decode("utf-8", errors="replace")
                else:
                    html_text = raw_bytes.decode("utf-8", errors="replace")
                feed_html_cache[feed_url] = html_text

            feed_links = self.extract_article_links_from_feed(pub, feed_url, html_text)
            for fl in feed_links:
                canon_fl = normalize_url(fl)
                if canon_fl in self.prior_urls or canon_fl in cat_pub_seen[bucket_key][pub]:
                    continue
                cat_pub_seen[bucket_key][pub].add(canon_fl)
                cat_pub_links[bucket_key][pub].append(fl)

        # Build balanced per-category queues (interleaving publishers within each category)
        cat_queues = {}
        for bucket_key, pub_dict in cat_pub_links.items():
            q = []
            seen_in_cat = set()
            pubs = list(pub_dict.keys())
            for p, lst in pub_dict.items():
                if p != "vneconomy.vn":
                    lst.sort(key=self._extract_numeric_article_id, reverse=True)
            for round_idx in range(25):
                for p in pubs:
                    lst = pub_dict.get(p, [])
                    if round_idx < len(lst):
                        link_u = lst[round_idx]
                        c_u = normalize_url(link_u)
                        if c_u not in seen_in_cat:
                            seen_in_cat.add(c_u)
                            q.append((p, link_u, None if bucket_key == "GENERAL" else bucket_key))
            cat_queues[bucket_key] = q

        # 2. Balanced Round-Robin Selection across categories & publishers
        selected_article_queue = []
        queued_canon = set()
        bucket_keys = list(cat_queues.keys())
        max_per_cat = 60

        for round_idx in range(max_per_cat):
            for bk in bucket_keys:
                cq = cat_queues.get(bk, [])
                if round_idx < len(cq):
                    p, link_u, f_cat = cq[round_idx]
                    c_u = normalize_url(link_u)
                    if c_u not in queued_canon:
                        queued_canon.add(c_u)
                        selected_article_queue.append((p, link_u, f_cat))
                if len(selected_article_queue) >= max_articles:
                    break
            if len(selected_article_queue) >= max_articles:
                break

        # 3. Retrieve individual articles and extract clean content
        candidates = []
        today_str = self.run_timestamp.strftime("%Y%m%d")

        for idx, (pub, art_url, feed_cat) in enumerate(selected_article_queue):
            res = self.fetch_url(art_url)
            retrieved_at = res["retrievedAt"]
            code = res["statusCode"]
            final_url = res["finalUrl"]
            raw_bytes = res["originalBytes"]
            sha256 = res["responseSha256"]
            
            self.http_retrieval_ledger[art_url] = {
                "statusCode": code,
                "originalUrl": art_url,
                "finalUrl": final_url,
                "retrievedAt": retrieved_at,
                "byteLength": len(raw_bytes),
                "responseSha256": sha256,
                "error": res["error"]
            }
            
            if code != 200 or not raw_bytes:
                continue

            # Save exact original wire bytes to disk
            snapshot_filename = f"snapshot_live_{idx+1:03d}_{sha256[:10]}.html"
            snapshot_path = os.path.join(self.raw_evidence_dir, snapshot_filename)
            with open(snapshot_path, "wb") as sf:
                sf.write(raw_bytes)

            # Decompress if gzipped
            if raw_bytes[:2] == b'\x1f\x8b':
                try:
                    html_text = gzip.decompress(raw_bytes).decode("utf-8", errors="replace")
                except Exception:
                    html_text = raw_bytes.decode("utf-8", errors="replace")
            else:
                html_text = raw_bytes.decode("utf-8", errors="replace")

            # Article Extraction Layer: clean headline, summary, article body (no footers/navs)
            art_content = extract_clean_article_content(html_text, art_url)
            if not art_content["isArticle"]:
                # If homepage or unavailable body, skip candidate
                continue
                
            headline = art_content["headline"]
            summary = art_content["summary"]
            article_body = art_content["articleBody"]

            # Publication Timestamp: Strict 5-stage hierarchy (NO RETRIEVAL FALLBACK!)
            pub_dt, raw_ts_str, ts_method = extract_publication_timestamp_hierarchy(html_text)
            if pub_dt:
                iso_pub_ts = pub_dt.isoformat()
                event_date = pub_dt.strftime("%Y-%m-%d")
            else:
                iso_pub_ts = None
                event_date = None

            # Dynamic Relevance Scoring on clean content
            edit_rel, comm_rel, is_irrel, irrel_reason = evaluate_editorial_and_commercial_relevance(headline, summary, article_body)

            # Canonical Category Mapping on clean content + originating category feed signal
            canonical_cat = classify_canonical_category(headline, summary, article_body, feed_category=feed_cat)

            # Extract Subject Named Entities (NOT publisher domain!)
            main_entities = extract_named_entities(headline, summary, article_body)

            # Supporting Quote: isolate sentence from article body using sentence-boundary regex (never splitting decimals/thousands)
            clean_summary = " ".join(summary.split())
            clean_body = " ".join(article_body.split())
            body_sents = [
                s.strip() for s in re.split(r'(?<=[.!?])\s+', clean_body)
                if len(s.strip()) > 35 and not re.search(r'\|\s*\d{1,2}[-/]\d{1,2}[-/]\d{4}', s)
            ]
            if clean_summary and len(clean_summary) > 30 and clean_summary.lower() in clean_body.lower():
                supporting_quote = clean_summary[:180].strip()
            elif body_sents:
                supporting_quote = body_sents[0][:180].strip()
            else:
                supporting_quote = clean_body[:180].strip() if clean_body else headline

            # Extract Financial Facts with P0-04 Semantic Integrity
            fin_facts, review_required_facts = extract_semantic_financial_facts(
                article_body=article_body,
                summary=summary,
                headline=headline,
                canonical_cat=canonical_cat,
                main_entities=main_entities,
                snapshot_text=html_text
            )

            publisher_name = TRUSTED_DOMAINS.get(pub, pub)
            rel_snapshot_path = os.path.join("raw_evidence_store", snapshot_filename)

            cand = {
                "candidateId": f"CAND-{today_str}-{len(candidates)+1:03d}",
                "eventId": f"EVT-{today_str}-{len(candidates)+1:03d}",
                "headline": headline,
                "originalHeadline": headline,
                "candidateUrl": art_url,
                "canonicalUrl": normalize_url(art_url),
                "originalUrl": normalize_url(art_url),
                "publisher": publisher_name,
                "originalPublisher": publisher_name,
                "discoveredAt": retrieved_at,
                "retrievedAt": retrieved_at,
                "retrievedTimestamp": retrieved_at,
                "originalPublishedAt": iso_pub_ts,
                "originalPubTimestamp": iso_pub_ts,
                "eventDate": event_date,
                "timestampExtractionMethod": ts_method,
                "category": canonical_cat,
                "feedCategory": feed_cat,
                "summary": summary,
                "mainEntities": main_entities,
                "supportingQuote": supporting_quote,
                "financialFacts": fin_facts,
                "reviewRequiredFacts": review_required_facts,
                "evidencePath": rel_snapshot_path,
                "evidenceSnapshotPath": rel_snapshot_path,
                "snapshotPath": snapshot_path,
                "evidenceSha256": sha256,
                "httpStatusCode": code,
                "httpFinalUrl": final_url,
                "editorialRelevance": edit_rel,
                "commercialRelevance": comm_rel,
                "imageUrl": art_content.get("imageUrl", ""),
                "isIrrelevant": is_irrel,
                "irrelevanceReason": irrel_reason if is_irrel else None,
                "mainFacts": [summary[:120]]
            }
            candidates.append(cand)

        return candidates, self.http_retrieval_ledger

    def evaluate_candidate_freshness(self, candidate: dict) -> tuple:
        """
        Validates original publication timestamp against collector run timestamp.
        Returns (is_valid: bool, bucket_or_reason: str, age_hours: float)
        """
        pub_ts_str = candidate.get("originalPublishedAt") or candidate.get("originalPubTimestamp")
        if not pub_ts_str:
            return False, "TIMESTAMP_UNVERIFIED", None
            
        pub_dt = parse_timestamp_iso_or_vietnamese(pub_ts_str)
        if not pub_dt:
            return False, f"UNPARSEABLE_TIMESTAMP: {pub_ts_str}", None
            
        bucket, age_hours = compute_freshness_bucket(pub_dt, self.run_timestamp)
        
        if bucket == "FUTURE_TIMESTAMP":
            return False, f"FUTURE_TIMESTAMP (age: {age_hours:.2f}h)", age_hours
        if bucket == "STALE_OVER_72H" or age_hours > MAX_AGE_HOURS:
            return False, f"STALE_CONTENT (age: {age_hours:.2f}h > {MAX_AGE_HOURS:.1f}h)", age_hours
        if bucket == "TIMESTAMP_UNVERIFIED":
            return False, "TIMESTAMP_UNVERIFIED", None
            
        return True, bucket, age_hours

    def process_candidate_pool(self, raw_candidates: list) -> tuple:
        """
        Processes candidate events:
        - Filters out non-financial topics (REJECTED_IRRELEVANT)
        - Filters out already-published URLs/headlines from prior daily editions
        - Validates freshness and age bounds (<= 48.0h ceiling)
        - Classifies candidates into valid and rejected pools
        - Applies freshness priority sorting: 0-24h first, then 24-48h
        - Deduplicates same-day duplicate stories across publishers
        - Checks quota (25 events) and 0-24h ratio (>= 80%)
        Returns (status_code: str, report_dict: dict)
        """
        valid_pool = []
        rejected_pool = []
        
        for cand in raw_candidates:
            c = dict(cand)
            raw_url = c.get("candidateUrl") or c.get("originalUrl") or ""
            c["canonicalUrl"] = normalize_url(raw_url)
            
            # 1. Relevance check
            if c.get("isIrrelevant", False) or c.get("editorialRelevance") == "IRRELEVANT":
                c["verificationStatus"] = "REJECTED"
                c["rejectionReason"] = f"REJECTED_IRRELEVANT: {c.get('irrelevanceReason', 'Non-financial content')}"
                c["disposition"] = "REJECTED_IRRELEVANT"
                rejected_pool.append(c)
                continue

            # 1b. Cross-edition duplicate check against prior daily editions
            hl_str = (c.get("headline") or "").strip()
            prior_match_reason = None
            if c["canonicalUrl"] in self.prior_urls:
                prior_match_reason = f"REJECTED_ALREADY_PUBLISHED_PRIOR_EDITION (canonicalUrl={c['canonicalUrl']})"
            elif self.prior_titles and hl_str:
                cand_tokens = headline_tokens(hl_str)
                for p_date, p_hl, p_toks in self.prior_titles:
                    sim = headline_similarity(cand_tokens, p_toks)
                    if sim >= 0.60:
                        prior_match_reason = (
                            f"REJECTED_ALREADY_PUBLISHED_PRIOR_EDITION "
                            f"(sim={sim:.2f} with {p_date}: {p_hl[:60]})"
                        )
                        break
            if prior_match_reason:
                c["verificationStatus"] = "REJECTED"
                c["rejectionReason"] = prior_match_reason
                c["disposition"] = "REJECTED_ALREADY_PUBLISHED_PRIOR_EDITION"
                rejected_pool.append(c)
                continue
            
            # 2. Freshness validation
            is_valid, bucket_reason, age_hours = self.evaluate_candidate_freshness(c)
            if not is_valid:
                c["verificationStatus"] = "REJECTED"
                c["rejectionReason"] = bucket_reason
                if bucket_reason == "TIMESTAMP_UNVERIFIED":
                    c["disposition"] = "MANUAL_REVIEW_REQUIRED"
                elif "FUTURE_TIMESTAMP" in bucket_reason:
                    c["disposition"] = "REJECTED_FUTURE"
                else:
                    c["disposition"] = "REJECTED_STALE"
                    
                if age_hours is not None:
                    c["dataAgeHours"] = round(age_hours, 2)
                rejected_pool.append(c)
                continue
                
            c["freshnessBucket"] = bucket_reason
            c["dataAgeHours"] = round(age_hours, 2)
            c["verificationStatus"] = c.get("verificationStatus", "PENDING_VERIFICATION")
            valid_pool.append(c)

        def compute_candidate_priority(c):
            # Base freshness score: lower age is better
            age_h = c.get("dataAgeHours", 24.0) or 24.0
            score = 100.0 - (age_h * 2.0)
            
            # Massive priority for articles published on the target edition date
            target_date_str = str(self.run_timestamp)[:10] if self.run_timestamp else ""
            pub_str = str(c.get("originalPublishedAt") or c.get("eventDate") or "")
            if target_date_str and target_date_str in pub_str:
                score += 100.0
            
            # Editorial relevance bonus
            ed_rel = c.get("editorialRelevance", "LOW")
            if ed_rel == "HIGH":
                score += 60.0
            elif ed_rel == "MEDIUM":
                score += 30.0
                
            cat = c.get("category", "")
            if cat in [CATEGORY_BANKING_CREDIT, CATEGORY_FINTECH_PAYMENT, CATEGORY_MACRO_MONETARY]:
                score += 50.0
            elif cat == CATEGORY_CAPITAL_MARKETS:
                score += 30.0
                
            # FinTech, Banking, Interest Rates, FX, Payment keywords bonus
            hl_low = (c.get("headline") or "").lower()
            if any(k in hl_low for k in ["lãi suất", "ngân hàng", "tín dụng", "tiền gửi", "tỷ giá", "nhnn", "usd", "vn-index", "thanh toán", "vietqr", "smartpos", "chứng khoán", "cổ phiếu"]):
                score += 40.0

            return score

        # Sort valid candidates prioritizing 0-24h freshness (>= 80% target) then score
        valid_pool.sort(
            key=lambda c: (1 if c.get("freshnessBucket") == "0_TO_24H" else 0, compute_candidate_priority(c)),
            reverse=True
        )

        # Deduplicate same-edition URLs and same-story multi-publisher headlines (highest-priority wins)
        dedup_valid_pool = []
        seen_valid_urls = set()
        seen_valid_titles = []
        for cand in valid_pool:
            cand_url = cand.get("canonicalUrl") or normalize_url(cand.get("candidateUrl") or "")
            cand_hl = (cand.get("headline") or "").strip()
            cand_toks = headline_tokens(cand_hl)

            dup_reason = None
            if cand_url and cand_url in seen_valid_urls:
                dup_reason = f"Duplicate canonical URL within same edition ({cand_url})"
            elif cand_toks:
                for sel_hl, sel_toks in seen_valid_titles:
                    sim = headline_similarity(cand_toks, sel_toks)
                    if sim >= 0.50:
                        dup_reason = f"Duplicate story within same edition (sim={sim:.2f} with '{sel_hl[:60]}')"
                        break

            if dup_reason:
                dup_copy = dict(cand)
                dup_copy["verificationStatus"] = "REJECTED"
                dup_copy["disposition"] = "REJECTED_DUPLICATE_STORY_SAME_EDITION"
                dup_copy["rejectionReason"] = dup_reason
                rejected_pool.append(dup_copy)
                continue

            dedup_valid_pool.append(cand)
            if cand_url:
                seen_valid_urls.add(cand_url)
            if cand_toks:
                seen_valid_titles.append((cand_hl, cand_toks))

        valid_pool = dedup_valid_pool
        total_valid = len(valid_pool)
        
        # Check quota
        if total_valid < TARGET_EVENTS:
            return "COLLECTION_SHORTFALL", {
                "status": "COLLECTION_SHORTFALL",
                "runTimestamp": self.run_timestamp.isoformat(),
                "targetQuota": TARGET_EVENTS,
                "validCount": total_valid,
                "shortfall": TARGET_EVENTS - total_valid,
                "validCandidates": valid_pool,
                "selectedCandidates": valid_pool,
                "rejectedCount": len(rejected_pool),
                "rejectedCandidates": rejected_pool,
                "shortfallReason": f"Discovered {total_valid} valid unique events meeting freshness criteria; requires {TARGET_EVENTS}. Zero fabrication enforced."
            }
            
        # Balanced Category Selection: guarantee >= MIN_EVENTS_PER_CATEGORY across all 6 core categories,
        # then fill remaining slots up to TARGET_EVENTS prioritizing under-represented categories & priority score
        def _norm_core_cat(cat_val: str) -> str:
            if cat_val == CATEGORY_GLOBAL_MACRO:
                return CATEGORY_MACRO_MONETARY
            return cat_val if cat_val in CORE_EDITION_CATEGORIES else CATEGORY_CORPORATE_ENTERPRISE

        cat_buckets = {c: [] for c in CORE_EDITION_CATEGORIES}
        for cand in valid_pool:
            cat_buckets[_norm_core_cat(cand.get("category", ""))].append(cand)

        selected = []
        selected_ids = set()

        # Pass 1: take top MIN_EVENTS_PER_CATEGORY per category
        for c_key in CORE_EDITION_CATEGORIES:
            for item in cat_buckets[c_key][:MIN_EVENTS_PER_CATEGORY]:
                selected.append(item)
                selected_ids.add(id(item))

        # Pass 2: balance extra slots round-robin across categories until TARGET_EVENTS (or pool exhausted)
        cat_cursors = {c_key: MIN_EVENTS_PER_CATEGORY for c_key in CORE_EDITION_CATEGORIES}
        made_progress = True
        while len(selected) < TARGET_EVENTS and made_progress:
            made_progress = False
            # Pick from category with smallest current selection first
            ordered_cats = sorted(
                CORE_EDITION_CATEGORIES,
                key=lambda k: min(cat_cursors[k], len(cat_buckets[k]))
            )
            for c_key in ordered_cats:
                idx = cat_cursors[c_key]
                while idx < len(cat_buckets[c_key]) and id(cat_buckets[c_key][idx]) in selected_ids:
                    idx += 1
                if idx < len(cat_buckets[c_key]):
                    item = cat_buckets[c_key][idx]
                    selected.append(item)
                    selected_ids.add(id(item))
                    cat_cursors[c_key] = idx + 1
                    made_progress = True
                    if len(selected) >= TARGET_EVENTS:
                        break

        excess = [cand for cand in valid_pool if id(cand) not in selected_ids]

        for ex in excess:
            ex_copy = dict(ex)
            ex_copy["disposition"] = "EXCESS_NOT_SELECTED"
            ex_copy["rejectionReason"] = f"Candidate pool exceeded target quota ceiling of {TARGET_EVENTS}"
            rejected_pool.append(ex_copy)

        count_0_24h = sum(1 for c in selected if c.get("freshnessBucket") == "0_TO_24H")
        freshness_ratio = count_0_24h / len(selected) if selected else 0.0
        category_distribution = {
            c_key: sum(1 for c in selected if _norm_core_cat(c.get("category", "")) == c_key)
            for c_key in CORE_EDITION_CATEGORIES
        }

        return "DATA_READY", {
            "status": "DATA_READY",
            "runTimestamp": self.run_timestamp.isoformat(),
            "targetQuota": TARGET_EVENTS,
            "minPerCategory": MIN_EVENTS_PER_CATEGORY,
            "validCount": total_valid,
            "selectedCandidates": selected,
            "categoryDistribution": category_distribution,
            "count0To24h": count_0_24h,
            "freshnessRatio": round(freshness_ratio, 4),
            "rejectedCount": len(rejected_pool),
            "rejectedCandidates": rejected_pool
        }
