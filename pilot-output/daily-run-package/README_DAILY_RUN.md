# 🚀 BRYAN FINTECH MARKET INTELLIGENCE — HƯỚNG DẪN VẬN HÀNH HÀNG NGÀY (DAILY SOP)

Thư mục này (`pilot-output/daily-run-package/`) là gói thực thi độc lập chuẩn hóa dành riêng cho việc **nghiên cứu, phân tích và xuất bản ấn bản tài chính số hàng ngày (Daily Financial Intelligence Edition)** của Bryan FinTech Market Intelligence.

---

## 📁 CẤU TRÚC GÓI VẬN HÀNH (`daily-run-package`)

```
pilot-output/daily-run-package/
├── run_daily_edition.py               # Lệnh điều phối chính thực thi 1 chạm mỗi ngày
├── update_magspread_pilot_ui.py       # Bộ máy phân tích tài chính động & xuất bản dữ liệu
├── index.html                         # Giao diện chính E-Magazine Portal
├── magspread-preview.html             # Bản sao dự phòng giao diện
├── magspread.js                       # Frontend JavaScript (xử lý Drawer, tương tác, tabs)
├── magspread.css                      # Hệ thống thiết kế chuẩn tạp chí tài chính (Typography, Spacing)
├── edition-data.json                  # CSDL chuẩn của ấn bản ngày hiện tại
├── edition-data.js                    # CSDL nhúng cho trình duyệt offline (file://)
├── zalo-icon.svg                      # Asset liên kết mạng xã hội
└── README_DAILY_RUN.md                # Tài liệu hướng dẫn này
```

---

## ⚡ HƯỚNG DẪN VẬN HÀNH 1 LỆNH DUY NHẤT (ONE-COMMAND EXECUTION)

Mỗi ngày, sau khi kết thúc phiên giao dịch (khoảng **17:30 - 18:00**), mở Terminal và chạy lệnh sau:

```bash
cd /Users/quangtri/Documents/Bryan-Portfolio-Antigravity/pilot-output/daily-run-package
python3 run_daily_edition.py
```

### Quy trình tự động diễn ra sau khi gõ lệnh:
1. **Thu thập & Kiểm định tin tức**: Quét 25 bản tin xác minh từ các báo lớn (VnEconomy, Báo Đầu Tư, Tuổi Trẻ, Thanh Niên, CafeF, Vietstock), bắt buộc tối thiểu **80% tin tức (>= 20 bài)** thuộc khung thời gian 0–24h.
2. **Cập nhật 4 chỉ số Market Pulse trọng tâm (100% nguồn báo chí xác thực)**:
   - **MP-01 (Tỷ giá trung tâm USD/VND)**: Công bố bởi NHNN, xác minh qua Báo VOV / Thời báo Ngân hàng kèm biên độ ±5%.
   - **MP-02 (Lãi suất tiền gửi 12T cao nhất)**: Khảo sát thực tế biểu lãi suất hệ thống NHTM qua CafeF / Báo Tổ quốc.
   - **MP-03 (Chỉ số VN-Index)**: Điểm số chốt phiên sàn HoSE, thanh khoản và cổ phiếu vốn hóa lớn dẫn dắt qua Báo Đầu Tư.
   - **MP-04 (Khách du lịch quốc tế đến Việt Nam)**: Số liệu lũy kế từ Cục Du lịch Quốc gia & Tổng cục Thống kê qua Báo Nhân Dân.
   - Nút `Mở link bài báo gốc ↗` dẫn thẳng tới bài báo cụ thể (100% bài viết sống, không 404); phân tách hoàn toàn giữa *Ý nghĩa điều hành (Field 08-09)* và *Diễn giải tài chính thực tế & FinTech Impact (Field 10)*.
3. **Quy tắc xác định Bài đinh trang nhất (Cover Story)**:
   - Tự động chấm điểm và chọn ra tin tức có tầm ảnh hưởng vĩ mô/ngân sách lớn nhất trong 25 tin (Top Lead News).
   - Tóm tắt chi tiết bài đinh, trích dẫn bài báo gốc và mã sự kiện `[EVT-XX]`.
   - **■ Đúc kết biên tập**: AI tự động tổng hợp bức tranh kinh tế chung từ toàn bộ 25 tin tức trong ngày.
   - **Tác động thị trường & FinTech Lens**: Phân tích cơ hội cụ thể cho giải pháp Payoo SmartPOS All-in-One, Trả góp 0%, VietQR Global và Hóa đơn điện tử máy tính tiền.
4. **4 Chuỗi truyền dẫn Vĩ mô $\rightarrow$ Vi mô độc lập**:
   - Tự động xâu chuỗi 5 tầng logic: *Vĩ mô $\rightarrow$ Điều hành NHNN $\rightarrow$ NHTM & Vốn $\rightarrow$ Doanh nghiệp & Bán lẻ $\rightarrow$ Điểm chạm SmartPOS/QR*.
5. **3 Tín hiệu hành động (Executive Decision Brief)**:
   - Nút `ĐỌC PHÂN TÍCH →` mở Drawer chi tiết với 8 mục phân tích chiến lược (A đến H).
6. **Đồng bộ hóa tức thì**: Ghi đè vào `edition-data.json`, `edition-data.js` và cập nhật trực tiếp lên `index.html`.

---

## 🕒 THIẾT LẬP TỰ ĐỘNG CHẠY HÀNG NGÀY BẰNG CRONTAB (TÙY CHỌN)

Nếu muốn máy Mac tự động chạy vào **18:00 từ Thứ Hai đến Thứ Sáu** hàng tuần:

1. Mở Terminal và gõ:
   ```bash
   crontab -e
   ```
2. Thêm dòng sau vào cuối file:
   ```cron
   0 18 * * 1-5 cd /Users/quangtri/Documents/Bryan-Portfolio-Antigravity/pilot-output/daily-run-package && /usr/bin/python3 run_daily_edition.py >> daily_run.log 2>&1
   ```
3. Lưu lại (`:wq` trong vim). Hệ thống sẽ tự động xuất bản mỗi ngày mà không cần can thiệp thủ công.

---

## 🔍 KIỂM TRA & XEM GIAO DIỆN

Sau khi chạy xong, mở file sau bằng bất kỳ trình duyệt nào (Chrome, Safari, Edge):
```
file:///Users/quangtri/Documents/Bryan-Portfolio-Antigravity/pilot-output/daily-run-package/index.html
```
Hoặc mở từ thư mục root:
```
file:///Users/quangtri/Documents/Bryan-Portfolio-Antigravity/pilot-output/magspread-preview.html
```

---
*Tài liệu chuẩn hóa bởi: Bryan FinTech Intelligence System Engine*
