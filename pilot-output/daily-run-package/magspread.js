/**
 * Bryan FinTech Market Intelligence — MagSpread Editorial Portal Engine
 * Strict MagSpread Design System Implementation
 */

'use strict';

let EDITION_DATA = null;
let currentCategoryFilter = 'ALL';
let currentSearchTerm = '';

// DOM Helpers
const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => document.querySelectorAll(sel);

function escapeHtml(str) {
  if (str === null || str === undefined) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

// ─── THEME CONTROLLER ───
function initTheme() {
  const saved = localStorage.getItem('ms-theme');
  if (saved === 'dark' || (!saved && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
    document.documentElement.setAttribute('data-theme', 'dark');
  } else {
    document.documentElement.setAttribute('data-theme', 'light');
  }
  updateThemeIcon();
}

function toggleTheme() {
  const current = document.documentElement.getAttribute('data-theme');
  const next = current === 'dark' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', next);
  localStorage.setItem('ms-theme', next);
  updateThemeIcon();
}

function updateThemeIcon() {
  const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
  const btn = $('#themeToggleBtn');
  if (btn) {
    btn.innerHTML = isDark
      ? '<span style="font-size:14px;">☼ BẬT BẢN SÁNG (CREAM)</span>'
      : '<span style="font-size:14px;">☽ BẬT BẢN TỐI (EDITORIAL)</span>';
  }
  // Sync Bryan Portfolio Logo correctly
  const logo = $('#headerBryanLogo');
  const footerLogo = $('#footerBryanLogo');
  const targetLogo = isDark ? '../bryan-logo-2.webp' : '../bryan-logo-light.webp';
  if (logo) logo.src = targetLogo;
  if (footerLogo) footerLogo.src = targetLogo;
}

// ─── DRAWER CONTROLLER ───
function openDrawer(title, htmlContent) {
  const drawer = $('#sideDrawer');
  const backdrop = $('#drawerBackdrop');
  const titleEl = $('#drawerTitle');
  const contentEl = $('#drawerContent');

  if (!drawer || !backdrop) return;
  titleEl.textContent = title;
  contentEl.innerHTML = htmlContent;

  backdrop.classList.add('open');
  drawer.classList.add('open');
  document.body.style.overflow = 'hidden';
}

function closeDrawer() {
  const drawer = $('#sideDrawer');
  const backdrop = $('#drawerBackdrop');
  if (drawer) drawer.classList.remove('open');
  if (backdrop) backdrop.classList.remove('open');
  document.body.style.overflow = '';
}

// ─── DATA LOADING ───
async function loadEditionData() {
  const isFileProtocol = window.location.protocol === 'file:';

  // 1. file:// environment: use existing synchronized JS mirror directly
  if (isFileProtocol) {
    if (window.EDITION_DATA && typeof window.EDITION_DATA === 'object') {
      console.log('[MagSpread] Chế độ file://: Nạp thành công window.EDITION_DATA nội tuyến.');
      EDITION_DATA = window.EDITION_DATA;
      renderAllSections();
      return;
    } else {
      console.error('[MagSpread] Chế độ file://: Không tìm thấy window.EDITION_DATA.');
      const mc = document.getElementById('mainContent');
      if (mc) {
        mc.innerHTML = `
          <div class="ms-container" style="padding:48px 0; text-align:center;">
            <h2 style="color:var(--ms-error);">Không thể tải dữ liệu ấn bản (file://)</h2>
            <p style="margin-top:12px;">Vui lòng kiểm tra file edition-data.js trong thư mục pilot-output/.</p>
          </div>
        `;
      }
      return;
    }
  }

  // 2. HTTP/HTTPS environment: fetch canonical edition-data.json
  try {
    const res = await fetch('./edition-data.json?v=' + Date.now());
    if (!res.ok) {
      throw new Error(`HTTP ${res.status}: ${res.statusText}`);
    }
    const freshData = await res.json();

    // Validate required editorial and Archive structure before updating runtime state
    if (!freshData || typeof freshData !== 'object' || !freshData.editorialSections || !freshData.editorialSections.sec09_archive) {
      throw new Error('Dữ liệu edition-data.json không đạt tiêu chuẩn schema biên tập hoặc thiếu sec09_archive.');
    }

    // Replace runtime state only after successful validation
    EDITION_DATA = freshData;
    window.EDITION_DATA = freshData;
    console.log('[MagSpread] Nạp và thẩm định thành công canonical edition-data.json.');
    renderAllSections();
  } catch (err) {
    console.warn('[MagSpread] Không thể tải hoặc thẩm định edition-data.json qua HTTP, fallback sang window.EDITION_DATA:', err.message);
    if (window.EDITION_DATA && typeof window.EDITION_DATA === 'object') {
      EDITION_DATA = window.EDITION_DATA;
      renderAllSections();
    } else {
      const mc = document.getElementById('mainContent');
      if (mc) {
        mc.innerHTML = `
          <div class="ms-container" style="padding:48px 0; text-align:center;">
            <h2 style="color:var(--ms-error);">Không thể tải dữ liệu ấn bản</h2>
            <p style="margin-top:12px;">Vui lòng kiểm tra file edition-data.json hoặc edition-data.js trong thư mục pilot-output/.</p>
          </div>
        `;
      }
    }
  }
}

// ─── RENDER ALL SECTIONS ───
function renderAllSections() {
  if (!EDITION_DATA) return;

  renderMasthead();
  renderCoverStory();
  renderMarketPulse();
  renderDecisionBrief();
  renderNewsDesk();
  // renderConnectTheDots();
  renderMacroToMicro();
  renderPaymentRadar();
  renderExpertLearning();
  renderWatchlist();
  renderArchive();
  initFintechTabs();
}

// ─── SECTION 01: MASTHEAD ───
function renderMasthead() {
  const dateEl = $('#mastheadDate');
  const editionBadge = $('#mastheadEditionBadge');
  const metaBar = $('#mastheadMetaBar');

  if (dateEl) dateEl.textContent = (EDITION_DATA.dayOfWeek ? (EDITION_DATA.dayOfWeek.toUpperCase() + ', ') : '') + (EDITION_DATA.editionDate || '11/11/2026');
  if (editionBadge) {
    const isPreviewOnly = EDITION_DATA.publicationGateStatus?.status === 'FAIL_SHORTFALL_24H_PREVIEW_ONLY' || EDITION_DATA.publicationGateStatus?.gateStatus === 'FAIL_SHORTFALL_24H_PREVIEW_ONLY';
    const badgeLabel = EDITION_DATA.publicationGateStatus?.publicBadgeLabel || 'PREVIEW — CHƯA XUẤT BẢN';
    const badgeSuffix = isPreviewOnly ? ` · ${badgeLabel}` : '';
    editionBadge.textContent = (EDITION_DATA.editionNumber || 'ẤN BẢN SỐ 24') + badgeSuffix;
    if (isPreviewOnly) {
      editionBadge.className = 'ms-badge ms-badge-warning';
    }
  }

  if (metaBar) {
    metaBar.style.display = 'none';
  }
}

// ─── SECTION 02: COVER STORY / CORE THESIS ───
function renderCoverStory() {
  const ct = EDITION_DATA.editorialSections?.sec02_coverStory || EDITION_DATA.editorialSections?.coreThesis;
  if (!ct) return;

  const headlineEl = $('#coverHeadline');
  const subheadlineEl = $('#coverSubheadline');
  const summaryEl = $('#coverSummary');
  const quoteEl = $('#coverPullQuote');
  const implicationEl = $('#coverImplication');
  const coverDateEl = $('#coverDate');

  if (coverDateEl) coverDateEl.textContent = 'Phiên ngày ' + (EDITION_DATA.editionDate || '12/11/2026');

  const lead = ct.leadArticle || {};
  const headline = lead.headline || ct.editorialHeadline || 'Sự kiện điều hành trọng tâm của phiên';
  const sourceName = lead.sourceName || 'Báo Thanh Niên';
  const publishedAt = lead.publishedAt || '';
  const sourceUrl = lead.sourceUrl || '#';
  const summary = lead.summary || ct.executiveSummary || '';

  if (headlineEl) headlineEl.textContent = headline;

  if (subheadlineEl) {
    const cleanPubTime = publishedAt.split(' | ')[0].trim();
    subheadlineEl.innerHTML = `
      <div style="display:flex; align-items:center; gap:8px; flex-wrap:wrap; margin:2px 0 4px 0; font-size:0.8125rem;">
        <span style="color:var(--ms-text-muted);">Nguồn xác minh: <strong style="color:var(--ms-text-primary);">${escapeHtml(sourceName)}</strong> ${cleanPubTime ? `(${escapeHtml(cleanPubTime)})` : ''}</span>
        <a href="${escapeHtml(sourceUrl)}" target="_blank" rel="noopener noreferrer" class="ms-source-link" style="color:var(--ms-primary); font-weight:700; text-decoration:none; display:inline-flex; align-items:center; gap:3px;">
          <span>Đọc bài báo gốc</span>
          <span style="font-size:0.75rem;">↗</span>
        </a>
      </div>
    `;
  }

  if (summaryEl) {
    summaryEl.innerHTML = `
      <div style="font-size:0.90625rem; line-height:1.65; color:var(--ms-text-primary); margin:0; text-align:justify;">
        ${escapeHtml(summary)}
      </div>
    `;
  }

  if (quoteEl) {
    quoteEl.innerHTML = `
      <div class="ms-quote-text">“${escapeHtml(ct.editorialPullQuote || '')}”</div>
      ${ct.editorialSynthesis ? `<p style="font-size:0.8125rem; line-height:1.55; margin:8px 0 0 0; color:var(--ms-text-secondary); text-align:justify;">${escapeHtml(ct.editorialSynthesis)}</p>` : ''}
      <div class="ms-quote-attribution" style="margin-top:8px; font-weight:700; font-size:0.6875rem; letter-spacing:0.04em;">■ ĐÚC KẾT BIÊN TẬP TỪ 25 BẢN TIN TRONG PHIÊN · BRYAN FINTECH INTELLIGENCE</div>
    `;
  }

  if (implicationEl) {
    implicationEl.innerHTML = `
      <div class="ms-implication-card">
        <div class="ms-implication-grid">
          <div class="ms-implication-col ms-implication-macro">
            <div class="ms-implication-header" style="color:var(--ms-secondary);">
              <span style="display:inline-block; width:6px; height:6px; border-radius:50%; background:var(--ms-secondary); flex-shrink:0;"></span>
              <span>TÁC ĐỘNG THỊ TRƯỜNG VĨ MÔ</span>
            </div>
            <p class="ms-implication-text">${escapeHtml(ct.marketImpact || ct.whyItMatters || '')}</p>
          </div>
          <div class="ms-implication-col ms-implication-fintech">
            <div class="ms-implication-header" style="color:var(--ms-primary);">
              <span style="display:inline-block; width:6px; height:6px; border-radius:50%; background:var(--ms-primary); flex-shrink:0;"></span>
              <span>GÓC NHÌN FINTECH &amp; CƠ HỘI PAYOO</span>
            </div>
            <p class="ms-implication-text">${escapeHtml(ct.fintechLensAction || ct.keyMarketImplication || '')}</p>
          </div>
        </div>
        <div class="ms-implication-watchpoint">
          <strong>Điều cần theo dõi:</strong> ${escapeHtml(ct.monitoringWatchpoint || 'Theo dõi sát diễn biến điều hành các phiên tiếp theo.')}
        </div>
      </div>
    `;
  }
}


// ─── SECTION 03: COMPACT MAGSPREAD MARKET PULSE ───
function renderMarketPulse() {
  const grid = $('#marketPulseGrid') || $('#pulseTier1Grid');
  const metrics = EDITION_DATA.marketPulseSnapshot || EDITION_DATA.metrics || [];

  if (grid) {
    grid.innerHTML = metrics.slice(0, 4).map(renderPulseCard).join('');
  }
}

function renderPulseCard(m) {
  const st = m.status || 'neutral';
  const badgeText = m.verificationStatus === '72H_NOT_VERIFIED'
    ? 'CHƯA XÁC MINH 72H'
    : (m.verificationStatus === 'SCOPE_SEPARATED_VERIFIED' ? 'SCOPE_VERIFIED' : 'VERIFIED');
  const badgeClass = m.verificationStatus === '72H_NOT_VERIFIED' ? 'ms-badge-warning' : (st === 'positive' ? 'ms-badge-success' : (st === 'negative' ? 'ms-badge-error' : 'ms-badge-primary'));

  const shortContext = m.referenceValue ? m.referenceValue : (m.note || '');

  return `
    <article class="ms-pulse-card status-${escapeHtml(st)}" onclick="openPulseDetail('${escapeHtml(m.key)}')">
      <div>
        <div class="ms-pulse-top">
          <span class="ms-pulse-label">${escapeHtml(m.shortLabel || m.label)}</span>
          <span class="ms-badge ${badgeClass}" style="font-size:9px; padding:2px 6px;">${escapeHtml(badgeText)}</span>
        </div>
        <div class="ms-pulse-value">${escapeHtml(m.value)}</div>
        <div class="ms-pulse-asof">Phiên: ${escapeHtml(m.asOf)}</div>
        <div class="ms-pulse-context">${escapeHtml(shortContext)}</div>
      </div>
      <div class="ms-pulse-open-btn">
        <span>Chi tiết & Nguồn</span>
        <span>→</span>
      </div>
    </article>
  `;
}

function openPulseDetail(key) {
  const metrics = EDITION_DATA.marketPulseSnapshot || EDITION_DATA.metrics || [];
  const m = metrics.find(x => x.key === key);
  if (!m) return;

  const gates = m.qualityGates || {};
  const items = (m.detailsExpandable && m.detailsExpandable.items) ? m.detailsExpandable.items : [];

  const html = `
    <div style="font-size:0.9375rem; line-height:1.7;">
      <!-- Header banner -->
      <div style="padding-bottom:16px; margin-bottom:18px; border-bottom:2px solid var(--ms-border);">
        <div style="display:flex; justify-content:space-between; align-items:center;">
          <span class="ms-badge ms-badge-primary" style="font-size:0.75rem;">THẺ ${escapeHtml(m.cardNumber || '')} · ${escapeHtml(m.tierGroup || 'MARKET PULSE')}</span>
          <span class="ms-badge ${m.verificationStatus === '72H_NOT_VERIFIED' ? 'ms-badge-warning' : 'ms-badge-success'}">
            ${escapeHtml(m.verificationStatus || 'VERIFIED')}
          </span>
        </div>
        <h3 style="font-family:var(--font-headline); font-size:1.5rem; font-weight:800; color:var(--ms-primary); margin:8px 0 4px 0;">
          ${escapeHtml(m.label)}
        </h3>
        <div style="font-size:2rem; font-weight:900; color:var(--ms-text-primary); font-family:var(--font-mono); letter-spacing:-0.02em;">
          ${escapeHtml(m.value)}
        </div>
        ${m.change ? `
          <div style="font-size:0.875rem; color:var(--ms-text-muted); font-weight:600; margin-top:2px;">
            Biến động: <span style="color:var(--ms-primary);">${escapeHtml(m.change)}</span>
          </div>
        ` : ''}
      </div>

      ${m.verificationStatus === '72H_NOT_VERIFIED' ? `
        <div style="background-color:rgba(217, 119, 6, 0.1); border:1px solid #d97706; padding:12px 16px; border-radius:4px; margin-bottom:18px;">
          <div style="font-weight:700; color:#d97706; margin-bottom:4px;">⚠️ THÔNG BÁO KIỂM ĐỊNH FRESHNESS 72H</div>
          <div style="font-size:0.875rem; line-height:1.6;">
            Số liệu phiên quan sát chưa có công bố chính thức kèm timestamp đối soát trong vòng 72 giờ qua. Để đảm bảo tính trung thực báo chí tài chính, giá trị hiển thị là <strong>Chưa xác minh trong 72h</strong>.
            <br>Giá trị tham khảo gần nhất: <strong>${escapeHtml(m.referenceValue || 'Kỳ quan sát trước')}</strong>.
          </div>
        </div>
      ` : ''}

      ${m.key === 'vietqrVolume' ? `
        <div style="background-color:rgba(14, 116, 144, 0.1); border:1px solid #0e7490; padding:12px 16px; border-radius:4px; margin-bottom:18px;">
          <div style="font-weight:700; color:#0e7490; margin-bottom:4px;">📌 LƯU Ý PHẠM VI DỮ LIỆU (SCOPE SEPARATION)</div>
          <div style="font-size:0.875rem; line-height:1.6;">
            Mức tăng trưởng <strong>${escapeHtml(m.value)}</strong> là số liệu áp dụng riêng cho luồng khách du lịch quốc tế và các điểm bán chấp nhận <strong>VietQR Global (Inbound & Cross-border)</strong>. Tuyệt đối không đồng nhất với tổng sản lượng giao dịch toàn hệ thống NAPAS.
          </div>
        </div>
      ` : ''}

      <!-- 11 Standardized Detailed Fields -->
      <div style="display:flex; flex-direction:column; gap:16px;">
        <!-- Field 01 to 05: Core Metadata -->
        <div style="background-color:var(--ms-surface-alt); padding:16px; border:1px solid var(--ms-border); border-radius:4px;">
          <div style="font-family:var(--font-mono); font-size:0.75rem; text-transform:uppercase; color:var(--ms-primary); font-weight:700; margin-bottom:10px;">
            THÔNG TIN QUAN SÁT & CHU KỲ (FIELDS 01–05)
          </div>
          <div style="display:grid; grid-template-columns:1fr 1fr; gap:8px; font-size:0.875rem;">
            <div><strong>Tên chỉ số:</strong> ${escapeHtml(m.label)}</div>
            <div><strong>Mã tham chiếu:</strong> ${escapeHtml(m.key)}</div>
            <div><strong>Ngày quan sát:</strong> ${escapeHtml(m.observationAt || m.asOf)}</div>
            <div><strong>Ngày công bố:</strong> ${escapeHtml(m.publishedAt || m.asOf)}</div>
            <div style="grid-column:1/-1;"><strong>Kỳ dữ liệu:</strong> ${escapeHtml(m.dataPeriod || '')}</div>
            ${m.referenceValue ? `<div style="grid-column:1/-1;"><strong>Giá trị tham chiếu:</strong> ${escapeHtml(m.referenceValue)}</div>` : ''}
          </div>
        </div>

        <!-- Field 06 & 07: Sources & Canonical Provenance -->
        <div style="background-color:var(--ms-surface-alt); padding:16px; border:1px solid var(--ms-border); border-radius:4px;">
          <div style="font-family:var(--font-mono); font-size:0.75rem; text-transform:uppercase; color:var(--ms-primary); font-weight:700; margin-bottom:8px;">
            NGUỒN GỐC & ĐƯỜNG DẪN XÁC MINH (FIELDS 06–07)
          </div>
          <div style="font-size:0.875rem; margin-bottom:8px;">
            <strong>Cơ quan công bố:</strong> ${escapeHtml(m.sourceName || 'Ngân hàng Nhà nước / Cơ quan thống kê')}
          </div>
          <div style="display:flex; flex-wrap:wrap; gap:8px; margin-top:8px;">
            <a href="${escapeHtml(m.sourceUrl)}" target="_blank" rel="noopener" class="ms-btn ms-btn-primary ms-btn-sm">
              Mở link bài báo gốc ↗
            </a>
            ${(m.secondarySourceUrls || []).filter(u => u && u.startsWith('http') && u.length > 25 && !u.endsWith('.vn') && !u.endsWith('.com')).map((secUrl, idx) => `
              <a href="${escapeHtml(secUrl)}" target="_blank" rel="noopener" class="ms-btn ms-btn-ghost ms-btn-sm">
                Nguồn đối soát #${idx + 1} ↗
              </a>
            `).join('')}
          </div>
        </div>

        <!-- Field 08 & 09: Methodology & Details -->
        <div style="background-color:var(--ms-surface-alt); padding:16px; border:1px solid var(--ms-border); border-radius:4px;">
          <div style="font-family:var(--font-mono); font-size:0.75rem; text-transform:uppercase; color:var(--ms-primary); font-weight:700; margin-bottom:8px;">
            Ý NGHĨA CHỈ SỐ & CÔNG THỨC QUY CHUẨN (FIELDS 08–09)
          </div>
          <div style="font-size:0.875rem; margin-bottom:8px; font-weight:600;">
            ${escapeHtml(m.detailsExpandable?.summaryTitle || 'Thuyết minh phương pháp luận & cơ sở tính toán:')}
          </div>
          <ul style="padding-left:18px; margin:0; font-size:0.875rem; display:flex; flex-direction:column; gap:6px;">
            ${items.map(it => `<li>${escapeHtml(it)}</li>`).join('')}
          </ul>
        </div>

        <!-- Field 10: Financial Interpretation & Impact -->
        <div style="background-color:var(--ms-surface-alt); padding:16px; border:1px solid var(--ms-border); border-radius:4px;">
          <div style="font-family:var(--font-mono); font-size:0.75rem; text-transform:uppercase; color:var(--ms-primary); font-weight:700; margin-bottom:8px;">
            DIỄN GIẢI TÀI CHÍNH & TÁC ĐỘNG THỰC TẾ (FIELD 10)
          </div>
          <p style="font-size:0.875rem; line-height:1.6; margin:0;">
            ${escapeHtml(m.financialInterpretation || m.implication || m.statusReason || m.note || 'Chỉ số phản ánh trạng thái cân bằng vĩ mô và tính thanh khoản của hệ thống.')}
          </p>
        </div>
      </div>
    </div>
  `;

  openDrawer(m.label, html);
}


// ─── SECTION 04: THE NEWS DESK ───
function renderNewsDesk() {
  const newsList = EDITION_DATA.eligibleNewsList || [];
  
  // Filter
  let filtered = newsList.filter(item => {
    const matchCat = currentCategoryFilter === 'ALL' || item.category === currentCategoryFilter;
    const matchSearch = !currentSearchTerm || 
      (item.title && item.title.toLowerCase().includes(currentSearchTerm.toLowerCase())) ||
      (item.summary && item.summary.toLowerCase().includes(currentSearchTerm.toLowerCase())) ||
      (item.author && item.author.toLowerCase().includes(currentSearchTerm.toLowerCase()));
    return matchCat && matchSearch;
  });

  // Strict sorting: 0–24h first, then 24–48h
  filtered.sort((a, b) => {
    const rankA = a.strictCombinedTimeWindow === '0–24h' ? 1 : 2;
    const rankB = b.strictCombinedTimeWindow === '0–24h' ? 1 : 2;
    if (rankA !== rankB) return rankA - rankB;
    return (b.originalSourcePublishedAt || '').localeCompare(a.originalSourcePublishedAt || '');
  });

  const leadContainer = $('#newsLeadContainer');
  const subContainer = $('#newsSubContainer');
  const editorialGrid = $('.ms-news-editorial-grid');
  const standardGrid = $('#newsStandardGrid');
  const countBadge = $('#newsCountBadge');

  if (countBadge) countBadge.textContent = `${filtered.length} BÀI ĐỦ ĐIỀU KIỆN (ĐÃ LOẠI REJECTED)`;

  if (filtered.length === 0) {
    if (editorialGrid) editorialGrid.style.display = 'none';
    if (standardGrid) {
      standardGrid.style.display = 'block';
      standardGrid.innerHTML = `
        <div style="padding:36px; text-align:center; background-color:var(--ms-surface-card); border:1px solid var(--ms-border); border-radius:4px;">
          <p style="margin:0; font-size:0.9375rem; color:var(--ms-text-secondary);">Không tìm thấy bài báo nào phù hợp với bộ lọc hiện tại.</p>
        </div>
      `;
    }
    return;
  }

  if (editorialGrid) editorialGrid.style.display = 'grid';

  // DYNAMIC REFLOW BASED ON RESULTS COUNT
  if (filtered.length === 1) {
    editorialGrid.style.gridTemplateColumns = '1fr';
    if (subContainer) subContainer.style.display = 'none';
    if (standardGrid) standardGrid.style.display = 'none';
    if (leadContainer) {
      leadContainer.innerHTML = renderNewsCardHtml(filtered[0], true);
    }
  } else if (filtered.length === 2) {
    editorialGrid.style.gridTemplateColumns = '1fr 1fr';
    if (subContainer) {
      subContainer.style.display = 'block';
      subContainer.innerHTML = renderSubfeatureCardHtml(filtered[1]);
    }
    if (standardGrid) standardGrid.style.display = 'none';
    if (leadContainer) {
      leadContainer.innerHTML = renderNewsCardHtml(filtered[0], true);
    }
  } else {
    editorialGrid.style.gridTemplateColumns = '';
    if (subContainer) subContainer.style.display = 'flex';
    if (leadContainer) {
      leadContainer.innerHTML = renderNewsCardHtml(filtered[0], true);
    }
    if (subContainer) {
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
  }
}

function renderNewsCardHtml(lead, isLead) {
  const cleanTime = (lead.publisherPublishedAt || lead.publicationTimestamp || '').split(' | ')[0].trim();
  return `
    <article class="ms-news-lead-story">
      <div>
        <div class="ms-lead-meta">
          <span class="ms-badge ms-badge-rose">${escapeHtml(lead.category || 'Tin tức')}</span>
          <span class="ms-badge ${lead.strictCombinedTimeWindow === '0–24h' ? 'ms-badge-success' : 'ms-badge-neutral'}">
            [${escapeHtml(lead.strictCombinedTimeWindow || '24h')}]
          </span>
          ${cleanTime ? `<span class="ms-xs" style="color:var(--ms-text-muted); font-family:var(--font-mono);">${escapeHtml(cleanTime)}</span>` : ''}
        </div>
        <h2 class="ms-lead-title" onclick="openArticleReader('${escapeHtml(lead.eventId)}')">
          ${escapeHtml(lead.pageTitle || lead.title)}
        </h2>
        <p class="ms-lead-summary">${escapeHtml(lead.summary || lead.supportingQuote || '')}</p>
        ${lead.supportingQuote ? `
          <div class="ms-lead-quote">
            “${escapeHtml(lead.supportingQuote)}”
          </div>
        ` : ''}
      </div>
      <div class="ms-news-card-footer">
        <span>Nguồn: <strong>${escapeHtml(lead.author || lead.originalSourceName || 'Báo chí')}</strong></span>
        <div style="display:flex; gap:10px;">
          <button class="ms-btn ms-btn-primary ms-btn-sm" onclick="openArticleReader('${escapeHtml(lead.eventId)}')">
            Đọc phân tích chuyên sâu
          </button>
          <a href="${escapeHtml(lead.canonicalUrl)}" target="_blank" rel="noopener" class="ms-source-link" style="align-self:center;">
            Bài gốc ↗
          </a>
        </div>
      </div>
    </article>
  `;
}

function renderSubfeatureCardHtml(item) {
  return `
    <article class="ms-subfeature-card">
      <div>
        <div style="display:flex; align-items:center; gap:6px; margin-bottom:6px;">
          <span class="ms-badge ms-badge-primary" style="font-size:9px;">${escapeHtml(item.category || 'Tài chính')}</span>
          <span class="ms-badge ${item.strictCombinedTimeWindow === '0–24h' ? 'ms-badge-success' : 'ms-badge-neutral'}" style="font-size:9px;">
            [${escapeHtml(item.strictCombinedTimeWindow || '24h')}]
          </span>
        </div>
        <h3 class="ms-subfeature-title" onclick="openArticleReader('${escapeHtml(item.eventId)}')">
          ${escapeHtml(item.pageTitle || item.title)}
        </h3>
        <p style="font-size:0.875rem; line-height:1.55; color:var(--ms-text-secondary); margin-bottom:8px;">
          ${escapeHtml((item.summary || item.supportingQuote || '').slice(0, 160))}...
        </p>
      </div>
      <div class="ms-news-card-footer">
        <span style="font-size:0.75rem;">${escapeHtml(item.author || item.originalSourceName || 'Báo chí')}</span>
        <div style="display:flex; gap:8px;">
          <button class="ms-btn ms-btn-ghost ms-btn-sm" onclick="openArticleReader('${escapeHtml(item.eventId)}')">
            Phân tích
          </button>
          <a href="${escapeHtml(item.canonicalUrl)}" target="_blank" rel="noopener" class="ms-source-link" style="align-self:center; font-size:0.75rem;">
            Bài gốc ↗
          </a>
        </div>
      </div>
    </article>
  `;
}

function renderStandardNewsCardHtml(item) {
  return `
    <article class="ms-news-card">
      <div>
        <div class="ms-news-card-meta">
          <div style="display:flex; align-items:center; gap:4px;">
            <span class="ms-badge ms-badge-neutral">${escapeHtml(item.category || 'FinTech')}</span>
            <span class="ms-badge ${item.strictCombinedTimeWindow === '0–24h' ? 'ms-badge-success' : 'ms-badge-neutral'}">
              [${escapeHtml(item.strictCombinedTimeWindow || '24h')}]
            </span>
          </div>
        </div>
        <h3 class="ms-news-card-title" onclick="openArticleReader('${escapeHtml(item.eventId)}')">
          ${escapeHtml(item.pageTitle || item.title)}
        </h3>
        <p class="ms-news-card-summary">${escapeHtml((item.summary || item.supportingQuote || '').slice(0, 150))}...</p>
      </div>
      <div class="ms-news-card-footer">
        <span>${escapeHtml(item.author || item.originalSourceName || 'Báo chí')}</span>
        <div style="display:flex; gap:8px;">
          <button class="ms-btn ms-btn-ghost ms-btn-sm" onclick="openArticleReader('${escapeHtml(item.eventId)}')">
            Phân tích
          </button>
          <a href="${escapeHtml(item.canonicalUrl)}" target="_blank" rel="noopener" class="ms-source-link" style="align-self:center;">
            Bài gốc ↗
          </a>
        </div>
      </div>
    </article>
  `;
}


function openArticleReader(eventId) {
  const item = (EDITION_DATA.eligibleNewsList || []).find(x => x.eventId === eventId);
  if (!item) return;

  const pubDate = (item.publisherPublishedAt || item.originalSourcePublishedAt || item.publicationTimestamp || '').split(' | ')[0].trim();

  const html = `
    <article style="font-size:1rem; line-height:1.75;">
      <!-- Article Header -->
      <div style="margin-bottom:16px;">
        <span class="ms-badge ms-badge-rose">${escapeHtml(item.category || 'Tin tức')}</span>
        <span class="ms-badge ${item.strictCombinedTimeWindow === '0–24h' ? 'ms-badge-success' : 'ms-badge-neutral'}">
          [${escapeHtml(item.strictCombinedTimeWindow || '0–24h')}]
        </span>
      </div>

      <h2 style="font-family:var(--font-headline); font-size:1.875rem; line-height:1.25; color:var(--ms-primary); margin-bottom:12px;">
        ${escapeHtml(item.pageTitle || item.title)}
      </h2>

      <div style="font-family:var(--font-mono); font-size:0.8125rem; color:var(--ms-text-muted); padding-bottom:12px; margin-bottom:18px; border-bottom:1px solid var(--ms-border);">
        Xuất bản: ${escapeHtml(pubDate)} | Nguồn: ${escapeHtml(item.originalSourceName || item.author || 'Báo chí')}
      </div>

      ${item.supportingQuote ? `
        <blockquote style="font-family:var(--font-headline); font-style:italic; font-size:1.0625rem; padding:12px 18px; background-color:var(--ms-surface-alt); border-left:3px solid var(--ms-secondary); margin-bottom:20px; border-radius:0 4px 4px 0;">
          “${escapeHtml(item.supportingQuote)}”
        </blockquote>
      ` : ''}

      <!-- 8-Section Comprehensive Editorial Analysis -->
      <div style="display:flex; flex-direction:column; gap:20px;">
        
        <!-- Section A: What Happened -->
        <section style="background-color:var(--ms-surface-alt); padding:16px 20px; border:1px solid var(--ms-border); border-radius:4px;">
          <h4 style="font-family:var(--font-headline); font-size:1rem; text-transform:uppercase; color:var(--ms-primary); margin-bottom:8px;">
            A. CHUYỆN GÌ ĐÃ XẢY RA? (SỰ KIỆN CỐT LÕI)
          </h4>
          <p style="margin:0; font-size:0.9375rem; line-height:1.6;">${escapeHtml(item.sectionA_whatHappened || item.summary || '')}</p>
        </section>

        <!-- Section B: Context -->
        <section style="background-color:var(--ms-surface-alt); padding:16px 20px; border:1px solid var(--ms-border); border-radius:4px;">
          <h4 style="font-family:var(--font-headline); font-size:1rem; text-transform:uppercase; color:var(--ms-primary); margin-bottom:8px;">
            B. BỐI CẢNH THỊ TRƯỜNG & PHÁP LÝ
          </h4>
          <p style="margin:0; font-size:0.9375rem; line-height:1.6;">${escapeHtml(item.sectionB_context || item.explanation || 'Sự kiện diễn ra trong bối cảnh toàn ngành tài chính - ngân hàng đang nâng cấp hạ tầng bảo mật và chuẩn hóa quy trình dữ liệu.')}</p>
        </section>

        <!-- Section C: Why It Matters -->
        <section style="background-color:var(--ms-surface-alt); padding:16px 20px; border:1px solid var(--ms-border); border-radius:4px;">
          <h4 style="font-family:var(--font-headline); font-size:1rem; text-transform:uppercase; color:var(--ms-primary); margin-bottom:8px;">
            C. VÌ SAO QUAN TRỌNG?
          </h4>
          <p style="margin:0; font-size:0.9375rem; line-height:1.6;">${escapeHtml(item.sectionC_whyItMatters || item.importance || 'Ảnh hưởng trực tiếp đến an toàn tài sản của người dân và uy tín vận hành của các định chế tài chính.')}</p>
        </section>

        <!-- Section D: Macro-to-Micro Transmission -->
        <section style="background-color:var(--ms-surface-alt); padding:16px 20px; border:1px solid var(--ms-border); border-radius:4px;">
          <h4 style="font-family:var(--font-headline); font-size:1rem; text-transform:uppercase; color:var(--ms-primary); margin-bottom:8px;">
            D. CƠ CHẾ TRUYỀN DẪN VĨ MÔ → VI MÔ
          </h4>
          <p style="margin:0; font-size:0.9375rem; line-height:1.6; font-family:var(--font-mono); color:var(--ms-secondary);">${escapeHtml(item.sectionD_macroMicro || item.macroToMicroText || '')}</p>
        </section>

        <!-- Section E: FinTech & Payment Lens -->
        <section style="background-color:var(--ms-surface-alt); padding:16px 20px; border:1px solid var(--ms-border); border-radius:4px; border-left:4px solid var(--ms-primary);">
          <h4 style="font-family:var(--font-headline); font-size:1rem; text-transform:uppercase; color:var(--ms-primary); margin-bottom:8px;">
            E. GÓC NHÌN FINTECH & THANH TOÁN
          </h4>
          <p style="margin:0; font-size:0.9375rem; line-height:1.6;">${escapeHtml(item.sectionE_fintechLens || item.fintechImpact || '')}</p>
        </section>

        <!-- Section F: Scenarios & Watchlist -->
        <section style="background-color:var(--ms-surface-alt); padding:16px 20px; border:1px solid var(--ms-border); border-radius:4px;">
          <h4 style="font-family:var(--font-headline); font-size:1rem; text-transform:uppercase; color:var(--ms-primary); margin-bottom:8px;">
            F. KỊCH BẢN & ĐIỀU CẦN THEO DÕI
          </h4>
          <p style="margin:0; font-size:0.9375rem; line-height:1.6;">${escapeHtml(item.sectionF_scenariosWatchlist || item.forecast || '')}</p>
        </section>

        <!-- Section G: Practical Takeaways -->
        <section style="background-color:var(--ms-surface-alt); padding:16px 20px; border:1px solid var(--ms-border); border-radius:4px;">
          <h4 style="font-family:var(--font-headline); font-size:1rem; text-transform:uppercase; color:var(--ms-primary); margin-bottom:8px;">
            G. BÀI HỌC HOẶC ỨNG DỤNG THỰC TẾ
          </h4>
          <p style="margin:0; font-size:0.9375rem; line-height:1.6; font-weight:600;">${escapeHtml(item.sectionG_practicalTakeaway || item.takeaway || '')}</p>
        </section>

        <!-- Section H: Canonical Provenance & Sources -->
        <section style="background-color:var(--ms-surface-alt); padding:16px 20px; border:1px solid var(--ms-border); border-radius:4px;">
          <h4 style="font-family:var(--font-headline); font-size:1rem; text-transform:uppercase; color:var(--ms-primary); margin-bottom:10px;">
            H. NGUỒN BÀI VIẾT GỐC & ĐỐI SOÁT BÁO CHÍ
          </h4>
          <div style="font-size:0.875rem; line-height:1.6; margin-bottom:12px;">
            <div>• Tác giả / Nguồn: <strong>${escapeHtml(item.author || item.originalSourceName || 'Báo chí')}</strong></div>
            <div>• Thời gian xuất bản gốc: <strong>${escapeHtml(pubDate)}</strong></div>
          </div>
          <div>
            <a href="${escapeHtml(item.canonicalUrl)}" target="_blank" rel="noopener" class="ms-btn ms-btn-primary ms-btn-sm" style="display:inline-flex; align-items:center; gap:6px;">
              <span>Đọc bài viết gốc trên ${escapeHtml(item.originalSourceName || 'báo')}</span>
              <span>↗</span>
            </a>
          </div>
        </section>

      </div>
    </article>
  `;

  openDrawer(item.pageTitle || item.title || 'Phân tích chuyên sâu', html);
}


// ─── SECTION 05: CONNECT THE DOTS ───
function renderConnectTheDots() {
  const dots = EDITION_DATA.editorialSections?.sec05_connectTheDots || EDITION_DATA.editorialSections?.connectTheDots;
  const grid = $('#connectTheDotsGrid');
  if (!dots || !grid) return;

  grid.innerHTML = (dots.clusters || []).map(cluster => `
    <article class="ms-dot-story-card">
      <div style="margin-bottom:8px;">
        <span class="ms-badge ms-badge-rose">PHÂN TÍCH CHUỖI SỰ KIỆN</span>
      </div>
      <h3 class="ms-dot-title">${escapeHtml(cluster.clusterTitle)}</h3>
      <p class="ms-dot-narrative">${escapeHtml(cluster.synthesisNarrative)}</p>
      
      <div style="margin-top:16px; border-top:1px solid var(--ms-border); padding-top:12px;">
        ${(cluster.factStatements || []).map(f => `
          <div class="ms-pill-block"><span class="ms-pill-tag tag-fact">FACT</span>${escapeHtml(f.replace(/^FACT \d+:\s*/, ''))}</div>
        `).join('')}
        ${(cluster.inferenceStatements || []).map(inf => `
          <div class="ms-pill-block"><span class="ms-pill-tag tag-inference">INFERENCE</span>${escapeHtml(inf.replace(/^INFERENCE \d+:\s*/, ''))}</div>
        `).join('')}
        ${(cluster.scenarioStatements || []).map(sc => `
          <div class="ms-pill-block"><span class="ms-pill-tag tag-scenario">SCENARIO</span>${escapeHtml(sc.replace(/^SCENARIO:\s*/, ''))}</div>
        `).join('')}
      </div>
    </article>
  `).join('');
}

// ─── SECTION 06: MACRO TO MICRO ───
function renderMacroToMicro() {
  const m2m = EDITION_DATA.editorialSections?.sec06_macroToMicro || EDITION_DATA.editorialSections?.macroToMicro;
  const flowContainer = $('#macroMicroFlow');
  if (!m2m || !flowContainer) return;

  const chains = m2m.chains || [];
  if (chains.length === 0) {
    flowContainer.innerHTML = '<p class="ms-text-muted">Đang cập nhật các chuỗi phân tích truyền dẫn...</p>';
    return;
  }

  flowContainer.innerHTML = chains.map(chain => {
    const layersHtml = (chain.layers || []).map((layer, lIdx) => {
      let badgeClass = 'ms-badge-neutral';
      if (layer.badge === 'FACT') badgeClass = 'ms-badge-success';
      else if (layer.badge === 'INFERENCE') badgeClass = 'ms-badge-primary';
      else if (layer.badge === 'HYPOTHESIS') badgeClass = 'ms-badge-warning';

      const rawNum = layer.levelNumber || layer.level || layer.stageNumber || (lIdx != null ? lIdx + 1 : 1);
      let numVal = parseInt(rawNum, 10);
      if (isNaN(numVal) || numVal < 1) numVal = (lIdx != null ? lIdx + 1 : 1);
      const lvlNum = String(numVal).padStart(2, '0');
      let lvlName = layer.levelName || layer.layerName || layer.stageName || `Tầng ${lvlNum}`;
      if (typeof lvlName !== 'string' || lvlName.includes('undefined')) {
        lvlName = `Tầng ${lvlNum}`;
      }
      let title = layer.title || layer.stageTitle || layer.layerName || `Tác động tầng ${lvlNum}`;
      if (typeof title !== 'string' || title.includes('undefined')) {
        title = `Tác động tầng ${lvlNum}`;
      }
      const desc = layer.content || layer.description || '';

      return `
        <div class="ms-chain-layer-step">
          <div class="ms-layer-step-header">
            <div style="display:flex; align-items:center; gap:4px;">
              <span class="ms-layer-num">${escapeHtml(lvlNum)}</span>
              <strong class="ms-layer-name">${escapeHtml(lvlName)}</strong>
            </div>
            <div>
              <span class="ms-badge ${badgeClass}" style="font-size:8px; padding:1px 5px;">[${escapeHtml(layer.badge || 'FACT')}]</span>
            </div>
          </div>
          <div class="ms-layer-step-title">${escapeHtml(title)}</div>
          <div class="ms-layer-step-desc">${escapeHtml(desc)}</div>
        </div>
      `;
    }).join('<div class="ms-chain-connector">➔</div>');

    return `
      <article class="ms-analysis-chain-card">
        <div class="ms-chain-header">
          <div>
            <div style="display:flex; align-items:center; gap:8px; margin-bottom:6px;">
              <span class="ms-badge ms-badge-secondary" style="font-size:9px;">ECONOMIC ANALYSIS CHAIN</span>
            </div>
            <h3 class="ms-chain-title">${escapeHtml(chain.chainTitle)}</h3>
            <p class="ms-chain-thesis">${escapeHtml(chain.coreThesis)}</p>
          </div>
          <div style="flex-shrink:0;">
            <button class="ms-btn ms-btn-primary ms-btn-sm" onclick="openMacroChainDrawer('${escapeHtml(chain.chainId)}')">
              Xem phân tích đầy đủ →
            </button>
          </div>
        </div>
        <div class="ms-chain-layers-flow">
          ${layersHtml}
        </div>
      </article>
    `;
  }).join('');
}

function openMacroChainDrawer(chainId) {
  const m2m = EDITION_DATA.editorialSections?.sec06_macroToMicro || EDITION_DATA.editorialSections?.macroToMicro;
  const chain = (m2m?.chains || []).find(c => c.chainId === chainId);
  if (!chain) return;

  const layersList = (chain.layers || []).map((layer, lIdx) => {
    let badgeClass = 'ms-badge-neutral';
    if (layer.badge === 'FACT') badgeClass = 'ms-badge-success';
    else if (layer.badge === 'INFERENCE') badgeClass = 'ms-badge-primary';
    else if (layer.badge === 'HYPOTHESIS') badgeClass = 'ms-badge-warning';

    const numVal = parseInt(layer.levelNumber || layer.level || (lIdx + 1), 10) || (lIdx + 1);
    const lvlNum = String(numVal).padStart(2, '0');
    let lvlName = layer.levelName || layer.layerName || `Tầng ${lvlNum}`;
    if (typeof lvlName !== 'string' || lvlName.includes('undefined')) {
      lvlName = `Tầng ${lvlNum}`;
    }
    let title = layer.title || layer.stageTitle || layer.layerName || `Tác động tầng ${lvlNum}`;
    if (typeof title !== 'string' || title.includes('undefined')) {
      title = `Tác động tầng ${lvlNum}`;
    }
    const desc = layer.content || layer.description || '';

    return `
      <div style="background-color:var(--ms-surface-alt); border:1px solid var(--ms-border); border-left:4px solid var(--ms-primary); padding:14px 16px; border-radius:4px; margin-bottom:12px;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
          <div style="font-family:var(--font-mono); font-size:0.8125rem; font-weight:800; color:var(--ms-primary);">
            LỚP ${lvlNum} · ${escapeHtml(lvlName)}
          </div>
          <span class="ms-badge ${badgeClass}" style="font-size:9px;">[${escapeHtml(layer.badge || 'FACT')}]</span>
        </div>
        <h4 style="font-family:var(--font-headline); font-size:1rem; margin:0 0 6px 0; color:var(--ms-text-primary);">
          ${escapeHtml(title)}
        </h4>
        <p style="font-size:0.875rem; line-height:1.6; margin:0 0 8px 0; color:var(--ms-text-secondary);">
          ${escapeHtml(desc)}
        </p>
      </div>
    `;
  }).join('');

  const html = `
    <article style="font-size:0.9375rem; line-height:1.7;">
      <div style="padding-bottom:14px; margin-bottom:18px; border-bottom:2px solid var(--ms-border);">
        <span class="ms-badge ms-badge-secondary">CHUỖI PHÂN TÍCH</span>
        <h2 style="font-family:var(--font-headline); font-size:1.625rem; line-height:1.25; color:var(--ms-primary); margin:8px 0 6px 0;">
          ${escapeHtml(chain.chainTitle)}
        </h2>
        <div style="font-size:1rem; font-weight:600; color:var(--ms-text-primary); line-height:1.5;">
          ${escapeHtml(chain.coreThesis)}
        </div>
      </div>

      <div style="margin-bottom:20px;">
        <h4 style="font-family:var(--font-headline); font-size:0.9375rem; text-transform:uppercase; color:var(--ms-primary); margin-bottom:10px;">
          5 TẦNG TRUYỀN DẪN TÁC ĐỘNG (TRANSMISSION LAYERS)
        </h4>
        ${layersList}
      </div>

      <div style="background-color:var(--ms-surface-alt); padding:16px; border:1px solid var(--ms-border); border-radius:4px; margin-bottom:16px;">
        <h4 style="font-family:var(--font-headline); font-size:0.875rem; text-transform:uppercase; color:var(--ms-primary); margin-bottom:6px;">
          Ý NGHĨA CHIẾN LƯỢC (STRATEGIC SIGNIFICANCE)
        </h4>
        <p style="font-size:0.875rem; line-height:1.6; margin:0;">
          ${escapeHtml(chain.drawerSummary?.whyItMatters || '')}
        </p>
      </div>

      <div style="background-color:rgba(14, 116, 144, 0.08); border:1px solid var(--ms-primary); padding:16px; border-radius:4px;">
        <h4 style="font-family:var(--font-headline); font-size:0.875rem; text-transform:uppercase; color:var(--ms-primary); margin-bottom:6px;">
          HÀNH ĐỘNG THỰC THI (ACTIONABLE TAKEAWAY)
        </h4>
        <p style="font-size:0.875rem; line-height:1.6; margin:0; font-weight:600;">
          ${escapeHtml(chain.drawerSummary?.actionableTakeaway || '')}
        </p>
      </div>
    </article>
  `;

  openDrawer(chain.chainTitle || 'Chuỗi truyền dẫn vĩ mô → vi mô', html);
}


// ─── SECTION 07: PAYMENT OPPORTUNITY RADAR ───
function renderPaymentRadar() {
  const radar = EDITION_DATA.editorialSections?.sec07_paymentRadar || EDITION_DATA.editorialSections?.paymentOpportunityRadar;
  const grid = $('#paymentRadarGrid');
  if (!radar || !grid) return;

  grid.innerHTML = (radar.opportunities || []).map(op => {
    const title = op.title || op.opportunityTitle || 'Cơ hội thanh toán';
    const segment = op.merchantSegment || op.targetSegment || 'Chuỗi bán lẻ & F&B';
    const painPoint = op.paymentPainPoint || op.merchantPainPoint || 'Thất thoát do thao tác xác nhận bill thủ công';
    const solution = op.paymentSolution || op.payooPotentialSolution || 'Payoo SmartPOS & VietQR Động Webhook';
    const rationale = op.businessRationale || op.commercialRationale || 'Bảo vệ dòng tiền doanh thu tại điểm bán';
    const bdAction = op.proposedBDAction || op.proposedBdAction || 'Tiếp cận ban điều hành các chuỗi bán lẻ';
    const readiness = op.solutionReadiness || 'CONFIRMED_EXISTING_CAPABILITY';
    const readinessBadge = readiness === 'CONFIRMED_EXISTING_CAPABILITY'
      ? '<span class="ms-badge ms-badge-success" style="font-size:9px;">NĂNG LỰC HIỆN HỮU</span>'
      : '<span class="ms-badge ms-badge-primary" style="font-size:9px;">TÍCH HỢP MỞ RỘNG</span>';

    return `
      <article class="ms-radar-card">
        <div>
          <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:8px; gap:8px;">
            <span class="ms-badge ms-badge-primary">B2B OPPORTUNITY</span>
            ${readinessBadge}
          </div>
          <h3 class="ms-radar-title">${escapeHtml(title)}</h3>
          <div class="ms-radar-row">
            <strong>Tín hiệu thị trường:</strong> ${escapeHtml(op.marketSignal || '')}
          </div>
          <div class="ms-radar-row">
            <strong>Phân khúc khách hàng:</strong> ${escapeHtml(segment)}
          </div>
          <div class="ms-radar-row">
            <strong>Điểm đau / Nhu cầu:</strong> ${escapeHtml(painPoint)}
          </div>
          <div class="ms-radar-row">
            <strong>Giải pháp Payoo:</strong> ${escapeHtml(solution)}
          </div>
          <div class="ms-radar-row">
            <strong>Lợi ích thương mại:</strong> ${escapeHtml(rationale)}
          </div>
          ${op.assumptionsAndRisks ? `
            <div class="ms-radar-row" style="font-size:0.75rem; color:var(--ms-text-muted);">
              <strong>Giả định & Rủi ro:</strong> ${escapeHtml(op.assumptionsAndRisks)}
            </div>
          ` : ''}
        </div>
        <div style="border-top:1px solid var(--ms-border); padding-top:10px; margin-top:12px; font-size:0.8125rem; background-color:var(--ms-surface-alt); padding:8px 10px; border-radius:4px;">
          <strong style="color:var(--ms-primary);">Hành động BD đề xuất:</strong> ${escapeHtml(bdAction)}
        </div>
      </article>
    `;
  }).join('');
}


// ─── SECTION 08: EXPERT LEARNING ───
function renderExpertLearning() {
  const el = EDITION_DATA.editorialSections?.sec08_expertLearning || EDITION_DATA.editorialSections?.expertLearning;
  const grid = $('#expertLearningGrid');
  if (!el || !grid) return;

  let html = '';

  // 1. Render Expert Masterclass Lessons if present
  if (el.lessons && el.lessons.length > 0) {
    html += el.lessons.map(lesson => {
      const concept = lesson.concept || lesson.financialConcept || '';
      const title = lesson.title || lesson.topic || '';
      const grounding = lesson.newsGrounding || lesson.groundingEvent || '';
      const explanation = lesson.simpleExplanation || lesson.plainEnglishExplanation || '';
      const example = lesson.realWorldExample || '';
      const takeaway = lesson.takeaway || lesson.readerTakeaway || '';
      const impact = lesson.impactOnBusiness || '';

      return `
        <article class="ms-learning-card">
          <div>
            <div class="ms-learning-concept">${escapeHtml(concept)}</div>
            <h3 class="ms-learning-topic">${escapeHtml(title)}</h3>
            <div style="font-size:0.8125rem; color:var(--ms-text-muted); margin-bottom:8px;">
              Căn cứ thực tế: ${escapeHtml(grounding)}
            </div>
            <p class="ms-learning-body"><strong>Giải thích đơn giản:</strong> ${escapeHtml(explanation)}</p>
            <p class="ms-learning-body"><strong>Ví dụ thực tế:</strong> ${escapeHtml(example)}</p>
            ${impact ? `<p class="ms-learning-body"><strong>Tác động đến doanh nghiệp / FinTech:</strong> ${escapeHtml(impact)}</p>` : ''}
          </div>
          <div class="ms-learning-takeaway">
            <strong>Bài học thực chiến:</strong> ${escapeHtml(takeaway)}
          </div>
        </article>
      `;
    }).join('');
  }

  // 2. Render Strategic Frameworks if present
  const frameworks = el.frameworks || [];
  if (frameworks.length > 0) {
    html += frameworks.map((fw, idx) => `
      <article class="ms-learning-card" style="border-left:4px solid var(--ms-primary);">
        <div>
          <div class="ms-learning-concept">KHUNG TƯ DUY CHIẾN LƯỢC · FRAMEWORK 0${idx + 1}</div>
          <h3 class="ms-learning-topic">${escapeHtml(fw.frameworkTitle || '')}</h3>
          <div style="display:flex; flex-direction:column; gap:8px; margin:12px 0; font-size:0.875rem; line-height:1.6;">
            <div style="background-color:var(--ms-surface-base); padding:8px 10px; border-radius:4px;">
              <strong style="color:var(--ms-primary);">Bước 1 (Vĩ mô):</strong> ${escapeHtml(fw.step1 || '')}
            </div>
            <div style="background-color:var(--ms-surface-base); padding:8px 10px; border-radius:4px;">
              <strong style="color:var(--ms-secondary);">Bước 2 (Ngân hàng & Vốn):</strong> ${escapeHtml(fw.step2 || '')}
            </div>
            <div style="background-color:var(--ms-surface-base); padding:8px 10px; border-radius:4px;">
              <strong style="color:var(--ms-accent-emerald);">Bước 3 (Thanh toán & POS):</strong> ${escapeHtml(fw.step3 || '')}
            </div>
          </div>
        </div>
        <div class="ms-learning-takeaway">
          <strong>Đúc kết vận hành:</strong> Chuẩn hóa dòng tiền từ nguồn vốn vĩ mô đến điểm chạm thanh toán tại quầy.
        </div>
      </article>
    `).join('');
  }

  // 3. Render B2B FinTech Sales Playbooks if present
  const playbooks = el.salesPlaybook || [];
  if (playbooks.length > 0) {
    html += playbooks.map((pb, idx) => `
      <article class="ms-learning-card" style="border-left:4px solid var(--ms-secondary);">
        <div>
          <div class="ms-learning-concept">KỊCH BẢN THỰC CHIẾN B2B FINTECH · PLAYBOOK 0${idx + 1}</div>
          <h3 class="ms-learning-topic">${escapeHtml(pb.title || '')}</h3>
          <div style="font-size:0.8125rem; color:var(--ms-text-muted); margin-bottom:8px;">
            Khách hàng mục tiêu: <strong>${escapeHtml(pb.target || '')}</strong>
          </div>
          <p class="ms-learning-body"><strong>Thông điệp tiếp cận:</strong> ${escapeHtml(pb.pitch || '')}</p>
        </div>
        <div class="ms-learning-takeaway" style="background-color:var(--ms-surface-alt);">
          <strong>Xử lý từ chối:</strong> ${escapeHtml(pb.objectionHandling || '')}
        </div>
      </article>
    `).join('');
  }

  // 4. Render FinTech Glossary if present
  const glossary = el.fintechGlossary || [];
  if (glossary.length > 0) {
    html += `
      <article class="ms-learning-card" style="grid-column:1/-1;">
        <div class="ms-learning-concept">THUẬT NGỮ CHUYÊN NGÀNH FINTECH & NGÂN HÀNG SỐ</div>
        <h3 class="ms-learning-topic">Từ Điển Quy Chuẩn Nghiệp Vụ Bryan FinTech</h3>
        <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(280px, 1fr)); gap:12px; margin-top:12px;">
          ${glossary.map(g => `
            <div style="background-color:var(--ms-surface-base); padding:10px 12px; border:1px solid var(--ms-border); border-radius:4px;">
              <div style="font-family:var(--font-mono); font-weight:700; color:var(--ms-primary); font-size:0.875rem;">${escapeHtml(g.term)}</div>
              <div style="font-size:0.8125rem; line-height:1.5; color:var(--ms-text-secondary); margin-top:4px;">${escapeHtml(g.definition)}</div>
            </div>
          `).join('')}
        </div>
      </article>
    `;
  }

  grid.innerHTML = html;
}


// ─── SECTION 09: GOOGLE SHEETS ARCHIVE & EDITION HISTORY ───
let currentArchiveSearch = '';
let currentArchiveStatus = 'ALL';

// Helper for strict editionId validation
function isValidArchiveEditionId(id) {
  return typeof id === 'string' && /^EDITION-\d{4}-\d{2}-\d{2}-[A-Za-z0-9_]+$/.test(id);
}

function renderArchive() {
  const tbody = $('#archiveTableBody');
  if (!tbody) return;

  const editionData = (typeof window !== 'undefined' && window.EDITION_DATA)
    ? window.EDITION_DATA
    : (typeof EDITION_DATA !== 'undefined' ? EDITION_DATA : null);

  const archiveSec = editionData?.editorialSections?.sec09_archive;
  const editions = Array.isArray(archiveSec?.editions) ? archiveSec.editions : [];

  if (editions.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="5" style="text-align:center; padding:24px; color:var(--ms-text-muted); font-size:0.875rem;">
          Không có dữ liệu lưu trữ ấn bản.
        </td>
      </tr>
    `;
    return;
  }

  tbody.innerHTML = editions.map(ed => {
    const statusText = ed.status || '';
    const isPreview = statusText.includes('PREVIEW');
    const badgeClass = isPreview ? 'ms-badge-warning' : 'ms-badge-neutral';
    const displayDate = ed.date || ed.editionDate || '';
    const editionId = ed.editionId || '';

    return `
      <tr>
        <td style="white-space:nowrap;">
          <strong>${escapeHtml(displayDate)}</strong>
          <div style="font-size:0.6875rem; font-family:var(--font-mono); color:var(--ms-text-muted);">${escapeHtml(editionId)}</div>
        </td>
        <td style="white-space:nowrap; font-weight:600;">${escapeHtml(ed.number || '')}</td>
        <td>
          <div style="font-weight:600; color:var(--ms-text-primary); margin-bottom:4px;">${escapeHtml(ed.theme || '')}</div>
          <div style="font-size:0.75rem; color:var(--ms-text-muted);">Tỷ lệ mới 0–24h: <strong>${escapeHtml(ed.freshness || '')}</strong> · ${escapeHtml(ed.newsCount || '')}</div>
        </td>
        <td>
          <span class="ms-badge ${badgeClass}" style="font-size:10px;">${escapeHtml(statusText)}</span>
        </td>
        <td style="white-space:nowrap; text-align:right;">
          <button type="button" class="ms-btn ms-btn-primary ms-btn-xs js-archive-drawer-btn" style="margin-right:6px;" data-edition-id="${escapeHtml(editionId)}">
            MỞ ĐỌC →
          </button>
          <button type="button" class="ms-btn ms-btn-ghost ms-btn-xs js-archive-sheets-btn" data-edition-id="${escapeHtml(editionId)}">
            SCHEMA SHEETS ↗
          </button>
        </td>
      </tr>
    `;
  }).join('');

  // Event Delegation: Bind listener once to tbody
  if (!tbody.dataset.archiveListenerBound) {
    tbody.addEventListener('click', (e) => {
      const drawerBtn = e.target.closest('.js-archive-drawer-btn');
      if (drawerBtn) {
        const id = drawerBtn.getAttribute('data-edition-id');
        if (isValidArchiveEditionId(id) && typeof window.openArchiveDrawer === 'function') {
          window.openArchiveDrawer(id);
        }
        return;
      }

      const sheetsBtn = e.target.closest('.js-archive-sheets-btn');
      if (sheetsBtn) {
        const id = sheetsBtn.getAttribute('data-edition-id');
        if (isValidArchiveEditionId(id) && typeof window.openSheetsSchemaModal === 'function') {
          window.openSheetsSchemaModal(id);
        }
        return;
      }
    });
    tbody.dataset.archiveListenerBound = 'true';
  }
}

function openArchiveDrawer(editionId) {
  const isCurrent = editionId === 'EDITION-2026-11-08-PILOT25';
  const ct = EDITION_DATA.editorialSections?.sec02_coverStory || EDITION_DATA.editorialSections?.coreThesis;
  const gate = EDITION_DATA.publicationGateStatus || {};
  const mp = EDITION_DATA.marketPulseSnapshot || [];

  const html = `
    <article style="font-size:0.9375rem; line-height:1.7;">
      <div style="padding-bottom:14px; margin-bottom:18px; border-bottom:2px solid var(--ms-border);">
        <span class="ms-badge ms-badge-warning">${escapeHtml(editionId)}</span>
        <h2 style="font-family:var(--font-headline); font-size:1.5rem; line-height:1.25; color:var(--ms-primary); margin:8px 0 6px 0;">
          ${escapeHtml(ct?.editorialHeadline || 'Siết Chặt Lá Chắn Bảo Mật & Phòng Chống Lừa Đảo Số')}
        </h2>
        <div style="font-size:0.875rem; color:var(--ms-text-secondary); line-height:1.5;">
          ${escapeHtml(ct?.executiveSummary || '')}
        </div>
      </div>

      <!-- Section A: Publication Gate Audit -->
      <div style="background-color:var(--ms-surface-alt); border:1px solid var(--ms-border); border-left:4px solid var(--ms-warning); padding:14px 16px; margin-bottom:16px;">
        <h4 style="font-family:var(--font-headline); font-size:0.875rem; text-transform:uppercase; color:var(--ms-warning-text); margin-bottom:6px;">
          TÌNH TRẠNG KIỂM DUYỆT XUẤT BẢN (PUBLICATION GATE STATUS)
        </h4>
        <div style="font-size:0.8125rem; font-family:var(--font-mono); line-height:1.6;">
          Trạng thái Gate: <strong>${escapeHtml(gate.gateStatus || 'FAIL_SHORTFALL_24H_PREVIEW_ONLY')}</strong><br>
          Nhãn công khai: <strong>${escapeHtml(gate.publicBadgeLabel || 'PREVIEW — CHƯA XUẤT BẢN')}</strong><br>
          Tỷ lệ 0–24h: <strong>11/21 tin (52,38%)</strong> (Ngưỡng đạt: ≥ 80%)<br>
          Quy tắc áp dụng: Giữ nguyên chế độ Preview, không xuất bản sản xuất khi chưa đủ hạn ngạch 24H-First.
        </div>
      </div>

      <!-- Section B: Market Pulse Snapshot -->
      <div style="margin-bottom:18px;">
        <h4 style="font-family:var(--font-headline); font-size:0.875rem; text-transform:uppercase; color:var(--ms-primary); margin-bottom:10px;">
          BỘ 8 CHỈ SỐ MARKET PULSE LƯU TRỮ
        </h4>
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:8px;">
          ${mp.slice(0, 8).map(card => `
            <div style="background:var(--ms-surface-card); border:1px solid var(--ms-border); padding:8px 10px; font-size:0.75rem;">
              <div style="font-family:var(--font-mono); color:var(--ms-text-muted); font-size:9px;">${escapeHtml(card.cardNumber || '')}. ${escapeHtml(card.shortLabel || card.label || '')}</div>
              <div style="font-family:var(--font-headline); font-size:0.9375rem; font-weight:700; color:var(--ms-primary);">${escapeHtml(card.value || 'N/A')} ${escapeHtml(card.unit || '')}</div>
              <div style="font-size:9px; color:var(--ms-text-muted);">Phiên: ${escapeHtml(card.asOf || '')}</div>
            </div>
          `).join('')}
        </div>
      </div>

      <!-- Section C: Google Sheets Archive Integration -->
      <div style="background:rgba(14, 116, 144, 0.08); border:1px solid var(--ms-primary); padding:14px; margin-bottom:14px;">
        <h4 style="font-family:var(--font-headline); font-size:0.875rem; text-transform:uppercase; color:var(--ms-primary); margin-bottom:6px;">
          ĐỒNG BỘ GOOGLE SHEETS ARCHIVE
        </h4>
        <p style="font-size:0.8125rem; line-height:1.5; margin-bottom:8px;">
          Ấn bản này đã sẵn sàng cấu trúc lưu trữ 7 tab chuẩn: <code>EDITIONS</code>, <code>NEWS_EVENTS</code>, <code>EDITORIAL_SECTIONS</code>, <code>MARKET_PULSE_HISTORY</code>, <code>EVENT_REGISTRY</code>, <code>SOURCE_LEDGER</code>, <code>PUBLISH_AUDIT</code>.
        </p>
        <button class="ms-btn ms-btn-primary ms-btn-sm" onclick="openSheetsSchemaModal('${escapeHtml(editionId)}')">
          XEM CHI TIẾT 7 TABS SCHEMA →
        </button>
      </div>
    </article>
  `;

  openDrawer(`Lưu Trữ: ${editionId}`, html);
}

function openSheetsSchemaModal(editionId) {
  const html = `
    <article style="font-size:0.875rem; line-height:1.6;">
      <div style="padding-bottom:12px; margin-bottom:16px; border-bottom:2px solid var(--ms-border);">
        <span class="ms-badge ms-badge-primary">GOOGLE SHEETS ARCHIVE SPECIFICATION</span>
        <h2 style="font-family:var(--font-headline); font-size:1.375rem; line-height:1.25; color:var(--ms-primary); margin:8px 0 4px 0;">
          BRYAN_FINTECH_EDITION_ARCHIVE
        </h2>
        <div style="font-size:0.8125rem; color:var(--ms-text-secondary);">
          Kiến trúc lưu trữ ấn bản dài hạn bên ngoài website phục vụ tra cứu lịch sử và báo cáo độc lập.
        </div>
      </div>

      <div style="margin-bottom:16px;">
        <h4 style="font-family:var(--font-headline); font-size:0.8125rem; text-transform:uppercase; color:var(--ms-primary); margin-bottom:8px;">
          7 TABS DỮ LIỆU CỐT LÕI (SPREADSHEET TABS SCHEMA)
        </h4>

        <div style="display:flex; flex-direction:column; gap:8px;">
          <div style="background:var(--ms-surface-card); border:1px solid var(--ms-border); padding:10px 12px;">
            <div style="font-weight:700; color:var(--ms-primary);">1. TAB [EDITIONS]</div>
            <div style="font-size:0.75rem; font-family:var(--font-mono); color:var(--ms-text-muted);">
              editionId, editionDate, editionNumber, publicationStatus, eligibleCount, count0To24h, freshnessRatio, createdAt, publishedAt, revision, schemaVersion
            </div>
          </div>

          <div style="background:var(--ms-surface-card); border:1px solid var(--ms-border); padding:10px 12px;">
            <div style="font-weight:700; color:var(--ms-primary);">2. TAB [NEWS_EVENTS]</div>
            <div style="font-size:0.75rem; font-family:var(--font-mono); color:var(--ms-text-muted);">
              editionId, eventId, canonicalEventKey, title, category, eventDate, publicationDate, dataPeriod, strictCombinedTimeWindow, sourceName, canonicalUrl, summary, analysis, verificationStatus, sourceHash
            </div>
          </div>

          <div style="background:var(--ms-surface-card); border:1px solid var(--ms-border); padding:10px 12px;">
            <div style="font-weight:700; color:var(--ms-primary);">3. TAB [EDITORIAL_SECTIONS]</div>
            <div style="font-size:0.75rem; font-family:var(--font-mono); color:var(--ms-text-muted);">
              editionId, sectionKey, sectionTitle, editorialContent, originEventIds, publicationStatus
            </div>
          </div>

          <div style="background:var(--ms-surface-card); border:1px solid var(--ms-border); padding:10px 12px;">
            <div style="font-weight:700; color:var(--ms-primary);">4. TAB [MARKET_PULSE_HISTORY]</div>
            <div style="font-size:0.75rem; font-family:var(--font-mono); color:var(--ms-text-muted);">
              editionId, metricKey, value, unit, asOf, dataPeriod, publishedAt, verificationStatus, sourceUrl
            </div>
          </div>

          <div style="background:var(--ms-surface-card); border:1px solid var(--ms-border); padding:10px 12px;">
            <div style="font-weight:700; color:var(--ms-primary);">5. TAB [EVENT_REGISTRY]</div>
            <div style="font-size:0.75rem; font-family:var(--font-mono); color:var(--ms-text-muted);">
              canonicalEventKey, firstSeenEditionId, firstSeenDate, primaryEntity, canonicalUrl, titleNormalized
            </div>
          </div>

          <div style="background:var(--ms-surface-card); border:1px solid var(--ms-border); padding:10px 12px;">
            <div style="font-weight:700; color:var(--ms-primary);">6. TAB [SOURCE_LEDGER]</div>
            <div style="font-size:0.75rem; font-family:var(--font-mono); color:var(--ms-text-muted);">
              canonicalUrl, sourcePublisher, initialCapturedAt, snapshotPath, sha256Hash, author, verificationFlag
            </div>
          </div>

          <div style="background:var(--ms-surface-card); border:1px solid var(--ms-border); padding:10px 12px;">
            <div style="font-weight:700; color:var(--ms-primary);">7. TAB [PUBLISH_AUDIT]</div>
            <div style="font-size:0.75rem; font-family:var(--font-mono); color:var(--ms-text-muted);">
              editionId, auditTimestamp, auditorRole, decisionStatus, shortfallReason, approvedRevision, masterPromptVersion
            </div>
          </div>
        </div>
      </div>

      <div style="background:var(--ms-surface-alt); padding:12px; border:1px solid var(--ms-border); font-size:0.75rem; font-family:var(--font-mono);">
        <strong>KIẾN TRÚC TRUY XUẤT READ-ONLY:</strong><br>
        • Google Apps Script Web App Endpoint: <code>doGet(e)</code><br>
        • Caching: CacheService 6 giờ cho các ấn bản đã lưu trữ<br>
        • Phân tách Public / Private: Chỉ trả dữ liệu các ấn bản đạt Gate; dữ liệu Draft / Review được bảo vệ qua API Key nội bộ.
      </div>
    </article>
  `;

  openDrawer(`Sheets Archive Schema: ${editionId}`, html);
}


// ─── TAB NAVIGATION CONTROLLER (BRYAN PORTFOLIO MULTI-PAGE PARITY) ───
function switchFintechTab(tabKey, targetSubId) {
  if (!tabKey) tabKey = 'today';
  
  const pages = {
    today: 'page-today',
    market: 'page-market',
    analysis: 'page-analysis',
    b2b: 'page-b2b',
    archive: 'page-archive'
  };
  
  const targetPageId = pages[tabKey] || 'page-today';

  // 1. Toggle page sections visibility
  document.querySelectorAll('.ms-page-section').forEach(sec => {
    sec.classList.remove('active');
  });
  const activePage = document.getElementById(targetPageId);
  if (activePage) {
    activePage.classList.add('active');
  }

  // 2. Update desktop tab buttons
  document.querySelectorAll('.ms-nav-tab-btn').forEach(btn => {
    btn.classList.toggle('active', btn.getAttribute('data-tab') === tabKey);
  });

  // 3. Update mobile quick tabs
  document.querySelectorAll('.ms-quick-tab').forEach(btn => {
    btn.classList.toggle('active', btn.getAttribute('data-tab') === tabKey);
  });

  // 4. Close mobile drawer if open
  closeMobileDrawer();

  // 5. Update browser URL hash cleanly
  if (window.history && window.history.replaceState) {
    window.history.replaceState(null, '', '#' + tabKey);
  }

  // 6. Scroll smoothly to target sub-section or top of page
  if (targetSubId) {
    setTimeout(() => {
      const el = document.getElementById(targetSubId);
      if (el) {
        el.scrollIntoView({ behavior: 'smooth', block: 'start' });
      } else {
        window.scrollTo({ top: 0, behavior: 'smooth' });
      }
    }, 60);
  } else {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
}

function initFintechTabs() {
  const hash = (window.location.hash || '').replace('#', '').toLowerCase();
  const validTabs = ['today', 'market', 'analysis', 'b2b', 'archive'];
  if (validTabs.includes(hash)) {
    switchFintechTab(hash);
  } else {
    switchFintechTab('today');
  }

  window.addEventListener('hashchange', () => {
    const newHash = (window.location.hash || '').replace('#', '').toLowerCase();
    if (validTabs.includes(newHash)) {
      switchFintechTab(newHash);
    }
  });
}

function openMobileDrawer() {
  const mobileDrawer = document.getElementById('mobileNavDrawer');
  if (mobileDrawer) {
    mobileDrawer.classList.add('open');
    mobileDrawer.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
  }
}

function closeMobileDrawer() {
  const mobileDrawer = document.getElementById('mobileNavDrawer');
  if (mobileDrawer) {
    mobileDrawer.classList.remove('open');
    mobileDrawer.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
  }
}

// ─── FILTER & SEARCH EVENTS ───
function setupEventListeners() {
  // Floating Contact Widget Toggle (Bryan Portfolio Parity)
  const fabBtn = $('#fabToggleBtn');
  const floatWidget = $('#floating-widget');
  if (fabBtn && floatWidget) {
    fabBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      floatWidget.classList.toggle('menu-open');
    });
    document.addEventListener('click', (e) => {
  // Floating widget close on outside click
  const fw = document.getElementById('floating-widget');
  if (fw && fw.classList.contains('menu-open') && !fw.contains(e.target)) {
    closeFabMenu();
  }

      if (!floatWidget.contains(e.target)) {
        floatWidget.classList.remove('menu-open');
      }
    });
  }
  // Category buttons in News Desk
  $$('.ms-cat-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      $$('.ms-cat-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      currentCategoryFilter = btn.getAttribute('data-cat') || 'ALL';
      renderNewsDesk();
    });
  });

  // Search input
  const searchInput = $('#newsSearchInput');
  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      currentSearchTerm = e.target.value.trim();
      renderNewsDesk();
    });
  }

  // Theme toggle
  const themeBtn = $('#themeToggleBtn');
  if (themeBtn) themeBtn.addEventListener('click', toggleTheme);

  // Drawer close & backdrop
  const closeBtn = $('#drawerCloseBtn');
  const backdrop = $('#drawerBackdrop');
  if (closeBtn) closeBtn.addEventListener('click', closeDrawer);
  if (backdrop) backdrop.addEventListener('click', closeDrawer);

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      closeDrawer();
      closeMobileDrawer();
      closeAllDropdowns();
    }
  });

  // ─── NAVIGATION MEGA MENU & MOBILE DRAWER INTERACTIONS ───
  const mobileToggle = $('#mobileMenuToggle');
  const mobileClose = $('#mobileDrawerClose');

  function closeAllDropdowns() {
    $$('.ms-nav-group').forEach(g => {
      g.classList.remove('open');
      const tr = g.querySelector('.ms-nav-trigger');
      if (tr) tr.setAttribute('aria-expanded', 'false');
    });
  }

  if (mobileToggle) mobileToggle.addEventListener('click', openMobileDrawer);
  if (mobileClose) mobileClose.addEventListener('click', closeMobileDrawer);

  // Desktop Navigation Trigger Click & Keyboard Toggle
  $$('.ms-nav-trigger').forEach(trigger => {
    trigger.addEventListener('click', (e) => {
      e.stopPropagation();
      const parent = trigger.closest('.ms-nav-group');
      const isOpen = parent.classList.contains('open');
      closeAllDropdowns();
      if (!isOpen) {
        parent.classList.add('open');
        trigger.setAttribute('aria-expanded', 'true');
      }
    });
  });

  // Click outside to close dropdowns
  document.addEventListener('click', (e) => {
  // Floating widget close on outside click
  const fw = document.getElementById('floating-widget');
  if (fw && fw.classList.contains('menu-open') && !fw.contains(e.target)) {
    closeFabMenu();
  }

    if (!e.target.closest('.ms-nav-group')) {
      closeAllDropdowns();
    }
  });

  // Mobile Accordion items
  $$('.ms-accordion-header').forEach(header => {
    header.addEventListener('click', () => {
      const parent = header.closest('.ms-accordion-item');
      if (parent) {
        parent.classList.toggle('active');
      }
    });
  });

  // Smooth scroll and auto-close for all dropdown items and accordion links
  $$('.ms-dropdown-item, .ms-accordion-link').forEach(link => {
    link.addEventListener('click', (e) => {
      const href = link.getAttribute('href');
      if (href && href.startsWith('#')) {
        e.preventDefault();
        const target = $(href);
        if (target) {
          closeMobileDrawer();
          closeAllDropdowns();
          target.scrollIntoView({ behavior: 'smooth' });
        }
      }
    });
  });
}


// ─── INITIALIZATION ───
document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  setupEventListeners();
  loadEditionData();
});

/* ─── SECTION 03B: RENDER TODAY'S DECISION BRIEF ─── */
function renderDecisionBrief() {
  const data = EDITION_DATA;
  if (!data) return;
  const container = document.getElementById('decisionBriefGrid');
  if (!container) return;
  
  const briefData = data.editorialSections?.sec04b_decisionBrief || {};
  const signals = briefData.signals || [];
  
  if (signals.length === 0) {
    container.innerHTML = '<p class="ms-text-muted">Đang cập nhật các tín hiệu hành động điều hành...</p>';
    return;
  }
  
  container.innerHTML = signals.map((sig, idx) => {
    const eventsStr = (sig.relatedEventIds || []).join(', ');
    const meaning = sig.whatItMeansForMyWork || sig.whyItMatters || '';
    const meaningSnippet = meaning.length > 160 ? meaning.slice(0, 160) + '...' : meaning;
    
    let categoryBadge = 'CHIẾN LƯỢC ĐIỀU HÀNH';
    if (idx === 0) categoryBadge = 'BẢO MẬT & CHỐNG GIAN LẬN';
    else if (idx === 1) categoryBadge = 'HẠ TẦNG AN NINH DỮ LIỆU';
    else if (idx === 2) categoryBadge = 'TUÂN THỦ THUẾ & ĐIỂM BÁN';
    else if (idx === 3) categoryBadge = 'DÒNG TIỀN GIÁO DỤC TỰ CHỦ';

    const priorityBadge = sig.confidenceLevel === 'HIGH_CONFIDENCE_GROUNDED'
      ? '<span class="ms-badge ms-badge-rose" style="font-size:9px;">ƯU TIÊN CAO</span>'
      : '<span class="ms-badge ms-badge-primary" style="font-size:9px;">TRỌNG TÂM</span>';

    return `
      <article class="ms-compact-decision-card">
        <div>
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
            <span class="ms-badge ms-badge-secondary" style="font-size:9px;">${escapeHtml(categoryBadge)}</span>
            ${priorityBadge}
          </div>
          <h3 class="ms-decision-card-title">${escapeHtml(sig.signalTitle)}</h3>
          <p class="ms-decision-card-lead">
            <strong>Ý nghĩa B2B:</strong> ${escapeHtml(meaningSnippet)}
          </p>
        </div>
        <div style="border-top:1px solid var(--ms-border); padding-top:10px; margin-top:12px; display:flex; justify-content:space-between; align-items:center;">
          <span style="font-size:0.75rem; color:var(--ms-text-muted); font-weight:600;">TÍN HIỆU #${idx + 1}</span>
          <button class="ms-btn ms-btn-primary ms-btn-sm" onclick="openDecisionSignalDrawer('${escapeHtml(sig.signalId)}')">
            ĐỌC PHÂN TÍCH →
          </button>
        </div>
      </article>
    `;
  }).join('');
}

function openDecisionSignalDrawer(signalId) {
  const briefData = EDITION_DATA.editorialSections?.sec04b_decisionBrief || {};
  const sig = (briefData.signals || []).find(s => s.signalId === signalId);
  if (!sig) return;

  const assumptionsText = Array.isArray(sig.assumptions)
    ? sig.assumptions.join('; ')
    : (typeof sig.assumptions === 'string' ? sig.assumptions : '');

  const risksText = Array.isArray(sig.risks)
    ? sig.risks.join('; ')
    : (typeof sig.risks === 'string' ? sig.risks : '');

  const segmentsText = Array.isArray(sig.relevantMerchantSegments)
    ? sig.relevantMerchantSegments.map(s => escapeHtml(s)).join(', ')
    : (typeof sig.relevantMerchantSegments === 'string' ? escapeHtml(sig.relevantMerchantSegments) : 'Chuỗi F&B, Khách sạn, Bán lẻ đa kênh & Hộ kinh doanh');

  const solutionsHtml = (sig.potentialPaymentSolutions || []).map(sol => {
    let pillClass = 'ms-pill-confirmed';
    let pillLabel = 'ĐÃ CÓ SẴN TẠI PAYOO (HIỆN HỮU)';
    if (sol.readinessType === 'POTENTIAL_INTEGRATION') {
      pillClass = 'ms-pill-potential';
      pillLabel = 'CẦN TÍCH HỢP MỞ RỘNG';
    } else if (sol.readinessType === 'PRODUCT_DEVELOPMENT_IDEA') {
      pillClass = 'ms-pill-idea';
      pillLabel = 'Ý TƯỞNG PHÁT TRIỂN MỚI';
    }
    return `
      <div style="background-color:var(--ms-surface-base); padding:10px 14px; border:1px solid var(--ms-border); border-left:3px solid var(--ms-primary); border-radius:4px; margin-bottom:8px;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
          <span class="ms-solution-pill ${pillClass}">${pillLabel}</span>
          <span class="ms-xs" style="color:var(--ms-text-muted); font-family:var(--font-mono);">${escapeHtml(sol.readinessType || '')}</span>
        </div>
        <div style="font-weight:700; font-size:0.875rem; color:var(--ms-text-primary);">${escapeHtml(sol.solutionName)}</div>
        <p style="font-size:0.8125rem; margin:4px 0 0 0; color:var(--ms-text-secondary); line-height:1.5;">${escapeHtml(sol.capabilityNote)}</p>
      </div>
    `;
  }).join('');

  let urls = sig.evidenceUrls || [];
  if (!urls.length && sig.relatedEventIds && sig.relatedEventIds.length) {
    const newsList = EDITION_DATA.eligibleNewsList || [];
    urls = sig.relatedEventIds.map(eid => {
      const found = newsList.find(n => n.eventId === eid || n.originEventId === eid);
      return found ? (found.canonicalUrl || found.sourceUrl) : null;
    }).filter(Boolean);
  }

  const urlsHtml = (urls || []).map(u => `
    <div style="margin-top:6px;">
      <a href="${escapeHtml(u)}" target="_blank" rel="noopener noreferrer" class="ms-btn ms-btn-ghost ms-btn-xs" style="word-break:break-all;">
        Mở bài viết gốc đã xác minh (${escapeHtml(u.slice(0, 50))}...) ↗
      </a>
    </div>
  `).join('');

  const html = `
    <article style="font-size:0.9375rem; line-height:1.7;">
      <!-- Header -->
      <div style="padding-bottom:14px; margin-bottom:18px; border-bottom:2px solid var(--ms-border);">
        <span class="ms-badge ms-badge-rose">TÍN HIỆU CHIẾN LƯỢC</span>
        <span class="ms-badge ms-badge-neutral" style="margin-left:6px;">${escapeHtml(sig.confidenceLevel || 'HIGH_CONFIDENCE')}</span>
        <h2 style="font-family:var(--font-headline); font-size:1.625rem; line-height:1.25; color:var(--ms-primary); margin:10px 0 6px 0;">
          ${escapeHtml(sig.signalTitle)}
        </h2>
      </div>

      <div style="display:flex; flex-direction:column; gap:16px;">
        <!-- Section A: What Happened -->
        <div style="background-color:var(--ms-surface-alt); padding:16px; border:1px solid var(--ms-border); border-radius:4px;">
          <h4 style="font-family:var(--font-headline); font-size:0.875rem; text-transform:uppercase; color:var(--ms-primary); margin-bottom:6px;">
            A. SỰ KIỆN NÀO ĐÃ XẢY RA?
          </h4>
          <p style="margin:0; font-size:0.875rem; line-height:1.6;">${escapeHtml(sig.whatHappened)}</p>
        </div>

        <!-- Section B: Why It Matters -->
        <div style="background-color:var(--ms-surface-alt); padding:16px; border:1px solid var(--ms-border); border-radius:4px;">
          <h4 style="font-family:var(--font-headline); font-size:0.875rem; text-transform:uppercase; color:var(--ms-primary); margin-bottom:6px;">
            B. VÌ SAO ĐÁNG CHÚ Ý?
          </h4>
          <p style="margin:0; font-size:0.875rem; line-height:1.6;">${escapeHtml(sig.whyItMatters)}</p>
        </div>

        <!-- Section C: What Changes -->
        <div style="background-color:var(--ms-surface-alt); padding:16px; border:1px solid var(--ms-border); border-radius:4px;">
          <h4 style="font-family:var(--font-headline); font-size:0.875rem; text-transform:uppercase; color:var(--ms-primary); margin-bottom:6px;">
            C. TÁC ĐỘNG NÀO CÓ THỂ XẢY RA?
          </h4>
          <p style="margin:0; font-size:0.875rem; line-height:1.6;">${escapeHtml(sig.whatChanges)}</p>
        </div>

        <!-- Section D: What It Means For B2B / Work -->
        <div style="background-color:var(--ms-surface-alt); padding:16px; border:1px solid var(--ms-border); border-radius:4px; border-left:4px solid var(--ms-secondary);">
          <h4 style="font-family:var(--font-headline); font-size:0.875rem; text-transform:uppercase; color:var(--ms-secondary); margin-bottom:6px;">
            D. LIÊN QUAN GÌ ĐẾN THANH TOÁN & CÔNG VIỆC B2B?
          </h4>
          <p style="margin:0; font-size:0.875rem; line-height:1.6; font-weight:600;">${escapeHtml(sig.whatItMeansForMyWork)}</p>
        </div>

        <!-- Section E: Opportunities, Assumptions & Risks -->
        <div style="background-color:var(--ms-surface-alt); padding:16px; border:1px solid var(--ms-border); border-radius:4px;">
          <h4 style="font-family:var(--font-headline); font-size:0.875rem; text-transform:uppercase; color:var(--ms-primary); margin-bottom:6px;">
            E. CƠ HỘI, GIỚI HẠN & RỦI RO
          </h4>
          <div style="font-size:0.875rem; line-height:1.6;">
            <div><strong>Phân khúc khách hàng:</strong> ${segmentsText}</div>
            ${assumptionsText ? `<div style="margin-top:4px;"><strong>Giả định:</strong> ${escapeHtml(assumptionsText)}</div>` : ''}
            ${risksText ? `<div style="margin-top:4px; color:var(--ms-text-muted);"><strong>Rủi ro cần lường trước:</strong> ${escapeHtml(risksText)}</div>` : ''}
          </div>
        </div>

        <!-- Section F: What to Watch & Next Action -->
        <div style="background-color:var(--ms-surface-alt); padding:16px; border:1px solid var(--ms-border); border-radius:4px;">
          <h4 style="font-family:var(--font-headline); font-size:0.875rem; text-transform:uppercase; color:var(--ms-primary); margin-bottom:6px;">
            F. TÔI NÊN LÀM GÌ HOẶC THEO DÕI GÌ?
          </h4>
          <p style="margin:0 0 8px 0; font-size:0.875rem; line-height:1.6;">${escapeHtml(sig.whatShouldIDoOrWatch)}</p>
          <div style="background-color:var(--ms-surface-base); padding:8px 12px; border-radius:4px; font-size:0.8125rem;">
            <strong>Hành động tiếp theo đề xuất:</strong> ${escapeHtml(sig.proposedNextAction)}
            <br><span style="color:var(--ms-text-muted); font-size:0.75rem;">Khung thời gian theo dõi: ${escapeHtml(sig.monitoringTimeHorizon || '')}</span>
          </div>
        </div>

        <!-- Section G: Relevant Payoo Solutions -->
        <div style="background-color:var(--ms-surface-alt); padding:16px; border:1px solid var(--ms-border); border-radius:4px;">
          <h4 style="font-family:var(--font-headline); font-size:0.875rem; text-transform:uppercase; color:var(--ms-primary); margin-bottom:10px;">
            G. CÁC SẢN PHẨM / GIẢI PHÁP PAYOO LIÊN QUAN
          </h4>
          ${solutionsHtml}
        </div>

        <!-- Section H: Evidence & Sources -->
        <div style="background-color:var(--ms-surface-alt); padding:16px; border:1px solid var(--ms-border); border-radius:4px;">
          <h4 style="font-family:var(--font-headline); font-size:0.875rem; text-transform:uppercase; color:var(--ms-primary); margin-bottom:6px;">
            H. NGUỒN BÁO CHÍ THAM KHẢO & ĐỐI SOÁT
          </h4>
          ${urlsHtml}
        </div>
      </div>
    </article>
  `;

  openDrawer(sig.signalTitle || 'Tín hiệu hành động điều hành', html);
}


function renderWatchlist() {
  const data = EDITION_DATA;
  if (!data) return;
  const container = document.getElementById('watchlistGrid');
  if (!container) return;
  
  const watchlist = data.editorialSections?.sec08b_watchlist?.watchlistItems 
                 || data.editorialSections?.sec08b_watchlist?.items 
                 || [];
  if (watchlist.length === 0) {
    container.innerHTML = '<p class="ms-text-muted">Chưa có chỉ báo nào cần kích hoạt theo dõi tuần tới.</p>';
    return;
  }
  
  container.innerHTML = watchlist.map((item, idx) => {
    const wId = item.watchlistId || `WL-0${idx + 1}`;
    const indicator = item.category || item.sourceOrIndicator || 'Chỉ báo trọng yếu';
    const title = item.itemTitle || item.signalTracked || 'Biến số theo dõi';
    const desc = item.description || item.conditionChangingAssessment || '';
    const impact = item.impactLevel || 'HIGH';
    const action = item.possibleAction || (impact === 'HIGH' ? 'Kích hoạt kịch bản điều hòa thanh khoản & dòng tiền' : 'Theo dõi biến động phiên tiếp theo');
    const horizon = item.observationHorizon || '7 ngày tới';

    return `
      <div class="ms-watchlist-card">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
          <div class="ms-watchlist-indicator">${escapeHtml(wId)} · ${escapeHtml(indicator)}</div>
          <span class="ms-badge ${impact === 'HIGH' ? 'ms-badge-error' : 'ms-badge-warning'}" style="font-size:8px; padding:1px 5px;">${escapeHtml(impact)}</span>
        </div>
        <h4 class="ms-watchlist-title">${escapeHtml(title)}</h4>
        <div class="ms-watchlist-desc">
          <strong>Trọng tâm theo dõi:</strong> ${escapeHtml(desc)}
        </div>
        <div class="ms-watchlist-action" style="margin-top:8px; font-size:0.8125rem;">
          <strong>Kịch bản ứng phó:</strong> ${escapeHtml(action)} (${escapeHtml(horizon)})
        </div>
      </div>
    `;
  }).join('');
}

// Global accessibility keyboard handler
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    closePulseDrawer();
    closeArticleReader();
  }
});


window.openArchiveDrawer = openArchiveDrawer;
window.openSheetsSchemaModal = openSheetsSchemaModal;


/* ==========================================================================
   P0 CRITICAL RESTORATION: MODALS, VCARD, FAB, BACK-TO-TOP & EVENT DELEGATION
   ========================================================================== */

// Offline Vector SVG QR for vCard, Zalo, LinkedIn
const QR_SVG_DATA = {
      vcard: {
        size: 71,
        color: "#292524",
        path: "M1,1h7v1h-7zM9,1h2v1h-2zM12,1h1v1h-1zM14,1h1v1h-1zM17,1h1v1h-1zM21,1h1v1h-1zM23,1h2v1h-2zM26,1h1v1h-1zM30,1h1v1h-1zM35,1h1v1h-1zM37,1h2v1h-2zM41,1h2v1h-2zM45,1h3v1h-3zM50,1h2v1h-2zM54,1h2v1h-2zM60,1h2v1h-2zM64,1h1v1h-1zM67,1h3v1h-3zM1,2h1v1h-1zM7,2h1v1h-1zM12,2h1v1h-1zM15,2h3v1h-3zM19,2h1v1h-1zM22,2h2v1h-2zM29,2h3v1h-3zM35,2h1v1h-1zM37,2h2v1h-2zM40,2h1v1h-1zM42,2h1v1h-1zM44,2h3v1h-3zM50,2h1v1h-1zM52,2h2v1h-2zM58,2h7v1h-7zM66,2h1v1h-1zM69,2h1v1h-1zM1,3h1v1h-1zM3,3h3v1h-3zM7,3h1v1h-1zM10,3h4v1h-4zM18,3h1v1h-1zM21,3h2v1h-2zM24,3h1v1h-1zM26,3h2v1h-2zM31,3h1v1h-1zM33,3h5v1h-5zM39,3h2v1h-2zM42,3h3v1h-3zM46,3h1v1h-1zM48,3h1v1h-1zM50,3h2v1h-2zM53,3h1v1h-1zM57,3h1v1h-1zM59,3h2v1h-2zM63,3h1v1h-1zM65,3h3v1h-3zM1,4h1v1h-1zM3,4h3v1h-3zM7,4h1v1h-1zM11,4h1v1h-1zM15,4h2v1h-2zM19,4h2v1h-2zM23,4h1v1h-1zM30,4h2v1h-2zM34,4h1v1h-1zM40,4h2v1h-2zM43,4h4v1h-4zM49,4h1v1h-1zM51,4h1v1h-1zM58,4h1v1h-1zM60,4h3v1h-3zM64,4h1v1h-1zM67,4h3v1h-3zM1,5h1v1h-1zM3,5h3v1h-3zM7,5h1v1h-1zM9,5h3v1h-3zM13,5h3v1h-3zM20,5h1v1h-1zM24,5h3v1h-3zM29,5h2v1h-2zM33,5h6v1h-6zM47,5h1v1h-1zM50,5h1v1h-1zM57,5h1v1h-1zM59,5h1v1h-1zM61,5h5v1h-5zM67,5h1v1h-1zM69,5h1v1h-1zM1,6h1v1h-1zM7,6h1v1h-1zM11,6h1v1h-1zM14,6h2v1h-2zM19,6h1v1h-1zM21,6h5v1h-5zM29,6h3v1h-3zM33,6h1v1h-1zM37,6h2v1h-2zM40,6h1v1h-1zM42,6h1v1h-1zM44,6h1v1h-1zM46,6h4v1h-4zM51,6h2v1h-2zM54,6h1v1h-1zM57,6h1v1h-1zM59,6h1v1h-1zM61,6h1v1h-1zM65,6h3v1h-3zM69,6h1v1h-1zM1,7h7v1h-7zM9,7h2v1h-2zM12,7h3v1h-3zM17,7h1v1h-1zM22,7h1v1h-1zM24,7h4v1h-4zM29,7h2v1h-2zM32,7h2v1h-2zM35,7h1v1h-1zM37,7h4v1h-4zM42,7h1v1h-1zM46,7h1v1h-1zM50,7h2v1h-2zM54,7h2v1h-2zM57,7h1v1h-1zM61,7h1v1h-1zM63,7h1v1h-1zM65,7h3v1h-3zM9,8h3v1h-3zM14,8h1v1h-1zM19,8h6v1h-6zM26,8h2v1h-2zM32,8h2v1h-2zM37,8h1v1h-1zM39,8h2v1h-2zM43,8h1v1h-1zM46,8h1v1h-1zM50,8h2v1h-2zM53,8h3v1h-3zM58,8h2v1h-2zM61,8h1v1h-1zM65,8h1v1h-1zM67,8h1v1h-1zM69,8h1v1h-1zM1,9h1v1h-1zM4,9h2v1h-2zM7,9h2v1h-2zM11,9h1v1h-1zM14,9h1v1h-1zM16,9h1v1h-1zM18,9h1v1h-1zM23,9h1v1h-1zM25,9h1v1h-1zM28,9h1v1h-1zM31,9h8v1h-8zM41,9h1v1h-1zM44,9h2v1h-2zM47,9h2v1h-2zM52,9h1v1h-1zM54,9h2v1h-2zM57,9h1v1h-1zM60,9h7v1h-7zM69,9h1v1h-1zM1,10h1v1h-1zM8,10h2v1h-2zM11,10h3v1h-3zM15,10h1v1h-1zM19,10h3v1h-3zM24,10h2v1h-2zM27,10h1v1h-1zM29,10h1v1h-1zM31,10h2v1h-2zM35,10h1v1h-1zM38,10h1v1h-1zM42,10h1v1h-1zM44,10h4v1h-4zM49,10h1v1h-1zM52,10h2v1h-2zM56,10h2v1h-2zM59,10h2v1h-2zM63,10h1v1h-1zM65,10h1v1h-1zM69,10h1v1h-1zM1,11h1v1h-1zM3,11h1v1h-1zM5,11h8v1h-8zM15,11h4v1h-4zM20,11h1v1h-1zM23,11h1v1h-1zM25,11h2v1h-2zM28,11h6v1h-6zM35,11h5v1h-5zM44,11h1v1h-1zM46,11h1v1h-1zM50,11h5v1h-5zM57,11h5v1h-5zM63,11h1v1h-1zM65,11h1v1h-1zM2,12h2v1h-2zM5,12h1v1h-1zM9,12h1v1h-1zM12,12h2v1h-2zM15,12h1v1h-1zM19,12h3v1h-3zM24,12h1v1h-1zM26,12h3v1h-3zM30,12h1v1h-1zM32,12h3v1h-3zM37,12h1v1h-1zM39,12h1v1h-1zM41,12h5v1h-5zM47,12h1v1h-1zM49,12h1v1h-1zM51,12h2v1h-2zM54,12h2v1h-2zM60,12h1v1h-1zM62,12h3v1h-3zM66,12h2v1h-2zM69,12h1v1h-1zM1,13h1v1h-1zM3,13h3v1h-3zM7,13h1v1h-1zM9,13h1v1h-1zM15,13h5v1h-5zM21,13h1v1h-1zM24,13h2v1h-2zM27,13h2v1h-2zM30,13h3v1h-3zM34,13h1v1h-1zM36,13h3v1h-3zM40,13h11v1h-11zM52,13h1v1h-1zM54,13h4v1h-4zM59,13h1v1h-1zM62,13h2v1h-2zM67,13h1v1h-1zM69,13h1v1h-1zM1,14h1v1h-1zM5,14h1v1h-1zM8,14h1v1h-1zM10,14h1v1h-1zM12,14h2v1h-2zM16,14h2v1h-2zM19,14h3v1h-3zM23,14h1v1h-1zM26,14h4v1h-4zM31,14h2v1h-2zM34,14h1v1h-1zM38,14h1v1h-1zM40,14h2v1h-2zM45,14h5v1h-5zM54,14h1v1h-1zM56,14h1v1h-1zM58,14h2v1h-2zM62,14h3v1h-3zM66,14h1v1h-1zM1,15h1v1h-1zM4,15h1v1h-1zM7,15h1v1h-1zM9,15h1v1h-1zM12,15h2v1h-2zM15,15h2v1h-2zM20,15h1v1h-1zM23,15h1v1h-1zM27,15h5v1h-5zM33,15h1v1h-1zM35,15h1v1h-1zM37,15h2v1h-2zM41,15h1v1h-1zM44,15h1v1h-1zM46,15h3v1h-3zM51,15h4v1h-4zM58,15h3v1h-3zM62,15h1v1h-1zM65,15h1v1h-1zM68,15h1v1h-1zM3,16h4v1h-4zM9,16h2v1h-2zM12,16h1v1h-1zM14,16h2v1h-2zM18,16h1v1h-1zM23,16h1v1h-1zM25,16h2v1h-2zM29,16h2v1h-2zM32,16h1v1h-1zM34,16h1v1h-1zM37,16h3v1h-3zM43,16h2v1h-2zM46,16h1v1h-1zM48,16h2v1h-2zM51,16h2v1h-2zM55,16h2v1h-2zM58,16h1v1h-1zM63,16h1v1h-1zM65,16h1v1h-1zM67,16h1v1h-1zM69,16h1v1h-1zM1,17h4v1h-4zM7,17h4v1h-4zM12,17h2v1h-2zM16,17h3v1h-3zM23,17h3v1h-3zM27,17h1v1h-1zM29,17h1v1h-1zM31,17h4v1h-4zM36,17h2v1h-2zM39,17h3v1h-3zM44,17h1v1h-1zM46,17h1v1h-1zM52,17h1v1h-1zM54,17h1v1h-1zM56,17h1v1h-1zM58,17h1v1h-1zM61,17h2v1h-2zM66,17h2v1h-2zM69,17h1v1h-1zM1,18h1v1h-1zM9,18h1v1h-1zM16,18h2v1h-2zM20,18h1v1h-1zM22,18h2v1h-2zM25,18h2v1h-2zM28,18h1v1h-1zM31,18h1v1h-1zM34,18h1v1h-1zM37,18h1v1h-1zM40,18h1v1h-1zM44,18h1v1h-1zM47,18h2v1h-2zM51,18h1v1h-1zM54,18h2v1h-2zM60,18h2v1h-2zM64,18h3v1h-3zM1,19h1v1h-1zM4,19h1v1h-1zM6,19h4v1h-4zM12,19h2v1h-2zM15,19h2v1h-2zM22,19h2v1h-2zM25,19h2v1h-2zM30,19h1v1h-1zM33,19h1v1h-1zM35,19h1v1h-1zM38,19h1v1h-1zM41,19h4v1h-4zM46,19h1v1h-1zM48,19h2v1h-2zM52,19h1v1h-1zM55,19h1v1h-1zM60,19h3v1h-3zM67,19h2v1h-2zM2,20h1v1h-1zM5,20h1v1h-1zM8,20h1v1h-1zM10,20h1v1h-1zM12,20h1v1h-1zM14,20h1v1h-1zM16,20h1v1h-1zM18,20h1v1h-1zM21,20h7v1h-7zM29,20h1v1h-1zM31,20h3v1h-3zM37,20h3v1h-3zM41,20h1v1h-1zM44,20h1v1h-1zM46,20h1v1h-1zM49,20h1v1h-1zM51,20h8v1h-8zM61,20h1v1h-1zM64,20h1v1h-1zM67,20h1v1h-1zM69,20h1v1h-1zM1,21h3v1h-3zM7,21h1v1h-1zM14,21h1v1h-1zM19,21h2v1h-2zM22,21h1v1h-1zM25,21h2v1h-2zM29,21h9v1h-9zM40,21h2v1h-2zM43,21h1v1h-1zM45,21h2v1h-2zM48,21h2v1h-2zM51,21h2v1h-2zM54,21h1v1h-1zM56,21h3v1h-3zM60,21h1v1h-1zM62,21h5v1h-5zM68,21h2v1h-2zM1,22h1v1h-1zM3,22h1v1h-1zM6,22h1v1h-1zM9,22h1v1h-1zM13,22h1v1h-1zM15,22h1v1h-1zM18,22h2v1h-2zM23,22h1v1h-1zM25,22h1v1h-1zM27,22h3v1h-3zM31,22h1v1h-1zM34,22h1v1h-1zM36,22h2v1h-2zM39,22h2v1h-2zM42,22h1v1h-1zM44,22h1v1h-1zM47,22h1v1h-1zM50,22h2v1h-2zM54,22h1v1h-1zM64,22h1v1h-1zM66,22h1v1h-1zM68,22h2v1h-2zM3,23h2v1h-2zM7,23h1v1h-1zM10,23h2v1h-2zM14,23h1v1h-1zM17,23h1v1h-1zM19,23h1v1h-1zM22,23h1v1h-1zM25,23h1v1h-1zM33,23h1v1h-1zM36,23h1v1h-1zM38,23h2v1h-2zM41,23h1v1h-1zM46,23h1v1h-1zM48,23h2v1h-2zM53,23h4v1h-4zM63,23h1v1h-1zM67,23h2v1h-2zM2,24h1v1h-1zM4,24h3v1h-3zM8,24h3v1h-3zM12,24h1v1h-1zM14,24h1v1h-1zM16,24h1v1h-1zM18,24h1v1h-1zM21,24h4v1h-4zM27,24h1v1h-1zM29,24h1v1h-1zM31,24h4v1h-4zM36,24h1v1h-1zM39,24h1v1h-1zM41,24h1v1h-1zM43,24h3v1h-3zM47,24h1v1h-1zM50,24h2v1h-2zM54,24h2v1h-2zM57,24h2v1h-2zM60,24h2v1h-2zM63,24h2v1h-2zM67,24h3v1h-3zM1,25h1v1h-1zM4,25h2v1h-2zM7,25h8v1h-8zM20,25h1v1h-1zM24,25h1v1h-1zM26,25h2v1h-2zM30,25h1v1h-1zM32,25h1v1h-1zM40,25h8v1h-8zM50,25h1v1h-1zM54,25h1v1h-1zM57,25h2v1h-2zM62,25h7v1h-7zM1,26h2v1h-2zM4,26h1v1h-1zM8,26h3v1h-3zM12,26h1v1h-1zM14,26h1v1h-1zM16,26h1v1h-1zM20,26h2v1h-2zM24,26h1v1h-1zM28,26h1v1h-1zM30,26h1v1h-1zM32,26h2v1h-2zM37,26h1v1h-1zM39,26h2v1h-2zM42,26h1v1h-1zM46,26h4v1h-4zM52,26h4v1h-4zM58,26h2v1h-2zM61,26h1v1h-1zM64,26h3v1h-3zM68,26h2v1h-2zM1,27h1v1h-1zM4,27h2v1h-2zM7,27h4v1h-4zM12,27h2v1h-2zM16,27h1v1h-1zM24,27h1v1h-1zM27,27h1v1h-1zM32,27h1v1h-1zM34,27h1v1h-1zM36,27h1v1h-1zM38,27h1v1h-1zM41,27h2v1h-2zM46,27h1v1h-1zM48,27h4v1h-4zM53,27h1v1h-1zM55,27h2v1h-2zM58,27h2v1h-2zM61,27h1v1h-1zM64,27h2v1h-2zM67,27h1v1h-1zM69,27h1v1h-1zM2,28h2v1h-2zM5,28h2v1h-2zM11,28h1v1h-1zM13,28h2v1h-2zM18,28h3v1h-3zM23,28h1v1h-1zM25,28h2v1h-2zM31,28h1v1h-1zM35,28h3v1h-3zM40,28h1v1h-1zM42,28h1v1h-1zM45,28h1v1h-1zM47,28h2v1h-2zM54,28h2v1h-2zM57,28h2v1h-2zM60,28h2v1h-2zM63,28h1v1h-1zM65,28h1v1h-1zM67,28h1v1h-1zM69,28h1v1h-1zM3,29h2v1h-2zM7,29h2v1h-2zM12,29h1v1h-1zM14,29h4v1h-4zM20,29h2v1h-2zM24,29h3v1h-3zM29,29h1v1h-1zM32,29h3v1h-3zM36,29h1v1h-1zM39,29h1v1h-1zM42,29h2v1h-2zM46,29h2v1h-2zM50,29h1v1h-1zM52,29h1v1h-1zM54,29h1v1h-1zM56,29h4v1h-4zM63,29h1v1h-1zM66,29h1v1h-1zM68,29h1v1h-1zM1,30h1v1h-1zM4,30h2v1h-2zM9,30h1v1h-1zM12,30h3v1h-3zM16,30h1v1h-1zM19,30h1v1h-1zM21,30h3v1h-3zM27,30h7v1h-7zM39,30h1v1h-1zM42,30h3v1h-3zM46,30h5v1h-5zM53,30h2v1h-2zM57,30h5v1h-5zM64,30h6v1h-6zM4,31h2v1h-2zM7,31h2v1h-2zM10,31h2v1h-2zM13,31h2v1h-2zM18,31h2v1h-2zM21,31h2v1h-2zM24,31h2v1h-2zM30,31h1v1h-1zM32,31h1v1h-1zM34,31h2v1h-2zM40,31h1v1h-1zM50,31h6v1h-6zM60,31h1v1h-1zM65,31h1v1h-1zM67,31h2v1h-2zM1,32h1v1h-1zM4,32h1v1h-1zM6,32h1v1h-1zM8,32h2v1h-2zM11,32h1v1h-1zM13,32h1v1h-1zM15,32h2v1h-2zM19,32h1v1h-1zM24,32h1v1h-1zM26,32h2v1h-2zM34,32h1v1h-1zM36,32h2v1h-2zM39,32h1v1h-1zM41,32h3v1h-3zM46,32h1v1h-1zM48,32h3v1h-3zM52,32h2v1h-2zM55,32h2v1h-2zM60,32h1v1h-1zM64,32h1v1h-1zM67,32h1v1h-1zM2,33h1v1h-1zM4,33h11v1h-11zM16,33h1v1h-1zM18,33h1v1h-1zM20,33h4v1h-4zM27,33h1v1h-1zM31,33h8v1h-8zM40,33h1v1h-1zM42,33h1v1h-1zM45,33h3v1h-3zM53,33h2v1h-2zM56,33h10v1h-10zM67,33h3v1h-3zM3,34h1v1h-1zM5,34h1v1h-1zM9,34h1v1h-1zM12,34h1v1h-1zM15,34h2v1h-2zM20,34h3v1h-3zM26,34h5v1h-5zM33,34h1v1h-1zM37,34h1v1h-1zM39,34h2v1h-2zM42,34h1v1h-1zM47,34h3v1h-3zM54,34h1v1h-1zM58,34h2v1h-2zM61,34h1v1h-1zM65,34h1v1h-1zM68,34h2v1h-2zM3,35h3v1h-3zM7,35h1v1h-1zM9,35h2v1h-2zM12,35h1v1h-1zM15,35h1v1h-1zM17,35h1v1h-1zM19,35h1v1h-1zM21,35h1v1h-1zM24,35h1v1h-1zM27,35h1v1h-1zM29,35h1v1h-1zM32,35h2v1h-2zM35,35h1v1h-1zM37,35h2v1h-2zM40,35h4v1h-4zM46,35h1v1h-1zM50,35h2v1h-2zM53,35h3v1h-3zM57,35h5v1h-5zM63,35h1v1h-1zM65,35h1v1h-1zM67,35h2v1h-2zM1,36h3v1h-3zM5,36h1v1h-1zM9,36h3v1h-3zM14,36h2v1h-2zM17,36h1v1h-1zM21,36h1v1h-1zM26,36h1v1h-1zM30,36h4v1h-4zM37,36h1v1h-1zM39,36h3v1h-3zM45,36h1v1h-1zM49,36h3v1h-3zM53,36h1v1h-1zM56,36h2v1h-2zM60,36h2v1h-2zM65,36h3v1h-3zM1,37h1v1h-1zM5,37h5v1h-5zM11,37h2v1h-2zM20,37h1v1h-1zM24,37h2v1h-2zM27,37h2v1h-2zM31,37h8v1h-8zM41,37h2v1h-2zM45,37h4v1h-4zM51,37h1v1h-1zM54,37h1v1h-1zM56,37h1v1h-1zM59,37h8v1h-8zM68,37h2v1h-2zM2,38h5v1h-5zM12,38h2v1h-2zM16,38h1v1h-1zM18,38h1v1h-1zM20,38h1v1h-1zM26,38h2v1h-2zM29,38h1v1h-1zM33,38h3v1h-3zM37,38h2v1h-2zM40,38h3v1h-3zM45,38h2v1h-2zM49,38h2v1h-2zM53,38h2v1h-2zM57,38h3v1h-3zM61,38h2v1h-2zM64,38h2v1h-2zM68,38h1v1h-1zM4,39h6v1h-6zM11,39h1v1h-1zM13,39h2v1h-2zM16,39h1v1h-1zM20,39h1v1h-1zM22,39h4v1h-4zM30,39h1v1h-1zM32,39h1v1h-1zM38,39h3v1h-3zM47,39h1v1h-1zM51,39h3v1h-3zM57,39h1v1h-1zM60,39h2v1h-2zM63,39h1v1h-1zM65,39h4v1h-4zM1,40h1v1h-1zM4,40h3v1h-3zM8,40h4v1h-4zM17,40h4v1h-4zM22,40h1v1h-1zM25,40h3v1h-3zM29,40h1v1h-1zM31,40h1v1h-1zM33,40h1v1h-1zM35,40h3v1h-3zM40,40h8v1h-8zM49,40h1v1h-1zM51,40h1v1h-1zM53,40h1v1h-1zM60,40h5v1h-5zM66,40h3v1h-3zM1,41h3v1h-3zM7,41h1v1h-1zM9,41h3v1h-3zM13,41h1v1h-1zM15,41h3v1h-3zM22,41h1v1h-1zM26,41h1v1h-1zM28,41h1v1h-1zM31,41h2v1h-2zM37,41h2v1h-2zM43,41h4v1h-4zM48,41h4v1h-4zM56,41h5v1h-5zM67,41h1v1h-1zM69,41h1v1h-1zM1,42h2v1h-2zM6,42h1v1h-1zM8,42h1v1h-1zM11,42h1v1h-1zM14,42h4v1h-4zM19,42h1v1h-1zM22,42h5v1h-5zM29,42h1v1h-1zM33,42h2v1h-2zM36,42h3v1h-3zM40,42h1v1h-1zM42,42h1v1h-1zM46,42h1v1h-1zM48,42h3v1h-3zM52,42h2v1h-2zM59,42h1v1h-1zM62,42h1v1h-1zM65,42h2v1h-2zM69,42h1v1h-1zM1,43h1v1h-1zM3,43h2v1h-2zM6,43h2v1h-2zM9,43h2v1h-2zM12,43h2v1h-2zM16,43h1v1h-1zM20,43h1v1h-1zM22,43h1v1h-1zM24,43h1v1h-1zM26,43h1v1h-1zM30,43h1v1h-1zM32,43h1v1h-1zM36,43h2v1h-2zM39,43h4v1h-4zM47,43h2v1h-2zM50,43h6v1h-6zM57,43h2v1h-2zM60,43h3v1h-3zM65,43h5v1h-5zM1,44h6v1h-6zM8,44h1v1h-1zM12,44h1v1h-1zM14,44h2v1h-2zM17,44h2v1h-2zM20,44h2v1h-2zM23,44h3v1h-3zM27,44h2v1h-2zM30,44h3v1h-3zM36,44h2v1h-2zM40,44h2v1h-2zM44,44h1v1h-1zM47,44h1v1h-1zM51,44h2v1h-2zM57,44h1v1h-1zM59,44h2v1h-2zM63,44h2v1h-2zM67,44h2v1h-2zM1,45h4v1h-4zM6,45h2v1h-2zM11,45h1v1h-1zM13,45h2v1h-2zM17,45h1v1h-1zM19,45h5v1h-5zM28,45h1v1h-1zM30,45h2v1h-2zM34,45h1v1h-1zM36,45h4v1h-4zM47,45h1v1h-1zM49,45h1v1h-1zM55,45h1v1h-1zM57,45h1v1h-1zM64,45h1v1h-1zM66,45h1v1h-1zM69,45h1v1h-1zM5,46h2v1h-2zM10,46h1v1h-1zM12,46h2v1h-2zM16,46h1v1h-1zM20,46h1v1h-1zM22,46h1v1h-1zM24,46h1v1h-1zM26,46h1v1h-1zM28,46h2v1h-2zM31,46h1v1h-1zM34,46h5v1h-5zM40,46h2v1h-2zM45,46h2v1h-2zM48,46h1v1h-1zM51,46h4v1h-4zM56,46h5v1h-5zM62,46h1v1h-1zM64,46h2v1h-2zM67,46h1v1h-1zM69,46h1v1h-1zM1,47h1v1h-1zM3,47h1v1h-1zM5,47h1v1h-1zM7,47h3v1h-3zM11,47h2v1h-2zM14,47h1v1h-1zM16,47h1v1h-1zM18,47h1v1h-1zM20,47h2v1h-2zM24,47h1v1h-1zM27,47h1v1h-1zM30,47h1v1h-1zM34,47h1v1h-1zM36,47h2v1h-2zM39,47h4v1h-4zM44,47h1v1h-1zM47,47h1v1h-1zM50,47h6v1h-6zM60,47h4v1h-4zM65,47h1v1h-1zM67,47h3v1h-3zM1,48h1v1h-1zM3,48h2v1h-2zM6,48h1v1h-1zM8,48h1v1h-1zM10,48h3v1h-3zM15,48h2v1h-2zM19,48h2v1h-2zM22,48h1v1h-1zM26,48h2v1h-2zM29,48h1v1h-1zM31,48h4v1h-4zM36,48h2v1h-2zM40,48h1v1h-1zM42,48h2v1h-2zM51,48h3v1h-3zM55,48h1v1h-1zM58,48h1v1h-1zM63,48h6v1h-6zM1,49h3v1h-3zM6,49h2v1h-2zM11,49h3v1h-3zM16,49h1v1h-1zM23,49h1v1h-1zM29,49h1v1h-1zM31,49h1v1h-1zM35,49h1v1h-1zM37,49h3v1h-3zM42,49h1v1h-1zM44,49h2v1h-2zM50,49h1v1h-1zM55,49h2v1h-2zM59,49h3v1h-3zM66,49h2v1h-2zM69,49h1v1h-1zM2,50h5v1h-5zM9,50h1v1h-1zM12,50h2v1h-2zM16,50h1v1h-1zM19,50h1v1h-1zM25,50h2v1h-2zM29,50h1v1h-1zM31,50h4v1h-4zM38,50h1v1h-1zM41,50h1v1h-1zM45,50h2v1h-2zM53,50h2v1h-2zM56,50h1v1h-1zM59,50h1v1h-1zM64,50h1v1h-1zM67,50h1v1h-1zM69,50h1v1h-1zM1,51h1v1h-1zM5,51h1v1h-1zM7,51h2v1h-2zM11,51h1v1h-1zM13,51h1v1h-1zM15,51h2v1h-2zM18,51h1v1h-1zM21,51h1v1h-1zM24,51h2v1h-2zM27,51h1v1h-1zM29,51h3v1h-3zM34,51h2v1h-2zM37,51h1v1h-1zM40,51h2v1h-2zM44,51h1v1h-1zM46,51h1v1h-1zM48,51h1v1h-1zM50,51h3v1h-3zM54,51h1v1h-1zM58,51h5v1h-5zM65,51h1v1h-1zM68,51h2v1h-2zM1,52h2v1h-2zM4,52h1v1h-1zM9,52h6v1h-6zM16,52h1v1h-1zM19,52h2v1h-2zM23,52h3v1h-3zM27,52h2v1h-2zM30,52h1v1h-1zM32,52h1v1h-1zM36,52h2v1h-2zM40,52h2v1h-2zM44,52h1v1h-1zM46,52h2v1h-2zM51,52h1v1h-1zM54,52h1v1h-1zM56,52h3v1h-3zM63,52h2v1h-2zM68,52h1v1h-1zM2,53h2v1h-2zM7,53h1v1h-1zM10,53h2v1h-2zM13,53h2v1h-2zM16,53h1v1h-1zM20,53h3v1h-3zM24,53h1v1h-1zM30,53h2v1h-2zM34,53h1v1h-1zM38,53h1v1h-1zM41,53h2v1h-2zM45,53h1v1h-1zM47,53h1v1h-1zM52,53h1v1h-1zM54,53h1v1h-1zM56,53h8v1h-8zM65,53h2v1h-2zM69,53h1v1h-1zM3,54h3v1h-3zM11,54h4v1h-4zM16,54h3v1h-3zM20,54h3v1h-3zM24,54h1v1h-1zM27,54h3v1h-3zM31,54h2v1h-2zM34,54h1v1h-1zM38,54h3v1h-3zM44,54h1v1h-1zM47,54h1v1h-1zM49,54h1v1h-1zM51,54h1v1h-1zM53,54h2v1h-2zM59,54h2v1h-2zM65,54h1v1h-1zM1,55h1v1h-1zM3,55h1v1h-1zM6,55h4v1h-4zM12,55h1v1h-1zM14,55h1v1h-1zM16,55h2v1h-2zM19,55h6v1h-6zM26,55h1v1h-1zM30,55h4v1h-4zM38,55h5v1h-5zM44,55h1v1h-1zM46,55h3v1h-3zM50,55h4v1h-4zM55,55h1v1h-1zM57,55h2v1h-2zM61,55h1v1h-1zM63,55h2v1h-2zM68,55h2v1h-2zM2,56h2v1h-2zM6,56h1v1h-1zM8,56h1v1h-1zM10,56h3v1h-3zM15,56h1v1h-1zM18,56h4v1h-4zM23,56h1v1h-1zM25,56h2v1h-2zM29,56h2v1h-2zM32,56h3v1h-3zM36,56h1v1h-1zM38,56h1v1h-1zM41,56h1v1h-1zM43,56h2v1h-2zM47,56h1v1h-1zM50,56h1v1h-1zM52,56h1v1h-1zM57,56h1v1h-1zM59,56h2v1h-2zM63,56h2v1h-2zM67,56h3v1h-3zM2,57h3v1h-3zM6,57h2v1h-2zM10,57h1v1h-1zM12,57h2v1h-2zM15,57h2v1h-2zM19,57h2v1h-2zM22,57h2v1h-2zM27,57h2v1h-2zM31,57h1v1h-1zM34,57h1v1h-1zM37,57h1v1h-1zM39,57h1v1h-1zM42,57h1v1h-1zM44,57h2v1h-2zM47,57h1v1h-1zM50,57h3v1h-3zM54,57h1v1h-1zM56,57h3v1h-3zM60,57h2v1h-2zM64,57h2v1h-2zM68,57h1v1h-1zM2,58h1v1h-1zM4,58h1v1h-1zM8,58h1v1h-1zM11,58h1v1h-1zM13,58h1v1h-1zM16,58h1v1h-1zM18,58h2v1h-2zM21,58h3v1h-3zM27,58h3v1h-3zM31,58h4v1h-4zM39,58h4v1h-4zM44,58h6v1h-6zM52,58h1v1h-1zM54,58h1v1h-1zM58,58h4v1h-4zM63,58h7v1h-7zM3,59h1v1h-1zM5,59h4v1h-4zM10,59h1v1h-1zM13,59h1v1h-1zM15,59h2v1h-2zM18,59h3v1h-3zM23,59h1v1h-1zM26,59h1v1h-1zM33,59h1v1h-1zM36,59h1v1h-1zM41,59h2v1h-2zM44,59h1v1h-1zM46,59h1v1h-1zM48,59h1v1h-1zM51,59h4v1h-4zM56,59h1v1h-1zM60,59h2v1h-2zM63,59h2v1h-2zM67,59h1v1h-1zM69,59h1v1h-1zM1,60h1v1h-1zM8,60h1v1h-1zM12,60h3v1h-3zM19,60h3v1h-3zM23,60h1v1h-1zM25,60h1v1h-1zM27,60h2v1h-2zM31,60h1v1h-1zM34,60h1v1h-1zM37,60h1v1h-1zM39,60h1v1h-1zM41,60h2v1h-2zM44,60h4v1h-4zM51,60h1v1h-1zM53,60h3v1h-3zM58,60h1v1h-1zM61,60h1v1h-1zM63,60h3v1h-3zM67,60h2v1h-2zM1,61h1v1h-1zM5,61h1v1h-1zM7,61h6v1h-6zM14,61h1v1h-1zM16,61h2v1h-2zM19,61h2v1h-2zM22,61h3v1h-3zM26,61h6v1h-6zM33,61h6v1h-6zM41,61h1v1h-1zM44,61h2v1h-2zM49,61h2v1h-2zM52,61h1v1h-1zM54,61h1v1h-1zM56,61h4v1h-4zM61,61h6v1h-6zM69,61h1v1h-1zM9,62h2v1h-2zM12,62h1v1h-1zM14,62h1v1h-1zM16,62h1v1h-1zM23,62h4v1h-4zM28,62h2v1h-2zM33,62h1v1h-1zM37,62h1v1h-1zM41,62h1v1h-1zM43,62h1v1h-1zM47,62h3v1h-3zM53,62h3v1h-3zM57,62h2v1h-2zM60,62h2v1h-2zM1,63h7v1h-7zM9,63h1v1h-1zM11,63h1v1h-1zM13,63h1v1h-1zM15,63h1v1h-1zM17,63h1v1h-1zM19,63h1v1h-1zM21,63h1v1h-1zM23,63h1v1h-1zM25,63h1v1h-1zM27,63h1v1h-1zM29,63h1v1h-1zM31,63h1v1h-1zM33,63h1v1h-1zM35,63h1v1h-1zM37,63h1v1h-1zM39,63h1v1h-1zM41,63h1v1h-1zM43,63h1v1h-1zM45,63h1v1h-1zM47,63h1v1h-1zM49,63h1v1h-1zM51,63h1v1h-1zM53,63h1v1h-1zM55,63h1v1h-1zM57,63h1v1h-1zM59,63h1v1h-1zM61,63h1v1h-1zM63,63h7v1h-7zM1,64h1v1h-1zM7,64h1v1h-1zM9,64h2v1h-2zM12,64h2v1h-2zM16,64h2v1h-2zM19,64h1v1h-1zM26,64h6v1h-6zM33,64h1v1h-1zM37,64h1v1h-1zM39,64h2v1h-2zM42,64h1v1h-1zM44,64h2v1h-2zM47,64h1v1h-1zM51,64h2v1h-2zM57,64h3v1h-3zM63,64h1v1h-1zM69,64h1v1h-1zM1,65h1v1h-1zM3,65h3v1h-3zM7,65h1v1h-1zM9,65h5v1h-5zM15,65h2v1h-2zM19,65h1v1h-1zM21,65h1v1h-1zM23,65h2v1h-2zM26,65h3v1h-3zM31,65h1v1h-1zM33,65h6v1h-6zM40,65h2v1h-2zM46,65h3v1h-3zM50,65h1v1h-1zM52,65h1v1h-1zM54,65h1v1h-1zM56,65h4v1h-4zM61,65h1v1h-1zM63,65h1v1h-1zM65,65h3v1h-3zM69,65h1v1h-1zM1,66h1v1h-1zM3,66h3v1h-3zM7,66h1v1h-1zM9,66h2v1h-2zM12,66h1v1h-1zM15,66h2v1h-2zM19,66h1v1h-1zM21,66h3v1h-3zM26,66h5v1h-5zM35,66h7v1h-7zM44,66h1v1h-1zM46,66h2v1h-2zM49,66h5v1h-5zM56,66h1v1h-1zM61,66h1v1h-1zM63,66h1v1h-1zM65,66h3v1h-3zM69,66h1v1h-1zM1,67h1v1h-1zM3,67h3v1h-3zM7,67h1v1h-1zM13,67h1v1h-1zM15,67h1v1h-1zM17,67h1v1h-1zM23,67h1v1h-1zM25,67h1v1h-1zM27,67h2v1h-2zM30,67h2v1h-2zM34,67h2v1h-2zM37,67h1v1h-1zM40,67h4v1h-4zM47,67h2v1h-2zM50,67h1v1h-1zM52,67h1v1h-1zM54,67h6v1h-6zM63,67h1v1h-1zM65,67h3v1h-3zM69,67h1v1h-1zM1,68h1v1h-1zM7,68h1v1h-1zM10,68h3v1h-3zM15,68h1v1h-1zM17,68h3v1h-3zM21,68h1v1h-1zM23,68h2v1h-2zM28,68h2v1h-2zM31,68h1v1h-1zM34,68h1v1h-1zM37,68h3v1h-3zM41,68h2v1h-2zM44,68h1v1h-1zM47,68h2v1h-2zM57,68h2v1h-2zM63,68h1v1h-1zM69,68h1v1h-1zM1,69h7v1h-7zM9,69h3v1h-3zM15,69h1v1h-1zM17,69h2v1h-2zM20,69h2v1h-2zM26,69h1v1h-1zM28,69h1v1h-1zM30,69h1v1h-1zM32,69h1v1h-1zM37,69h3v1h-3zM41,69h3v1h-3zM46,69h3v1h-3zM50,69h1v1h-1zM52,69h2v1h-2zM55,69h3v1h-3zM59,69h3v1h-3zM63,69h7v1h-7z"
      },
      zalo: {
        size: 27,
        color: "#0068FF",
        path: "M1,1h7v1h-7zM9,1h1v1h-1zM11,1h1v1h-1zM13,1h1v1h-1zM15,1h2v1h-2zM18,1h1v1h-1zM20,1h6v1h-6zM1,2h1v1h-1zM7,2h1v1h-1zM10,2h1v1h-1zM13,2h2v1h-2zM16,2h3v1h-3zM20,2h3v1h-3zM25,2h1v1h-1zM1,3h1v1h-1zM3,3h3v1h-3zM7,3h1v1h-1zM9,3h2v1h-2zM14,3h2v1h-2zM17,3h1v1h-1zM22,3h2v1h-2zM25,3h1v1h-1zM1,4h1v1h-1zM3,4h3v1h-3zM7,4h1v1h-1zM9,4h1v1h-1zM13,4h2v1h-2zM16,4h4v1h-4zM21,4h5v1h-5zM1,5h1v1h-1zM3,5h3v1h-3zM7,5h1v1h-1zM9,5h1v1h-1zM12,5h1v1h-1zM16,5h6v1h-6zM23,5h1v1h-1zM25,5h1v1h-1zM1,6h1v1h-1zM7,6h1v1h-1zM9,6h1v1h-1zM12,6h1v1h-1zM15,6h1v1h-1zM17,6h1v1h-1zM21,6h2v1h-2zM25,6h1v1h-1zM1,7h7v1h-7zM10,7h4v1h-4zM17,7h1v1h-1zM19,7h1v1h-1zM21,7h1v1h-1zM23,7h3v1h-3zM9,8h1v1h-1zM11,8h1v1h-1zM14,8h4v1h-4zM21,8h2v1h-2zM1,9h1v1h-1zM3,9h3v1h-3zM7,9h3v1h-3zM11,9h1v1h-1zM13,9h2v1h-2zM17,9h5v1h-5zM23,9h1v1h-1zM1,10h1v1h-1zM3,10h4v1h-4zM8,10h4v1h-4zM13,10h2v1h-2zM16,10h2v1h-2zM19,10h3v1h-3zM25,10h1v1h-1zM1,11h1v1h-1zM5,11h1v1h-1zM7,11h1v1h-1zM9,11h3v1h-3zM14,11h5v1h-5zM20,11h3v1h-3zM24,11h2v1h-2zM1,12h2v1h-2zM5,12h1v1h-1zM8,12h2v1h-2zM11,12h1v1h-1zM13,12h1v1h-1zM15,12h1v1h-1zM17,12h1v1h-1zM20,12h1v1h-1zM22,12h1v1h-1zM24,12h1v1h-1zM1,13h1v1h-1zM3,13h5v1h-5zM9,13h3v1h-3zM15,13h2v1h-2zM18,13h4v1h-4zM23,13h3v1h-3zM5,14h1v1h-1zM8,14h1v1h-1zM10,14h1v1h-1zM12,14h3v1h-3zM16,14h4v1h-4zM21,14h1v1h-1zM25,14h1v1h-1zM1,15h2v1h-2zM4,15h4v1h-4zM9,15h1v1h-1zM11,15h3v1h-3zM16,15h2v1h-2zM19,15h1v1h-1zM21,15h2v1h-2zM24,15h2v1h-2zM1,16h3v1h-3zM5,16h2v1h-2zM10,16h2v1h-2zM14,16h2v1h-2zM20,16h1v1h-1zM24,16h1v1h-1zM1,17h1v1h-1zM3,17h5v1h-5zM10,17h1v1h-1zM13,17h1v1h-1zM15,17h1v1h-1zM19,17h5v1h-5zM9,18h2v1h-2zM12,18h4v1h-4zM17,18h1v1h-1zM1,19h7v1h-7zM9,19h1v1h-1zM11,19h1v1h-1zM13,19h1v1h-1zM15,19h1v1h-1zM17,19h1v1h-1zM19,19h7v1h-7zM1,20h1v1h-1zM7,20h1v1h-1zM9,20h2v1h-2zM14,20h1v1h-1zM16,20h2v1h-2zM19,20h1v1h-1zM25,20h1v1h-1zM1,21h1v1h-1zM3,21h3v1h-3zM7,21h1v1h-1zM9,21h1v1h-1zM11,21h1v1h-1zM15,21h2v1h-2zM19,21h1v1h-1zM21,21h3v1h-3zM25,21h1v1h-1zM1,22h1v1h-1zM3,22h3v1h-3zM7,22h1v1h-1zM9,22h5v1h-5zM15,22h3v1h-3zM19,22h1v1h-1zM21,22h3v1h-3zM25,22h1v1h-1zM1,23h1v1h-1zM3,23h3v1h-3zM7,23h1v1h-1zM9,23h2v1h-2zM16,23h1v1h-1zM19,23h1v1h-1zM21,23h3v1h-3zM25,23h1v1h-1zM1,24h1v1h-1zM7,24h1v1h-1zM10,24h1v1h-1zM13,24h1v1h-1zM16,24h1v1h-1zM19,24h1v1h-1zM25,24h1v1h-1zM1,25h7v1h-7zM11,25h4v1h-4zM19,25h7v1h-7z"
      },
      linkedin: {
        size: 35,
        color: "#0A66C2",
        path: "M1,1h7v1h-7zM9,1h3v1h-3zM14,1h1v1h-1zM16,1h1v1h-1zM18,1h1v1h-1zM23,1h1v1h-1zM25,1h2v1h-2zM28,1h1v1h-1zM30,1h1v1h-1zM32,1h1v1h-1zM1,2h1v1h-1zM7,2h1v1h-1zM10,2h1v1h-1zM12,2h5v1h-5zM22,2h3v1h-3zM26,2h2v1h-2zM29,2h3v1h-3zM1,3h1v1h-1zM3,3h3v1h-3zM7,3h1v1h-1zM9,3h2v1h-2zM13,3h1v1h-1zM15,3h4v1h-4zM21,3h8v1h-8zM30,3h1v1h-1zM1,4h1v1h-1zM3,4h3v1h-3zM7,4h1v1h-1zM9,4h1v1h-1zM12,4h1v1h-1zM14,4h1v1h-1zM16,4h1v1h-1zM18,4h5v1h-5zM24,4h1v1h-1zM26,4h1v1h-1zM29,4h5v1h-5zM1,5h1v1h-1zM3,5h3v1h-3zM7,5h1v1h-1zM9,5h2v1h-2zM13,5h1v1h-1zM15,5h1v1h-1zM17,5h1v1h-1zM23,5h1v1h-1zM25,5h6v1h-6zM33,5h1v1h-1zM1,6h1v1h-1zM7,6h1v1h-1zM9,6h1v1h-1zM12,6h2v1h-2zM15,6h2v1h-2zM18,6h2v1h-2zM21,6h5v1h-5zM29,6h4v1h-4zM1,7h7v1h-7zM11,7h3v1h-3zM16,7h3v1h-3zM22,7h1v1h-1zM24,7h2v1h-2zM27,7h1v1h-1zM29,7h1v1h-1zM31,7h2v1h-2zM9,8h1v1h-1zM14,8h1v1h-1zM17,8h6v1h-6zM24,8h2v1h-2zM29,8h1v1h-1zM31,8h1v1h-1zM33,8h1v1h-1zM1,9h1v1h-1zM5,9h3v1h-3zM9,9h2v1h-2zM12,9h2v1h-2zM18,9h2v1h-2zM23,9h1v1h-1zM25,9h5v1h-5zM1,10h1v1h-1zM3,10h1v1h-1zM6,10h1v1h-1zM9,10h1v1h-1zM11,10h5v1h-5zM17,10h1v1h-1zM20,10h1v1h-1zM22,10h3v1h-3zM26,10h2v1h-2zM30,10h4v1h-4zM1,11h1v1h-1zM3,11h2v1h-2zM6,11h4v1h-4zM11,11h1v1h-1zM13,11h3v1h-3zM26,11h1v1h-1zM32,11h1v1h-1zM1,12h4v1h-4zM8,12h1v1h-1zM10,12h2v1h-2zM13,12h2v1h-2zM16,12h3v1h-3zM20,12h1v1h-1zM23,12h3v1h-3zM27,12h1v1h-1zM30,12h1v1h-1zM33,12h1v1h-1zM1,13h2v1h-2zM4,13h2v1h-2zM7,13h2v1h-2zM10,13h3v1h-3zM14,13h1v1h-1zM19,13h2v1h-2zM29,13h2v1h-2zM1,14h2v1h-2zM5,14h1v1h-1zM11,14h1v1h-1zM13,14h2v1h-2zM17,14h1v1h-1zM22,14h1v1h-1zM24,14h1v1h-1zM27,14h6v1h-6zM2,15h7v1h-7zM12,15h1v1h-1zM16,15h1v1h-1zM19,15h1v1h-1zM21,15h1v1h-1zM26,15h4v1h-4zM31,15h2v1h-2zM1,16h1v1h-1zM3,16h1v1h-1zM8,16h1v1h-1zM13,16h2v1h-2zM19,16h4v1h-4zM24,16h5v1h-5zM30,16h2v1h-2zM33,16h1v1h-1zM5,17h4v1h-4zM11,17h6v1h-6zM18,17h1v1h-1zM20,17h1v1h-1zM23,17h4v1h-4zM28,17h2v1h-2zM33,17h1v1h-1zM2,18h2v1h-2zM8,18h1v1h-1zM11,18h1v1h-1zM13,18h4v1h-4zM20,18h3v1h-3zM25,18h7v1h-7zM7,19h1v1h-1zM10,19h1v1h-1zM13,19h2v1h-2zM16,19h3v1h-3zM21,19h1v1h-1zM23,19h1v1h-1zM26,19h2v1h-2zM30,19h3v1h-3zM1,20h3v1h-3zM5,20h2v1h-2zM8,20h2v1h-2zM11,20h1v1h-1zM14,20h1v1h-1zM16,20h1v1h-1zM18,20h2v1h-2zM24,20h2v1h-2zM27,20h1v1h-1zM30,20h1v1h-1zM32,20h2v1h-2zM3,21h2v1h-2zM6,21h2v1h-2zM9,21h2v1h-2zM12,21h1v1h-1zM15,21h1v1h-1zM17,21h1v1h-1zM20,21h1v1h-1zM23,21h2v1h-2zM26,21h1v1h-1zM28,21h3v1h-3zM32,21h2v1h-2zM2,22h3v1h-3zM6,22h1v1h-1zM9,22h2v1h-2zM12,22h3v1h-3zM17,22h8v1h-8zM26,22h1v1h-1zM29,22h3v1h-3zM33,22h1v1h-1zM1,23h2v1h-2zM4,23h2v1h-2zM7,23h2v1h-2zM11,23h1v1h-1zM14,23h5v1h-5zM23,23h1v1h-1zM25,23h2v1h-2zM29,23h1v1h-1zM31,23h1v1h-1zM2,24h2v1h-2zM8,24h2v1h-2zM12,24h1v1h-1zM14,24h2v1h-2zM17,24h4v1h-4zM22,24h1v1h-1zM24,24h1v1h-1zM27,24h2v1h-2zM30,24h2v1h-2zM33,24h1v1h-1zM1,25h1v1h-1zM3,25h5v1h-5zM10,25h1v1h-1zM12,25h1v1h-1zM14,25h2v1h-2zM18,25h1v1h-1zM20,25h1v1h-1zM23,25h1v1h-1zM25,25h1v1h-1zM27,25h5v1h-5zM9,26h1v1h-1zM11,26h1v1h-1zM17,26h1v1h-1zM20,26h5v1h-5zM1,27h7v1h-7zM9,27h1v1h-1zM11,27h1v1h-1zM13,27h1v1h-1zM15,27h1v1h-1zM17,27h1v1h-1zM19,27h1v1h-1zM21,27h1v1h-1zM23,27h1v1h-1zM25,27h1v1h-1zM27,27h7v1h-7zM1,28h1v1h-1zM7,28h1v1h-1zM9,28h1v1h-1zM11,28h2v1h-2zM14,28h1v1h-1zM18,28h3v1h-3zM22,28h1v1h-1zM25,28h1v1h-1zM27,28h1v1h-1zM33,28h1v1h-1zM1,29h1v1h-1zM3,29h3v1h-3zM7,29h1v1h-1zM9,29h2v1h-2zM15,29h3v1h-3zM21,29h1v1h-1zM23,29h2v1h-2zM27,29h1v1h-1zM29,29h3v1h-3zM33,29h1v1h-1zM1,30h1v1h-1zM3,30h3v1h-3zM7,30h1v1h-1zM9,30h3v1h-3zM13,30h1v1h-1zM16,30h1v1h-1zM19,30h2v1h-2zM24,30h2v1h-2zM27,30h1v1h-1zM29,30h3v1h-3zM33,30h1v1h-1zM1,31h1v1h-1zM3,31h3v1h-3zM7,31h1v1h-1zM9,31h2v1h-2zM15,31h1v1h-1zM20,31h4v1h-4zM27,31h1v1h-1zM29,31h3v1h-3zM33,31h1v1h-1zM1,32h1v1h-1zM7,32h1v1h-1zM11,32h1v1h-1zM16,32h1v1h-1zM19,32h1v1h-1zM22,32h1v1h-1zM25,32h1v1h-1zM27,32h1v1h-1zM33,32h1v1h-1zM1,33h7v1h-7zM11,33h3v1h-3zM15,33h1v1h-1zM17,33h1v1h-1zM19,33h4v1h-4zM24,33h1v1h-1zM27,33h7v1h-7z"
      }
    };

let currentVCardTab = 'vcard';

function switchVCardTab(type) {
  currentVCardTab = type;
  ['vcard', 'zalo', 'linkedin'].forEach(t => {
    const btn = document.getElementById(`vtab-${t}`);
    if (btn) btn.classList.toggle('active', t === type);
  });
  const qrData = QR_SVG_DATA[type] || QR_SVG_DATA.vcard;
  const container = document.getElementById('vcard-qr-container');
  if (container) {
    container.innerHTML = `<svg viewBox="0 0 ${qrData.size} ${qrData.size}" shape-rendering="crispEdges" role="img" aria-label="${type} QR Code"><rect width="${qrData.size}" height="${qrData.size}" fill="#ffffff"/><path d="${qrData.path}" fill="${qrData.color}"/></svg>`;
  }
  const hintEl = document.getElementById('vcard-scan-hint');
  if (hintEl) {
    if (type === 'vcard') {
      hintEl.innerText = 'Đưa Camera iPhone vào quét để lưu thẳng Danh bạ trong 1 giây';
    } else if (type === 'zalo') {
      hintEl.innerText = 'Quét bằng Camera hoặc Zalo để nhắn tin trực tiếp với Quang Trí (Bryan)';
    } else {
      hintEl.innerText = 'Quét để mở hồ sơ LinkedIn chính thức của Bryan Nguyen';
    }
  }
}

function openVCardModal() {
  switchVCardTab(currentVCardTab);
  const modal = document.getElementById('vcard-modal-backdrop');
  if (modal) {
    modal.classList.add('open');
    document.body.style.overflow = 'hidden';
  }
}

function closeVCardModal() {
  const modal = document.getElementById('vcard-modal-backdrop');
  if (modal) {
    modal.classList.remove('open');
    document.body.style.overflow = '';
  }
}

function downloadVCard() {
  const vcfContent = [
    "BEGIN:VCARD",
    "VERSION:3.0",
    "N:Nguyen;Bryan (Huynh Quang Tri);;;",
    "FN:Bryan Nguyen (Nguyen Huynh Quang Tri)",
    "ORG:Payoo (VietUnion)",
    "TITLE:Enterprise B2B & Fintech Executive",
    "TEL;TYPE=CELL,VOICE:+84838673639",
    "EMAIL;TYPE=WORK,INTERNET:quangtritc1805@gmail.com",
    "URL:https://bryanportfolio.io.vn/",
    "ITEM1.URL:https://www.linkedin.com/in/bryan-nguyen-796a7b1ab/",
    "ITEM1.X-ABLabel:LinkedIn",
    "ITEM2.URL:https://zalo.me/0838673639",
    "ITEM2.X-ABLabel:Zalo",
    "ADR;TYPE=WORK:;;Ho Chi Minh City;;;Vietnam",
    "NOTE:Enterprise B2B Development & FinTech Infrastructure | Master of Business Analytics (UOW)",
    "END:VCARD"
  ].join("\r\n");

  const blob = new Blob([vcfContent], { type: "text/vcard;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "Bryan_Nguyen_Payoo_vCard.vcf";
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  setTimeout(() => URL.revokeObjectURL(url), 1500);
}

function copyVCardLink() {
  const url = "https://bryanportfolio.io.vn/";
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(url);
  }
  alert('Đã sao chép link Bryan Portfolio: ' + url);
}

// Floating Action Menu Toggle
function toggleFabMenu(event) {
  if (event) event.stopPropagation();
  const fw = document.getElementById('floating-widget');
  if (fw) fw.classList.toggle('menu-open');
}

function closeFabMenu() {
  const fw = document.getElementById('floating-widget');
  if (fw) fw.classList.remove('menu-open');
}

// Back To Top Controller
function scrollToTop() {
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Global Scroll Handler
window.addEventListener('scroll', () => {
  const btn = document.getElementById('backToTopBtn');
  if (btn) {
    if (window.scrollY > 350) {
      btn.classList.add('show');
    } else {
      btn.classList.remove('show');
    }
  }
}, { passive: true });

// Centralized Click & Event Delegation
document.addEventListener('click', (e) => {
  // Floating widget close on outside click
  const fw = document.getElementById('floating-widget');
  if (fw && fw.classList.contains('menu-open') && !fw.contains(e.target)) {
    closeFabMenu();
  }

  // 1. Drawer close
  if (e.target.closest('#drawerCloseBtn') || e.target.matches('#drawerBackdrop')) {
    closeDrawer();
    return;
  }
  // 2. vCard modal close
  if (e.target.closest('.vcard-close-btn') || e.target.matches('#vcard-modal-backdrop')) {
    closeVCardModal();
    return;
  }
  // 3. Floating menu close on outside click
  if (!e.target.closest('#floating-widget')) {
    closeFabMenu();
  }
  // 4. Back to top button
  if (e.target.closest('#backToTopBtn')) {
    e.preventDefault();
    scrollToTop();
    return;
  }
  // 5. FAB toggle button
  if (e.target.closest('#fabToggleBtn')) {
    e.preventDefault();
    toggleFabMenu(e);
    return;
  }
  // 6. vCard triggers
  if (e.target.closest('.float-btn-vcard, [data-vcard-trigger], .ms-vcard-trigger')) {
    e.preventDefault();
    openVCardModal();
    closeFabMenu();
    return;
  }
});

// Escape key listener for all drawers and modals
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    closeDrawer();
    closeVCardModal();
    closeFabMenu();
  }
});

// EXPLICIT WINDOW EXPORTS (Guarantee inline handlers work 100%)
window.openDrawer = openDrawer;
window.closeDrawer = closeDrawer;
window.openPulseDetail = openPulseDetail;
window.openArticleReader = openArticleReader;
window.openDecisionSignalDrawer = openDecisionSignalDrawer;
window.openMacroChainDrawer = openMacroChainDrawer;
window.openArchiveDrawer = openArchiveDrawer;
window.openSheetsSchemaModal = openSheetsSchemaModal;
window.switchFintechTab = switchFintechTab;
window.initFintechTabs = initFintechTabs;
window.openMobileDrawer = openMobileDrawer;
window.closeMobileDrawer = closeMobileDrawer;
window.openVCardModal = openVCardModal;
window.closeVCardModal = closeVCardModal;
window.switchVCardTab = switchVCardTab;
window.downloadVCard = downloadVCard;
window.copyVCardLink = copyVCardLink;
window.toggleFabMenu = toggleFabMenu;
window.closeFabMenu = closeFabMenu;
window.scrollToTop = scrollToTop;

console.log('[MagSpread] All P0 Drawer, Modal & Contact controllers successfully exported to window.');


/* ==========================================================================
   V2.2.3 R1: INDEPENDENT POPUP SYSTEMS (CONTACT POPUP & EDITORIAL WELCOME)
   ========================================================================== */

function openContactModal() {
  closeWelcomeModal();
  closeDrawer();
  switchVCardTab(currentVCardTab);
  const modal = document.getElementById('contact-modal-backdrop') || document.getElementById('vcard-modal-backdrop');
  if (modal) {
    modal.classList.add('open');
    document.body.style.overflow = 'hidden';
  }
}

function closeContactModal() {
  const modal = document.getElementById('contact-modal-backdrop') || document.getElementById('vcard-modal-backdrop');
  if (modal) {
    modal.classList.remove('open');
    const isOtherModalOpen = document.querySelector('.vcard-modal-backdrop.open, .ms-modal-backdrop.open, .ms-drawer.open');
    if (!isOtherModalOpen) {
      document.body.style.overflow = '';
    }
  }
}

function openVCardModal() {
  openContactModal();
}

function closeVCardModal() {
  closeContactModal();
}

function toggleFabMenu(event) {
  if (event) event.stopPropagation();
  const fw = document.getElementById('floating-widget');
  if (fw) fw.classList.toggle('menu-open');
}

function closeFabMenu() {
  const fw = document.getElementById('floating-widget');
  if (fw) fw.classList.remove('menu-open');
}

// ─── EDITORIAL WELCOME MODAL CONTROLLERS (R3 RESTORATION) ───
function openWelcomeModal() {
  closeContactModal();
  closeDrawer();
  const modal = document.getElementById('welcome-modal-backdrop');
  if (modal) {
    modal.classList.add('open');
    document.body.style.overflow = 'hidden';
  }
}

function closeWelcomeModal() {
  const modal = document.getElementById('welcome-modal-backdrop');
  if (modal) {
    modal.classList.remove('open');
    const isOtherModalOpen = document.querySelector('.ms-modal-backdrop.open, .ms-drawer.open, .vcard-modal-backdrop.open');
    if (!isOtherModalOpen) {
      document.body.style.overflow = '';
    }
  }
  try {
    sessionStorage.setItem('bryan_fintech_welcome_shown', 'true');
  } catch (e) {}
}

function checkWelcomeModalOnLoad() {
  try {
    const shown = sessionStorage.getItem('bryan_fintech_welcome_shown');
    if (!shown) {
      setTimeout(() => {
        openWelcomeModal();
      }, 400);
    }
  } catch (e) {
    console.warn('[MagSpread] Session storage inaccessible:', e);
  }
}

// Global click event delegation for V2.2.3 R1
document.addEventListener('click', (e) => {
  // Floating widget close on outside click
  const fw = document.getElementById('floating-widget');
  if (fw && fw.classList.contains('menu-open') && !fw.contains(e.target)) {
    closeFabMenu();
  }

  // 1. Floating Contact Launcher or Contact Triggers
  if (e.target.closest('#floatingContactLauncher, .ms-contact-trigger, [data-contact-trigger]')) {
    e.preventDefault();
    openContactModal();
    return;
  }

  // 2. Welcome trigger button (e.g. in Masthead)
  if (e.target.closest('#btnOpenWelcomeIntro')) {
    e.preventDefault();
    openWelcomeModal();
    return;
  }

  // 3. Contact modal backdrop click
  if (e.target.matches('#contact-modal-backdrop')) {
    closeContactModal();
    return;
  }

  // 4. Welcome modal backdrop click
  if (e.target.matches('#welcome-modal-backdrop')) {
    closeWelcomeModal();
    return;
  }
});

// Update Escape key handler for all overlays
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    closeContactModal();
    closeWelcomeModal();
    closeVCardModal();
    closeDrawer();
  }
});

// Window Exports
window.openContactModal = openContactModal;
window.closeContactModal = closeContactModal;
window.openWelcomeModal = openWelcomeModal;
window.closeWelcomeModal = closeWelcomeModal;
window.checkWelcomeModalOnLoad = checkWelcomeModalOnLoad;

// Trigger welcome check on initialization
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    checkWelcomeModalOnLoad();
  });
} else {
  checkWelcomeModalOnLoad();
}

console.log('[MagSpread] V2.2.3 R1 Contact & Welcome modal controllers successfully registered.');
