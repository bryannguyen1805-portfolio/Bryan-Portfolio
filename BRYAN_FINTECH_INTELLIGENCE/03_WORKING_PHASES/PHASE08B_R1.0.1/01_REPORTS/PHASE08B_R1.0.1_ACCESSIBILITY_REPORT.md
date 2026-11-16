# BÁO CÁO KIỂM ĐỊNH KHẢ NĂNG TRUY CẬP (ACCESSIBILITY AUDIT — WCAG 2.2 AA)
## DỰ ÁN: BRYAN FINTECH INTELLIGENCE / BNEWS
### PHIÊN BẢN: PHASE 08B — R1.0.1 (`ED-20261114-D01` | `ẤN BẢN SỐ 29`)

**Mã tài liệu:** `PHASE08B_R1.0.1_ACCESSIBILITY_REPORT`  
**Tiêu chuẩn tham chiếu:** WCAG 2.2 Level AA & WAI-ARIA Authoring Practices Guide (Dialog Modal / Tabs)  
**Công cụ kiểm chứng:** Google Chrome Headless CDP Computed DOM Inspector (`verify_r101_browser.mjs`)  
**Ngày kiểm tra:** `14/11/2026`

---

## 1. ĐỘ TƯƠNG PHẢN MÀU SẮC TỰ ĐỘNG TRÊN DOM THỰC TẾ (D-07)

Bộ quét tương phản tính toán màu nền hiệu dụng nhiều lớp (`getEffBg` tổng hợp alpha gradient & background parent) cho toàn bộ các phần tử văn bản hiển thị qua cả 4 tab (`today`, `market`, `analysis`, `b2b`) sau khi chuyển theme ổn định (`650ms`):

| Chế độ hiển thị | Số phần tử văn bản kiểm tra | Tỷ lệ tương phản thấp nhất (`minRatio`) | Ngưỡng WCAG 2.2 AA (Thường / Lớn) | Số lỗi (`failCount`) | Trạng thái |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Light Mode (`data-theme="light"`)** | `795` phần tử | **5.02 : 1** | `>= 4.50 : 1` / `>= 3.00 : 1` | **`0`** | **PASS** |
| **Dark Mode (`data-theme="dark"`)** | `795` phần tử | **4.83 : 1** | `>= 4.50 : 1` / `>= 3.00 : 1` | **`0`** | **PASS** |

### Các điều chỉnh kỹ thuật D-07 đã áp dụng
- Dark Mode định nghĩa `--ms-text-on-primary: #061513`, `--ms-text-on-secondary: #120609`, `--ms-success: #4ADE80`, `--ms-warning: #FBBF24`, `--ms-error: #F87171` trên `:root[data-theme="dark"]` (`magspread.css`).
- Nút nền gradient vàng-nâu `.fab-toggle-btn` và `.btn-top` sử dụng màu chữ `#1C1917` thay cho chữ trắng.
- Phân tách tiêu đề `.ms-masthead-sep` dùng `var(--ms-text-muted)` kèm `aria-hidden="true"`.
- Loại bỏ hoàn toàn màu chữ cứng tương phản kém `#d97706` và `#0e7490` trong `magspread.js` (`openPulseDetail`), chuyển sang token CSS theo theme.

---

## 2. QUẢN LÝ FOCUS, NGỮ NGHĨA HTML & BÀN PHÍM (D-09)

### 2.1. Unified Focus Trap trên toàn bộ lớp phủ Modal & Drawer
Hàm `activateFocusTrap()`, `deactivateFocusTrap()`, `setBackgroundInert()` trong `magspread.js` được áp dụng đồng bộ cho cả 3 hộp thoại:

| Đối tượng kiểm tra | `role` / `aria-modal` / `aria-labelledby` | Khóa nền (`#mainContent`) | Chu kỳ `Tab` (12 bước) & `Shift+Tab` | Đóng `Escape` & Click Backdrop | Khôi phục Focus về nút mở | Trạng thái |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: |
| `#welcome-modal-backdrop` | `dialog` / `true` / `welcomeModalTitle` | `aria-hidden="true"` + `inert: true` | Không thoát (`escapedTab: false`, `shiftInside: true`) | Đạt | Khớp trigger (`navTabToday`) | **PASS** |
| `#contact-modal-backdrop` | `dialog` / `true` / `vcardModalName` | `aria-hidden="true"` + `inert: true` | Không thoát (`escapedTab: false`, `shiftInside: true`) | Đạt (`contactAfterClick: false`) | Khớp `.ms-vcard-trigger` | **PASS** |
| `#sideDrawer` | `dialog` / `true` / `drawerTitle` | `aria-hidden="true"` + `inert: true` | Không thoát (`escapedTab: false`, `shiftInside: true`) | Đạt (`#drawerBackdrop` → `false`) | Khớp `.ms-pulse-open-btn` | **PASS** |

### 2.2. Phần tử ngữ nghĩa & Điều hướng bàn phím `role="tablist"`
- Các khối nhảy nhanh ở Trang nhất (`.ms-today-jump-card` — 3 thẻ) và nút mở chi tiết Market Pulse (`.ms-pulse-open-btn` — 4 thẻ) đã chuyển thành `<button type="button">` chuẩn ngữ nghĩa.
- Nút lưu trữ ẩn `#navGroupArchive` giữ `tabindex="-1" aria-hidden="true"` để không xen ngang chuỗi focus bàn phím.
- **Desktop Tablist (`#navTabToday`..`#navTabB2B`):** Hỗ trợ đầy đủ `ArrowRight` (`#navTabMarket`), `End` (`#navTabB2B`), `Home` (`#navTabToday`), `ArrowLeft` vòng lại `#navTabB2B`.
- **Mobile Tablist (`.ms-mobile-quick-tabs` ở 390px):** Hỗ trợ `ArrowRight` (`#mobileTabMarket`), `End` (`#mobileTabB2B`), `Home` (`#mobileTabToday`).
- Vùng focus `:focus-visible` hiển thị viền rõ `2px solid var(--ms-primary)` trên các thành phần tương tác.

---

## 3. KÍCH THƯỚC CHỮ & VÙNG CHẠM CẢM ỨNG (D-16)

- Quét DOM thực tế qua 6 viewport (`320, 360, 390, 768, 1024, 1440`px) trên cả 4 tab: **`0` nút văn bản trực tiếp nhỏ hơn `12px`** (`smallFonts = []`).
- Quét toàn bộ nút/liên kết/ô nhập liệu hiển thị qua cả 4 tab ở độ phân giải di động `320, 360, 390, 768`px (bao gồm cả lúc mở `.floating-widget`): **`0` thành phần tương tác nhỏ hơn `44×44px`** (`smallTargetCount = 0`).
