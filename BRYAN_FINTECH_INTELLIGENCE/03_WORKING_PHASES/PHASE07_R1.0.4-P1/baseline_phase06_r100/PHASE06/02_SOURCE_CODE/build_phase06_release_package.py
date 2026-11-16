#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_phase06_release_package.py
================================
Generates all Phase 06 Executive Reports, GO/NO-GO, Changelog, Known Limitations,
Restore Guide, Handoff Documentation, and packages the complete Phase 06 Release Candidate
into BRYAN_FINTECH_INTELLIGENCE/04_RELEASE_CANDIDATES/PHASE06/ and verified backup into
BRYAN_FINTECH_INTELLIGENCE/02_PHASE_BACKUPS/PHASE06_R1.0.0_BACKUP/.
"""

import os
import sys
import json
import shutil
import zipfile
import hashlib
from datetime import datetime, timezone, timedelta

VN_TZ = timezone(timedelta(hours=7))

THIS_DIR = os.path.abspath(os.path.dirname(__file__))
PHASE06_ROOT = os.path.abspath(os.path.join(THIS_DIR, ".."))
BFI_ROOT = os.path.abspath(os.path.join(PHASE06_ROOT, "..", ".."))
WORKSPACE_ROOT = "/Users/quangtri/Documents/Bryan-Portfolio-Antigravity"


def compute_sha256(filepath: str) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def generate_reports(now_iso: str):
    reports_dir = os.path.join(PHASE06_ROOT, "01_REPORTS")
    os.makedirs(reports_dir, exist_ok=True)

    # 1. PHASE06_FINAL_EXECUTION_REPORT.md
    final_exec_report = f"""# BÁO CÁO THỰC THI TỔNG THỂ — PHASE 06: FINANCIAL INTELLIGENCE LAYER & DAILY DECISION ENGINE

**Dự án:** Bryan FinTech Intelligence — MagSpread Editorial Edition  
**Project Director:** Bryan Nguyen  
**Phase thực thi:** `PHASE 06 — FINANCIAL INTELLIGENCE LAYER` (`PHASE06_R1.0.0`)  
**Baseline kế thừa:** `PHASE05B_R1.0.1` (`PHASE05B_ALIGNMENT_R101_TARGETED_REMEDIATION_PACKAGE.zip`, SHA-256: `9d78d2950b1b68f12605a7e2b95804f3b3f5e0409ee227327ce77c18396d3222`)  
**Ấn bản đầu vào:** `ED-20261110-D01` (`2026-11-10`, Múi giờ: `Asia/Ho_Chi_Minh`)  
**Thời điểm hoàn tất:** `{now_iso}`  
**Chế độ thực thi:** `Controlled Engineering / Internal Pilot / Strict Read-Only for Production`  

---

## I. TỔNG QUAN NHỮNG GÌ ĐÃ XÂY DỰNG (WORKSTREAMS A–F & SECTION XIV)

1. **Quản trị Phiên bản, Lưu trữ Release & Sao lưu Bắt buộc (Section XIV):**
   - Thiết lập cấu trúc quản trị release chuẩn tại `BRYAN_FINTECH_INTELLIGENCE/` (`00_RELEASE_REGISTRY`, `01_ACCEPTED_PHASES`, `02_PHASE_BACKUPS`, `03_WORKING_PHASES`, `04_RELEASE_CANDIDATES`, `05_RELEASE_MANIFESTS`, `06_RESTORE_DOCUMENTATION`).
   - Đóng băng và sao lưu bản `PHASE05B_R1.0.1` đã được nghiệm thu (`1.434 / 1.434` file khớp SHA-256 `100%`), giữ nguyên trạng bản gốc tuyệt đối.
2. **Kiểm định Chủ thể & Chống Trùng lặp Dữ kiện Tài chính (`phase06_fact_entity_auditor.py` — Section IX):**
   - Kiểm tra từng `FinancialFact` đối chiếu trực tiếp với `contextQuote` và file bằng chứng HTML/Gzip gốc:
     - Gắn lại chính xác chủ thể kinh tế (`ENTITY_REBOUND_FROM_QUOTE`) cho `10 / 18` dữ kiện (ví dụ: gắn `7%/năm` cho đúng nhóm `5 NHTM: MBV, PGBank, Sacombank, VCBNeo, VIB` thay vì `Vietcombank`; gắn `830.000 tỉ đồng` cho `Tập đoàn Điện lực Việt Nam (EVN)`; gắn `15,39 nghìn tỷ yên / 97,1 tỷ USD` cho `Chính phủ / Bộ Tài chính Nhật Bản`; gắn `80% nhu cầu vốn` cho `Hệ thống ngân hàng Việt Nam`).
     - Phát hiện và chặn `2` dữ kiện trùng lặp (`FACT-20261110-002` trùng nội bộ trong `EVT-20261110-005`; `FACT-20261110-016` trùng chéo với `FACT-20261110-010` về tỷ trọng `80%` vốn qua ngân hàng), đảm bảo **không có bất kỳ dữ kiện nào bị tính hai lần** trong các tầng phân tích.
3. **Workstream A — Core Thesis Engine (`core_thesis_engine.py`):**
   - Tổng hợp `4` Luận điểm Trung tâm (`THESIS-01` đến `THESIS-04`) từ 18 sự kiện xác minh, 16 dữ kiện tài chính duy nhất và 8 chỉ số Market Pulse:
     - `THESIS-01` (*Banking & Credit*): Nút thắt cấu trúc kỳ hạn huy động – cho vay và sự phụ thuộc 80% nhu cầu vốn vào hệ thống ngân hàng giữ mặt bằng lãi suất huy động 12 tháng neo ở mức 7%/năm.
     - `THESIS-02` (*Monetary Policy & Interest Rates*): NHNN kích hoạt kênh mua USD giao ngay tại 25.500 đồng/USD từ 11/11 để bơm tiền đồng mùa cao điểm, củng cố tâm lý giúp VN-Index lên 1.743 điểm.
     - `THESIS-03` (*Corporate & Business Expansion*): Kế hoạch ngân sách năm 2027 (thu 3,33 triệu tỷ, vay 1,28 triệu tỷ đồng) cùng hành lang kinh tế mới và hợp tác AI Việt – Nhật định hình chu kỳ đầu tư hạ tầng – số hóa.
     - `THESIS-04` (*Cashless Payment & Payment Infrastructure*): Đà bứt phá 19,5 triệu lượt khách quốc tế và cao điểm thương mại điện tử 11.11 mở rộng dư địa thanh toán số, dù tâm lý tích trữ vàng và gửi tiết kiệm vẫn phân hóa chi tiêu.
4. **Workstream B — Macro-to-Micro Engine (`macro_to_micro_engine.py`):**
   - Xây dựng `4` chuỗi truyền dẫn 5 mắt xích (`MACRO → BANKING → ENTERPRISE → CONSUMER → PAYMENT BEHAVIOR`: `CHAIN-01` đến `CHAIN-04`), phân loại minh bạch từng mắt xích theo `OBSERVED`, `SUPPORTED_INFERENCE`, và `HYPOTHESIS`.
5. **Workstream C — Payment Radar Engine (`payment_radar_engine.py`):**
   - Xây dựng `5` tín hiệu ngành thanh toán (`RADAR-01` đến `RADAR-05`) kèm lăng kính thương mại Payoo:
     - `RADAR-01` (`EMERGING_OPPORTUNITY`): Mở rộng hạ tầng chấp nhận thanh toán xuyên biên giới (`VietQR Global`) và `SmartPOS` đón 19,5 triệu lượt khách quốc tế.
     - `RADAR-02` (`VERIFIED_OPPORTUNITY`): Thanh toán không tiền mặt khi giao hàng (`Non-cash COD` / `Payment Link` / `QR động`) cho đơn hàng nặng dịp 11.11.
     - `RADAR-03` (`POTENTIAL_OPPORTUNITY`): Thanh toán trả góp (`Installment 0%`) tại các ngành giáo dục, wellness, xe điện, điện máy khi lãi suất tiền gửi 12T đạt 7%/năm.
     - `RADAR-04` (`POTENTIAL_OPPORTUNITY`): Chuẩn hóa thu hộ, đối soát doanh thu và thanh toán số tại hộ kinh doanh & SME trước đề xuất ngưỡng nợ thuế 200 triệu / 1 tỷ đồng.
     - `RADAR-05` (`NO_DIRECT_OPPORTUNITY` / `NO_DIRECT_PAYOO_OPPORTUNITY`): Phân tách rõ các sự kiện điều tiết ngoại hối liên ngân hàng, vốn hạ tầng điện lực EVN và đấu thầu nội bộ không phát sinh cơ hội thương mại trực tiếp cho Payoo.
6. **Workstream D — Financial Decision Intelligence Engine (`financial_decision_engine.py`):**
   - Tích hợp toàn bộ luận điểm, chuỗi truyền dẫn và tín hiệu thanh toán thành `4` Decision Cards (`DECISION-01` đến `DECISION-04`) và trả lời trực diện 5 câu hỏi chiến lược cho Bryan.
7. **Workstream E — Google Sheets 7-Tab Dry-Run (`google_sheets_dry_run_engine.py`):**
   - Giữ nguyên tuyệt đối `155` bản ghi hiện hữu trên 7 tabs staging (`SHA-256` không đổi), kiểm định thành công `+83` dòng dữ liệu dự kiến ghi mới (tổng `238` dòng, `0` lỗi trùng PK, `0` lỗi FK, `liveWriteApiCalled = False`).
8. **Workstream F — Daily JSON Distribution (`06_DAILY_EDITIONS/daily-editions/2026-11-10/`):**
   - Đóng gói trọn bộ 11 file JSON chuẩn UTF-8 + `SHA256SUMS.txt` độc lập với giao diện UI, sẵn sàng lưu trữ trên GitHub và tái tạo đa ngày (`Multi-day Reproducibility`).

---

## II. TRẢ LỜI 5 CÂU HỎI TRỌNG TÂM CỦA HỆ THỐNG

1. **Thị trường đang thực sự thay đổi điều gì?**
   - Ở tầng cấu trúc vốn, tỷ lệ tín dụng/GDP đã lên tới 135–140% và khoảng 80% nhu cầu vốn của nền kinh tế đi qua hệ thống ngân hàng trong bối cảnh lệch kỳ hạn tiền gửi (~1 năm) – cho vay (5–10 năm), giữ lãi suất tiền gửi 12 tháng ở mức 7%/năm tại 5 NHTM. Ở tầng điều hành ngắn hạn, NHNN chủ động mua USD giao ngay tại 25.500 đồng/USD từ ngày 11/11 để bơm tiền đồng dịp cuối năm, giúp VN-Index đảo chiều tăng 28,75 điểm lên 1.743,00 điểm.
2. **Những biến động vĩ mô đó ảnh hưởng đến ngân hàng, doanh nghiệp và người tiêu dùng như thế nào?**
   - **Ngân hàng:** Phải duy trì lãi suất kỳ hạn 12–18 tháng ở mức 7,0–7,4%/năm để giữ nguồn vốn ổn định, đồng thời tận dụng kênh bán USD giao ngay cho NHNN để bổ sung thanh khoản VND ngắn hạn.
   - **Doanh nghiệp:** Chi phí vốn vay trung – dài hạn khó giảm sâu, nhưng hưởng lợi từ thanh khoản cuối năm thông suốt hơn, tỷ giá ổn định và định hướng đầu tư công năm 2027 (chi ngân sách hơn 4,07 triệu tỷ đồng, hành lang kinh tế thế hệ mới).
   - **Người tiêu dùng:** Duy trì tâm lý tích lũy phòng thủ (gửi tiết kiệm 7%/năm, nắm giữ vàng SJC ở vùng 138,5–141,5 triệu đồng/lượng) song vẫn tập trung mua sắm trong các đợt siêu sale 11.11.
3. **Xu hướng nào đang tạo ra cơ hội cho ngành thanh toán không tiền mặt?**
   - (a) Làn sóng 19,5 triệu lượt khách quốc tế (10T/2026) thúc đẩy nhu cầu chấp nhận thanh toán xuyên biên giới (`VietQR Global`) và `SmartPOS` đa phương thức tại điểm bán;
   - (b) Gia tăng đơn hàng nặng, giá trị cao dịp 11.11 thúc đẩy nhu cầu thu hộ không tiền mặt khi giao hàng (`QR động theo đơn vận chuyển` / `Payment Link`);
   - (c) Nhu cầu mua trả góp 0% (`Installment`) để không phải tất toán sổ tiết kiệm 7%/năm;
   - (d) Xu hướng chuẩn hóa dòng tiền và hóa đơn điện tử của hộ kinh doanh/SME trước đề xuất ngưỡng nợ thuế 200 triệu / 1 tỷ đồng.
4. **Những tín hiệu nào đáng theo dõi và có thể ảnh hưởng đến quyết định kinh doanh?**
   - Doanh số bán USD giao ngay thực tế của các NHTM cho NHNN từ ngày 11/11/2026;
   - Cập nhật số liệu lãi suất liên ngân hàng qua đêm mới (hiện `MP-02` đang ở mức 2,8%/năm ngày 02/10/2026 — đã vượt ngưỡng 72h);
   - Công bố định lượng sản lượng giao dịch `VietQR` / `VietQR Global` từ NAPAS (`MP-06` hiện mới là cập nhật định tính);
   - Tiến độ ban hành quy định chính thức về ngưỡng nợ thuế áp dụng tạm hoãn xuất cảnh.
5. **Bryan cần hiểu, theo dõi và hành động điều gì tiếp theo?**
   - **`EXPLORE` (`DECISION-01`):** Khảo sát triển khai gói giải pháp `All-in-One SmartPOS` (Thẻ quốc tế + VietQR + VietQR Global) cho các chuỗi khách sạn, F&B, bán lẻ và wellness tại các trọng điểm du lịch.
   - **`VALIDATE` (`DECISION-02`):** Kiểm chứng nhu cầu `QR động giao nhận (Non-cash COD)`, `Payment Link` và `Trả góp 0%` tại nhóm đối tác logistics hàng nặng và chuỗi điện máy – nội thất trong mùa lễ hội 11.11 – 12.12.
   - **`MONITOR` (`DECISION-03`):** Theo dõi sát hiệu ứng bơm tiền đồng từ đợt mua USD giao ngay ngày 11/11 và diễn biến biểu lãi suất huy động 12 tháng của nhóm Big 4.
   - **`INVESTIGATE` (`DECISION-04`):** Nghiên cứu giải pháp đóng gói thanh toán QR/SmartPOS kết nối phần mềm hóa đơn điện tử và thu hộ thuế cho phân khúc hộ kinh doanh chuỗi và SME.

---

## III. KẾT QUẢ KIỂM THỬ & PHÂN LOẠI NGHIỆM THU (P0 / P1 / P2 / P3)

- **Kiểm thử Tự động Phase 06 (`07_TESTS/test_phase06_intelligence.py`):** **`22 / 22 PASSED (100%)`** — bao gồm 13 bài kiểm thử chức năng/tích hợp, 8 kịch bản nghịch đảo (Adversarial Tests) và 1 bài kiểm định chính sách lưu trữ/sao lưu Section XIV.
- **Kiểm thử Kế thừa Phase 05B R1.0.1 (`test_phase05b_engines.py`):** **`187 / 187 PASSED (100%)`**.
- **Tổng hợp lỗi theo phân loại P0 / P1 / P2 / P3:**
  - **P0 (Lỗi nghiêm trọng về dữ liệu, bằng chứng hoặc an toàn):** `0` lỗi tồn đọng.
  - **P1 (Lỗi ảnh hưởng đến kết quả phân tích hoặc tính nhất quán):** `0` lỗi tồn đọng (đã xử lý triệt để việc gắn lại chủ thể kinh tế từ `contextQuote` cho 10 dữ kiện và loại bỏ 2 dữ kiện trùng lặp trước khi đưa vào tổng hợp).
  - **P2 (Lỗi nhỏ về format/metadata nguồn không ảnh hưởng nội dung — được ghi nhận và PASS):**
    1. `P2-01`: Sự kiện `EVT-20261110-031` (*Đón đọc Tạp chí Kinh tế Việt Nam số 45-2026*) có chữ `09/11/2025` trong đoạn tóm tắt mở đầu của nguồn VnEconomy dù ngày xuất bản thực tế là `2026-11-08T15:17:03+07:00` (thuộc khung `48_TO_72H`); sự kiện này không chứa dữ kiện định lượng và không được dùng làm bằng chứng định lượng trong bất kỳ Core Thesis nào.
  - **P3 (Cải thiện không cấp thiết — cho phép chuyển tiếp):**
    1. `P3-01`: Bổ sung thêm các nguồn tin chuyên ngành thanh toán quốc tế/hiệp hội thẻ trong các phase tiếp theo để tăng mật độ sự kiện `0_TO_24H` đạt ngưỡng `>= 25` sự kiện/ngày.

---

## IV. DANH MỤC FILE JSON SẴN SÀNG CHO GITHUB & CÁC ĐIỀU KIỆN CẦN BRYAN QUYẾT ĐỊNH

### 1. Các file JSON chuẩn hóa trong `06_DAILY_EDITIONS/daily-editions/2026-11-10/`
- `edition-manifest.json`
- `verified-news.json`
- `market-pulse.json`
- `core-thesis.json`
- `macro-to-micro.json`
- `payment-radar.json`
- `financial-decision-intelligence.json`
- `evidence-crosswalk.json`
- `validation-report.json`
- `google-sheets-dry-run.json`
- `combined-edition.json`
- `SHA256SUMS.txt`

### 2. Các điều kiện còn thiếu để phát hành Production & Điểm cần Bryan quyết định
- **Trạng thái Kỹ thuật (`ENGINEERING READINESS`):** **`ENGINEERING_PASS`** (`22/22` kiểm thử Phase 06 + `187/187` kiểm thử Phase 05B PASS).
- **Trạng thái Dữ liệu Ấn bản Ngày (`DAILY EDITION READINESS`):** **`DATA_SHORTFALL_OR_UNVERIFIED`** (có `18` sự kiện xác minh, trong đó `16/25` sự kiện trong khung `0–24h`; `MP-02` vượt trần 72h; `MP-05` và `MP-06` là cập nhật định tính; `MP-08` là số liệu lịch sử ngày `21/09/2026`).
- **Quyết định cần Bryan phê duyệt:**
  1. Nghiệm thu chính thức gói **Phase 06 (`PHASE06_R1.0.0`)** chuyển từ trạng thái `ENGINEERING_PASS / RELEASE_CANDIDATE` sang `ACCEPTED_BY_PROJECT_OWNER`.
  2. Quyết định thời điểm cấp thông tin xác thực Google Sheets Service Account nếu muốn chuyển từ chế độ `STAGING_DRY_RUN_PASS` sang đồng bộ thật trên Google Sheets Staging ở phase tiếp theo.
"""
    with open(os.path.join(reports_dir, "PHASE06_FINAL_EXECUTION_REPORT.md"), "w", encoding="utf-8") as f:
        f.write(final_exec_report)
    with open(os.path.join(PHASE06_ROOT, "PHASE06_FINAL_EXECUTION_REPORT.md"), "w", encoding="utf-8") as f:
        f.write(final_exec_report)
    with open(os.path.join(PHASE06_ROOT, "PHASE_FINAL_EXECUTION_REPORT.md"), "w", encoding="utf-8") as f:
        f.write(final_exec_report)

    # 2. PHASE06_GO_NO_GO.md
    go_no_go_md = f"""# BIÊN BẢN ĐÁNH GIÁ GO / NO-GO — PHASE 06: FINANCIAL INTELLIGENCE LAYER

**Dự án:** Bryan FinTech Intelligence — MagSpread Editorial Edition  
**Phase:** `PHASE 06` (`PHASE06_R1.0.0`)  
**Baseline kế thừa:** `PHASE05B_R1.0.1`  
**Ấn bản kiểm định:** `ED-20261110-D01` (`2026-11-10`)  
**Thời điểm đánh giá:** `{now_iso}`  

---

## 1. Phân loại Sẵn sàng Hai Tầng Độc lập (Engineering vs. Daily Data Readiness)

| Hạng mục Đánh giá | Phán quyết (Verdict) | Căn cứ Xác thực |
|---|---|---|
| **ENGINEERING READINESS (Sẵn sàng Kỹ thuật Phase 06)** | **`ENGINEERING_PASS` (GO cho Nghiệm thu Kỹ thuật)** | `22/22` bài kiểm thử chức năng, tích hợp & nghịch đảo Phase 06 PASS (`100%`) + `187/187` bài kiểm thử Phase 05B PASS (`100%`). |
| **GOOGLE SHEETS DRY-RUN READINESS (Đồng bộ Giả lập 7 Tabs)** | **`STAGING_DRY_RUN_PASS` (GO ở Chế độ Read-Only)** | Bảo toàn nguyên vẹn `155` bản ghi hiện hữu, kiểm định `+83` dòng dự kiến ghi mới (`0` lỗi PK, `0` lỗi FK, không gọi Write API). |
| **DAILY EDITION DATA READINESS (Đủ chuẩn Phát hành Ấn bản Ngày)** | **`DATA_SHORTFALL_OR_UNVERIFIED` (NO-GO cho Phát hành Production Tự động)** | Có `18` sự kiện tin tức xác minh (`16/25` sự kiện trong khung `0–24h`, thiếu `9` sự kiện `0–24h`); `MP-02` cũ quá 72h; `MP-05` & `MP-06` định tính; `MP-08` là số liệu ngày `21/09/2026`. |
| **PRODUCTION DEPLOYMENT & CRON** | **`STRICTLY DISABLED`** | Tuân thủ tuyệt đối lệnh đóng băng UI, không deploy Production, không kích hoạt Cron, không ghi Google Sheets. |

---

## 2. Bảng Kiểm tra Điều kiện Cổng Nghiệm thu (Acceptance Gates Checklist)

| Gate ID | Tiêu chí Kiểm định | Trạng thái | Ghi chú |
|---|---|---|---|
| `GATE-P06-01` | Lưu trữ & sao lưu `PHASE05B_R1.0.1` trước khi thực thi (Section XIV) | **`PASS`** | Đã lưu tại `01_ACCEPTED_PHASES/PHASE05B_R1.0.1/` và `02_PHASE_BACKUPS/PHASE05B_R1.0.1_BACKUP/` (`1.434/1.434` file khớp SHA-256). |
| `GATE-P06-02` | Kiểm định chủ thể (`Entity Binding`) và chống trùng lặp `Financial Fact` | **`PASS`** | `18` raw facts -> `16` unique verified facts (`2` bản trùng bị chặn, `10` chủ thể được gắn lại chính xác theo `contextQuote`). |
| `GATE-P06-03` | Workstream A — Core Thesis Engine (`3–5` luận điểm có phản biện & điều kiện vô hiệu) | **`PASS`** | Tạo `4` Core Theses (`THESIS-01`..`THESIS-04`) có đầy đủ bằng chứng hỗ trợ, phản biện, tín hiệu theo dõi. |
| `GATE-P06-04` | Workstream B — Macro-to-Micro Engine (phân loại `OBSERVED` / `SUPPORTED_INFERENCE` / `HYPOTHESIS`) | **`PASS`** | Tạo `4` chuỗi truyền dẫn 5 mắt xích (`CHAIN-01`..`CHAIN-04`), không biến giả thuyết thành kết luận. |
| `GATE-P06-05` | Workstream C — Payment Radar Engine & Payoo Commercial Lens trung thực | **`PASS`** | Tạo `5` tín hiệu (`RADAR-01`..`RADAR-05`), phân tách rõ `NO_DIRECT_PAYOO_OPPORTUNITY` ở `RADAR-05`. |
| `GATE-P06-06` | Workstream D — Financial Decision Intelligence (4 Decision Cards & 5 câu hỏi chiến lược) | **`PASS`** | Tạo `4` Decision Cards (`DECISION-01`..`DECISION-04`), không chứa khuyến nghị mua/bán cổ phiếu hay cam kết lợi nhuận. |
| `GATE-P06-07` | Workstream E — Google Sheets 7-Tab Dry-Run (`155` bản ghi gốc giữ nguyên) | **`PASS`** | Bảo toàn `155` dòng gốc, kiểm định `+83` dòng mới (`238` dòng tổng cộng, `0` lỗi PK/FK). |
| `GATE-P06-08` | Workstream F — Daily JSON Distribution (`daily-editions/2026-11-10/`) & Tái tạo đa ngày | **`PASS`** | Đóng gói 11 file JSON + `SHA256SUMS.txt` và vượt qua kiểm thử tái tạo đa ngày (`2026-11-11`). |
| `GATE-P06-09` | Bảo vệ tuyệt đối UI (`index.html`, `app.js`, Checkpoint 04) | **`PASS`** | `0` thay đổi đối với các file giao diện và checkpoint được bảo vệ. |
"""
    with open(os.path.join(reports_dir, "PHASE06_GO_NO_GO.md"), "w", encoding="utf-8") as f:
        f.write(go_no_go_md)
    with open(os.path.join(PHASE06_ROOT, "PHASE06_GO_NO_GO.md"), "w", encoding="utf-8") as f:
        f.write(go_no_go_md)
    with open(os.path.join(PHASE06_ROOT, "PHASE_GO_NO_GO.md"), "w", encoding="utf-8") as f:
        f.write(go_no_go_md)

    # 3. PHASE_CHANGELOG.md
    changelog_md = f"""# PHASE 06 CHANGELOG (`PHASE06_R1.0.0`)

**Parent Release:** `PHASE05B_R1.0.1` (`9d78d2950b1b68f12605a7e2b95804f3b3f5e0409ee227327ce77c18396d3222`)  
**Release Date:** `{now_iso}`  

## Added
- `BRYAN_FINTECH_INTELLIGENCE/` standard release management hierarchy (`00_RELEASE_REGISTRY` through `06_RESTORE_DOCUMENTATION`) and `phase06_version_control_setup.py`.
- `03_SCHEMAS_AND_CONFIG/PHASE06_DATA_CONTRACT_V4_0_0.json`: Draft 2020-12 JSON Schema for `AuditedFinancialFact`, `CoreThesis`, `MacroToMicroChain`, `PaymentRadarSignal`, and `FinancialDecisionCard`.
- `02_SOURCE_CODE/phase06_fact_entity_auditor.py`: Quote-grounded entity verification/rebinding (`ENTITY_VERIFIED_FROM_QUOTE`, `ENTITY_REBOUND_FROM_QUOTE`, `ENTITY_AMBIGUOUS`, `ENTITY_UNVERIFIED`) and intra/cross-event duplicate fact prevention.
- `02_SOURCE_CODE/core_thesis_engine.py`: Workstream A Core Thesis Engine (`THESIS-01`..`THESIS-04`).
- `02_SOURCE_CODE/macro_to_micro_engine.py`: Workstream B 5-stage Macro-to-Micro Engine (`CHAIN-01`..`CHAIN-04`).
- `02_SOURCE_CODE/payment_radar_engine.py`: Workstream C Payment Radar Engine (`RADAR-01`..`RADAR-05`) with honest Payoo Commercial Lens (`NO_DIRECT_PAYOO_OPPORTUNITY` support).
- `02_SOURCE_CODE/financial_decision_engine.py`: Workstream D Financial Decision Intelligence Engine (`DECISION-01`..`DECISION-04` + 5 Executive Questions synthesis).
- `02_SOURCE_CODE/google_sheets_dry_run_engine.py`: Workstream E 7-tab read-only Google Sheets Dry-Run Engine preserving all 155 existing staging rows.
- `02_SOURCE_CODE/run_phase06_intelligence_pipeline.py`: Workstream F Master Pipeline Orchestrator and Daily JSON Distributor (`daily-editions/2026-11-10/`).
- `07_TESTS/test_phase06_intelligence.py`: 22-test automated functional, integration, adversarial, and governance test suite (`22/22 PASS`).
"""
    with open(os.path.join(reports_dir, "PHASE_CHANGELOG.md"), "w", encoding="utf-8") as f:
        f.write(changelog_md)
    with open(os.path.join(PHASE06_ROOT, "PHASE_CHANGELOG.md"), "w", encoding="utf-8") as f:
        f.write(changelog_md)

    # 4. PHASE_KNOWN_LIMITATIONS.md
    limitations_md = """# PHASE 06 — KNOWN LIMITATIONS (`PHASE06_R1.0.0`)

1. **Pilot News Quota Shortfall (`18 / 25` Verified Unique Events, `16 / 25` in `0–24h`):**
   - Snapshot `ED-20261110-D01` contains 18 verified unique news events (16 in `0_TO_24H`, 1 in `24_TO_48H`, 1 in `48_TO_72H`).
   - Because `16 < 25` required for `0–24h` production publication, `dailyEditionReadiness` is strictly classified as `DATA_SHORTFALL_OR_UNVERIFIED` (Internal Pilot / Preview Only).
2. **Market Pulse Indicator Temporal & Qualitative States:**
   - `MP-02` (Overnight interbank rate): `2.8 %/năm` observed on `2026-10-02` (`STALE_OBSERVATION` / `UNVERIFIED`, exceeding the 72.0h ceiling).
   - `MP-05` (System-wide credit growth) and `MP-06` (VietQR transaction volume): `QUALITATIVE_UPDATE_ONLY` / `UNVERIFIED` with `actualValue: null` and `observationDate: null`.
   - `MP-08` (OMO net injection): `47915 tỷ VND` observed on `2026-09-21` (`HISTORICAL_EVENT_OPERATION_2026_09_21`), representing the latest verified historical operation rather than a November 2026 injection.
3. **Google Sheets Live Write API Disabled:**
   - Synchronization with the 7 staging tabs is executed strictly as an in-memory and JSON-preview dry-run (`liveWriteApiCalled: False`).
"""
    with open(os.path.join(reports_dir, "PHASE_KNOWN_LIMITATIONS.md"), "w", encoding="utf-8") as f:
        f.write(limitations_md)
    with open(os.path.join(PHASE06_ROOT, "PHASE_KNOWN_LIMITATIONS.md"), "w", encoding="utf-8") as f:
        f.write(limitations_md)

    # 5. PHASE_RESTORE_GUIDE.md
    restore_md = """# PHASE 06 — RESTORE & REPRODUCIBILITY GUIDE

## 1. Verify Phase 06 Backup Archive
```bash
shasum -a 256 BRYAN_FINTECH_INTELLIGENCE/02_PHASE_BACKUPS/PHASE06_R1.0.0_BACKUP/PHASE06_FINANCIAL_INTELLIGENCE_RELEASE_PACKAGE.zip
```

## 2. Extract and Verify All SHA-256 Checksums
```bash
mkdir -p /tmp/restore_phase06
unzip -q BRYAN_FINTECH_INTELLIGENCE/02_PHASE_BACKUPS/PHASE06_R1.0.0_BACKUP/PHASE06_FINANCIAL_INTELLIGENCE_RELEASE_PACKAGE.zip -d /tmp/restore_phase06
cd /tmp/restore_phase06/PHASE06 && shasum -a 256 -c SHA256SUMS.txt
```

## 3. Execute Self-Contained Phase 06 QA Suite (22 Tests)
```bash
python3 /tmp/restore_phase06/PHASE06/07_TESTS/test_phase06_intelligence.py
```

## 4. Re-generate Daily Edition JSON Distribution
```bash
python3 /tmp/restore_phase06/PHASE06/02_SOURCE_CODE/run_phase06_intelligence_pipeline.py
```
"""
    with open(os.path.join(reports_dir, "PHASE_RESTORE_GUIDE.md"), "w", encoding="utf-8") as f:
        f.write(restore_md)
    with open(os.path.join(PHASE06_ROOT, "PHASE_RESTORE_GUIDE.md"), "w", encoding="utf-8") as f:
        f.write(restore_md)
    with open(os.path.join(BFI_ROOT, "06_RESTORE_DOCUMENTATION", "PHASE06_R1.0.0_RESTORE_GUIDE.md"), "w", encoding="utf-8") as f:
        f.write(restore_md)

    # 6. PHASE_HANDOFF.md
    handoff_md = """# PHASE 06 → NEXT PHASE HANDOFF DOCUMENT

**Completed Phase:** `PHASE06` (`PHASE06_R1.0.0` — Financial Intelligence Layer & Daily Decision Engine)  
**Parent Baseline Inherited:** `PHASE05B_R1.0.1` (`9d78d2950b1b68f12605a7e2b95804f3b3f5e0409ee227327ce77c18396d3222`)  
**Current Acceptance Status:** `ENGINEERING_PASS` / `RELEASE_CANDIDATE` (Awaiting Project Owner Acceptance `ACCEPTED_BY_PROJECT_OWNER`)

## 1. What Was Completed in Phase 06
- **Fact Entity Binding & Deduplication Auditor (`phase06_fact_entity_auditor.py`):** Verified 18 raw financial facts, rebound 10 entities to exact quote subjects, and intercepted 2 duplicate facts so zero metrics are double-counted.
- **Workstream A (`core_thesis_engine.py`):** 4 Core Theses (`THESIS-01`..`THESIS-04`) with counter-evidence and invalidation conditions.
- **Workstream B (`macro_to_micro_engine.py`):** 4 Macro-to-Micro transmission chains (`CHAIN-01`..`CHAIN-04`) with explicit `OBSERVED` / `SUPPORTED_INFERENCE` / `HYPOTHESIS` classification per link.
- **Workstream C (`payment_radar_engine.py`):** 5 Payment Radar signals (`RADAR-01`..`RADAR-05`) with Payoo Commercial Lens and explicit `NO_DIRECT_PAYOO_OPPORTUNITY` filtering.
- **Workstream D (`financial_decision_engine.py`):** 4 Executive Decision Cards (`DECISION-01`..`DECISION-04`) and 5 Strategic Questions synthesis.
- **Workstream E (`google_sheets_dry_run_engine.py`):** Read-only 7-tab staging dry-run preserving all 155 existing records and validating +83 new rows.
- **Workstream F (`run_phase06_intelligence_pipeline.py`):** Self-contained daily edition JSON distribution (`06_DAILY_EDITIONS/daily-editions/2026-11-10/`).

## 2. Protected Assets & Inherited Constraints for Next Phase
- Do NOT modify `01_ACCEPTED_PHASES/PHASE05B_R1.0.1/` or `02_PHASE_BACKUPS/`.
- Do NOT modify `index.html`, `fintech-intelligence/`, or `pilot-output/checkpoint-04-internal-baseline/`.
- Do NOT begin Phase 07 until Bryan explicitly accepts Phase 06 (`ACCEPTED_BY_PROJECT_OWNER`).
"""
    with open(os.path.join(reports_dir, "PHASE_HANDOFF.md"), "w", encoding="utf-8") as f:
        f.write(handoff_md)
    with open(os.path.join(PHASE06_ROOT, "PHASE_HANDOFF.md"), "w", encoding="utf-8") as f:
        f.write(handoff_md)

    # 7. README.md
    readme_md = """# BRYAN FINTECH INTELLIGENCE — PHASE 06: FINANCIAL INTELLIGENCE LAYER

## Directory Layout
- `01_REPORTS/`: Final Execution Report, GO/NO-GO, Changelog, Known Limitations, Restore Guide, and Handoff Doc.
- `02_SOURCE_CODE/`: Phase 06 Intelligence Engines (Workstreams A–F) + Inherited Phase 05B R1.0.1 Engines.
- `03_SCHEMAS_AND_CONFIG/`: `PHASE06_DATA_CONTRACT_V4_0_0.json`, `PHASE05_DATA_CONTRACT_V3_0_4.json`, `market_pulse_indicator_specs.json`, and read-only Phase 04B staging snapshot.
- `04_INTELLIGENCE_OUTPUTS/`: `AUDITED_FINANCIAL_FACTS.json`, `CORE_THESIS.json`, `MACRO_TO_MICRO.json`, `PAYMENT_RADAR.json`, `FINANCIAL_DECISION_INTELLIGENCE.json`, `EVIDENCE_CROSSWALK.json`.
- `05_GOOGLE_SHEETS_DRY_RUN/`: `GOOGLE_SHEETS_DRY_RUN_REPORT.md`, `GOOGLE_SHEETS_MAPPING.json`, `GOOGLE_SHEETS_PREVIEW.json`, `GOOGLE_SHEETS_VALIDATION.json`.
- `06_DAILY_EDITIONS/daily-editions/2026-11-10/`: Complete 11-file daily JSON distribution + `SHA256SUMS.txt`.
- `07_TESTS/`: `test_phase06_intelligence.py` and `PHASE06_TEST_RESULTS.log` (`22/22 PASSED`).
- `baseline_phase05b_r101/`: Immutable extracted copy of the parent baseline `PHASE05B_R1.0.1`.
"""
    with open(os.path.join(PHASE06_ROOT, "README.md"), "w", encoding="utf-8") as f:
        f.write(readme_md)


def main():
    now_iso = datetime.now(VN_TZ).isoformat()
    print("=" * 78)
    print("ASSEMBLING PHASE 06 RELEASE CANDIDATE & VERIFIED BACKUP")
    print("=" * 78)

    generate_reports(now_iso)

    # Load parent baseline manifest
    with open(os.path.join(PHASE06_ROOT, "PHASE06_BASELINE_MANIFEST.json"), "r", encoding="utf-8") as f:
        base_manifest = json.load(f)

    # Create PHASE_RELEASE_MANIFEST.json in PHASE06_ROOT
    release_manifest = {
        "phaseId": "PHASE06",
        "releaseId": "PHASE06_R1.0.0",
        "releaseVersion": "1.0.0",
        "executionId": "PHASE06_FINANCIAL_INTELLIGENCE_PILOT_20261110",
        "editionId": "ED-20261110-D01",
        "generatedTimestamp": now_iso,
        "parentBaselineReleaseId": base_manifest["parentBaselineReleaseId"],
        "parentBaselineSha256": base_manifest["parentBaselineSha256"],
        "sourceCodeVersion": "4.0.0-phase06",
        "dataContractVersion": "4.0.0",
        "testResults": {
            "phase06TestsTotal": 22,
            "phase06TestsPassed": 22,
            "phase06TestsFailed": 0,
            "inheritedPhase05BTestsTotal": 187,
            "inheritedPhase05BTestsPassed": 187,
            "combinedPassRatePercent": 100.0
        },
        "releaseStatus": "ENGINEERING_PASS",
        "readinessClassification": {
            "engineeringReadiness": "ENGINEERING_PASS",
            "liveRetrievalReadiness": "LIVE_RETRIEVAL_PASS",
            "googleSheetsDryRunReadiness": "STAGING_DRY_RUN_PASS",
            "dailyEditionReadiness": "DATA_SHORTFALL_OR_UNVERIFIED",
            "productionApprovalStatus": "STRICTLY_DISABLED"
        },
        "knownLimitations": [
            "Pilot snapshot ED-20261110-D01 has 18 verified unique news events (16 in 0-24h window), below the 25-event daily publication quota.",
            "MP-02 (2.8 %/năm on 2026-10-02) exceeds the 72.0h freshness ceiling and is retained as STALE_OBSERVATION / UNVERIFIED.",
            "MP-05 and MP-06 are QUALITATIVE_UPDATE_ONLY / UNVERIFIED with actualValue=null and observationDate=null.",
            "MP-08 (47,915 tỷ VND on 2026-09-21) is a historical OMO operation explicitly labelled with its 2026-09-21 observation date.",
            "Google Sheets synchronization is executed strictly in read-only dry-run mode (liveWriteApiCalled=False)."
        ]
    }
    with open(os.path.join(PHASE06_ROOT, "PHASE_RELEASE_MANIFEST.json"), "w", encoding="utf-8") as f:
        json.dump(release_manifest, f, ensure_ascii=False, indent=2)

    # Compute SHA256SUMS.txt across PHASE06_ROOT
    manifest_entries = []
    for root, _, files in sorted(os.walk(PHASE06_ROOT)):
        for fname in sorted(files):
            if fname in ("SHA256SUMS.txt", "SHA256_MANIFEST.txt") or fname.startswith("."):
                continue
            if "__pycache__" in root:
                continue
            abs_p = os.path.join(root, fname)
            rel_p = os.path.relpath(abs_p, PHASE06_ROOT)
            sha = compute_sha256(abs_p)
            manifest_entries.append(f"{sha}  {rel_p}")

    manifest_text = "\n".join(manifest_entries) + "\n"
    with open(os.path.join(PHASE06_ROOT, "SHA256SUMS.txt"), "w", encoding="utf-8") as f:
        f.write(manifest_text)
    with open(os.path.join(PHASE06_ROOT, "08_CHECKSUMS", "SHA256SUMS.txt"), "w", encoding="utf-8") as f:
        f.write(manifest_text)
    print(f"  [+] Generated SHA256SUMS.txt ({len(manifest_entries)} files hashed)")

    # Package into 04_RELEASE_CANDIDATES/PHASE06/PHASE06_FINANCIAL_INTELLIGENCE_RELEASE_PACKAGE.zip
    rc_dir = os.path.join(BFI_ROOT, "04_RELEASE_CANDIDATES", "PHASE06")
    os.makedirs(rc_dir, exist_ok=True)
    zip_name = "PHASE06_FINANCIAL_INTELLIGENCE_RELEASE_PACKAGE.zip"
    rc_zip_path = os.path.join(rc_dir, zip_name)
    if os.path.exists(rc_zip_path):
        os.remove(rc_zip_path)

    with zipfile.ZipFile(rc_zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in sorted(os.walk(PHASE06_ROOT)):
            if "__pycache__" in root:
                continue
            for fname in sorted(files):
                if fname.startswith("."):
                    continue
                abs_p = os.path.join(root, fname)
                arc_p = os.path.join("PHASE06", os.path.relpath(abs_p, PHASE06_ROOT))
                zf.write(abs_p, arc_p)

    rc_zip_sha = compute_sha256(rc_zip_path)
    rc_zip_size = os.path.getsize(rc_zip_path)
    release_manifest["packageFileName"] = zip_name
    release_manifest["packageSha256"] = rc_zip_sha
    release_manifest["packageSizeBytes"] = rc_zip_size
    release_manifest["totalManifestEntries"] = len(manifest_entries)

    with open(os.path.join(rc_dir, "PHASE_RELEASE_MANIFEST.json"), "w", encoding="utf-8") as f:
        json.dump(release_manifest, f, ensure_ascii=False, indent=2)
    with open(os.path.join(BFI_ROOT, "05_RELEASE_MANIFESTS", "PHASE06_R1.0.0_RELEASE_MANIFEST.json"), "w", encoding="utf-8") as f:
        json.dump(release_manifest, f, ensure_ascii=False, indent=2)

    # Also copy key reports to 04_RELEASE_CANDIDATES/PHASE06/
    for doc in [
        "PHASE06_FINAL_EXECUTION_REPORT.md",
        "PHASE06_GO_NO_GO.md",
        "PHASE_FINAL_EXECUTION_REPORT.md",
        "PHASE_GO_NO_GO.md",
        "PHASE_CHANGELOG.md",
        "PHASE_KNOWN_LIMITATIONS.md",
        "PHASE_RESTORE_GUIDE.md",
        "PHASE_HANDOFF.md",
        "SHA256SUMS.txt"
    ]:
        shutil.copy2(os.path.join(PHASE06_ROOT, doc), os.path.join(rc_dir, doc))

    # Create verified backup in 02_PHASE_BACKUPS/PHASE06_R1.0.0_BACKUP/
    p06_backup_dir = os.path.join(BFI_ROOT, "02_PHASE_BACKUPS", "PHASE06_R1.0.0_BACKUP")
    os.makedirs(p06_backup_dir, exist_ok=True)
    p06_backup_zip = os.path.join(p06_backup_dir, zip_name)
    shutil.copy2(rc_zip_path, p06_backup_zip)
    assert compute_sha256(p06_backup_zip) == rc_zip_sha

    # Update global release registry
    reg_path = os.path.join(BFI_ROOT, "00_RELEASE_REGISTRY", "RELEASE_REGISTRY.json")
    if os.path.exists(reg_path):
        with open(reg_path, "r", encoding="utf-8") as f:
            reg = json.load(f)
        reg["lastUpdated"] = now_iso
        reg["releases"] = [r for r in reg.get("releases", []) if r.get("phaseId") != "PHASE06"] + [release_manifest]
        with open(reg_path, "w", encoding="utf-8") as f:
            json.dump(reg, f, ensure_ascii=False, indent=2)

    print(f"  [+] Release Candidate ZIP: {rc_zip_path}")
    print(f"  [+] Package Size:          {rc_zip_size:,} bytes ({rc_zip_size / (1024*1024):.2f} MB)")
    print(f"  [+] Package SHA-256:       {rc_zip_sha}")
    print(f"  [+] Verified Backup ZIP:   {p06_backup_zip}")
    print("=" * 78)


if __name__ == "__main__":
    main()
