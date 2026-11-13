# ĐẶC TẢ CHI TIẾT SCHEMA 7 TAB GOOGLE SHEETS
## GOOGLE SHEETS ARCHIVAL DATABASE SCHEMA SPECIFICATION — V1.0
**Dự án:** Bryan FinTech Intelligence — MagSpread Editorial Edition  
**Phân hệ:** Phase 04B — Google Sheets Integration  
**Tệp định nghĩa mã nguồn:** `pilot-output/phase04b-sheets-staging/sheets_schema.py`  
**Ngày hiệu lực:** 2026-11-09  

---

## 1. TAB 1: `EDITIONS` — DANH MỤC ẤN BẢN
- **Mục đích:** Lưu trữ thông tin định danh cấp ấn bản, trạng thái xuất bản, kết quả cổng kiểm soát độ tươi và số liệu tổng hợp.
- **Khóa chính (PK):** `editionId`
- **Quy tắc cập nhật:** Bất biến (Immutable) đối với các ấn bản đã `PUBLISHED`. Chỉ cho phép cập nhật ấn bản xem trước (`PREVIEW_ONLY` / `DRAFT`) kèm lịch sử kiểm toán.

| STT | Tên cột | Kiểu dữ liệu | Bắt buộc | Mô tả nghiệp vụ | Ví dụ thực tế |
| :---: | :--- | :---: | :---: | :--- | :--- |
| 1 | `editionId` | `STRING` | **CÓ (PK)** | Mã định danh chuẩn tắc của ấn bản | `EDITION-2026-11-08-PILOT25` |
| 2 | `editionNumber` | `STRING` | **CÓ** | Tên số thứ tự ấn bản hiển thị | `Ấn bản số 24 (Pilot 25)` |
| 3 | `editionDate` | `DATE` | **CÓ** | Ngày xuất bản theo lịch (YYYY-MM-DD) | `2026-11-08` |
| 4 | `displayDate` | `STRING` | CÓ | Ngày hiển thị địa phương hóa | `08/11/2026` |
| 5 | `cutoffTime` | `DATETIME_ISO` | **CÓ** | Mốc thời gian chốt tin tại múi giờ +07:00 | `2026-11-08T12:24:46+07:00` |
| 6 | `publicationStatus` | `ENUM` | **CÓ** | `PUBLISHED` \| `DRAFT_INTERNAL_ONLY` \| `PREVIEW_ONLY` | `DRAFT_INTERNAL_ONLY` |
| 7 | `gateStatus` | `ENUM` | **CÓ** | `PASS_ALL_GATES` \| `FAIL_SHORTFALL_24H_PREVIEW_ONLY` | `FAIL_SHORTFALL_24H_PREVIEW_ONLY` |
| 8 | `freshnessRatio` | `PERCENTAGE` | **CÓ** | Tỷ lệ tin trong cửa sổ 0-24h | `52.38%` |
| 9 | `eligibleCount` | `INTEGER` | **CÓ** | Tổng số tin hợp lệ trong ấn bản | `21` |
| 10 | `count0To24h` | `INTEGER` | **CÓ** | Số tin thuộc cửa sổ 0–24h | `11` |
| 11 | `count24To48h` | `INTEGER` | **CÓ** | Số tin thuộc cửa sổ 24–48h | `9` |
| 12 | `count48To72h` | `INTEGER` | **CÓ** | Số tin thuộc cửa sổ 48–72h | `1` |
| 13 | `leadStoryTitle` | `STRING` | KHÔNG | Tiêu đề bài viết tiêu điểm hôm nay | `Siết chặt lá chắn bảo mật số...` |
| 14 | `macroTheme` | `STRING` | KHÔNG | Chủ đề vĩ mô chi phối ấn bản | `Quản trị chi phí vốn ngân hàng` |
| 15 | `archivedAt` | `DATETIME_ISO` | **CÓ** | Thời điểm ghi bản ghi vào kho | `2026-11-09T00:38:08+07:00` |

---

## 2. TAB 2: `NEWS_EVENTS` — CHI TIẾT SỰ KIỆN TIN TỨC
- **Mục đích:** Lưu trữ chi tiết 21–25 sự kiện của từng ấn bản, nguồn tin, băm SHA-256 và phân tích tài chính.
- **Khóa chính (PK):** Khóa kết hợp `(editionId, eventId)`
- **Khóa ngoại (FK):** `editionId` liên kết với `EDITIONS.editionId`
- **Quy tắc cập nhật:** Append-only cho mỗi ấn bản mới. Cấm ghi trùng cặp `(editionId, eventId)`.

| STT | Tên cột | Kiểu dữ liệu | Bắt buộc | Mô tả nghiệp vụ |
| :---: | :--- | :---: | :---: | :--- |
| 1 | `editionId` | `STRING` | **CÓ (FK)** | Mã ấn bản sở hữu tin tức |
| 2 | `eventId` | `STRING` | **CÓ (PK)** | Mã định danh sự kiện (EVT-01, EVT-P04A-001) |
| 3 | `stt` | `INTEGER` | **CÓ** | Số thứ tự hiển thị trong chuyên mục (1–25) |
| 4 | `headline` | `STRING` | **CÓ** | Tiêu đề biên tập tin tức |
| 5 | `category` | `STRING` | **CÓ** | Ngân hàng & Fintech \| Thị trường vốn \| Vĩ mô... |
| 6 | `tier` | `INTEGER` | **CÓ** | Phân hạng trọng yếu: 1 (Trọng tâm), 2 (Chiến lược) |
| 7 | `sourceName` | `STRING` | **CÓ** | Tên đơn vị xuất bản gốc (CafeF, SBV, NAPAS) |
| 8 | `canonicalUrl` | `URL` | **CÓ** | Đường dẫn URL chuẩn tắc kiểm chứng |
| 9 | `originalSourcePublishedAt` | `DATETIME_ISO` | **CÓ** | Mốc thời gian báo chí đăng bài |
| 10 | `timeDeltaFromCutoff` | `STRING` | **CÓ** | Khoảng cách thời gian tính từ mốc chốt tin (e.g. 3.0h) |
| 11 | `timeWindowBucket` | `ENUM` | **CÓ** | `0–24h` \| `24–48h` \| `48–72h` |
| 12 | `verificationStatus` | `ENUM` | **CÓ** | `VERIFIED` \| `PARTIAL` \| `REJECTED` |
| 13 | `dedupStatus` | `ENUM` | **CÓ** | `UNIQUE_NEW_EVENT` \| `FOLLOW_UP_MATERIAL_DEVELOPMENT` |
| 14 | `isFollowUp` | `BOOLEAN` | **CÓ** | Cờ đánh dấu bước phát triển mới (TRUE/FALSE) |
| 15 | `followUpTo` | `STRING` | KHÔNG | Mã sự kiện tiền đề nếu là bài viết nối tiếp |
| 16 | `evidenceSha256` | `STRING_HEX` | **CÓ** | Mã băm SHA-256 bất biến của văn bản gốc |
| 17 | `verifiedFactSummary` | `STRING` | **CÓ** | Dữ kiện số liệu cốt lõi đã được kiểm định |
| 18 | `macroToMicro` | `STRING` | KHÔNG | Chuỗi truyền dẫn từ vĩ mô đến vi mô |
| 19 | `fintechImpact` | `STRING` | KHÔNG | Tác động cụ thể đến Payoo và hệ thống thanh toán |
| 20 | `prediction` | `STRING` | KHÔNG | Dự báo định hướng và mức độ tin cậy |

---

## 3. TAB 3: `EDITORIAL_SECTIONS` — PHÂN TÍCH BIÊN TẬP ĐẶC BIỆT
- **Khóa chính (PK):** Khóa kết hợp `(editionId, sectionKey)`
- **Các phân hệ hỗ trợ:** `sec02_coverStory`, `sec04b_decisionBrief`, `sec06_macroToMicro`, `sec07_paymentRadar`, `sec08b_watchlist`.

| STT | Tên cột | Kiểu dữ liệu | Mô tả nghiệp vụ |
| :---: | :--- | :---: | :--- |
| 1 | `editionId` | `STRING (FK)` | Mã ấn bản |
| 2 | `sectionKey` | `STRING (PK)` | Mã chuyên mục phân tích |
| 3 | `sectionTitle` | `STRING` | Tiêu đề đầy đủ của chuyên mục hiển thị |
| 4 | `editorialRating` | `STRING` | Đánh giá định hướng (STRATEGIC_FOCUS, ACTION_REQUIRED...) |
| 5 | `primaryThesis` | `STRING` | Luận điểm điều hành cốt lõi |
| 6 | `transmissionMechanism` | `STRING` | Cơ chế truyền dẫn tác động |
| 7 | `actionableRecommendations` | `JSON_ARRAY` | Khuyến nghị hành động chiến lược cho Bryan/Payoo |
| 8 | `riskFactors` | `JSON_ARRAY` | Yếu tố rủi ro và điểm nghẽn thị trường |
| 9 | `monitoringChecklist` | `JSON_ARRAY` | Danh mục chỉ số cần theo dõi trong 24–48h tới |
| 10 | `sectionWordCount` | `INTEGER` | Tổng độ dài số từ của nội dung biên tập |
| 11 | `lastEditedAt` | `DATETIME_ISO` | Thời điểm phê duyệt biên tập |

---

## 4. TAB 4: `MARKET_PULSE_HISTORY` — CHUỖI THỜI GIAN CHỈ SỐ THỊ TRƯỜNG
- **Khóa chính (PK):** Khóa kết hợp `(editionId, indicatorId)`
- **8 Chỉ số cố định:** `IND-01` VN-Index, `IND-02` Lãi suất O/N, `IND-03` USD/VND Trung tâm, `IND-04` Thanh khoản khớp lệnh, `IND-05` Lợi suất TPCP 10Y, `IND-06` Tỷ lệ mua/bán ròng FII, `IND-07` Tăng trưởng tín dụng YTD, `IND-08` Tỷ trọng QR/Napas.

| STT | Tên cột | Kiểu dữ liệu | Mô tả nghiệp vụ |
| :---: | :--- | :---: | :--- |
| 1 | `editionId` | `STRING (FK)` | Mã ấn bản quan sát |
| 2 | `indicatorId` | `STRING (PK)` | Mã chỉ số cố định |
| 3 | `indicatorName` | `STRING` | Tên chỉ số tài chính |
| 4 | `category` | `STRING` | Nhóm chỉ số (Vĩ mô, Thị trường vốn, Ngoại hối) |
| 5 | `tier` | `INTEGER` | Phân hạng chỉ số (1: Trọng yếu, 2: Bổ trợ) |
| 6 | `currentValue` | `STRING` | Giá trị ghi nhận tại phiên |
| 7 | `previousValue` | `STRING` | Giá trị phiên liền trước |
| 8 | `changeAbsolute` | `STRING` | Thay đổi giá trị tuyệt đối |
| 9 | `changePercent` | `STRING` | Thay đổi tỷ lệ phần trăm |
| 10 | `unit` | `STRING` | Đơn vị đo lường (Điểm, VND/USD, %/năm, Tỷ đồng) |
| 11 | `trendSignal` | `ENUM` | `UP` \| `DOWN` \| `STABLE` \| `VOLATILE` |
| 12 | `sourceAgency` | `STRING` | Đơn vị cung cấp số liệu thẩm quyền |
| 13 | `measurementDate` | `DATE` | Ngày đo lường số liệu (YYYY-MM-DD) |
| 14 | `verificationStatus` | `ENUM` | Trạng thái kiểm định nguồn số liệu (`VERIFIED`) |

---

## 5. TAB 5: `EVENT_REGISTRY` — KHO ĐĂNG KÝ SỰ KIỆN LỊCH SỬ CHỐNG TRÙNG
- **Khóa chính (PK):** `eventId`
- **Chỉ mục duy nhất (UK):** `canonicalUrl`
- **Mục tiêu:** Lưu trữ dấu vết nhận dạng của toàn bộ các sự kiện từ các ấn bản trước, phục vụ so sánh khử trùng lặp cho các ấn bản tương lai.
- **Các trường:** `eventId`, `canonicalUrl`, `normalizedHeadlineSignature`, `originalTitle`, `primaryEntity`, `eventDate`, `publicationDate`, `firstDiscoveredInEdition`, `duplicateCount`, `isFollowUp`, `followUpToEventId`, `lifecycleStatus`, `registeredAt`.

---

## 6. TAB 6: `SOURCE_LEDGER` — SỔ CÁI NGUỒN GỐC DỮ LIỆU
- **Khóa chính (PK):** Khóa kết hợp `(collectionRunId, sourceUrl)`
- **Mục tiêu:** Minh bạch toàn bộ 100% URL được cào về, thời gian kết nối, mã trạng thái HTTP, băm SHA-256 và lý do chấp nhận hoặc từ chối.
- **Các trường:** `collectionRunId`, `sourceUrl`, `sourceDomain`, `sourceChannel`, `originalTitle`, `retrievalTimestamp`, `httpStatus`, `rawContentSha256`, `evidenceSnapshotFile`, `verificationOutcome`, `gateAuditSummary`, `associatedEventId`.

---

## 7. TAB 7: `PUBLISH_AUDIT` — NHẬT KÝ PHÊ DUYỆT XUẤT BẢN & PHỤC HỒI
- **Khóa chính (PK):** `auditLogId`
- **Khóa ngoại (FK):** `editionId`
- **Mục tiêu:** Bằng chứng pháp lý về quyết định xuất bản, kiểm soát độ tươi, mã băm tệp JSON cục bộ và tham chiếu khôi phục (checkpoint rollback).
- **Các trường:** `auditLogId`, `editionId`, `action`, `performedBy`, `gateDecision`, `freshnessRatioRecorded`, `verifiedCountRecorded`, `localJsonChecksum`, `sheetsSyncStatus`, `rollbackReferenceCheckpoint`, `notes`, `timestamp`.
