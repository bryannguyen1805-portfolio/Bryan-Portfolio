# BÁO CÁO ÁNH XẠ DỮ LIỆU LƯU TRỮ GOOGLE SHEETS
## ARCHIVE DATA MAPPING & TRANSFORMATION REPORT
**Dự án:** Bryan FinTech Intelligence — MagSpread Editorial Edition  
**Phân hệ:** Phase 04B — Google Sheets Integration  
**Tệp dữ liệu chứng thực:** `pilot-output/phase04b-sheets-staging/staging_tables.json`  
**Ngày báo cáo:** 2026-11-09  

---

## 1. TỔNG QUAN KẾT QUẢ ÁNH XẠ DỮ LIỆU TẦNG STAGING

Hệ thống đã triển khai bộ chuyển đổi dữ liệu xác định (**Deterministic Transformation Engine** - `sheets_sync_engine.py`) bóc tách toàn bộ dữ liệu từ các tệp vận hành lõi (`edition-data.json`, `verified_events.json`, `source_ledger.json`, `event_registry.json`) sang **155 hàng dữ liệu chuẩn hóa** trải dài trên 7 tab:

| Tên tab trên Google Sheets | Số hàng dữ liệu thực tế | Số cột schema quy định | Số cột thực tế ánh xạ | Khóa chính (Primary Key) | Trạng thái tuân thủ |
| :--- | :---: | :---: | :---: | :--- | :---: |
| **1. `EDITIONS`** | **3 hàng** | 15 cột | 15 cột | `editionId` | **PASS (100%)** |
| **2. `NEWS_EVENTS`** | **21 hàng** | 20 cột | 20 cột | `(editionId, eventId)` | **PASS (100%)** |
| **3. `EDITORIAL_SECTIONS`** | **5 hàng** | 11 cột | 11 cột | `(editionId, sectionKey)` | **PASS (100%)** |
| **4. `MARKET_PULSE_HISTORY`** | **8 hàng** | 14 cột | 14 cột | `(editionId, indicatorId)` | **PASS (100%)** |
| **5. `EVENT_REGISTRY`** | **67 hàng** | 13 cột | 13 cột | `eventId` | **PASS (100%)** |
| **6. `SOURCE_LEDGER`** | **50 hàng** | 12 cột | 12 cột | `(collectionRunId, sourceUrl)` | **PASS (100%)** |
| **7. `PUBLISH_AUDIT`** | **1 hàng** | 12 cột | 12 cột | `auditLogId` | **PASS (100%)** |
| **TỔNG CỘNG:** | **155 hàng** | — | — | **7/7 Tab đạt chuẩn** | **PASS TOÀN DIỆN** |

---

## 2. CHI TIẾT NGUỒN DỮ LIỆU ĐƯỢC CHUYỂN ĐỔI

### 2.1. Tab 1: `EDITIONS` (3 bản ghi)
Bảo lưu đầy đủ ấn bản hiện tại và toàn bộ lịch sử ấn bản đã nghiệm thu:
1. `EDITION-2026-11-08-PILOT25`: Ngày 08/11/2026, Ấn bản số 24 (Pilot 25), trạng thái `DRAFT_INTERNAL_ONLY` / `FAIL_SHORTFALL_24H_PREVIEW_ONLY` (Độ tươi 52.38%, 21 tin hợp lệ).
2. `EDITION-2026-11-07-PILOT24`: Ngày 07/11/2026, Ấn bản số 23, trạng thái `ĐÃ LƯU TRỮ (ARCHIVED)` / `PASS_PUBLISHED` (Độ tươi 84.00%, 25 tin hợp lệ).
3. `EDITION-2026-11-06-PILOT23`: Ngày 06/11/2026, Ấn bản số 22, trạng thái `ĐÃ LƯU TRỮ (ARCHIVED)` / `PASS_PUBLISHED` (Độ tươi 88.00%, 25 tin hợp lệ).

### 2.2. Tab 2: `NEWS_EVENTS` (21 bản ghi)
Ánh xạ 21 sự kiện tin tức hợp lệ của Pilot 25, bao gồm đầy đủ các phân tích sâu:
- `EVT-01` đến `EVT-25` (loại bỏ EVT-03, 08, 19, 21 theo quyết định của Gate kiểm định).
- Mỗi sự kiện mang đầy đủ chuỗi truyền dẫn vĩ mô sang vi mô (`macroToMicro`), tác động hạ tầng thanh toán Payoo (`fintechImpact`), và băm SHA-256 đối soát.

### 2.3. Tab 3: `EDITORIAL_SECTIONS` (5 phân hệ biên tập)
Bóc tách trực tiếp từ `editorialSections` của `edition-data.json`:
1. `sec02_coverStory`: TIÊU ĐIỂM HÔM NAY · CORE EDITORIAL THESIS
2. `sec04b_decisionBrief`: NHỮNG TÍN HIỆU TÔI CẦN CHÚ Ý HÔM NAY
3. `sec06_macroToMicro`: CHUỖI TRUYỀN DẪN VĨ MÔ → VI MÔ (MACRO TO MICRO)
4. `sec07_paymentRadar`: PAYMENT OPPORTUNITY RADAR · CƠ HỘI PHÁT TRIỂN KINH DOANH B2B
5. `sec08b_watchlist`: ĐIỀU CẦN THEO DÕI TIẾP · MONITORING & DECISION WATCHLIST

### 2.4. Tab 4: `MARKET_PULSE_HISTORY` (8 chỉ số thị trường)
Ánh xạ 8 chỉ số cố định của `marketPulseSnapshot`:
- `vnindex`: 1.725,36 điểm (-15,37 điểm, -0,88%)
- `usdvnd_central`: 26.347 VND/USD (+12 VND, +0,05%)
- `interbank_on`: 5,88%/năm (+0,32% điểm)
- `market_liquidity`: 20.400 tỷ đồng
- `bond_yield_10y`: 3,15%/năm
- `fii_net_flow`: +409 tỷ đồng (HoSE)
- `credit_growth_ytd`: 10,08%
- `qr_volume_share`: 58,4%

### 2.5. Tab 5: `EVENT_REGISTRY` (67 sự kiện lịch sử)
Gồm 28 sự kiện nền tảng trước đó cộng thêm 39 sự kiện độc bản mới đã được nghiệm thu qua 5 Gate từ Phase 04A. Đảm bảo chống trùng lặp tuyệt đối cho các ấn bản ngày 09/11 và các ngày kế tiếp.

### 2.6. Tab 6: `SOURCE_LEDGER` (50 liên kết bài viết)
Toàn bộ 50 URL bài viết mạng thật được quét và đối soát trong đợt chạy trực tiếp Phase 04A, lưu trữ mã trạng thái HTTP, băm SHA-256 và bằng chứng snapshot.

### 2.7. Tab 7: `PUBLISH_AUDIT` (1 bản ghi kiểm toán)
Ghi nhận phiên kiểm toán đồng bộ staging dry-run với mã băm SHA-256 bất biến của `edition-data.json`:
`c95a591a4b695e51f980737d0f5c3a85e498023292c1c62e63daed0bf3dbe67a`.

---

## 3. TỆP XUẤT BẢN CSV KIỂM TRA ĐỘC LẬP

Hệ thống đã xuất bản đồng thời 7 tệp CSV sạch tại `pilot-output/phase04b-sheets-staging/csv_exports/` phục vụ kiểm tra bằng mắt hoặc tải lên trực tiếp bằng tay khi chưa cấp quyền API:
- `EDITIONS.csv` (3 hàng)
- `NEWS_EVENTS.csv` (21 hàng)
- `EDITORIAL_SECTIONS.csv` (5 hàng)
- `MARKET_PULSE_HISTORY.csv` (8 hàng)
- `EVENT_REGISTRY.csv` (67 hàng)
- `SOURCE_LEDGER.csv` (50 hàng)
- `PUBLISH_AUDIT.csv` (1 hàng)
