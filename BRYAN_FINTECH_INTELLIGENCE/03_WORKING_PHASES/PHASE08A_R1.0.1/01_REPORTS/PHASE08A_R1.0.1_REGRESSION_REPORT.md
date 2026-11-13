# BÁO CÁO KIỂM THỬ HỒI QUY TOÀN DIỆN (REGRESSION TEST REPORT)
## DỰ ÁN: BRYAN FINTECH INTELLIGENCE
### PHIÊN BẢN: PHASE 08A — R1.0.1
**Mã tài liệu:** PHASE08A_R1.0.1_REGRESSION_REPORT  
**Ấn bản kiểm thử:** ED-20261113-D01 | **Môi trường:** Production URL (`https://bryanportfolio.io.vn/fintech-intelligence/index.html`)  
**Tác giả:** QA Lead & Senior Technical Director  
**Kết quả chung cuộc:** **PASS — 100% TÍNH NĂNG HOẠT ĐỘNG ỔN ĐỊNH, KHÔNG PHÁT SINH LỖI MỚI**

---

## 1. MA TRẬN ĐIỀU HƯỚNG & ROUTING (NAVIGATION REGRESSION)

| Kịch bản kiểm thử | Hành động thực hiện | Kết quả mong đợi | Kết quả thực tế | Trạng thái |
|:---|:---|:---|:---|:---:|
| **Desktop Tab 01** | Bấm `01. HÔM NAY` | Kích hoạt màn hình Hôm Nay, URL `#today` | Chuyển mượt mà, hiển thị Cover Story | **PASS** |
| **Desktop Tab 02** | Bấm `02. THỊ TRƯỜNG & TIN TỨC` | Kích hoạt Thị Trường, URL `#market` | Hiển thị Market Pulse & The News Desk | **PASS** |
| **Desktop Tab 03** | Bấm `03. PHÂN TÍCH & HỌC TẬP` | Kích hoạt Phân Tích, URL `#analysis` | Hiển thị Macro to Micro & Learning Hub | **PASS** |
| **Desktop Tab 04** | Bấm `04. CƠ HỘI B2B` | Kích hoạt B2B, URL `#b2b` | Hiển thị Executive Decision & Signals | **PASS** |
| **Desktop Tab 05** | Kiểm tra hiển thị Tab 05 | Hoàn toàn ẩn khỏi thanh điều hướng | Ẩn sạch sẽ (`display: none !important`) | **PASS** |
| **Legacy URL Fallback**| Truy cập trực tiếp link `#archive` | Tự động chuyển hướng về `#today` | URL đổi thành `#today`, không lỗi DOM | **PASS** |
| **Mobile Drawer Nav** | Mở Drawer Menu trên di động | Hiển thị 4 phân hệ cốt lõi | Hiển thị 4 item, đóng mở mượt | **PASS** |
| **Mobile Quick Bar** | Chạm các pill ở đáy màn hình | Chuyển tab tương ứng tức thì | Điều hướng êm dịu, cuộn trơn tru | **PASS** |

---

## 2. ĐỐI SOÁT DỮ LIỆU THỊ TRƯỜNG (MARKET PULSE REGRESSION)

| Thẻ dữ liệu | Tên chỉ số | Giá trị hiển thị | Đơn vị | Nhãn kỳ/phiên | Ngày quan sát | Nguồn xác minh | Trạng thái |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Card 01** | Tỷ giá can thiệp USD/VND | `25.611 VND/USD` | VND/USD | `Phiên: 2026-11-11` | 2026-11-11 | Cục QL Ngoại hối NHNN | **PASS** |
| **Card 02** | Lãi suất tiền gửi 12T | `7 %/năm` | %/năm | `Phiên: 2026-11-10` | 2026-11-10 | Biểu niêm yết NHTM | **PASS** |
| **Card 03** | Chỉ số VN-Index | `1.743,00 Điểm` | Điểm | `Phiên: 2026-11-10` | 2026-11-10 | Chốt phiên HoSE | **PASS** |
| **Card 04** | Khách du lịch quốc tế | `+36,8 %` | % (YoY) | `Kỳ: 10 tháng 2026` | Tháng 10/2026 | TCTK & Báo chí chính thống | **PASS** |

*Ghi chú đặc biệt về Card 04 (R-04):* Giá trị `+36,8 %` biểu thị tốc độ tăng trưởng lũy kế 10 tháng năm 2026 so với cùng kỳ năm trước. Dữ liệu trên giao diện và trong file JSON hoàn toàn ăn khớp và phản ánh đúng bản chất kinh tế.

---

## 3. ĐÁNH GIÁ TRẢI NGHIỆM GIAO DIỆN & CHỦ ĐỀ (UI/UX & THEME)

1. **Light & Dark Theme Parity:**
   - Nút chuyển theme (`#themeToggleBtn`): Chuyển đổi êm dịu giữa chế độ Sáng (Cream & British Racing Green) và chế độ Tối (Deep Teal Dark Slate).
   - Logo Bnews tự động hoán đổi hình ảnh: `bnews-logo-light.png` trên nền sáng và `bnews-logo-dark.png` trên nền tối.
2. **Kích thước logo cố định:**
   - Header Logo: Khóa kích thước hiển thị `119 × 36px` với `aspect-ratio: 1024/309`.
   - Footer Logo: Khóa kích thước hiển thị `126 × 38px` với `aspect-ratio: 1024/309`.
3. **Drawer Thông tin chi tiết (Market Pulse Drawer):**
   - Bấm "Chi tiết & Nguồn →": Drawer trượt ra từ bên phải màn hình hiển thị đầy đủ phương pháp luận, nguồn tin, trích dẫn báo chí và nút liên kết gốc.

---

## 4. KIỂM THỬ KHẢ NĂNG CO GIÃN THIẾT BỊ (RESPONSIVE VIEWPORT SUITE)

Đo kiểm tại 6 kích thước tiêu chuẩn:
- **320px (Mobile Compact):** `scrollWidth = 320`, không có thanh trượt ngang, không mất chữ.
- **360px (Android Common):** `scrollWidth = 360`, tỷ lệ hiển thị cân đối.
- **390px (iPhone Standard):** `scrollWidth = 390`, bố cục thẻ phân tích rõ ràng.
- **768px (Tablet Portrait):** `scrollWidth = 768`, chia 2 cột thẻ nhịp nhàng.
- **1280px (Laptop Standard):** `scrollWidth = 1265`, hiển thị đầy đủ thanh điều hướng desktop.
- **1440px (Desktop High-Res):** `scrollWidth = 1425`, bố cục MagSpread cao cấp.

---

## 5. ĐỘ BỀN PIPELINE VẬN HÀNH HÀNG NGÀY (DAILY AUTOMATION)

Thực hiện 2 lần chạy kiểm thử độc lập đối với script `python3 run_daily_edition.py`:
- **Lần chạy 1 (00:02):** Thời gian thực thi 1.97 giây. Nhận diện ngày mới, kích hoạt Live Runtime Orchestrator, tổng hợp và xuất bản JSON thành công.
- **Lần chạy 2 (00:34):** Thời gian thực thi 2.15 giây. Đồng bộ dữ liệu sang `pilot-output/daily-run-package/` và `fintech-intelligence/`, tự động bơm timestamp cache buster `?v=TIMESTAMP`.
- **Dữ liệu Archive:** Toàn bộ 2.341 file lịch sử trong thư mục `06_DAILY_EDITIONS` không hề bị ảnh hưởng, ghi đè hay thất thoát.

---

## 6. KẾT LUẬN

Tất cả các ca kiểm thử hồi quy đều đạt kết quả **PASS**. Phiên bản **PHASE08A_R1.0.1** duy trì sự ổn định tối đa của hệ thống và sẵn sàng cho việc nghiệm thu chính thức.
