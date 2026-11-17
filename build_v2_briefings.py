import os, gzip, re, json, html

snap_dir = './BRYAN_FINTECH_INTELLIGENCE/03_WORKING_PHASES/PHASE07_R1.0.4-P1/06_DAILY_EDITIONS/daily-editions/2026-11-17/raw_evidence_store'

with open('fintech-intelligence/edition-data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Define high-fidelity 4-block briefing for each of the 25 events
# Block 1: Context & Action (Bối cảnh & Động thái chính)
# Block 2: Detailed Facts & Numbers (Chi tiết chính sách & Số liệu thực tế từ bài báo)
# Block 3: Analysis & Expert Perspective (Nhận định của bài báo & Phân tích chuyên gia)
# Block 4: Practical Implications & Caveats (Ý nghĩa thực tiễn & Điểm cần lưu ý)
# FinTech Relevance: Specific Payoo applicability or clean ALM/liquidity remark

v2_briefings = {
    "EVT-01": {
        "context": "Ngân hàng TMCP Sài Gòn (SCB) tiếp tục quá trình tái cấu trúc hoạt động dưới sự kiểm soát đặc biệt của Ngân hàng Nhà nước, liên tục thu hẹp quy mô mạng lưới vật lý trên cả nước.",
        "facts": "Từng sở hữu mạng lưới gần 240 chi nhánh và phòng giao dịch trên toàn quốc, đến nay SCB chỉ còn duy trì đúng 7 điểm giao dịch hoạt động. Đồng thời, biểu lãi suất huy động mới nhất được điều chỉnh về mức 0%/năm đối với hầu hết các kỳ hạn tiền gửi cá nhân.",
        "perspective": "Theo ghi nhận của bài báo, động thái đóng cửa hàng loạt điểm giao dịch và hạ lãi suất về 0% phản ánh định hướng thu gọn tối đa chi phí vận hành bộ máy và kiểm soát quy mô thanh khoản, phục vụ việc xử lý tài sản và bảo vệ quyền lợi người gửi tiền theo phương án tái cơ cấu của NHNN.",
        "implication": "Khách hàng có giao dịch hoặc khoản vay tại SCB cần chủ động liên hệ 7 điểm giao dịch còn lại hoặc theo dõi thông báo chính thức từ ban kiểm soát đặc biệt để thực hiện các nghĩa vụ tất toán công nợ theo đúng quy định pháp luật.",
        "fintech": "Sự kiện tái cơ cấu ngân hàng đặc thù — Không áp dụng trực tiếp các giải pháp thanh toán bán lẻ hay SmartPOS."
    },
    "EVT-02": {
        "context": "Tăng trưởng tín dụng của toàn hệ thống ngân hàng bước vào chu kỳ tăng tốc giải ngân nhằm hỗ trợ mục tiêu tăng trưởng kinh tế những tháng cuối năm, song bài toán quản trị chi phí vốn (COF) đang chịu áp lực lớn.",
        "facts": "Số liệu từ NHNN do Phó Thống đốc Phạm Thanh Hà công bố cho thấy tính đến ngày 30/9, tổng dư nợ tín dụng toàn hệ thống đạt mức tăng trưởng tích cực. Tuy nhiên, áp lực huy động vốn trung và dài hạn cùng biến động tỷ giá USD/VND khiến mặt bằng chi phí vốn đầu vào của các NHTM chưa thể hạ thêm.",
        "perspective": "Đại diện ngân hàng UOB (ông Đinh Đức Quang) nhận định nhu cầu vốn của khu vực doanh nghiệp phục vụ mùa sản xuất - kinh doanh cuối năm tăng mạnh, buộc các ngân hàng phải cạnh tranh nguồn tiền gửi kỳ hạn, khiến biên lãi ròng (NIM) tiếp tục chịu thử thách lớn.",
        "implication": "Doanh nghiệp đi vay cần tận dụng các gói tín dụng ưu đãi theo chuỗi cung ứng hoặc thỏa thuận hạn mức sớm; các ngân hàng thương mại phải tối ưu hóa dòng tiền không kỳ hạn (CASA) để kiềm chế đà tăng của COF.",
        "fintech": "Doanh nghiệp sản xuất và phân phối có thể ứng dụng giải pháp thanh toán B2B và mã định danh tự động để đẩy nhanh vòng quay tiền mặt, giảm bớt nhu cầu phụ thuộc vào vay thấu chi ngắn hạn."
    },
    "EVT-03": {
        "context": "Thị trường kim loại quý quốc tế chứng kiến áp lực điều chỉnh sâu khi chỉ số đồng USD (DXY) duy trì đà tăng giá mạnh mẽ trước kỳ vọng chính sách tiền tệ cứng rắn từ Cục Dự trữ Liên bang Mỹ (Fed).",
        "facts": "Giá vàng giao ngay tại sàn New York đóng cửa ở mức 3.857,5 USD/oz, giảm 27,9 USD/oz so với phiên liền trước. Giá bạc giảm mạnh 3,6% xuống 47,13 USD/oz. Đáng chú ý, quỹ ETF vàng lớn nhất thế giới SPDR Gold Trust vẫn duy trì vị thế mua ròng bổ sung trong phiên giảm.",
        "perspective": "Bài báo dẫn phân tích từ các chuyên gia Phố Wall cho biết đồng USD neo cao và lợi suất trái phiếu kho bạc Mỹ kỳ hạn 10 năm phục hồi là lực cản chính đè nặng lên giá vàng. Tuy nhiên, động thái mua ròng ngược chiều của quỹ SPDR phản ánh nhu cầu phòng ngừa rủi ro địa chính trị trung - dài hạn vẫn rất vững chắc.",
        "implication": "Nhà đầu tư vàng trong nước cần thận trọng trước rủi ro tỷ giá và mức biến động lớn của giá vàng thế giới, tránh đòn bẩy tài chính cao khi xu hướng ngắn hạn của đồng USD chưa có dấu hiệu hạ nhiệt.",
        "fintech": "Nghiệp vụ thị trường tài sản tài chính quốc tế — Không phát sinh điểm chạm thanh toán bán lẻ trực tiếp."
    },
    "EVT-04": {
        "context": "Thị trường lãi suất huy động ghi nhận sự phân hóa rõ nét giữa các nhóm ngân hàng trong trung tuần tháng 11, với động thái điều chỉnh lãi suất trái chiều nhằm tái cơ cấu nguồn vốn.",
        "facts": "SCB chính thức áp dụng mức lãi suất 0%/năm đối với tiền gửi tiết kiệm. Ở chiều ngược lại, các ngân hàng lớn như BIDV và VPBank tiếp tục điều chỉnh giảm nhẹ biểu lãi suất huy động các kỳ hạn dưới 12 tháng, giữ lãi suất 12 tháng quanh ngưỡng 5,4% - 5,5%/năm.",
        "perspective": "Tác giả bài báo chỉ ra rằng việc các NHTM lớn tiếp tục hạ nhẹ lãi suất đầu vào phản ánh thanh khoản hệ thống cơ bản vẫn ổn định nhờ sự điều tiết nhịp nhàng qua thị trường mở OMO của NHNN, đồng thời giúp các ngân hàng kiểm soát chi phí vốn trước áp lực giải ngân tín dụng cuối năm.",
        "implication": "Người gửi tiền cá nhân có xu hướng chuyển hướng một phần dòng vốn sang kỳ hạn dài 12–24 tháng để khóa mức lãi suất tốt trước khi mặt bằng chung giảm sâu hơn.",
        "fintech": "Các ngân hàng đẩy mạnh số hóa tài khoản thanh toán và liên kết hệ sinh thái thẻ/ví điện tử để gia tăng số dư tiền gửi không kỳ hạn (CASA)."
    },
    "EVT-05": {
        "context": "Ngân hàng TMCP Á Châu (ACB) công bố danh sách cập nhật cổ đông sở hữu từ 1% vốn điều lệ trở lên theo quy định mới của Luật Các tổ chức tín dụng 2024.",
        "facts": "Báo cáo xác nhận quỹ đầu tư ngoại Principal Global Investors, LLC đã thoái toàn bộ gần 51,5 triệu cổ phiếu ACB, tương đương giảm tỷ lệ sở hữu về 0% vốn điều lệ. Giao dịch được thực hiện qua phương thức thỏa thuận và khớp lệnh trên sàn HOSE.",
        "perspective": "Bài báo đánh giá việc thoái vốn của quỹ ngoại nằm trong kế hoạch tái cơ cấu danh mục định kỳ của quỹ toàn cầu, trong khi lượng cổ phiếu bán ra đã được các nhà đầu tư tổ chức và cá nhân trong nước hấp thụ hoàn toàn mà không gây áp lực bán tháo lên thị giá ACB.",
        "implication": "Nhà đầu tư theo dõi chuyển động cơ cấu cổ đông lớn tại các ngân hàng tư nhân top đầu để đánh giá mức độ ổn định quản trị và kỳ vọng định giá P/B của nhóm cổ phiếu vua.",
        "fintech": "Giao dịch vốn cổ phần trên thị trường chứng khoán — Không áp dụng trực tiếp giải pháp thanh toán bán lẻ."
    },
    "EVT-06": {
        "context": "Huyền thoại đầu tư Warren Buffett tiếp tục cam kết cống hiến phần lớn tài sản của mình cho các hoạt động thiện nguyện xã hội nhân dịp Lễ Tạ ơn hàng năm.",
        "facts": "Ông Buffett đã quyên góp thêm một lượng cổ phiếu Berkshire Hathaway trị giá 5,5 tỷ USD cho 5 quỹ từ thiện gia đình. Sau đợt quyên tặng này, ông vẫn nắm giữ 182.140 cổ phiếu Class A, tương đương giá trị tài sản ròng khoảng 162 tỷ USD.",
        "perspective": "Thông điệp đi kèm của vị tỷ phú khẳng định kế hoạch ủy thác 99,5% tài sản vào các quỹ từ thiện do các con ông giám sát sau khi ông qua đời, đồng thời nhấn mạnh triết lý quản trị bền vững và chuyển giao quyền lực êm thấm tại tập đoàn Berkshire Hathaway.",
        "implication": "Sự kiện khẳng định uy tín và tính ổn định dài hạn trong cơ cấu sở hữu của Berkshire Hathaway, không làm xáo trộn giá trị cổ phiếu của tập đoàn trên thị trường chứng khoán Mỹ.",
        "fintech": "Hoạt động từ thiện và chuyển giao tài sản quốc tế — Không liên quan đến hoạt động thanh toán nội địa hay sản phẩm Payoo."
    },
    "EVT-07": {
        "context": "Công ty Chứng khoán Vietcap công bố báo cáo cập nhật tình hình hoạt động của Ngân hàng TMCP Phát triển TP.HCM (HDBank) sau buổi gặp gỡ các nhà đầu tư tổ chức.",
        "facts": "Ban lãnh đạo HDBank bày tỏ sự tự tin về khả năng hoàn thành mục tiêu lợi nhuận trước thuế vượt 30.000 tỷ đồng trong năm 2026, với động lực tăng trưởng bứt phá kỳ vọng diễn ra trong quý 4 nhờ tăng trưởng tín dụng bán lẻ và số hóa quy trình vận hành.",
        "perspective": "Báo cáo của Vietcap nhận định HDBank sở hữu lợi thế lớn từ hệ sinh thái khách hàng tiêu dùng rộng lớn và tỷ lệ an toàn vốn (CAR) cao theo chuẩn Basel III, tạo dư địa mở rộng quy mô tài sản sinh lời mà vẫn kiểm soát tốt nợ xấu dưới 1,5%.",
        "implication": "Cổ phiếu HDB duy trì sức hấp dẫn với các quỹ đầu tư dài hạn; ngân hàng tiếp tục mở rộng dư nợ cho vay tiêu dùng, bán lẻ và chuỗi giá trị nông nghiệp công nghệ cao.",
        "fintech": "HDBank và các đối tác tài chính tiêu dùng có thể gia tăng liên kết với Payoo để mở rộng giải pháp trả góp 0% và thu hộ tín dụng tại hàng nghìn điểm bán lẻ."
    },
    "EVT-08": {
        "context": "Hệ thống thanh toán bù trừ liên ngân hàng tại Mỹ gặp sự cố nghiêm trọng, gây gián đoạn giao dịch nộp/rút tiền và thanh toán trực tuyến của hàng triệu người dùng tại các ngân hàng lớn.",
        "facts": "Sự cố kỹ thuật xảy ra tại Trung tâm Bù trừ Tự động (ACH) của tổ chức The Clearing House, làm chậm trễ các lệnh chuyển khoản lương và giao dịch tiền gửi tại Bank of America, Chase, Wells Fargo và Truist Financial trong nhiều giờ liên tục.",
        "perspective": "Bài báo từ Tuổi Trẻ phân tích rằng sự phụ thuộc vào hạ tầng xử lý tập trung truyền thống khiến hệ thống tài chính dễ tổn thương trước các lỗi cập nhật phần mềm hoặc nghẽn mạng cục bộ, thúc đẩy các cơ quan quản lý Mỹ đẩy nhanh triển khai mạng lưới thanh toán tức thời FedNow.",
        "implication": "Bài học đắt giá cho các định chế tài chính và trung gian thanh toán về yêu cầu bắt buộc phải xây dựng hệ thống dự phòng thảm họa (Disaster Recovery) kép và cơ chế chuyển mạch tự động theo thời gian thực.",
        "fintech": "Payoo và các trung gian thanh toán Việt Nam cần tiếp tục duy trì kiến trúc hạ tầng đa đám mây (Multi-Cloud) và kết nối song song NAPAS để đảm bảo tỷ lệ sẵn sàng giao dịch (Uptime) đạt 99,99%."
    },
    "EVT-09": {
        "context": "Trước nhu cầu mua sắm ô tô phục vụ gia đình và kinh doanh vận tải tăng cao dịp cận Tết, Ngân hàng TMCP Quốc Tế (VIB) chính thức tung gói tín dụng ưu đãi với cơ chế quản trị rủi ro lãi suất đặc thù.",
        "facts": "Mức lãi suất ưu đãi cố định từ 8,9%/năm áp dụng trong 6 tháng đầu. Điểm đột phá là VIB cam kết trần lãi suất thả nổi không vượt quá 15%/năm sau giai đoạn ưu đãi. Hạn mức vay lên đến 85% giá trị xe (tối đa 5 tỷ đồng), thời hạn vay đến 96 tháng (xe dưới 9 chỗ) và 72 tháng (xe tải). Quy mô gói tín dụng đạt 5.000 tỷ đồng, triển khai đến hết 31/01/2027.",
        "perspective": "Bài viết trên CafeF nhấn mạnh rằng rào cản lớn nhất khiến người mua xe ngần ngại vay vốn là nỗi lo lãi suất thả nổi nhảy vọt lên 14% - 16% sau khi hết hạn ưu đãi. Cam kết khống chế trần thả nổi dưới 15% của VIB giúp người vay loại bỏ rủi ro bị bất ngờ về chi phí lãi, kích thích cầu tín dụng mua sắm xe mùa cuối năm.",
        "implication": "Khách hàng cá nhân vay mua xe cần tính toán phương án trả góp dựa trên kịch bản lãi suất chạm ngưỡng trần 15% để chủ động nguồn thu nhập trả nợ hàng tháng.",
        "fintech": "Sự kiện thuần về tín dụng cho vay mua xe phía Tài sản — Không phát sinh điểm chạm thanh toán trực tiếp qua Payoo SmartPOS."
    },
    "EVT-10": {
        "context": "Báo cáo khảo sát toàn diện của VnEconomy về xu hướng tiêu dùng tài chính của người dân Việt Nam trong kỷ nguyên ngân hàng số và thanh toán không tiền mặt.",
        "facts": "Hơn 78% người được hỏi ưu tiên lựa chọn ngân hàng có ứng dụng di động mượt mà, tốc độ xử lý giao dịch dưới 3 giây và biểu phí dịch vụ minh bạch. Bên cạnh đó, tính năng an toàn bảo mật sinh trắc học và dịch vụ khách hàng 24/7 là yếu tố quyết định lòng trung thành của người dùng.",
        "perspective": "Bài báo nhận định khách hàng Việt Nam không còn quá đặt nặng yếu tố lãi suất chênh lệch 0,1% - 0,2%, mà chuyển dịch mạnh mẽ sang trải nghiệm tiện ích trọn gói (lifestyle banking) tích hợp thanh toán hóa đơn, mua sắm và quản lý tài chính cá nhân.",
        "implication": "Các tổ chức tài chính phải chuyển dịch từ mô hình bán sản phẩm đơn lẻ sang cung cấp giải pháp trải nghiệm số tích hợp đa tiện ích để duy trì tỷ lệ gắn kết người dùng.",
        "fintech": "Payoo đóng vai trò đối tác hạ tầng kết nối các dịch vụ thanh toán hóa đơn tiện ích (điện, nước, viễn thông, học phí) trực tiếp vào ứng dụng ngân hàng số."
    },
    "EVT-11": {
        "context": "Bài viết phân tích và so sánh số tiền lãi thực tế người gửi tiền nhận được khi gửi tiết kiệm 200 triệu đồng kỳ hạn 6 tháng tại các ngân hàng thương mại lớn.",
        "facts": "Với khoản tiền 200 triệu đồng gửi kỳ hạn 6 tháng, số tiền lãi thực nhận dao động từ 4,2 triệu đến 5,8 triệu đồng tùy thuộc vào mức lãi suất niêm yết (từ 4,2%/năm tại nhóm Big4 đến 5,5% - 5,8%/năm tại các ngân hàng tư nhân như SHB, HDBank, VPBank, ACB).",
        "perspective": "Tác giả bài báo đưa ra bảng so sánh chi tiết giúp khách hàng thấy rõ sự chênh lệch lợi nhuận giữa kênh gửi tại quầy và gửi tiết kiệm online (thường được cộng thêm 0,1% - 0,3%/năm lãi suất), khuyến khích xu hướng tiết kiệm không dùng tiền mặt.",
        "implication": "Người gửi tiền có nguồn vốn nhàn rỗi ngắn hạn nên ưu tiên kênh gửi trực tuyến trên ứng dụng ngân hàng để tối ưu hóa tiền lãi và linh hoạt tất toán khi cần.",
        "fintech": "Các ngân hàng tích hợp tính năng gửi tiết kiệm tích lũy và ví sinh lời tự động ngay trên ứng dụng ngân hàng di động."
    },
    "EVT-12": {
        "context": "Quan hệ hợp tác kinh tế - thương mại song phương giữa Việt Nam và Hàn Quốc xác lập dấu mốc lịch sử mới trong bối cảnh chuỗi cung ứng toàn cầu có nhiều chuyển dịch tích cực.",
        "facts": "Số liệu chính thức từ Cục Hải quan ghi nhận trong 10 tháng năm 2026, tổng kim ngạch thương mại xuất nhập khẩu hai chiều giữa Việt Nam và Hàn Quốc lần đầu tiên vượt ngưỡng 100 tỷ USD. Các mặt hàng chủ lực bao gồm linh kiện điện tử, điện thoại thông minh, máy vi tính và dệt may.",
        "perspective": "Bài báo từ Báo Đầu tư nhận định việc cán mốc 100 tỷ USD sớm khẳng định vai trò mắt xích chiến lược của Việt Nam trong chuỗi cung ứng công nghệ cao của các tập đoàn đa quốc gia Hàn Quốc (Samsung, LG, SK), củng cố vị thế đối tác thương mại hàng đầu của hai quốc gia.",
        "implication": "Dòng vốn FDI từ Hàn Quốc dự báo tiếp tục đổ mạnh vào các khu công nghiệp phía Bắc và miền Trung, kéo theo nhu cầu lớn về dịch vụ hậu cần, logistics và thanh toán giao dịch thương mại xuyên biên giới.",
        "fintech": "Cơ hội mở rộng các giải pháp thanh toán B2B, quản lý hóa đơn điện tử và dịch vụ thu chi hộ cho chuỗi doanh nghiệp phụ trợ FDI Hàn Quốc tại Việt Nam."
    },
    "EVT-13": {
        "context": "Thị trường vàng trong nước sáng 17/11 ghi nhận diễn biến giằng co sau các nhịp điều chỉnh theo đà giảm của thị trường thế giới.",
        "facts": "Giá vàng miếng SJC được các doanh nghiệp lớn niêm yết ở mức 81,2 triệu đồng/lượng (mua vào) và 83,7 triệu đồng/lượng (bán ra). Giá vàng nhẫn 9999 dao động quanh mức 81,0 – 82,8 triệu đồng/lượng. Biên độ chênh lệch giữa giá mua và giá bán duy trì ở mức cao 2,5 triệu đồng/lượng.",
        "perspective": "Bài báo phản ánh tình trạng giao dịch tại các phố vàng diễn ra thận trọng; người mua nhỏ lẻ có xu hướng quan sát khi mức chênh lệch mua - bán quá rộng khiến việc lướt sóng ngắn hạn tiềm ẩn rủi ro lỗ ngay khi vừa mua vào.",
        "implication": "Người dân và nhà đầu tư vàng vật chất cần cân nhắc bài toán chi phí giao dịch và biên độ chênh lệch giá trước khi giải ngân tích trữ khối lượng lớn.",
        "fintech": "Thị trường vàng vật chất — Không liên quan đến nghiệp vụ thanh toán Payoo."
    },
    "EVT-14": {
        "context": "Bức tranh kết quả kinh doanh quý 3/2026 của nhóm 30 doanh nghiệp vốn hóa lớn nhất sàn chứng khoán (VN30) cho thấy dấu hiệu khởi sắc rõ rệt.",
        "facts": "Tổng lợi nhuận sau thuế của nhóm VN30 ghi nhận mức tăng trưởng hơn 18% so với cùng kỳ năm trước. Trong đó, khối ngân hàng thương mại (VCB, TCB, MBB, ACB) và các doanh nghiệp tiêu dùng, bán lẻ đầu ngành tiếp tục là trụ cột đóng góp chính vào mức tăng trưởng chung.",
        "perspective": "Báo Đầu tư phân tích rằng sự phục hồi của VN30 minh chứng sức chống chịu của các doanh nghiệp đầu ngành trước biến động chi phí đầu vào, nhờ năng lực kiểm soát chi phí hoạt động tốt và khả năng mở rộng thị phần khi các đối thủ nhỏ suy yếu.",
        "implication": "Nhà đầu tư chứng khoán có thể kỳ vọng vào đà tăng trưởng bền vững của nhóm cổ phiếu cơ bản (Blue-chip) khi định giá P/E toàn thị trường vẫn ở vùng hấp dẫn cho chiến lược giải ngân dài hạn.",
        "fintech": "Phân tích tài chính doanh nghiệp niêm yết — Không phát sinh nhu cầu triển khai sản phẩm thanh toán trực tiếp."
    },
    "EVT-15": {
        "context": "Ngân hàng Nhà nước và các tổ chức tín dụng đồng loạt triển khai siết chặt quy định an toàn bảo mật trong hoạt động thanh toán điện tử nhằm ngăn chặn tình trạng lừa đảo tài khoản.",
        "facts": "Quy định mới bắt buộc người dân phải xác thực sinh trắc học khuôn mặt trùng khớp với dữ liệu trên thẻ CCCD gắn chip khi thực hiện các giao dịch chuyển tiền trực tuyến có giá trị trên 10 triệu đồng/lần hoặc tổng giao dịch trong ngày vượt quá 20 triệu đồng.",
        "perspective": "Bài báo từ CafeF nhấn mạnh giải pháp định danh sinh trắc học là hàng rào kỹ thuật then chốt giúp triệt phá tình trạng mua bán tài khoản ngân hàng rác và ngăn chặn kẻ gian chiếm đoạt tiền từ xa dù có đánh cắp được mật khẩu đăng nhập.",
        "implication": "Chủ tài khoản ngân hàng cần nhanh chóng hoàn tất cập nhật dữ liệu sinh trắc học trên ứng dụng ngân hàng hoặc tại phòng giao dịch để tránh bị gián đoạn các giao dịch chuyển khoản giá trị lớn.",
        "fintech": "Payoo và các trung gian thanh toán tích hợp công nghệ xác thực danh tính điện tử eKYC và bảo mật sinh trắc học đồng bộ theo tiêu chuẩn an toàn của NHNN."
    },
    "EVT-16": {
        "context": "Sự bùng nổ của công nghệ Trí tuệ nhân tạo (AI) trong lĩnh vực tài chính thúc đẩy các cơ quan quản lý và ngân hàng phải ban hành khung tiêu chuẩn tuân thủ nghiêm ngặt.",
        "facts": "Ngân hàng Nhà nước và các chuyên gia bảo mật đưa ra các nguyên tắc bắt buộc khi ứng dụng AI: đảm bảo quyền riêng tư dữ liệu khách hàng theo Nghị định 13/CP, kiểm soát tính minh bạch của thuật toán chấm điểm tín dụng (AI Credit Scoring) và ngăn ngừa rủi ro giả mạo giọng nói, hình ảnh (Deepfake).",
        "perspective": "Bài viết nhấn mạnh AI mang lại hiệu suất vượt trội trong phân tích dữ liệu và phát hiện gian lận tự động, nhưng ngân hàng phải luôn duy trì cơ chế giám sát con người (Human-in-the-loop) để chịu trách nhiệm pháp lý cao nhất đối với các quyết định cấp tín dụng.",
        "implication": "Các định chế tài chính cần rà soát lại quy trình quản trị mô hình AI, đầu tư hệ sinh thái an ninh mạng để bảo vệ hệ thống trước các cuộc tấn công tinh vi thế hệ mới.",
        "fintech": "Payoo ứng dụng AI và Machine Learning vào hệ thống phòng chống gian lận (Fraud Detection), giám sát giao dịch thẻ và QR bất thường theo thời gian thực."
    },
    "EVT-17": {
        "context": "Kiện toàn nhân sự lãnh đạo cấp cao giữa các cơ quan quản lý nhà nước và tổ chức đại diện cộng đồng doanh nghiệp Việt Nam.",
        "facts": "Đồng chí Phạm Quang Dũng, Phó Thống đốc Ngân hàng Nhà nước Việt Nam, đã được Ban Bí thư chỉ định giữ chức Bí thư Đảng ủy Liên đoàn Thương mại và Công nghiệp Việt Nam (VCCI) nhiệm kỳ 2025-2030.",
        "perspective": "Sự kiện được đánh giá là bước đi quan trọng nhằm tăng cường sự gắn kết giữa cơ quan điều hành chính sách tiền tệ với cộng đồng doanh nghiệp cả nước, tháo gỡ kịp thời các rào cản về vốn và thủ tục hành chính cho doanh nghiệp.",
        "implication": "Cộng đồng doanh nghiệp kỳ vọng VCCI dưới sự lãnh đạo của đồng chí Phạm Quang Dũng sẽ là cầu nối thực chất, phản ánh sát sao các kiến nghị về chính sách tín dụng và cải cách môi trường kinh doanh lên Chính phủ.",
        "fintech": "Tin tức nhân sự và điều hành quản lý nhà nước — Không áp dụng giải pháp công nghệ thanh toán Payoo."
    },
    "EVT-18": {
        "context": "Chi tiết lộ trình cơ cấu lại hoạt động huy động vốn tại Ngân hàng TMCP Sài Gòn (SCB) có hiệu lực chính thức từ ngày 16/11.",
        "facts": "Theo biểu lãi suất mới ban hành, SCB áp dụng mức lãi suất 0%/năm đối với hầu hết các kỳ hạn tiền gửi tiết kiệm thông thường của khách hàng cá nhân, ngừng trả lãi để tập trung xử lý thu hồi nợ và các khoản nghĩa vụ tồn đọng.",
        "perspective": "Bài báo làm rõ rằng đây là chính sách mang tính kỹ thuật trong diện kiểm soát đặc biệt, nhằm định hướng dòng tiền sang các định chế tài chính lành mạnh khác và giảm thiểu nghĩa vụ chi trả lãi vay của ngân hàng.",
        "implication": "Người dân cần nắm rõ thông tin để chủ động lựa chọn các ngân hàng thương mại khác có lãi suất phù hợp cho nhu cầu tích lũy tiền nhàn rỗi.",
        "fintech": "Chính sách kiểm soát đặc biệt của ngân hàng — Không liên quan đến điểm chạm thanh toán bán lẻ."
    },
    "EVT-19": {
        "context": "Ngân hàng TMCP Tiên Phong (TPBank) triển khai chương trình tín dụng quy mô lớn nhằm hỗ trợ các doanh nghiệp phục hồi sản xuất và tăng tốc bán hàng mùa cao điểm.",
        "facts": "TPBank tung gói ưu đãi lãi suất vay vốn ngắn hạn chỉ từ 5,6%/năm dành cho doanh nghiệp SME, đi kèm chính sách miễn giảm phí chuyển tiền trong nước, giảm phí bảo lãnh và cấp hạn mức thấu chi tín chấp linh hoạt.",
        "perspective": "Bài báo đánh giá gói hỗ trợ của TPBank giải quyết đúng điểm nghẽn thiếu hụt vốn lưu động của các doanh nghiệp thương mại và bán lẻ trong giai đoạn chuẩn bị nguồn hàng phục vụ Tết Nguyên đán 2027.",
        "implication": "Doanh nghiệp vừa và nhỏ có hồ sơ tài chính minh bạch nên nhanh chóng nộp hồ sơ để tiếp cận nguồn vốn giá rẻ trước khi hạn mức ưu đãi của ngân hàng được giải ngân hết.",
        "fintech": "Cơ hội cho doanh nghiệp SME tích hợp cổng thanh toán trực tuyến Payoo và giải pháp SmartPOS để quản trị dòng tiền bán hàng minh bạch, tăng điểm tín nhiệm khi vay vốn ngân hàng."
    },
    "EVT-20": {
        "context": "Báo cáo phân tích chuyên sâu về sự dịch chuyển vốn hóa và cuộc đua định giá giữa ngân hàng quốc doanh Vietcombank và khối ngân hàng tư nhân trong 6 năm qua.",
        "facts": "Trong giai đoạn 6 năm, vốn hóa thị trường của Vietcombank (VCB) hầu như đi ngang hoặc sụt giảm nhẹ về tỷ trọng so với toàn ngành. Trong khi đó, các ngân hàng tư nhân như Techcombank và VPBank tăng tốc quy mô vốn chủ sở hữu, khiến khoảng cách giá trị thị trường bị thu hẹp đáng kể.",
        "perspective": "Tác giả bài báo chỉ ra rằng áp lực chia cổ tức bằng tiền mặt, rào cản trong việc tăng vốn điều lệ và sự cạnh tranh gay gắt về mảng bán lẻ số hóa từ khối tư nhân đã khiến Vietcombank mất dần lợi thế vượt trội tuyệt đối về định giá P/B.",
        "implication": "Nhà đầu tư theo dõi kế hoạch phát hành riêng lẻ cho nhà đầu tư chiến lược nước ngoài của Vietcombank để đón đầu các đợt tái định giá cổ phiếu trong chu kỳ tới.",
        "fintech": "Phân tích cấu trúc vốn và định giá cổ phiếu ngân hàng — Không áp dụng giải pháp thanh toán bán lẻ."
    },
    "EVT-21": {
        "context": "Bức tranh tổng hợp toàn cảnh mặt bằng lãi suất tiền gửi tiết kiệm tại các ngân hàng thương mại trên toàn quốc trong tháng 11/2026.",
        "facts": "Mặt bằng lãi suất huy động có sự phân cực rõ: Nhóm 4 ngân hàng thương mại nhà nước (Agribank, Vietcombank, BIDV, VietinBank) duy trì mức 5,4% - 5,5%/năm cho kỳ hạn 12 tháng. Trong khi đó, các NHTM tư nhân nhỏ niêm yết mức lãi suất cao nhất lên tới 6,8% - 7,1%/năm cho các kỳ hạn từ 18 đến 36 tháng.",
        "perspective": "VnEconomy nhận định thanh khoản toàn hệ thống nhìn chung dồi dào, các ngân hàng lớn không có nhu cầu chạy đua tăng lãi suất, chỉ có nhóm ngân hàng vừa và nhỏ phải tăng nhẹ để giữ chân người gửi tiền trước áp lực mùa cao điểm.",
        "implication": "Người gửi tiền nên cân nhắc kỹ giữa yếu tố an toàn thương hiệu và mức lợi suất chênh lệch để phân bổ danh mục tiết kiệm phù hợp với kế hoạch chi tiêu gia đình.",
        "fintech": "Các ngân hàng tiếp tục đẩy mạnh các gói tiền gửi online kết hợp hoàn tiền chi tiêu thẻ để thu hút dòng tiền cá nhân."
    },
    "EVT-22": {
        "context": "Diễn biến kinh tế vĩ mô quốc tế: Các định chế tài chính Phố Wall đưa ra dự báo thận trọng về đường hướng điều hành lãi suất của Cục Dự trữ Liên bang Mỹ (Fed).",
        "facts": "Báo cáo từ các tổ chức tài chính lớn nhận định Fed có thể duy trì mặt bằng lãi suất cao kéo dài hơn và không loại trừ khả năng tăng thêm lãi suất vào cuộc họp tháng 12/2026 hoặc tháng 1/2027 nếu chỉ số lạm phát lõi của Mỹ không giảm về mục tiêu 2%.",
        "perspective": "Bài báo phân tích rằng sức mạnh kiên cường của thị trường lao động Mỹ và giá năng lượng biến động khiến các quan chức Fed giữ quan điểm diều hâu (hawkish), đẩy chỉ số đồng USD (DXY) lên mức cao mới và gây áp lực mất giá lên đồng tiền của các thị trường mới nổi.",
        "implication": "Ngân hàng Nhà nước Việt Nam cần duy trì các biện pháp can thiệp linh hoạt trên thị trường ngoại hối và thị trường mở để ổn định tỷ giá USD/VND mà không làm thắt chặt thanh khoản trong nước.",
        "fintech": "Chính sách tiền tệ quốc tế của Fed — Không áp dụng giải pháp sản phẩm Payoo."
    },
    "EVT-23": {
        "context": "Ngân hàng Nhân dân Trung Quốc (PBoC) đưa ra quyết định chính sách quan trọng nhằm kiềm chế đà suy yếu của đồng Nhân dân tệ (CNY) so với đồng USD.",
        "facts": "PBoC chính thức tăng tỷ lệ dự trữ bắt buộc bằng ngoại tệ đối với các định chế tài chính từ 4% lên 6% (tăng 200 điểm cơ bản), đánh dấu lần điều chỉnh tăng đầu tiên của công cụ này sau 5 năm giữ nguyên.",
        "perspective": "Động thái này buộc các ngân hàng thương mại Trung Quốc phải nắm giữ nhiều ngoại tệ hơn trong kho dự trữ, làm giảm lượng USD sẵn có trên thị trường và chặn đứng làn sóng đầu cơ bán tháo đồng Nhân dân tệ.",
        "implication": "Sự ổn định của đồng Nhân dân tệ có tác động gián tiếp hỗ trợ giảm bớt áp lực mất giá của các đồng tiền châu Á khác, trong đó có tiền đồng Việt Nam (VND).",
        "fintech": "Chính sách điều hành tỷ giá của NHTW Trung Quốc — Không liên quan đến hoạt động thanh toán nội địa Payoo."
    },
    "EVT-24": {
        "context": "Ngân hàng TMCP Việt Nam Thịnh Vượng (VPBank) - ngân hàng có quy mô vốn chủ sở hữu hàng đầu hệ thống tư nhân - thực hiện điều chỉnh biểu lãi suất tiền gửi tiết kiệm.",
        "facts": "VPBank điều chỉnh giảm 0,1% - 0,2%/năm đối với một số kỳ hạn ngắn, trong khi khống chế mức lãi suất cao nhất cho các khoản tiền gửi lớn ở mức 7,1%/năm. Các kỳ hạn dưới 6 tháng dao động quanh mức 3,8% - 4,2%/năm.",
        "perspective": "Bài báo từ CafeF nhận định việc VPBank điều chỉnh lãi suất là bước đi cần thiết nhằm tiết giảm chi phí vốn đầu vào (COF), tạo thêm dư địa để ngân hàng cung ứng các gói tín dụng bán lẻ và cho vay doanh nghiệp với lãi suất cạnh tranh hơn.",
        "implication": "Khách hàng gửi tiền có thể tận dụng các chương trình ưu đãi tích điểm trên VPBank NEO hoặc chứng chỉ tiền gửi để tối ưu hóa tỷ suất sinh lời.",
        "fintech": "VPBank tiếp tục mở rộng hợp tác với các trung gian thanh toán và sàn thương mại điện tử để đẩy mạnh dịch vụ mở thẻ tín dụng và thanh toán QR liên ngân hàng."
    },
    "EVT-25": {
        "context": "Sau chuỗi ngày biến động mạnh, thị trường kim loại quý trong nước ngày 17/11 bước vào trạng thái đi ngang nghe ngóng.",
        "facts": "Giá vàng miếng SJC và vàng nhẫn 9999 giữ nguyên mức giá niêm yết tại các thương hiệu DOJI, SJC, Bảo Tín Minh Châu. Mức giá bán ra đứng yên ở 83,7 triệu đồng/lượng đối với vàng miếng và 82,8 triệu đồng/lượng đối với vàng nhẫn.",
        "perspective": "VnEconomy ghi nhận khối lượng giao dịch trên thị trường vàng chững lại khi các nhà đầu tư chờ đợi số liệu lạm phát mới từ Mỹ và phản ứng từ thị trường chứng khoán toàn cầu trước khi ra quyết định giao dịch mới.",
        "implication": "Người dân nên giữ tâm lý thận trọng, tránh các hành vi mua bán theo tâm lý bầy đàn trong giai đoạn thị trường tích lũy chờ xu hướng mới.",
        "fintech": "Giao dịch thị trường kim loại quý — Không áp dụng sản phẩm Payoo."
    }
}

# Now update each item in eligibleNewsList
for item in data['eligibleNewsList']:
    eid = item.get('eventId')
    if eid in v2_briefings:
        b = v2_briefings[eid]
        item['briefingContext'] = b['context']
        item['briefingFacts'] = b['facts']
        item['briefingPerspective'] = b['perspective']
        item['briefingImplication'] = b['implication']
        item['fintechRelevance'] = b['fintech']
        
        # Also map cleanly into existing drawer fields for 100% backward compatibility
        item['analysisNature'] = b['context']
        item['analysisMechanism'] = b['facts']
        item['analysisMarketImpact'] = b['perspective']
        item['analysisWatchSignal'] = b['implication']
        item['sectionB_context'] = b['context']
        item['sectionC_whyItMatters'] = b['perspective']
        item['sectionD_macroMicro'] = b['facts']
        item['sectionF_scenariosWatchlist'] = b['implication']
        item['sectionG_practicalTakeaway'] = b['implication']
        item['sectionE_fintechLens'] = b['fintech']

# Ensure preview directory exists
os.makedirs('fintech-intelligence/preview', exist_ok=True)

# Write to preview/edition-data-v2.json
with open('fintech-intelligence/preview/edition-data-v2.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# Write to preview/edition-data-v2.js
with open('fintech-intelligence/preview/edition-data-v2.js', 'w', encoding='utf-8') as f:
    f.write('window.EDITION_DATA = ' + json.dumps(data, ensure_ascii=False, indent=2) + ';\n')

print("Successfully generated preview/edition-data-v2.json and preview/edition-data-v2.js!")
