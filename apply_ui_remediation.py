import re
import os
import time

def remediate_html(file_path):
    if not os.path.exists(file_path):
        return
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Remove duplicate stray 04. CƠ HỘI B2B button
    pattern_duplicate_b2b = r'(<li class="ms-nav-group" role="none">\s*<button class="ms-nav-tab-btn"[^>]*id="navTabB2B"[^>]*>[\s\S]*?<\/button>\s*<\/li>)\s*<span class="ms-nav-num">04\.<\/span>\s*CƠ HỘI B2B\s*<\/button>\s*<\/li>'
    content = re.sub(pattern_duplicate_b2b, r'\1', content)

    # 2. Add #btnOpenMobileNav in masthead topbar if not already present
    if 'id="btnOpenMobileNav"' not in content:
        topbar_target = '<div style="display:flex; align-items:center; gap:10px;">\n          <button id="btnOpenWelcomeIntro"'
        topbar_replacement = '''<div style="display:flex; align-items:center; gap:8px;">
          <button id="btnOpenMobileNav" class="ms-btn ms-btn-outline ms-btn-sm ms-hide-desktop" onclick="openMobileDrawer()" aria-label="Mở danh mục ấn bản" style="font-weight:700; font-size:12px; padding:0 10px;">
            <span style="margin-right:4px;">☰</span> DANH MỤC
          </button>
          <button id="btnOpenWelcomeIntro"'''
        content = content.replace(topbar_target, topbar_replacement)

    # 3. Add [☰ Danh mục] in ms-mobile-quick-tabs if not present
    if 'ms-quick-tab-drawer' not in content:
        quick_target = '<div class="ms-quick-tabs-scroll">\n      <button class="ms-quick-tab active" data-tab="today"'
        quick_replacement = '''<div class="ms-quick-tabs-scroll">
      <button class="ms-quick-tab ms-quick-tab-drawer" type="button" onclick="openMobileDrawer()" aria-label="Mở danh mục đầy đủ" style="font-weight:700; background:var(--ms-surface-card); color:var(--ms-primary); border:1px solid var(--ms-border);">
        <span style="margin-right:4px;">☰</span> Danh mục
      </button>
      <button class="ms-quick-tab active" data-tab="today"'''
        content = content.replace(quick_target, quick_replacement)

    # 4. Remove #newsCountBadge
    content = re.sub(r'\s*<span class="ms-badge ms-badge-primary" id="newsCountBadge"[^>]*>[\s\S]*?<\/span>', '', content)

    # 5. Classify all right-side notes with ms-section-note ms-hide-mobile
    notes_to_fix = [
        ('4 CHỈ SỐ TRỌNG TÂM · NGUỒN BÁO CHÍ XÁC THỰC 100%',
         '<div class="ms-section-note ms-hide-mobile" style="font-family:var(--font-mono); font-size:0.75rem; color:var(--ms-text-muted);">\n              4 CHỈ SỐ TRỌNG TÂM · NGUỒN BÁO CHÍ XÁC THỰC 100%\n            </div>'),
        ('VĨ MÔ → NGÂN HÀNG → DOANH NGHIỆP → TIÊU DÙNG → THANH TOÁN',
         '<div class="ms-section-note ms-hide-mobile" style="font-family:var(--font-mono); font-size:0.75rem; color:var(--ms-text-muted);">\n              VĨ MÔ → NGÂN HÀNG → DOANH NGHIỆP → TIÊU DÙNG → THANH TOÁN\n            </div>'),
        ('GIẢI THÍCH THUẬT NGỮ &amp; BÀI HỌC THỰC CHIẾN TÀI CHÍNH',
         '<div class="ms-section-note ms-hide-mobile" style="font-family:var(--font-mono); font-size:0.75rem; color:var(--ms-text-muted);">\n              GIẢI THÍCH THUẬT NGỮ &amp; BÀI HỌC THỰC CHIẾN TÀI CHÍNH\n            </div>'),
        ('CƠ HỘI THƯƠNG MẠI CHO DOANH NGHIỆP &amp; GIẢI PHÁP PAYOO',
         '<div class="ms-section-note ms-hide-mobile" style="font-family:var(--font-mono); font-size:0.75rem; color:var(--ms-text-muted);">\n              CƠ HỘI THƯƠNG MẠI CHO DOANH NGHIỆP &amp; GIẢI PHÁP PAYOO\n            </div>'),
        ('4 CHỈ BÁO &amp; NGƯỠNG KÍCH HOẠT HÀNH ĐỘNG TUẦN TỚI',
         '<div class="ms-section-note ms-hide-mobile" style="font-family:var(--font-mono); font-size:0.75rem; color:var(--ms-text-muted);">\n              4 CHỈ BÁO &amp; NGƯỠNG KÍCH HOẠT HÀNH ĐỘNG TUẦN TỚI\n            </div>'),
        ('TRA CỨU LỊCH SỬ ẤN BẢN THEO NGÀY',
         '<div class="ms-section-note ms-hide-mobile" style="font-family:var(--font-mono); font-size:0.75rem; color:var(--ms-text-muted);">\n              TRA CỨU LỊCH SỬ ẤN BẢN THEO NGÀY\n            </div>')
    ]
    for text_kw, replacement in notes_to_fix:
        # replace div containing this text if not already having ms-section-note
        pattern = rf'<div style="font-family:var\(--font-mono\); font-size:0\.75rem; color:var\(--ms-text-muted\);">\s*{re.escape(text_kw)}\s*<\/div>'
        content = re.sub(pattern, replacement, content)

    # Decision Brief badge note
    content = re.sub(
        r'<span class="ms-badge ms-badge-rose"(?!.*ms-section-note)[^>]*>\s*DÀNH RIÊNG CHO PHÁT TRIỂN B2B &amp; PAYOO\s*<\/span>',
        r'<span class="ms-badge ms-badge-rose ms-section-note ms-hide-mobile" style="font-size:10px; letter-spacing:0.06em;">DÀNH RIÊNG CHO PHÁT TRIỂN B2B &amp; PAYOO</span>',
        content
    )

    # 6. Cache busting timestamp
    ts = int(time.time())
    content = re.sub(r'src="\./magspread\.js(\?v=\d+)?"', f'src="./magspread.js?v={ts}"', content)
    content = re.sub(r'src="\./edition-data\.js(\?v=\d+)?"', f'src="./edition-data.js?v={ts}"', content)
    content = re.sub(r'href="\./magspread\.css(\?v=\d+)?"', f'href="./magspread.css?v={ts}"', content)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'Successfully remediated HTML: {file_path}')


def remediate_js(file_path):
    if not os.path.exists(file_path):
        return
    with open(file_path, 'r', encoding='utf-8') as f:
        js = f.read()

    # Suppress countBadge logic
    pattern_count = r'const countBadge = \$\([\'"]#newsCountBadge[\'"]\);[\s\S]*?if \(countBadge\) \{[\s\S]*?\}\s*\}'
    replacement_count = '''const countBadge = $('#newsCountBadge');
  if (countBadge) {
    countBadge.remove();
  }'''
    js = re.sub(pattern_count, replacement_count, js)

    # Dynamic Reflow Zero Orphan logic
    pattern_reflow = r'// DYNAMIC REFLOW BASED ON RESULTS COUNT[\s\S]*?editorialGrid\.style\.gridTemplateColumns = \'\';[\s\S]*?standardGrid\.style\.display = \'none\';\s*\}\s*\}'
    replacement_reflow = '''// DYNAMIC REFLOW: ZERO ORPHAN POLICY FOR CATEGORY AND SEARCH FILTERS
  if (filtered.length === 1) {
    if (editorialGrid) {
      editorialGrid.style.display = 'grid';
      editorialGrid.style.gridTemplateColumns = '1fr';
    }
    if (subContainer) subContainer.style.display = 'none';
    if (standardGrid) standardGrid.style.display = 'none';
    if (leadContainer) {
      leadContainer.innerHTML = renderNewsCardHtml(filtered[0], true);
    }
  } else if (filtered.length % 2 === 0) {
    // When results count is even (e.g. 2, 4, 10):
    // Render balanced 2-column grid in standardGrid with 0 orphan cards!
    if (editorialGrid) editorialGrid.style.display = 'none';
    if (standardGrid) {
      standardGrid.style.display = 'grid';
      standardGrid.innerHTML = filtered.map(item => renderStandardNewsCardHtml(item)).join('');
    }
  } else {
    // When results count is odd (e.g. 3, 5, 7, 9, 25):
    // Editorial grid takes 3 items (1 lead + 2 subfeatures);
    // remaining is (odd - 3) = EVEN, which fills 2-column standardGrid with 0 orphan cards!
    if (editorialGrid) {
      editorialGrid.style.display = 'grid';
      editorialGrid.style.gridTemplateColumns = '';
    }
    if (leadContainer) {
      leadContainer.innerHTML = renderNewsCardHtml(filtered[0], true);
    }
    if (subContainer) {
      subContainer.style.display = 'flex';
      const subFeatures = filtered.slice(1, 3);
      subContainer.innerHTML = subFeatures.map(item => renderSubfeatureCardHtml(item)).join('');
    }
    if (standardGrid) {
      const remaining = filtered.slice(3);
      if (remaining.length > 0) {
        standardGrid.style.display = 'grid';
        standardGrid.innerHTML = remaining.map(item => renderStandardNewsCardHtml(item)).join('');
      } else {
        standardGrid.style.display = 'none';
      }
    }
  }'''
    js = re.sub(pattern_reflow, replacement_reflow, js)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(js)
    print(f'Successfully remediated JS: {file_path}')


def remediate_css(file_path):
    if not os.path.exists(file_path):
        return
    with open(file_path, 'r', encoding='utf-8') as f:
        css = f.read()

    # Make sure .ms-section-note and right side labels are hidden on mobile
    # and mobile section header is clean and spacious
    mobile_additions = '''
/* ─── MOBILE UI/UX POLISH & CLEAN SECTION HEADERS ─── */
@media (max-width: 768px) {
  .ms-section-note,
  .ms-hide-mobile,
  #newsCountBadge,
  .ms-section-header > div:not(.ms-section-title-wrap),
  .ms-section-header > span.ms-badge {
    display: none !important;
  }

  .ms-section-header {
    display: flex !important;
    flex-direction: column !important;
    align-items: flex-start !important;
    gap: 4px !important;
    padding-bottom: 8px !important;
    margin-bottom: 12px !important;
    border-bottom: 1px solid var(--ms-border) !important;
  }

  .ms-section-kicker {
    font-size: 0.6875rem !important;
    letter-spacing: 0.08em !important;
  }

  .ms-section-heading {
    font-size: 1.15rem !important;
    line-height: 1.3 !important;
    margin: 0 !important;
  }

  /* Filter strip on mobile: full width clean layout */
  .ms-filter-strip {
    display: flex !important;
    flex-direction: column !important;
    align-items: stretch !important;
    gap: 10px !important;
    padding: 10px 12px !important;
    background-color: var(--ms-surface-card) !important;
    border-radius: 4px !important;
    margin-bottom: 14px !important;
  }

  .ms-category-buttons {
    width: 100% !important;
    display: flex !important;
    flex-wrap: nowrap !important;
    overflow-x: auto !important;
    -webkit-overflow-scrolling: touch !important;
    gap: 6px !important;
    padding: 2px 0 6px 0 !important;
    scrollbar-width: none !important;
  }

  .ms-category-buttons::-webkit-scrollbar {
    display: none !important;
  }

  .ms-cat-btn {
    flex-shrink: 0 !important;
    font-size: 0.75rem !important;
    padding: 6px 12px !important;
    white-space: nowrap !important;
    height: 32px !important;
  }

  .ms-search-input-wrap {
    width: 100% !important;
    min-width: 0 !important;
    flex: 1 1 auto !important;
  }

  .ms-search-input {
    width: 100% !important;
    box-sizing: border-box !important;
    padding: 8px 12px !important;
  }
}
'''
    if 'MOBILE UI/UX POLISH & CLEAN SECTION HEADERS' not in css:
        css += '\n' + mobile_additions

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(css)
    print(f'Successfully remediated CSS: {file_path}')


if __name__ == '__main__':
    targets = [
        'fintech-intelligence',
        'pilot-output/daily-run-package',
        'BRYAN_FINTECH_INTELLIGENCE/03_WORKING_PHASES/PHASE08B_R1.0.0/02_SOURCE_CODE'
    ]
    for base in targets:
        remediate_html(os.path.join(base, 'index.html'))
        remediate_js(os.path.join(base, 'magspread.js'))
        remediate_css(os.path.join(base, 'magspread.css'))
