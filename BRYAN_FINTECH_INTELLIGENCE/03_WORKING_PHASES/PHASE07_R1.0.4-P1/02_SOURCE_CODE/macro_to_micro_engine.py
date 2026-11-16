#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
macro_to_micro_engine.py
========================
Workstream B — Macro-to-Micro Engine for Bryan FinTech Intelligence Phase 06.

Constructs explicit 5-stage transmission chains:
  MACRO -> BANKING -> ENTERPRISE -> CONSUMER -> PAYMENT BEHAVIOR
and classifies every link strictly as OBSERVED, SUPPORTED_INFERENCE, or HYPOTHESIS
so hypotheses are never misrepresented as observed facts.
"""

from typing import Dict, List, Any

VALID_INFERENCE_LEVELS = {"OBSERVED", "SUPPORTED_INFERENCE", "HYPOTHESIS"}


class MacroToMicroEngine:
    """
    Translates verified macroeconomic and policy events into step-by-step microeconomic
    and payment behavior transmission chains.
    """

    def __init__(
        self,
        verified_news: List[Dict[str, Any]],
        audited_facts_bundle: Dict[str, Any],
        audited_market_pulse: List[Dict[str, Any]]
    ):
        self.news_by_id = {ev["eventId"]: ev for ev in verified_news if "eventId" in ev}
        self.unique_facts_by_id = {
            f["factId"]: f for f in audited_facts_bundle.get("uniqueVerifiedFacts", [])
        }
        self.mp_by_id = {m["indicatorId"]: m for m in audited_market_pulse if "indicatorId" in m}

    def _build_evidence_refs(
        self,
        event_ids: List[str],
        fact_ids: List[str],
        mp_ids: List[str]
    ) -> List[Dict[str, Any]]:
        refs = []
        for eid in event_ids:
            if eid not in self.news_by_id:
                raise ValueError(f"CHAIN_UNRESOLVED_EVENT_ID: {eid}")
            ev = self.news_by_id[eid]
            refs.append({
                "refType": "NEWS_EVENT",
                "id": eid,
                "headline": ev.get("headline"),
                "publishedAt": ev.get("publishedAt"),
                "sourceUrl": ev.get("sourceUrl"),
                "evidenceSha256": ev.get("evidenceSha256")
            })
        for fid in fact_ids:
            if fid not in self.unique_facts_by_id:
                raise ValueError(f"CHAIN_INVALID_OR_DUPLICATE_FACT_ID: {fid}")
            fact = self.unique_facts_by_id[fid]
            refs.append({
                "refType": "FINANCIAL_FACT",
                "id": fid,
                "eventId": fact.get("eventId"),
                "extractedExpression": fact.get("extractedExpression"),
                "verifiedEntity": fact.get("verifiedEntity")
            })
        for mid in mp_ids:
            if mid not in self.mp_by_id:
                raise ValueError(f"CHAIN_UNRESOLVED_MP_ID: {mid}")
            mp = self.mp_by_id[mid]
            refs.append({
                "refType": "MARKET_PULSE",
                "id": mid,
                "indicatorName": mp.get("indicatorName"),
                "actualValue": mp.get("actualValue"),
                "unit": mp.get("unit"),
                "observationDate": mp.get("observationDate"),
                "updateStatus": mp.get("updateStatus"),
                "verificationStatus": mp.get("verificationStatus")
            })
        return refs

    def generate_chains(self) -> Dict[str, Any]:
        raw_chains = [
            {
                "chainId": "CHAIN-01",
                "macroDriver": (
                    "[OBSERVED] Tỷ lệ tín dụng/GDP đã lên tới 135–140% GDP và khoảng 80% nhu cầu vốn của nền kinh tế "
                    "đi qua hệ thống ngân hàng (EVT-20261110-001, EVT-20261110-016), trong khi người dân chủ yếu gửi tiết kiệm "
                    "ngắn hạn (~1 năm) còn nhu cầu vay đầu tư kéo dài 5–10 năm (như 830.000 tỷ đồng vốn đầu tư của EVN)."
                ),
                "transmissionMechanism": (
                    "Sự lệch pha kỳ hạn giữa nguồn vốn huy động ngắn hạn và nhu cầu vay trung – dài hạn buộc các ngân hàng "
                    "phải duy trì lãi suất tiền gửi kỳ hạn 12–18 tháng ở mức hấp dẫn để giữ ổn định nguồn vốn. Chi phí huy động đầu vào "
                    "này truyền dẫn sang mặt bằng lãi suất cho vay doanh nghiệp và chi phí tài chính của người tiêu dùng."
                ),
                "bankingImpact": (
                    "[OBSERVED] Ngày 10/11/2026, có 5 ngân hàng thương mại (MBV, PGBank, Sacombank, VCBNeo, VIB) cùng niêm yết "
                    "lãi suất tiền gửi trực tuyến kỳ hạn 12 tháng ở mức 7%/năm, kỳ hạn 18 tháng đạt tới 7,4%/năm (EVT-20261110-005, MP-03), "
                    "cho thấy chi phí vốn huy động (COF) kỳ hạn từ 1 năm trở lên đang neo ở vùng cao."
                ),
                "enterpriseImpact": (
                    "[OBSERVED & SUPPORTED_INFERENCE] Khi kênh trái phiếu doanh nghiệp vẫn phụ thuộc vào bảo lãnh và mua lại của ngân hàng "
                    "('tuy hai mà một' - EVT-20261110-016), các doanh nghiệp sản xuất, bán lẻ và hạ tầng phải chịu chi phí vốn vay cao hơn "
                    "và cần tối ưu vòng quay vốn lưu động nhanh hơn để giảm áp lực lãi vay."
                ),
                "consumerImpact": (
                    "[SUPPORTED_INFERENCE] Lãi suất tiết kiệm 12 tháng ở mức 7%/năm cùng giá vàng SJC neo quanh 138,5–141,5 triệu đồng/lượng "
                    "(EVT-20261110-021) khuyến khích người có tiền nhàn rỗi duy trì tích lũy tài sản an toàn và cân nhắc kỹ hơn trước các khoản chi tiêu lớn."
                ),
                "paymentImpact": (
                    "[HYPOTHESIS] Để kích cầu các mặt hàng giá trị cao (điện máy, xe máy/xe điện, giáo dục, chăm sóc sức khỏe) khi người mua "
                    "không muốn rút sổ tiết kiệm trước hạn, nhu cầu sử dụng giải pháp trả góp 0% lãi suất qua thẻ/SmartPOS/cổng thanh toán "
                    "và giải pháp đối soát dòng tiền nhanh cho merchant có thể tăng lên trong quý IV/2026 – quý I/2027."
                ),
                "supportingEventIds": [
                    "EVT-20261110-001",
                    "EVT-20261110-016",
                    "EVT-20261110-005",
                    "EVT-20261110-010",
                    "EVT-20261110-021"
                ],
                "supportingFactIds": [
                    "FACT-20261110-001",
                    "FACT-20261110-010",
                    "FACT-20261110-015",
                    "FACT-20261110-004",
                    "FACT-20261110-012"
                ],
                "supportingMarketPulseIds": [
                    "MP-03",
                    "MP-05"
                ],
                "inferenceClassification": {
                    "macroDriver": "OBSERVED",
                    "bankingImpact": "OBSERVED",
                    "enterpriseImpact": "SUPPORTED_INFERENCE",
                    "consumerImpact": "SUPPORTED_INFERENCE",
                    "paymentImpact": "HYPOTHESIS"
                },
                "confidenceLevel": "HIGH",
                "potentialTimeLag": "1 đến 3 tháng (truyền dẫn từ biểu lãi suất huy động 12T sang điều kiện tín dụng và hành vi trả góp mùa cuối năm)",
                "watchSignals": [
                    "Biểu lãi suất huy động 12 tháng của nhóm Big 4 và các NHTM cổ phần lớn trong nửa cuối tháng 11/2026.",
                    "Tỷ trọng giao dịch trả góp (Installment) trên tổng giá trị giao dịch (GMV) tại các ngành hàng điện máy, giáo dục và xe hai bánh.",
                    "Số liệu công bố chính thức về tăng trưởng tín dụng toàn hệ thống từ NHNN (MP-05 hiện mới có cập nhật định tính)."
                ]
            },
            {
                "chainId": "CHAIN-02",
                "macroDriver": (
                    "[OBSERVED] Từ ngày 11/11/2026, Ngân hàng Nhà nước triển khai mua ngoại tệ (USD) giao ngay ở mức 25.500 đồng/USD "
                    "(EVT-20261110-006) trong bối cảnh tỷ giá trung tâm ngày 10/11 niêm yết ở mức 25.600 đồng/USD, giảm 10 đồng (MP-01)."
                ),
                "transmissionMechanism": (
                    "Khi NHNN mua USD từ các ngân hàng thương mại, một lượng tiền đồng (VND) tương ứng được bơm trực tiếp ra hệ thống. "
                    "Khác với nghiệp vụ OMO có kỳ hạn hoàn trả ngắn (quan sát lịch sử gần nhất MP-08 là ngày 21/09/2026 với 47.915 tỷ VND), "
                    "mua USD giao ngay bổ sung thanh khoản tiền đồng bền vững hơn cho mùa cao điểm thanh toán cuối năm."
                ),
                "bankingImpact": (
                    "[SUPPORTED_INFERENCE] Các ngân hàng thương mại có nguồn ngoại tệ dồi dào có thêm kênh chuyển đổi sang VND ngay lập tức, "
                    "giúp giảm áp lực thiếu hụt thanh khoản tiền đồng cục bộ vào dịp quyết toán cuối năm."
                ),
                "enterpriseImpact": (
                    "[OBSERVED & SUPPORTED_INFERENCE] Tâm lý thị trường vốn và doanh nghiệp khởi sắc rõ rệt: chỉ số VN-Index phiên 10/11 tăng "
                    "28,75 điểm (+1,68%) lên 1.743,00 điểm (MP-04); các doanh nghiệp xuất nhập khẩu hưởng lợi từ biên độ tỷ giá ổn định hơn."
                ),
                "consumerImpact": (
                    "[HYPOTHESIS] Sự phục hồi của thị trường chứng khoán (VN-Index vượt 1.740 điểm) và tỷ giá ổn định có thể hỗ trợ hiệu ứng "
                    "tài sản (wealth effect) tích cực cho nhóm khách hàng thu nhập trung – cao tại đô thị trong mùa mua sắm cuối năm."
                ),
                "paymentImpact": (
                    "[HYPOTHESIS] Thanh khoản hệ thống ngân hàng thông suốt và tâm lý thị trường tích cực là điều kiện thuận lợi để dòng tiền "
                    "giao dịch qua cổng thanh toán trực tuyến, chuyển khoản nhanh 24/7 và thanh toán hóa đơn duy trì nhịp tăng trưởng cao dịp cuối năm."
                ),
                "supportingEventIds": [
                    "EVT-20261110-006",
                    "EVT-20261110-026"
                ],
                "supportingFactIds": [
                    "FACT-20261110-005",
                    "FACT-20261110-009"
                ],
                "supportingMarketPulseIds": [
                    "MP-01",
                    "MP-04",
                    "MP-02",
                    "MP-08"
                ],
                "inferenceClassification": {
                    "macroDriver": "OBSERVED",
                    "bankingImpact": "SUPPORTED_INFERENCE",
                    "enterpriseImpact": "OBSERVED",
                    "consumerImpact": "HYPOTHESIS",
                    "paymentImpact": "HYPOTHESIS"
                },
                "confidenceLevel": "HIGH",
                "potentialTimeLag": "Tức thì đến 4 tuần (bắt đầu từ ngày 11/11/2026 khi NHNN thực hiện giao dịch mua USD giao ngay)",
                "watchSignals": [
                    "Doanh số bán USD giao ngay thực tế của các NHTM cho NHNN từ ngày 11/11/2026.",
                    "Cập nhật số liệu lãi suất liên ngân hàng qua đêm mới (hiện MP-02 đang ở mức 2,8%/năm ngày 02/10/2026 - STALE_OBSERVATION).",
                    "Diễn biến thanh khoản và điểm số VN-Index quanh ngưỡng 1.743 điểm."
                ]
            },
            {
                "chainId": "CHAIN-03",
                "macroDriver": (
                    "[OBSERVED] Quốc hội thông qua dự toán ngân sách năm 2027 với tổng thu 3.334.338 tỷ đồng, tổng mức vay 1.279.717 tỷ đồng "
                    "(EVT-20261110-032), Chính phủ ban hành Nghị quyết 358/NQ-CP ưu tiên đầu tư trục Bắc – Nam và hành lang Đông – Tây (EVT-20261110-017), "
                    "đồng thời VCCI kiến nghị quy định rõ ngưỡng nợ thuế áp dụng tạm hoãn xuất cảnh: trên 200 triệu đồng với cá nhân/hộ kinh doanh "
                    "và trên 1 tỷ đồng với doanh nghiệp (EVT-20261110-020)."
                ),
                "transmissionMechanism": (
                    "Chính sách mở rộng đầu tư hạ tầng đi đôi với kỷ luật thu ngân sách và quản lý nợ thuế tạo ra áp lực tuân thủ minh bạch: "
                    "các doanh nghiệp và hộ kinh doanh muốn tham gia chuỗi cung ứng hoặc tránh rủi ro pháp lý về thuế cần chuẩn hóa ghi nhận doanh thu và nghĩa vụ nộp thuế."
                ),
                "bankingImpact": (
                    "[SUPPORTED_INFERENCE] Các ngân hàng thương mại gia tăng vai trò thu ngân sách nhà nước, tài trợ chuỗi cung ứng hạ tầng "
                    "và cung cấp tài khoản định danh chuyên biệt cho hộ kinh doanh tách bạch dòng tiền cá nhân – kinh doanh."
                ),
                "enterpriseImpact": (
                    "[SUPPORTED_INFERENCE] Hộ kinh doanh cá thể và doanh nghiệp SME có động lực rõ rệt để theo dõi sát nghĩa vụ thuế "
                    "(đặc biệt quanh ngưỡng tham chiếu 200 triệu đồng và 1 tỷ đồng) và số hóa quy trình xuất hóa đơn – đối soát doanh thu."
                ),
                "consumerImpact": (
                    "[HYPOTHESIS] Người tiêu dùng khi giao dịch tại các hộ kinh doanh, cửa hàng bán lẻ, dịch vụ ăn uống sẽ ngày càng quen thuộc "
                    "với việc thanh toán qua mã QR định danh cửa hàng gắn với hóa đơn điện tử khởi tạo từ máy tính tiền."
                ),
                "paymentImpact": (
                    "[SUPPORTED_INFERENCE] Thúc đẩy nhu cầu đối với các giải pháp thiết bị chấp nhận thanh toán tích hợp phần mềm quản lý bán hàng, "
                    "xuất hóa đơn điện tử, dịch vụ thu hộ ngân sách/thu hộ hóa đơn và thông báo biến động số dư tự động cho merchant."
                ),
                "supportingEventIds": [
                    "EVT-20261110-032",
                    "EVT-20261110-017",
                    "EVT-20261110-020",
                    "EVT-20261110-022"
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
                "inferenceClassification": {
                    "macroDriver": "OBSERVED",
                    "bankingImpact": "SUPPORTED_INFERENCE",
                    "enterpriseImpact": "SUPPORTED_INFERENCE",
                    "consumerImpact": "HYPOTHESIS",
                    "paymentImpact": "SUPPORTED_INFERENCE"
                },
                "confidenceLevel": "MEDIUM",
                "potentialTimeLag": "3 đến 12 tháng (theo lộ trình hoàn thiện văn bản pháp luật thuế và triển khai đầu tư công 2026–2027)",
                "watchSignals": [
                    "Quyết định chính thức của cơ quan lập pháp về ngưỡng nợ thuế tạm hoãn xuất cảnh đối với hộ kinh doanh và doanh nghiệp.",
                    "Tỷ lệ hộ kinh doanh chuyển đổi sang sử dụng POS/SmartPOS tích hợp hóa đơn điện tử và QR động định danh."
                ]
            },
            {
                "chainId": "CHAIN-04",
                "macroDriver": (
                    "[OBSERVED] Khách du lịch quốc tế đến Việt Nam 10 tháng đầu năm 2026 đạt 19,5 triệu lượt (MP-07, tính đến 31/10/2026), "
                    "rút ngắn khoảng cách với Thái Lan (25,4 triệu lượt) xuống còn 5,9 triệu lượt; đồng thời thị trường nội địa bước vào "
                    "cao điểm mua sắm trực tuyến 11.11 với sản lượng vận chuyển hàng nặng tăng mạnh (EVT-20261110-004)."
                ),
                "transmissionMechanism": (
                    "Dòng khách quốc tế quy mô gần 20 triệu lượt tạo ra nhu cầu thanh toán trực tiếp tại các điểm bán lẻ, khách sạn, ẩm thực "
                    "bằng cả thẻ quốc tế lẫn mã QR xuyên biên giới (VietQR Global - MP-06), trong khi mùa siêu sale 11.11 thúc đẩy giao dịch "
                    "thương mại điện tử và thanh toán khi giao nhận hàng (COD/non-cash COD) đối với hàng cồng kềnh, giá trị lớn."
                ),
                "bankingImpact": (
                    "[OBSERVED & SUPPORTED_INFERENCE] Các ngân hàng và tổ chức chuyển mạch (NAPAS) đẩy mạnh kết nối thanh toán xuyên biên giới "
                    "(VietQR Global - MP-06) nhằm đưa khả năng chấp nhận thanh toán quốc tế xuống tận từng điểm bán lẻ (merchant)."
                ),
                "enterpriseImpact": (
                    "[OBSERVED] Các doanh nghiệp logistics (như J&T Cargo - EVT-20261110-004) và chuỗi bán lẻ, du lịch chủ động tăng cường "
                    "năng lực vận hành, xử lý đơn hàng nặng và tối ưu quy trình thu tiền tại điểm bán cũng như khi giao hàng."
                ),
                "consumerImpact": (
                    "[SUPPORTED_INFERENCE] Du khách quốc tế kỳ vọng trải nghiệm quét mã QR hoặc chạm thẻ liền mạch tại Việt Nam tương tự như "
                    "tại Thái Lan; người tiêu dùng nội địa tập trung mua sắm hàng gia dụng/hàng nặng trong các đợt siêu sale 11.11."
                ),
                "paymentImpact": (
                    "[SUPPORTED_INFERENCE] Gia tăng trực tiếp nhu cầu trang bị SmartPOS đa phương thức (chấp nhận thẻ quốc tế + VietQR + "
                    "VietQR Global), Payment Link / QR động cho đội ngũ giao nhận (shipper) hàng nặng và cổng thanh toán cho sàn/D2C."
                ),
                "supportingEventIds": [
                    "EVT-20261110-004"
                ],
                "supportingFactIds": [],
                "supportingMarketPulseIds": [
                    "MP-07",
                    "MP-06"
                ],
                "inferenceClassification": {
                    "macroDriver": "OBSERVED",
                    "bankingImpact": "SUPPORTED_INFERENCE",
                    "enterpriseImpact": "OBSERVED",
                    "consumerImpact": "SUPPORTED_INFERENCE",
                    "paymentImpact": "SUPPORTED_INFERENCE"
                },
                "confidenceLevel": "HIGH",
                "potentialTimeLag": "Hiện hữu ngay trong quý IV/2026 (mùa cao điểm lễ hội 11.11 – Tết Dương lịch và mùa cao điểm khách quốc tế)",
                "watchSignals": [
                    "Số lượng điểm chấp nhận thanh toán (merchant acceptance points) kích hoạt tính năng VietQR Global.",
                    "Sản lượng giao dịch qua SmartPOS và QR tại nhóm ngành Khách sạn, Nhà hàng (F&B), Bán lẻ du lịch và Giao nhận (Logistics)."
                ]
            }
        ]

        chains_out = []
        for ch in raw_chains:
            for k, v in ch["inferenceClassification"].items():
                if v not in VALID_INFERENCE_LEVELS:
                    raise ValueError(f"INVALID_INFERENCE_CLASSIFICATION: {k}={v}")
            ch["evidenceReferences"] = self._build_evidence_refs(
                ch["supportingEventIds"],
                ch["supportingFactIds"],
                ch["supportingMarketPulseIds"]
            )
            chains_out.append(ch)

        return {
            "totalChains": len(chains_out),
            "chains": chains_out
        }
