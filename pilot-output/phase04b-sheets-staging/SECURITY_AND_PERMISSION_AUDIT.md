# BÁO CÁO KIỂM TOÁN AN TOÀN THÔNG TIN VÀ PHÂN QUYỀN API
## SECURITY AND PERMISSION AUDIT REPORT
**Dự án:** Bryan FinTech Intelligence — MagSpread Editorial Edition  
**Phân hệ:** Phase 04B — Google Sheets Integration (Canary Live Acceptance)  
**Ngày kiểm toán:** 2026-11-09  
**Người kiểm toán:** Principal Security Auditor & Release QA Lead  
**Đánh giá an toàn:** `100% COMPLIANT WITH ZERO PRIVILEGE ESCALATION / ZERO CREDENTIAL LEAKAGE`

---

## 1. KIỂM SOÁT VÀ BẢO VỆ MẬT MÃ (SECRET HYGIENE AUDIT)

| Tiêu chuẩn an ninh | Quy tắc áp dụng | Kết quả kiểm tra thực tế |
| :--- | :--- | :--- |
| **Lưu trữ Private Key** | Không lưu trữ trong mã nguồn dự án Git | Nằm tại thư mục riêng biệt của người dùng, không nằm trong cây Git |
| **Xác thực Token** | Tạo JWT tạm thời và ký qua OpenSSL hệ thống | Khóa tạm thời được hủy ngay lập tức sau khi ký |
| **Access Token Scope** | Chỉ cấp quyền tối thiểu cần thiết | Giới hạn trong `spreadsheets` và `drive.readonly` |
| **Không in log nhạy cảm** | Cấm in Private Key hoặc Bearer Token ra Terminal / Report | Toàn bộ log và báo cáo chỉ chứa định danh không nhạy cảm |
| **Git Working Tree Status** | Cấm commit tệp thông tin xác thực vào Git | Không có tệp `.json` chứa khóa nào được commit vào repository |

---

## 2. KIỂM ĐỊNH PHẠM VI BẢNG TÍNH ĐÍCH (ENVIRONMENT SEGREGATION)

Tiến trình đã thực hiện xác minh danh tính bảng tính đích 3 lớp độc lập trước khi gửi bất kỳ lệnh ghi nào:
1. **Lớp 1 — Kiểm tra Spreadsheet ID:** Khớp chính xác ID `10MG2RSmh7MtX3x7Ej1u0NFD-rp6rqXXXOhQi11hkvy8`.
2. **Lớp 2 — Kiểm tra Tiêu đề bảng tính:** Tiêu đề bắt buộc phải chứa chuỗi chuẩn tắc: `Bryan FinTech Intelligence — Archive STAGING`. Nếu tiêu đề là Production, tiến trình sẽ kích hoạt mã dừng khẩn cấp (Emergency Abort).
3. **Lớp 3 — Quyền hạn sở hữu:** Chủ sở hữu bảng tính được xác thực là `bryannguyen1805@gmail.com`.

---

## 3. KIỂM THỬ XỬ LÝ LỖI VÀ TÍNH PHỤC HỒI (FAILURE & ANOMALY HANDLING)

Hệ thống đã chủ động giả lập các tình huống lỗi mạng và truy cập bất hợp pháp để kiểm tra độ tin cậy của mã nguồn:

| Mã kịch bản | Tình huống thử nghiệm | Hành vi mong đợi | Mã HTTP thực tế | Kết quả đánh giá |
| :---: | :--- | :--- | :---: | :---: |
| **ERR-01** | Truy vấn tab không tồn tại (`NON_EXISTENT_TAB!A1:Z10`) | Google Sheets API trả về lỗi 400, client bắt lỗi và không gây sập chương trình | `HTTP 400 Bad Request` | **PASS** |
| **ERR-02** | Sử dụng OAuth2 Token giả mạo hoặc hết hạn | Google API từ chối truy cập ngay lập tức, không để lộ dữ liệu | `HTTP 401 Unauthorized` | **PASS** |
| **ERR-03** | Cú pháp dải ô không hợp lệ (`EDITIONS!A-INVALID:Z`) | API trả về lỗi cú pháp, dữ liệu trong bảng tính không bị ảnh hưởng | `HTTP 400 Bad Request` | **PASS** |

> [!NOTE]
> Mọi lỗi thử nghiệm đều được ghi nhận vào nhật ký mà không có bất kỳ thông tin nhạy cảm nào bị phơi bày.

---

## 4. BẢO TỒN NỀN TẢNG BẤT KHẢ XÂM PHẠM (FROZEN BASELINES INTEGRITY)

Kiểm tra đối chiếu mã băm SHA-256 của các tệp giao diện V2.2.3 và dữ liệu ấn bản đã nghiệm thu:

| Tệp nền tảng (Protected File) | Mã băm SHA-256 chuẩn tắc | Mã băm sau khi chạy Canary | Trạng thái toàn vẹn |
| :--- | :--- | :--- | :---: |
| `magspread-preview.html` | `a7679251c49d4f30485a90e36191eeaf6185313625e264878273b1e79a6577d4` | `a7679251c49d4f30485a90e36191eeaf6185313625e264878273b1e79a6577d4` | **100% MATCH** |
| `magspread.css` | `82d7c64209e3b726d7e0c7cf4e29524ad336c03b151369ff360aba82b6ce49ba` | `82d7c64209e3b726d7e0c7cf4e29524ad336c03b151369ff360aba82b6ce49ba` | **100% MATCH** |
| `magspread.js` | `860a21903aa03ab31ec597d8cff8fcdb028b63b1d8ca10adffb90318dbf2ce6c` | `860a21903aa03ab31ec597d8cff8fcdb028b63b1d8ca10adffb90318dbf2ce6c` | **100% MATCH** |
| `edition-data.json` | `c95a591a4b695e51f980737d0f5c3a85e498023292c1c62e63daed0bf3dbe67a` | `c95a591a4b695e51f980737d0f5c3a85e498023292c1c62e63daed0bf3dbe67a` | **100% MATCH** |
| `edition-data.js` | `9d819ad6323ac42e13eabb16c5b5150cf306192739524bd6317d1efbf8f9a694` | `9d819ad6323ac42e13eabb16c5b5150cf306192739524bd6317d1efbf8f9a694` | **100% MATCH** |

Các Checkpoint đã nghiệm thu (`Checkpoint 01`, `Checkpoint 02`, `Checkpoint 03`, và bản Cold Backup ngoài workspace) hoàn toàn bất biến, không bị tác động.

---

## 5. KẾT LUẬN

Hạ tầng tích hợp Google Sheets API v4 đáp ứng đầy đủ các tiêu chuẩn bảo mật doanh nghiệp khắt khe nhất. Quá trình kiểm thử thực tế không gây rò rỉ thông tin, không làm thay đổi baseline và không gây rủi ro cho bất kỳ phân hệ nào.
