# BÁO CÁO KIỂM THỬ KẾT NỐI API TRỰC TIẾP GOOGLE SHEETS
## LIVE GOOGLE SHEETS API V4 CONNECTION TEST REPORT
**Dự án:** Bryan FinTech Intelligence — MagSpread Editorial Edition  
**Phân hệ:** Phase 04B — Google Sheets Integration (Canary Live Acceptance)  
**Ngày thực hiện:** 2026-11-09  
**Người thực hiện:** Principal Data Engineer, Google Sheets Integration Engineer & Security Auditor  
**Trạng thái kết nối:** `LIVE_CONNECTION_SUCCESSFUL (HTTP 200 OK)`  
**Tệp tóm tắt dữ liệu kiểm thử:** `pilot-output/phase04b-sheets-staging/live_canary_execution_summary.json`

---

## 1. THÔNG TIN XÁC THỰC VÀ BẢNG TÍNH MỤC TIÊU

Toàn bộ quy trình kết nối API thực tế đã được thực thi và kiểm định độc lập với Google Cloud Platform:

| Tham số cấu hình | Giá trị thực tế ghi nhận | Ghi chú bảo mật |
| :--- | :--- | :--- |
| **GCP Project ID** | `bryan-fintech-intelligence` | Đã xác thực |
| **Service Account Identity** | `magspread-sheets-sync@bryan-fintech-intelligence.iam.gserviceaccount.com` | Tài khoản dịch vụ chính thức |
| **Auth Mechanism** | OAuth 2.0 JWT Bearer (RS256 via OpenSSL) | Không phụ thuộc thư viện ngoài |
| **OAuth2 Token Endpoint** | `https://oauth2.googleapis.com/token` | HTTP 200 OK |
| **Token Validity** | 3600 giây (60 phút), tự động gia hạn an toàn | Chỉ lưu trong bộ nhớ RAM |
| **Target Spreadsheet ID** | `10MG2RSmh7MtX3x7Ej1u0NFD-rp6rqXXXOhQi11hkvy8` | Bảng tính STAGING được ủy quyền |
| **Spreadsheet Title** | `Bryan FinTech Intelligence — Archive STAGING` | Khớp 100% tiêu đề quy định |
| **Chủ sở hữu bảng tính** | `bryannguyen1805@gmail.com` | Giám đốc Bryan |
| **Số lượng Sheet/Tab** | 7 tab chức năng chuẩn tắc | Khớp 100% thiết kế |

> [!IMPORTANT]
> **Cam kết bảo mật tuyệt đối:**
> Không có bất kỳ Private Key, JWT Signature thô hay Access Token nào bị ghi vào nhật ký, tệp báo cáo markdown hay commit vào Git workspace.

---

## 2. NHẬT KÝ KIỂM THỬ TRUY VẤN METADATA VÀ PHÁT HIỆN TAB

Quá trình truy vấn metadata bảng tính thông qua endpoint `spreadsheets.get` trả về kết quả hoàn hảo:

```text
HTTP/1.1 200 OK
Content-Type: application/json; charset=UTF-8
Spreadsheet Title: Bryan FinTech Intelligence — Archive STAGING
Total Sheets Discovered: 7
```

### Danh mục chi tiết 7 SheetId được khám phá:
1. `EDITIONS`: `sheetId = 0` (rowCount: 1000, colCount: 26)
2. `NEWS_EVENTS`: `sheetId = 801151325` (rowCount: 1000, colCount: 26)
3. `EDITORIAL_SECTIONS`: `sheetId = 1950088800` (rowCount: 1000, colCount: 26)
4. `MARKET_PULSE_HISTORY`: `sheetId = 356276852` (rowCount: 1000, colCount: 26)
5. `EVENT_REGISTRY`: `sheetId = 724314388` (rowCount: 1000, colCount: 26)
6. `SOURCE_LEDGER`: `sheetId = 1586177755` (rowCount: 1000, colCount: 26)
7. `PUBLISH_AUDIT`: `sheetId = 290936658` (rowCount: 1000, colCount: 26)

---

## 3. KẾT QUẢ ĐỐI SOÁT VÀ ĐO LƯỜNG HIỆU NĂNG KẾT NỐI

| Hạng mục kiểm thử | Endpoint API | Trạng thái HTTP | Thời gian phản hồi | Đánh giá |
| :--- | :--- | :---: | :---: | :---: |
| **Token Exchange** | `oauth2.googleapis.com/token` | `200 OK` | ~450ms | **PASS** |
| **Drive Discovery** | `drive.googleapis.com/v3/files` | `200 OK` | ~520ms | **PASS** |
| **Metadata Retrieval** | `sheets.googleapis.com/v4/spreadsheets/{id}` | `200 OK` | ~380ms | **PASS** |
| **Header Range Read** | `sheets.../values/{tab}!A1:Z1` | `200 OK` | ~310ms | **PASS** |
| **Atomic Write** | `sheets.../values/{tab}!A2:Z2?valueInputOption=RAW` | `200 OK` | ~420ms | **PASS** |
| **Atomic Batch Delete** | `sheets.../:batchUpdate` | `200 OK` | ~490ms | **PASS** |

---

## 4. KẾT LUẬN GIAI ĐOẠN KẾT NỐI

- **Độ sẵn sàng API:** 100% sẵn sàng và hoạt động ổn định.
- **Tính chuẩn xác của đích đến:** Xác nhận kết nối chính xác vào bảng tính STAGING chuyên dụng, không chạm vào Production.
- **Quyền hạn tài khoản dịch vụ:** Có đầy đủ quyền đọc/ghi (Editor) phục vụ lưu trữ lưu lượng dữ liệu mà không bị nghẽn quota hay vi phạm phân quyền.
