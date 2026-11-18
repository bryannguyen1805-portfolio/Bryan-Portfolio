#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_daily_newsletter_email.py
-----------------------------------------------------------------------------
BRYAN FINTECH INTELLIGENCE — DAILY EMAIL NEWSLETTER GENERATOR (V1.2 PREVIEW)
Đặc trưng thiết kế:
- Thừa hưởng 100% DNA thiết kế MagSpread độc bản của Bryan News:
  + Nền giấy kem ấm áp: #FDF2E9 (Warm Cream)
  + Màu chủ đạo: #134E4A (Deep Teal) và điểm nhấn đỏ báo chí #BE123C (Rose Accent)
  + Font chữ hiện đại: 'Be Vietnam Pro', -apple-system, Segoe UI, Roboto, Arial
  + Đổi toàn bộ "Web App" -> "Bnews".
  + Các bảng Market Pulse đồng đều, ngang hàng 100%.
  + LOẠI BỎ 100% EMOJI 4-BYTE: Thay toàn bộ bằng ký tự chuẩn BMP '■' và '+' 
    đảm bảo KHÔNG BAO GIỜ bị lỗi font ô vuông hỏi chấm () trên Gmail & Mobile.
  + Chuẩn hóa độ rộng 600px tối ưu hiển thị Mobile.
  + Tối ưu phân cấp thị giác nút bấm: Nút chính đọc tin (Đỏ mận), Nút phụ Subscribe (Deep Teal).
-----------------------------------------------------------------------------
"""

import os
import sys
import json
import re
from datetime import datetime
from html import escape

WORKSPACE_ROOT = "/Users/quangtri/Documents/Bryan-Portfolio-Antigravity"
SOURCE_JSON = os.path.join(WORKSPACE_ROOT, "fintech-intelligence", "edition-data.json")
OUT_PREVIEW_PILOT = os.path.join(WORKSPACE_ROOT, "pilot-output", "newsletter-preview.html")
OUT_PREVIEW_WEB = os.path.join(WORKSPACE_ROOT, "fintech-intelligence", "preview", "newsletter-preview.html")

def build_newsletter_html(data: dict) -> str:
    ed_id = data.get("editionId", "ED-20261116-D01")
    ed_date = data.get("editionDate", "16/11/2026")
    day_of_week = data.get("dayOfWeek", "THỨ HAI")
    session_name = data.get("sessionName", "ẤN BẢN ĐẦU TUẦN")
    raw_ed_num = data.get("editionNumber", "31")

    # Clean edition badge
    ed_badge_str = str(raw_ed_num).strip()
    if not ed_badge_str.upper().startswith("ẤN BẢN"):
        ed_badge_str = f"ẤN BẢN SỐ {ed_badge_str}"

    es = data.get("editorialSections", {})
    cover = es.get("sec02_coverStory", {})
    synthesis = cover.get("editorialSynthesis", "")
    lead_hl = cover.get("editorialHeadline", "TỔNG QUAN PHIÊN GIAO DỊCH")
    lead_dek = cover.get("dek", "")
    
    # 1. Tóm tắt cốt lõi
    lead_sapo = (
        cover.get("executiveSummary")
        or cover.get("editorialSummary3Sentences")
        or cover.get("summary")
        or ""
    )
    lead_quote = cover.get("supportingQuote", "")
    lead_img = cover.get("imageUrl", "") or cover.get("leadArticle", {}).get("imageUrl", "")

    # 2. Parse 4 synthesis items [1], [2], [3], [4] with nested parentheses support
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

    # 3. Market Pulse: 4 cards matching the website exactly
    raw_mp = data.get("marketPulseSnapshot", [])
    if isinstance(raw_mp, dict):
        raw_mp = raw_mp.get("cards", [])
    mp_cards = raw_mp[:4]

    # 4. News list: Filter to representative/featured news (1 per category)
    news_list = data.get("eligibleNewsList", [])
    cats = {}
    for n in news_list:
        c = n.get("category", "Doanh nghiệp")
        cats.setdefault(c, []).append(n)

    cat_order = ["Ngân hàng", "Thị trường vốn", "Bán lẻ, D2C và xu hướng tiêu dùng", "Thanh toán", "Doanh nghiệp"]
    featured_news_by_cat = {}
    for cat_name in cat_order:
        if cat_name in cats and cats[cat_name]:
            featured_news_by_cat[cat_name] = cats[cat_name][:1]

    # HTML Generator with 600px width for bulletproof mobile responsiveness
    html = f"""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="vi">
<head>
  <meta charset="UTF-8" />
  <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Bnews FinTech Intelligence — {escape(ed_badge_str)} ({escape(ed_date)})</title>
  <style type="text/css">
    body, table, td, p, a, li, blockquote {{ -webkit-text-size-adjust: 100%; -ms-text-size-adjust: 100%; }}
    table, td {{ mso-table-lspace: 0pt; mso-table-rspace: 0pt; }}
    img {{ -ms-interpolation-mode: bicubic; border: 0; height: auto; line-height: 100%; outline: none; text-decoration: none; }}
    @media only screen and (max-width: 620px) {{
      .email-container {{ width: 100% !important; max-width: 100% !important; }}
      .mp-col {{ display: block !important; width: 100% !important; box-sizing: border-box !important; margin-bottom: 12px !important; }}
      .mp-spacer {{ display: none !important; }}
      .mobile-padding {{ padding-left: 14px !important; padding-right: 14px !important; }}
      .mobile-p-top {{ padding-top: 16px !important; }}
      .cover-title {{ font-size: 19px !important; line-height: 1.35 !important; }}
      .header-title {{ font-size: 21px !important; }}
      .hide-mobile {{ display: none !important; }}
      .stack-mobile {{ display: block !important; width: 100% !important; box-sizing: border-box !important; }}
      .action-table {{ width: 100% !important; margin-top: 10px !important; }}
      .action-btn {{ display: block !important; width: 100% !important; text-align: center !important; margin-bottom: 6px !important; box-sizing: border-box !important; }}
      .featured-img {{ width: 100% !important; max-width: 100% !important; height: auto !important; aspect-ratio: 16/9 !important; max-height: 220px !important; object-fit: cover !important; display: block !important; }}
      .nowrap-badge {{ white-space: nowrap !important; }}
    }}
  </style>
</head>
<body style="margin: 0; padding: 0; background-color: #FDF2E9; font-family: 'Be Vietnam Pro', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #1C1917; -webkit-font-smoothing: antialiased; line-height: 1.5;">

  <!-- PREVIEW TEXT (HIDDEN IN EMAIL CLIENTS) -->
  <div style="display: none; font-size: 1px; color: #FDF2E9; line-height: 1px; max-height: 0px; max-width: 0px; opacity: 0; overflow: hidden;">
    Bnews Bản tin tài chính & ngân hàng ngày {escape(ed_date)}: Đúc kết 4 chuyển động lớn, 4 chỉ số Market Pulse và tiêu điểm 25 sự kiện xác minh.
  </div>

  <!-- MAIN EMAIL CONTAINER (600px standard for bulletproof email rendering) -->
  <table border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #FDF2E9; padding: 16px 4px;">
    <tr>
      <td align="center">
        <table class="email-container" border="0" cellpadding="0" cellspacing="0" width="600" style="max-width: 600px; width: 100%; background-color: #FFFFFF; border: 1px solid #E7E5E4; box-shadow: 0 4px 16px rgba(19, 78, 74, 0.06);">
          
          <!-- TOP MASTHEAD HEADER -->
          <tr>
            <td class="mobile-padding" style="background-color: #134E4A; padding: 22px 24px; border-bottom: 3px solid #BE123C;">
              <table border="0" cellpadding="0" cellspacing="0" width="100%">
                <tr>
                  <td class="stack-mobile" style="vertical-align: middle;">
                    <div style="font-family: 'SF Mono', Menlo, Consolas, monospace; font-size: 10px; text-transform: uppercase; letter-spacing: 1.5px; color: #F7EBE0; margin-bottom: 4px;">
                      FINTECH & FINANCIAL INTELLIGENCE • {escape(day_of_week)}, {escape(ed_date)}
                    </div>
                    <div class="header-title" style="font-size: 22px; font-weight: 800; color: #FFFFFF; letter-spacing: -0.5px; line-height: 1.2;">
                      BNEWS <span style="font-weight: 300; opacity: 0.85;">| BẢN TIN TÀI CHÍNH</span>
                    </div>
                  </td>
                  <td class="stack-mobile" align="right" style="vertical-align: middle;">
                    <span style="display: inline-block; background-color: #0F3D3A; color: #FFFFFF; font-family: 'SF Mono', monospace; font-size: 10px; font-weight: 700; padding: 5px 10px; border: 1px solid #2DD4BF; border-radius: 2px; margin-top: 6px;">
                      {escape(ed_badge_str)}
                    </span>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- BNEWS TOP ACTION BAR (RESPONSIVE BUTTONS) -->
          <tr>
            <td class="mobile-padding" style="background-color: #F7EBE0; padding: 10px 24px; border-bottom: 1px solid #E7E5E4;">
              <table border="0" cellpadding="0" cellspacing="0" width="100%">
                <tr>
                  <td class="stack-mobile" style="font-size: 12px; color: #44403C; font-weight: 500; vertical-align: middle; padding: 4px 0;">
                    Phiên: <strong>{escape(session_name)}</strong> • 25 Tin xác minh 0–24h
                  </td>
                  <td class="stack-mobile" align="right" style="vertical-align: middle;">
                    <!-- INLINE BUTTONS -->
                    <table class="action-table" border="0" cellpadding="0" cellspacing="0" align="right" style="border-collapse: collapse;">
                      <tr>
                        <td class="action-btn" style="padding-right: 6px;">
                          <a href="https://bryanportfolio.io.vn/fintech-intelligence/#subscribe" target="_blank" style="display: inline-block; background-color: #BE123C; color: #FFFFFF; text-decoration: none; font-size: 11px; font-weight: 700; padding: 6px 12px; border-radius: 2px; text-transform: uppercase; letter-spacing: 0.3px; white-space: nowrap;">
                            + ĐĂNG KÝ (SUBSCRIBE)
                          </a>
                        </td>
                        <td class="action-btn">
                          <a href="https://bryanportfolio.io.vn/fintech-intelligence/" target="_blank" style="display: inline-block; background-color: #134E4A; color: #FFFFFF; text-decoration: none; font-size: 11px; font-weight: 700; padding: 6px 12px; border-radius: 2px; text-transform: uppercase; letter-spacing: 0.3px; white-space: nowrap;">
                            XEM TRÊN BNEWS ↗
                          </a>
                        </td>
                      </tr>
                    </table>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- COVER STORY HERO -->
          <tr>
            <td class="mobile-padding" style="padding: 24px 24px 18px 24px;">
              <div style="display: inline-block; background-color: #BE123C; color: #FFFFFF; font-family: 'SF Mono', monospace; font-size: 10px; font-weight: 700; padding: 3px 8px; text-transform: uppercase; letter-spacing: 1px; border-radius: 2px; margin-bottom: 10px;">
                BÀI ĐINH TRANG NHẤT (COVER STORY)
              </div>
              <h1 class="cover-title" style="font-size: 21px; font-weight: 800; color: #1C1917; line-height: 1.35; margin: 0 0 10px 0;">
                {escape(lead_hl)}
              </h1>
              {f'<div style="font-size: 13px; color: #57534E; font-weight: 500; line-height: 1.5; margin-bottom: 14px; font-style: italic;">{escape(lead_dek)}</div>' if lead_dek else ''}
              {f'''
              <div style="margin: 12px 0 16px 0; border-radius: 4px; overflow: hidden; border: 1px solid #E7E5E4; background-color: #F5F5F4;">
                <img src="{escape(lead_img)}" alt="{escape(lead_hl)}" width="100%" class="featured-img" style="width: 100%; max-width: 100%; height: auto; max-height: 280px; aspect-ratio: 16/9; object-fit: cover; display: block;" onerror="this.parentElement.style.display='none'" />
              </div>
              ''' if lead_img else ''}
              
              <!-- SAPO / EXECUTIVE SUMMARY -->
              <div style="font-size: 13px; line-height: 1.6; color: #1C1917; background-color: #FDF2E9; border-left: 3px solid #134E4A; padding: 12px 14px; margin-bottom: 16px; border-radius: 2px;">
                <div style="font-family: 'SF Mono', monospace; font-size: 10px; font-weight: 700; color: #134E4A; text-transform: uppercase; margin-bottom: 4px;">
                  ■ TÓM TẮT CỐT LÕI (EXECUTIVE SUMMARY):
                </div>
                <div>{escape(lead_sapo)}</div>
              </div>

              <!-- SUPPORTING QUOTE -->
              {f'''
              <div style="background-color: #F7EBE0; border: 1px solid #E7E5E4; padding: 12px 14px; margin-bottom: 20px; border-radius: 2px;">
                <div style="font-family: 'SF Mono', monospace; font-size: 10px; font-weight: 700; color: #134E4A; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px;">
                  TRÍCH DẪN NGUYÊN VĂN BÁO CHÍ
                </div>
                <div style="font-size: 13px; font-style: italic; color: #44403C; line-height: 1.5;">
                  “{escape(lead_quote)}”
                </div>
              </div>
              ''' if lead_quote else ''}

              <!-- 4-BOX SYNTHESIS: ĐÚC KẾT TOÀN CẢNH PHIÊN -->
              <div style="border-top: 2px solid #134E4A; padding-top: 16px; margin-bottom: 20px;">
                <table border="0" cellpadding="0" cellspacing="0" width="100%">
                  <tr>
                    <td style="font-family: 'SF Mono', monospace; font-size: 11px; font-weight: 800; color: #134E4A; text-transform: uppercase; letter-spacing: 0.5px;">
                      ■ ĐÚC KẾT TOÀN CẢNH PHIÊN (4 MẠCH CHUYỂN ĐỘNG)
                    </td>
                    <td align="right" style="font-family: 'SF Mono', monospace; font-size: 10px; color: #BE123C; font-weight: 700;">
                      25 SỰ KIỆN XÁC MINH
                    </td>
                  </tr>
                </table>
                <div style="font-size: 12px; color: #57534E; margin: 6px 0 12px 0;">
                  Toàn cảnh phiên {escape(ed_date)} phản ánh bốn mạch chuyển động lớn từ 25 sự kiện xác minh:
                </div>

                <!-- 4 BOXES -->
                <table border="0" cellpadding="0" cellspacing="0" width="100%">
                  {''.join([f'''
                  <tr>
                    <td style="padding-bottom: 8px; vertical-align: top;">
                      <table border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #FDF2E9; border: 1px solid #E7E5E4; border-radius: 2px;">
                        <tr>
                          <td width="32" align="center" style="vertical-align: top; padding: 10px 0 10px 10px;">
                            <span style="display: inline-block; width: 20px; height: 20px; line-height: 20px; text-align: center; background-color: #134E4A; color: #FFFFFF; font-family: 'SF Mono', monospace; font-size: 11px; font-weight: 700; border-radius: 2px;">
                              {item_num}
                            </span>
                          </td>
                          <td style="padding: 10px 12px 10px 8px; font-size: 12px; line-height: 1.5; color: #1C1917;">
                            {escape(item_text)}
                          </td>
                        </tr>
                      </table>
                    </td>
                  </tr>
                  ''' for item_num, item_text in synth_items])}
                </table>
              </div>

            </td>
          </tr>

          <!-- SECTION: MARKET PULSE (4 CORE INDICATORS - GUARANTEED EQUAL HEIGHT) -->
          <tr>
            <td class="mobile-padding" style="background-color: #F7EBE0; padding: 20px 24px; border-top: 1px solid #E7E5E4; border-bottom: 1px solid #E7E5E4;">
              <table border="0" cellpadding="0" cellspacing="0" width="100%" style="margin-bottom: 12px;">
                <tr>
                  <td>
                    <div style="font-family: 'SF Mono', monospace; font-size: 10px; font-weight: 800; color: #BE123C; text-transform: uppercase; letter-spacing: 1px;">
                      MARKET PULSE
                    </div>
                    <div style="font-size: 17px; font-weight: 800; color: #134E4A;">
                      4 NHỊP ĐẬP THỊ TRƯỜNG THEN CHỐT
                    </div>
                  </td>
                  <td align="right">
                    <span style="font-size: 10px; font-family: 'SF Mono', monospace; color: #57534E;">
                      PHIÊN: {escape(ed_date)}
                    </span>
                  </td>
                </tr>
              </table>

              <!-- 2x2 TILES GRID (GUARANTEED EQUAL HEIGHT ACROSS COLUMNS) -->
              <table border="0" cellpadding="0" cellspacing="0" width="100%">
                <!-- ROW 1 -->
                <tr>
                  {_render_pulse_cell(mp_cards, 0)}
                  <td class="mp-spacer" width="12" style="width: 12px; font-size: 1px; line-height: 1px;">&nbsp;</td>
                  {_render_pulse_cell(mp_cards, 1)}
                </tr>
                <tr>
                  <td colspan="3" height="12" style="height: 12px; font-size: 1px; line-height: 1px;">&nbsp;</td>
                </tr>
                <!-- ROW 2 -->
                <tr>
                  {_render_pulse_cell(mp_cards, 2)}
                  <td class="mp-spacer" width="12" style="width: 12px; font-size: 1px; line-height: 1px;">&nbsp;</td>
                  {_render_pulse_cell(mp_cards, 3)}
                </tr>
              </table>
            </td>
          </tr>

          <!-- SECTION: FEATURED HIGHLIGHTS (TÓM LƯỢC CÁC TIN TIÊU BIỂU) -->
          <tr>
            <td class="mobile-padding" style="padding: 22px 24px 18px 24px;">
              <table border="0" cellpadding="0" cellspacing="0" width="100%" style="margin-bottom: 14px; border-bottom: 2px solid #134E4A; padding-bottom: 6px;">
                <tr>
                  <td>
                    <div style="font-size: 17px; font-weight: 800; color: #134E4A;">
                      TIÊU ĐIỂM TIN TỨC CHỌN LỌC (FEATURED HIGHLIGHTS)
                    </div>
                    <div style="font-size: 11px; color: #57534E; margin-top: 2px;">
                      Chọn lọc các sự kiện trọng điểm đại diện 5 ngành • Phân tích góc nhìn FinTech & B2B
                    </div>
                  </td>
                </tr>
              </table>

              <!-- FEATURED NEWS ITEMS -->
              {''.join([_render_featured_category_block(cat_name, featured_news_by_cat[cat_name]) for cat_name in cat_order if cat_name in featured_news_by_cat])}

              <!-- PROMINENT CTA BANNER: ĐỌC TRỌN BỘ 25 TIN TRÊN BNEWS (PRIMARY ACTION) -->
              <div style="background-color: #134E4A; padding: 20px 22px; text-align: center; border-radius: 4px; margin-top: 18px; box-shadow: 0 4px 12px rgba(19, 78, 74, 0.15);">
                <div style="color: #F7EBE0; font-size: 12px; line-height: 1.5; margin-bottom: 12px;">
                  Bản tin phiên này còn <strong>20 sự kiện xác minh chuyên sâu</strong> khác về điều hành lãi suất, biến động thị trường chứng khoán, dữ liệu thanh toán số và an ninh tài chính.
                </div>
                <a href="https://bryanportfolio.io.vn/fintech-intelligence/#verified-news" target="_blank" style="display: inline-block; background-color: #BE123C; color: #FFFFFF; font-weight: 700; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; padding: 11px 24px; text-decoration: none; border-radius: 2px;">
                  ĐỌC TOÀN BỘ 25 BẢN TIN TRÊN BNEWS →
                </a>
              </div>

              <!-- DEDICATED SUBSCRIBE CALL-OUT BOX (SECONDARY ACTION - CLEAN & BALANCED) -->
              <div style="background-color: #F7EBE0; border: 1px solid #134E4A; border-radius: 4px; padding: 18px 20px; text-align: center; margin-top: 18px;">
                <div style="font-family: 'SF Mono', monospace; font-size: 10px; font-weight: 700; color: #BE123C; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 4px;">
                  BẠN ĐƯỢC BẠN BÈ CHUYỂN TIẾP (FORWARD) EMAIL NÀY?
                </div>
                <div style="font-size: 15px; font-weight: 800; color: #134E4A; margin-bottom: 4px;">
                  Đăng Ký Nhận Bản Tin Bnews Hàng Ngày
                </div>
                <div style="font-size: 12px; color: #57534E; line-height: 1.5; max-width: 440px; margin: 0 auto 12px auto;">
                  Cập nhật phân tích tài chính, thanh toán số, lãi suất tiền gửi và 25 sự kiện xác minh lúc 9h00 sáng mỗi ngày. Miễn phí 100%.
                </div>
                <a href="https://bryanportfolio.io.vn/fintech-intelligence/#subscribe" target="_blank" style="display: inline-block; background-color: #134E4A; color: #FFFFFF; font-weight: 700; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; padding: 9px 20px; text-decoration: none; border-radius: 2px;">
                  + ĐĂNG KÝ NHẬN BẢN TIN (SUBSCRIBE) →
                </a>
              </div>

            </td>
          </tr>

          <!-- FOOTER -->
          <tr>
            <td class="mobile-padding" style="background-color: #134E4A; padding: 24px 20px; color: #F7EBE0; text-align: center; border-top: 3px solid #BE123C;">
              <div style="font-size: 15px; font-weight: 800; color: #FFFFFF; margin-bottom: 4px;">
                BNEWS | FINTECH & FINANCIAL INTELLIGENCE
              </div>
              <div style="font-size: 11px; opacity: 0.85; line-height: 1.5; max-width: 460px; margin: 0 auto 14px auto;">
                Bản quyền nội dung thuộc về Bryan Portfolio & Ban Biên Tập Bnews FinTech Intelligence. Bản tin được tổng hợp, kiểm chứng và biên tập tự động lúc 9h00 hàng ngày.
              </div>
              <div style="margin-bottom: 14px;">
                <a href="https://bryanportfolio.io.vn/fintech-intelligence/" target="_blank" style="color: #FDF2E9; text-decoration: underline; font-size: 11px; font-weight: 600; margin: 0 10px;">Truy cập Bnews</a>
                <a href="https://bryanportfolio.io.vn" target="_blank" style="color: #FDF2E9; text-decoration: underline; font-size: 11px; font-weight: 600; margin: 0 10px;">Bryan Portfolio</a>
              </div>
              <div style="font-size: 11px; border-top: 1px solid rgba(255,255,255,0.2); padding-top: 12px; font-family: 'SF Mono', monospace; line-height: 1.5;">
                <span style="color: rgba(255,255,255,0.75);">
                  Bạn nhận được email này vì đã đăng ký theo dõi Bản tin Bnews FinTech Intelligence.<br/>
                  Nếu không muốn tiếp tục nhận email, vui lòng 
                </span>
                <a href="#unsubscribe" style="color: #5EEAD4; text-decoration: underline; font-weight: 700;">Hủy đăng ký (Unsubscribe)</a>.
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

    ref_val = card.get("referenceValue", "")
    period = card.get("dataPeriod") or card.get("asOf", "")
    url = card.get("sourceUrl", "https://bryanportfolio.io.vn/fintech-intelligence/")
    article_title = card.get("articleTitle", "")

    # Outer TD carries background, borders, and border-top directly so HTML table engine renders 100% equal height
    return f"""
    <td class="mp-col" width="48%" style="background-color: #FFFFFF; border: 1px solid #E7E5E4; border-top: 3px solid #134E4A; border-radius: 2px; padding: 12px 14px; vertical-align: top;">
      <table border="0" cellpadding="0" cellspacing="0" width="100%" style="height: 100%;">
        <tr>
          <td style="vertical-align: top;">
            <!-- HEADER: LABEL + BADGE -->
            <table border="0" cellpadding="0" cellspacing="0" width="100%" style="margin-bottom: 4px;">
              <tr>
                <td style="font-family: 'SF Mono', monospace; font-size: 10px; font-weight: 700; color: #134E4A; text-transform: uppercase;">
                  {escape(lbl)}
                </td>
                <td align="right">
                  <span style="display: inline-block; background-color: #DCFCE7; color: #15803D; font-family: 'SF Mono', monospace; font-size: 9px; font-weight: 700; padding: 1px 5px; border-radius: 2px;">
                    VERIFIED
                  </span>
                </td>
              </tr>
            </table>

            <!-- VALUE -->
            <div style="font-size: 19px; font-weight: 800; color: #047857; line-height: 1.2; margin-bottom: 3px; font-family: 'SF Mono', monospace;">
              {escape(val_display)}
            </div>

            <!-- PERIOD -->
            {f'<div style="font-size: 10px; color: #78716C; margin-bottom: 5px; font-weight: 500;">{escape(period)}</div>' if period else ''}

            <!-- REFERENCE INFO -->
            <div style="font-size: 11px; color: #44403C; line-height: 1.45; margin-bottom: 5px;">
              {escape(ref_val[:110])}{'...' if len(ref_val) > 110 else ''}
            </div>

            <!-- ARTICLE TITLE (IF PRESENT) -->
            {f'<div style="font-size: 11px; color: #134E4A; font-weight: 600; margin-bottom: 5px; line-height: 1.3;">Bài viết: {escape(article_title[:55])}...</div>' if article_title else ''}
          </td>
        </tr>
        <tr>
          <!-- BOTTOM ALIGNED LINK -->
          <td style="vertical-align: bottom; padding-top: 8px;">
            <a href="{escape(url)}" target="_blank" style="font-size: 10px; font-family: 'SF Mono', monospace; font-weight: 700; color: #BE123C; text-decoration: none;">
              CHI TIẾT & NGUỒN →
            </a>
          </td>
        </tr>
      </table>
    </td>
    """

def _render_featured_category_block(cat_name: str, items: list) -> str:
    if not items:
        return ""
    
    # 100% standard BMP Unicode characters (never corrupt into  in any mail client)
    cat_bullets = {
        "Ngân hàng": "■",
        "Thị trường vốn": "■",
        "Bán lẻ, D2C và xu hướng tiêu dùng": "■",
        "Thanh toán": "■",
        "Doanh nghiệp": "■"
    }
    bullet = cat_bullets.get(cat_name, "■")

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
            <div style="margin: 8px 0 10px 0; border-radius: 4px; overflow: hidden; border: 1px solid #E7E5E4; background-color: #F5F5F4;">
              <a href="{escape(url)}" target="_blank" style="display: block; text-decoration: none;">
                <img src="{escape(img_url)}" alt="{escape(hl)}" width="100%" class="featured-img" style="width: 100%; max-width: 100%; height: auto; max-height: 220px; aspect-ratio: 16/9; object-fit: cover; display: block;" onerror="this.parentElement.parentElement.style.display='none'" />
              </a>
            </div>
            """

        items_html.append(f"""
        <table border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #FFFFFF; border: 1px solid #E7E5E4; border-radius: 3px; margin-bottom: 12px;">
          <tr>
            <td style="padding: 13px 15px;">
              <!-- META ROW: ID, SOURCE & 0-24H BADGE -->
              <table border="0" cellpadding="0" cellspacing="0" width="100%" style="margin-bottom: 6px;">
                <tr>
                  <td style="vertical-align: middle;">
                    <span style="font-family: 'SF Mono', monospace; font-size: 10px; font-weight: 700; background-color: #134E4A; color: #FFFFFF; padding: 2px 6px; border-radius: 2px; white-space: nowrap;">
                      {escape(eid)}
                    </span>
                    <span style="font-size: 11px; color: #57534E; margin-left: 6px; line-height: 1.4;">
                      Nguồn: <strong style="color: #1C1917;">{escape(src)}</strong>
                    </span>
                  </td>
                  <td align="right" style="vertical-align: top; white-space: nowrap; padding-left: 8px;">
                    <span class="nowrap-badge" style="font-family: 'SF Mono', monospace; font-size: 10px; font-weight: 700; color: #15803D; background-color: #DCFCE7; padding: 2px 6px; border-radius: 2px; white-space: nowrap; display: inline-block;">
                      [0–24H]
                    </span>
                  </td>
                </tr>
              </table>

              <!-- FEATURED IMAGE BANNER (RESPONSIVE FULL-WIDTH) -->
              {img_banner_html}

              <!-- HEADLINE -->
              <div style="font-size: 14px; font-weight: 700; color: #1C1917; line-height: 1.4; margin-bottom: 6px;">
                <a href="{escape(url)}" target="_blank" style="color: #1C1917; text-decoration: none;">
                  {escape(hl)}
                </a>
              </div>

              <!-- SUMMARY -->
              <div style="font-size: 12px; color: #44403C; line-height: 1.55; margin-bottom: 8px;">
                {escape(sm)}
              </div>

              <!-- FINTECH LENS -->
              {f'''
              <div style="background-color: #FDF2E9; border-left: 3px solid #BE123C; padding: 8px 10px; font-size: 11px; color: #1C1917; line-height: 1.45; margin-bottom: 6px;">
                <strong>Góc nhìn FinTech & B2B:</strong> {escape(fintech_lens)}
              </div>
              ''' if fintech_lens else ''}

              <!-- SUPPORTING QUOTE -->
              {f'''
              <div style="font-size: 11px; font-style: italic; color: #57534E; line-height: 1.4; margin-bottom: 6px;">
                “{escape(quote)}”
              </div>
              ''' if quote else ''}

              <div style="text-align: right; margin-top: 4px;">
                <a href="{escape(url)}" target="_blank" style="font-size: 10px; font-family: 'SF Mono', monospace; font-weight: 700; color: #134E4A; text-decoration: none;">
                  XEM NGUỒN BÁO GỐC ↗
                </a>
              </div>
            </td>
          </tr>
        </table>
        """)

    return f"""
    <div style="margin-bottom: 14px;">
      <div style="font-family: 'SF Mono', monospace; font-size: 11px; font-weight: 800; color: #BE123C; text-transform: uppercase; margin-bottom: 6px; letter-spacing: 0.5px;">
        <span style="color: #BE123C; margin-right: 4px;">{bullet}</span> {escape(cat_name.upper())}
      </div>
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

    # Save to pilot-output
    os.makedirs(os.path.dirname(OUT_PREVIEW_PILOT), exist_ok=True)
    with open(OUT_PREVIEW_PILOT, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Successfully generated: {OUT_PREVIEW_PILOT} ({len(html_content):,} bytes)")

    # Save to preview
    os.makedirs(os.path.dirname(OUT_PREVIEW_WEB), exist_ok=True)
    with open(OUT_PREVIEW_WEB, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Successfully synced: {OUT_PREVIEW_WEB} ({len(html_content):,} bytes)")

if __name__ == "__main__":
    main()
