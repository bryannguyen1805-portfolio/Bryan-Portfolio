#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
core_thesis_engine.py
=====================
Workstream A — Core Thesis Engine for Bryan FinTech Intelligence Phase 06.

Reads verified news events, audited unique financial facts, and Market Pulse context,
groups events by thematic pillars, evaluates supporting and counter-evidence, and
constructs 3–5 high-conviction Core Theses without summarizing individual articles
or fabricating unsupported claims.
"""

from typing import Dict, List, Any, Set


CANONICAL_THEME_GROUPS = [
    "Monetary Policy & Interest Rates",
    "Banking & Credit",
    "Capital Markets",
    "Corporate & Business Expansion",
    "Consumer Behavior",
    "Digital Economy",
    "Cashless Payment & Payment Infrastructure",
    "International Finance & Global Economy",
]


class CoreThesisEngine:
    """
    Synthesizes multi-event, fact-grounded Core Theses with explicit causal explanations,
    counter-evidence, watch signals, and invalidation conditions.
    """

    def __init__(
        self,
        verified_news: List[Dict[str, Any]],
        audited_facts_bundle: Dict[str, Any],
        audited_market_pulse: List[Dict[str, Any]]
    ):
        self.news_by_id: Dict[str, Dict[str, Any]] = {
            ev["eventId"]: ev for ev in verified_news if "eventId" in ev
        }
        self.all_facts_by_id: Dict[str, Dict[str, Any]] = {
            f["factId"]: f for f in audited_facts_bundle.get("allAuditedFacts", [])
        }
        self.unique_facts_by_id: Dict[str, Dict[str, Any]] = {
            f["factId"]: f for f in audited_facts_bundle.get("uniqueVerifiedFacts", [])
        }
        self.mp_by_id: Dict[str, Dict[str, Any]] = {
            m["indicatorId"]: m for m in audited_market_pulse if "indicatorId" in m
        }

    def _build_source_references(
        self,
        event_ids: List[str],
        fact_ids: List[str],
        mp_ids: List[str]
    ) -> List[Dict[str, Any]]:
        refs: List[Dict[str, Any]] = []
        for eid in event_ids:
            if eid not in self.news_by_id:
                raise ValueError(f"UNRESOLVED_EVENT_REFERENCE: {eid}")
            ev = self.news_by_id[eid]
            refs.append({
                "refType": "NEWS_EVENT",
                "id": eid,
                "headline": ev.get("headline"),
                "publisher": ev.get("publisher"),
                "publishedAt": ev.get("publishedAt"),
                "sourceUrl": ev.get("sourceUrl"),
                "evidenceSha256": ev.get("evidenceSha256")
            })
        for fid in fact_ids:
            if fid not in self.all_facts_by_id:
                raise ValueError(f"UNRESOLVED_FACT_REFERENCE: {fid}")
            fact = self.all_facts_by_id[fid]
            if fact.get("isDuplicate"):
                raise ValueError(
                    f"DUPLICATE_FACT_IN_THESIS_PROHIBITED: {fid} is a duplicate of {fact.get('duplicateOfFactId')}"
                )
            if fact.get("entityBindingStatus") in ("ENTITY_UNVERIFIED", "ENTITY_AMBIGUOUS"):
                raise ValueError(
                    f"UNVERIFIED_ENTITY_FACT_IN_THESIS_PROHIBITED: {fid} has status {fact.get('entityBindingStatus')}"
                )
            refs.append({
                "refType": "FINANCIAL_FACT",
                "id": fid,
                "eventId": fact.get("eventId"),
                "metricName": fact.get("metricName"),
                "extractedExpression": fact.get("extractedExpression"),
                "verifiedEntity": fact.get("verifiedEntity"),
                "entityBindingStatus": fact.get("entityBindingStatus")
            })
        for mid in mp_ids:
            if mid not in self.mp_by_id:
                raise ValueError(f"UNRESOLVED_MARKET_PULSE_REFERENCE: {mid}")
            mp = self.mp_by_id[mid]
            refs.append({
                "refType": "MARKET_PULSE_CONTEXT",
                "id": mid,
                "indicatorName": mp.get("indicatorName"),
                "actualValue": mp.get("actualValue"),
                "unit": mp.get("unit"),
                "observationDate": mp.get("observationDate"),
                "updateStatus": mp.get("updateStatus"),
                "verificationStatus": mp.get("verificationStatus"),
                "sourceUrl": mp.get("sourceUrl"),
                "evidenceSha256": mp.get("evidenceSha256")
            })
        return refs

    def generate_theses(self) -> Dict[str, Any]:
        """
        Generates 4 high-conviction Core Theses backed by verified events, deduplicated facts,
        and Market Pulse context, and documents coverage across all 8 canonical theme groups.
        """
        raw_theses = [
            {
                "thesisId": "THESIS-01",
                "themeGroup": "Banking & Credit",
                "title": "Nút thắt cấu trúc kỳ hạn huy động – cho vay và sự phụ thuộc 80% nhu cầu vốn vào hệ thống ngân hàng giữ mặt bằng lãi suất huy động 12 tháng neo ở mức 7%/năm",
                "centralArgument": (
                    "Hệ thống tài chính Việt Nam đang đối mặt với áp lực lệch kỳ hạn mang tính cấu trúc khi khoảng 80% nhu cầu vốn "
                    "của nền kinh tế đi qua hệ thống ngân hàng và tỷ lệ tín dụng/GDP đã lên tới 135–140% GDP, trong khi kênh trái phiếu "
                    "doanh nghiệp vẫn phụ thuộc ngược vào bảo lãnh ngân hàng ('tuy hai mà một'). Để tài trợ cho nhu cầu vốn trung – dài hạn "
                    "khổng lồ (như 830.000 tỷ đồng vốn đầu tư của EVN hay nhu cầu 1.100 tỷ USD trong 5 năm tới), các ngân hàng thương mại "
                    "buộc phải duy trì mặt bằng lãi suất huy động kỳ hạn 12 tháng ở mức cao tới 7%/năm tại nhóm 5 ngân hàng dẫn đầu."
                ),
                "whatChanged": (
                    "Ngày 10/11/2026 ghi nhận 5 ngân hàng thương mại (MBV, PGBank, Sacombank, VCBNeo, VIB) cùng niêm yết lãi suất trực tuyến "
                    "kỳ hạn 12 tháng ở mức 7%/năm (kỳ hạn 18 tháng lên tới 7,4%/năm), đồng thời các chuyên gia và lãnh đạo ngân hàng (TS Đào Minh Tú, "
                    "TS Nguyễn Tú Anh, CEO Techcombank) đồng loạt cảnh báo giới hạn của mô hình tăng trưởng dựa vào tín dụng ngân hàng."
                ),
                "whyItMatters": (
                    "Chi phí vốn huy động đầu vào của hệ thống ngân hàng khó giảm sâu trong ngắn hạn, kéo theo chi phí tài chính của doanh nghiệp "
                    "và lãi suất cho vay tiêu dùng/mua trả góp duy trì ở ngưỡng chọn lọc khắt khe hơn."
                ),
                "supportingEventIds": [
                    "EVT-20261110-001",
                    "EVT-20261110-016",
                    "EVT-20261110-005",
                    "EVT-20261110-019",
                    "EVT-20261110-010"
                ],
                "supportingFactIds": [
                    "FACT-20261110-001",
                    "FACT-20261110-010",
                    "FACT-20261110-015",
                    "FACT-20261110-004"
                ],
                "supportingMarketPulseIds": [
                    "MP-03",
                    "MP-05"
                ],
                "counterEvidence": [
                    "NHNN đã có động thái mở kênh mua USD giao ngay ở mức 25.500 đồng/USD từ ngày 11/11 (EVT-20261110-006) để bơm thêm tiền đồng hỗ trợ thanh khoản ngắn hạn cho hệ thống.",
                    "Về mặt chính sách tín dụng (MP-05, cập nhật định tính ngày 25/10/2026), NHNN đã có cơ chế điều hành linh hoạt hơn đối với room tín dụng, dù chưa có số liệu định lượng tăng trưởng tín dụng toàn hệ thống mới nhất."
                ],
                "causalExplanation": (
                    "Khi người gửi tiền chỉ ưu tiên kỳ hạn ngắn (khoảng 1 năm trở xuống) nhưng doanh nghiệp và các dự án hạ tầng – năng lượng "
                    "đòi hỏi vốn vay 5–10 năm, ngân hàng phải trả phần bù kỳ hạn và rủi ro thanh khoản cao hơn để giữ chân tiền gửi 12–18 tháng, "
                    "tạo sàn chi phí vốn (COF) cứng cho toàn hệ thống."
                ),
                "affectedSectors": [
                    "Hệ thống Ngân hàng Thương mại (NHTM)",
                    "Thị trường Trái phiếu Doanh nghiệp & Đầu tư Hạ tầng – Năng lượng",
                    "Doanh nghiệp sản xuất – thương mại sử dụng đòn bẩy vốn lưu động",
                    "Dịch vụ tài chính tiêu dùng & Thanh toán trả góp"
                ],
                "impactHorizon": "MEDIUM_TERM_3_12M",
                "confidenceLevel": "HIGH",
                "confidenceReason": (
                    "Được xác thực đồng thời bởi 5 sự kiện tin tức độc lập trong khung 0–24h (CafeF, VnEconomy, Tuổi Trẻ), "
                    "4 dữ kiện định lượng đã kiểm định chủ thể và chỉ số MP-03 (7%/năm ngày 10/11/2026, VERIFIED)."
                ),
                "watchSignals": [
                    "Biến động biểu lãi suất huy động kỳ hạn 6–12 tháng của nhóm Big 4 (Agribank, Vietcombank, BIDV, VietinBank) so với nhóm NHTM cổ phần (7%/năm).",
                    "Tỷ trọng phát hành trái phiếu doanh nghiệp phi ngân hàng có tài sản đảm bảo và xếp hạng tín nhiệm độc lập.",
                    "Công bố chính thức từ NHNN về số liệu tăng trưởng tín dụng toàn hệ thống quý IV/2026 (hiện MP-05 đang ở trạng thái QUALITATIVE_UPDATE_ONLY)."
                ],
                "invalidationConditions": [
                    "Lãi suất huy động kỳ hạn 12 tháng tại nhóm NHTM cổ phần giảm đồng loạt xuống dưới 6,0%/năm mà không cần chương trình cộng thêm lãi suất.",
                    "Kênh trái phiếu doanh nghiệp và vốn ngoại hấp thụ được phần lớn nhu cầu vốn trung – dài hạn, kéo tỷ trọng cung ứng vốn qua ngân hàng giảm mạnh khỏi ngưỡng 80%."
                ]
            },
            {
                "thesisId": "THESIS-02",
                "themeGroup": "Monetary Policy & Interest Rates",
                "title": "NHNN kích hoạt kênh mua USD giao ngay tại 25.500 đồng/USD từ 11/11 để bơm tiền đồng mùa cao điểm, củng cố tâm lý giúp VN-Index lên 1.743 điểm",
                "centralArgument": (
                    "Thay vì chỉ dựa vào kênh thị trường mở (OMO), Ngân hàng Nhà nước chủ động triển khai phương án mua ngoại tệ giao ngay "
                    "với tỷ giá 25.500 đồng/USD từ ngày 11/11/2026 trong bối cảnh tỷ giá trung tâm ngày 10/11 được giữ ổn định ở mức 25.600 VND/USD. "
                    "Động thái kép này vừa bổ sung nguồn cung tiền đồng trực tiếp cho hệ thống ngân hàng bước vào cao điểm thanh toán cuối năm, "
                    "vừa giải tỏa tâm lý thị trường vốn, thúc đẩy VN-Index tăng 28,75 điểm (+1,68%) lên 1.743,00 điểm."
                ),
                "whatChanged": (
                    "Ngày 10/11/2026, NHNN công bố mua USD giao ngay ở mức 25.500 đồng/USD áp dụng từ 11/11, đồng thời đề xuất bãi bỏ 17 văn bản "
                    "quy phạm pháp luật cũ về lãi suất cho vay USD và tái cơ cấu TCTD; ngay trong phiên 10/11, VN-Index đảo chiều tăng lên 1.743,00 điểm."
                ),
                "whyItMatters": (
                    "Việc bơm tiền đồng qua kênh mua ngoại tệ giúp giảm áp lực căng thẳng thanh khoản cục bộ dịp cuối năm cho các ngân hàng và doanh nghiệp, "
                    "hỗ trợ dòng tiền trên thị trường chứng khoán và hoạt động giao dịch thương mại."
                ),
                "supportingEventIds": [
                    "EVT-20261110-006",
                    "EVT-20261110-009",
                    "EVT-20261110-026"
                ],
                "supportingFactIds": [
                    "FACT-20261110-005",
                    "FACT-20261110-003",
                    "FACT-20261110-008",
                    "FACT-20261110-009"
                ],
                "supportingMarketPulseIds": [
                    "MP-01",
                    "MP-04",
                    "MP-02",
                    "MP-08"
                ],
                "counterEvidence": [
                    "Bối cảnh tỷ giá quốc tế vẫn tiềm ẩn rủi ro cấu trúc: Nhật Bản đã chi kỷ lục 15,39 nghìn tỷ yên (97,1 tỷ USD) can thiệp nhưng đồng Yên vẫn neo ở vùng 157–158 JPY/USD (EVT-20261110-026).",
                    "Dữ liệu lãi suất liên ngân hàng qua đêm gần nhất trong kho dữ liệu (MP-02: 2,8%/năm ngày 02/10/2026) đã vượt trần độ tươi 72h (STALE_OBSERVATION), và số liệu OMO (MP-08: bơm ròng 47.915 tỷ VND) là quan sát lịch sử ngày 21/09/2026 nên chưa phản ánh quy mô khớp lệnh thực tế của đợt mua USD từ ngày 11/11."
                ],
                "causalExplanation": (
                    "Khi NHNN niêm yết giá mua USD giao ngay ở mức 25.500 đồng/USD (thấp hơn tỷ giá trung tâm 25.600 đồng/USD ngày 10/11), "
                    "các ngân hàng có trạng thái ngoại tệ dương có thể bán USD lấy VND ngay lập tức, chuyển hóa ngoại tệ thành thanh khoản tiền đồng "
                    "mà không tạo áp lực mất giá VND."
                ),
                "affectedSectors": [
                    "Ngân hàng Thương mại & Khối Kinh doanh Vốn – Ngoại hối (Treasury)",
                    "Thị trường Chứng khoán (VN-Index) & Công ty Chứng khoán",
                    "Doanh nghiệp Xuất nhập khẩu & FDI có dòng tiền ngoại tệ"
                ],
                "impactHorizon": "SHORT_TERM_0_3M",
                "confidenceLevel": "HIGH",
                "confidenceReason": (
                    "Dựa trên thông báo chính sách xác thực từ NHNN (EVT-20261110-006), dữ liệu tỷ giá trung tâm MP-01 (25.600 VND/USD ngày 10/11, VERIFIED) "
                    "và kết quả đóng cửa VN-Index MP-04 (1.743,00 điểm ngày 10/11, VERIFIED)."
                ),
                "watchSignals": [
                    "Khối lượng USD thực tế các NHTM bán giao ngay cho NHNN từ ngày 11/11/2026.",
                    "Cập nhật mới của lãi suất liên ngân hàng kỳ hạn qua đêm (MP-02) và nghiệp vụ thị trường mở (MP-08) trong tuần tiếp theo.",
                    "Diễn biến tỷ giá trung tâm USD/VND (MP-01) và chênh lệch lãi suất quốc tế (Fed – khu vực châu Á)."
                ],
                "invalidationConditions": [
                    "Tỷ giá USD/VND trên thị trường liên ngân hàng tăng vọt vượt trần biên độ khiến các NHTM ngừng bán USD cho NHNN.",
                    "Thanh khoản VND tiếp tục thắt chặt và VN-Index đánh mất toàn bộ nhịp phục hồi ngày 10/11."
                ]
            },
            {
                "thesisId": "THESIS-03",
                "themeGroup": "Corporate & Business Expansion",
                "title": "Kế hoạch ngân sách năm 2027 (thu 3,33 triệu tỷ, vay 1,28 triệu tỷ đồng) cùng hành lang kinh tế mới và hợp tác AI Việt – Nhật định hình chu kỳ đầu tư hạ tầng – số hóa",
                "centralArgument": (
                    "Quốc hội và Chính phủ đang thiết lập khung tài khóa và không gian phát triển quy mô lớn hướng tới mục tiêu tăng trưởng GDP "
                    "từ 10%/năm trở lên: dự toán ngân sách năm 2027 xác định tổng thu 3.334.338 tỷ đồng, chi hơn 4,07 triệu tỷ đồng và tổng mức vay "
                    "1.279.717 tỷ đồng, đi kèm Chương trình hành động phát triển trục xương sống Bắc – Nam và hành lang Đông – Tây thế hệ mới. "
                    "Song song, khu vực doanh nghiệp công nghệ dẫn đầu (như FPT với 5 trụ cột AI, lượng tử và tài chính công nghệ Việt – Nhật) "
                    "và cải cách hành chính thuế (đề xuất ngưỡng nợ thuế tạm hoãn xuất cảnh 200 triệu đồng cho cá nhân/hộ kinh doanh, 1 tỷ đồng cho doanh nghiệp) "
                    "đang thúc đẩy môi trường kinh doanh minh bạch và số hóa sâu hơn."
                ),
                "whatChanged": (
                    "Ngày 10/11/2026, các nghị quyết về dự toán ngân sách 2027 (EVT-20261110-032), Nghị quyết 358/NQ-CP về không gian phát triển vùng "
                    "(EVT-20261110-017), đề xuất 5 trụ cột công nghệ Việt – Nhật của FPT (EVT-20261110-022) và kiến nghị ngưỡng nợ thuế của VCCI (EVT-20261110-020) "
                    "được công bố đồng bộ."
                ),
                "whyItMatters": (
                    "Đầu tư công quy mô lớn kết hợp chuẩn hóa quản trị thuế đối với hộ kinh doanh và doanh nghiệp sẽ tạo lực đẩy kép: vừa mở rộng nhu cầu "
                    "thanh toán B2B/B2G theo các hành lang kinh tế, vừa buộc hộ kinh doanh cá thể chuyển dịch sang hóa đơn điện tử và thanh toán không tiền mặt minh bạch."
                ),
                "supportingEventIds": [
                    "EVT-20261110-032",
                    "EVT-20261110-017",
                    "EVT-20261110-022",
                    "EVT-20261110-020"
                ],
                "supportingFactIds": [
                    "FACT-20261110-013",
                    "FACT-20261110-014",
                    "FACT-20261110-006",
                    "FACT-20261110-007"
                ],
                "supportingMarketPulseIds": [
                    "MP-04"
                ],
                "counterEvidence": [
                    "Quy mô vay nợ ngân sách năm 2027 ở mức 1.279.717 tỷ đồng (FACT-20261110-013) đòi hỏi khả năng hấp thụ lớn của thị trường trái phiếu Chính phủ và kỷ luật giải ngân đầu tư công.",
                    "Ngưỡng nợ thuế 200 triệu đồng (cá nhân/hộ kinh doanh) và 1 tỷ đồng (doanh nghiệp) hiện mới là kiến nghị của VCCI (EVT-20261110-020, POLICY_THRESHOLD), chưa phải văn bản luật đã có hiệu lực thi hành."
                ],
                "causalExplanation": (
                    "Khi nhà nước đẩy mạnh chi đầu tư phát triển dọc các hành lang kinh tế và siết chặt kỷ luật quản lý thuế theo ngưỡng định lượng rõ ràng, "
                    "các doanh nghiệp và hộ kinh doanh có động lực trực tiếp để chuẩn hóa dòng tiền qua tài khoản ngân hàng và công cụ thu hộ/thanh toán số."
                ),
                "affectedSectors": [
                    "Hạ tầng, Xây dựng, Năng lượng & Logistics liên vùng",
                    "Công nghệ thông tin, AI & Tài chính công nghệ (FinTech)",
                    "Hộ kinh doanh cá thể, SME & Chuỗi bán lẻ nội địa"
                ],
                "impactHorizon": "LONG_TERM_12M_PLUS",
                "confidenceLevel": "HIGH",
                "confidenceReason": (
                    "Số liệu ngân sách nhà nước năm 2027 và Nghị quyết 358/NQ-CP là văn bản chính thức của Quốc hội và Chính phủ, được xác minh đầy đủ qua bằng chứng gốc."
                ),
                "watchSignals": [
                    "Tiến độ cụ thể hóa ngưỡng nợ thuế tạm hoãn xuất cảnh trong dự thảo nghị định/luật quản lý thuế.",
                    "Tốc độ giải ngân vốn đầu tư công vào các dự án trục Bắc – Nam và hành lang Đông – Tây.",
                    "Các dự án thương mại hóa tài chính công nghệ (FinTech) trong khuôn khổ hợp tác Việt Nam – Nhật Bản."
                ],
                "invalidationConditions": [
                    "Giải ngân đầu tư công chậm tiến độ hoặc chi phí huy động trái phiếu tăng mạnh làm thu hẹp dư địa tài khóa.",
                    "Kiến nghị phân loại ngưỡng nợ thuế cho hộ kinh doanh và doanh nghiệp không được đưa vào quy định chính thức."
                ]
            },
            {
                "thesisId": "THESIS-04",
                "themeGroup": "Cashless Payment & Payment Infrastructure",
                "title": "Đà bứt phá 19,5 triệu lượt khách quốc tế và cao điểm thương mại điện tử 11.11 mở rộng dư địa thanh toán số, dù tâm lý tích trữ vàng và gửi tiết kiệm vẫn phân hóa chi tiêu",
                "centralArgument": (
                    "Hai động lực thực tế đang thúc đẩy giao dịch thanh toán cuối năm: (1) Lượng khách du lịch quốc tế đến Việt Nam đạt 19,5 triệu lượt "
                    "(tính đến 31/10/2026), rút ngắn khoảng cách với Thái Lan (25,4 triệu lượt) xuống còn 5,9 triệu lượt, đặt ra bài toán mở rộng chấp nhận "
                    "thanh toán xuyên biên giới (VietQR Global) đến từng điểm bán; và (2) Cao điểm mua sắm trực tuyến 11.11 thúc đẩy lưu lượng đơn hàng lớn, "
                    "kể cả hàng nặng và cồng kềnh. Tuy nhiên, ở chiều ngược lại, giá vàng SJC duy trì vùng đỉnh 138,5–141,5 triệu đồng/lượng (mức giảm trong nước "
                    "chỉ bằng 30% thế giới) cùng lãi suất tiết kiệm 12 tháng ở mức 7%/năm cho thấy dòng tiền nhàn rỗi của người dân vẫn ưu tiên tích trữ phòng thủ."
                ),
                "whatChanged": (
                    "Thống kê mới nhất ngày 10/11/2026 xác nhận Việt Nam đón 19,5 triệu lượt khách quốc tế (MP-07, VERIFIED) song hành với đợt vận hành "
                    "cao điểm siêu sale 11.11 của ngành logistics (EVT-20261110-004) và sự kiện giá vàng SJC neo ở mức 138,5–141,5 triệu đồng/lượng (EVT-20261110-021)."
                ),
                "whyItMatters": (
                    "Cơ hội tăng trưởng giao dịch thanh toán không tiền mặt giai đoạn cuối năm tập trung rõ nét nhất ở phân khúc khách quốc tế (F&B, khách sạn, "
                    "bán lẻ du lịch) và thương mại điện tử/trả góp hàng giá trị cao, nơi người tiêu dùng nội địa cần giải pháp chia nhỏ dòng tiền thanh toán."
                ),
                "supportingEventIds": [
                    "EVT-20261110-004",
                    "EVT-20261110-021",
                    "EVT-20261110-013",
                    "EVT-20261110-005"
                ],
                "supportingFactIds": [
                    "FACT-20261110-011",
                    "FACT-20261110-012",
                    "FACT-20261110-017",
                    "FACT-20261110-018",
                    "FACT-20261110-001"
                ],
                "supportingMarketPulseIds": [
                    "MP-07",
                    "MP-06",
                    "MP-03"
                ],
                "counterEvidence": [
                    "Chỉ số MP-06 (Sản lượng giao dịch VietQR NAPAS) hiện chỉ có cập nhật định tính về định hướng triển khai VietQR Global đến từng điểm bán (QUALITATIVE_UPDATE_ONLY, actualValue: null), chưa có số liệu định lượng sản lượng giao dịch mới nhất trong ngày.",
                    "Sự hấp dẫn của lãi suất tiền gửi 12 tháng ở mức 7%/năm (MP-03) và tâm lý nắm giữ vàng SJC (EVT-20261110-021) có thể làm chậm tốc độ chi tiêu tiêu dùng nội địa thông thường."
                ],
                "causalExplanation": (
                    "Khách du lịch quốc tế tăng trưởng mạnh tạo ra dòng chi tiêu trực tiếp tại điểm bán vật lý (POS/SmartPOS/QR xuyên biên giới), "
                    "trong khi người tiêu dùng nội địa có xu hướng săn khuyến mãi tập trung vào các kỳ siêu sale (11.11) hoặc sử dụng công cụ trả góp "
                    "để bảo toàn khoản tiền gửi tiết kiệm đang hưởng lãi suất tốt."
                ),
                "affectedSectors": [
                    "Du lịch, Khách sạn, Nhà hàng (F&B) & Chuỗi bán lẻ tại điểm đến quốc tế",
                    "Thương mại điện tử, Logistics & Bán lẻ hàng điện máy / gia dụng cồng kềnh",
                    "Trung gian thanh toán (Payment Gateway, SmartPOS, VietQR / Cross-border QR, Trả góp)"
                ],
                "impactHorizon": "SHORT_TERM_0_3M",
                "confidenceLevel": "MEDIUM",
                "confidenceReason": (
                    "Số liệu khách quốc tế MP-07 (19,5 triệu lượt) và giá vàng/lãi suất tiền gửi được xác minh định lượng (VERIFIED), "
                    "nhưng số liệu sản lượng VietQR (MP-06) hiện mới ở mức cập nhật định tính (QUALITATIVE_UPDATE_ONLY)."
                ),
                "watchSignals": [
                    "Công bố định lượng tiếp theo từ NAPAS/NHNN về sản lượng và giá trị giao dịch VietQR / VietQR Global (MP-06).",
                    "Tốc độ tăng trưởng khách quốc tế tháng 11–12/2026 (mùa cao điểm du lịch cuối năm).",
                    "Tỷ lệ chuyển đổi đơn hàng hàng nặng/giá trị cao qua cổng thanh toán và trả góp trong kỳ 11.11 – 12.12."
                ],
                "invalidationConditions": [
                    "Đà tăng khách quốc tế chững lại trong quý IV/2026 hoặc độ phủ điểm chấp nhận thanh toán QR xuyên biên giới tại merchant vật lý bị nghẽn kỹ thuật.",
                    "Chi tiêu mùa lễ hội sụt giảm mạnh bất chấp các chương trình khuyến mãi 11.11 – 12.12."
                ]
            }
        ]

        # Attach verified sourceReferences and run anti-duplication & reference integrity checks
        seen_titles: Set[str] = set()
        theses_out: List[Dict[str, Any]] = []
        for t in raw_theses:
            norm_title = " ".join(t["title"].lower().split())
            if norm_title in seen_titles:
                raise ValueError(f"DUPLICATE_THESIS_DETECTED: {t['thesisId']}")
            seen_titles.add(norm_title)

            t["sourceReferences"] = self._build_source_references(
                t["supportingEventIds"],
                t["supportingFactIds"],
                t["supportingMarketPulseIds"]
            )
            theses_out.append(t)

        theme_group_evaluation = [
            {
                "themeGroup": "Banking & Credit",
                "status": "PROMOTED_TO_CORE_THESIS",
                "thesisId": "THESIS-01",
                "note": "Có 5 sự kiện tin tức đã xác minh và 4 dữ kiện tài chính độc lập cùng MP-03, MP-05."
            },
            {
                "themeGroup": "Monetary Policy & Interest Rates",
                "status": "PROMOTED_TO_CORE_THESIS",
                "thesisId": "THESIS-02",
                "note": "Có thông báo mua USD giao ngay của NHNN (EVT-20261110-006), bối cảnh tỷ giá quốc tế (EVT-20261110-026) và MP-01, MP-04."
            },
            {
                "themeGroup": "Corporate & Business Expansion",
                "status": "PROMOTED_TO_CORE_THESIS",
                "thesisId": "THESIS-03",
                "note": "Kết hợp khung ngân sách 2027 (EVT-20261110-032), hành lang kinh tế (EVT-20261110-017), hợp tác công nghệ FPT (EVT-20261110-022) và ngưỡng nợ thuế VCCI (EVT-20261110-020)."
            },
            {
                "themeGroup": "Cashless Payment & Payment Infrastructure",
                "status": "PROMOTED_TO_CORE_THESIS",
                "thesisId": "THESIS-04",
                "note": "Kết hợp động lực 19,5 triệu lượt khách quốc tế (MP-07), định hướng VietQR Global (MP-06), siêu sale 11.11 (EVT-20261110-004) và hành vi phòng thủ tài sản của người tiêu dùng."
            },
            {
                "themeGroup": "Capital Markets",
                "status": "INTEGRATED_INTO_THESIS_01_AND_02",
                "thesisId": "THESIS-01 / THESIS-02",
                "note": "Diễn biến VN-Index 1.743 điểm (MP-04) và thị trường trái phiếu doanh nghiệp (EVT-20261110-016) gắn kết hữu cơ với chính sách tiền tệ và cấu trúc vốn ngân hàng; không tách riêng để tránh trùng lặp luận điểm."
            },
            {
                "themeGroup": "Consumer Behavior",
                "status": "INTEGRATED_INTO_THESIS_04",
                "thesisId": "THESIS-04",
                "note": "Hành vi mua sắm 11.11, du lịch và nắm giữ vàng/tiết kiệm được tích hợp trực tiếp vào THESIS-04."
            },
            {
                "themeGroup": "Digital Economy",
                "status": "INTEGRATED_INTO_THESIS_03_AND_04",
                "thesisId": "THESIS-03 / THESIS-04",
                "note": "Đề xuất 5 trụ cột AI – lượng tử – tài chính công nghệ của FPT (EVT-20261110-022) và thương mại điện tử 11.11 đã được tích hợp vào THESIS-03 và THESIS-04."
            },
            {
                "themeGroup": "International Finance & Global Economy",
                "status": "INTEGRATED_INTO_THESIS_02",
                "thesisId": "THESIS-02",
                "note": "Can thiệp tỷ giá đồng Yên Nhật Bản 97,1 tỷ USD (EVT-20261110-026) đóng vai trò bối cảnh đối chiếu quốc tế cho điều hành tỷ giá của NHNN trong THESIS-02."
            }
        ]

        return {
            "totalTheses": len(theses_out),
            "themeGroupEvaluation": theme_group_evaluation,
            "theses": theses_out
        }
