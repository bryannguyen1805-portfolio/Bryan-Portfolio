import re

p = 'update_magspread_pilot_ui.py'
with open(p, 'r', encoding='utf-8') as f:
    code = f.read()

old_branch = '''    elif any(k in hl_l for k in ["chứng khoán", "cổ phiếu", "lên sàn", "gda"]):
        enrich = "Diễn biến niêm yết và tái cấu trúc danh mục phản ánh mức độ sàng lọc khắt khe của dòng vốn đầu tư đối với năng lực quản trị và tính minh bạch tài chính của doanh nghiệp."
    else:
        ctx = sections_dict.get("sectionB_context", "") or sections_dict.get("sectionC_whyItMatters", "")
        if ctx and len(ctx) > 30 and len(ctx) < 160:
            enrich = ctx.strip()
            if not enrich.endswith("."):
                enrich += "."'''

new_branch = '''    elif any(k in hl_l for k in ["cam kết", "1.000 tỷ", "kiến hưng", "khắc phục", "bemes", "thản"]):
        enrich = "Động thái bảo lãnh và cam kết tín dụng quy mô lớn phản ánh nỗ lực tháo gỡ điểm nghẽn pháp lý tài chính, củng cố thanh khoản và bảo toàn quyền lợi dòng tiền của khách hàng tại các dự án bất động sản trọng điểm."
    elif any(k in hl_l for k in ["chứng khoán", "cổ phiếu", "lên sàn", "gda"]):
        enrich = "Diễn biến niêm yết và tái cấu trúc danh mục phản ánh mức độ sàng lọc khắt khe của dòng vốn đầu tư đối với năng lực quản trị và tính minh bạch tài chính của doanh nghiệp."
    else:
        ctx = sections_dict.get("sectionB_context", "") or sections_dict.get("sectionC_whyItMatters", "")
        if ctx:
            sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', ctx.strip()) if len(s.strip()) > 25]
            if sentences:
                cand = sentences[0]
                if not cand.endswith("."):
                    cand += "."
                enrich = cand'''

if old_branch in code:
    code = code.replace(old_branch, new_branch)
    with open(p, 'w', encoding='utf-8') as f:
        f.write(code)
    print('Successfully refined enrich_editorial_standfirst in update_magspread_pilot_ui.py')
else:
    print('Pattern not found!')
