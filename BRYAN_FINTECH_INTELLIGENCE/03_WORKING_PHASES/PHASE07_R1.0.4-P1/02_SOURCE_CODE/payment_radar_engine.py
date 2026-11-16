#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
payment_radar_engine.py
=======================
Workstream C — Payment Radar Engine for Bryan FinTech Intelligence Phase 06.

Evaluates verified news events, audited financial facts, and Market Pulse context
across the 10 payment industry domains and key merchant verticals (F&B, Retail,
Tourism/Hospitality, Private Education, Spa/Wellness, Two-Wheelers/EV, D2C,
E-commerce, Cross-border), applying the Payoo Commercial Lens honestly without
inventing corporate leads or forcing Payoo relevance onto non-commercial macro news.
"""

from typing import Dict, List, Any

VALID_OPPORTUNITY_TYPES = {
    "VERIFIED_OPPORTUNITY",
    "EMERGING_OPPORTUNITY",
    "POTENTIAL_OPPORTUNITY",
    "NO_DIRECT_OPPORTUNITY",
}


class PaymentRadarEngine:
    """
    Identifies grounded payment market signals and commercial opportunities,
    explicitly marking NO_DIRECT_PAYOO_OPPORTUNITY when no genuine Payoo fit exists.
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
        if not event_ids and not mp_ids:
            raise ValueError("PAYMENT_RADAR_UNGROUNDED_SIGNAL: Must reference at least one verified event or Market Pulse indicator.")
        refs = []
        for eid in event_ids:
            if eid not in self.news_by_id:
                raise ValueError(f"RADAR_UNRESOLVED_EVENT_ID: {eid}")
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
                raise ValueError(f"RADAR_INVALID_OR_DUPLICATE_FACT_ID: {fid}")
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
                raise ValueError(f"RADAR_UNRESOLVED_MP_ID: {mid}")
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
        return refs

    def generate_radar_signals(self) -> Dict[str, Any]:
        raw_signals = [
            {
                "radarId": "RADAR-01",
                "signalTitle": "Mở rộng hạ tầng chấp nhận thanh toán xuyên biên giới (VietQR Global) và SmartPOS tại điểm bán đón 19,5 triệu lượt khách quốc tế",
                "paymentDomain": "VietQRGlobal & Cross-border Payment / POS & SmartPOS / Merchant Acquiring",
                "marketSignal": (
                    "Lượng khách quốc tế đến Việt Nam đạt 19,5 triệu lượt (tính đến 31/10/2026 - MP-07, VERIFIED), "
                    "rút ngắn khoảng cách với Thái Lan (25,4 triệu lượt) xuống còn 5,9 triệu lượt, đồng thời bài toán trọng tâm "
                    "của thị trường thanh toán hiện nay là đưa khả năng chấp nhận VietQR Global từ cấp độ kết nối liên ngân hàng "
                    "xuống tận từng điểm bán vật lý (MP-06, QUALITATIVE_UPDATE_ONLY)."
                ),
                "triggerEventIds": [
                    "EVT-20261110-022"
                ],
                "supportingFacts": [],
                "supportingMarketPulseIds": [
                    "MP-07",
                    "MP-06"
                ],
                "marketDrivers": [
                    "Sự phục hồi mạnh mẽ của dòng khách du lịch quốc tế (19,5 triệu lượt trong 10 tháng năm 2026).",
                    "Nhu cầu thanh toán liền mạch bằng ứng dụng ngân hàng/ví điện tử bản địa của du khách châu Á (Nhật Bản, Hàn Quốc, Thái Lan, Trung Quốc, ASEAN) khi chi tiêu tại Việt Nam.",
                    "Khoảng trống vận hành giữa kết nối kỹ thuật cấp chuyển mạch (NAPAS) và độ phủ thực tế tại quầy thu ngân của merchant."
                ],
                "merchantImpact": (
                    "Các cơ sở lưu trú, nhà hàng, chuỗi bán lẻ tại các thành phố du lịch cần một thiết bị/luồng đối soát thống nhất "
                    "vừa nhận được thẻ quốc tế (Visa/Mastercard/JCB), vừa hiển thị mã QR động chấp nhận thanh toán xuyên biên giới mà thu ngân không phải thao tác phức tạp."
                ),
                "consumerImpact": (
                    "Du khách quốc tế có thể quét mã QR trực tiếp từ ứng dụng ngân hàng quê nhà với tỷ giá minh bạch thay vì phải đổi tiền mặt mệnh giá nhỏ."
                ),
                "affectedSegments": [
                    "Du lịch, khách sạn và khu nghỉ dưỡng",
                    "Nhà hàng và chuỗi F&B tại các đô thị du lịch (Hà Nội, TP.HCM, Đà Nẵng, Nha Trang, Phú Quốc)",
                    "Retail và chuỗi bán lẻ đặc sản, miễn thuế, trung tâm thương mại",
                    "Spa, thẩm mỹ và wellness phục vụ khách quốc tế",
                    "Doanh nghiệp có giao dịch xuyên biên giới (Việt Nam – Nhật Bản và nội khối châu Á)"
                ],
                "paymentImplication": (
                    "Hình thành nhu cầu tích hợp VietQR Global và thẻ quốc tế trên cùng một thiết bị SmartPOS / hệ thống Omnichannel POS "
                    "kèm báo cáo đối soát đa ngoại tệ – quyết toán VND tự động."
                ),
                "opportunity": (
                    "Triển khai gói giải pháp chấp nhận thanh toán toàn diện (All-in-One SmartPOS: Thẻ quốc tế + VietQR nội địa + VietQR Global) "
                    "cho nhóm chuỗi F&B, khách sạn, bán lẻ và wellness tại các trọng điểm du lịch trước thềm cao điểm cuối năm."
                ),
                "commercialRelevance": "HIGH",
                "payooRelevance": (
                    "Phù hợp trực tiếp với thế mạnh mạng lưới Merchant Acquiring, SmartPOS và giải pháp thanh toán hợp kênh (Omnichannel) của Payoo: "
                    "giúp merchant chỉ cần một đầu mối tích hợp để nhận cả thẻ quốc tế lẫn QR xuyên biên giới và đối soát tự động trên một cổng duy nhất."
                ),
                "opportunityType": "EMERGING_OPPORTUNITY",
                "riskFactors": [
                    "Chỉ số MP-06 hiện mới là cập nhật định tính (QUALITATIVE_UPDATE_ONLY), chưa có số liệu định lượng công bố về sản lượng giao dịch thực tế của VietQR Global tại điểm bán.",
                    "Cần đào tạo nhân viên thu ngân tại điểm bán (cashier) nhận diện và hướng dẫn khách quốc tế quét đúng chuẩn mã QR liên thông."
                ],
                "recommendedMonitoring": [
                    "Theo dõi lộ trình mở rộng ngân hàng thành viên và quốc gia kết nối VietQR Global của NAPAS.",
                    "Theo dõi tỷ trọng giao dịch thẻ quốc tế và QR tại các merchant ngành Khách sạn, F&B và Bán lẻ du lịch trong tháng 11–12/2026."
                ],
                "confidenceLevel": "HIGH"
            },
            {
                "radarId": "RADAR-02",
                "signalTitle": "Nhu cầu thanh toán không tiền mặt khi giao hàng (Non-cash COD / Payment Link / QR động) cho đơn hàng nặng và giá trị cao dịp siêu sale 11.11",
                "paymentDomain": "E-commerce Payment / Payment Link / QR Payment & VietQR / Omnichannel Payment",
                "marketSignal": (
                    "Mùa mua sắm 11.11 ghi nhận áp lực gia tăng đơn hàng thương mại điện tử, đặc biệt ở phân khúc hàng nặng và hàng cồng kềnh "
                    "(EVT-20261110-004: J&T Cargo chủ động nguồn lực vận chuyển hàng nặng)."
                ),
                "triggerEventIds": [
                    "EVT-20261110-004",
                    "EVT-20261110-005"
                ],
                "supportingFacts": [
                    "FACT-20261110-001"
                ],
                "supportingMarketPulseIds": [
                    "MP-03"
                ],
                "marketDrivers": [
                    "Chiến dịch khuyến mãi 11.11 thúc đẩy người tiêu dùng đặt mua các mặt hàng gia dụng, nội thất, thiết bị điện máy và hàng cồng kềnh qua kênh online/D2C.",
                    "Giá trị mỗi đơn hàng nặng thường cao hơn đơn hàng tiêu dùng nhanh, khiến việc thu tiền mặt (COD truyền thống) tiềm ẩn rủi ro bảo quản tiền mặt và chậm vòng quay vốn cho cả nhà bán hàng lẫn đơn vị vận chuyển."
                ],
                "merchantImpact": (
                    "Các doanh nghiệp D2C, chuỗi điện máy – nội thất và đơn vị giao nhận cần công cụ tạo mã QR động theo từng mã vận đơn hoặc gửi Payment Link/chấp nhận trả góp ngay tại thời điểm giao hàng và lắp đặt."
                ),
                "consumerImpact": (
                    "Người mua hàng nặng/điện máy muốn kiểm tra hàng khi nhận rồi mới thanh toán bằng quét mã QR hoặc quẹt thẻ trả góp tại nhà thay vì chuẩn bị sẵn lượng tiền mặt lớn."
                ),
                "affectedSegments": [
                    "Thương mại điện tử và các đơn vị Logistics / Giao nhận hàng nặng",
                    "Doanh nghiệp D2C (điện máy, gia dụng, nội thất, thiết bị tập luyện)",
                    "Retail và chuỗi bán lẻ đa kênh (Omnichannel)",
                    "Xe máy, xe điện và đại lý phân phối"
                ],
                "paymentImplication": (
                    "Gia tăng nhu cầu đối với giải pháp QR động gắn mã đơn hàng trên ứng dụng của shipper (Non-cash COD), "
                    "Payment Link gửi qua Zalo/SMS và thiết bị mPOS/SmartPOS di động hỗ trợ trả góp tại điểm giao hàng."
                ),
                "opportunity": (
                    "Cung cấp giải pháp thu hộ COD không tiền mặt (QR động định danh theo đơn hàng + đối soát thời gian thực qua API) "
                    "và Payment Link tích hợp trả góp cho các đơn vị logistics hàng nặng và thương hiệu D2C điện máy/nội thất."
                ),
                "commercialRelevance": "HIGH",
                "payooRelevance": (
                    "Phù hợp trực tiếp với bộ sản phẩm Payment Link, QR Payment định danh đơn hàng, SmartPOS di động và cổng thanh toán "
                    "Omnichannel của Payoo dành cho ngành bán lẻ điện máy, nội thất và giao nhận."
                ),
                "opportunityType": "VERIFIED_OPPORTUNITY",
                "riskFactors": [
                    "Đòi hỏi tích hợp API đồng bộ trạng thái đơn hàng tức thời giữa hệ thống quản lý vận đơn (TMS/OMS) của đối tác logistics và cổng thanh toán.",
                    "Tỷ lệ hủy đơn hoặc đổi trả đối với hàng cồng kềnh cần quy trình hoàn tiền (refund reconciliation) tự động rõ ràng."
                ],
                "recommendedMonitoring": [
                    "Theo dõi sản lượng giao dịch qua Payment Link và QR động tại nhóm merchant điện máy, gia dụng và logistics trong tuần lễ 11.11 và Black Friday.",
                    "Theo dõi tỷ lệ chuyển đổi từ COD tiền mặt sang quét mã QR khi nhận hàng."
                ],
                "confidenceLevel": "HIGH"
            },
            {
                "radarId": "RADAR-03",
                "signalTitle": "Thúc đẩy thanh toán trả góp (Installment / BNPL) tại các ngành dịch vụ – bán lẻ giá trị cao khi lãi suất tiền gửi 12T đạt 7%/năm",
                "paymentDomain": "Installment Payment / BNPL / Payment Gateway / POS & SmartPOS",
                "marketSignal": (
                    "Lãi suất tiền gửi trực tuyến kỳ hạn 12 tháng tại 5 ngân hàng thương mại đã đạt mức 7%/năm (kỳ hạn 18 tháng đạt 7,4%/năm - "
                    "EVT-20261110-005, FACT-20261110-001, MP-03), trong khi giá vàng SJC duy trì vùng cao 138,5–141,5 triệu đồng/lượng (EVT-20261110-021, FACT-20261110-012)."
                ),
                "triggerEventIds": [
                    "EVT-20261110-005",
                    "EVT-20261110-001",
                    "EVT-20261110-021"
                ],
                "supportingFacts": [
                    "FACT-20261110-001",
                    "FACT-20261110-012",
                    "FACT-20261110-015"
                ],
                "supportingMarketPulseIds": [
                    "MP-03"
                ],
                "marketDrivers": [
                    "Khi lãi suất tiết kiệm 12 tháng ở mức 7%/năm, chi phí cơ hội của việc rút tiền gửi trước hạn để thanh toán một lần (lump-sum) cho các khoản chi tiêu lớn tăng lên.",
                    "Chênh lệch kỳ hạn vốn ngân hàng (EVT-20261110-001) khiến các khoản vay tiêu dùng thông thường có lãi suất cao hơn, làm tăng sức hấp dẫn của các chương trình trả góp 0% lãi suất qua thẻ tín dụng do merchant và ngân hàng đồng tài trợ."
                ],
                "merchantImpact": (
                    "Các trường tư thục/trung tâm đào tạo, viện thẩm mỹ/wellness, đại lý xe máy – xe điện và chuỗi bán lẻ công nghệ cần công cụ "
                    "chuyển đổi trả góp kỳ hạn 3–12 tháng ngay tại quầy hoặc qua link thanh toán từ xa để chốt đơn dễ dàng hơn."
                ),
                "consumerImpact": (
                    "Khách hàng cá nhân ưu tiên giữ nguyên khoản tiền gửi tiết kiệm hưởng lãi suất 7%/năm và sử dụng hạn mức thẻ tín dụng "
                    "để chia nhỏ khoản chi học phí, làm đẹp, mua xe hoặc thiết bị công nghệ thành 6–12 kỳ thanh toán."
                ),
                "affectedSegments": [
                    "Giáo dục tư nhân (trường quốc tế, trung tâm ngoại ngữ, khóa học kỹ năng/công nghệ)",
                    "Spa, thẩm mỹ viện, nha khoa và wellness",
                    "Xe máy, xe điện và hệ thống đại lý phân phối",
                    "Retail và chuỗi bán lẻ thiết bị công nghệ, điện máy"
                ],
                "paymentImplication": (
                    "Tăng nhu cầu kết nối cổng trả góp 0% đa ngân hàng (Multi-bank Credit Card Installment) trên cả SmartPOS tại điểm bán và Payment Link / Payment Gateway trực tuyến."
                ),
                "opportunity": (
                    "Mở rộng gói giải pháp Trả góp 0% đa ngân hàng qua SmartPOS và Payment Link cho nhóm ngành Giáo dục tư nhân (kỳ thu học phí học kỳ II), "
                    "Spa/Wellness (mùa làm đẹp cuối năm) và Đại lý xe máy/xe điện."
                ),
                "commercialRelevance": "MEDIUM",
                "payooRelevance": (
                    "Phù hợp với mạng lưới liên kết trả góp thẻ tín dụng rộng khắp các ngân hàng của Payoo trên cả kênh SmartPOS tại quầy "
                    "lẫn Payment Link từ xa (không yêu cầu khách hàng phải có mặt tại quầy để quẹt thẻ vật lý)."
                ),
                "opportunityType": "POTENTIAL_OPPORTUNITY",
                "riskFactors": [
                    "Chi phí phí chuyển đổi trả góp (merchant discount rate / installment fee) tăng theo mặt bằng lãi suất có thể khiến một số merchant nhỏ ngần ngại tài trợ 100% phí chuyển đổi cho khách mua.",
                    "Hạn mức tín dụng thẻ của một bộ phận khách hàng có thể đã được sử dụng cao vào cuối năm."
                ],
                "recommendedMonitoring": [
                    "Theo dõi biểu phí chuyển đổi trả góp của các ngân hàng phát hành thẻ trong quý IV/2026.",
                    "Theo dõi tỷ lệ giao dịch trả góp kỳ hạn 6 tháng và 12 tháng tại nhóm merchant Giáo dục, Chăm sóc sức khỏe – Thẩm mỹ và Xe điện."
                ],
                "confidenceLevel": "MEDIUM"
            },
            {
                "radarId": "RADAR-04",
                "signalTitle": "Nhu cầu chuẩn hóa thu hộ, đối soát doanh thu và thanh toán số tại hộ kinh doanh & SME trước đề xuất ngưỡng nợ thuế 200 triệu / 1 tỷ đồng",
                "paymentDomain": "Payment Infrastructure & Banking API / QR Payment & VietQR / POS & SmartPOS",
                "marketSignal": (
                    "VCCI kiến nghị quy định rõ ngưỡng nợ thuế áp dụng biện pháp tạm hoãn xuất cảnh ở mức trên 200 triệu đồng đối với cá nhân, "
                    "hộ kinh doanh và trên 1 tỷ đồng đối với doanh nghiệp (EVT-20261110-020, FACT-20261110-006, FACT-20261110-007), "
                    "trong bối cảnh Quốc hội chốt chỉ tiêu thu ngân sách năm 2027 đạt 3.334.338 tỷ đồng (EVT-20261110-032, FACT-20261110-014)."
                ),
                "triggerEventIds": [
                    "EVT-20261110-020",
                    "EVT-20261110-032"
                ],
                "supportingFacts": [
                    "FACT-20261110-006",
                    "FACT-20261110-007",
                    "FACT-20261110-014"
                ],
                "supportingMarketPulseIds": [],
                "marketDrivers": [
                    "Áp lực tuân thủ thuế và minh bạch hóa dòng tiền kinh doanh của nhóm hộ kinh doanh cá thể có doanh thu lớn và doanh nghiệp SME.",
                    "Yêu cầu kết nối đồng bộ giữa dữ liệu thanh toán tại điểm bán với hóa đơn điện tử và nghĩa vụ nộp thuế định kỳ."
                ],
                "merchantImpact": (
                    "Hộ kinh doanh và doanh nghiệp SME cần tách bạch tài khoản nhận tiền bán hàng với tài khoản cá nhân, đồng thời sử dụng giải pháp "
                    "thanh toán có báo cáo đối soát rõ ràng để kê khai và nộp thuế đúng hạn, tránh phát sinh nợ thuế quá hạn."
                ),
                "consumerImpact": (
                    "Khách hàng mua sắm tại các hộ kinh doanh F&B, bán lẻ được cung cấp hóa đơn điện tử và phương thức quét mã QR động chuyên nghiệp hơn."
                ),
                "affectedSegments": [
                    "Nhà hàng và F&B (hộ kinh doanh chuỗi quán ăn, cà phê)",
                    "Retail và cửa hàng bán lẻ chuyên doanh",
                    "Doanh nghiệp vừa và nhỏ (SME) dịch vụ – thương mại"
                ],
                "paymentImplication": (
                    "Nhu cầu tích hợp thiết bị chấp nhận thanh toán (QR/SmartPOS/loa thông báo tiền về) với phần mềm kế toán – hóa đơn điện tử "
                    "và tiện ích nộp thuế/phí trực tuyến."
                ),
                "opportunity": (
                    "Tích hợp sâu giải pháp thanh toán QR/SmartPOS với các nền tảng phần mềm quản lý bán hàng – hóa đơn điện tử và cổng thu hộ ngân sách/hóa đơn cho phân khúc SME và hộ kinh doanh."
                ),
                "commercialRelevance": "MEDIUM",
                "payooRelevance": (
                    "Mở ra cơ hội hợp tác tích hợp (embedded payment & bill collection) giữa hạ tầng thu hộ/chấp nhận thanh toán của Payoo "
                    "với các đơn vị cung cấp phần mềm quản lý bán hàng và hóa đơn điện tử phục vụ SME."
                ),
                "opportunityType": "POTENTIAL_OPPORTUNITY",
                "riskFactors": [
                    "Ngưỡng 200 triệu đồng và 1 tỷ đồng hiện mới là đề xuất chính sách của VCCI (POLICY_THRESHOLD), cần chờ quy định pháp luật chính thức ban hành.",
                    "Một bộ phận hộ kinh doanh nhỏ lẻ vẫn có tâm lý e ngại chi phí đầu tư thiết bị ban đầu."
                ],
                "recommendedMonitoring": [
                    "Theo dõi tiến trình lấy ý kiến và ban hành văn bản hướng dẫn chính thức về ngưỡng nợ thuế áp dụng tạm hoãn xuất cảnh.",
                    "Theo dõi tốc độ áp dụng hóa đơn điện tử khởi tạo từ máy tính tiền tại nhóm ngành F&B và bán lẻ."
                ],
                "confidenceLevel": "MEDIUM"
            },
            {
                "radarId": "RADAR-05",
                "signalTitle": "Nghiệp vụ mua USD giao ngay của NHNN, vốn đầu tư hạ tầng điện lực EVN và hoạt động đấu thầu/CSR doanh nghiệp (Không phát sinh cơ hội thương mại trực tiếp cho Payoo)",
                "paymentDomain": "Payment Infrastructure & Banking API",
                "marketSignal": (
                    "NHNN triển khai mua USD giao ngay ở mức 25.500 đồng/USD từ ngày 11/11 để bơm tiền đồng cho hệ thống ngân hàng (EVT-20261110-006), "
                    "EVN xác định nhu cầu vốn đầu tư khoảng 830.000 tỷ đồng cho các dự án điện (EVT-20261110-010), SeABank thông báo mời thầu nội bộ "
                    "(EVT-20261110-008) và Nutifood đề xuất đầu tư công viên ven sông Sài Gòn (EVT-20261110-007)."
                ),
                "triggerEventIds": [
                    "EVT-20261110-006",
                    "EVT-20261110-010",
                    "EVT-20261110-008",
                    "EVT-20261110-007"
                ],
                "supportingFacts": [
                    "FACT-20261110-005",
                    "FACT-20261110-004"
                ],
                "supportingMarketPulseIds": [
                    "MP-01",
                    "MP-08"
                ],
                "marketDrivers": [
                    "Điều tiết thanh khoản tiền đồng và tỷ giá trên thị trường liên ngân hàng của NHNN.",
                    "Huy động vốn tín dụng hợp vốn và vốn đầu tư quốc tế quy mô hàng chục tỷ USD cho hạ tầng năng lượng quốc gia."
                ],
                "merchantImpact": (
                    "Tác động gián tiếp ở tầm vĩ mô giúp ổn định thanh khoản hệ thống ngân hàng và nguồn cung điện dài hạn, không làm thay đổi trực tiếp quy trình thu ngân tại điểm bán lẻ."
                ),
                "consumerImpact": (
                    "Không làm thay đổi trực tiếp hành vi thanh toán hàng ngày của người tiêu dùng cá nhân."
                ),
                "affectedSegments": [
                    "Khối Kinh doanh Vốn & Ngoại hối (Treasury) của các Ngân hàng Thương mại",
                    "Tập đoàn năng lượng nhà nước (EVN) và các định chế tài chính quốc tế"
                ],
                "paymentImplication": (
                    "Các giao dịch này diễn ra trên hệ thống thanh toán điện tử liên ngân hàng giá trị cao (IBPS) và kênh tín dụng dự án vĩ mô, "
                    "không thuộc phạm vi trung gian thanh toán bán lẻ."
                ),
                "opportunity": "NO_DIRECT_PAYOO_OPPORTUNITY",
                "commercialRelevance": "NONE",
                "payooRelevance": (
                    "NO_DIRECT_PAYOO_OPPORTUNITY: Đây là các nghiệp vụ điều hành tiền tệ liên ngân hàng của NHNN, huy động vốn dự án hạ tầng điện lực "
                    "cấp quốc gia và hoạt động đấu thầu/CSR riêng lẻ; không phát sinh cơ hội thương mại trực tiếp cho Payment Gateway, SmartPOS hay QR của Payoo."
                ),
                "opportunityType": "NO_DIRECT_OPPORTUNITY",
                "riskFactors": [
                    "Rủi ro phân tích sai lệch nếu gượng ép gắn kết các sự kiện vĩ mô/đấu thầu nội bộ thành cơ hội bán hàng trung gian thanh toán."
                ],
                "recommendedMonitoring": [
                    "Chỉ theo dõi ở góc độ bối cảnh thanh khoản vĩ mô (Macro Context) để đánh giá sức khỏe dòng tiền chung của nền kinh tế."
                ],
                "confidenceLevel": "HIGH"
            }
        ]

        signals_out = []
        for sig in raw_signals:
            if sig["opportunityType"] not in VALID_OPPORTUNITY_TYPES:
                raise ValueError(f"INVALID_OPPORTUNITY_TYPE: {sig['opportunityType']}")
            if sig["opportunityType"] == "NO_DIRECT_OPPORTUNITY" and "NO_DIRECT_PAYOO_OPPORTUNITY" not in sig["payooRelevance"]:
                raise ValueError("NO_DIRECT_OPPORTUNITY must explicitly state NO_DIRECT_PAYOO_OPPORTUNITY in payooRelevance.")
            sig["evidenceReferences"] = self._build_evidence_refs(
                sig["triggerEventIds"],
                sig["supportingFacts"],
                sig["supportingMarketPulseIds"]
            )
            signals_out.append(sig)

        return {
            "totalSignals": len(signals_out),
            "opportunityBreakdown": {
                "VERIFIED_OPPORTUNITY": sum(1 for s in signals_out if s["opportunityType"] == "VERIFIED_OPPORTUNITY"),
                "EMERGING_OPPORTUNITY": sum(1 for s in signals_out if s["opportunityType"] == "EMERGING_OPPORTUNITY"),
                "POTENTIAL_OPPORTUNITY": sum(1 for s in signals_out if s["opportunityType"] == "POTENTIAL_OPPORTUNITY"),
                "NO_DIRECT_OPPORTUNITY": sum(1 for s in signals_out if s["opportunityType"] == "NO_DIRECT_OPPORTUNITY")
            },
            "signals": signals_out
        }
