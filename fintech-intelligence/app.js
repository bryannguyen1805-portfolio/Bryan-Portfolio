/* Bryan FinTech Intelligence — public read-only frontend, no API secrets. */
'use strict';
let LIVE_DATA = {};
let currentNewsList = [];
let currentCategoryFilter = 'ALL';
let currentSearch = '';

function element(tag, className, text) {
  const item = document.createElement(tag);
  if (className) item.className = className;
  if (text !== undefined && text !== null) item.textContent = String(text);
  return item;
}
function clear(node) { node.replaceChildren(); return node; }
function safeArray(x) { return Array.isArray(x) ? x : []; }
function validHttpUrl(raw) {
  try {
    const u = new URL(String(raw || ''));
    return ['https:', 'http:'].includes(u.protocol) ? u.href : null;
  } catch (_) { return null; }
}
function addLine(parent, label, value, cls='branding-row') {
  const row = element('div', cls);
  const strong = element('strong', null, label + ' ');
  row.append(strong, document.createTextNode(String(value || 'Chưa có dữ liệu')));
  parent.append(row);
  return row;
}
function empty(parent, message) { parent.append(element('div', 'empty-state', message)); }
function reportStatus(kind, message, updated='') {
  const dot = document.getElementById('dataStatusDot');
  dot.className = 'status-dot ' + (kind === 'ready' ? 'ready' : kind === 'error' ? 'error' : '');
  document.getElementById('dataStatusText').textContent = message;
  document.getElementById('dataUpdatedAt').textContent = updated;
}
function formatTime(iso) {
  if (!iso) return '';
  const d = new Date(iso);
  return Number.isNaN(d.getTime()) ? '' : 'Xuất bản: ' + d.toLocaleString('vi-VN', {timeZone:'Asia/Ho_Chi_Minh'});
}
function localDate(str) {
  const m = String(str || '').match(/^(\d{2})\/(\d{2})\/(\d{4})$/);
  return m ? `${m[3]}-${m[2]}-${m[1]}` : null;
}
async function refreshFeed() {
  reportStatus('loading','Đang tải bản tin từ GitHub Pages...');
  try {
    const response = await fetch('./data/latest.json?v=' + Date.now(), {cache:'no-store'});
    if (!response.ok) throw new Error('HTTP ' + response.status);
    const latest = await response.json();
    if (!latest || latest.status === 'setup_required') throw new Error('Chưa xuất bản snapshot từ Apps Script');
    if (!Array.isArray(latest.newsList)) throw new Error('Dữ liệu không đúng định dạng');
    LIVE_DATA = latest;
    renderAllData(latest);
    populateArchiveDropdown(safeArray(latest.archives));
    document.getElementById('archiveBanner').style.display = 'none';
    const old = latest.status === 'stale';
    reportStatus(old ? 'warning' : 'ready',
      old ? 'Dữ liệu đang cũ — cần kiểm tra nguồn trước khi sử dụng' : 'Đã đồng bộ dữ liệu từ Google Apps Script',
      formatTime(latest.publishedAt));
  } catch (err) {
    reportStatus('error','Chưa có dữ liệu trực tuyến: ' + err.message);
    renderAllData({date:'—', newsList:[]});
  }
}
function initTheme() {
  let saved = null;
  try { saved = localStorage.getItem('fintech_portal_theme'); } catch (_) {}
  const isDay = new Date().getHours() >= 6 && new Date().getHours() < 18;
  applyTheme(saved || (isDay ? 'light' : 'dark'));
}
function applyTheme(theme) {
  document.body.classList.toggle('light-theme', theme === 'light');
  document.body.classList.toggle('dark-theme', theme !== 'light');
  document.getElementById('themeToggleBtn').textContent = theme === 'light' ? '☀️ Giao diện: Sáng' : '🌙 Giao diện: Tối';
}
function toggleTheme() {
  const next = document.body.classList.contains('light-theme') ? 'dark' : 'light';
  try { localStorage.setItem('fintech_portal_theme', next); } catch (_) {}
  applyTheme(next);
}
function switchSiteTab(tabId) {
  const panels = ['overview','news','macro','branding','subscribe'];
  const all = tabId === 'tab-all';
  panels.forEach(name => {
    const p = document.getElementById('panel-'+name);
    p.classList.toggle('active-panel', all || tabId === 'tab-'+name);
    p.style.display = (all || tabId === 'tab-'+name) ? 'block' : 'none';
  });
  document.querySelectorAll('.nav-tab-btn').forEach(b => {
    b.classList.toggle('active', (b.getAttribute('onclick') || '').includes("'"+tabId+"'"));
  });
  const hash = all ? 'all' : tabId.slice(4);
  if (history.replaceState) history.replaceState(null,'','#'+hash);
  window.scrollTo({top:0,behavior:'smooth'});
}
function renderAllData(data) {
  document.getElementById('headerDate').textContent = 'Ngày: ' + (data.date || '—') + ' | Khung: ' + (data.researchWindow || '—');
  document.getElementById('navDateBadge').textContent = 'Ngày ' + (data.date || '—');
  document.getElementById('quoteContent').textContent = '“' + (data.highlightQuote || data.thesis || 'Chưa có luận điểm trong kỳ') + '”';
  document.getElementById('quoteSummary').textContent = data.bigPictureSummary || 'Thông tin sẽ được cập nhật sau khi hệ thống đồng bộ.';

  const pulse = clear(document.getElementById('pulseGrid'));
  safeArray(data.metrics).forEach(m => {
    const box = element('article','pulse-card');
    box.append(element('div','pulse-label',m.label), element('div','pulse-value '+(['positive','alert','warning'].includes(m.status) ? m.status : ''),m.value), element('div','pulse-note',m.note));
    pulse.append(box);
  });
  if (!pulse.childElementCount) empty(pulse,'Chưa có chỉ số Market Pulse cập nhật.');

  const mix = clear(document.getElementById('paymentMixContainer'));
  safeArray(data.paymentMix).forEach(pm => {
    const box = element('div','progress-item');
    const header = element('div','progress-header');
    const color = /^#[0-9a-f]{6}$/i.test(String(pm.color || '')) ? pm.color : '#38bdf8';
    const value = element('span','',pm.value); value.style.color = color;
    header.append(element('span','',pm.label), value);
    const track = element('div','progress-track');
    const bar = element('div','progress-bar');
    bar.style.width = Math.min(100,Math.max(0,Number(pm.percent)||0))+'%';
    bar.style.backgroundColor = color;
    track.append(bar); box.append(header,track); mix.append(box);
  });
  if (!mix.childElementCount) empty(mix,'Chưa có dữ liệu cơ cấu thanh toán.');

  const radar = clear(document.getElementById('radarGrid'));
  safeArray(data.radarList).slice(0,4).forEach((r,i) => {
    const box = element('article','radar-card');
    box.append(element('div','radar-top-badge','Top '+(i+1)+' · '+(r.status||'Market Radar')),
      element('div','radar-name',r.segment));
    addLine(box,'Bối cảnh:',r.context,'radar-detail');
    addLine(box,'Giải pháp:',r.solution,'radar-detail');
    if (r.action) addLine(box,'Hướng hành động:',r.action,'radar-action');
    radar.append(box);
  });
  if (!radar.childElementCount) empty(radar,'Chưa có ngành trọng tâm mới.');

  currentNewsList = safeArray(data.newsList);
  document.getElementById('countAll').textContent = currentNewsList.length;
  document.getElementById('menuNewsCount').textContent = currentNewsList.length;
  drawFilteredNews();

  const map = clear(document.getElementById('macroMapBody'));
  safeArray(data.macroMap).forEach(m => {
    const tr = document.createElement('tr');
    ['macro','banking','corporate','consumer','payment'].forEach(key => tr.append(element('td','',m[key] || '—')));
    map.append(tr);
  });
  if (!map.childElementCount) { const tr = document.createElement('tr'); const td = element('td','', 'Chưa có dữ liệu truyền dẫn vĩ mô đến vi mô.'); td.colSpan = 5; tr.append(td); map.append(tr); }

  const dots = clear(document.getElementById('connectTheDotsContainer'));
  safeArray(data.connectTheDots).forEach(c => {
    const box = element('article','connect-card');
    box.append(element('div','connect-title',c.title),element('div','connect-desc',c.desc));
    dots.append(box);
  });
  if (!dots.childElementCount) empty(dots,'Mục Connect the Dots sẽ có nội dung sau khi phân tích được cập nhật.');

  const branding = clear(document.getElementById('brandingContainer'));
  safeArray(data.brandingData).slice(0,1).forEach(b => {
    const box = element('article','branding-box');
    box.append(element('div','branding-title',b.title));
    addLine(box,'Đối tượng:',b.audience); addLine(box,'Hook:',b.hook);
    addLine(box,'Góc nhìn:',b.perspective); addLine(box,'Takeaway:',b.takeaway);
    addLine(box,'CTA:',b.cta); branding.append(box);
  });
  if (!branding.childElementCount) empty(branding,'Chưa có đề xuất bài viết LinkedIn mới.');
  const learning = clear(document.getElementById('learningCornerContainer'));
  if (data.learningCorner && data.learningCorner.concept) {
    const box = element('article','learning-box');
    box.append(element('div','learning-title','GÓC HỌC TẬP: '+data.learningCorner.concept));
    addLine(box,'Định nghĩa:',data.learningCorner.definition,'learning-desc');
    addLine(box,'Ví dụ dễ hiểu:',data.learningCorner.analogy,'learning-desc');
    addLine(box,'Liên hệ FinTech:',data.learningCorner.whyFintech,'learning-desc');
    learning.append(box);
  }
}
function matchesCategory(category, cat) {
  if (cat === 'ALL') return true;
  const str = String(category||'').toLowerCase();
  const aliases = {
    Macroeconomics:['macro','vĩ mô','kinh tế'], Banking:['bank','ngân hàng','ngoại hối','lãi suất','tiền tệ','tín dụng'],
    Payment:['payment','thanh toán','vietqr','napas','hạ tầng'], Consumer:['consumer','tiêu dùng','bnpl','trả góp'],
    Stock:['stock','chứng khoán','thị trường vốn'], Digital:['digital','số','fintech']
  };
  return (aliases[cat] || []).some(t => str.includes(t));
}
function filterNews(cat) {
  currentCategoryFilter = cat;
  document.querySelectorAll('.filter-btn').forEach(b => b.classList.toggle('active',b.dataset.cat === cat));
  drawFilteredNews();
}
function searchNews(text) { currentSearch = String(text||'').trim().toLowerCase(); drawFilteredNews(); }
function drawFilteredNews() {
  const subset = currentNewsList.filter(n => matchesCategory(n.category,currentCategoryFilter) &&
    (!currentSearch || [n.title,n.source,n.summary,n.category,n.fintechImpact].some(v=>String(v||'').toLowerCase().includes(currentSearch))));
  document.getElementById('filteredNewsCount').textContent = subset.length + ' / ' + currentNewsList.length + ' tin';
  const container = clear(document.getElementById('newsListContainer'));
  subset.forEach(n => {
    const box = element('article','news-card '+(n.tier === 'Tier 1' ? 'tier-1' : n.tier === 'Tier 2' ? 'tier-2' : 'tier-3'));
    const meta = element('div','news-meta');
    meta.append(element('span','news-category',(n.tier||'Tin tức')+' · '+(n.category||'Thị trường')));
    const source = element('span','news-source');
    const u = validHttpUrl(n.url);
    if (u) { const a = element('a','',n.source || 'Nguồn bài báo'); a.href=u; a.target='_blank'; a.rel='noopener noreferrer'; source.append(a); }
    else source.textContent = (n.source || 'Chưa xác định') + ' · Chưa có liên kết hợp lệ';
    meta.append(source); box.append(meta);
    const title = element('h3','news-title');
    if (u) { const a=element('a','',n.title||'Không có tiêu đề'); a.href=u;a.target='_blank';a.rel='noopener noreferrer';title.append(a); }
    else title.textContent=n.title||'Không có tiêu đề';
    box.append(title,element('p','news-summary',n.summary||'Chưa có tóm tắt.'));
    if (n.explanation) addLine(box,'Bản chất sự kiện:',n.explanation,'news-breakdown');
    if (n.fintechImpact) addLine(box,'Tác động FinTech:',n.fintechImpact,'news-fintech');
    const details=element('details','news-extra');
    details.append(element('summary','', 'Phân tích, dự báo & takeaway'));
    addLine(details,'Vì sao quan trọng:',n.importance,'branding-row');
    addLine(details,'Vĩ mô → vi mô:',n.macroToMicro,'branding-row');
    addLine(details,'Dự báo (nhận định, không phải dữ kiện):',n.prediction,'branding-row');
    addLine(details,'Takeaway:',n.takeaway,'branding-row');
    box.append(details); container.append(box);
  });
  if (!subset.length) empty(container,'Không có tin phù hợp với bộ lọc hoặc dữ liệu chưa được đồng bộ.');
}
function populateArchiveDropdown(archives) {
  const sel = clear(document.getElementById('archiveSelect'));
  const opt = document.createElement('option'); opt.value='';opt.textContent='-- Chọn ngày lưu trữ --';sel.append(opt);
  const seen=new Set();
  safeArray(archives).forEach(a => {
    const date=localDate(a.date);
    if (!date || seen.has(date)) return;
    seen.add(date);
    const item=element('option','',a.date+' — '+String(a.title||'Bản tin lưu trữ').slice(0,55));
    item.value=a.date; sel.append(item);
  });
}
async function onSelectArchive(dateVal) {
  const formatted=localDate(dateVal);
  if (!formatted) return;
  try {
    reportStatus('loading','Đang tải bản tin lưu trữ ngày '+dateVal+'...');
    const response=await fetch('./data/archives/'+formatted+'.json', {cache:'no-store'});
    if (!response.ok) throw new Error('Chưa có bản snapshot lịch sử trên GitHub');
    const archive=await response.json();
    if (!Array.isArray(archive.newsList)) throw new Error('Bản tin lịch sử chưa đầy đủ');
    renderAllData(archive);
    document.getElementById('archiveDateNotice').textContent=archive.date||dateVal;
    document.getElementById('archiveBanner').style.display='flex';
    switchSiteTab('tab-overview');
    reportStatus('ready','Đang xem bản tin lưu trữ',formatTime(archive.publishedAt));
  } catch(err) {
    reportStatus('error','Không mở được bản tin '+dateVal+': '+err.message);
  }
}
function restoreLiveView() {
  renderAllData(LIVE_DATA);
  document.getElementById('archiveBanner').style.display='none';
  document.getElementById('archiveSelect').value='';
  reportStatus(LIVE_DATA.status === 'stale' ? 'warning':'ready','Đang xem bản tin mới nhất',formatTime(LIVE_DATA.publishedAt));
  switchSiteTab('tab-overview');
}
function initSubscription() {
  const host=clear(document.getElementById('subscriptionHost'));
  const endpoint=validHttpUrl(window.FINTECH_CONFIG && window.FINTECH_CONFIG.appsScriptWebAppUrl);
  if (!endpoint || !endpoint.startsWith('https://script.google.com/macros/')) {
    empty(host,'Đăng ký email chưa được kết nối. Chủ website cần cấu hình Apps Script Web App URL trong config.js.');
    return;
  }
  const u=new URL(endpoint); u.searchParams.set('action','subscribe-form');
  const frame=element('iframe');
  frame.src=u.toString(); frame.title='Biểu mẫu đăng ký bản tin FinTech'; frame.loading='lazy';
  frame.referrerPolicy='no-referrer';
  host.append(frame);
  const note=element('p','inline-hint','Nếu biểu mẫu không hiển thị do trình duyệt chặn nội dung nhúng, mở biểu mẫu bảo mật tại: ');
  const link=element('a','','Trang đăng ký'); link.href=u.toString();link.target='_blank';link.rel='noopener noreferrer';note.append(link);host.append(note);
}
function initPortal() {
  initTheme(); initSubscription();
  const h=location.hash;
  const tabs=['overview','news','macro','branding','subscribe','all'];
  const selected=tabs.includes(h.replace('#','')) ? 'tab-'+h.slice(1) : 'tab-overview';
  switchSiteTab(selected);
  refreshFeed();
}
window.addEventListener('DOMContentLoaded',initPortal);
