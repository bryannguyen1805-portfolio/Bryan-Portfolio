# BÁO CÁO KIỂM THỬ TÍNH LŨY THỪA VÀ DỌN DẸP DỮ LIỆU CANARY
## IDEMPOTENCY AND SAFE CLEANUP REPORT
**Dự án:** Bryan FinTech Intelligence — MagSpread Editorial Edition  
**Phân hệ:** Phase 04B — Google Sheets Integration (Canary Live Acceptance)  
**Ngày thực hiện:** 2026-11-09  
**Người thực hiện:** Principal Data Engineer & Release QA Lead  
**Mục tiêu:** Chứng minh hệ thống không bị nhân bản dữ liệu khi chạy lại và có khả năng làm sạch 100% dữ liệu thử nghiệm  
**Kết quả kiểm thử:** `IDEMPOTENCY PASS & CLEANUP VERIFIED (ZERO RESIDUAL ARTIFACTS)`

---

## 1. KIỂM THỬ TÍNH LŨY THỪA (IDEMPOTENCY & DUPLICATE PREVENTION)

### Kịch bản thử nghiệm:
1. Hệ thống đã có 1 dòng tiêu đề (Row 1) và 1 dòng dữ liệu Canary (Row 2) trên cả 7 tab (tổng số dòng hiện hữu = 2).
2. Tiến trình gửi lại chính xác cùng một lệnh ghi với cùng các khóa chính (`CANARY_PHASE04B_...`).
3. Động cơ đồng bộ (`sheets_sync_engine`) phát hiện khóa chính đã tồn tại trong bảng tính và chuyển hướng sang chế độ cập nhật tại chỗ (In-place Overwrite / Upsert) thay vì chèn dòng mới (Append).
4. Đếm lại số dòng trên toàn bộ 7 tab để kiểm tra xem có bất kỳ dòng trùng nào bị phát sinh hay không.

### Kết quả kiểm định tính lũy thừa trên 7 tab:

| Tab | Khóa chính kiểm tra | Số dòng ban đầu | Số dòng sau ghi lặp lại | Phát sinh trùng lặp? | Đánh giá |
| :--- | :--- | :---: | :---: | :---: | :---: |
| `EDITIONS` | `CANARY_PHASE04B_ED_01` | 2 | 2 | **KHÔNG (0)** | **PASS** |
| `NEWS_EVENTS` | `(CANARY_PHASE04B_ED_01, CANARY_PHASE04B_EVT_01)` | 2 | 2 | **KHÔNG (0)** | **PASS** |
| `EDITORIAL_SECTIONS` | `(CANARY_PHASE04B_ED_01, sec02_coverStory)` | 2 | 2 | **KHÔNG (0)** | **PASS** |
| `MARKET_PULSE_HISTORY` | `(CANARY_PHASE04B_ED_01, CANARY_IND_01)` | 2 | 2 | **KHÔNG (0)** | **PASS** |
| `EVENT_REGISTRY` | `CANARY_PHASE04B_EVT_01` | 2 | 2 | **KHÔNG (0)** | **PASS** |
| `SOURCE_LEDGER` | `(CANARY_PHASE04B_RUN_..., https://bryan...)` | 2 | 2 | **KHÔNG (0)** | **PASS** |
| `PUBLISH_AUDIT` | `AUDIT-CANARY-...` | 2 | 2 | **KHÔNG (0)** | **PASS** |

> [!NOTE]
> Kết quả: Toàn bộ 7 tab giữ nguyên đúng 2 dòng. Không có bất kỳ bản ghi thừa nào bị chèn vào bảng tính khi thực thi lặp lại.

---

## 2. QUY TRÌNH DỌN DẸP BẢN GHI THỬ NGHIỆM (STAGE 7: CONTROLLED CLEANUP)

### Phương thức dọn dẹp:
Để đảm bảo tính nguyên tử (Atomicity), hệ thống không xóa thủ công từng ô tính mà gửi một lệnh gộp `spreadsheets.batchUpdate` chứa 7 yêu cầu `deleteDimension` đồng thời:
```json
{
  "requests": [
    {
      "deleteDimension": {
        "range": {
          "sheetId": "<sheetId>",
          "dimension": "ROWS",
          "startIndex": 1,
          "endIndex": 2
        }
      }
    }
    // ... lặp lại cho 7 tab
  ]
}
```

Mã phản hồi từ Google API: `HTTP 200 OK`. Dòng dữ liệu số 2 (Row index 1) trên toàn bộ 7 tab đã bị xóa hoàn toàn khỏi cloud.

---

## 3. KIỂM ĐỊNH TRẠNG THÁI NGUYÊN SƠ SAU KHI DỌN DẸP (READ-BACK AUDIT)

Sau khi gọi lệnh xóa, hệ thống tiến hành đọc lại dải ô `A1:Z10` của cả 7 tab để kiểm tra trạng thái bảng tính:

| Tab | Số dòng còn lại | Nội dung dòng còn lại | Tình trạng dòng tiêu đề Header | Đánh giá |
| :--- | :---: | :--- | :---: | :---: |
| `EDITIONS` | **1** | Dòng tiêu đề 15 cột Schema V1.0 | Nguyên vẹn 100% | **PRISTINE** |
| `NEWS_EVENTS` | **1** | Dòng tiêu đề 20 cột Schema V1.0 | Nguyên vẹn 100% | **PRISTINE** |
| `EDITORIAL_SECTIONS` | **1** | Dòng tiêu đề 11 cột Schema V1.0 | Nguyên vẹn 100% | **PRISTINE** |
| `MARKET_PULSE_HISTORY` | **1** | Dòng tiêu đề 14 cột Schema V1.0 | Nguyên vẹn 100% | **PRISTINE** |
| `EVENT_REGISTRY` | **1** | Dòng tiêu đề 13 cột Schema V1.0 | Nguyên vẹn 100% | **PRISTINE** |
| `SOURCE_LEDGER` | **1** | Dòng tiêu đề 12 cột Schema V1.0 | Nguyên vẹn 100% | **PRISTINE** |
| `PUBLISH_AUDIT` | **1** | Dòng tiêu đề 12 cột Schema V1.0 | Nguyên vẹn 100% | **PRISTINE** |

---

## 4. KẾT LUẬN

1. Tính lũy thừa đạt chuẩn tuyệt đối: Không phát sinh bản ghi trùng lặp khi chạy lại pipeline.
2. Quy trình dọn dẹp hoạt động hoàn hảo: Bản ghi thử nghiệm Canary đã được dọn sạch 100%, bảo toàn nguyên vẹn cấu trúc dòng tiêu đề chuẩn hóa cho toàn bộ 7 tab.
3. Không để lại bất kỳ rác dữ liệu thử nghiệm nào trên bảng tính STAGING.
