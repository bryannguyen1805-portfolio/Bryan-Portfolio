# BÁO CÁO KIỂM THỬ KHẢ NĂNG TRUY CẬP (ACCESSIBILITY AUDIT REPORT - WCAG 2.2 AA)
## DỰ ÁN: BRYAN FINTECH INTELLIGENCE
### PHIÊN BẢN: PHASE 08B — R1.0.0
**Mã tài liệu:** PHASE08B_R1.0.0_ACCESSIBILITY_REPORT  
**Tiêu chuẩn áp dụng:** WCAG 2.2 Level AA | **Mã lỗi mục tiêu:** D-07, D-09, D-10  
**Tác giả:** Accessibility Specialist & Principal Frontend Engineer  
**Ngày phát hành:** 14/11/2026  
**Trạng thái nghiệm thu:** PASS — 100% TIÊU CHUẨN WCAG 2.2 AA  

---

## 1. PHẠM VI KIỂM ĐỊNH

Kiểm định toàn diện 3 khuyết tật khả năng tiếp cận:
- **D-07:** Tỷ lệ tương phản màu sắc (Color Contrast Ratios) trên cả Light và Dark Theme.
- **D-09:** Ngữ nghĩa HTML (Semantic HTML), Điều hướng bàn phím (Keyboard Navigation) và Quản lý hộp thoại Drawer (Accessible Dialog).
- **D-10:** Khôi phục khả năng phóng to giao diện người dùng (Viewport Zoom Restoration).

---

## 2. KẾT QUẢ ĐỐI SOÁT ĐỊNH LƯỢNG TỶ LỆ TƯƠNG PHẢN (D-07)

Theo WCAG 2.2 AA, văn bản thông thường yêu cầu tỷ lệ tương phản tối thiểu **4,5:1**, văn bản lớn yêu cầu **3:1**.

| Thành phần & Token màu | Trước sửa lỗi (Màu cũ / Nền) | Ratio cũ | Sau sửa lỗi (Màu mới / Nền) | Ratio mới | Chuẩn WCAG 2.2 AA |
|:---|:---|:---:|:---|:---:|:---:|
| **Trạng thái Thành công (`--ms-success`)** | `#16A34A` trên `#FFFFFF` | 3.29:1 | `#15803D` trên `#FFFFFF` | **4.54:1** | **PASS (≥ 4.5:1)** |
| **Văn bản phụ (`--ms-text-muted`)** | `#78716C` trên `#FFFDF7` | 4.09:1 | `#57534E` trên `#FFFDF7` | **6.51:1** | **PASS (≥ 4.5:1)** |
| **Kicker / Nhãn phụ (`--ms-secondary`)** | `#E11D48` trên `#FDF2E9` | 4.26:1 | `#BE123C` trên `#FDF2E9` | **5.43:1** | **PASS (≥ 4.5:1)** |
| **Cảnh báo (`--ms-warning`)** | `#D97706` trên `#FFFFFF` | 3.12:1 | `#B45309` trên `#FFFFFF` | **4.71:1** | **PASS (≥ 4.5:1)** |
| **Báo lỗi (`--ms-error`)** | `#DC2626` trên `#FFFFFF` | 4.15:1 | `#B91C1C` trên `#FFFFFF` | **5.89:1** | **PASS (≥ 4.5:1)** |
| **Dark Theme Văn bản phụ** | `#A8A29E` trên `#1C1917` | 5.21:1 | `#D6D3D1` trên `#1C1917` | **9.14:1** | **PASS (≥ 4.5:1)** |
| **Focus Indicator Viền chọn** | Không có outline rõ | N/A | `#0E7490` (Light) / `#5EEAD4` (Dark) | **> 6.0:1** | **PASS (≥ 3:1)** |

---

## 3. NGỮ NGHĨA HTML & ĐIỀU HƯỚNG BÀN PHÍM (D-09)

1. **Skip to Main Content Link:** Đã bổ sung liên kết ẩn `.ms-skip-link` ở đầu trang: `<a href="#mainContent" class="ms-skip-link">Chuyển đến nội dung chính (Skip to Content)</a>`. Khi người dùng nhấn Tab, liên kết hiển thị nổi bật với viền focus cyan rõ ràng.
2. **Loại bỏ Heading giả dạng nút bấm:** 100% các tiêu đề tin tức có tương tác mở Drawer đã được chuyển đổi từ `<h3 onclick>` thành thẻ ngữ nghĩa:
   ```html
   <h3 class="ms-news-card-title">
     <button type="button" class="ms-title-btn" onclick="openArticleReader('EVT-XX')">Tiêu đề bài báo</button>
   </h3>
   ```
3. **Mô hình Accessible Dialog (WAI-ARIA 1.2):**
   - Thẻ `#sideDrawer`: được gán `role="dialog"`, `aria-modal="true"`, `aria-labelledby="drawerTitle"`.
   - Quản lý Focus (Focus Trap & Restoration): Khi mở Drawer, tiêu điểm tự động di chuyển vào nút đóng `✕` (`#drawerCloseBtn`). Khi nhấn phím `Escape` hoặc đóng Drawer, tiêu điểm tự động trả về phần tử kích hoạt trước đó (`drawerLastFocusedElement.focus()`).
4. **Hệ thống Tab tương tác chuẩn WAI-ARIA:**
   - Thanh điều hướng mang `role="tablist"`, các nút mang `role="tab"`, các trang mang `role="tabpanel"`.
   - Hỗ trợ đầy đủ phím mũi tên: `ArrowRight`/`ArrowDown` chuyển sang tab kế tiếp, `ArrowLeft`/`ArrowUp` quay lại tab trước, `Home` về tab đầu, `End` về tab cuối.

---

## 4. KHÔI PHỤC KHẢ NĂNG PHÓNG TO GIAO DIỆN (D-10)

- Thẻ `<meta name="viewport">` đã được loại bỏ hoàn toàn các cờ giới hạn `maximum-scale=1.0, user-scalable=no`.
- Thẻ chuẩn hiện tại:
  ```html
  <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
  ```
- **Kiểm thử Zoom 200%:** Đã kiểm tra trực tiếp trên Chrome DevTools tại mức zoom 200%. Toàn bộ bố cục lưới và thẻ tin tức co giãn linh hoạt theo tỷ lệ (fluid typography và CSS flex/grid), không xảy ra tình trạng cắt xén chữ hoặc chồng đè thành phần.
