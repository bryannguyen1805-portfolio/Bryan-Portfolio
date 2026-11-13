# KIẾN TRÚC NGUỒN DỮ LIỆU CHUẨN DUY NHẤT (SINGLE SOURCE OF TRUTH)
## DỰ ÁN: BRYAN FINTECH INTELLIGENCE
### PHIÊN BẢN: PHASE 08A — R1.0.1
**Mã tài liệu:** PHASE08A_R1.0.1_SOURCE_OF_TRUTH  
**Ấn bản chính thức:** ED-20261113-D01 | **Trạng thái:** SYNCHRONIZED & LOCKED  
**Tác giả:** Giám đốc Kỹ thuật Cấp cao & Kiến trúc sư Trưởng  

---

## 1. PHÂN ĐỊNH RANH GIỚI VAI TRÒ CÁC TẦNG HỆ THỐNG

Để tránh hoàn toàn tình trạng sai lệch hoặc xung đột giữa các bản sao dữ liệu trong Candidate, kiến trúc dữ liệu của Bryan Fintech Intelligence được chuẩn hóa theo 5 tầng phân định rõ ràng:

```
[TẦNG 1: DỮ LIỆU TÌNH BÁO GỐC]
   BRYAN_FINTECH_INTELLIGENCE/.../06_DAILY_EDITIONS/daily-editions/<date>/
                           │
                           ▼
[TẦNG 2: SOURCE CODE & PIPELINE ENGINE]
   update_magspread_pilot_ui.py  +  run_daily_edition.py
                           │
                           ▼
[TẦNG 3: CANONICAL GENERATED OUTPUT (NGUỒN DỮ LIỆU CHUẨN DUY NHẤT)]
   pilot-output/edition-data.json (và edition-data.js)
                           │
         ┌─────────────────┴─────────────────┐
         ▼                                   ▼
[TẦNG 4: RUNTIME STAGING]            [TẦNG 5: PRODUCTION DEPLOYMENT]
   pilot-output/daily-run-package/      fintech-intelligence/
   (Gói phục vụ chạy tự động)            (Cổng phát hành GitHub Pages)
         │                                   │
         └─────────────────┬─────────────────┘
                           ▼
[LƯU TRỮ PHIÊN BẢN: PHASE WORKING REPO]
   BRYAN_FINTECH_INTELLIGENCE/03_WORKING_PHASES/PHASE08A_R1.0.1/02_SOURCE_CODE/
```

### Chi tiết vai trò từng tầng:
1. **Tầng 1 (Raw Intelligence Store):** Nơi lưu trữ toàn bộ các file phân tích, trích xuất dữ liệu thị trường của từng ngày (2,341 files lịch sử). Tuyệt đối chỉ đọc (Read-only), không chỉnh sửa tay.
2. **Tầng 2 (Transformation Engine):** Mã nguồn Python chịu trách nhiệm đối soát, làm sạch, định dạng số học (vi-VN) và gán nhãn dữ liệu chuẩn xác.
3. **Tầng 3 (Canonical Output):** Là điểm phát hành gốc duy nhất (`pilot-output/edition-data.json`). Mọi bản sao khác của file dữ liệu này trong hệ thống đều phải được sao chép trực tiếp từ đây và phải có mã băm SHA-256 hoàn toàn trùng khớp.
4. **Tầng 4 & 5 (Operational Packages):** Các thư mục phục vụ vận hành thực tế (Staging Package và Web Public Root). Không bao giờ được phép chỉnh sửa dữ liệu trực tiếp trong hai thư mục này; mọi cập nhật phải bắt nguồn từ Tầng 2.

---

## 2. QUY CHUẨN ĐỒNG NHẤT ẤN BẢN (EDITION ID GOVERNANCE)

### 2.1. Mã ấn bản chính thức
- **Mã ấn bản chuẩn (Canonical Edition ID):** **`ED-20261113-D01`**
- **Tên hiển thị:** **ẤN BẢN SỐ 28**
- **Ngày ấn bản:** **Thứ Sáu, ngày 13/11/2026**
- **Thời điểm đóng cổng kiểm định (Cutoff):** `2026-11-13T09:28:45.112309+07:00`
- **Tỷ lệ bài viết hợp lệ 0–24h:** **24/25 bài (96.0%)**

### 2.2. Phân định rạch ròi giữa Ngày xuất bản và Ngày quan sát thị trường
Một ấn bản báo chí chuyên nghiệp luôn phản ánh các số liệu tài chính được ghi nhận tại các phiên giao dịch chính thức gần nhất. Do đó, nghiêm cấm việc đồng nhất các mốc thời gian này:
- **Ngày xuất bản ấn bản (Edition Publication Date):** `13/11/2026` (Ngày phát hành số báo đến độc giả).
- **Ngày quan sát USD/VND (Observation Date):** `2026-11-11` (Theo công bố can thiệp của NHNN).
- **Ngày quan sát VN-Index (Observation Date):** `2026-11-10` (Phiên giao dịch HoSE chốt phiên).
- **Ngày quan sát Lãi suất 12T (Observation Date):** `2026-11-10` (Biểu niêm yết NHTM).
- **Kỳ quan sát Khách du lịch (Observation Period):** `10 tháng 2026` (Báo cáo tháng 10 của TCTK).

---

## 3. BẰNG CHỨNG ĐỐI SOÁT CHÉO TÍNH TOÀN VẸN (SHA-256 HASH PARITY)

Đo lường trực tiếp mã băm SHA-256 trên toàn bộ 4 bản sao dữ liệu trong Candidate:

| Đường dẫn tập tin | Dung lượng (Bytes) | Mã băm SHA-256 | Kết quả đối soát |
|:---|:---:|:---|:---:|
| `pilot-output/edition-data.json` | 302.579 | `457e06184c29eb25a9a9609198f0c8204db876fd6f9fa95e06d325d35d4d5b74` | **GỐC (CANONICAL)** |
| `pilot-output/daily-run-package/edition-data.json` | 302.579 | `457e06184c29eb25a9a9609198f0c8204db876fd6f9fa95e06d325d35d4d5b74` | **100% PARITY** |
| `fintech-intelligence/edition-data.json` | 302.579 | `457e06184c29eb25a9a9609198f0c8204db876fd6f9fa95e06d325d35d4d5b74` | **100% PARITY** |
| `02_SOURCE_CODE/edition-data.json` | 302.579 | `457e06184c29eb25a9a9609198f0c8204db876fd6f9fa95e06d325d35d4d5b74` | **100% PARITY** |

**Kết luận:** Đạt tính toàn vẹn 100% byte-for-byte trên toàn bộ các phân vùng của hệ sinh thái dự án.
