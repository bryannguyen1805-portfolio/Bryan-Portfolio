targets = [
    'fintech-intelligence/magspread.js',
    'pilot-output/daily-run-package/magspread.js',
    'BRYAN_FINTECH_INTELLIGENCE/03_WORKING_PHASES/PHASE08B_R1.0.0/02_SOURCE_CODE/magspread.js'
]
import re

for p in targets:
    with open(p, 'r', encoding='utf-8') as f:
        c = f.read()
    
    # replace updateThemeIcon body
    pattern = r'function updateThemeIcon\(\)\s*\{[\s\S]*?const btn = \$\([\'"]#themeToggleBtn[\'"]\);[\s\S]*?const logo = \$\([\'"]#headerBryanLogo[\'"]\);'
    replacement = '''function updateThemeIcon() {
  const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
  const btn = $('#themeToggleBtn');
  if (btn) {
    btn.setAttribute('aria-label', isDark ? 'Chuyển sang giao diện Sáng' : 'Chuyển sang giao diện Tối');
    btn.setAttribute('title', isDark ? 'Chuyển sang giao diện Sáng' : 'Chuyển sang giao diện Tối');
    btn.innerHTML = isDark
      ? '<span class="ms-theme-icon" aria-hidden="true">☀️</span>'
      : '<span class="ms-theme-icon" aria-hidden="true">🌙</span>';
  }
  const logo = $('#headerBryanLogo');'''
    
    c = re.sub(pattern, replacement, c)
    with open(p, 'w', encoding='utf-8') as f:
        f.write(c)
    print('Updated theme button icon in:', p)
