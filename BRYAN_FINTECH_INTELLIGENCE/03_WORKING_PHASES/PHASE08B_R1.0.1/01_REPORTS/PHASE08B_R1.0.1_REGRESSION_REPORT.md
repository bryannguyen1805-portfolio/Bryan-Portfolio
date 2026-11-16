# BÁO CÁO KIỂM THỬ HỒI QUY (REGRESSION TEST REPORT — D-01 TO D-16)
## DỰ ÁN: BRYAN FINTECH INTELLIGENCE / BNEWS
### PHIÊN BẢN: PHASE 08B — R1.0.1 (`ED-20261114-D01` | `ẤN BẢN SỐ 29`)

**Mã tài liệu:** `PHASE08B_R1.0.1_REGRESSION_REPORT`  
**Phiên bản tham chiếu kế thừa:** `PHASE08A_R1.0.1` (D-01..D-05) & `PHASE08B_R1.0.0` (D-06..D-16)  
**Ngày kiểm tra:** `14/11/2026`

---

## 1. BẢO TOÀN ĐỘ TIN CẬY NỀN (D-01 → D-05 & MARKET PULSE ED-29)

| Nhóm kiểm tra hồi quy | Kết quả xác minh thực tế trên R1.0.1 | Trạng thái |
| :--- | :--- | :---: |
| **Edition Identity & Freshness (`ED-20261114-D01`)** | `ẤN BẢN SỐ 29` · `THỨ BẢY, 14/11/2026` · `PASS_25_EVENTS_24H_80PCT` (`25/25` tin trong 0–24h = 100.0%, `rejectedEvents: 2`). | **PASS (NO REGRESSION)** |
| **Market Pulse — `01. TỶ GIÁ NGOẠI HỐI & CAN THIỆP USD/VND`** | `25.637 VND/USD` · `Phiên: 2026-11-14` (`publishedAt: 2026-11-14T08:22:47+07:00`). | **PASS (PRESERVED)** |
| **Market Pulse — `02. LÃI SUẤT TIỀN GỬI 12T CAO NHẤT`** | `7 %/năm` · `Phiên: 2026-11-13` (`publishedAt: 2026-11-13T08:30:00+07:00`). | **PASS (PRESERVED)** |
| **Market Pulse — `03. CHỈ SỐ VN-INDEX`** | `1.734,93 Điểm` · `Phiên: 2026-11-14` (`publishedAt: 2026-11-14T07:42:37+07:00`). | **PASS (PRESERVED)** |
| **Market Pulse — `04. KHÁCH DU LỊCH QUỐC TẾ ĐẾN VIỆT NAM`** | `+36,8 %` · `Kỳ: 10 tháng 2026` (`publishedAt: 2026-10-31T23:59:59+07:00`). | **PASS (PRESERVED)** |
| **Giao diện MagSpread & Archive Gate (`D-01..D-05`)** | Giữ nguyên hệ lưới MagSpread biên tập phẳng; `#navGroupArchive` giữ `display: none` & `aria-hidden="true"`; nút mở chi tiết Market Pulse hoạt động chính xác (`SideDrawer`). | **PASS (NO REGRESSION)** |
| **Welcome Popup truy cập lần đầu** | Tự động bật `#welcome-modal-backdrop` cho người dùng lần đầu chưa có khóa `bryan_fintech_welcome_shown_v1`, giữ header sạch không có nút giới thiệu dư thừa. | **PASS (PRESERVED)** |

---

## 2. ĐỒNG BỘ MÃ NGUỒN ĐA THƯ MỤC & TÍNH TOÀN VẸN CÚ PHÁP

Kiểm tra `shasum -a 256` xác nhận trùng khớp tuyệt đối byte-by-byte cho cả 5 tệp chính (`index.html`/`magspread-preview.html`, `magspread.css`, `magspread.js`, `edition-data.json`, `edition-data.js`) trên:
1. `fintech-intelligence/`
2. `pilot-output/`
3. `pilot-output/daily-run-package/`
4. `BRYAN_FINTECH_INTELLIGENCE/03_WORKING_PHASES/PHASE08B_R1.0.1/02_SOURCE_CODE/`

Kiểm tra cú pháp (`node --check magspread.js`), kiểm tra chạy builder (`python3 update_magspread_pilot_ui.py --date 2026-11-14`) và kiểm tra runtime Headless Chrome đều kết thúc với `0` lỗi JavaScript, `0` lỗi mạng `>= 400`, và `0` hồi quy D-01..D-16.

---

## 3. RÀNG BUỘC PHÁT HÀNH (RELEASE SAFETY)

- **Chưa deploy Production:** Không thực hiện đẩy mã hay thay đổi cấu hình Production trực tiếp.
- **Bản gốc & Backup được bảo toàn:** `PHASE08B_R1.0.0_CANDIDATE.zip`, `PHASE08B_R1.0.0_BACKUP.zip` và `PHASE08B_R1.0.1_BACKUP.zip` còn nguyên vẹn với SHA-256 kiểm chứng.
