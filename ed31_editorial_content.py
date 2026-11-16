# -*- coding: utf-8 -*-
"""
Curated, Fact-Grounded Editorial Content Registry for ED-20261116-D01 (Edition 31 — 16/11/2026)
Every field is strictly anchored in verified source HTML snapshots in 05_LIVE_DATA/raw_evidence/.
Zero shared sentences across articles (>=25 chars); zero fake pull-quote marks on editorial analysis;
Cover Story Sapo = 3 sentences (250-320 chars); News Desk Sapo = 2 sentences (160-240 chars).
"""

ED31_COVER_OVERRIDE = {
    "targetOriginEventId": "EVT-20261116-048",
    "editorialHeadline": "6 năm qua, vốn hóa Vietcombank không tăng thậm chí sụt giảm - từng lớn hơn 10 ngân hàng tư nhân cộng lại, nay chưa bằng tổng giá trị Techcombank và VPBank",
    "editorialSubheadline": "Cơ cấu vốn hóa và lợi nhuận ngành ngân hàng phân cực mạnh mẽ khi khối NHTM tư nhân bứt phá vượt ngưỡng 1 tỷ USD lợi nhuận.",
    "dek": "Biến động vốn hóa phản ánh sự chuyển dịch động lực tăng trưởng từ khối ngân hàng quốc doanh sang các NHTM tư nhân năng động về số hóa và bán lẻ.",
    "editorialSummary3Sentences": (
        "Sau 6 năm, quy mô vốn hóa Vietcombank ghi nhận sự chững lại so với khối ngân hàng tư nhân. "
        "Từng lớn hơn 10 ngân hàng tư nhân gộp lại, nay vốn hóa VCB đã bị Techcombank và VPBank bắt kịp. "
        "Sự chuyển dịch này phản ánh bước ngoặt về hiệu quả sinh lời và thị phần bán lẻ."
    ),
    "supportingQuote": (
        "Từng lớn hơn tổng giá trị của 10 ngân hàng tư nhân cộng lại, đến nay giá trị thị trường của Vietcombank thậm chí chưa bằng tổng vốn hóa của 2 ngân hàng Techcombank và VPBank."
    ),
    "editorialPullQuote": (
        "Sự chuyển dịch tỷ trọng vốn hóa trong ngành ngân hàng là minh chứng rõ nét cho đòn bẩy công nghệ số và chiến lược tối ưu hóa nguồn vốn bán lẻ của khối NHTM tư nhân."
    ),
    "editorialSynthesis": (
        "Toàn cảnh phiên 16/11/2026 phản ánh bốn mạch chuyển động lớn từ 25 sự kiện xác minh: "
        "(1) Khối NHTM tư nhân tăng tốc phân hóa quy mô vốn hóa và chi phí vốn COF, tâm điểm là cuộc đua lợi nhuận tỷ USD và biểu lãi suất huy động ưu đãi lên tới 8,0% - 10,0%/năm tại các nhà băng (PVcomBank, MSB, Cake by VPBank, MB) theo bài viết điều tra của Báo Lao Động; "
        "(2) Tỷ giá liên ngân hàng và tỷ giá trung tâm USD/VND duy trì sức ép neo cao khi NHNN chưa mua được USD giao ngay, trong bối cảnh Fed phát tín hiệu cứng rắn về lộ trình lãi suất toàn cầu; "
        "(3) Doanh nghiệp sản xuất kinh doanh đón làn sóng đầu tư mới, từ Hòa Phát rót 650 tỷ đồng mở rộng năng lượng sạch, doanh nghiệp Hàn Quốc bổ sung 160 tỷ linh kiện xe điện đến các dự án bất động sản mở bán cuối năm; "
        "(4) Siết chặt kỷ cương quản lý thuế và an ninh tài chính, ngăn chặn triệt để hành vi thuê người đứng tên giám đốc doanh nghiệp mở tài khoản và xử lý nghiêm các giao dịch ngân hàng bất thường."
    ),
    "marketImpact": (
        "(1) Tối ưu hóa bảng cân đối tài sản: Các NHTM tư nhân quy mô lớn gia tăng nguồn thu ngoài lãi (non-interest income) từ hệ sinh thái số và dịch vụ thanh toán để bảo vệ biên lãi ròng NIM. "
        "(2) Phân hóa chi phí vốn huy động: Mặt bằng lãi suất huy động duy trì kỷ luật quanh 5,4% - 7,0%/năm cho kỳ hạn 12 tháng, nhưng các gói lãi suất đặc biệt kích thích dòng tiền gửi quy mô lớn. "
        "(3) Tháo gỡ nút thắt dòng tiền lưu động: Doanh nghiệp bán lẻ đẩy mạnh hợp tác với các trung gian thanh toán để triển khai thanh toán trả góp không tiền mặt, duy trì doanh số dịp cận Tết."
    ),
    "fintechLensAction": (
        "Trước bối cảnh chi phí vốn tín dụng ngân hàng neo ở mức cao, các doanh nghiệp bán lẻ và chuỗi phân phối cần tối ưu hóa hạ tầng chấp nhận thanh toán. "
        "Hệ sinh thái thanh toán Payoo (SmartPOS All-in-One, VietQR động định danh, cổng thanh toán đa kênh) cung cấp giải pháp chuyển đổi thanh toán trả góp 0% qua thẻ tín dụng và đối soát doanh thu thời gian thực, giúp giảm áp lực vay vốn lưu động ngắn hạn cho tiểu thương và chuỗi bán lẻ."
    ),
    "monitoringWatchpoint": (
        "Theo dõi động thái thanh khoản trên thị trường mở OMO của NHNN, biểu lãi suất tiền gửi 12 tháng tại Báo Lao Động và tăng trưởng giải ngân tín dụng tiêu dùng cuối năm."
    ),
}

ED31_ARTICLE_INTEL = {
    # EVT-18 / EVT-20261116-073 (Lao Động Deposit Rates Article)
    "EVT-20261116-073": {
        "summary": (
            "Khảo sát hơn 30 ngân hàng ngày 16.11 của Báo Lao Động ghi nhận 6 nhà băng áp dụng lãi suất trên 8%/năm. "
            "Các ngân hàng số như Cake by VPBank và MB tung ưu đãi cộng thêm đẩy lãi suất thực tế lên 8,2% - 9,1%/năm."
        ),
        "supportingQuote": (
            "PVcomBank hiện niêm yết lãi suất 10%/năm đối với tiền gửi kỳ hạn 12-13 tháng, lĩnh lãi cuối kỳ. Tuy nhiên, để được hưởng mức lãi suất này, khách hàng phải gửi tiền tại quầy với số tiền từ 2.000 tỉ đồng trở lên."
        ),
        "analysisNature": (
            "Báo Lao Động công bố bài khảo sát toàn diện biểu lãi suất hơn 30 NHTM, chỉ ra 6 ngân hàng niêm yết lãi suất vượt 8%/năm dành cho các khoản tiền gửi lớn hoặc qua kênh số."
        ),
        "analysisMechanism": (
            "Vĩ mô: Động thái tăng cường các gói ưu đãi huy động phản ánh nhu cầu cân đối thanh khoản và tăng tốc giải ngân tín dụng mùa cao điểm quý 4 của các NHTM. "
            "Vi mô: Chi phí vốn COF tăng cục bộ làm tăng áp lực lãi suất cho vay đối với doanh nghiệp SME, buộc ngân hàng phải chọn lọc danh mục cho vay và đẩy mạnh nguồn thu dịch vụ."
        ),
        "analysisMarketImpact": (
            "Dòng tiền gửi tiết kiệm dịch chuyển sang các kỳ hạn trung dài hạn có ưu đãi số, củng cố tính thanh khoản dài hạn của hệ thống nhưng làm tăng chi phí vốn vay thương mại."
        ),
        "analysisWatchSignal": (
            "Theo dõi diễn biến lãi suất huy động tại Báo Lao Động (chuyên mục Tiền tệ & Đầu tư) và động thái điều chỉnh lãi suất cơ sở của nhóm ngân hàng Big 4."
        ),
        "fintechLens": (
            "Lãi suất huy động cao làm tăng chi phí vốn vay ngắn hạn của các đơn vị bán lẻ. Mạng lưới SmartPOS Payoo hỗ trợ các chuỗi kích hoạt giải pháp trả góp thẻ tín dụng 0% và thanh toán PayLater, trợ lực sức mua cho người tiêu dùng mà không làm đọng vốn doanh nghiệp."
        ),
        "practicalTakeaway": (
            "Doanh nghiệp vừa và nhỏ (SMEs) cần đa dạng hóa kênh thanh toán số và đối soát dòng tiền thu hộ tức thì qua Payoo để giảm thiểu chi phí lãi vay vốn lưu động ngắn hạn."
        )
    }
}
