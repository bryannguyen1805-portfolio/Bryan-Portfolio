# BÁO CÁO KIỂM ĐỊNH TOÀN VẸN SCHEMA 7 TAB GOOGLE SHEETS
## SEVEN-TAB GOOGLE SHEETS SCHEMA VALIDATION REPORT — V1.0
**Dự án:** Bryan FinTech Intelligence — MagSpread Editorial Edition  
**Phân hệ:** Phase 04B — Google Sheets Integration (Live Testing Protocol)  
**Ngày kiểm định:** 2026-11-09  
**Người kiểm định:** Principal Data Engineer & Release QA Lead  
**Tiêu chuẩn đối chiếu:** `pilot-output/phase04b-sheets-staging/GOOGLE_SHEETS_SCHEMA_V1.md` và `sheets_schema.py`  
**Kết quả tổng quan:** `7/7 TABS PASS (97/97 COLUMNS MATCH 100%)`

---

## 1. MA TRẬN ĐỐI SOÁT CẤU TRÚC 7 TAB

| STT | Tên Tab (Sheet Name) | Sheet ID | Số cột quy định | Số cột thực tế trên Sheet | Khóa chính (Primary Key) | Trạng thái |
| :---: | :--- | :---: | :---: | :---: | :--- | :---: |
| 1 | `EDITIONS` | 0 | 15 | 15 | `editionId` | **PASS** |
| 2 | `NEWS_EVENTS` | 801151325 | 20 | 20 | `(editionId, eventId)` | **PASS** |
| 3 | `EDITORIAL_SECTIONS` | 1950088800 | 11 | 11 | `(editionId, sectionKey)` | **PASS** |
| 4 | `MARKET_PULSE_HISTORY` | 356276852 | 14 | 14 | `(editionId, indicatorId)` | **PASS** |
| 5 | `EVENT_REGISTRY` | 724314388 | 13 | 13 | `eventId` | **PASS** |
| 6 | `SOURCE_LEDGER` | 1586177755 | 12 | 12 | `(collectionRunId, sourceUrl)` | **PASS** |
| 7 | `PUBLISH_AUDIT` | 290936658 | 12 | 12 | `auditLogId` | **PASS** |
| **TỔNG** | **7 TABS** | — | **97 CỘT** | **97 CỘT** | — | **100% MATCH** |

---

## 2. CHI TIẾT DANH MỤC CỘT TRÊN TỪNG TAB

### 2.1 Tab 1: `EDITIONS` (15 cột)
- **Danh sách cột đã ghi nhận và kiểm chứng:**
  `editionId`, `editionNumber`, `editionDate`, `displayDate`, `cutoffTime`, `publicationStatus`, `gateStatus`, `freshnessRatio`, `eligibleCount`, `count0To24h`, `count24To48h`, `count48To72h`, `leadStoryTitle`, `macroTheme`, `archivedAt`
- **Khóa chính:** `editionId` (Bắt buộc, không được để trống hoặc trùng).
- **Quy tắc:** Bất biến sau khi ấn bản đã được gắn nhãn `PUBLISHED`.

### 2.2 Tab 2: `NEWS_EVENTS` (20 cột)
- **Danh sách cột:**
  `editionId`, `eventId`, `stt`, `headline`, `category`, `tier`, `sourceName`, `canonicalUrl`, `originalSourcePublishedAt`, `timeDeltaFromCutoff`, `timeWindowBucket`, `verificationStatus`, `dedupStatus`, `isFollowUp`, `followUpTo`, `evidenceSha256`, `verifiedFactSummary`, `macroToMicro`, `fintechImpact`, `prediction`
- **Khóa chính kết hợp:** `(editionId, eventId)`
- **Khóa ngoại:** `editionId` tham chiếu tới `EDITIONS.editionId`
- **Kiểu dữ liệu:** URL chuẩn tắc, mã băm SHA-256 64 ký tự hex, JSON string cho `verifiedFactSummary`.

### 2.3 Tab 3: `EDITORIAL_SECTIONS` (11 cột)
- **Danh sách cột:**
  `editionId`, `sectionKey`, `sectionTitle`, `editorialRating`, `primaryThesis`, `transmissionMechanism`, `actionableRecommendations`, `riskFactors`, `monitoringChecklist`, `sectionWordCount`, `lastEditedAt`
- **Khóa chính kết hợp:** `(editionId, sectionKey)`
- **Chuyên mục hỗ trợ:** `sec02_coverStory`, `sec04b_decisionBrief`, `sec06_macroToMicro`, `sec07_paymentRadar`, `sec08b_watchlist`.

### 2.4 Tab 4: `MARKET_PULSE_HISTORY` (14 cột)
- **Danh sách cột:**
  `editionId`, `indicatorId`, `indicatorName`, `category`, `tier`, `currentValue`, `previousValue`, `changeAbsolute`, `changePercent`, `unit`, `trendSignal`, `sourceAgency`, `measurementDate`, `verificationStatus`
- **Khóa chính kết hợp:** `(editionId, indicatorId)`
- **Quy tắc định dạng:** Lưu trữ dạng văn bản thô (`RAW string`) để bảo toàn các tiền tố dấu cộng (ví dụ: `+10,00`, `+0.50%`) mà không bị phân giải thành công thức Excel gây lỗi `#ERROR!`.

### 2.5 Tab 5: `EVENT_REGISTRY` (13 cột)
- **Danh sách cột:**
  `eventId`, `canonicalUrl`, `normalizedHeadlineSignature`, `originalTitle`, `primaryEntity`, `eventDate`, `publicationDate`, `firstDiscoveredInEdition`, `duplicateCount`, `isFollowUp`, `followUpToEventId`, `lifecycleStatus`, `registeredAt`
- **Khóa chính:** `eventId`
- **Chỉ mục kiểm tra chống trùng:** `canonicalUrl` và `normalizedHeadlineSignature`.

### 2.6 Tab 6: `SOURCE_LEDGER` (12 cột)
- **Danh sách cột:**
  `collectionRunId`, `sourceUrl`, `sourceDomain`, `sourceChannel`, `originalTitle`, `retrievalTimestamp`, `httpStatus`, `rawContentSha256`, `evidenceSnapshotFile`, `verificationOutcome`, `gateAuditSummary`, `associatedEventId`
- **Khóa chính kết hợp:** `(collectionRunId, sourceUrl)`
- **Mục tiêu:** Minh bạch toàn bộ dấu vết cào dữ liệu thô phục vụ kiểm toán tài chính.

### 2.7 Tab 7: `PUBLISH_AUDIT` (12 cột)
- **Danh sách cột:**
  `auditLogId`, `editionId`, `action`, `performedBy`, `gateDecision`, `freshnessRatioRecorded`, `verifiedCountRecorded`, `localJsonChecksum`, `sheetsSyncStatus`, `rollbackReferenceCheckpoint`, `notes`, `timestamp`
- **Khóa chính:** `auditLogId`
- **Khóa ngoại:** `editionId` tham chiếu tới `EDITIONS.editionId`

---

## 3. KẾT LUẬN KIỂM ĐỊNH SCHEMA

1. Cả 7 tab đều đã tồn tại trên bảng tính STAGING với định danh và thứ tự hoàn toàn chính xác.
2. Dòng tiêu đề Header (Row 1) của cả 7 tab đã được chuẩn hóa và đối soát 100% khớp với tài liệu đặc tả `GOOGLE_SHEETS_SCHEMA_V1.md`.
3. Không phát hiện bất kỳ sự thiếu sót, sai lệch tên cột, sai thứ tự cột, hay xung đột kiểu dữ liệu nào.
