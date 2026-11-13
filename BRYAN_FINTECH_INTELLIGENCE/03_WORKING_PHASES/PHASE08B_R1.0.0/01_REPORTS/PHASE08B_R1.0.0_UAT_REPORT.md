# BÁO CÁO NGHIỆM THU NGƯỜI DÙNG (USER ACCEPTANCE TESTING REPORT - UAT)
## DỰ ÁN: BRYAN FINTECH INTELLIGENCE
### PHIÊN BẢN: PHASE 08B — R1.0.0
**Mã tài liệu:** PHASE08B_R1.0.0_UAT_REPORT  
**Môi trường kiểm thử:** Production Live URL (`https://bryanportfolio.io.vn/fintech-intelligence/index.html`)  
**Tác giả:** QA Lead & Senior Technical Director  
**Ngày phát hành:** 14/11/2026  
**Kết luận nghiệm thu:** ACCEPTED CANDIDATE — 100% KỊCH BẢN ĐẠT (PASS)  

---

## 1. MA TRẬN KỊCH BẢN KIỂM THỬ NGHIỆM THU (UAT TEST CASES)

| STT | Kịch bản kiểm thử (Test Scenario) | Thao tác thực hiện | Kết quả kỳ vọng | Kết quả thực tế | Đánh giá |
|:---:|:---|:---|:---|:---|:---:|
| **TC-01** | Kiểm tra câu mẫu lặp D-06 | Quét toàn bộ 25 bài tin tức và Cover story | Không còn câu mẫu lặp "Sự kiện ghi nhận..." | 0 câu mẫu, 0 lỗi `?;` | **PASS** |
| **TC-02** | Kiểm tra màu tương phản D-07 | Dùng công cụ đo màu chữ phụ và nhãn | Tỷ lệ tương phản đạt ≥ 4.5:1 | Ratios đạt từ 4.54:1 đến 6.51:1 | **PASS** |
| **TC-03** | Tìm kiếm không có kết quả D-08 | Nhập `zzzzqqq` vào ô tìm kiếm | Hiển thị Empty State rõ ràng kèm nút xóa | Empty state hiển thị đẹp mắt, nút xóa hoạt động ngay | **PASS** |
| **TC-04** | Bộ đếm tin tức D-08 | Nhập tìm kiếm và lọc chuyên mục | Phân biệt rõ số bài khớp và tổng 25 bài | Hiển thị "X bài phù hợp trên tổng 25 bài đủ điều kiện" | **PASS** |
| **TC-05** | Phím Tab & Skip Link D-09 | Nhấn Tab ngay khi trang vừa tải | Skip link xuất hiện trên góc trái | Skip link hiện rõ với viền cyan, bấm nhảy vào `#mainContent` | **PASS** |
| **TC-06** | Thao tác Drawer bằng phím D-09 | Nhấn Enter vào tiêu đề bài viết, sau đó nhấn Escape | Tiêu điểm vào nút đóng khi mở, đóng khi nhấn Esc | Drawer mở mượt mà, Esc đóng và trả lại tiêu điểm | **PASS** |
| **TC-07** | Phím mũi tên trên Tab D-09 | Focus vào thanh Tab và bấm mũi tên sang phải | Chuyển tab kế tiếp tức thì | Phím ArrowRight/Left chuyển tab và active đúng chuẩn ARIA | **PASS** |
| **TC-08** | Khả năng thu phóng D-10 | Thao tác phóng to trình duyệt lên 200% | Bố cục co giãn linh hoạt, không bị khóa zoom | Zoom 200% mượt mà, văn bản đọc rõ nét | **PASS** |
| **TC-09** | Giao diện Header Mobile D-11 | Xem trang ở màn hình 390px (iPhone 14) | Không có ký tự `|` thừa, nút Theme 1 dòng | Header cân đối, nút đổi bản sáng/tối không bị rớt dòng | **PASS** |
| **TC-10** | Dữ liệu cấu trúc SEO D-12 | Kiểm tra mã nguồn thẻ `<head>` | Có Canonical, OG tags, Schema JSON-LD | Đầy đủ 100% metadata chuẩn Schema.org Person & WebSite | **PASS** |
| **TC-11** | Dung lượng Logo D-13 | Kiểm tra Network tab file logo | Logo tải nhẹ, hiển thị sắc nét | Dung lượng ~45 KB (giảm 80%), hiển thị sắc nét Retina | **PASS** |
| **TC-12** | Nhãn chuyên mục đồng nhất D-14 | Đối chiếu tên 4 tab trên Desktop và Mobile | Tên gọi hoàn toàn trùng khớp | 4 chuyên mục đồng nhất 100% | **PASS** |
| **TC-13** | Lưu trữ Theme D-15 | Đổi Dark Mode, F5 tải lại trang | Giữ nguyên Dark Mode, đồng bộ cùng Portfolio | Theme được lưu trữ bền vững trong localStorage | **PASS** |
| **TC-14** | Vùng chạm cảm ứng D-16 | Thao tác các nút trên màn hình cảm ứng di động | Diện tích bấm tối thiểu 44px | Bấm dễ dàng, không bị bấm nhầm nút lân cận | **PASS** |
| **TC-15** | Bảo toàn Market Pulse D-01 | Kiểm tra 4 thẻ Market Pulse | Số liệu và ngày quan sát chính xác | 100% số liệu bảo toàn nguyên vẹn | **PASS** |
| **TC-16** | Ẩn giao diện Lưu trữ D-03 | Tìm kiếm tab Lưu trữ trên UI | Không nhìn thấy tab Lưu trữ trên giao diện | Tab 05 Lưu trữ được ẩn hoàn toàn theo yêu cầu | **PASS** |

**Tổng kết:** 16/16 kịch bản kiểm thử nghiệm thu đạt kết quả **PASS (100%)**.
