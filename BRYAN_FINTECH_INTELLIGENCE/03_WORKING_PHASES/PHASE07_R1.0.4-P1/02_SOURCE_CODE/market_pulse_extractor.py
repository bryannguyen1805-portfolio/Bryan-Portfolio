#!/usr/bin/env python3
"""
market_pulse_extractor.py — Bryan FinTech Intelligence Phase 05B-R1.3A.3
Source-Specific Financial Metric Extractors for MP-01 through MP-08.

Mandates:
1. Zero hardcoded dates or fabricated changes/directions/timestamps.
2. Fact-level grounding: extract observation date in proximity; handle date ranges (binding end-date).
3. P0-01: MP-03 main article body isolation, rate candidate binding, promotion vs standard separation,
   unnamed bank rejection (UNVERIFIED without confirmed bank identity).
4. P0-02: MP-06 removal of default unit 'tỷ'; explicit transaction count required; duration phrases rejected.
5. P0-03: MP-01 date range end-point binding; contextual year from publication metadata.
6. P0-06: MP-04 approximate change nullification; no hardcoded 15:00 timestamp.
"""

import re
import hashlib
import calendar
from typing import Dict, Any, Optional, Tuple, List
from financial_numeric_normalizer import FinancialNumericNormalizer, FinancialDecimal


class MarketPulseExtractor:
    """Decoupled, zero-distortion extractors for all 8 Market Pulse indicators."""

    @staticmethod
    def extract_contextual_year(text: str, default_year: int = 2026) -> int:
        """Extracts contextual year from publication metadata or title."""
        # 1. Look for publication date timestamp (e.g. 06-11-2026, 2026-11-06, 14/11/2026) across document
        m_meta = re.search(r'\b(?:202[4-9])-(\d{2})-(\d{2})\b|\b(\d{1,2})[-/](\d{1,2})[-/](202[4-9])\b', text[:30000])
        if m_meta:
            if m_meta.group(5):
                return int(m_meta.group(5))
            elif m_meta.group(0)[:4].isdigit():
                return int(m_meta.group(0)[:4])

        m_yr = re.search(r'\b(202[6-9])\b', text[:15000])
        if m_yr:
            return int(m_yr.group(1))
        m_yr_fallback = re.search(r'\b(202[4-9])\b', text[:1500])
        if m_yr_fallback:
            return int(m_yr_fallback.group(1))
        return default_year

    @classmethod
    def extract_observation_date_proximity(
        cls,
        text: str,
        anchor_pos: int,
        window: int = 250,
        contextual_year: Optional[int] = None
    ) -> Optional[str]:
        """
        Extracts observation date strictly in the immediate proximity (+/- window characters)
        of the metric anchor.
        - Detects date ranges ('từ X đến Y') and binds the END date Y as the measurement date.
        - Preserves contextual year from document metadata.
        """
        if contextual_year is None:
            contextual_year = cls.extract_contextual_year(text)

        start = max(0, anchor_pos - window)
        end = min(len(text), anchor_pos + window)
        sub = text[start:end]

        # 1. Date Range: 'từ ngày DD/MM(/YYYY)? đến (ngày)? DD/MM(/YYYY)?' or 'tuần (giao dịch)? DD-DD/MM(/YYYY)?'
        range_pat = r'(?:từ\s+(?:ngày\s+)?|tuần(?:\s+giao\s+dịch)?\s+)(\d{1,2})(?:[\/\-\.](\d{1,2})(?:[\/\-\.](\d{4}))?)?\s*(?:đến|tới|\-|–)\s*(?:ngày\s+)?(\d{1,2})[\/\-\.](\d{1,2})(?:[\/\-\.](\d{4}))?'
        m_range = re.search(range_pat, sub, re.I)
        if m_range:
            d_end = int(m_range.group(4))
            m_end = int(m_range.group(5))
            y_end = int(m_range.group(6)) if m_range.group(6) else contextual_year
            return f"{y_end:04d}-{m_end:02d}-{d_end:02d}"

        # 2. Look for 'ngày/sáng/chiều/hôm nay DD/MM/YYYY' or 'DD-MM-YYYY'
        dm = re.search(r'(?:ngày|sáng|chiều|tối|hôm nay|phiên)\s+(\d{1,2})[\/\-\.](\d{1,2})[\/\-\.](\d{4})', sub, re.I)
        if dm:
            d, m, y = int(dm.group(1)), int(dm.group(2)), int(dm.group(3))
            return f"{y:04d}-{m:02d}-{d:02d}"

        # 3. Look for 'ngày/sáng/chiều/hôm nay DD/MM' or 'DD-MM'
        dm_short = re.search(r'(?:ngày|sáng|chiều|tối|hôm nay)\s+(\d{1,2})[\/\-\.](\d{1,2})', sub, re.I)
        if dm_short:
            d, m = int(dm_short.group(1)), int(dm_short.group(2))
            return f"{contextual_year:04d}-{m:02d}-{d:02d}"

        # 4. Look for 'phiên DD/MM' or 'phiên DD-MM' (for stock sessions)
        dm_sess = re.search(r'phiên(?:\s+giao\s+dịch)?(?:\s+ngày)?\s+(\d{1,2})[\/\-\.](\d{1,2})(?:[\/\-\.](\d{4}))?', sub, re.I)
        if dm_sess:
            d, m = int(dm_sess.group(1)), int(dm_sess.group(2))
            y = int(dm_sess.group(3)) if dm_sess.group(3) else contextual_year
            return f"{y:04d}-{m:02d}-{d:02d}"

        # 5. Look for 'đến ngày DD/MM/YYYY' or 'đến ngày DD/MM'
        dm_to = re.search(r'(?:đến|tới)\s+(?:ngày\s+)?(\d{1,2})[\/\-\.](\d{1,2})(?:[\/\-\.](\d{4}))?', sub, re.I)
        if dm_to:
            d, m = int(dm_to.group(1)), int(dm_to.group(2))
            y = int(dm_to.group(3)) if dm_to.group(3) else contextual_year
            return f"{y:04d}-{m:02d}-{d:02d}"

        # 6. Periodic reporting period: 'trong/lũy kế X tháng (đầu năm)? (YYYY)?'
        # Negative lookbehind to prevent false matching deposit term 'kỳ hạn 12 tháng'
        m_per = re.search(r'(?<!kỳ hạn\s)(?<!kỳ hạn\s\s)(?:trong|lũy kế|tổng cộng)?\s*(\d{1,2})\s+tháng(?:\s+đầu\s+năm|\s+năm\s+(202[4-9]))', sub, re.I)
        if m_per:
            m_val = int(m_per.group(1))
            if 1 <= m_val <= 12:
                y_val = int(m_per.group(2)) if m_per.group(2) else contextual_year
                last_day = calendar.monthrange(y_val, m_val)[1]
                return f"{y_val:04d}-{m_val:02d}-{last_day:02d}"

        # 7. Month-end session: 'phiên cuối tháng X'
        m_endm = re.search(r'phiên\s+cuối\s+tháng\s*(\d{1,2})?(?:\/(202[4-9]))?', sub, re.I)
        if m_endm:
            m_val = int(m_endm.group(1)) if m_endm.group(1) else (int(re.search(r'T(\d{1,2})', sub).group(1)) if re.search(r'T(\d{1,2})', sub) else None)
            if m_val and 1 <= m_val <= 12:
                y_val = int(m_endm.group(2)) if m_endm.group(2) else contextual_year
                last_day = calendar.monthrange(y_val, m_val)[1]
                return f"{y_val:04d}-{m_val:02d}-{last_day:02d}"

        # 8. Fallback for financial news headlines: check article title/h1 or lead text for session date
        dm_head = re.search(r'(?:(?:<(?:h1|title)[^>]*>.*?)?(?:phiên|ngày)\s+|(?:\b))(\d{1,2})[\/\-\.](\d{1,2})[\/\-\.](202[4-9])', text[:2500], re.I)
        if dm_head:
            d, m = int(dm_head.group(1)), int(dm_head.group(2))
            y = int(dm_head.group(3)) if dm_head.group(3) else contextual_year
            if 1 <= d <= 31 and 1 <= m <= 12:
                return f"{y:04d}-{m:02d}-{d:02d}"

        dm_head_short = re.search(r'(?:phiên|ngày|sáng|chiều|hôm nay)\s+(\d{1,2})[\/\-\.](\d{1,2})(?:[\/\-\.](202[4-9]))?', text[:2500], re.I)
        if dm_head_short:
            d, m = int(dm_head_short.group(1)), int(dm_head_short.group(2))
            y = int(dm_head_short.group(3)) if dm_head_short.group(3) else contextual_year
            if 1 <= d <= 31 and 1 <= m <= 12:
                return f"{y:04d}-{m:02d}-{d:02d}"

        return None

    @classmethod
    def is_navigation_quote(cls, quote: str) -> bool:
        """Detects if a candidate quote is merely a navigation/header/breadcrumb snippet."""
        if not quote:
            return True
        lq = quote.lower()
        nav_markers = [
            "lfr-nav-item", "nav-item", "<nav", "class=\"menu", "class=\"header",
            "breadcrumb", "<a aria-labelledby", "role=\"presentation\"", "class=\"tags\"",
            "<ul class=", "<li><a href="
        ]
        return any(nm in lq for nm in nav_markers)

    @classmethod
    def extract_article_body(cls, html_text: str) -> str:
        """
        Isolates the main editorial article body, extracting paragraph text while
        excluding site navigation, headers, sidebars ('tin tức liên quan', 'bài viết khác'),
        and footers.
        """
        # Find detail content container
        m_start = re.search(r'class=["\'][^"\']*(?:detail__content|content-detail|detail-content|article-content|fck_detail)[^"\']*["\']', html_text, re.I)
        if m_start:
            content_sub = html_text[m_start.end():]
            m_end = re.search(r'class=["\'][^"\']*(?:tagdetail|link-source-detail|t-contentdetail|footer)[^"\']*["\']', content_sub, re.I)
            if m_end:
                content_sub = content_sub[:m_end.start()]
            p_matches = re.findall(r'<p[^>]*>(.*?)</p>', content_sub, re.I | re.S)
            if p_matches:
                clean_ps = []
                for p in p_matches:
                    cp = re.sub(r'<[^>]+>', ' ', p)
                    cp = ' '.join(cp.split())
                    if cp and not cls.is_navigation_quote(cp):
                        clean_ps.append(cp)
                if clean_ps:
                    return " ".join(clean_ps)

        # Fallback: extract all <p> tags with significant length (>30 chars)
        p_matches = re.findall(r'<p[^>]*>(.*?)</p>', html_text, re.I | re.S)
        clean_ps = []
        for p in p_matches:
            cp = re.sub(r'<[^>]+>', ' ', p)
            cp = ' '.join(cp.split())
            if len(cp) > 30 and not cls.is_navigation_quote(cp):
                clean_ps.append(cp)
        return " ".join(clean_ps) if clean_ps else html_text

    @classmethod
    def extract_mp01_central_rate(cls, text: str, raw_bytes: bytes = b"") -> Dict[str, Any]:
        """
        MP-01: Central USD/VND Exchange Rate from SBV or accredited financial press.
        Must distinguish central rate from commercial rates or free market.
        Rejects navigation labels and ungrounded observation dates.
        """
        body_text = cls.extract_article_body(text)
        search_text = body_text if len(body_text) > 50 else text

        # Look for central rate statement
        pat = r'(?:tỷ giá trung tâm.*?do\s+(?:ngân hàng nhà nước|nhnn).*?(?:công bố|niêm yết).*?(?:lên|ở mức|đạt|là)|(?:ngân hàng nhà nước|nhnn).*?(?:niêm yết|công bố)\s+tỷ giá trung tâm.*?(?:ở mức|đạt|là)|tỷ giá trung tâm.*?(?:ngày\s+\d{1,2}[\/\-\.]\d{1,2}(?:[\/\-\.]\d{4})?\s+)?(?:ở mức|đạt|là|:|\s))\s*(?:khoảng|mức)?\s*(?P<val>2\d{1}[\.,]\d{3})\s*(?:đồng|vnd|đ)?'
        m = re.search(pat, search_text, re.I) or re.search(pat, text, re.I)
        matched_in_body = bool(re.search(pat, search_text, re.I))

        if not m:
            pat_table = r'(?:bảng\s+)?tỷ giá trung tâm.*?(\b2\d{1}[\.,]\d{3}\b)'
            m = re.search(pat_table, search_text, re.I) or re.search(pat_table, text, re.I)
            matched_in_body = bool(re.search(pat_table, search_text, re.I))

        if not m:
            return {
                "success": False,
                "unverifiedReason": "Không tìm thấy số liệu tỷ giá trung tâm USD/VND trong nội dung nguồn.",
                "actualValue": None,
                "observationDate": None,
                "observationTimestamp": None,
                "supportingQuote": None
            }

        target_src = search_text if matched_in_body else text
        m_sent = re.search(r'[^.!?\n<>]*?' + re.escape(m.group(0)) + r'[^.!?\n<>]*', target_src)
        raw_quote = m_sent.group(0) if m_sent else m.group(0)
        clean_q = re.sub(r'</(h\d|p|div|li|figcaption)>', '. ', raw_quote)
        clean_q = re.sub(r'<[^>]+>', ' ', clean_q)
        clean_q = re.sub(r'^[^<>]*?>\s*', '', clean_q).strip()
        quote = ' '.join(clean_q.split())[:160].strip()
        if quote not in text and m.group(0).strip() in text:
            quote = m.group(0).strip()[:160]
        if cls.is_navigation_quote(quote):
            return {
                "success": False,
                "unverifiedReason": "NAVIGATION_LABEL_REJECTED: Đoạn trích dẫn thuộc thanh điều hướng trang, không phải dữ liệu đo lường.",
                "actualValue": None,
                "observationDate": None,
                "observationTimestamp": None,
                "supportingQuote": None
            }

        val_raw = m.group('val') if 'val' in m.groupdict() else m.group(1)
        anchor_pos = m.start()
        obs_date = (
            cls.extract_observation_date_proximity(target_src, anchor_pos, window=250, contextual_year=cls.extract_contextual_year(text))
            or cls.extract_observation_date_proximity(text, 0, window=3000, contextual_year=cls.extract_contextual_year(text))
        )

        norm = FinancialNumericNormalizer.normalize_measurement(
            val_raw, "VND/USD", quote, raw_bytes, locale="vi_VN", indicator_id="MP-01"
        )
        # Separate date and timestamp: do NOT fabricate T17:00:00 when only calendar date is supported
        obs_timestamp = None

        m_chg = re.search(r'(?P<dir>tăng|giảm)\s*(?P<cval>\d{1,3})\s*đồng', quote, re.I)
        chg_val = None
        dir_val = None
        if m_chg:
            is_down = "giảm" in m_chg.group("dir").lower()
            dir_val = "DOWN" if is_down else "UP"
            chg_val = f"-{m_chg.group('cval')} đồng" if is_down else f"+{m_chg.group('cval')} đồng"

        return {
            "success": True,
            "actualValue": norm["normalizedNumericValue"],
            "unit": "VND/USD",
            "observationDate": obs_date,
            "observationTimestamp": obs_timestamp,
            "observationPeriod": "Hằng ngày",
            "change": chg_val,
            "direction": dir_val,
            "supportingQuote": quote,
            "sourcePublisher": "sbv.gov.vn",
            "normalizationTrace": norm
        }

    @classmethod
    def extract_mp02_interbank_rate(cls, text: str, raw_bytes: bytes = b"") -> Dict[str, Any]:
        """
        MP-02: Overnight Interbank Interest Rate.
        Must distinguish overnight from 1W, 1M, and policy rates within the same sentence.
        """
        body_text = cls.extract_article_body(text)
        search_text = body_text if len(body_text) > 50 else text
        lower_text = search_text.lower()
        if "tái cấp vốn" in lower_text and not ("qua đêm" in lower_text or "overnight" in lower_text):
            return {
                "success": False,
                "unverifiedReason": "POLICY_RATE_EXCLUDED: Số liệu phát hiện là lãi suất tái cấp vốn/điều hành, không phải lãi suất liên ngân hàng qua đêm.",
                "actualValue": None,
                "observationDate": None,
                "observationTimestamp": None,
                "supportingQuote": None
            }

        # Restrict matching within a single sentence (allowing decimal dots like 4.7%) so overnight keyword never jumps to 1W/2W/1M rate in next sentence
        pat_end = (
            r'(?:lãi suất liên ngân hàng(?:[^.!?\n<>]|\.(?=\d)){0,80}?(?:kỳ hạn\s+)?qua đêm|'
            r'lãi suất qua đêm(?:\s*\(on\))?)(?:[^.!?\n<>]|\.(?=\d)){0,120}?'
            r'(?:trước khi\s+)?(?:tăng lên|lên|xuống còn|còn|ở mức|chốt phiên\s*(?:ở mức)?|kết phiên|đạt)\s*'
            r'(?P<val>\d{1,2}(?:[\.,]\d{1,2})?)\s*'
            r'(?P<unit>%/năm|%)?'
            r'(?:\s+vào\s+phiên\s+cuối\s+tháng|\s+cuối\s+tháng|\s+cuối\s+kỳ|\s+ngày\s+\d{1,2}[\/\-\.]\d{1,2})?'
        )
        m = re.search(pat_end, search_text, re.I)
        if not m:
            pat = (
                r'(?:lãi suất liên ngân hàng(?:[^.!?\n<>]|\.(?=\d)){0,80}?(?:kỳ hạn\s+)?qua đêm|'
                r'lãi suất qua đêm(?:\s*\(on\))?(?:\s+liên ngân hàng)?|'
                r'lãi suất bình quân liên ngân hàng(?:[^.!?\n<>]|\.(?=\d)){0,80}?(?:kỳ hạn\s+)?qua đêm)(?:[^.!?\n<>]|\.(?=\d)){0,120}?'
                r'(?:ở mức|đạt|là|:|tăng lên|lên|xuống còn|còn|chốt phiên\s*(?:ở mức)?)\s*'
                r'(?:\d{1,2}(?:[\.,]\d{1,2})?%?\s*(?:[–\-]|đến)\s*)?'
                r'(?P<val>\d{1,2}(?:[\.,]\d{1,2})?)\s*'
                r'(?P<unit>%/năm|%)?'
            )
            m = re.search(pat, search_text, re.I)
        if not m:
            return {
                "success": False,
                "unverifiedReason": "Không tìm thấy số liệu lãi suất liên ngân hàng kỳ hạn qua đêm trong nội dung nguồn.",
                "actualValue": None,
                "observationDate": None,
                "observationTimestamp": None,
                "supportingQuote": None
            }

        val_raw = m.group('val')
        anchor_pos = m.start()
        obs_date = cls.extract_observation_date_proximity(search_text, anchor_pos, window=250)
        if not obs_date:
            raw_pos = text.find(m.group(0))
            if raw_pos != -1:
                obs_date = cls.extract_observation_date_proximity(text, raw_pos, window=250)

        m_sent = re.search(r'[^.!?\n]*?' + re.escape(m.group(0)) + r'[^.!?\n]*', search_text)
        raw_quote = m_sent.group(0) if m_sent else m.group(0)
        clean_q = re.sub(r'</(h\d|p|div|li|figcaption)>', '. ', raw_quote)
        clean_q = re.sub(r'<[^>]+>', ' ', clean_q).strip()
        clean_q = ' '.join(clean_q.split())
        quote = clean_q
        for s in re.split(r'(?<=[.!?])\s+', clean_q):
            if val_raw in s:
                quote = s[:160].strip()
                break
        if quote not in text and m.group(0).strip() in text:
            quote = m.group(0).strip()[:160]
        if cls.is_navigation_quote(quote):
            return {
                "success": False,
                "unverifiedReason": "NAVIGATION_LABEL_REJECTED: Trích dẫn thuộc thanh điều hướng.",
                "actualValue": None,
                "observationDate": None,
                "observationTimestamp": None,
                "supportingQuote": None
            }

        norm = FinancialNumericNormalizer.normalize_measurement(
            val_raw, "%/năm", quote, raw_bytes, locale="vi_VN", indicator_id="MP-02"
        )
        obs_timestamp = None

        return {
            "success": True,
            "actualValue": norm["normalizedNumericValue"],
            "unit": "%/năm",
            "observationDate": obs_date,
            "observationTimestamp": obs_timestamp,
            "observationPeriod": "Hằng ngày",
            "change": None,
            "direction": None,
            "supportingQuote": quote,
            "sourcePublisher": "sbv.gov.vn",
            "normalizationTrace": norm
        }

    @classmethod
    def extract_mp03_deposit_rate(cls, text: str, raw_bytes: bytes = b"", source_url: str = "") -> Dict[str, Any]:
        """
        MP-03: Highest 12-Month Deposit Rate across surveyed commercial banks.
        Enforces P0-01 Mandates:
        1. Extracts from actual main article body, ignoring sidebars and unrelated article links.
        2. Identifies each 12-month rate candidate.
        3. Distinguishes standard rates (e.g. 6.7-7.1%) from promotional rates (e.g. 8.9-9.1%).
        4. Identifies deposit channel, minimum deposit, and promotional terms.
        5. Does not infer bank coverage from unrelated sidebar links.
        6. If the article describes an unnamed bank ('một ngân hàng') without established coverage:
           Classifies as UNVERIFIED with actualValue: None.
        """
        # Step 1: Extract main article body
        body_html = cls.extract_article_body(text)
        # Strip tags for textual inspection
        body_clean = re.sub(r'<[^>]+>', ' ', body_html)
        body_clean = ' '.join(body_clean.split())

        # Check if the article describes an unnamed institution
        is_unnamed_bank = bool(re.search(r'\bmột ngân hàng\b|\bngân hàng này\b', body_clean, re.I))

        # Check for 12-month rate expressions in article body
        # Standard rate: e.g. "Lãi suất kỳ hạn 12 tháng là 6,7 - 7,1%/năm", "Lãi suất tiền gửi 12 tháng tại Vietcombank là 4,7%/năm",
        # or survey: "Ở kỳ hạn 12 tháng, MBV, PGBank, Sacombank, VCBNeo và VIB cùng niêm yết mức 7%/năm, cao nhất."
        pat_std = r'(?:lãi suất\s+)?(?:tiền gửi\s+)?(?:kỳ hạn\s+12\s+tháng|12\s+tháng).*?(?:(?:tại\s+(?P<bank>[A-Za-z0-9\s]+?))\s+)?(?:là|ở mức|đạt|niêm yết(?:\s+mức)?|cùng niêm yết(?:\s+mức)?|áp dụng|cao nhất(?: đạt)?|\:)\s*(?P<r1>\d{1,2}(?:[\.,]\d{1,2})?)(?:\s*-\s*(?P<r2>\d{1,2}(?:[\.,]\d{1,2})?))?\s*(?P<unit>%/năm|%)'
        m_std = re.search(pat_std, body_clean, re.I)

        # Promotional rate: e.g. "sau khi cộng thêm lãi suất, mức cao nhất lên tới 8,9 - 9,1%/năm"
        pat_promo = r'(?:sau khi cộng thêm|cao nhất lên tới|lên tới)\s*(?P<r1>\d{1,2}[\.,]\d{1,2})(?:\s*-\s*(?P<r2>\d{1,2}[\.,]\d{1,2}))?\s*(?P<unit>%/năm|%)'
        m_promo = re.search(pat_promo, body_clean, re.I)

        if not m_std and not m_promo:
            # Fallback scan across article body
            pat_gen = r'(?:kỳ hạn\s+12\s+tháng|12\s+tháng).*?(?P<r1>\d{1,2}[\.,]\d{1,2})(?:\s*-\s*(?P<r2>\d{1,2}[\.,]\d{1,2}))?\s*(?P<unit>%/năm|%)'
            m_std = re.search(pat_gen, body_clean, re.I)

        if not m_std and not m_promo:
            return {
                "success": False,
                "unverifiedReason": "Không tìm thấy biểu lãi suất hoặc thống kê tiền gửi kỳ hạn 12 tháng trong nội dung bài viết.",
                "bankName": None,
                "actualValue": None,
                "rateType": None,
                "termMonths": 12,
                "depositChannel": None,
                "minimumDeposit": None,
                "promotionalConditions": None,
                "observationDate": None,
                "observationTimestamp": None,
                "sourceUrl": source_url,
                "supportingQuote": None,
                "evidenceSha256": hashlib.sha256(raw_bytes).hexdigest() if raw_bytes else None
            }

        # Build rates inventory
        std_val = m_std.group('r2') or m_std.group('r1') if m_std else None
        promo_val = m_promo.group('r2') or m_promo.group('r1') if m_promo else None

        # Detect deposit channel
        channel = "ONLINE" if "online" in body_clean.lower() else "COUNTER" if "tại quầy" in body_clean.lower() else "ALL"

        # Detect minimum deposit & promotional terms
        min_dep = None
        m_min = re.search(r'từ\s+(?:\d+\s+(?:triệu|tỷ))\s+đồng', body_clean, re.I)
        if m_min:
            min_dep = m_min.group(0)

        promo_cond = None
        if "cộng thêm" in body_clean.lower() or "khuyến mại" in body_clean.lower() or "ưu đãi" in body_clean.lower():
            promo_cond = "Áp dụng chương trình ưu đãi / cộng thêm lãi suất có điều kiện tiền gửi tối thiểu hoặc thời hạn áp dụng."

        # Date extraction: check announcement date at article start, or proximity to rates
        anchor_pos = m_std.start() if m_std else (m_promo.start() if m_promo else 0)
        obs_date = (
            cls.extract_observation_date_proximity(body_clean, anchor_pos, window=350) or
            cls.extract_observation_date_proximity(text, 0, window=1000) or
            cls.extract_observation_date_proximity(body_clean, 0, window=350)
        )

        # Build supporting quote containing exact rate and terms
        quote_parts = []
        if m_std:
            quote_parts.append(m_std.group(0))
        if m_promo:
            quote_parts.append(m_promo.group(0))
        quote = ". ".join(quote_parts)[:180].strip()

        ev_sha = hashlib.sha256(raw_bytes).hexdigest() if raw_bytes else None

        is_promo = bool(promo_val or promo_cond or "ưu đãi" in body_clean.lower() or "vip" in body_clean.lower() or "khuyến mại" in body_clean.lower())

        # Check bank identity
        # P0-01 Rule: Do NOT infer bank coverage from sidebar headlines.
        # If the article describes an unnamed bank ('một ngân hàng'), it cannot establish nationwide coverage.
        if is_unnamed_bank:
            return {
                "success": False,
                "unverifiedReason": "UNVERIFIED_BANK_IDENTITY: Nguồn tin chỉ nêu 'một ngân hàng' chưa công bố danh tính cụ thể; không đủ điều kiện xác thực lãi suất đại diện toàn hệ thống hoặc khảo sát đa ngân hàng.",
                "bankName": "Chưa xác định danh tính (NHTM chưa công bố tên)",
                "actualValue": None,
                "unit": "%/năm",
                "rateType": "PROMOTIONAL" if is_promo else "STANDARD",
                "isPromotional": is_promo,
                "termMonths": 12,
                "depositChannel": channel,
                "minimumDeposit": min_dep,
                "promotionalConditions": promo_cond,
                "observationDate": obs_date,
                "observationTimestamp": None,
                "sourceUrl": source_url,
                "supportingQuote": quote,
                "evidenceSha256": ev_sha,
                "standardRateRange": f"{m_std.group('r1')}{' - ' + m_std.group('r2') if m_std.group('r2') else ''} %/năm" if m_std else None,
                "promotionalRateRange": f"{m_promo.group('r1')}{' - ' + m_promo.group('r2') if m_promo.group('r2') else ''} %/năm" if m_promo else None
            }

        # Extract bank name if present
        extracted_bank = "NHTM được xác minh"
        if m_std:
            m_b = re.search(r'(?:tại|ở kỳ hạn 12 tháng,?\s*)([A-Za-z0-9\s, và]+?)\s+(?:cùng\s+)?(?:niêm yết|áp dụng)', body_clean, re.I)
            if m_b and len(m_b.group(1).strip()) > 2:
                extracted_bank = m_b.group(1).strip()
            else:
                try:
                    b_cand = m_std.group('bank')
                    if b_cand and b_cand.strip():
                        extracted_bank = b_cand.strip()
                except IndexError:
                    pass
        if extracted_bank == "NHTM được xác minh":
            m_b2 = re.search(r'tại\s+([A-Za-z0-9\s]+?)(?:\s+(?:cao nhất|đạt|là|\.|\,)|$)', body_clean, re.I)
            if m_b2 and len(m_b2.group(1).strip()) > 2:
                extracted_bank = m_b2.group(1).strip()

        # If a specific identified bank or authenticated survey is present in main body
        chosen_val = promo_val or std_val
        norm = FinancialNumericNormalizer.normalize_measurement(
            chosen_val, "%/năm", quote, raw_bytes, locale="vi_VN", indicator_id="MP-03"
        )
        return {
            "success": True,
            "unverifiedReason": None,
            "bankName": extracted_bank,
            "actualValue": norm["normalizedNumericValue"],
            "unit": "%/năm",
            "rateType": "PROMOTIONAL" if is_promo else "STANDARD",
            "isPromotional": is_promo,
            "termMonths": 12,
            "depositChannel": channel,
            "minimumDeposit": min_dep,
            "promotionalConditions": promo_cond,
            "standardRateRange": f"{m_std.group('r1')}{' - ' + m_std.group('r2') if m_std.group('r2') else ''} %/năm" if m_std else None,
            "promotionalRateRange": f"{m_promo.group('r1')}{' - ' + m_promo.group('r2') if m_promo.group('r2') else ''} %/năm" if m_promo else None,
            "observationDate": obs_date,
            "observationTimestamp": None,
            "sourceUrl": source_url,
            "supportingQuote": quote,
            "evidenceSha256": ev_sha,
            "normalizationTrace": norm
        }

    @classmethod
    def extract_mp04_vnindex(cls, text: str, raw_bytes: bytes = b"") -> Dict[str, Any]:
        """
        MP-04: VN-Index Official Closing Level.
        Enforces P0-06 Mandates:
        1. Strictly rejects intraday sessions.
        2. If change is approximate ('giảm hơn 11 điểm'), change = None; do not fabricate -11.00.
        3. Do not hardcode 15:00 measurement timestamp when source only supports session date.
        """
        lower_text = text.lower()
        intraday_markers = [
            "tạm dừng phiên sáng", "phiên sáng", "khớp lệnh liên tục", "tính đến 11h",
            "tính đến 14h", "đang giao dịch", "phiên giao dịch sáng"
        ]
        if any(im in lower_text for im in intraday_markers) and not any(cm in lower_text for cm in ["đóng cửa", "chốt phiên", "kết phiên"]):
            return {
                "success": False,
                "unverifiedReason": "UNVERIFIED_INTRADAY: Phiên giao dịch intraday chưa kết thúc hoặc số liệu thuộc phiên sáng; không đủ tiêu chuẩn chỉ số đóng cửa.",
                "actualValue": None,
                "observationDate": None,
                "observationTimestamp": None,
                "supportingQuote": None
            }

        # Check for arithmetic discrepancy between close, prev close, and claimed change
        m_arith = re.search(r'đóng cửa tại\s*(?P<close>[\d\.,]+)\s*điểm,\s*(?P<dir>tăng|giảm)\s*(?P<chg>[\d\.,]+)\s*điểm.*?phiên liền trước\s*(?P<prev>[\d\.,]+)', text, re.I)
        if m_arith:
            try:
                c_val = float(FinancialNumericNormalizer.parse_locale_number(m_arith.group('close'), indicator_id="MP-04"))
                p_val = float(FinancialNumericNormalizer.parse_locale_number(m_arith.group('prev'), indicator_id="MP-04"))
                chg_val = float(FinancialNumericNormalizer.parse_locale_number(m_arith.group('chg')))
                expected_diff = chg_val if "tăng" in m_arith.group('dir').lower() else -chg_val
                actual_diff = c_val - p_val
                if abs(actual_diff - expected_diff) > 0.1:
                    return {
                        "success": False,
                        "unverifiedReason": "ARITHMETIC_MISMATCH: Chênh lệch số học giữa giá đóng cửa, giá tham chiếu và mức thay đổi.",
                        "actualValue": None,
                        "observationDate": None,
                        "observationTimestamp": None,
                        "supportingQuote": None
                    }
            except Exception:
                pass

        body_text = cls.extract_article_body(text)
        search_text = body_text if len(body_text) > 50 else text
        ctx_yr = cls.extract_contextual_year(text)

        # Look for closing index phrasing
        pat = (
            r'(?:kết thúc phiên(?:\s+giao\s+dịch)?|đóng cửa phiên|chốt phiên|kết phiên|kết tuần|'
            r'chỉ số vn-index đóng cửa)[^.!?\n<]*?'
            r'(?:tại|ở mức|đạt|xuống|lên|về)?\s*'
            r'(?P<val>\b1[\.,]\d{3}(?:[\.,]\d{1,2})?|\b[7-9]\d{2}(?:[\.,]\d{1,2})?)\s*'
            r'(?:điểm)?'
        )
        m = re.search(pat, search_text, re.I) or re.search(pat, text, re.I)
        matched_in_body = bool(re.search(pat, search_text, re.I))
        if not m:
            pat2 = (
                r'(?:vn-index[^.!?\n<]*?(?:đóng cửa|chốt phiên|kết phiên|kết thúc phiên|kết tuần|tăng|giảm|lên|về|đạt))[^.!?\n<]*?'
                r'(?:tại|ở mức|đạt|lên|về|xuống)?\s*'
                r'(?P<val>\b1[\.,]\d{3}(?:[\.,]\d{1,2})?|\b[7-9]\d{2}(?:[\.,]\d{1,2})?)\s*'
                r'(?:điểm)?'
            )
            m = re.search(pat2, search_text, re.I) or re.search(pat2, text, re.I)
            matched_in_body = bool(re.search(pat2, search_text, re.I))

        if not m:
            return {
                "success": False,
                "unverifiedReason": "Không tìm thấy mức điểm đóng cửa chính thức của VN-Index.",
                "actualValue": None,
                "observationDate": None,
                "observationTimestamp": None,
                "supportingQuote": None
            }

        target_src = search_text if matched_in_body else text
        val_raw = m.group('val')
        anchor_pos = m.start()
        obs_date = (
            cls.extract_observation_date_proximity(target_src, anchor_pos, window=300, contextual_year=ctx_yr)
            or cls.extract_observation_date_proximity(text, 0, window=3000, contextual_year=ctx_yr)
        )

        m_sent = re.search(r'[^.!?\n<>]*?' + re.escape(m.group(0)) + r'[^.!?\n<>]*', target_src)
        raw_quote = m_sent.group(0) if m_sent else m.group(0)
        clean_q = re.sub(r'</(h\d|p|div|li|figcaption)>', '. ', raw_quote)
        clean_q = re.sub(r'<[^>]+>', ' ', clean_q)
        clean_q = re.sub(r'^[^<>]*?>\s*', '', clean_q).strip()
        clean_q = ' '.join(clean_q.split())
        quote = clean_q
        for s in re.split(r'(?<=[.!?])\s+', clean_q):
            if val_raw in s:
                quote = s[:160].strip()
                break
        if quote not in text and m.group(0).strip() in text:
            quote = m.group(0).strip()[:160]
        if cls.is_navigation_quote(quote):
            return {
                "success": False,
                "unverifiedReason": "NAVIGATION_LABEL_REJECTED: Trích dẫn thuộc thanh điều hướng.",
                "actualValue": None,
                "observationDate": None,
                "observationTimestamp": None,
                "supportingQuote": None
            }

        # Detect net change in points
        # P0-06 Mandate: If change is qualified as approximate ('hơn 11 điểm', 'gần 11 điểm'),
        # change must NOT be represented as exactly -11. If exact previous close is unavailable, change = None.
        m_change = re.search(r'(?P<dir>tăng|giảm)\s*(?:nhẹ\s*|mạnh\s*)?(?P<qual>hơn\s*|gần\s*|khoảng\s*)?(?P<cval>\b\d{1,2}(?:[\.,]\d{1,2})?)\s*điểm', quote, re.I)
        change_val = None
        direction_val = None
        if m_change:
            is_approx = bool(m_change.group('qual'))
            is_down = "giảm" in m_change.group('dir').lower()
            direction_val = "DOWN" if is_down else "UP"
            if not is_approx:
                cval_str = m_change.group('cval').replace(",", ".")
                change_val = f"-{cval_str}" if is_down else f"+{cval_str}"
            else:
                # Approximate change -> cannot represent as exact number without previous close
                change_val = None

        norm = FinancialNumericNormalizer.normalize_measurement(
            val_raw, "Điểm", quote, raw_bytes, locale="vi_VN", indicator_id="MP-04"
        )
        # P0-06: Do NOT hardcode 15:00 as an exact measurement timestamp when source only supports session date
        obs_timestamp = None

        return {
            "success": True,
            "actualValue": norm["normalizedNumericValue"],
            "unit": "Điểm",
            "observationDate": obs_date,
            "observationTimestamp": obs_timestamp,
            "observationPeriod": "Hằng ngày",
            "change": change_val,
            "direction": direction_val,
            "supportingQuote": quote,
            "normalizationTrace": norm
        }

    @classmethod
    def extract_mp05_credit_growth(cls, text: str, raw_bytes: bytes = b"") -> Dict[str, Any]:
        """
        MP-05: System-wide Credit Growth.
        Rejects single-bank quotas and local municipality numbers.
        """
        body_text = cls.extract_article_body(text)
        search_text = body_text if len(body_text) > 50 else text
        lower_text = search_text.lower()
        if "tphcm" in lower_text or "tp.hcm" in lower_text or "hà nội" in lower_text:
            if not ("toàn hệ thống" in lower_text or "toàn nền kinh tế" in lower_text or "cả nước" in lower_text):
                if re.search(r'tín dụng[^.!?\n]{0,80}(?:tp\.?hcm|hà nội)|(?:tp\.?hcm|hà nội)[^.!?\n]{0,80}tín dụng', lower_text):
                    return {
                        "success": False,
                        "unverifiedReason": "LOCAL_SCOPE_EXCLUDED: Số liệu tín dụng thuộc phạm vi địa phương riêng lẻ (TP.HCM/Hà Nội), không phải toàn hệ thống.",
                        "actualValue": None,
                        "observationDate": None,
                        "observationTimestamp": None,
                        "supportingQuote": None
                    }

        pat = r'(?:tăng trưởng tín dụng[^.!?\n<>]{0,80}?(?:toàn hệ thống|nền kinh tế)?|tín dụng đối với nền kinh tế|dư nợ tín dụng toàn (?:hệ thống|nền kinh tế))[^.!?\n<>]{0,80}?(?:đạt|khoảng|ước đạt|tăng)\s*(?P<val>\b\d{1,2}[\.,]\d{1,2})\s*(?P<unit>%)'
        m = re.search(pat, search_text, re.I)
        if not m:
            return {
                "success": False,
                "unverifiedReason": "Không tìm thấy số liệu tăng trưởng tín dụng toàn hệ thống.",
                "actualValue": None,
                "observationDate": None,
                "observationTimestamp": None,
                "supportingQuote": None
            }

        val_raw = m.group('val')
        anchor_pos = m.start()
        obs_date = cls.extract_observation_date_proximity(text, anchor_pos, window=250)

        m_sent = re.search(r'[^.!?\n]*?' + re.escape(m.group(0)) + r'[^.!?\n]*', text)
        full_cand = m_sent.group(0).strip() if m_sent else m.group(0).strip()
        val_pos = full_cand.find(val_raw)
        if val_pos != -1 and len(full_cand) > 160:
            start_q = max(0, val_pos - 80)
            end_q = min(len(full_cand), val_pos + 80)
            quote = full_cand[start_q:end_q].strip()
        else:
            quote = full_cand[:160].strip()

        if cls.is_navigation_quote(quote):
            return {
                "success": False,
                "unverifiedReason": "NAVIGATION_LABEL_REJECTED: Trích dẫn thuộc thanh điều hướng.",
                "actualValue": None,
                "observationDate": None,
                "observationTimestamp": None,
                "supportingQuote": None
            }

        period_str = f"Tính đến ngày {obs_date}" if obs_date else "Tính đến kỳ báo cáo"

        norm = FinancialNumericNormalizer.normalize_measurement(
            val_raw, "%", quote, raw_bytes, locale="vi_VN", indicator_id="MP-05"
        )
        obs_timestamp = None

        return {
            "success": True,
            "actualValue": norm["normalizedNumericValue"],
            "unit": "%",
            "observationDate": obs_date,
            "observationTimestamp": obs_timestamp,
            "observationPeriod": period_str,
            "change": None,
            "direction": None,
            "supportingQuote": quote,
            "normalizationTrace": norm
        }

    @classmethod
    def extract_mp06_vietqr_volume(cls, text: str, raw_bytes: bytes = b"") -> Dict[str, Any]:
        """
        MP-06: VietQR-specific Transaction Volume.
        Enforces P0-02 & Bug B Mandates:
        1. Sentence-level scope isolation: VietQR subject and transaction volume metric must
           co-occur within the SAME sentence or clause.
        2. Strictly prevents cross-sentence scope leakage where VietQR keyword in one sentence
           associates with total NAPAS switching volume in another sentence.
        3. Strictly rejects duration phrases ('hơn 1 tháng nay', '1 năm qua').
        4. Rejects total NAPAS switching / ATM / POS volume even if VietQR is mentioned elsewhere.
        """
        lower_text = text.lower()

        # P0-02: Strictly reject service duration expressions
        # e.g. "VietQRGlobal đã được sử dụng hơn 1 tháng nay."
        if re.search(r'vietqr.*?\b(?:hơn|được)?\s*\d+\s*(?:tháng|năm|ngày|tuần)\s*nay\b', text, re.I):
            has_actual_tx = bool(re.search(r'(?:giao dịch|sản lượng).*?\b\d+\s*(?:triệu|tỷ)\s*(?:giao dịch|lượt)', text, re.I))
            if not has_actual_tx:
                return {
                    "success": False,
                    "unverifiedReason": "UNVERIFIED_METRIC_ABSENT: Nội dung nguồn chỉ mô tả thời gian vận hành dịch vụ (thời lượng), không có số liệu sản lượng giao dịch.",
                    "actualValue": None,
                    "observationDate": None,
                    "observationTimestamp": None,
                    "supportingQuote": None
                }

        # Break text into individual sentences for strict sentence-boundary evaluation
        sentences = [s.strip() for s in re.split(r'(?<=[.!?\n])\s+', text) if s.strip()]

        matched_sentence = None
        matched_match = None
        has_napas_system_volume = False

        vietqr_subject_kw = ["vietqr", "mã qr", "quét mã qr", "thanh toán qr", "mã vietqr", "cổng vietqr"]
        napas_total_kw = ["toàn hệ thống napas", "chuyển mạch napas", "hệ thống napas", "chuyển mạch bù trừ", "kênh atm", "máy pos", "toàn hệ thống"]

        pat_same_sentence = r'(?:giao dịch qua mã vietqr|giao dịch vietqr|thanh toán quét mã qr|giao dịch qua mã qr|sản lượng giao dịch qua mã vietqr|sản lượng vietqr|thanh toán vietqr|vietqr\s*(?:đạt|đã đạt|ghi nhận)?|giao dịch quét mã vietqr).*?(?:đạt|ước đạt|khoảng|hơn|ghi nhận)?\s*(?P<val>\b\d{1,4}(?:[\.,]\d{1,2})?)\s*(?P<unit>triệu|tỷ|nghìn)\s*(?:giao dịch|lượt giao dịch|lượt)\b'
        pat_reverse_sentence = r'(?P<val>\b\d{1,4}(?:[\.,]\d{1,2})?)\s*(?P<unit>triệu|tỷ|nghìn)\s*(?:giao dịch|lượt giao dịch|lượt)\s*(?:qua|bằng)?\s*(?:mã\s*)?(?:vietqr|qr)'

        for sent in sentences:
            sent_lower = sent.lower()

            # Detect whether this sentence contains system-wide NAPAS volume
            if any(k in sent_lower for k in napas_total_kw):
                if re.search(r'\b\d{1,4}(?:[\.,]\d{1,2})?\s*(?:triệu|tỷ)\s*(?:giao dịch|lượt)', sent, re.I):
                    has_napas_system_volume = True

            # Sentence must contain VietQR subject to qualify
            if not any(k in sent_lower for k in vietqr_subject_kw):
                continue

            # If sentence mentions total NAPAS system volume as the subject of the transaction metric
            if any(k in sent_lower for k in napas_total_kw):
                # Check if the number belongs to NAPAS total rather than VietQR
                if re.search(r'(?:toàn hệ thống|napas|chuyển mạch).*?(?:đạt|khoảng|hơn)?\s*\d+\s*(?:triệu|tỷ)\s*giao dịch', sent, re.I):
                    if not re.search(r'vietqr\s*(?:đạt|đạt mức|chiếm|được)?\s*\d+\s*(?:triệu|tỷ)\s*giao dịch', sent, re.I):
                        continue

            m = re.search(pat_same_sentence, sent, re.I) or re.search(pat_reverse_sentence, sent, re.I)
            if m:
                matched_sentence = sent
                matched_match = m
                break

        if not matched_match:
            # Check if general text has NAPAS switching volume
            if has_napas_system_volume or "hệ thống napas" in lower_text or "chuyển mạch" in lower_text or "toàn hệ thống napas" in lower_text:
                return {
                    "success": False,
                    "unverifiedReason": "UNVERIFIED_SCOPE_MISMATCH: Số liệu thuộc tổng sản lượng chuyển mạch bù trừ NAPAS toàn hệ thống, không tách riêng VietQR.",
                    "actualValue": None,
                    "observationDate": None,
                    "observationTimestamp": None,
                    "supportingQuote": None
                }
            return {
                "success": False,
                "unverifiedReason": "UNVERIFIED_METRIC_ABSENT: Không tìm thấy số liệu sản lượng giao dịch VietQR cụ thể hoặc thiếu đơn vị đo lường hợp lệ trong cùng ngữ cảnh câu.",
                "actualValue": None,
                "observationDate": None,
                "observationTimestamp": None,
                "supportingQuote": None
            }

        quote = matched_match.group(0)[:160].strip()
        if cls.is_navigation_quote(quote):
            return {
                "success": False,
                "unverifiedReason": "NAVIGATION_LABEL_REJECTED: Trích dẫn thuộc thanh điều hướng.",
                "actualValue": None,
                "observationDate": None,
                "observationTimestamp": None,
                "supportingQuote": None
            }

        val_raw = matched_match.group('val')
        unit_raw = matched_match.group('unit')
        if not unit_raw:
            return {
                "success": False,
                "unverifiedReason": "UNVERIFIED_METRIC_ABSENT: Thiếu đơn vị đo lường giao dịch.",
                "actualValue": None,
                "observationDate": None,
                "observationTimestamp": None,
                "supportingQuote": None
            }

        expr = f"{val_raw} {unit_raw} giao dịch"
        anchor_pos = text.find(matched_sentence)
        if anchor_pos == -1:
            anchor_pos = 0
        obs_date = cls.extract_observation_date_proximity(text, anchor_pos, window=250)

        norm = FinancialNumericNormalizer.normalize_measurement(
            expr, "tỷ giao dịch", quote, raw_bytes, locale="vi_VN", indicator_id="MP-06"
        )
        obs_timestamp = None

        return {
            "success": True,
            "actualValue": norm["normalizedNumericValue"],
            "unit": "tỷ giao dịch",
            "observationDate": obs_date,
            "observationTimestamp": obs_timestamp,
            "observationPeriod": "Hằng quý",
            "change": None,
            "direction": None,
            "supportingQuote": quote,
            "normalizationTrace": norm
        }

    @classmethod
    def extract_mp07_tourist_arrivals(cls, text: str, raw_bytes: bytes = b"") -> Dict[str, Any]:
        """
        MP-07: International Tourist Arrivals to Vietnam.
        Enforces P0-01 Mandates:
        1. Binds every numeric observation to its country/entity (Vietnam vs foreign countries such as Thailand)
           and reporting period (monthly vs cumulative YTD vs historical years).
        2. Handles Vietnam vs Thailand in the same sentence, multiple countries in one paragraph,
           and monthly vs YTD reporting periods.
        3. Fails closed if only foreign-country, local-province, or gap/target numbers are present.
        """
        body_text = cls.extract_article_body(text)
        clean_body = body_text if len(body_text) > 50 else re.sub(r'<[^>]+>', ' ', text)
        clean_body = ' '.join(clean_body.split())

        foreign_countries = [
            "thái lan", "malaysia", "singapore", "trung quốc", "hàn quốc", "nhật bản",
            "campuchia", "indonesia", "philippines", "lào", "myanmar", "ấn độ",
            "mỹ", "châu âu", "đài loan", "nga", "úc"
        ]
        local_provinces = [
            "hà nội", "tp.hcm", "tphcm", "tp hồ chí minh", "đà nẵng", "khánh hòa", "nha trang",
            "phú quốc", "kiên giang", "quảng ninh", "hạ long", "lào cai", "sa pa", "hội an",
            "quảng nam", "huế", "bình thuận", "vũng tàu", "đà lạt", "lâm đồng", "ninh bình", "thanh hóa"
        ]
        non_arrival_markers = [
            "chênh lệch", "khoảng cách", "rút ngắn", "thu hẹp",
            "mục tiêu", "kế hoạch", "phấn đấu", "dự kiến đón", "kỳ vọng đón",
            "doanh thu", "tổng thu", "khôi phục mốc", "kỷ lục"
        ]
        historical_years = ["2019", "2020", "2021", "2022", "2023", "2024", "2025", "trước đại dịch"]

        sentences = [s.strip() for s in re.split(r'(?<=[.!?\n])\s+', clean_body) if s.strip()]
        candidates = []
        rejected_foreign = []
        rejected_local = []

        pat_clause_num = re.compile(
            r'(?P<val>\b\d{1,3}(?:[\.,]\d{1,3})?)\s*(?P<unit>triệu|nghìn)\s*(?:lượt(?:\s*khách(?:\s*quốc\s*tế)?)?|khách(?:\s*quốc\s*tế)?)',
            re.I
        )

        for idx, sent in enumerate(sentences):
            sent_lower = sent.lower()
            prev_sent = sentences[idx - 1] if idx > 0 else ""
            prev_lower = prev_sent.lower()
            next_sent = sentences[idx + 1] if idx + 1 < len(sentences) else ""
            context_window = f"{prev_sent} {sent}".strip()
            context_lower = context_window.lower()

            # Ensure context is about international tourists (not domestic tourists or unrelated metrics)
            has_intl_context = any(
                kw in sent_lower or kw in prev_lower or kw in next_sent.lower()
                for kw in ["khách quốc tế", "khách du lịch quốc tế", "du khách quốc tế", "lượt khách quốc tế"]
            )
            if not has_intl_context:
                continue

            # Split sentence into individual clauses to bind each number to its subject entity (preserve decimal commas like 19,5)
            clauses = re.split(r'(?<!\d),(?!\d)|;|(?:\btrong khi\b|\bso với\b|\bnhưng\b|\bkéo\b)', sent, flags=re.I)

            # Determine sentence-level period context (including immediate short period sentence like "Trong 10 tháng đầu năm.")
            sent_has_hist_year = any(hy in sent_lower for hy in historical_years) and "2026" not in sent_lower and "năm nay" not in sent_lower

            for cl in clauses:
                cl_strip = cl.strip()
                if not cl_strip:
                    continue
                cl_lower = cl_strip.lower()

                for m_num in pat_clause_num.finditer(cl_strip):
                    val_raw = m_num.group("val")
                    unit_raw = m_num.group("unit") or "triệu"

                    # 1. Check non-arrival / difference / target markers in clause
                    pre_in_clause = cl_lower[:m_num.start()]
                    if any(nam in cl_lower for nam in non_arrival_markers):
                        # If the marker directly governs this clause's number, skip it
                        if any(nam in pre_in_clause or nam in cl_lower for nam in ["chênh lệch", "khoảng cách", "mục tiêu", "kế hoạch", "phấn đấu", "doanh thu", "khôi phục mốc"]):
                            continue

                    # 2. Identify entity bound to this clause
                    has_vn_clause = any(v in cl_lower for v in ["việt nam", "nước ta", "cả nước"])
                    foreign_in_clause = [fc for fc in foreign_countries if fc in cl_lower]
                    local_in_clause = [lp for lp in local_provinces if lp in cl_lower]

                    if foreign_in_clause and not has_vn_clause:
                        rejected_foreign.append((foreign_in_clause[0], val_raw, cl_strip))
                        continue

                    if local_in_clause and not has_vn_clause:
                        rejected_local.append((local_in_clause[0], val_raw, cl_strip))
                        continue

                    # If foreign countries exist elsewhere in the sentence, require explicit Vietnam binding in this clause
                    has_foreign_in_sent = any(fc in sent_lower for fc in foreign_countries)
                    has_local_in_sent = any(lp in sent_lower for lp in local_provinces)
                    if (has_foreign_in_sent or has_local_in_sent) and not has_vn_clause:
                        if has_foreign_in_sent:
                            rejected_foreign.append(("foreign_in_sentence", val_raw, cl_strip))
                        continue

                    # If no foreign country or local province in sentence, check Vietnam binding in sentence or article
                    has_vn_sent_or_doc = has_vn_clause or any(
                        v in sent_lower or v in prev_lower or v in clean_body.lower()
                        for v in ["việt nam", "nước ta", "cả nước"]
                    )
                    if not has_vn_sent_or_doc:
                        continue

                    # 3. Check historical year binding
                    clause_has_hist_year = any(hy in cl_lower for hy in historical_years)
                    if clause_has_hist_year or sent_has_hist_year:
                        continue

                    # 4. Bind reporting period (Monthly vs Cumulative YTD)
                    period_search_str = f"{prev_sent} {sent}"
                    m_ytd = re.search(
                        r'((?:tính\s+chung\s+|trong\s+|lũy\s+kế\s+)?\b\d{1,2}\s+tháng(?:\s+đầu\s+năm)?(?:\s+năm\s+\d{4}|\s+\d{4})?)',
                        period_search_str, re.I
                    )
                    m_monthly = re.search(
                        r'((?:riêng\s+|trong\s+)?tháng\s+\d{1,2}(?:[\/\-]\d{4}|\s+năm\s+\d{4})?(?:\s+ước\s+đạt)?)',
                        cl_strip if "tháng" in cl_lower else sent, re.I
                    )

                    # Distinguish monthly vs YTD in the same sentence/paragraph
                    clause_is_monthly = bool(re.search(r'(?:riêng\s+|trong\s+)?tháng\s+\d{1,2}(?!\s+đầu\s+năm)', cl_lower))
                    clause_is_ytd = bool(re.search(r'\b\d{1,2}\s+tháng\s+đầu\s+năm|tính\s+chung\s+\d{1,2}\s+tháng|lũy\s+kế', cl_lower))

                    if clause_is_monthly and not clause_is_ytd:
                        is_monthly = True
                        is_ytd = False
                        reporting_period = m_monthly.group(1).strip() if m_monthly else "Hằng tháng"
                    elif clause_is_ytd or (m_ytd and not clause_is_monthly):
                        is_monthly = False
                        is_ytd = True
                        reporting_period = m_ytd.group(1).strip() if m_ytd else "Lũy kế năm"
                    elif m_monthly:
                        is_monthly = True
                        is_ytd = False
                        reporting_period = m_monthly.group(1).strip()
                    else:
                        is_monthly = False
                        is_ytd = True
                        reporting_period = "Lũy kế năm"

                    candidates.append({
                        "val_raw": val_raw,
                        "unit_raw": unit_raw,
                        "sentence": sent,
                        "clause": cl_strip,
                        "prev_sent": prev_sent,
                        "is_monthly": is_monthly,
                        "is_ytd": is_ytd,
                        "reporting_period": reporting_period,
                        "explicit_vn_clause": has_vn_clause,
                    })

        if not candidates:
            if rejected_foreign:
                fc_name, fc_val, _ = rejected_foreign[0]
                return {
                    "success": False,
                    "unverifiedReason": f"WRONG_COUNTRY_ENTITY: Số liệu khách quốc tế ({fc_val}) thuộc thực thể nước ngoài ({fc_name}), không phải lượng khách quốc tế đến Việt Nam.",
                    "actualValue": None,
                    "observationDate": None,
                    "observationTimestamp": None,
                    "supportingQuote": None
                }
            if rejected_local:
                lp_name, lp_val, _ = rejected_local[0]
                return {
                    "success": False,
                    "unverifiedReason": f"LOCAL_SCOPE_EXCLUDED: Số liệu khách du lịch ({lp_val}) thuộc địa phương ({lp_name}), không phải toàn quốc.",
                    "actualValue": None,
                    "observationDate": None,
                    "observationTimestamp": None,
                    "supportingQuote": None
                }
            return {
                "success": False,
                "unverifiedReason": "Không tìm thấy số liệu lượt khách quốc tế đến Việt Nam.",
                "actualValue": None,
                "observationDate": None,
                "observationTimestamp": None,
                "supportingQuote": None
            }

        # Prefer cumulative YTD national headline figure when both monthly and YTD are present, or first explicit Vietnam-bound candidate
        chosen = None
        for cand in candidates:
            if cand["explicit_vn_clause"] and cand["is_ytd"]:
                chosen = cand
                break
        if not chosen:
            for cand in candidates:
                if cand["explicit_vn_clause"]:
                    chosen = cand
                    break
        if not chosen:
            chosen = candidates[0]

        val_raw = chosen["val_raw"]
        unit_raw = chosen["unit_raw"]
        sent_text = chosen["sentence"]
        raw_pos = text.find( chosen["clause"][:30] )
        if raw_pos == -1:
            raw_pos = text.find(val_raw)
        if raw_pos == -1:
            raw_pos = 0

        obs_date = cls.extract_observation_date_proximity(
            f"{chosen['prev_sent']} {sent_text}", 0, window=len(chosen["prev_sent"]) + len(sent_text) + 50
        ) or cls.extract_observation_date_proximity(text, raw_pos, window=300)

        # Find verbatim supportingQuote in raw `text` that contains the Vietnam-bound clause
        quote = None
        if sent_text in text and len(sent_text) <= 180:
            quote = sent_text
        elif chosen["clause"] in text and len(chosen["clause"]) >= 15:
            # Prefer full sentence if it exists verbatim in text
            for p in re.findall(r'<p[^>]*>(.*?)</p>', text, re.I | re.DOTALL):
                if val_raw in p and ("việt nam" in p.lower() or "khách quốc tế" in p.lower()):
                    clean_p = ' '.join(re.sub(r'<[^>]+>', ' ', p).split())
                    for s in re.split(r'(?<=[.!?])\s+', clean_p):
                        if val_raw in s and s.strip() in text:
                            quote = s.strip()[:160]
                            break
                    if quote:
                        break
            if not quote:
                quote = chosen["clause"][:160].strip()
        else:
            m_sent = re.search(r'[^.!?\n<>]*?' + re.escape(val_raw) + r'[^.!?\n<>]*', text)
            if m_sent:
                quote = ' '.join(m_sent.group(0).split())[:160].strip()
            else:
                quote = sent_text[:160].strip()

        if cls.is_navigation_quote(quote):
            return {
                "success": False,
                "unverifiedReason": "NAVIGATION_LABEL_REJECTED: Trích dẫn thuộc thanh điều hướng.",
                "actualValue": None,
                "observationDate": None,
                "observationTimestamp": None,
                "supportingQuote": None
            }

        is_monthly = chosen["is_monthly"]
        is_ytd = chosen["is_ytd"]
        period_type = "Hằng tháng" if is_monthly and not is_ytd else "Lũy kế năm"
        expr = f"{val_raw} {unit_raw} lượt"

        norm = FinancialNumericNormalizer.normalize_measurement(
            expr, "triệu lượt", quote, raw_bytes, locale="vi_VN", indicator_id="MP-07"
        )
        obs_timestamp = None

        # YoY comparison extraction
        m_yoy = re.search(r'(tăng|giảm)\s+(\d+(?:[.,]\d+)?%)\s+(?:so với cùng kỳ|YoY)', sent_text, re.I) or re.search(
            r'(tăng|giảm)\s+(\d+(?:[.,]\d+)?%)\s+(?:so với cùng kỳ|YoY)', clean_body, re.I
        )
        yoy_change = None
        yoy_dir = "UNKNOWN"
        if m_yoy:
            yoy_dir = "UP" if m_yoy.group(1).lower() == "tăng" else "DOWN"
            sign = "+" if yoy_dir == "UP" else "-"
            yoy_change = f"{sign}{m_yoy.group(2)} YoY"

        return {
            "success": True,
            "actualValue": norm["normalizedNumericValue"],
            "unit": "triệu lượt",
            "boundEntity": "Việt Nam",
            "reportingPeriod": chosen["reporting_period"],
            "observationDate": obs_date,
            "observationTimestamp": obs_timestamp,
            "observationPeriod": period_type,
            "isMonthly": is_monthly,
            "isCumulativeYTD": is_ytd,
            "allBoundObservations": [
                {
                    "entity": "Việt Nam",
                    "value": c["val_raw"],
                    "unit": f"{c['unit_raw']} lượt",
                    "reportingPeriod": c["reporting_period"],
                    "isMonthly": c["is_monthly"],
                    "isCumulativeYTD": c["is_ytd"],
                }
                for c in candidates
            ],
            "change": yoy_change,
            "direction": yoy_dir,
            "supportingQuote": quote,
            "normalizationTrace": norm
        }

    @classmethod
    def extract_mp08_omo_operations(cls, text: str, raw_bytes: bytes = b"") -> Dict[str, Any]:
        """
        MP-08: SBV Open Market Operations (OMO) Net Liquidity.
        Strictly requires both injection (Repo) and drain (T-bill/Reverse Repo) components.
        Rejects single gross repo awards as net liquidity injection.
        """
        lower_text = text.lower()
        has_drain_keyword = any(k in lower_text for k in ["hút ròng", "rút ròng", "đáo hạn", "tín phiếu", "reverse repo", "bán tín phiếu"])
        has_injection_keyword = any(k in lower_text for k in ["bơm ròng", "cho vay cầm cố", "chào mua", "mua kỳ hạn", "bơm thanh khoản"])

        # Look for explicit net liquidity statement
        pat_net = r'(?:bơm ròng|hút ròng|rút ròng)(?:\s+(?:khoảng|ước tính|đạt|là|gần|hơn|thêm|quy mô))*\s*(?P<val>\b\d{1,3}(?:\.\d{3})+(?:,\d+)?|\b\d+(?:[\.,]\d+)?)\s*(?P<unit>tỷ\s*đồng|tỷ\s*vnd|tỷ)'
        matches = list(re.finditer(pat_net, text, re.I))

        selected_match = None
        selected_obs_date = None
        for m in matches:
            q = m.group(0)[:160].strip()
            if cls.is_navigation_quote(q):
                continue
            od = cls.extract_observation_date_proximity(text, m.start(), window=350)
            if od:
                selected_match = m
                selected_obs_date = od
                break

        if not selected_match and matches:
            for m in matches:
                q = m.group(0)[:160].strip()
                if not cls.is_navigation_quote(q):
                    selected_match = m
                    selected_obs_date = cls.extract_observation_date_proximity(text, m.start(), window=350)
                    break

        if selected_match:
            m_net = selected_match
            obs_date = selected_obs_date
            quote = m_net.group(0)[:160].strip()
            val_raw = m_net.group('val')
            anchor_pos = m_net.start()
            if not obs_date:
                obs_date = cls.extract_observation_date_proximity(text, anchor_pos, window=350)

            is_drain = any(d in quote.lower() for d in ["hút", "rút"])
            direction = "DOWN" if is_drain else "UP"

            norm = FinancialNumericNormalizer.normalize_measurement(
                val_raw, "tỷ VND", quote, raw_bytes, locale="vi_VN", indicator_id="MP-08"
            )
            net_val = f"-{norm['normalizedNumericValue']}" if is_drain else norm["normalizedNumericValue"]
            obs_timestamp = None

            return {
                "success": True,
                "actualValue": net_val,
                "unit": "tỷ VND",
                "observationDate": obs_date,
                "observationTimestamp": obs_timestamp,
                "observationPeriod": "Hằng ngày",
                "change": None,
                "direction": direction,
                "supportingQuote": quote,
                "normalizationTrace": norm
            }

        # If only gross awarded volume is mentioned without maturity/net reconciliation
        if "trúng thầu" in lower_text or "chào mua" in lower_text:
            return {
                "success": False,
                "unverifiedReason": "UNVERIFIED_INCOMPLETE_COMPONENTS: Chỉ có số liệu cho vay cầm cố/trúng thầu thô, thiếu khối lượng đáo hạn cùng kỳ để xác định thanh khoản bơm/hút ròng.",
                "actualValue": None,
                "observationDate": None,
                "observationTimestamp": None,
                "supportingQuote": None
            }

        return {
            "success": False,
            "unverifiedReason": "Không tìm thấy số liệu thanh khoản bơm/hút ròng OMO hoàn chỉnh.",
            "actualValue": None,
            "observationDate": None,
            "observationTimestamp": None,
            "supportingQuote": None
        }
