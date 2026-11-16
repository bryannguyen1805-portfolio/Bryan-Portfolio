# BÁO CÁO NGHIỆM THU NGƯỜI DÙNG CUỐI (USER ACCEPTANCE TESTING — UAT REPORT)
## DỰ ÁN: BRYAN FINTECH INTELLIGENCE / BNEWS
### PHIÊN BẢN: PHASE 08B — R1.0.1 (`ED-20261114-D01` | `ẤN BẢN SỐ 29`)

**Mã tài liệu:** `PHASE08B_R1.0.1_UAT_REPORT`  
**Môi trường kiểm thử:** Local HTTP Preview (`http://127.0.0.1:8091/fintech-intelligence/index.html`) trên Google Chrome Headless CDP (`verify_r101_browser.mjs`)  
**Ngày kiểm thử:** `14/11/2026`  
**Tổng kết UAT:** **18/18 kịch bản ĐẠT (100% PASS)**

---

## 1. MA TRẬN KỊCH BẢN KIỂM THỬ THỰC TẾ (UAT EXECUTION MATRIX)

| ID | Kịch bản kiểm thử | Kết quả quan sát thực tế | Trạng thái |
| :--- | :--- | :--- | :---: |
| **UAT-01** | Tải trang lần đầu chưa có `localStorage` | Modal giới thiệu `#welcome-modal-backdrop` tự động mở (`openOnFirstVisit: true`, `aria-hidden: "false"`), không phát sinh lỗi mạng hoặc console (`0` lỗi). | **PASS** |
| **UAT-02** | Xác định ấn bản & thời gian chuẩn | Header hiển thị `THỨ BẢY, 14/11/2026` và huy hiệu `ẤN BẢN SỐ 29` khớp `ED-20261114-D01`. | **PASS** |
| **UAT-03** | Bài đinh trang nhất (Cover Story) | Hiển thị đúng `EVT-04`: *"SHB được Forbes Việt Nam vinh danh trong Top 10 thương hiệu dẫn đầu năm 2026"*; Sapo 3 câu (297 ký tự); Pull Quote độc lập không ngoặc kép với nhãn `■ GÓC NHÌN BIÊN TẬP · ĐÚC KẾT TỪ 25 BẢN TIN TRONG PHIÊN · BRYAN NEWS | FINTECH INTELLIGENCE`. | **PASS** |
| **UAT-04** | Khối Market Pulse & dữ liệu D-01..D-05 | 4 chỉ số giữ nguyên chuẩn: USD/VND `25.637 VND/USD` (`2026-11-14`), Lãi suất `7 %/năm` (`2026-11-13`), VN-Index `1.734,93 Điểm` (`2026-11-14`), Khách quốc tế `+36,8 %` (`10 tháng 2026`). Toàn bộ thẻ Market Pulse & Jump Cards là thẻ `<button type="button">`. | **PASS** |
| **UAT-05** | Mở trình đọc bài chi tiết (`openArticleReader('EVT-04')`) | Side Drawer mở mượt, hiển thị đầy đủ 4 khối cấu trúc: `01. Bản chất sự kiện`, `02. Cơ chế tác động`, `03. Tác động thị trường`, `04. Hàm ý và tín hiệu theo dõi` cùng Sapo, Góc nhìn Fintech & Nguồn đối soát. | **PASS** |
| **UAT-06** | Bộ đếm kết quả ban đầu (`D-08`) | `#newsResultCounterBar` hiển thị `"25 bài phù hợp trên tổng 25 bài đủ điều kiện."`. | **PASS** |
| **UAT-07** | Tìm kiếm từ khóa `"ACB"` (không có trong ED-29) | Bộ đếm cập nhật `"0 bài phù hợp trên tổng 25 bài đủ điều kiện."`; hiển thị Empty State `"🔍 Không tìm thấy bản tin phù hợp với từ khóa hoặc bộ lọc hiện tại. Xóa bộ lọc"`; bấm nút `"Xóa bộ lọc"` khôi phục về 25 bài. | **PASS** |
| **UAT-08** | Tìm kiếm từ khóa `"SHB"` | Bộ đếm hiển thị `"1 bài phù hợp trên tổng 25 bài đủ điều kiện."`; bài đầu là `"SHB được Forbes Việt Nam vinh danh trong Top 10 thương hiệu dẫn đầu năm 2026"`. | **PASS** |
| **UAT-09** | Lọc danh mục `"Thanh toán"` & `"Ngân hàng"` | Chọn `"Thanh toán"` → `"0 bài phù hợp trên tổng 25 bài đủ điều kiện."` kèm Empty State + Reset; chọn `"Ngân hàng"` → `"7 bài phù hợp trên tổng 25 bài đủ điều kiện."`. | **PASS** |
| **UAT-10** | Tìm kiếm chuỗi không tồn tại `"zzzzqqq"` & Reset | Hiển thị `"0 bài phù hợp trên tổng 25 bài đủ điều kiện."` kèm Empty State; bấm `"Xóa bộ lọc"` phục hồi `"25 bài phù hợp trên tổng 25 bài đủ điều kiện."`. | **PASS** |
| **UAT-11** | Migrate & lưu trữ Theme `'site_theme'` (`D-15`) | Cấy `localStorage['ms-theme']='dark'` và reload → `data-theme="dark"`, `site_theme="dark"`, `ms-theme=null`; bật tắt theme giữ khóa `'site_theme'` duy nhất (`ms-theme` luôn `null`). | **PASS** |
| **UAT-12** | Điều hướng bàn phím `role="tablist"` Desktop | Focus `#navTabToday` → `ArrowRight` chuyển `#navTabMarket` (`#market`), `End` chuyển `#navTabB2B` (`#b2b`), `Home` về `#navTabToday`, `ArrowLeft` vòng về `#navTabB2B`. | **PASS** |
| **UAT-13** | Điều hướng bàn phím `role="tablist"` Mobile (390px) | Focus `#mobileTabToday` → `ArrowRight` chuyển `#mobileTabMarket`, `End` chuyển `#mobileTabB2B`, `Home` về `#mobileTabToday`. | **PASS** |
| **UAT-14** | Focus Trap trên Welcome Modal, Contact Modal & Side Drawer | Không lọt `Tab` (12 bước) hay `Shift+Tab` ra ngoài (`escapedTab: false`, `shiftInside: true`), `#mainContent` có `aria-hidden="true"` và `inert: true`, nhấn `Escape` đóng modal và trả focus về đúng phần tử kích hoạt. | **PASS** |
| **UAT-15** | Đóng Overlay bằng thao tác click Backdrop | Click `#contact-modal-backdrop` đóng Contact Modal (`contactAfterClick: false`); click `#drawerBackdrop` đóng Side Drawer (`drawerAfterOverlay: false`). | **PASS** |
| **UAT-16** | Kiểm tra độ tương phản Light & Dark Mode | Light Mode (795 phần tử): `minRatio = 5.02`, `failCount = 0`; Dark Mode (795 phần tử): `minRatio = 4.83`, `failCount = 0`. | **PASS** |
| **UAT-17** | Kiểm tra tràn ngang & cỡ chữ trên 6 độ phân giải | `320, 360, 390, 768, 1024, 1440`px qua cả 4 tab: `0` tràn ngang (`diff <= 0`), `0` văn bản `< 12px`. | **PASS** |
| **UAT-18** | Kiểm tra vùng chạm di động (`<= 768px`) & Menu đơn | Trên `320, 360, 390, 768`px qua cả 4 tab (kể cả khi mở `.floating-widget`): `smallTargetCount = 0`; chỉ có 4 `.ms-quick-tab` hiển thị (`btnOpenMobileNav`, `mobileMenuToggle`, `mobileNavDrawer`, `quickTabDrawer` = `false`). | **PASS** |

---

## 2. KẾT LUẬN NGHIỆM THU KỸ THUẬT

Phiên bản **PHASE08B_R1.0.1** vượt qua **18/18 kịch bản UAT** trong trình duyệt thực tế, không ghi nhận lỗi console/HTTP, sẵn sàng trình Chủ sản phẩm xem xét nghiệm thu (chưa xuất bản Production).
