/**
 * Bryan News | Fintech Intelligence — V4.0 Clean Institutional UI Pilot
 * Isolated preview reading live ../edition-data.json with ../edition-data.js fallback.
 */
'use strict';

(() => {
  const CATEGORIES = [
    { key: 'Thanh toán', label: 'Thanh toán số' },
    { key: 'Ngân hàng', label: 'Ngân hàng' },
    { key: 'Thị trường vốn', label: 'Thị trường vốn' },
    { key: 'Doanh nghiệp', label: 'Doanh nghiệp' },
    { key: 'Kinh tế vĩ mô', label: 'Kinh tế vĩ mô' },
    { key: 'Bán lẻ, D2C và xu hướng tiêu dùng', label: 'Bán lẻ & Tiêu dùng' }
  ];

  const CAT_LABEL_MAP = Object.fromEntries(CATEGORIES.map(c => [c.key, c.label]));

  const V4_FALLBACK_IMG =
    'data:image/svg+xml;charset=UTF-8,' +
    encodeURIComponent(
      '<svg xmlns="http://www.w3.org/2000/svg" width="800" height="450" viewBox="0 0 800 450">' +
        '<rect width="800" height="450" fill="#F8FAFC"/>' +
        '<rect x="36" y="36" width="728" height="378" fill="none" stroke="#E5E7EB" stroke-width="2"/>' +
        '<text x="400" y="218" text-anchor="middle" font-family="Georgia, serif" font-size="28" font-weight="700" fill="#0A3D7A">Bnews Fintech</text>' +
        '<text x="400" y="252" text-anchor="middle" font-family="sans-serif" font-size="14" fill="#6B7280">Clean Institutional Intelligence</text>' +
      '</svg>'
    );

  const state = {
    data: null,
    activePage: 'today',
    activeCategory: 'ALL',
    searchTerm: '',
    activeChainIdx: 0,
    activeLayerIdx: 0,
    nlLoaded: false,
    newsById: {}
  };

  const $ = (sel) => document.querySelector(sel);
  const $$ = (sel) => Array.from(document.querySelectorAll(sel));

  function esc(str) {
    if (str === null || str === undefined) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function catLabel(rawCat) {
    return CAT_LABEL_MAP[rawCat] || rawCat || 'Tài chính';
  }

  function sourceLabel(item) {
    return item.originalSourceName || item.publisher || item.sourceName || 'Báo chí chính thống';
  }

  function extractTimeHM(item) {
    const iso = item.originalSourcePublishedAt || item.originalPublishedAt || '';
    const mIso = String(iso).match(/T(\d{2}:\d{2})/);
    if (mIso) return mIso[1];
    const pub = item.publisherPublishedAt || item.publicationTimestamp || '';
    const mPub = String(pub).match(/(\d{2}:\d{2})/);
    return mPub ? mPub[1] : '--:--';
  }

  function extractDateTimeReadable(item) {
    const pub = String(item.publisherPublishedAt || '').trim();
    const mPub = pub.match(/^(\d{2}\/\d{2}\/\d{4}\s+\d{2}:\d{2})/);
    if (mPub) return mPub[1];
    const iso = String(item.originalSourcePublishedAt || item.originalPublishedAt || '').trim();
    const m = iso.match(/^(\d{4})-(\d{2})-(\d{2})T(\d{2}:\d{2})/);
    if (m) return `${m[3]}/${m[2]}/${m[1]} ${m[4]}`;
    return state.data?.editionDate || '';
  }

  function imgTag(src, alt, cls) {
    const safeSrc = src && /^https?:|^data:|^\./.test(src) ? src : V4_FALLBACK_IMG;
    return `<img src="${esc(safeSrc)}" alt="${esc(alt)}" class="${cls}" loading="lazy" onerror="this.onerror=null;this.src='${V4_FALLBACK_IMG}'">`;
  }

  // ─── DATA LOADER ──────────────────────────────────────────────────────────
  async function loadEditionData() {
    try {
      const resp = await fetch(`../edition-data.json?v=${Date.now()}`, { cache: 'no-store' });
      if (resp.ok) {
        return await resp.json();
      }
    } catch (_) {
      // Fall back silently to window.EDITION_DATA
    }
    return window.EDITION_DATA || null;
  }

  // ─── HEADER & MARKET PULSE (44PX) ─────────────────────────────────────────
  function renderMasthead() {
    const d = state.data;
    const dateEl = $('#v4Date');
    const edEl = $('#v4EditionLabel');
    const drawerBadgeEl = $('#v4DrawerEditionBadge');
    const footerEl = $('#v4FooterNote');

    if (dateEl && (d.dayOfWeek || d.editionDate)) {
      const dow = String(d.dayOfWeek || '')
        .toLowerCase()
        .replace(/(^|\s)\S/g, (ch) => ch.toUpperCase());
      dateEl.textContent = `${dow ? dow + ', ' : ''}${d.editionDate || ''}`;
    }
    if (edEl && d.editionNumber) {
      const rawEd = String(d.editionNumber);
      const mNum = rawEd.match(/(\d+)/);
      edEl.textContent = mNum ? `Ấn bản số ${mNum[1]}` : rawEd;
      if (drawerBadgeEl) {
        const cleanBadge = rawEd
          .replace(/ẤN BẢN SỐ/gi, 'Ấn bản số')
          .replace(/PHIÊN CHIỀU/gi, 'Phiên chiều')
          .replace(/PHIÊN SÁNG/gi, 'Phiên sáng');
        drawerBadgeEl.textContent = cleanBadge;
      }
    }
    if (footerEl && d.editionId) {
      footerEl.textContent = `Bnews | Fintech Intelligence — Giao diện Pilot V4.0 · ${d.editionId} (${d.editionDate || ''}). Nguồn tin tổng hợp từ báo chí kinh tế chính thống.`;
    }
  }

  function formatPulseParts(m) {
    const sl = String(m.shortLabel || m.label || '').toUpperCase();
    const rawVal = String(m.value || '');
    const rawDelta = String(m.compactDelta || '');

    let shortName = m.shortLabel || m.label || 'Chỉ số';
    let cleanVal = rawVal;
    let cleanDelta = '';
    let tone = 'is-neutral';

    if (sl.includes('USD')) {
      shortName = 'USD/VND';
      cleanVal = rawVal.replace(/\s*VND\/USD/i, '').trim();
      const mDelta = rawDelta.match(/^([+-]?\d[\d.,]*đ)/i);
      cleanDelta = mDelta ? `(${mDelta[1]})` : rawDelta ? `(${rawDelta})` : '';
      tone = m.status === 'negative' ? 'is-down' : m.status === 'positive' ? 'is-up' : 'is-neutral';
    } else if (sl.includes('LÃI SUẤT')) {
      shortName = 'Lãi suất 12T';
      cleanVal = rawVal.replace(/\s*%\/năm/i, '%').replace(/\s+%/g, '%').trim();
      cleanDelta = '';
      tone = 'is-neutral';
    } else if (sl.includes('VN-INDEX')) {
      shortName = 'VN-Index';
      cleanVal = rawVal.replace(/\s*Điểm/i, '').trim();
      const mPct = rawDelta.match(/\(([+-]?[\d.,]+%)\)/);
      cleanDelta = mPct ? `(${mPct[1]})` : rawDelta ? `(${rawDelta})` : '';
      tone = cleanDelta.includes('-') || m.status === 'negative' ? 'is-down' : 'is-up';
    } else if (sl.includes('KHÁCH')) {
      shortName = 'Khách QT';
      cleanVal = rawVal.replace(/\s*Triệu lượt/i, 'M').replace(/\s+M$/i, 'M').trim();
      const mYoy = rawDelta.match(/([+-]?[\d.,]+%)/);
      cleanDelta = mYoy ? `(${mYoy[1]})` : rawDelta ? `(${rawDelta})` : '';
      tone = m.status === 'positive' ? 'is-up' : m.status === 'negative' ? 'is-down' : 'is-neutral';
    }

    return { shortName, cleanVal, cleanDelta, tone };
  }

  function renderPulseStrip() {
    const track = $('#v4PulseTrack');
    const items = state.data.marketPulseSnapshot || [];
    if (!track || !items.length) return;

    track.innerHTML = items
      .map((m, idx) => {
        const p = formatPulseParts(m);
        return `
          <button type="button" class="v4-pulse-item" data-mp-idx="${idx}" title="Bấm xem nguồn đối soát ${esc(p.shortName)}">
            <span class="v4-pulse-name">${esc(p.shortName)}</span>
            <span class="v4-pulse-val">${esc(p.cleanVal)}</span>
            ${p.cleanDelta ? `<span class="v4-pulse-delta ${p.tone}">${esc(p.cleanDelta)}</span>` : ''}
          </button>
        `;
      })
      .join('');

    track.querySelectorAll('.v4-pulse-item').forEach((btn) => {
      btn.addEventListener('click', () => {
        const idx = Number(btn.dataset.mpIdx);
        openMarketPulseDrawer(items[idx]);
      });
    });
  }

  // ─── B1. TRANG NHẤT 3 CỘT (25% | 50% | 25%) ─────────────────────────────────
  function parseSynthesisPoints(synthStr) {
    if (!synthStr) return [];
    const cleaned = String(synthStr)
      .replace(/^Toàn cảnh phiên[^:]*:\s*/i, '')
      .trim();
    const matches = cleaned.match(/\(\d\)\s*[^;]+(?:;|$)/g);
    if (!matches || !matches.length) {
      return [{ num: '01', title: 'Đúc kết thị trường', body: cleaned }];
    }
    return matches.slice(0, 4).map((rawItem, idx) => {
      const noPrefix = rawItem.replace(/^\(\d\)\s*/, '').replace(/;$/, '').trim();
      const colonIdx = noPrefix.indexOf(':');
      if (colonIdx > 0 && colonIdx < 80) {
        return {
          num: `0${idx + 1}`,
          title: noPrefix.slice(0, colonIdx).trim(),
          body: noPrefix.slice(colonIdx + 1).trim()
        };
      }
      return {
        num: `0${idx + 1}`,
        title: `Mạch chuyển động ${idx + 1}`,
        body: noPrefix
      };
    });
  }

  function renderFrontPage() {
    const cs = state.data.editorialSections?.sec02_coverStory || {};
    const newsList = state.data.eligibleNewsList || [];
    const leadId = cs.leadArticle?.eventId || newsList[0]?.eventId;
    const leadItem = state.newsById[leadId] || cs.leadArticle || newsList[0];

    // Cột trái (25%): Đúc kết 4 mạch phiên 01 -> 04
    const synthCol = $('#v4SynthesisCol');
    if (synthCol) {
      const points = parseSynthesisPoints(cs.editorialSynthesis);
      synthCol.innerHTML = `
        <div class="v4-col-label">
          <span>Đúc kết 4 mạch phiên</span>
          <span class="v4-col-label-sub">25 tin</span>
        </div>
        <div class="v4-synth-list">
          ${points
            .map(
              (pt) => `
            <div class="v4-synth-item">
              <div class="v4-synth-num">${esc(pt.num)}</div>
              <div>
                <h3 class="v4-synth-title">${esc(pt.title)}</h3>
                <p class="v4-synth-desc">${esc(pt.body)}</p>
              </div>
            </div>
          `
            )
            .join('')}
        </div>
      `;
    }

    // Cột giữa (50%): Bài đinh trang nhất (không có nhãn XÁC MINH 100%)
    const coverCol = $('#v4CoverCol');
    if (coverCol && leadItem) {
      const coverTitle = cs.editorialHeadline || leadItem.headline || leadItem.title;
      const coverSapo = cs.editorialSubheadline || leadItem.summary || cs.dek || '';
      const coverImg = leadItem.imageUrl || cs.imageUrl;
      const categoryTxt = catLabel(leadItem.category || 'Ngân hàng');
      const srcTxt = sourceLabel(leadItem);
      const timeTxt = extractDateTimeReadable(leadItem);

      coverCol.innerHTML = `
        <article class="v4-cover-card">
          <button type="button" class="v4-cover-img-btn" data-open-event="${esc(leadItem.eventId)}" aria-label="Đọc bài đinh: ${esc(coverTitle)}">
            ${imgTag(coverImg, coverTitle, 'v4-cover-img')}
          </button>
          <div class="v4-cover-kicker">
            <span class="v4-crimson-tag">${esc(categoryTxt)} · Tiêu điểm</span>
          </div>
          <h1 class="v4-cover-headline" data-open-event="${esc(leadItem.eventId)}">${esc(coverTitle)}</h1>
          <p class="v4-cover-sapo">${esc(coverSapo)}</p>
          <div class="v4-article-meta">
            <span>${esc(srcTxt)}</span>
            <span aria-hidden="true">·</span>
            <span class="v4-mono-time">${esc(timeTxt)}</span>
            <button type="button" class="v4-read-inline-btn" data-open-event="${esc(leadItem.eventId)}">Đọc phân tích chi tiết &rarr;</button>
          </div>
        </article>
      `;
    }

    // Cột phải (25%): Dòng tin mới 0-24h (6 tin mới nhất, không trùng bài đinh)
    const feedCol = $('#v4LatestFeedCol');
    if (feedCol) {
      const latestSix = newsList
        .filter((n) => n.eventId !== leadId)
        .slice()
        .sort((a, b) => (b.originalSourcePublishedAt || '').localeCompare(a.originalSourcePublishedAt || ''))
        .slice(0, 6);

      feedCol.innerHTML = `
        <div class="v4-col-label">
          <span>Dòng tin mới 0–24h</span>
          <span class="v4-col-label-sub">Quét nhanh</span>
        </div>
        <div class="v4-feed-list">
          ${latestSix
            .map(
              (item) => `
            <article class="v4-feed-item" data-open-event="${esc(item.eventId)}">
              <div class="v4-feed-meta">
                <span class="v4-crimson-tag">${esc(catLabel(item.category))}</span>
                <span class="v4-mono-time">${esc(extractTimeHM(item))}</span>
              </div>
              <h3 class="v4-feed-title">${esc(item.headline || item.title)}</h3>
            </article>
          `
            )
            .join('')}
        </div>
      `;
    }
  }

  // ─── B2. 6 CHUYÊN MỤC TIN TỨC (KHÔNG TRÙNG BÀI ĐINH) ───────────────────────
  function renderCategoryClusters() {
    const mount = $('#v4CategoriesMount');
    if (!mount) return;

    const cs = state.data.editorialSections?.sec02_coverStory || {};
    const leadId = cs.leadArticle?.eventId;
    const newsList = (state.data.eligibleNewsList || []).filter((n) => n.eventId !== leadId);

    const grouped = CATEGORIES.map((cat) => {
      const items = newsList
        .filter((n) => n.category === cat.key)
        .sort((a, b) => (b.originalSourcePublishedAt || '').localeCompare(a.originalSourcePublishedAt || ''));
      return { ...cat, items };
    }).filter((g) => g.items.length > 0);

    const richGroups = grouped.filter((g) => g.items.length >= 4);
    const sparseGroups = grouped.filter((g) => g.items.length < 4);

    let html = richGroups
      .map((g) => {
        const first = g.items[0];
        const nextThree = g.items.slice(1, 4);
        const extras = g.items.slice(4);
        return `
        <div class="v4-cat-cluster" data-cat-cluster="${esc(g.key)}">
          <div class="v4-cat-cluster-head">
            <h2 class="v4-cat-heading">${esc(g.label)}</h2>
            <div class="v4-cat-actions">
              <span class="v4-cat-count">${g.items.length} bản tin</span>
              <button type="button" class="v4-cat-more-btn" data-filter-cat="${esc(g.key)}">Xem chuyên mục &rarr;</button>
            </div>
          </div>

          <div class="v4-cat-rich-grid">
            <article class="v4-cat-lead" data-open-event="${esc(first.eventId)}">
              <div class="v4-thumb-wrap">${imgTag(first.imageUrl, first.headline, 'v4-thumb-img')}</div>
              <div>
                <h3 class="v4-cat-lead-title">${esc(first.headline || first.title)}</h3>
                <p class="v4-cat-lead-sapo">${esc(first.summary || '')}</p>
                <div class="v4-article-meta">
                  <span>${esc(sourceLabel(first))}</span>
                  <span aria-hidden="true">·</span>
                  <span class="v4-mono-time">${esc(extractTimeHM(first))}</span>
                </div>
              </div>
            </article>

            <div class="v4-cat-stack">
              ${nextThree
                .map(
                  (it) => `
                <article class="v4-cat-stack-item" data-open-event="${esc(it.eventId)}">
                  <h4 class="v4-cat-stack-title">${esc(it.headline || it.title)}</h4>
                  <div class="v4-article-meta">
                    <span>${esc(sourceLabel(it))}</span>
                    <span aria-hidden="true">·</span>
                    <span class="v4-mono-time">${esc(extractTimeHM(it))}</span>
                  </div>
                </article>
              `
                )
                .join('')}
            </div>
          </div>

          ${
            extras.length
              ? `
            <div class="v4-cat-extra-wrap">
              <div class="v4-cat-extra-grid">
                ${extras
                  .map(
                    (it) => `
                  <article class="v4-cat-extra-item" data-open-event="${esc(it.eventId)}">
                    <h4 class="v4-cat-extra-title">${esc(it.headline || it.title)}</h4>
                    <div class="v4-article-meta">
                      <span>${esc(sourceLabel(it))}</span>
                      <span aria-hidden="true">·</span>
                      <span class="v4-mono-time">${esc(extractTimeHM(it))}</span>
                    </div>
                  </article>
                `
                  )
                  .join('')}
              </div>
            </div>
          `
              : ''
          }
        </div>
      `;
      })
      .join('');

    if (sparseGroups.length) {
      html += `
        <div class="v4-sparse-grid">
          ${sparseGroups
            .map((g) => {
              const first = g.items[0];
              const rest = g.items.slice(1);
              return `
              <div class="v4-sparse-cluster" data-cat-cluster="${esc(g.key)}">
                <div class="v4-cat-cluster-head">
                  <h2 class="v4-cat-heading">${esc(g.label)}</h2>
                  <button type="button" class="v4-cat-more-btn" data-filter-cat="${esc(g.key)}">Mở rộng &rarr;</button>
                </div>
                <article class="v4-sparse-card" data-open-event="${esc(first.eventId)}">
                  <div class="v4-thumb-wrap">${imgTag(first.imageUrl, first.headline, 'v4-thumb-img')}</div>
                  <div>
                    <h3 class="v4-sparse-title">${esc(first.headline || first.title)}</h3>
                    <p class="v4-cat-lead-sapo">${esc(first.summary || '')}</p>
                    <div class="v4-article-meta">
                      <span>${esc(sourceLabel(first))}</span>
                      <span aria-hidden="true">·</span>
                      <span class="v4-mono-time">${esc(extractTimeHM(first))}</span>
                    </div>
                  </div>
                </article>
                ${
                  rest.length
                    ? `<div class="v4-cat-stack" style="border-left:none; padding-left:0; margin-top:12px;">
                        ${rest
                          .map(
                            (it) => `
                          <article class="v4-cat-stack-item" data-open-event="${esc(it.eventId)}">
                            <h4 class="v4-cat-stack-title">${esc(it.headline || it.title)}</h4>
                            <div class="v4-article-meta">
                              <span>${esc(sourceLabel(it))}</span>
                              <span aria-hidden="true">·</span>
                              <span class="v4-mono-time">${esc(extractTimeHM(it))}</span>
                            </div>
                          </article>
                        `
                          )
                          .join('')}
                      </div>`
                    : ''
                }
              </div>
            `;
            })
            .join('')}
        </div>
      `;
    }

    mount.innerHTML = html;
  }

  // ─── C1. CHUỖI TRUYỀN DẪN VĨ MÔ -> VI MÔ (CHẤT TẠP CHÍ 7 BƯỚC NGANG) ────────
  function renderMacroMicro() {
    const chains = state.data.editorialSections?.sec06_macroToMicro?.chains || [];
    const tabsEl = $('#v4ChainTabs');
    const headEl = $('#v4ChainHeader');
    const stepBarEl = $('#v4StepBar');
    const stepContentEl = $('#v4StepContent');
    if (!chains.length || !tabsEl || !headEl || !stepBarEl || !stepContentEl) return;

    if (state.activeChainIdx >= chains.length) state.activeChainIdx = 0;
    const activeChain = chains[state.activeChainIdx];
    const layers = activeChain.layers || [];
    if (state.activeLayerIdx >= layers.length) state.activeLayerIdx = 0;
    const activeLayer = layers[state.activeLayerIdx] || {};

    tabsEl.innerHTML = chains
      .map((ch, idx) => {
        const shortT = String(ch.title || ch.chainTitle || `Chuỗi ${idx + 1}`)
          .replace(/^Chuỗi truyền dẫn vĩ mô\s*[—-]\s*vi mô:\s*/i, '');
        return `
          <button type="button" class="v4-chain-tab ${idx === state.activeChainIdx ? 'active' : ''}" data-chain-idx="${idx}">
            0${idx + 1} · ${esc(shortT)}
          </button>
        `;
      })
      .join('');

    headEl.innerHTML = `
      <h3 class="v4-chain-title">${esc(activeChain.title || activeChain.chainTitle)}</h3>
      <p class="v4-chain-thesis">${esc(activeChain.coreThesis || activeChain.macroDriver || '')}</p>
    `;

    stepBarEl.innerHTML = layers
      .map((ly, idx) => {
        const stepNum = String(ly.levelNumber || idx + 1).padStart(2, '0');
        const shortLayer = String(ly.levelName || ly.layerName || ly.title || '')
          .replace(/^Tầng\s*\d+:\s*/i, '');
        return `
          <button type="button" class="v4-step-btn ${idx === state.activeLayerIdx ? 'active' : ''}" data-layer-idx="${idx}" role="tab" aria-selected="${idx === state.activeLayerIdx}">
            <span class="v4-step-num">${esc(stepNum)}</span>
            <span class="v4-step-label">${esc(shortLayer)}</span>
          </button>
        `;
      })
      .join('');

    const relEvents = (activeLayer.eventIds || [])
      .map((eid) => state.newsById[eid])
      .filter(Boolean);

    const stepNumStr = String(activeLayer.levelNumber || state.activeLayerIdx + 1).padStart(2, '0');
    const stepBadge = activeLayer.badge === 'INFERENCE' ? 'SUY LUẬN HỆ THỐNG' : 'SỰ KIỆN XÁC MINH';

    stepContentEl.innerHTML = `
      <div>
        <div class="v4-step-kicker">
          <span class="v4-step-badge">${esc(stepBadge)}</span>
          <span class="v4-step-layer-name">${esc(activeLayer.levelName || `Tầng ${stepNumStr}`)}</span>
        </div>
        <h4 class="v4-step-heading">${esc(activeLayer.title || '')}</h4>
        <p class="v4-step-desc">${esc(activeLayer.content || activeLayer.description || '')}</p>
        <div class="v4-step-pager">
          <button type="button" class="v4-step-pager-btn" id="v4PrevStepBtn" ${state.activeLayerIdx === 0 ? 'disabled' : ''}>&larr; Tầng trước</button>
          <button type="button" class="v4-step-pager-btn" id="v4NextStepBtn" ${state.activeLayerIdx >= layers.length - 1 ? 'disabled' : ''}>Tầng tiếp theo &rarr;</button>
        </div>
      </div>

      <aside class="v4-step-side">
        <div class="v4-step-side-label">Động lực vĩ mô dẫn dắt</div>
        <p class="v4-step-driver">${esc(activeChain.macroDriver || activeChain.coreThesis || '')}</p>

        <div class="v4-step-side-label">Tin tức liên đới ở tầng này (${relEvents.length})</div>
        <div class="v4-step-events">
          ${
            relEvents.length
              ? relEvents
                  .map(
                    (ev) => `
                  <button type="button" class="v4-step-event-link" data-open-event="${esc(ev.eventId)}">
                    <span class="v4-step-event-title">${esc(ev.headline || ev.title)}</span>
                    <span class="v4-step-event-src">${esc(sourceLabel(ev))} · ${esc(extractTimeHM(ev))}</span>
                  </button>
                `
                  )
                  .join('')
              : '<span class="v4-step-event-src">Tầng phân tích tổng hợp xuyên suốt mạch dữ kiện phiên.</span>'
          }
        </div>
      </aside>
    `;

    tabsEl.querySelectorAll('.v4-chain-tab').forEach((btn) => {
      btn.addEventListener('click', () => {
        state.activeChainIdx = Number(btn.dataset.chainIdx);
        state.activeLayerIdx = 0;
        renderMacroMicro();
      });
    });

    stepBarEl.querySelectorAll('.v4-step-btn').forEach((btn) => {
      btn.addEventListener('click', () => {
        state.activeLayerIdx = Number(btn.dataset.layerIdx);
        renderMacroMicro();
      });
    });

    const prevBtn = $('#v4PrevStepBtn');
    const nextBtn = $('#v4NextStepBtn');
    if (prevBtn) {
      prevBtn.addEventListener('click', () => {
        if (state.activeLayerIdx > 0) {
          state.activeLayerIdx -= 1;
          renderMacroMicro();
        }
      });
    }
    if (nextBtn) {
      nextBtn.addEventListener('click', () => {
        if (state.activeLayerIdx < layers.length - 1) {
          state.activeLayerIdx += 1;
          renderMacroMicro();
        }
      });
    }
  }

  // ─── C2. GÓC CHUYÊN MÔN FINTECH (3 CỘT + PLAYBOOK 2 CỘT + TỪ ĐIỂN PHẲNG) ────
  function renderFintechCorner() {
    const elSec = state.data.editorialSections?.sec08_expertLearning || {};
    const lessons = elSec.lessons || [];
    const frameworks = elSec.frameworks || [];
    const playbooks = elSec.salesPlaybook || [];
    const glossary = elSec.fintechGlossary || [];

    // 1. Lưới 3 cột không viền khung (6 mục: 4 lessons + 2 frameworks = 2 hàng x 3 cột đầy đặn)
    const gridEl = $('#v4FintechGrid');
    if (gridEl) {
      const mergedItems = [
        ...lessons.map((l, idx) => ({
          kind: 'lesson',
          idx,
          kicker: l.concept || 'Kiến thức Fintech',
          title: l.title || l.topic,
          desc: l.simpleExplanation || l.newsGrounding || '',
          payload: l
        })),
        ...frameworks.map((fw, idx) => ({
          kind: 'framework',
          idx,
          kicker: 'Khung kiến trúc chuyển dịch',
          title: String(fw.frameworkTitle || '').replace(/^Framework\s*\d+:\s*/i, ''),
          desc: `${fw.step1 || ''} ${fw.step2 || ''}`.trim(),
          payload: fw
        }))
      ];

      gridEl.innerHTML = mergedItems
        .map(
          (item, i) => `
          <article class="v4-fintech-card" data-fintech-idx="${i}">
            <div class="v4-fintech-card-cat">${esc(item.kicker)}</div>
            <h3 class="v4-fintech-card-title">${esc(item.title)}</h3>
            <p class="v4-fintech-card-desc">${esc(item.desc)}</p>
            <span class="v4-fintech-card-cta">Đọc chuyên đề &rarr;</span>
          </article>
        `
        )
        .join('');

      gridEl.querySelectorAll('.v4-fintech-card').forEach((card) => {
        card.addEventListener('click', () => {
          const item = mergedItems[Number(card.dataset.fintechIdx)];
          openFintechItemDrawer(item);
        });
      });
    }

    // 2. Playbook 2 cột cân đối
    const pbGrid = $('#v4PlaybookGrid');
    if (pbGrid) {
      pbGrid.innerHTML = playbooks
        .map(
          (pb, idx) => `
          <article class="v4-playbook-card" data-playbook-idx="${idx}">
            <div class="v4-fintech-card-cat">Playbook 0${idx + 1}</div>
            <h4 class="v4-playbook-title">${esc(pb.title)}</h4>
            <p class="v4-playbook-pitch">${esc(pb.pitch)}</p>
            <div class="v4-playbook-meta">Đối tượng: ${esc(pb.target)}</div>
          </article>
        `
        )
        .join('');

      pbGrid.querySelectorAll('.v4-playbook-card').forEach((card) => {
        card.addEventListener('click', () => {
          openPlaybookDrawer(playbooks[Number(card.dataset.playbookIdx)]);
        });
      });
    }

    // 3. Từ điển 2 cột phẳng (table)
    const glBody = $('#v4GlossaryBody');
    if (glBody) {
      glBody.innerHTML = glossary
        .map(
          (g) => `
          <tr>
            <td class="v4-glossary-term">${esc(g.term)}</td>
            <td>${esc(g.definition)}</td>
          </tr>
        `
        )
        .join('');
    }
  }

  // ─── TRANG 04: TÍN HIỆU & CƠ HỘI B2B ───────────────────────────────────────
  function renderB2BPage() {
    const es = state.data.editorialSections || {};
    const signals = es.sec04b_decisionBrief?.signals || [];
    const opps = es.sec07_paymentRadar?.opportunities || [];
    const watchlist = es.sec08b_watchlist?.items || es.sec08b_watchlist?.watchlistItems || [];

    const dbMount = $('#v4DecisionBriefMount');
    if (dbMount) {
      dbMount.innerHTML = signals
        .map((sig, idx) => {
          const segs = (sig.relevantMerchantSegments || []).slice(0, 4);
          const sols = (sig.potentialPaymentSolutions || []).slice(0, 2);
          return `
            <article class="v4-b2b-card">
              <div class="v4-b2b-card-top">
                <span class="v4-crimson-tag">${esc(sig.categoryBadge || 'TÍN HIỆU ĐIỀU HÀNH')}</span>
                <span class="v4-b2b-pill">${esc(sig.signalId || `DECISION-0${idx + 1}`)}</span>
              </div>
              <h3 class="v4-b2b-title">${esc(sig.signalTitle || '')}</h3>
              <div class="v4-b2b-row">
                <div class="v4-b2b-label">Diễn biến thị trường</div>
                <p class="v4-b2b-text">${esc(sig.whatHappened || '')}</p>
              </div>
              <div class="v4-b2b-row">
                <div class="v4-b2b-label">Cơ hội ứng dụng B2B</div>
                <p class="v4-b2b-text">${esc(sig.whatItMeansForMyWork || sig.proposedNextAction || '')}</p>
              </div>
              ${
                segs.length
                  ? `<div class="v4-b2b-row">
                      <div class="v4-b2b-label">Phân khúc ưu tiên</div>
                      <div class="v4-b2b-tags">${segs.map((s) => `<span class="v4-b2b-tag">${esc(s)}</span>`).join('')}</div>
                    </div>`
                  : ''
              }
              ${
                sols.length
                  ? `<div class="v4-b2b-row">
                      <div class="v4-b2b-label">Giải pháp đối ứng</div>
                      <p class="v4-b2b-text">${sols.map((s) => `<strong>${esc(s.solutionName)}</strong>: ${esc(s.capabilityNote)}`).join('<br>')}</p>
                    </div>`
                  : ''
              }
            </article>
          `;
        })
        .join('');
    }

    const radarMount = $('#v4PaymentRadarMount');
    if (radarMount) {
      radarMount.innerHTML = opps
        .map((op) => {
          const rels = (op.relevantEventIds || op.originEventIds || [])
            .map((eid) => state.newsById[eid])
            .filter(Boolean);
          return `
            <article class="v4-b2b-card">
              <div class="v4-b2b-card-top">
                <span class="v4-crimson-tag">${esc(op.merchantSegment || 'B2B PAYMENT RADAR')}</span>
                <span class="v4-b2b-pill">${esc(op.opportunityId || 'RADAR')} · ${esc(op.priority || 'P1')}</span>
              </div>
              <h3 class="v4-b2b-title">${esc(op.title || op.opportunityTitle || '')}</h3>
              <div class="v4-b2b-row">
                <div class="v4-b2b-label">Điểm nghẽn thanh toán</div>
                <p class="v4-b2b-text">${esc(op.paymentPainPoint || '')}</p>
              </div>
              <div class="v4-b2b-row">
                <div class="v4-b2b-label">Giải pháp &amp; Giá trị thương mại</div>
                <p class="v4-b2b-text">${esc(op.paymentSolution || '')} ${esc(op.commercialRationale || '')}</p>
              </div>
              <div class="v4-b2b-row">
                <div class="v4-b2b-label">Hành động đề xuất</div>
                <p class="v4-b2b-text"><strong>${esc(op.proposedBDAction || '')}</strong></p>
              </div>
              ${
                rels.length
                  ? `<div class="v4-b2b-row">
                      <div class="v4-b2b-label">Tin tức nền tảng (${rels.length})</div>
                      <div class="v4-b2b-tags">
                        ${rels
                          .map(
                            (ev) => `<button type="button" class="v4-b2b-tag" style="cursor:pointer;" data-open-event="${esc(ev.eventId)}">${esc(ev.eventId)} · ${esc((ev.headline || '').slice(0, 56))}...</button>`
                          )
                          .join('')}
                      </div>
                    </div>`
                  : ''
              }
            </article>
          `;
        })
        .join('');
    }

    const wlMount = $('#v4WatchlistMount');
    if (wlMount) {
      wlMount.innerHTML = watchlist
        .map(
          (wl, idx) => `
          <article class="v4-b2b-card">
            <div class="v4-b2b-card-top">
              <span class="v4-crimson-tag">${esc(wl.category || 'GIÁM SÁT VĨ MÔ')}</span>
              <span class="v4-b2b-pill">${esc(wl.watchlistId || `WL-0${idx + 1}`)} · ${esc(wl.impactLevel || 'HIGH')}</span>
            </div>
            <h3 class="v4-b2b-title">${esc(wl.itemTitle || '')}</h3>
            <div class="v4-b2b-row">
              <div class="v4-b2b-label">Chỉ báo theo dõi (${esc(wl.observationHorizon || '7 ngày tới')})</div>
              <p class="v4-b2b-text">${esc(wl.signalTracked || wl.description || '')}</p>
            </div>
            <div class="v4-b2b-row">
              <div class="v4-b2b-label">Ngưỡng kích hoạt &amp; Hành động</div>
              <p class="v4-b2b-text"><strong>Ngưỡng:</strong> ${esc(wl.threshold || wl.conditionChangingAssessment || '')}<br><strong>Đề xuất:</strong> ${esc(wl.possibleAction || '')}</p>
            </div>
          </article>
        `
        )
        .join('');
    }
  }

  // ─── CHUYỂN TRANG ĐIỀU HÀNH (01 -> 04) ──────────────────────────────────────
  function loadNewsletterPreview() {
    if (state.nlLoaded) return;
    const mount = $('#v4NlPreviewMount');
    if (!mount) return;
    state.nlLoaded = true;
    mount.innerHTML = `<iframe src="./newsletter-preview.html?v=${Date.now()}" class="v4-nl-iframe" title="Bản tin Bnews mới nhất"></iframe>`;
    const ifr = mount.querySelector('iframe');
    if (ifr) {
      ifr.addEventListener('load', () => {
        try {
          const h = ifr.contentDocument?.documentElement?.scrollHeight;
          if (h && h > 400) ifr.style.height = `${h + 24}px`;
        } catch (_) {
          // Keep default min-height
        }
      });
    }
  }

  function switchPage(pageKey) {
    const pages = {
      today: $('#v4PageToday'),
      newsletter: $('#v4PageNewsletter'),
      analysis: $('#v4PageAnalysis'),
      b2b: $('#v4PageB2B')
    };
    if (!pages[pageKey]) pageKey = 'today';
    state.activePage = pageKey;

    Object.entries(pages).forEach(([k, el]) => {
      if (el) el.hidden = k !== pageKey;
    });

    $$('[data-drawer-page]').forEach((btn) => {
      btn.classList.toggle('active', btn.dataset.drawerPage === pageKey);
    });
    $$('[data-switch-page]').forEach((btn) => {
      btn.classList.toggle('active', btn.dataset.switchPage === pageKey);
    });

    if (pageKey === 'newsletter') {
      loadNewsletterPreview();
    }
    applyFilters();
    window.scrollTo({ top: 0, behavior: 'instant' });
  }

  // ─── CHẾ ĐỘ LỌC CHUYÊN MỤC & TÌM KIẾM ────────────────────────────────────
  function applyFilters() {
    const isToday = state.activePage === 'today';
    const tabs = $$('#v4CatTabs .v4-cat-btn');
    tabs.forEach((btn) => {
      const active = isToday && btn.dataset.cat === state.activeCategory;
      btn.classList.toggle('active', active);
      btn.setAttribute('aria-selected', String(active));
    });

    $$('[data-drawer-cat]').forEach((btn) => {
      btn.classList.toggle('active', isToday && btn.dataset.drawerCat === state.activeCategory);
    });

    const frontView = $('#v4FrontPageView');
    const filteredView = $('#v4FilteredView');
    const clearBtn = $('#v4SearchClear');
    const needle = state.searchTerm.trim().toLowerCase();

    if (clearBtn) clearBtn.hidden = !needle;

    if (!isToday) return;

    if (state.activeCategory === 'ALL' && !needle) {
      if (frontView) frontView.hidden = false;
      if (filteredView) filteredView.hidden = true;
      return;
    }

    if (frontView) frontView.hidden = true;
    if (filteredView) filteredView.hidden = false;

    const allNews = state.data.eligibleNewsList || [];
    const matches = allNews
      .filter((item) => {
        const matchCat = state.activeCategory === 'ALL' || item.category === state.activeCategory;
        const matchQ =
          !needle ||
          String(item.headline || '').toLowerCase().includes(needle) ||
          String(item.summary || '').toLowerCase().includes(needle) ||
          String(item.publisher || '').toLowerCase().includes(needle) ||
          String(item.category || '').toLowerCase().includes(needle);
        return matchCat && matchQ;
      })
      .sort((a, b) => (b.originalSourcePublishedAt || '').localeCompare(a.originalSourcePublishedAt || ''));

    const headingText =
      state.activeCategory === 'ALL'
        ? `Kết quả tìm kiếm: "${state.searchTerm.trim()}"`
        : `${catLabel(state.activeCategory)}${needle ? ` · lọc "${state.searchTerm.trim()}"` : ''}`;

    filteredView.innerHTML = `
      <div class="v4-filtered-head">
        <div>
          <h2 class="v4-sec-title">${esc(headingText)}</h2>
          <p class="v4-sec-subtitle" style="margin-top:6px; padding-left:12px;">Tìm thấy ${matches.length} bản tin phù hợp trong ấn bản</p>
        </div>
        <button type="button" class="v4-back-front-btn" id="v4BackFrontBtn">&larr; Quay lại Trang nhất</button>
      </div>

      ${
        matches.length
          ? `<div class="v4-filtered-grid">
              ${matches
                .map(
                  (it) => `
                <article class="v4-filtered-card" data-open-event="${esc(it.eventId)}">
                  <div class="v4-thumb-wrap">${imgTag(it.imageUrl, it.headline, 'v4-thumb-img')}</div>
                  <div>
                    <div class="v4-crimson-tag" style="margin-bottom:4px;">${esc(catLabel(it.category))}</div>
                    <h3 class="v4-cat-lead-title">${esc(it.headline || it.title)}</h3>
                    <p class="v4-cat-lead-sapo">${esc(it.summary || '')}</p>
                    <div class="v4-article-meta">
                      <span>${esc(sourceLabel(it))}</span>
                      <span aria-hidden="true">·</span>
                      <span class="v4-mono-time">${esc(extractDateTimeReadable(it))}</span>
                    </div>
                  </div>
                </article>
              `
                )
                .join('')}
            </div>`
          : `<p class="v4-sec-subtitle">Không có bản tin nào khớp bộ lọc hiện tại.</p>`
      }
    `;

    const backBtn = $('#v4BackFrontBtn');
    if (backBtn) {
      backBtn.addEventListener('click', () => {
        state.activeCategory = 'ALL';
        state.searchTerm = '';
        const input = $('#v4SearchInput');
        if (input) input.value = '';
        applyFilters();
        window.scrollTo({ top: 0, behavior: 'smooth' });
      });
    }
  }

  // ─── DRAWER READER ────────────────────────────────────────────────────────
  function openDrawer(kicker, bodyHtml) {
    $('#v4DrawerKicker').textContent = kicker;
    $('#v4DrawerBody').innerHTML = bodyHtml;
    $('#v4DrawerBackdrop').hidden = false;
    $('#v4Drawer').hidden = false;
    document.body.style.overflow = 'hidden';
  }

  function closeDrawer() {
    $('#v4DrawerBackdrop').hidden = true;
    $('#v4Drawer').hidden = true;
    document.body.style.overflow = '';
  }

  function openArticleDrawer(eventId) {
    const item = state.newsById[eventId];
    if (!item) return;

    const blocks = [
      { label: '01 · Bối cảnh & Động thái chính', text: item.briefingContext || item.sectionB_context },
      { label: '02 · Dữ kiện & Con số trọng tâm', text: item.briefingFacts || item.sectionA_whatHappened },
      { label: '03 · Tác động thị trường', text: item.briefingPerspective || item.sectionC_whyItMatters },
      { label: '04 · Hệ lụy & Góc nhìn doanh nghiệp', text: item.briefingImplication || item.sectionD_macroMicro },
      { label: '05 · Liên hệ hạ tầng Fintech & Thanh toán', text: item.fintechRelevance || item.sectionE_fintechLens },
      { label: '06 · Khuyến nghị hành động', text: item.sectionG_practicalTakeaway }
    ].filter((b) => b.text && String(b.text).trim().length > 0);

    const html = `
      <span class="v4-crimson-tag">${esc(catLabel(item.category))}</span>
      <h2 class="v4-drawer-title" id="v4DrawerTitle">${esc(item.headline || item.title)}</h2>
      <div class="v4-drawer-meta">
        <span>Nguồn: <strong>${esc(sourceLabel(item))}</strong></span>
        <span aria-hidden="true"> · </span>
        <span class="v4-mono-time">${esc(extractDateTimeReadable(item))}</span>
      </div>
      ${item.imageUrl ? imgTag(item.imageUrl, item.headline, 'v4-drawer-img') : ''}
      ${item.supportingQuote ? `<blockquote class="v4-drawer-quote">“${esc(item.supportingQuote)}”</blockquote>` : ''}
      ${blocks
        .map(
          (b) => `
        <div class="v4-drawer-block">
          <div class="v4-drawer-block-label">${esc(b.label)}</div>
          <p class="v4-drawer-block-text">${esc(b.text)}</p>
        </div>
      `
        )
        .join('')}
      <div class="v4-drawer-actions">
        ${
          item.sourceUrl
            ? `<a href="${esc(item.sourceUrl)}" target="_blank" rel="noopener noreferrer" class="v4-btn-navy">Đọc bài gốc (${esc(sourceLabel(item))}) &nearr;</a>`
            : ''
        }
      </div>
    `;
    openDrawer(`${item.eventId} · Tóm tắt phân tích`, html);
  }

  function openMarketPulseDrawer(m) {
    if (!m) return;
    const html = `
      <span class="v4-crimson-tag">CHỈ SỐ THỊ TRƯỜNG · MARKET PULSE</span>
      <h2 class="v4-drawer-title" id="v4DrawerTitle">${esc(m.label || m.shortLabel)}</h2>
      <div class="v4-drawer-meta">
        <span>Giá trị hiện tại: <strong class="v4-mono-time">${esc(m.value)}</strong></span>
        <span aria-hidden="true"> · </span>
        <span>Biến động: <strong>${esc(m.compactDelta || m.change || '--')}</strong></span>
      </div>
      <div class="v4-drawer-block">
        <div class="v4-drawer-block-label">Thông số đối soát gốc</div>
        <p class="v4-drawer-block-text">${esc(m.referenceValue || m.statusReason || '')}</p>
      </div>
      <div class="v4-drawer-block">
        <div class="v4-drawer-block-label">Diễn giải tài chính &amp; Ứng dụng thực tế</div>
        <p class="v4-drawer-block-text">${esc(m.financialInterpretation || m.statusReason || '')}</p>
      </div>
      <div class="v4-drawer-block">
        <div class="v4-drawer-block-label">Điểm cần theo dõi tiếp theo</div>
        <p class="v4-drawer-block-text">${esc(m.monitoringWatchpoint || '')}</p>
      </div>
      <div class="v4-drawer-actions">
        ${
          m.dailyArticleUrl || m.sourceUrl
            ? `<a href="${esc(m.dailyArticleUrl || m.sourceUrl)}" target="_blank" rel="noopener noreferrer" class="v4-btn-navy">Mở nguồn báo đối soát (${esc(m.sourceShortName || 'Nguồn gốc')}) &nearr;</a>`
            : ''
        }
      </div>
    `;
    openDrawer('Market Pulse · Đối soát chi tiết', html);
  }

  function openFintechItemDrawer(item) {
    if (!item) return;
    if (item.kind === 'framework') {
      const fw = item.payload;
      const html = `
        <span class="v4-crimson-tag">${esc(item.kicker)}</span>
        <h2 class="v4-drawer-title" id="v4DrawerTitle">${esc(fw.frameworkTitle)}</h2>
        <div class="v4-drawer-block">
          <div class="v4-drawer-block-label">Bước 01 · Tác động vĩ mô</div>
          <p class="v4-drawer-block-text">${esc(fw.step1 || '')}</p>
        </div>
        <div class="v4-drawer-block">
          <div class="v4-drawer-block-label">Bước 02 · Năng lực ngân hàng số</div>
          <p class="v4-drawer-block-text">${esc(fw.step2 || '')}</p>
        </div>
        <div class="v4-drawer-block">
          <div class="v4-drawer-block-label">Bước 03 · Điểm chạm thanh toán bán lẻ</div>
          <p class="v4-drawer-block-text">${esc(fw.step3 || '')}</p>
        </div>
      `;
      openDrawer('Góc chuyên môn Fintech', html);
      return;
    }

    const l = item.payload;
    const html = `
      <span class="v4-crimson-tag">${esc(l.concept || 'Chuyên đề Fintech')}</span>
      <h2 class="v4-drawer-title" id="v4DrawerTitle">${esc(l.title || l.topic)}</h2>
      <div class="v4-drawer-meta">${esc(l.newsGrounding || '')}</div>
      <div class="v4-drawer-block">
        <div class="v4-drawer-block-label">Giải thích cơ chế</div>
        <p class="v4-drawer-block-text">${esc(l.simpleExplanation || '')}</p>
      </div>
      <div class="v4-drawer-block">
        <div class="v4-drawer-block-label">Ví dụ thực tiễn</div>
        <p class="v4-drawer-block-text">${esc(l.realWorldExample || '')}</p>
      </div>
      <div class="v4-drawer-block">
        <div class="v4-drawer-block-label">Tác động đối với doanh nghiệp</div>
        <p class="v4-drawer-block-text">${esc(l.impactOnBusiness || l.takeaway || '')}</p>
      </div>
    `;
    openDrawer('Góc chuyên môn Fintech', html);
  }

  function openPlaybookDrawer(pb) {
    if (!pb) return;
    const html = `
      <span class="v4-crimson-tag">PLAYBOOK TRIỂN KHAI B2B</span>
      <h2 class="v4-drawer-title" id="v4DrawerTitle">${esc(pb.title)}</h2>
      <div class="v4-drawer-block">
        <div class="v4-drawer-block-label">Nhóm khách hàng mục tiêu</div>
        <p class="v4-drawer-block-text">${esc(pb.target || '')}</p>
      </div>
      <div class="v4-drawer-block">
        <div class="v4-drawer-block-label">Đề xuất giá trị cốt lõi (Pitch)</div>
        <p class="v4-drawer-block-text">${esc(pb.pitch || '')}</p>
      </div>
      <div class="v4-drawer-block">
        <div class="v4-drawer-block-label">Xử lý rào cản &amp; Từ chối</div>
        <p class="v4-drawer-block-text">${esc(pb.objectionHandling || '')}</p>
      </div>
    `;
    openDrawer('Playbook B2B · Triển khai thực tế', html);
  }

  // ─── LEFT DRAWER, THEME & VCARD MODAL ─────────────────────────────────────
  function openNavDrawer() {
    $('#v4NavBackdrop').hidden = false;
    $('#v4NavDrawer').hidden = false;
    $('#v4MenuBtn')?.setAttribute('aria-expanded', 'true');
    document.body.style.overflow = 'hidden';
  }

  function closeNavDrawer() {
    $('#v4NavBackdrop').hidden = true;
    $('#v4NavDrawer').hidden = true;
    $('#v4MenuBtn')?.setAttribute('aria-expanded', 'false');
    document.body.style.overflow = '';
  }

  function openVCardModal() {
    $('#v4VCardBackdrop').hidden = false;
    $('#v4VCardModal').hidden = false;
    document.body.style.overflow = 'hidden';
  }

  function closeVCardModal() {
    $('#v4VCardBackdrop').hidden = true;
    $('#v4VCardModal').hidden = true;
    document.body.style.overflow = '';
  }

  function applyTheme(theme) {
    const isDark = theme === 'dark';
    document.documentElement.setAttribute('data-theme', isDark ? 'dark' : 'light');
    const logoPath = isDark ? '../bnews-logo-dark-opt.webp' : '../bnews-logo-light-opt.webp';
    $$('.v4-brand-logo, .v4-nav-drawer-logo, .v4-footer-logo').forEach((img) => {
      img.src = logoPath;
    });
    const tBtn = $('#v4ThemeToggleBtn');
    if (tBtn) {
      tBtn.textContent = isDark ? 'Chuyển sang Giao diện Sáng' : 'Đổi giao diện Sáng / Tối';
    }
  }

  // ─── EVENTS & INITIALIZATION ──────────────────────────────────────────────
  function bindGlobalEvents() {
    document.addEventListener('click', (e) => {
      const eventTrigger = e.target.closest('[data-open-event]');
      if (eventTrigger) {
        e.preventDefault();
        openArticleDrawer(eventTrigger.dataset.openEvent);
        return;
      }

      const pageBtn = e.target.closest('[data-switch-page], [data-drawer-page]');
      if (pageBtn) {
        const targetPage = pageBtn.dataset.switchPage || pageBtn.dataset.drawerPage;
        closeNavDrawer();
        switchPage(targetPage);
        return;
      }

      const drawerCatBtn = e.target.closest('[data-drawer-cat]');
      if (drawerCatBtn) {
        state.activeCategory = drawerCatBtn.dataset.drawerCat;
        closeNavDrawer();
        switchPage('today');
        return;
      }

      const catFilterTrigger = e.target.closest('[data-filter-cat]');
      if (catFilterTrigger) {
        state.activeCategory = catFilterTrigger.dataset.filterCat;
        switchPage('today');
      }
    });

    $$('#v4CatTabs .v4-cat-btn').forEach((btn) => {
      btn.addEventListener('click', () => {
        state.activeCategory = btn.dataset.cat;
        switchPage('today');
      });
    });

    const resetBrand = $('#v4BrandReset');
    if (resetBrand) {
      resetBrand.addEventListener('click', (e) => {
        e.preventDefault();
        state.activeCategory = 'ALL';
        state.searchTerm = '';
        const input = $('#v4SearchInput');
        if (input) input.value = '';
        switchPage('today');
      });
    }

    const searchInput = $('#v4SearchInput');
    const searchClear = $('#v4SearchClear');
    if (searchInput) {
      searchInput.addEventListener('input', () => {
        state.searchTerm = searchInput.value;
        if (state.activePage !== 'today') {
          switchPage('today');
        } else {
          applyFilters();
        }
      });
    }
    if (searchClear) {
      searchClear.addEventListener('click', () => {
        searchInput.value = '';
        state.searchTerm = '';
        applyFilters();
        searchInput.focus();
      });
    }

    // Left Navigation Drawer controls
    $('#v4MenuBtn')?.addEventListener('click', openNavDrawer);
    $('#v4NavClose')?.addEventListener('click', closeNavDrawer);
    $('#v4NavBackdrop')?.addEventListener('click', closeNavDrawer);

    $('#v4DrawerSearchForm')?.addEventListener('submit', (e) => {
      e.preventDefault();
      const val = ($('#v4DrawerSearchInput')?.value || '').trim();
      state.searchTerm = val;
      if (searchInput) searchInput.value = val;
      closeNavDrawer();
      switchPage('today');
    });

    // Utility buttons inside Drawer
    $('#v4OpenVCardBtn')?.addEventListener('click', () => {
      closeNavDrawer();
      openVCardModal();
    });
    $('#v4ThemeToggleBtn')?.addEventListener('click', () => {
      const cur = document.documentElement.getAttribute('data-theme');
      const next = cur === 'dark' ? 'light' : 'dark';
      localStorage.setItem('site_theme', next);
      applyTheme(next);
    });

    // Right Detail Drawer
    $('#v4DrawerClose')?.addEventListener('click', closeDrawer);
    $('#v4DrawerBackdrop')?.addEventListener('click', closeDrawer);

    // Header "Đăng ký Bản tin" CTA -> Chuyển sang Trang 02 (Bản tin & Đăng ký)
    $('#v4SubscribeBtn')?.addEventListener('click', () => {
      switchPage('newsletter');
    });

    // Newsletter subscribe form on Trang 02
    $('#v4NlForm')?.addEventListener('submit', (e) => {
      e.preventDefault();
      const email = ($('#v4NlEmailInput')?.value || '').trim();
      const fb = $('#v4NlFeedback');
      if (fb && email) {
        fb.hidden = false;
        fb.textContent = `Đã ghi nhận yêu cầu đăng ký bản tin sáng cho địa chỉ: ${email}.`;
        $('#v4NlEmailInput').value = '';
      }
    });

    // vCard Modal controls
    $('#v4VCardClose')?.addEventListener('click', closeVCardModal);
    $('#v4VCardBackdrop')?.addEventListener('click', closeVCardModal);

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        closeDrawer();
        closeNavDrawer();
        closeVCardModal();
      }
    });
  }

  async function init() {
    const savedTheme = localStorage.getItem('site_theme') === 'dark' ? 'dark' : 'light';
    applyTheme(savedTheme);

    const data = await loadEditionData();
    if (!data) {
      const mount = $('#v4FrontPageView');
      if (mount) {
        mount.innerHTML = '<div class="v4-container" style="padding:48px 24px;"><p>Không thể tải dữ liệu ấn bản.</p></div>';
      }
      return;
    }

    state.data = data;
    (data.eligibleNewsList || []).forEach((item) => {
      if (item.eventId) state.newsById[item.eventId] = item;
    });

    renderMasthead();
    renderPulseStrip();
    renderFrontPage();
    renderCategoryClusters();
    renderMacroMicro();
    renderFintechCorner();
    renderB2BPage();
    bindGlobalEvents();
    switchPage('today');
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
