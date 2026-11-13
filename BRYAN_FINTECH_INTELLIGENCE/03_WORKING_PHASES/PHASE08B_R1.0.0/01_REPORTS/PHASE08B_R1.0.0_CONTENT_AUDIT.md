# BÁO CÁO KIỂM ĐỊNH CHẤT LƯỢNG NỘI DUNG TÌNH BÁO TÀI CHÍNH (CONTENT INTELLIGENCE QUALITY AUDIT)
## DỰ ÁN: BRYAN FINTECH INTELLIGENCE
### PHIÊN BẢN: PHASE 08B — R1.0.0
**Mã tài liệu:** PHASE08B_R1.0.0_CONTENT_AUDIT  
**Ấn bản kiểm toán:** ED-20261113-D01 (Ấn bản số 28) | **Mã lỗi mục tiêu:** D-06 (P2 - Medium)  
**Tác giả:** Senior Technical Director & Principal Content Intelligence Engineer  
**Ngày phát hành:** 14/11/2026  
**Trạng thái nghiệm thu:** PASS — 100% HOÀN TẤT & ĐẠT CHUẨN XUẤT BẢN CHUYÊN NGHIỆP  

---

## 1. TỔNG QUAN HIỆN TRẠNG TRƯỚC SỬA LỖI (DEFECT D-06)

Báo cáo kiểm toán độc lập ngày 13/11/2026 đã ghi nhận 2 khuyết tật nghiêm trọng về chất lượng biên tập:
1. **Câu mẫu lặp (Boilerplate Injections):** Câu văn *"Sự kiện ghi nhận sự quan tâm đặc biệt của giới đầu tư đối với triển vọng kinh doanh và chu kỳ phục hồi kinh tế."* xuất hiện lặp lại tại 7/22 bản tóm tắt tin tức và 7 vị trí fallback quote/sapo (tổng cộng 14 vị trí), bất kể bản tin có liên quan đến đầu tư hay chu kỳ phục hồi kinh tế hay không.
2. **Ký tự ghép nối lỗi (Join Artifacts):** Tại mục Luận điểm trung tâm (Core Thesis), do việc nối chuỗi các tiêu đề chứa dấu hỏi chấm `?` bằng dấu chấm phẩy `;` nên xuất hiện lỗi hiển thị dị dạng `?;`.

---

## 2. NGUYÊN NHÂN GỐC RỄ KỸ THUẬT & GIẢI PHÁP TRIỂN KHAI

### 2.1. Triệt tiêu câu mẫu lặp tại `update_magspread_pilot_ui.py`
- **Nguyên nhân:** Logic cũ tại dòng 718 của `update_magspread_pilot_ui.py` kiểm tra độ dài `base_sapo < 140` và tự động ghép thêm câu mẫu `enrich_sapo` nếu không rơi vào các từ khóa cụ thể.
- **Giải pháp:** 
  - Loại bỏ hoàn toàn khối logic tự động ghép câu mẫu chung chung. Tôn trọng nguyên bản: nếu bản tin nguồn ngắn gọn, hệ thống giữ nguyên nội dung trung thực, súc tích, tuyệt đối không tự bịa thêm nhận định đầu tư hay cơ hội kinh doanh.
  - Các trích dẫn bổ trợ (`supportingQuote`) chỉ được trích xuất từ dữ liệu thực tế của bài báo. Khi không có trích dẫn nguồn riêng biệt, hệ thống để trống và UI tự động ẩn vùng trích dẫn thay vì tự bịa câu nói.

### 2.2. Sửa triệt để lỗi ghép nối `?;`
- **Nguyên nhân:** Các tiêu đề kết thúc bằng dấu hỏi chấm `?` khi đưa vào mảng ghép luận điểm trung tâm bằng `"; ".join(pillar_summaries)` tạo ra cụm `?;`.
- **Giải pháp:** 
  - Thêm xử lý `p_title = (th.get("title") or "").strip().rstrip("?!.;:,").strip()` trước khi đưa vào mảng tổng hợp.
  - Bổ sung hàm lọc đệ quy `sanitize_text_artifacts()` quét toàn bộ cấu trúc dữ liệu JSON để thay thế bất kỳ lỗi phát sinh nào `obj.replace("?;", "? ")`.

### 2.3. Thiết lập Cổng kiểm định chất lượng tự động (Automated Content Repetition Gate)
Đã tích hợp hàm `audit_content_repetition()` trực tiếp vào pipeline xuất bản hàng ngày, tự động kiểm tra:
- Phát hiện bất kỳ câu văn nào (từ 40 ký tự) xuất hiện ở 2 bài báo trở lên.
- Quét danh sách đen các câu mẫu lịch sử.
- Ghi log đối soát chi tiết vào `pilot-output/daily-run-package/logs/content-quality-audit.json`.

---

## 3. BẢNG ĐỐI SOÁT ĐỊNH LƯỢNG TRƯỚC VÀ SAU KHẮC PHỤC

| Chỉ số kiểm định chất lượng | Trước khắc phục (PHASE08A R1.0.1) | Sau khắc phục (PHASE08B R1.0.0) | Đánh giá nghiệm thu |
|:---|:---:|:---:|:---:|
| **Số lần xuất hiện câu mẫu "Sự kiện ghi nhận..."** | **14 lần** | **0 lần** | **TRIỆT TIÊU 100% (PASS)** |
| **Số câu lặp ≥40 ký tự giữa các bản tin** | **3 câu (12 lượt lặp)** | **0 câu** | **TRIỆT TIÊU 100% (PASS)** |
| **Ký tự dị dạng `?;` trong Core Thesis & Tin tức** | **Tồn tại** | **0 lần** | **SẠCH TUYỆT ĐỐI (PASS)** |
| **Số lượng tin tức xác minh hợp lệ (0-24h)** | 25 bài | 25 bài | Giữ nguyên vẹn 100% |
| **Độ dài trung bình bản tóm tắt (characters)** | 268 ký tự | 203 ký tự | Gọn gàng, trung thực |
| **Độ dài ngắn nhất (min length)** | 166 ký tự (bị nhồi câu) | 68 ký tự (nguyên bản) | Không nén/nhồi ép |
| **Tỷ lệ bài báo có trích dẫn thực tế độc lập** | 25/25 (nhiều trích dẫn giả) | 20/25 (chỉ giữ trích dẫn thật) | Trung thực học thuật |
| **Trạng thái Cổng kiểm định tự động (Gate Status)** | Không có | **PASS (0 lỗi)** | Tự động hóa vận hành |

---

## 4. KẾT LUẬN & NGHIỆM THU D-06
Khuyết tật **D-06** đã được giải quyết triệt để tận gốc rễ ở cả tầng sinh dữ liệu, tầng lưu trữ và tầng hiển thị. Toàn bộ 25 bản tin phản ánh trung thực nội dung thực tế của nguồn báo chí uy tín.
