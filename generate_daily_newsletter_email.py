#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_daily_newsletter_email.py
-----------------------------------------------------------------------------
BRYAN FINTECH INTELLIGENCE — DAILY EMAIL NEWSLETTER GENERATOR (V4.0 INSTITUTIONAL)
Đồng bộ 100% hệ thiết kế V4.0 Clean Institutional UI của Bnews:
- Nền trang: #F8FAFC (Cool Slate) — Bề mặt thẻ: #FFFFFF
- Viền & phân cách: 1px solid #E5E7EB (Flat Institutional, zero box-shadow)
- Màu chủ đạo: #0A3D7A (Institutional Navy) · Nhấn biên tập: #C8102E (Crimson)
- Tín hiệu thị trường: #15803D (Tăng/Tích cực) · #C8102E (Giảm/Rủi ro)
- Typography: 'Be Vietnam Pro' + 'JetBrains Mono' (tabular-nums)
- Ký tự chuẩn BMP ('·', '→', '↗') tương thích tuyệt đối Gmail, Apple Mail, Outlook.
- Số lượng tin tự động theo edition-data.json (40 tin · 6 danh mục chuẩn V4.0).
-----------------------------------------------------------------------------
"""

import os
import sys
import json
import re
from html import escape

WORKSPACE_ROOT = "/Users/quangtri/Documents/Bryan-Portfolio-Antigravity"
SOURCE_JSON = os.path.join(WORKSPACE_ROOT, "fintech-intelligence", "edition-data.json")
OUT_TARGETS = [
    os.path.join(WORKSPACE_ROOT, "pilot-output", "newsletter-preview.html"),
    os.path.join(WORKSPACE_ROOT, "fintech-intelligence", "preview", "newsletter-preview.html"),
    os.path.join(WORKSPACE_ROOT, "fintech-intelligence", "newsletter-preview.html"),
    os.path.join(WORKSPACE_ROOT, "pilot-output", "daily-run-package", "newsletter-preview.html"),
]

SITE_BASE_URL = "https://bryanportfolio.io.vn/fintech-intelligence/"
SUBSCRIBE_URL = "https://bryanportfolio.io.vn/fintech-intelligence/#newsletter"

CAT_ORDER = [
    "Thanh toán",
    "Ngân hàng",
    "Thị trường vốn",
    "Doanh nghiệp",
    "Kinh tế vĩ mô",
    "Bán lẻ, D2C và xu hướng tiêu dùng",
]

CAT_DISPLAY_MAP = {
    "Thanh toán": "Thanh toán số",
    "Ngân hàng": "Ngân hàng",
    "Thị trường vốn": "Thị trường vốn",
    "Doanh nghiệp": "Doanh nghiệp",
    "Kinh tế vĩ mô": "Kinh tế vĩ mô",
    "Bán lẻ, D2C và xu hướng tiêu dùng": "Bán lẻ & Tiêu dùng",
}


def build_newsletter_html(data: dict) -> str:
    ed_id = data.get("editionId", "ED-20261120-D01")
    ed_date = data.get("editionDate", "20/11/2026")
    day_of_week = data.get("dayOfWeek", "THỨ SÁU")
    session_name = data.get("sessionName", "PHIÊN SÁNG")
    raw_ed_num = data.get("editionNumber", "35")

    ed_badge_str = str(raw_ed_num).strip()
    if not ed_badge_str.upper().startswith("ẤN BẢN"):
        ed_badge_str = f"ẤN BẢN SỐ {ed_badge_str}"

    session_display = session_name if ed_date in session_name else f"{session_name} ngày {ed_date}"

    es = data.get("editorialSections", {})
    cover = es.get("sec02_coverStory", {})
    synthesis = cover.get("editorialSynthesis", "")
    lead_hl = cover.get("editorialHeadline", "TỔNG QUAN PHIÊN GIAO DỊCH")
    lead_dek = cover.get("dek", "")

    lead_sapo = (
        cover.get("executiveSummary")
        or cover.get("editorialSummary3Sentences")
        or cover.get("summary")
        or ""
    )
    lead_quote = cover.get("supportingQuote", "")
    lead_img = cover.get("imageUrl", "") or cover.get("leadArticle", {}).get("imageUrl", "")

    # Parse 4 synthesis items [1]..[4]
    synth_items = []
    if synthesis:
        pattern = r'\(([1-4])\)\s*(.*?)(?=\s*\([1-4]\)|$)'
        matches = re.findall(pattern, synthesis, re.DOTALL)
        if matches:
            for num, txt in matches:
                clean_txt = txt.strip().rstrip(";.")
                synth_items.append((num, clean_txt))
        else:
            sents = [s.strip() for s in re.split(r'(?<=[.!?])\s+', synthesis) if s.strip()]
            for idx, s in enumerate(sents[:4]):
                synth_items.append((str(idx + 1), s))

    # Market Pulse: 4 cards
    raw_mp = data.get("marketPulseSnapshot", [])
    if isinstance(raw_mp, dict):
        raw_mp = raw_mp.get("cards", [])
    mp_cards = raw_mp[:4]

    # News list grouped across all 6 V4.0 categories
    news_list = data.get("eligibleNewsList", [])
    total_news = len(news_list)

    cats = {}
    for n in news_list:
        c = n.get("category", "Doanh nghiệp")
        cats.setdefault(c, []).append(n)

    featured_blocks = []
    for c_key in CAT_ORDER:
        items = cats.get(c_key, [])
        if items:
            display_name = CAT_DISPLAY_MAP.get(c_key, c_key)
            featured_blocks.append(
                _render_featured_category_block(display_name, items[:1], len(items))
            )

    featured_count = len(featured_blocks)
    remaining_news = max(0, total_news - featured_count)

    # Render synthesis rows (V4.0 clean hairline rows)
    synth_html = ""
    for idx, (num, txt) in enumerate(synth_items):
        num_fmt = f"0{num}" if len(str(num)) == 1 else str(num)
        border_bottom = "border-bottom: 1px solid #E5E7EB;" if idx < len(synth_items) - 1 else ""
        synth_html += f"""
        <tr>
          <td style="padding: 10px 0; {border_bottom} vertical-align: top;">
            <table border="0" cellpadding="0" cellspacing="0" width="100%">
              <tr>
                <td width="30" style="vertical-align: top; font-family: 'JetBrains Mono', 'SF Mono', Menlo, Consolas, monospace; font-size: 12px; font-weight: 700; color: #0A3D7A; padding-top: 2px; font-variant-numeric: tabular-nums;">
                  {escape(num_fmt)}
                </td>
                <td style="font-size: 13px; line-height: 1.55; color: #374151;">
                  {escape(txt)}
                </td>
              </tr>
            </table>
          </td>
        </tr>
        """

    lead_image_block = ""
    if lead_img:
        lead_image_block = f"""
        <tr>
          <td style="padding: 0 24px 16px 24px;">
            <a href="{SITE_BASE_URL}" target="_blank" style="display: block; text-decoration: none;">
              <div style="border-radius: 4px; overflow: hidden; border: 1px solid #E5E7EB; background-color: #F8FAFC;">
                <img src="{escape(lead_img)}" alt="{escape(lead_hl)}" width="552" class="hero-img" style="width: 100%; max-width: 552px; height: auto; aspect-ratio: 16/9; object-fit: cover; display: block;" />
              </div>
            </a>
          </td>
        </tr>
        """

    html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta http-equiv="X-UA-Compatible" content="IE=edge" />
  <meta name="referrer" content="no-referrer" />
  <title>Bnews | FinTech Intelligence · {escape(ed_badge_str)} ({escape(ed_date)})</title>
  <link rel="icon" type="image/svg+xml" href="/fintech-intelligence/fintech-favicon.svg" />
  <link rel="icon" type="image/png" sizes="32x32" href="/fintech-intelligence/fintech-favicon-32.png" />
  <link rel="shortcut icon" href="/fintech-intelligence/fintech-favicon.ico" />
  <link href="https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;600;700&display=swap" rel="stylesheet" />
  <style type="text/css">
    body, table, td, a {{ -webkit-text-size-adjust: 100%; -ms-text-size-adjust: 100%; }}
    table, td {{ mso-table-lspace: 0pt; mso-table-rspace: 0pt; }}
    img {{ -ms-interpolation-mode: bicubic; border: 0; height: auto; line-height: 100%; outline: none; text-decoration: none; }}
    body {{ margin: 0; padding: 0; width: 100% !important; background-color: #F8FAFC; font-family: 'Be Vietnam Pro', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif; color: #111827; }}

    @media only screen and (max-width: 620px) {{
      .main-container {{ width: 100% !important; max-width: 100% !important; border-left: none !important; border-right: none !important; border-radius: 0 !important; }}
      .pad-mobile {{ padding-left: 16px !important; padding-right: 16px !important; }}
      .stack-col {{ display: block !important; width: 100% !important; max-width: 100% !important; text-align: left !important; padding-bottom: 8px !important; }}
      .mp-col {{ display: block !important; width: 100% !important; max-width: 100% !important; margin-bottom: 10px !important; box-sizing: border-box !important; }}
      .mp-spacer {{ display: none !important; height: 0 !important; }}
      .btn-row {{ display: block !important; width: 100% !important; text-align: left !important; padding-top: 8px !important; }}
      .btn-inline {{ display: inline-block !important; margin-bottom: 6px !important; }}
      .hero-img {{ max-height: 220px !important; }}
      .featured-img {{ max-height: 200px !important; }}
      .nowrap-badge {{ white-space: nowrap !important; }}
    }}
  </style>
</head>
<body style="margin: 0; padding: 0; background-color: #F8FAFC;">

  <!-- PREHEADER -->
  <div style="display: none; font-size: 1px; color: #F8FAFC; line-height: 1px; max-height: 0px; max-width: 0px; opacity: 0; overflow: hidden;">
    {escape(ed_badge_str)} · {escape(ed_date)} — {escape(lead_hl)} | {total_news} tin tức Tài chính &amp; Ngân hàng đã xác minh.
  </div>

  <!-- OUTER WRAPPER -->
  <table border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #F8FAFC;">
    <tr>
      <td align="center" style="padding: 20px 10px;">

        <!-- MAIN CONTAINER (600px MAX-WIDTH, FLAT INSTITUTIONAL V4.0) -->
        <table border="0" cellpadding="0" cellspacing="0" width="600" class="main-container" style="max-width: 600px; width: 100%; background-color: #FFFFFF; border: 1px solid #E5E7EB; border-top: 3px solid #0A3D7A; border-radius: 4px; overflow: hidden;">

          <!-- 1. V4.0 INSTITUTIONAL MASTHEAD -->
          <tr>
            <td style="background-color: #FFFFFF; padding: 18px 24px; border-bottom: 1px solid #E5E7EB;" class="pad-mobile">
              <table border="0" cellpadding="0" cellspacing="0" width="100%">
                <tr>
                  <td class="stack-col" style="vertical-align: middle;">
                    <div style="font-family: 'JetBrains Mono', 'SF Mono', Menlo, Consolas, monospace; font-size: 10px; font-weight: 600; letter-spacing: 0.9px; color: #6B7280; text-transform: uppercase; margin-bottom: 5px;">
                      FINTECH INTELLIGENCE · {escape(day_of_week)}, {escape(ed_date)}
                    </div>
                    <div style="font-size: 20px; font-weight: 800; color: #152C49; letter-spacing: -0.4px; line-height: 1.15; white-space: nowrap;">
                      Bnews <span style="font-weight: 400; color: #AD1935; margin: 0 4px;">|</span> <span style="font-weight: 600; color: #111827; font-size: 15px; letter-spacing: 0;">BẢN TIN TÀI CHÍNH</span>
                    </div>
                  </td>
                  <td class="stack-col" align="right" style="vertical-align: middle;">
                    <div style="display: inline-block; background-color: #EFF6FF; border: 1px solid #BFDBFE; color: #0A3D7A; padding: 5px 10px; border-radius: 3px; font-family: 'JetBrains Mono', 'SF Mono', Menlo, Consolas, monospace; font-size: 10px; font-weight: 700; letter-spacing: 0.5px; text-transform: uppercase; white-space: nowrap;">
                      {escape(ed_badge_str)}
                    </div>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- 2. ACTION BAR (SLATE UTILITY STRIP) -->
          <tr>
            <td style="background-color: #F8FAFC; padding: 10px 24px; border-bottom: 1px solid #E5E7EB;" class="pad-mobile">
              <table border="0" cellpadding="0" cellspacing="0" width="100%">
                <tr>
                  <td class="stack-col" style="font-size: 11px; color: #374151; font-weight: 500; vertical-align: middle; line-height: 1.4;">
                    <strong style="color: #111827;">{escape(session_display)}</strong> · <span style="font-family: 'JetBrains Mono', monospace; color: #0A3D7A; font-weight: 700; font-variant-numeric: tabular-nums;">{total_news}</span> tin xác minh 0–24h
                  </td>
                  <td class="btn-row" align="right" style="vertical-align: middle; white-space: nowrap;">
                    <a href="{SUBSCRIBE_URL}" target="_blank" class="btn-inline" style="display: inline-block; background-color: #FFFFFF; color: #0A3D7A; border: 1px solid #0A3D7A; font-size: 10px; font-weight: 700; padding: 6px 10px; border-radius: 3px; text-decoration: none; letter-spacing: 0.3px; margin-right: 6px;">
                      + ĐĂNG KÝ
                    </a>
                    <a href="{SITE_BASE_URL}" target="_blank" class="btn-inline" style="display: inline-block; background-color: #0A3D7A; color: #FFFFFF; border: 1px solid #0A3D7A; font-size: 10px; font-weight: 700; padding: 6px 11px; border-radius: 3px; text-decoration: none; letter-spacing: 0.3px;">
                      XEM TRÊN BNEWS ↗
                    </a>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- 3. COVER STORY (TIÊU ĐIỂM PHIÊN) -->
          <tr>
            <td style="padding: 22px 24px 10px 24px;" class="pad-mobile">
              <div style="font-family: 'JetBrains Mono', 'SF Mono', Menlo, Consolas, monospace; font-size: 10px; font-weight: 700; color: #C8102E; text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 8px;">
                TIÊU ĐIỂM PHIÊN · COVER STORY
              </div>
              <h1 style="margin: 0 0 8px 0; font-size: 21px; line-height: 1.32; font-weight: 800; color: #111827; letter-spacing: -0.3px;">
                <a href="{SITE_BASE_URL}" target="_blank" style="color: #111827; text-decoration: none;">
                  {escape(lead_hl)}
                </a>
              </h1>
              {f'<p style="margin: 0 0 12px 0; font-size: 13px; line-height: 1.5; color: #4B5563;">{escape(lead_dek)}</p>' if lead_dek else ''}
            </td>
          </tr>

          <!-- 3B. COVER IMAGE -->
          {lead_image_block}

          <!-- 3C. EXECUTIVE SUMMARY BOX (FLAT V4.0 SURFACE) -->
          <tr>
            <td style="padding: 0 24px 16px 24px;" class="pad-mobile">
              <table border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #F8FAFC; border: 1px solid #E5E7EB; border-radius: 4px;">
                <tr>
                  <td style="padding: 13px 16px;">
                    <div style="font-family: 'JetBrains Mono', 'SF Mono', Menlo, Consolas, monospace; font-size: 10px; font-weight: 700; color: #0A3D7A; text-transform: uppercase; letter-spacing: 0.6px; margin-bottom: 5px;">
                      TÓM TẮT ĐIỀU HÀNH
                    </div>
                    <div style="font-size: 13px; line-height: 1.6; color: #111827;">
                      {escape(lead_sapo)}
                    </div>
                    {f'<div style="margin-top: 8px; padding-top: 8px; border-top: 1px solid #E5E7EB; font-size: 12px; font-style: italic; color: #4B5563; line-height: 1.45;">“{escape(lead_quote)}”</div>' if lead_quote else ''}
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- 4. 4 SYNTHESIS HIGHLIGHTS -->
          <tr>
            <td style="padding: 0 24px 20px 24px;" class="pad-mobile">
              <div style="font-family: 'JetBrains Mono', 'SF Mono', Menlo, Consolas, monospace; font-size: 10px; font-weight: 700; color: #0A3D7A; text-transform: uppercase; letter-spacing: 0.7px; padding-bottom: 8px; border-bottom: 1px solid #E5E7EB;">
                04 ĐIỂM NHẤN TỔNG HỢP
              </div>
              <table border="0" cellpadding="0" cellspacing="0" width="100%">
                {synth_html}
              </table>
            </td>
          </tr>

          <!-- DIVIDER -->
          <tr>
            <td style="padding: 0 24px;" class="pad-mobile">
              <div style="height: 1px; background-color: #E5E7EB;"></div>
            </td>
          </tr>

          <!-- 5. MARKET PULSE SNAPSHOT (2x2 TABLE GRID) -->
          <tr>
            <td style="padding: 20px 24px 16px 24px; background-color: #F8FAFC;" class="pad-mobile">
              <table border="0" cellpadding="0" cellspacing="0" width="100%" style="margin-bottom: 12px;">
                <tr>
                  <td style="border-left: 3px solid #0A3D7A; padding-left: 9px;">
                    <div style="font-size: 14px; font-weight: 800; color: #111827; letter-spacing: -0.2px;">
                      NHỊP ĐẬP THỊ TRƯỜNG
                    </div>
                  </td>
                  <td align="right" style="font-family: 'JetBrains Mono', monospace; font-size: 10px; color: #6B7280; font-weight: 600;">
                    MARKET PULSE
                  </td>
                </tr>
              </table>

              <table border="0" cellpadding="0" cellspacing="0" width="100%">
                <tr>
                  {_render_pulse_cell(mp_cards, 0)}
                  <td class="mp-spacer" width="4%" style="width: 4%;">&nbsp;</td>
                  {_render_pulse_cell(mp_cards, 1)}
                </tr>
                <tr><td colspan="3" height="12" style="font-size: 0; line-height: 0;">&nbsp;</td></tr>
                <tr>
                  {_render_pulse_cell(mp_cards, 2)}
                  <td class="mp-spacer" width="4%" style="width: 4%;">&nbsp;</td>
                  {_render_pulse_cell(mp_cards, 3)}
                </tr>
              </table>
            </td>
          </tr>

          <!-- DIVIDER -->
          <tr>
            <td style="padding: 0 24px;" class="pad-mobile">
              <div style="height: 1px; background-color: #E5E7EB;"></div>
            </td>
          </tr>

          <!-- 6. FEATURED CATEGORY HIGHLIGHTS (6 V4.0 CATEGORIES) -->
          <tr>
            <td style="padding: 20px 24px 8px 24px;" class="pad-mobile">
              <table border="0" cellpadding="0" cellspacing="0" width="100%" style="margin-bottom: 14px;">
                <tr>
                  <td style="border-left: 3px solid #0A3D7A; padding-left: 9px;">
                    <div style="font-size: 14px; font-weight: 800; color: #111827; letter-spacing: -0.2px;">
                      TIN TIÊU BIỂU THEO CHUYÊN MỤC
                    </div>
                  </td>
                  <td align="right" style="font-family: 'JetBrains Mono', monospace; font-size: 10px; color: #6B7280; font-weight: 600; font-variant-numeric: tabular-nums;">
                    {featured_count}/{total_news} TIN CHỌN LỌC
                  </td>
                </tr>
              </table>

              {''.join(featured_blocks)}
            </td>
          </tr>

          <!-- 7. REMAINING NEWS CTA BANNER -->
          <tr>
            <td style="padding: 8px 24px 20px 24px;" class="pad-mobile">
              <table border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #F8FAFC; border: 1px solid #E5E7EB; border-radius: 4px;">
                <tr>
                  <td align="center" style="padding: 20px 18px;">
                    <div style="font-family: 'JetBrains Mono', monospace; font-size: 10px; font-weight: 700; color: #0A3D7A; letter-spacing: 0.6px; text-transform: uppercase; margin-bottom: 5px;">
                      TOÀN CẢNH {escape(ed_badge_str)}
                    </div>
                    <div style="font-size: 14px; font-weight: 700; color: #111827; margin-bottom: 6px;">
                      Còn {remaining_news} bản tin chuyên sâu &amp; Radar Chú ý trên Bnews
                    </div>
                    <div style="font-size: 12px; color: #4B5563; line-height: 1.5; margin-bottom: 14px;">
                      Đọc đầy đủ {total_news} tin tức đã xác minh từ nguồn chính thống cùng phân tích tác động B2B trên giao diện Bnews V4.0.
                    </div>
                    <a href="{SITE_BASE_URL}" target="_blank" style="display: inline-block; background-color: #0A3D7A; color: #FFFFFF; font-size: 12px; font-weight: 700; padding: 11px 22px; border-radius: 4px; text-decoration: none; letter-spacing: 0.3px;">
                      XEM ĐẦY ĐỦ {total_news} TIN TRÊN BNEWS ↗
                    </a>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- 8. COMMUNITY SUBSCRIBE BANNER (V4.0 NAVY CTA) -->
          <tr>
            <td style="padding: 0 24px 22px 24px;" class="pad-mobile">
              <table border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #0A3D7A; border-radius: 4px;">
                <tr>
                  <td align="center" style="padding: 22px 20px;">
                    <div style="font-family: 'JetBrains Mono', monospace; font-size: 10px; font-weight: 700; color: #BFDBFE; letter-spacing: 0.8px; text-transform: uppercase; margin-bottom: 6px;">
                      NHẬN BẢN TIN MỖI SÁNG
                    </div>
                    <div style="font-size: 16px; font-weight: 800; color: #FFFFFF; line-height: 1.35; margin-bottom: 6px;">
                      Đồng bộ nhịp đập Tài chính – Ngân hàng – Thanh toán
                    </div>
                    <div style="font-size: 12px; color: #E2E8F0; line-height: 1.5; margin-bottom: 16px;">
                      Tổng hợp lúc 07:30 sáng mỗi ngày · Hoàn toàn miễn phí · Hủy đăng ký bất kỳ lúc nào.
                    </div>
                    <a href="{SUBSCRIBE_URL}" target="_blank" style="display: inline-block; background-color: #FFFFFF; color: #0A3D7A; font-size: 12px; font-weight: 700; padding: 10px 22px; border-radius: 4px; text-decoration: none; letter-spacing: 0.3px;">
                      ĐĂNG KÝ NHẬN BẢN TIN →
                    </a>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- 9. INSTITUTIONAL FOOTER -->
          <tr>
            <td style="background-color: #F8FAFC; border-top: 1px solid #E5E7EB; padding: 16px 24px; text-align: center;" class="pad-mobile">
              <div style="font-size: 12px; font-weight: 700; color: #111827; margin-bottom: 4px;">
                BNEWS · FINTECH INTELLIGENCE
              </div>
              <div style="font-family: 'JetBrains Mono', monospace; font-size: 10px; color: #6B7280; margin-bottom: 10px;">
                {escape(ed_id)} · {escape(ed_date)} · {total_news} bản tin xác minh 0–24h
              </div>
              <div style="font-size: 11px; color: #6B7280; line-height: 1.5;">
                <a href="{SITE_BASE_URL}" target="_blank" style="color: #0A3D7A; text-decoration: none; font-weight: 600;">Trang chủ Bnews</a>
                &nbsp;·&nbsp;
                <a href="{SUBSCRIBE_URL}" target="_blank" style="color: #0A3D7A; text-decoration: none; font-weight: 600;">Đăng ký nhận tin</a>
                &nbsp;·&nbsp;
                <a href="https://www.linkedin.com/in/bryan-nguyen-796a7b1ab/" target="_blank" style="color: #0A3D7A; text-decoration: none; font-weight: 600;">LinkedIn</a>
                &nbsp;·&nbsp;
                <a href="https://zalo.me/0838673639" target="_blank" style="color: #0A3D7A; text-decoration: none; font-weight: 600;">Zalo</a>
              </div>
              <div style="margin-top: 10px; font-size: 10px; color: #9CA3AF;">
                © 2026 Bryan Nguyen FinTech Intelligence. Tổng hợp từ nguồn báo chí chính thống Việt Nam &amp; quốc tế.
              </div>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>

</body>
</html>"""
    return html


def _render_pulse_cell(cards: list, idx: int) -> str:
    if idx >= len(cards):
        return '<td class="mp-col" width="48%" style="padding: 0;"></td>'

    card = cards[idx]
    lbl = card.get("shortLabel") or card.get("label", f"CHỈ SỐ 0{idx+1}")
    val_raw = str(card.get("value", "--")).strip()
    unit = str(card.get("unit", "")).strip()

    if unit and unit.lower() not in val_raw.lower() and not val_raw.endswith(unit):
        val_display = f"{val_raw} {unit}"
    else:
        val_display = val_raw

    compact_delta = str(card.get("compactDelta", "")).strip()
    status = str(card.get("status", "neutral")).lower()
    if status == "positive":
        badge_bg, badge_fg = "#F0FDF4", "#15803D"
    elif status == "negative":
        badge_bg, badge_fg = "#FEF2F2", "#C8102E"
    else:
        badge_bg, badge_fg = "#EFF6FF", "#0A3D7A"

    badge_text = compact_delta if compact_delta else "ĐÃ XÁC MINH"
    ref_val = card.get("referenceValue", "")
    period = card.get("observationDate") or card.get("dataPeriod") or card.get("asOf", "")
    url = card.get("sourceUrl", SITE_BASE_URL)
    article_title = card.get("articleTitle", "")

    return f"""
    <td class="mp-col" width="48%" style="background-color: #FFFFFF; border: 1px solid #E5E7EB; border-top: 2px solid #0A3D7A; border-radius: 4px; padding: 12px 14px; vertical-align: top;">
      <table border="0" cellpadding="0" cellspacing="0" width="100%" style="height: 100%;">
        <tr>
          <td style="vertical-align: top;">
            <table border="0" cellpadding="0" cellspacing="0" width="100%" style="margin-bottom: 6px;">
              <tr>
                <td style="font-family: 'JetBrains Mono', 'SF Mono', monospace; font-size: 10px; font-weight: 700; color: #374151; text-transform: uppercase;">
                  {escape(lbl)}
                </td>
                <td align="right" style="white-space: nowrap; padding-left: 6px;">
                  <span style="display: inline-block; background-color: {badge_bg}; color: {badge_fg}; font-family: 'JetBrains Mono', 'SF Mono', monospace; font-size: 9px; font-weight: 700; padding: 2px 6px; border-radius: 2px; font-variant-numeric: tabular-nums;">
                    {escape(badge_text)}
                  </span>
                </td>
              </tr>
            </table>

            <div style="font-family: 'JetBrains Mono', 'SF Mono', Menlo, Consolas, monospace; font-size: 19px; font-weight: 700; color: #111827; line-height: 1.2; margin-bottom: 4px; font-variant-numeric: tabular-nums;">
              {escape(val_display)}
            </div>

            {f'<div style="font-size: 10px; color: #6B7280; margin-bottom: 6px; font-weight: 500;">{escape(period)}</div>' if period else ''}

            <div style="font-size: 11px; color: #374151; line-height: 1.45; margin-bottom: 6px;">
              {escape(ref_val[:110])}{'...' if len(ref_val) > 110 else ''}
            </div>

            {f'<div style="font-size: 11px; color: #0A3D7A; font-weight: 600; margin-bottom: 4px; line-height: 1.35;">{escape(article_title[:60])}{"..." if len(article_title) > 60 else ""}</div>' if article_title else ''}
          </td>
        </tr>
        <tr>
          <td style="vertical-align: bottom; padding-top: 8px; border-top: 1px solid #F3F4F6;">
            <a href="{escape(url)}" target="_blank" style="font-size: 10px; font-family: 'JetBrains Mono', monospace; font-weight: 700; color: #0A3D7A; text-decoration: none;">
              CHI TIẾT &amp; NGUỒN →
            </a>
          </td>
        </tr>
      </table>
    </td>
    """


def _render_featured_category_block(cat_display_name: str, items: list, cat_total: int) -> str:
    if not items:
        return ""

    items_html = []
    for item in items:
        eid = item.get("eventId", "")
        hl = item.get("headline", "")
        sm = item.get("summary", "")
        src = item.get("sourceName", "Báo chí")
        url = item.get("sourceUrl", "#")
        fintech_lens = item.get("sectionE_fintechLens", "")
        quote = item.get("supportingQuote", "")
        img_url = item.get("imageUrl", "")

        img_banner_html = ""
        if img_url:
            img_banner_html = f"""
            <div style="margin: 10px 0 12px 0; border-radius: 4px; overflow: hidden; border: 1px solid #E5E7EB; background-color: #F8FAFC;">
              <a href="{escape(url)}" target="_blank" style="display: block; text-decoration: none;">
                <img src="{escape(img_url)}" alt="{escape(hl)}" width="100%" class="featured-img" style="width: 100%; max-width: 100%; height: auto; max-height: 220px; aspect-ratio: 16/9; object-fit: cover; display: block;" onerror="this.parentElement.parentElement.style.display='none'" />
              </a>
            </div>
            """

        items_html.append(f"""
        <table border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 4px; margin-bottom: 14px;">
          <tr>
            <td style="padding: 14px 16px;">
              <!-- META ROW -->
              <table border="0" cellpadding="0" cellspacing="0" width="100%" style="margin-bottom: 6px;">
                <tr>
                  <td style="vertical-align: middle;">
                    <span style="font-family: 'JetBrains Mono', 'SF Mono', monospace; font-size: 10px; font-weight: 700; background-color: #EFF6FF; color: #0A3D7A; border: 1px solid #DBEAFE; padding: 2px 6px; border-radius: 2px; white-space: nowrap;">
                      {escape(eid)}
                    </span>
                    <span style="font-size: 11px; color: #6B7280; margin-left: 6px;">
                      <strong style="color: #111827;">{escape(src)}</strong>
                    </span>
                  </td>
                  <td align="right" style="vertical-align: middle; white-space: nowrap; padding-left: 8px;">
                    <span class="nowrap-badge" style="font-family: 'JetBrains Mono', monospace; font-size: 10px; font-weight: 600; color: #6B7280;">
                      0–24H
                    </span>
                  </td>
                </tr>
              </table>

              {img_banner_html}

              <!-- HEADLINE -->
              <div style="font-size: 15px; font-weight: 700; color: #111827; line-height: 1.4; margin-bottom: 6px;">
                <a href="{escape(url)}" target="_blank" style="color: #111827; text-decoration: none;">
                  {escape(hl)}
                </a>
              </div>

              <!-- SUMMARY -->
              <div style="font-size: 13px; color: #374151; line-height: 1.55; margin-bottom: 10px;">
                {escape(sm)}
              </div>

              <!-- FINTECH LENS (FLAT V4.0 BOX) -->
              {f'''
              <div style="background-color: #F8FAFC; border: 1px solid #E5E7EB; border-radius: 3px; padding: 9px 11px; font-size: 12px; color: #374151; line-height: 1.5; margin-bottom: 8px;">
                <strong style="color: #0A3D7A;">Góc nhìn FinTech &amp; B2B:</strong> {escape(fintech_lens)}
              </div>
              ''' if fintech_lens else ''}

              {f'''
              <div style="font-size: 11px; font-style: italic; color: #6B7280; line-height: 1.45; margin-bottom: 8px;">
                “{escape(quote)}”
              </div>
              ''' if quote else ''}

              <div style="text-align: right; padding-top: 4px;">
                <a href="{escape(url)}" target="_blank" style="font-size: 10px; font-family: 'JetBrains Mono', monospace; font-weight: 700; color: #0A3D7A; text-decoration: none;">
                  XEM NGUỒN BÁO GỐC ↗
                </a>
              </div>
            </td>
          </tr>
        </table>
        """)

    return f"""
    <div style="margin-bottom: 16px;">
      <table border="0" cellpadding="0" cellspacing="0" width="100%" style="margin-bottom: 8px;">
        <tr>
          <td style="border-left: 3px solid #0A3D7A; padding-left: 8px; font-size: 12px; font-weight: 700; color: #111827; text-transform: uppercase; letter-spacing: 0.4px;">
            {escape(cat_display_name)}
          </td>
          <td align="right" style="font-family: 'JetBrains Mono', monospace; font-size: 10px; color: #6B7280; font-variant-numeric: tabular-nums;">
            {cat_total} bản tin
          </td>
        </tr>
      </table>
      {''.join(items_html)}
    </div>
    """


def main():
    if not os.path.exists(SOURCE_JSON):
        print(f"Error: {SOURCE_JSON} not found!")
        sys.exit(1)

    with open(SOURCE_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    html_content = build_newsletter_html(data)

    for target_path in OUT_TARGETS:
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"Successfully synced: {target_path} ({len(html_content):,} bytes)")


if __name__ == "__main__":
    main()
