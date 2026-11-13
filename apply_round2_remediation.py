import os
import re
import time

def remediate_html(file_path):
    if not os.path.exists(file_path):
        return
    with open(file_path, 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. Remove #btnOpenWelcomeIntro button completely
    html = re.sub(r'\s*<button id="btnOpenWelcomeIntro"[\s\S]*?<\/button>', '', html)

    # 2. Update #themeToggleBtn to be icon-only (.ms-theme-toggle-btn)
    # Target existing themeToggleBtn
    old_theme_btn_pattern = r'<button id="themeToggleBtn"[^>]*>[\s\S]*?<\/button>'
    new_theme_btn = '''<button id="themeToggleBtn" class="ms-theme-toggle-btn" aria-label="Đổi giao diện Sáng / Tối" title="Đổi giao diện Sáng / Tối">
            <span class="ms-theme-icon" aria-hidden="true">🌙</span>
          </button>'''
    html = re.sub(old_theme_btn_pattern, new_theme_btn, html)

    # 3. Ensure #btnOpenMobileNav has ms-hide-desktop class and proper styling
    # In topbar:
    # If not present, add it; if present, ensure class has ms-hide-desktop
    if 'id="btnOpenMobileNav"' not in html:
        topbar_actions_target = r'(<div style="display:flex; align-items:center;[^"]*">)'
        topbar_actions_replacement = r'\1\n          <button id="btnOpenMobileNav" class="ms-btn ms-btn-outline ms-btn-sm ms-hide-desktop" onclick="openMobileDrawer()" aria-label="Mở danh mục ấn bản" style="font-weight:700; font-size:12px; padding:0 10px;">\n            <span style="margin-right:4px;">☰</span> DANH MỤC\n          </button>'
        html = re.sub(topbar_actions_target, topbar_actions_replacement, html, count=1)

    # 4. Cache busting timestamp
    ts = int(time.time())
    html = re.sub(r'magspread\.css(\?v=\d+)?', f'magspread.css?v={ts}', html)
    html = re.sub(r'magspread\.js(\?v=\d+)?', f'magspread.js?v={ts}', html)
    html = re.sub(r'edition-data\.js(\?v=\d+)?', f'edition-data.js?v={ts}', html)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'Remediated HTML: {file_path}')


def remediate_js(file_path):
    if not os.path.exists(file_path):
        return
    with open(file_path, 'r', encoding='utf-8') as f:
        js = f.read()

    # 1. Update updateThemeIcon to icon-only (🌙 / ☀️)
    pattern_update_theme = r'function updateThemeIcon\(\)\s*\{[\s\S]*?const btn = \$\([\'"]#themeToggleBtn[\'"]\);[\s\S]*?btn\.innerHTML = [^;]*;\s*\}'
    replacement_update_theme = '''function updateThemeIcon() {
  const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
  const btn = $('#themeToggleBtn');
  if (btn) {
    btn.setAttribute('aria-label', isDark ? 'Chuyển sang giao diện Sáng' : 'Chuyển sang giao diện Tối');
    btn.setAttribute('title', isDark ? 'Chuyển sang giao diện Sáng' : 'Chuyển sang giao diện Tối');
    btn.innerHTML = isDark
      ? '<span class="ms-theme-icon" aria-hidden="true">☀️</span>'
      : '<span class="ms-theme-icon" aria-hidden="true">🌙</span>';
  }'''
    js = re.sub(pattern_update_theme, replacement_update_theme, js)

    # 2. Update welcome popup storage logic: check localStorage for first visit
    old_welcome_check = r'function checkWelcomeModalOnLoad\(\)\s*\{[\s\S]*?const shown = sessionStorage\.getItem\([\'"]bryan_fintech_welcome_shown[\'"]\);[\s\S]*?\}\s*\}'
    new_welcome_check = '''function checkWelcomeModalOnLoad() {
  try {
    const shown = localStorage.getItem('bryan_fintech_welcome_shown_v1') || sessionStorage.getItem('bryan_fintech_welcome_shown');
    if (!shown) {
      setTimeout(() => {
        openWelcomeModal();
      }, 500);
    }
  } catch (e) {
    console.warn('[MagSpread] Storage inaccessible:', e);
  }
}'''
    js = re.sub(old_welcome_check, new_welcome_check, js)

    # In closeWelcomeModal, record both localStorage and sessionStorage
    old_close_welcome = r'function closeWelcomeModal\(\)\s*\{[\s\S]*?sessionStorage\.setItem\([\'"]bryan_fintech_welcome_shown[\'"],\s*[\'"]true[\'"]\);[\s\S]*?\}'
    new_close_welcome = '''function closeWelcomeModal() {
  const modal = document.getElementById('welcome-modal-backdrop');
  if (modal) {
    modal.classList.remove('open');
    document.body.style.overflow = '';
  }
  try {
    localStorage.setItem('bryan_fintech_welcome_shown_v1', 'true');
    sessionStorage.setItem('bryan_fintech_welcome_shown', 'true');
  } catch (e) {}
}'''
    js = re.sub(old_close_welcome, new_close_welcome, js)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(js)
    print(f'Remediated JS: {file_path}')


def remediate_css(file_path):
    if not os.path.exists(file_path):
        return
    with open(file_path, 'r', encoding='utf-8') as f:
        css = f.read()

    # Sticky navigation rules and desktop hide rule
    rules_to_inject = '''
/* ─── ROUND 2 POLISH: STICKY NAV, ICON TOGGLE & MOBILE ALIGNMENT ─── */

/* Desktop hide utility */
@media (min-width: 1024px) {
  .ms-hide-desktop {
    display: none !important;
  }
}

/* Icon-only Theme Toggle Button */
.ms-theme-toggle-btn {
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  width: 36px !important;
  height: 36px !important;
  min-width: 36px !important;
  min-height: 36px !important;
  border-radius: 50% !important;
  border: 1px solid var(--ms-border) !important;
  background-color: var(--ms-surface-card) !important;
  color: var(--ms-text-primary) !important;
  cursor: pointer !important;
  transition: all 0.2s ease !important;
  padding: 0 !important;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05) !important;
}

.ms-theme-toggle-btn:hover {
  background-color: var(--ms-border) !important;
  color: var(--ms-primary) !important;
  transform: scale(1.06) !important;
}

.ms-theme-icon {
  font-size: 1.125rem !important;
  line-height: 1 !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
}

/* VnEconomy-Style Sticky Mobile Navigation Bar */
.ms-mobile-quick-tabs {
  position: -webkit-sticky !important;
  position: sticky !important;
  top: 0 !important;
  z-index: 500 !important;
  background-color: var(--ms-surface-base) !important;
  border-bottom: 2px solid var(--ms-primary) !important;
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.08) !important;
}

[data-theme="cream"] .ms-mobile-quick-tabs {
  background-color: #FFFDF7 !important;
  border-bottom: 2px solid #007A70 !important;
}

[data-theme="dark"] .ms-mobile-quick-tabs {
  background-color: #0A1B1A !important;
  border-bottom: 2px solid #007A70 !important;
}

/* Mobile Alignment Fix: Unify All Section Headers to Exact Left Margin */
@media (max-width: 768px) {
  .ms-section-header,
  .ms-page-section > section:first-of-type .ms-section-header,
  #page-market #marketPulse .ms-section-header,
  #page-market #newsDesk .ms-section-header,
  #page-analysis #macroToMicro .ms-section-header,
  #page-analysis #expertLearning .ms-section-header,
  #page-b2b #decisionBrief .ms-section-header,
  #page-b2b #paymentRadar .ms-section-header,
  #page-b2b #decisionWatchlist .ms-section-header,
  #page-archive #archiveSection .ms-section-header {
    display: flex !important;
    flex-direction: column !important;
    align-items: flex-start !important;
    justify-content: flex-start !important;
    text-align: left !important;
    padding-left: 0 !important;
    margin-left: 0 !important;
    padding-bottom: 8px !important;
    margin-bottom: 12px !important;
    border-bottom: 1px solid var(--ms-border) !important;
    min-height: auto !important;
  }

  .ms-section-title-wrap {
    display: flex !important;
    flex-direction: column !important;
    align-items: flex-start !important;
    text-align: left !important;
    padding-left: 0 !important;
    margin-left: 0 !important;
    width: 100% !important;
  }

  .ms-section-kicker,
  .ms-section-heading {
    text-align: left !important;
    align-self: flex-start !important;
    padding-left: 0 !important;
    margin-left: 0 !important;
  }
}
'''
    if 'ROUND 2 POLISH: STICKY NAV, ICON TOGGLE & MOBILE ALIGNMENT' not in css:
        css += '\n' + rules_to_inject

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(css)
    print(f'Remediated CSS: {file_path}')


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
