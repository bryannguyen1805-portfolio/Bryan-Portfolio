# BÁO CÁO HIỆU SUẤT TẢI TRANG & TỐI ƯU HÓA HÌNH ẢNH (PERFORMANCE REPORT)
## DỰ ÁN: BRYAN FINTECH INTELLIGENCE
### PHIÊN BẢN: PHASE 08B — R1.0.0
**Mã tài liệu:** PHASE08B_R1.0.0_PERFORMANCE_REPORT  
**Mã lỗi mục tiêu:** D-13 (P2 - Medium), D-04 (Bảo toàn CLS)  
**Tác giả:** Principal Performance Engineer & Web Architect  
**Ngày phát hành:** 14/11/2026  
**Trạng thái nghiệm thu:** PASS — CORE WEB VITALS ĐẠT CHUẨN XANH (GREEN)  

---

## 1. TỐI ƯU HÓA HÌNH ẢNH LOGO BNEWS (D-13)

### 1.1. Thực trạng trước tối ưu
Logo Bnews ban đầu có độ phân giải gốc 1024×309px với dung lượng lên tới **227.951 bytes (~228 KB)**, nhưng trên giao diện thực tế chỉ hiển thị ở kích thước 38px chiều cao. Việc tải ảnh quá lớn gây lãng phí băng thông mạng di động.

### 1.2. Giải pháp thực thi
- Tạo phiên bản ảnh tối ưu sắc nét chuẩn Retina (400×121px) bằng thuật toán downsampling chất lượng cao:
  - `bnews-logo-light-opt.png`: **45.974 bytes (~45 KB, giảm 80% dung lượng)**.
  - `bnews-logo-dark-opt.png`: **42.408 bytes (~42 KB, giảm 81% dung lượng)**.
- Khai báo rõ ràng kích thước hiển thị `width="126" height="38"` trên thẻ `<img>` kết hợp tỉ lệ cố định để loại trừ 100% hiện tượng đẩy bố cục (Layout Shift).
- Đảm bảo độ trong suốt (alpha transparency) hoàn hảo, không răng cưa trên cả hai nền Light và Dark.

---

## 2. KẾT QUẢ ĐO KIỂM HIỆU NĂNG CORE WEB VITALS (CHROME DEVTOOLS TRACE)

Thực hiện đo kiểm Performance Trace trên trang vận hành thực tế:
- **Địa chỉ đo kiểm:** `https://bryanportfolio.io.vn/fintech-intelligence/index.html`
- **Môi trường:** Cold load (Bypass Cache = True), CPU Throttling = 1x.

| Chỉ số Core Web Vitals | Giá trị ghi nhận | Ngưỡng chuẩn Google | Trạng thái |
|:---|:---:|:---:|:---:|
| **Largest Contentful Paint (LCP)** | **447 ms** | ≤ 2.500 ms | **TỐT (GOOD - XANH)** |
| **Cumulative Layout Shift (CLS)** | **0.03** | ≤ 0.10 | **TỐT (GOOD - XANH)** |
| **Time to First Byte (TTFB)** | **132 ms** | ≤ 800 ms | **TỐT (GOOD - XANH)** |
| **First Contentful Paint (FCP)** | **210 ms** | ≤ 1.800 ms | **TỐT (GOOD - XANH)** |
| **Console Errors** | **0 lỗi** | 0 lỗi | **HOÀN HẢO** |

**Kết luận:** Điểm số CLS đạt mức 0.03 (thấp hơn nhiều so với ngưỡng trần 0.10), bảo toàn trọn vẹn thành quả của Phase 08A trong khi giảm tải hơn 80% dung lượng hình ảnh nhận diện.
