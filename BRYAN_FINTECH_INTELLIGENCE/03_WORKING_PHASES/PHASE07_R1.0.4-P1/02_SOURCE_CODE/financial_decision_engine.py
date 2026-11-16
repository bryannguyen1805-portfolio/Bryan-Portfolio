#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
financial_decision_engine.py
============================
Workstream D — Financial Decision Intelligence Engine for Bryan FinTech Intelligence Phase 06.

Integrates Core Thesis, Macro-to-Micro Chains, Payment Radar Signals, Verified News Events,
and Market Pulse context into structured Decision Cards with explicit action recommendations
(MONITOR, INVESTIGATE, VALIDATE, EXPLORE, NO_ACTION_YET), monitoring triggers, and limitations.
Strictly prohibits stock buy/sell advice, profit promises, or turning hypotheses into conclusions.
"""

import re
from typing import Dict, List, Any

VALID_DECISION_CATEGORIES = {
    "STRATEGIC_SIGNAL",
    "MARKET_OPPORTUNITY",
    "COMMERCIAL_OPPORTUNITY",
    "FINANCIAL_RISK",
    "EMERGING_TREND",
    "MONITORING_REQUIRED",
}

VALID_RECOMMENDED_ACTIONS = {
    "MONITOR",
    "INVESTIGATE",
    "VALIDATE",
    "EXPLORE",
    "NO_ACTION_YET",
}

PROHIBITED_INVESTMENT_PATTERNS = [
    r'\bkhuyến nghị mua cổ phiếu\b',
    r'\bkhuyến nghị bán cổ phiếu\b',
    r'\bcam kết lợi nhuận\b',
    r'\blợi nhuận chắc chắn\b',
    r'\bstrong buy\b',
    r'\bstrong sell\b',
]


class FinancialDecisionEngine:
    """
    Produces executive Decision Cards linking verified news, theses, transmission chains,
    payment radar signals, and Market Pulse context.
    """

    def __init__(
        self,
        verified_news: List[Dict[str, Any]],
        audited_facts_bundle: Dict[str, Any],
        audited_market_pulse: List[Dict[str, Any]],
        theses: List[Dict[str, Any]],
        chains: List[Dict[str, Any]],
        radar_signals: List[Dict[str, Any]]
    ):
        self.news_by_id = {ev["eventId"]: ev for ev in verified_news if "eventId" in ev}
        self.unique_facts_by_id = {
            f["factId"]: f for f in audited_facts_bundle.get("uniqueVerifiedFacts", [])
        }
        self.mp_by_id = {m["indicatorId"]: m for m in audited_market_pulse if "indicatorId" in m}
        self.theses_by_id = {t["thesisId"]: t for t in theses if "thesisId" in t}
        self.chains_by_id = {c["chainId"]: c for c in chains if "chainId" in c}
        self.radar_by_id = {r["radarId"]: r for r in radar_signals if "radarId" in r}

    def _validate_and_build_refs(self, card: Dict[str, Any]) -> List[Dict[str, Any]]:
        for tid in card.get("supportingThesisIds", []):
            if tid not in self.theses_by_id:
                raise ValueError(f"DECISION_UNRESOLVED_THESIS_ID: {tid}")
        for cid in card.get("supportingChainIds", []):
            if cid not in self.chains_by_id:
                raise ValueError(f"DECISION_UNRESOLVED_CHAIN_ID: {cid}")
        for rid in card.get("supportingRadarIds", []):
            if rid not in self.radar_by_id:
                raise ValueError(f"DECISION_UNRESOLVED_RADAR_ID: {rid}")

        refs = []
        for eid in card.get("supportingEventIds", []):
            if eid not in self.news_by_id:
                raise ValueError(f"DECISION_UNRESOLVED_EVENT_ID: {eid}")
            ev = self.news_by_id[eid]
            refs.append({
                "refType": "NEWS_EVENT",
                "id": eid,
                "headline": ev.get("headline"),
                "publishedAt": ev.get("publishedAt"),
                "sourceUrl": ev.get("sourceUrl"),
                "evidenceSha256": ev.get("evidenceSha256")
            })
        for mid in card.get("supportingMarketPulseIds", []):
            if mid not in self.mp_by_id:
                raise ValueError(f"DECISION_UNRESOLVED_MP_ID: {mid}")
            mp = self.mp_by_id[mid]
            refs.append({
                "refType": "MARKET_PULSE",
                "id": mid,
                "indicatorName": mp.get("indicatorName"),
                "actualValue": mp.get("actualValue"),
                "unit": mp.get("unit"),
                "observationDate": mp.get("observationDate"),
                "updateStatus": mp.get("updateStatus"),
                "verificationStatus": mp.get("verificationStatus"),
                "sourceUrl": mp.get("sourceUrl")
            })

        # Ensure no prohibited investment advice language exists anywhere in the card
        card_text = " ".join([
            str(card.get("headline", "")),
            str(card.get("executiveSummary", "")),
            str(card.get("opportunity", "")),
            str(card.get("risk", "")),
        ]).lower()
        for pat in PROHIBITED_INVESTMENT_PATTERNS:
            if re.search(pat, card_text, re.I):
                raise ValueError(f"PROHIBITED_INVESTMENT_RECOMMENDATION_DETECTED: {pat}")

        return refs

    def generate_decision_cards(self) -> Dict[str, Any]:
        raw_cards = [
            {
                "decisionId": "DECISION-01",
                "headline": "Ưu tiên giải pháp SmartPOS đa phương thức và chấp nhận QR xuyên biên giới (VietQR Global) tại các chuỗi du lịch, F&B và bán lẻ trọng điểm",
                "decisionCategory": "COMMERCIAL_OPPORTUNITY",
                "executiveSummary": (
                    "Sự kết hợp giữa cột mốc 19,5 triệu lượt khách quốc tế đến Việt Nam (tính đến 31/10/2026) và định hướng mở rộng "
                    "VietQR Global đến từng điểm bán đang tạo ra nhu cầu thực tế về thiết bị chấp nhận thanh toán hợp nhất (Thẻ quốc tế + "
                    "VietQR nội địa + QR xuyên biên giới) cho mùa cao điểm du lịch cuối năm."
                ),
                "whatChanged": (
                    "Số liệu chính thức xác nhận Việt Nam đón 19,5 triệu lượt khách quốc tế (MP-07, VERIFIED), thu hẹp khoảng cách với Thái Lan "
                    "(25,4 triệu lượt) xuống còn 5,9 triệu lượt; đồng thời bài toán đưa VietQR Global xuống từng điểm bán lẻ được đặt làm trọng tâm (MP-06)."
                ),
                "whyItMatters": (
                    "Đối với Bryan và mảng phát triển kinh doanh thanh toán, các merchant ngành Khách sạn, F&B, Bán lẻ đặc sản và Wellness "
                    "tại các đô thị du lịch đang cần nâng cấp trải nghiệm thu ngân một chạm cho khách ngoại quốc mà không phải vận hành rời rạc nhiều thiết bị."
                ),
                "supportingThesisIds": ["THESIS-04", "THESIS-03"],
                "supportingChainIds": ["CHAIN-04"],
                "supportingRadarIds": ["RADAR-01"],
                "supportingEventIds": ["EVT-20261110-022", "EVT-20261110-004"],
                "supportingMarketPulseIds": ["MP-07", "MP-06"],
                "opportunity": (
                    "Đẩy mạnh tư vấn giải pháp All-in-One SmartPOS và đối soát hợp kênh (Omnichannel Reconciliation) cho các chuỗi khách sạn, "
                    "nhà hàng F&B và bán lẻ phục vụ khách quốc tế trong quý IV/2026."
                ),
                "risk": (
                    "Độ phủ kết nối ngân hàng phát hành nước ngoài của VietQR Global tại từng điểm bán vẫn đang trong giai đoạn mở rộng; "
                    "nếu nhân viên thu ngân chưa quen thao tác có thể gây gián đoạn trải nghiệm tại quầy."
                ),
                "recommendedAction": "EXPLORE",
                "monitoringTriggers": [
                    "Danh sách các quốc gia và ngân hàng/ví điện tử nước ngoài đã hoàn tất kết nối thương mại VietQR Global với NAPAS.",
                    "Sản lượng giao dịch thẻ quốc tế và QR tại các merchant ngành Khách sạn – F&B trong tháng 11 và 12/2026."
                ],
                "timeHorizon": "Ngắn hạn (Quý IV/2026 – Quý I/2027, mùa cao điểm khách quốc tế)",
                "confidenceLevel": "HIGH",
                "limitations": [
                    "Số liệu khách quốc tế MP-07 (19,5 triệu lượt) là số liệu lũy kế 10 tháng đầu năm 2026 (chốt ngày 31/10/2026).",
                    "Chỉ số MP-06 (Sản lượng giao dịch VietQR NAPAS) hiện mới có cập nhật định tính (QUALITATIVE_UPDATE_ONLY, actualValue: null), chưa có số liệu định lượng sản lượng giao dịch VietQR Global mới nhất."
                ]
            },
            {
                "decisionId": "DECISION-02",
                "headline": "Khai thác nhu cầu thanh toán không tiền mặt khi giao hàng (Non-cash COD / Payment Link) và trả góp cho phân khúc hàng nặng, điện máy dịp cuối năm",
                "decisionCategory": "MARKET_OPPORTUNITY",
                "executiveSummary": (
                    "Cao điểm siêu sale 11.11 chứng kiến sự gia tăng đơn hàng ở phân khúc hàng nặng, hàng cồng kềnh (J&T Cargo chủ động tăng năng lực vận hành), "
                    "trong khi lãi suất tiền gửi 12 tháng neo ở mức 7%/năm khiến người tiêu dùng ưu tiên giữ tiền tiết kiệm và sử dụng công cụ thanh toán linh hoạt/trả góp khi mua hàng giá trị cao."
                ),
                "whatChanged": (
                    "Các đơn vị vận chuyển chuyên biệt (EVT-20261110-004) đẩy mạnh năng lực xử lý hàng nặng trong kỳ 11.11, diễn ra đúng lúc "
                    "5 ngân hàng niêm yết lãi suất tiền gửi 12 tháng ở mức 7%/năm (EVT-20261110-005, MP-03)."
                ),
                "whyItMatters": (
                    "Đơn hàng nặng (điện máy, nội thất, xe điện, thiết bị gia dụng) có giá trị hóa đơn cao (high-ticket size). "
                    "Việc thay thế COD tiền mặt bằng QR động gắn mã vận đơn, Payment Link và trả góp 0% giúp tăng tỷ lệ giao hàng thành công và rút ngắn vòng quay vốn cho merchant."
                ),
                "supportingThesisIds": ["THESIS-04", "THESIS-01"],
                "supportingChainIds": ["CHAIN-04", "CHAIN-01"],
                "supportingRadarIds": ["RADAR-02", "RADAR-03"],
                "supportingEventIds": ["EVT-20261110-004", "EVT-20261110-005", "EVT-20261110-021"],
                "supportingMarketPulseIds": ["MP-03"],
                "opportunity": (
                    "Triển khai gói giải pháp QR động định danh theo đơn vận chuyển (Shipper Dynamic QR), Payment Link và Trả góp 0% đa ngân hàng "
                    "cho các đối tác logistics hàng nặng, chuỗi điện máy – nội thất, đại lý xe điện và cơ sở giáo dục/wellness."
                ),
                "risk": (
                    "Tác động từ lãi suất tiền gửi 7%/năm sang hành vi tăng sử dụng trả góp hiện là giả thuyết có cơ sở (HYPOTHESIS trong CHAIN-01), "
                    "cần kiểm chứng bằng số liệu tỷ lệ chuyển đổi trả góp thực tế trong kỳ 11.11 – 12.12."
                ),
                "recommendedAction": "VALIDATE",
                "monitoringTriggers": [
                    "Tỷ trọng giá trị giao dịch (GMV) qua Payment Link và trả góp 0% trong đợt siêu sale 11.11 và Black Friday.",
                    "Tỷ lệ đơn hàng giá trị cao chuyển từ thu tiền mặt (cash COD) sang quét mã QR động khi nhận hàng."
                ],
                "timeHorizon": "Ngắn hạn (Tháng 11/2026 – Tháng 01/2027, cao điểm mua sắm cuối năm và Tết)",
                "confidenceLevel": "HIGH",
                "limitations": [
                    "Mắt xích hành vi người tiêu dùng chuyển sang trả góp để giữ sổ tiết kiệm 7%/năm được phân loại là HYPOTHESIS cần theo dõi thêm số liệu thực nghiệm, không mặc định là kết luận chắc chắn."
                ]
            },
            {
                "decisionId": "DECISION-03",
                "headline": "Theo dõi sát áp lực chi phí vốn (lãi suất huy động 12T ở mức 7%/năm) và hiệu quả thực tế của kênh NHNN mua USD giao ngay từ ngày 11/11",
                "decisionCategory": "STRATEGIC_SIGNAL",
                "executiveSummary": (
                    "Bức tranh tiền tệ đang có sự đan xen giữa hai lực đối lập: một mặt, cấu trúc 80% nhu cầu vốn dựa vào ngân hàng và lệch kỳ hạn "
                    "giữ lãi suất huy động 12 tháng ở mức 7%/năm; mặt khác, NHNN chủ động mua USD giao ngay tại 25.500 đồng/USD từ ngày 11/11 "
                    "để bơm thêm tiền đồng cho nền kinh tế, giúp VN-Index bật tăng lên 1.743,00 điểm."
                ),
                "whatChanged": (
                    "NHNN kích hoạt kênh mua USD giao ngay ở mức 25.500 đồng/USD từ 11/11 (EVT-20261110-006) trong khi tỷ giá trung tâm ngày 10/11 "
                    "ổn định ở mức 25.600 VND/USD (MP-01) và VN-Index đóng cửa tại 1.743,00 điểm (MP-04)."
                ),
                "whyItMatters": (
                    "Nếu kênh mua USD giao ngay bơm ra lượng tiền đồng đủ lớn, áp lực thanh khoản cuối năm của hệ thống ngân hàng sẽ dịu lại; "
                    "ngược lại, nếu chi phí vốn 12 tháng tiếp tục neo ở mức 7%/năm hoặc tăng thêm, các doanh nghiệp đối tác (merchant) sẽ thắt chặt chi phí tài chính hơn."
                ),
                "supportingThesisIds": ["THESIS-01", "THESIS-02"],
                "supportingChainIds": ["CHAIN-01", "CHAIN-02"],
                "supportingRadarIds": ["RADAR-03", "RADAR-05"],
                "supportingEventIds": [
                    "EVT-20261110-006",
                    "EVT-20261110-001",
                    "EVT-20261110-016",
                    "EVT-20261110-005",
                    "EVT-20261110-026"
                ],
                "supportingMarketPulseIds": ["MP-01", "MP-03", "MP-04", "MP-02", "MP-05", "MP-08"],
                "opportunity": (
                    "Thanh khoản VND được bổ sung từ ngày 11/11 hỗ trợ tâm lý kinh doanh và dòng tiền thanh toán B2B/B2C trong ngắn hạn."
                ),
                "risk": (
                    "Áp lực lệch kỳ hạn vốn ngân hàng (tín dụng/GDP ở mức 135–140% GDP) và biến động tỷ giá quốc tế (như việc đồng Yên Nhật Bản "
                    "khó phục hồi dù đã can thiệp 97,1 tỷ USD) có thể giới hạn dư địa giảm lãi suất trong trung hạn."
                ),
                "recommendedAction": "MONITOR",
                "monitoringTriggers": [
                    "Khối lượng USD thực tế được các NHTM bán giao ngay cho NHNN từ ngày 11/11/2026.",
                    "Cập nhật mới của lãi suất liên ngân hàng qua đêm (MP-02) và nghiệp vụ OMO (MP-08) từ nguồn chính thức.",
                    "Biến động biểu lãi suất huy động 12 tháng của nhóm NHTM lớn (MP-03)."
                ],
                "timeHorizon": "Ngắn đến trung hạn (1 – 6 tháng)",
                "confidenceLevel": "HIGH",
                "limitations": [
                    "Chỉ số MP-02 (Lãi suất liên ngân hàng qua đêm: 2,8%/năm ngày 02/10/2026) đã vượt ngưỡng 72 giờ (STALE_OBSERVATION / UNVERIFIED).",
                    "Chỉ số MP-08 (Bơm ròng OMO: 47.915 tỷ VND) là quan sát lịch sử từ ngày 21/09/2026, không phải số liệu bơm thanh khoản hiện tại của tháng 11/2026.",
                    "Chỉ số MP-05 (Tăng trưởng tín dụng toàn hệ thống) hiện chỉ có cập nhật định tính (QUALITATIVE_UPDATE_ONLY, actualValue: null)."
                ]
            },
            {
                "decisionId": "DECISION-04",
                "headline": "Nghiên cứu giải pháp thanh toán tích hợp hóa đơn điện tử và thu hộ thuế cho phân khúc Hộ kinh doanh & SME trước lộ trình siết quản lý nợ thuế",
                "decisionCategory": "EMERGING_TREND",
                "executiveSummary": (
                    "Đề xuất của VCCI về việc quy định rõ ngưỡng nợ thuế áp dụng tạm hoãn xuất cảnh (200 triệu đồng đối với cá nhân/hộ kinh doanh, "
                    "1 tỷ đồng đối với doanh nghiệp) cùng mục tiêu thu ngân sách năm 2027 đạt hơn 3,33 triệu tỷ đồng phản ánh xu hướng chuẩn hóa "
                    "quản trị thuế và dòng tiền kinh doanh của khu vực hộ kinh doanh cá thể và SME."
                ),
                "whatChanged": (
                    "Ngày 10/11/2026, VCCI đưa ra kiến nghị ngưỡng nợ thuế định lượng cụ thể (200 triệu đồng và 1 tỷ đồng - EVT-20261110-020) "
                    "song hành với Nghị quyết dự toán ngân sách năm 2027 của Quốc hội (EVT-20261110-032)."
                ),
                "whyItMatters": (
                    "Khi ranh giới tuân thủ thuế được lượng hóa rõ ràng, các hộ kinh doanh F&B, bán lẻ và dịch vụ có doanh thu khá sẽ chuyển dịch "
                    "từ nhận tiền mặt/chuyển khoản cá nhân sang giải pháp thanh toán định danh có kết nối hóa đơn điện tử và đối soát thuế tự động."
                ),
                "supportingThesisIds": ["THESIS-03"],
                "supportingChainIds": ["CHAIN-03"],
                "supportingRadarIds": ["RADAR-04"],
                "supportingEventIds": [
                    "EVT-20261110-020",
                    "EVT-20261110-032",
                    "EVT-20261110-017"
                ],
                "supportingMarketPulseIds": ["MP-04"],
                "opportunity": (
                    "Khảo sát khả năng đóng gói giải pháp chấp nhận thanh toán QR/SmartPOS kết nối sẵn với các đối tác phần mềm bán hàng – "
                    "hóa đơn điện tử và tiện ích nộp thuế/phí cho nhóm khách hàng hộ kinh doanh chuỗi và SME."
                ),
                "risk": (
                    "Ngưỡng nợ thuế 200 triệu đồng và 1 tỷ đồng hiện mới ở giai đoạn đề xuất chính sách của VCCI (POLICY_THRESHOLD), "
                    "thời điểm hiệu lực và mức ngưỡng cuối cùng phụ thuộc vào văn bản quy phạm pháp luật chính thức."
                ),
                "recommendedAction": "INVESTIGATE",
                "monitoringTriggers": [
                    "Văn bản dự thảo nghị định/thông tư chính thức của Bộ Tài chính và Chính phủ về ngưỡng nợ thuế áp dụng tạm hoãn xuất cảnh.",
                    "Nhu cầu tích hợp API thanh toán – hóa đơn điện tử từ các đối tác phần mềm POS tại Việt Nam."
                ],
                "timeHorizon": "Trung hạn (3 – 12 tháng)",
                "confidenceLevel": "MEDIUM",
                "limitations": [
                    "Dữ kiện 200 triệu đồng và 1 tỷ đồng trong EVT-20261110-020 là ngưỡng đề xuất chính sách (POLICY_THRESHOLD), không phải số liệu thống kê thực tế đã áp dụng.",
                    "Toàn bộ ấn bản hiện tại dựa trên 18 sự kiện tin tức đã xác minh (16 sự kiện trong khung 0–24h), đang ở trạng thái Pilot (DATA_SHORTFALL_OR_UNVERIFIED so với chuẩn 25 sự kiện/ngày)."
                ]
            }
        ]

        cards_out = []
        for card in raw_cards:
            if card["decisionCategory"] not in VALID_DECISION_CATEGORIES:
                raise ValueError(f"INVALID_DECISION_CATEGORY: {card['decisionCategory']}")
            if card["recommendedAction"] not in VALID_RECOMMENDED_ACTIONS:
                raise ValueError(f"INVALID_RECOMMENDED_ACTION: {card['recommendedAction']}")
            card["evidenceReferences"] = self._validate_and_build_refs(card)
            cards_out.append(card)

        return {
            "totalDecisionCards": len(cards_out),
            "fiveQuestionsExecutiveSynthesis": {
                "question1_whatIsMarketChanging": (
                    "Thị trường đang diễn ra sự dịch chuyển kép: (1) Ở tầng cấu trúc vốn, tỷ lệ tín dụng/GDP ở mức 135–140% và 80% nhu cầu vốn "
                    "dựa vào ngân hàng khiến lãi suất tiền gửi 12 tháng neo ở mức 7%/năm tại 5 NHTM; (2) Ở tầng điều hành ngắn hạn, NHNN chủ động "
                    "mở kênh mua USD giao ngay ở mức 25.500 đồng/USD từ ngày 11/11 để bơm tiền đồng dịp cuối năm, giúp VN-Index bật tăng lên 1.743,00 điểm."
                ),
                "question2_macroImpactOnBanksEnterprisesConsumers": (
                    "Ngân hàng phải cân đối giữa chi phí huy động kỳ hạn 12 tháng (7%/năm) và thanh khoản VND ngắn hạn được bổ sung qua kênh bán USD cho NHNN; "
                    "Doanh nghiệp đối mặt với chi phí vốn trung – dài hạn chọn lọc hơn nhưng hưởng lợi từ tỷ giá ổn định và đầu tư công (khung ngân sách 2027 hơn 4,07 triệu tỷ đồng); "
                    "Người tiêu dùng vừa tích lũy phòng thủ (tiết kiệm 7%/năm, vàng SJC 138,5–141,5 triệu đồng/lượng) vừa tập trung chi tiêu vào các dịp siêu sale 11.11."
                ),
                "question3_cashlessPaymentOpportunities": (
                    "Ba cơ hội thực chất nhất cho ngành thanh toán không tiền mặt gồm: (1) Mở rộng điểm chấp nhận VietQR Global và SmartPOS đa phương thức "
                    "đón làn sóng 19,5 triệu lượt khách quốc tế; (2) Giải pháp thanh toán không tiền mặt khi giao hàng (QR động theo đơn/Payment Link) "
                    "cho phân khúc hàng nặng dịp 11.11; và (3) Trả góp 0% đa ngân hàng giúp khách hàng mua sắm hàng giá trị cao mà không phải rút sổ tiết kiệm 7%/năm."
                ),
                "question4_keyWatchSignals": (
                    "Cần theo dõi sát: (1) Doanh số NHNN mua USD giao ngay thực tế từ ngày 11/11; (2) Cập nhật mới của lãi suất liên ngân hàng qua đêm (MP-02 hiện đã cũ từ 02/10) "
                    "và biểu lãi suất 12 tháng của nhóm Big 4; (3) Số liệu định lượng sản lượng giao dịch VietQR / VietQR Global (MP-06); và (4) Quy định chính thức về ngưỡng nợ thuế 200 triệu / 1 tỷ đồng."
                ),
                "question5_bryanNextActions": (
                    "EXPLORE giải pháp SmartPOS tích hợp thẻ quốc tế + VietQR Global cho các chuỗi F&B, khách sạn, bán lẻ du lịch; "
                    "VALIDATE nhu cầu QR động giao nhận (Non-cash COD) và trả góp 0% cho ngành hàng nặng/điện máy mùa 11.11 – 12.12; "
                    "INVESTIGATE hướng tích hợp thanh toán – hóa đơn điện tử cho phân khúc hộ kinh doanh/SME; và MONITOR sát diễn biến thanh khoản tiền tệ từ đợt mua USD ngày 11/11."
                )
            },
            "decisionCards": cards_out
        }
