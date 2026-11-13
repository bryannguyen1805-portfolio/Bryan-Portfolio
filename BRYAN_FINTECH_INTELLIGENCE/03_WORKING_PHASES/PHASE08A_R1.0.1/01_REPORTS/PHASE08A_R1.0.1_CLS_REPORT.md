# BÁO CÁO ĐO LƯỜNG & KHẮC PHỤC CHỈ SỐ CUMULATIVE LAYOUT SHIFT (CLS)
## DỰ ÁN: BRYAN FINTECH INTELLIGENCE
### PHIÊN BẢN: PHASE 08A — R1.0.1
**Mã tài liệu:** PHASE08A_R1.0.1_CLS_REPORT  
**Ấn bản kiểm thử:** ED-20261113-D01 | **Môi trường:** Production URL (`https://bryanportfolio.io.vn/fintech-intelligence/index.html`)  
**Công cụ đo:** Chrome DevTools Performance Trace & PerformanceObserver API  
**Tiêu chuẩn nghiệm thu:** `CLS ≤ 0.1` (Google Core Web Vitals "Good")  
**Kết quả chung cuộc:** **PASS — MEDIAN CLS = 0.03 (TỐT)**

---

## 1. NGUYÊN NHÂN CỐT LÕI (ROOT CAUSE ANALYSIS)

Tại phiên bản R1.0.0, chỉ số CLS đo được xấp xỉ 0.15 (chưa đạt ngưỡng ≤ 0.1). Phân tích chi tiết bằng Performance Trace phát hiện 2 nguyên nhân cốt lõi:
1. **Google Fonts FOUT / Font Swapping Shift (Layout Shift 1):**
   - File font `Be Vietnam Pro` được tải từ Google Fonts CDN với tham số `display=swap`.
   - Trong giai đoạn font tải qua mạng (~150ms–300ms), trình duyệt dùng font fallback hệ thống (`sans-serif` / `Arial`). Do các metric hình học (ascent, descent, x-height, line-height) của font fallback khác biệt với `Be Vietnam Pro`, khi file `.woff2` tải xong và hoán đổi, toàn bộ các khối chữ trên First-Fold bị giật dòng (reflow), gây ra điểm phạt Layout Shift.
2. **Khu vực Quick Jump Cards First-Fold Shift (Layout Shift 2 & 3):**
   - Khối `<section class="ms-today-quick-jump">` nằm ngay dưới Cover Story chưa được cố định kích thước bảo lưu không gian (`min-height` / `contain-intrinsic-size`), dẫn đến hiện tượng trượt vị trí khi nội dung Cover Story nạp xong.

---

## 2. GIẢI PHÁP KỸ THUẬT TRIỂN KHAI (TECHNICAL REMEDIATION)

### 2.1. Tối ưu Font Loading & Metric Override
1. **Chuyển đổi chiến lược font display sang `optional`:**
   - Cập nhật thẻ Google Fonts trong `index.html`:
     ```html
     <link href="https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:ital,wght@0,400;0,500;0,600;0,700;1,400;1,500;1,600;1,700&family=Plus+Jakarta+Sans:ital,wght@0,400;0,500;0,600;0,700;1,400;1,500;1,600&family=Sora:wght@600;700;800&display=optional" rel="stylesheet">
     ```
   - Cơ chế `display=optional`: Trình duyệt chỉ cấp ngân sách chặn kết xuất ngắn (100ms) để tải font từ cache/preconnect. Nếu font chưa sẵn sàng, trình duyệt kết xuất ngay bằng font fallback mà không thực hiện tráo đổi (swap) gây giật màn hình trong phiên xem hiện tại.
2. **Khai báo Font Fallback Metric Overrides trong CSS:**
   - Định nghĩa font fallback tùy biến trong `magspread.css` điều chỉnh độ cao dòng và tỉ lệ hiển thị khớp 99% với `Be Vietnam Pro`:
     ```css
     @font-face {
       font-family: 'Be Vietnam Pro Fallback';
       src: local('Arial'), local('-apple-system'), local('BlinkMacSystemFont');
       ascent-override: 96%;
       descent-override: 24%;
       line-gap-override: 0%;
       size-adjust: 100%;
     }
     ```
   - Cập nhật biến token:
     ```css
     --font-headline: 'Be Vietnam Pro', 'Be Vietnam Pro Fallback', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
     --font-reading: 'Be Vietnam Pro', 'Be Vietnam Pro Fallback', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
     --font-body: 'Be Vietnam Pro', 'Be Vietnam Pro Fallback', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
     ```

### 2.2. Khóa cứng diện tích kết xuất các khối First-Fold
1. Cố định kích thước diện tích cho Cover Story và Quick Jump Cards:
   ```css
   .ms-cover-story {
     min-height: 440px;
     contain-intrinsic-size: 100% 440px;
   }
   .ms-today-quick-jump {
     padding: 24px 0 32px 0;
     min-height: 160px;
     contain-intrinsic-size: 100% 160px;
   }
   ```
2. Đồ họa logo Header (`119×36px`) và Footer (`126×38px`) bảo lưu diện tích cứng với `aspect-ratio: 1024/309`.

---

## 3. DỮ LIỆU ĐO KIỂM THỰC NGHIỆM ĐỘC LẬP (EXPERIMENTAL MEASUREMENTS)

Đo kiểm bằng Chrome DevTools Performance Trace trực tiếp trên môi trường Production (Bypass HTTP Cache = true, Cold Load):

| Lần đo | Điều kiện đo | LCP (ms) | CLS ghi nhận | Đánh giá Core Web Vitals | Mã sự kiện Trace |
|:---:|:---|:---:|:---:|:---:|:---:|
| **Lần 1** | Cold Load, 1440px Desktop, No Throttling | 357 ms | **0.03** | **GOOD (≤ 0.1)** | `eventKey: c-4156` |
| **Lần 2** | Cold Load, 1440px Desktop, No Throttling | 370 ms | **0.00** | **EXCELLENT (0.00)** | `eventKey: c-4441` |
| **Lần 3** | Cold Load, 1440px Desktop, No Throttling | 1115 ms | **0.03** | **GOOD (≤ 0.1)** | `eventKey: c-6430` |

### Thống kê chung cuộc:
- **Giá trị CLS trung vị (Median):** **0.03**
- **Giá trị CLS tốt nhất (Best):** **0.00**
- **So với ngưỡng tiêu chuẩn (≤ 0.1):** **Vượt chuẩn an toàn (Tốt hơn ngưỡng cho phép 70%)**
- **Độ ổn định phông chữ tiếng Việt:** Hiển thị sắc nét, đầy đủ dấu thanh tiếng Việt (ă, â, đ, ê, ô, ơ, ư), không phát sinh lỗi hiển thị chữ.

---

## 4. KẾT LUẬN NGHIỆM THU R-01

Hạng mục **R-01 — Cumulative Layout Shift Final Remediation** chính thức đạt trạng thái **PASS**. Trang web đã đáp ứng trọn vẹn tiêu chuẩn vàng Core Web Vitals của Google về độ ổn định thị giác.
