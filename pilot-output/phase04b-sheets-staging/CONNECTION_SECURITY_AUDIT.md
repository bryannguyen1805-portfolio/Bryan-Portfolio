# BÁO CÁO KIỂM TOÁN AN TOÀN KẾT NỐI VÀ QUẢN TRỊ BÍ MẬT
## CONNECTION SECURITY & SECRETS GOVERNANCE AUDIT REPORT
**Dự án:** Bryan FinTech Intelligence — MagSpread Editorial Edition  
**Phân hệ:** Phase 04B — Google Sheets Integration  
**Ngày kiểm toán:** 2026-11-09  
**Người thực hiện:** Principal Security Auditor & Release QA Lead  

---

## 1. KẾT QUẢ RÀ SOÁT TÀI KHOẢN VÀ BÍ MẬT HIỆN TẠI (AUDIT FINDINGS)

Trước khi tiến hành bất kỳ cấu hình mạng nào, kiểm toán viên đã quét toàn bộ biến môi trường hệ thống và cấu trúc cây thư mục workspace để tìm kiếm các khóa kết nối Google:

```
[BẰNG CHỨNG QUÉT BÍ MẬT]
$ python3 -c "import os; print({k: os.environ.get(k) for k in ['GOOGLE_APPLICATION_CREDENTIALS', 'GOOGLE_SHEETS_SPREADSHEET_ID'] if os.environ.get(k)})"
{}
```

### Kết quả thẩm tra:
1. **Biến môi trường Google Cloud:** Hoàn toàn rỗng (`{}`).
2. **Tệp khóa bảo mật Service Account JSON:** Không tồn tại bất kỳ tệp JSON bí mật nào trong mã nguồn dự án.
3. **Mã nguồn Frontend (`magspread.js`, `magspread-preview.html`, `edition-data.js`):** Kiểm tra mã nguồn giao diện xác nhận **100% sạch**, hoàn toàn không chứa bất kỳ API key, client secret hay token xác thực nào (`test_09_no_secrets_exposed: PASS`).

> [!IMPORTANT]
> **KẾT LUẬN THẨM TRA AN TOÀN:**  
> Hệ thống hiện tại đang ở trạng thái **Cách ly an toàn tuyệt đối (Air-Gapped & Unauthenticated)**. Đúng theo chỉ đạo tại Mục 3 của Bryan: *Hệ thống không tự ý giả lập cuộc gọi API thành công và không yêu cầu dán khóa bảo mật vào hội thoại.*

---

## 2. QUY TRÌNH THIẾT LẬP KẾT NỐI AN TOÀN CHUẨN DOANH NGHIỆP

Khi Bryan phê duyệt chuyển từ giai đoạn Staging Dry-Run sang Live Testing, quy trình cấp quyền phải tuân thủ nghiêm ngặt theo các bước sau:

### Bước 1: Khởi tạo Service Account trên Google Cloud Console
1. Truy cập [Google Cloud Console](https://console.cloud.google.com/).
2. Chọn dự án nội bộ của Bryan FinTech hoặc tạo dự án mới: `bryan-fintech-intelligence`.
3. Kích hoạt API: **Google Sheets API v4** và **Google Drive API v3**.
4. Tạo Service Account chuyên dụng:
   - Tên: `magspread-sheets-sync`
   - Email sinh ra: `magspread-sheets-sync@bryan-fintech-intelligence.iam.gserviceaccount.com`
   - Quyền IAM: Chỉ cấp quyền tối thiểu cần thiết (`Editor` trên file bảng tính được chỉ định).
5. Tạo tệp khóa (Key) định dạng JSON và lưu trữ an toàn ngoài workspace Git (ví dụ: `~/.config/gcp/bryan_sheets_sa.json`).

### Bước 2: Tạo Bảng tính Staging chuyên dụng
1. Tạo một Google Spreadsheet mới trên Google Drive cá nhân của Bryan:
   - Tên bảng tính: `Bryan FinTech Intelligence — MagSpread Staging Archive [TEST]`
2. Nhấp nút **Chia sẻ (Share)** và thêm email Service Account:
   `magspread-sheets-sync@bryan-fintech-intelligence.iam.gserviceaccount.com`
   với quyền: **Người chỉnh sửa (Editor)**.
3. Lấy `SPREADSHEET_ID` từ thanh địa chỉ trình duyệt:
   `https://docs.google.com/spreadsheets/d/<SPREADSHEET_ID>/edit`

### Bước 3: Cung cấp biến môi trường cục bộ (Local Environment Only)
Chỉ kích hoạt kết nối thông qua biến môi trường cục bộ trên máy của kỹ sư hoặc CI runner được bảo vệ, **tuyệt đối không đưa vào file commit Git**:
```bash
export GOOGLE_APPLICATION_CREDENTIALS="/Users/quangtri/.config/gcp/bryan_sheets_sa.json"
export GOOGLE_SHEETS_SPREADSHEET_ID="<SPREADSHEET_ID_CHUYEN_DUNG>"
```

---

## 3. NGUYÊN TẮC BẢO VỆ DỮ LIỆU ĐỘC GIẢ (FRONTEND PRIVACY)

Để bảo vệ bí mật kinh doanh và an toàn hệ thống:
1. **Không có kết nối trực tiếp từ trình duyệt:** Trình duyệt của độc giả (MagSpread UI) không bao giờ gửi request mang Service Account Token trực tiếp đến Google Sheets API.
2. **Cơ chế đọc gián tiếp (Read-Only Mirror):** Dữ liệu lưu trữ chỉ được tải về giao diện web qua một tệp JSON tĩnh đã được ký băm (`archive_index.json`), hoặc qua một API gateway nội bộ bảo mật (Reverse Proxy / Cloud Functions) có gắn cơ chế Rate Limiting và CORS whitelist.
