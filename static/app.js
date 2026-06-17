// === LLM Tracker — single-page app ===

// ---------- Icon helpers (inline SVG, Lucide-style) ----------
const ICON = {
  eye:       '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>',
  wrench:    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/></svg>',
  brain:     '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96.44 2.5 2.5 0 0 1-2.96-3.08 3 3 0 0 1-.34-5.58 2.5 2.5 0 0 1 1.32-4.24 2.5 2.5 0 0 1 1.98-3A2.5 2.5 0 0 1 9.5 2z"/><path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96.44 2.5 2.5 0 0 0 2.96-3.08 3 3 0 0 0 .34-5.58 2.5 2.5 0 0 0-1.32-4.24 2.5 2.5 0 0 0-1.98-3A2.5 2.5 0 0 0 14.5 2z"/></svg>',
  calendar:  '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>',
  infinity:  '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18.178 8c5.096 0 5.096 8 0 8-5.095 0-7.133-8-12.739-8-4.585 0-4.585 8 0 8 5.606 0 7.644-8 12.739-8z"/></svg>',
};

// ---------- State ----------
const state = {
  data: null,
  activeCategory: null,
  filters: { free: false, open: false, vision: false, tools: false, reason: false },
  search: '',
  sort: 'provider',
};

// ---------- Provider metadata ----------
const PROVIDER_META = {
  'anthropic':     { name: 'Anthropic',     color: '#cc785c' },
  'openai':        { name: 'OpenAI',        color: '#10a37f' },
  'google':        { name: 'Google',        color: '#4285f4' },
  'x-ai':          { name: 'xAI (Grok)',    color: '#1da1f2' },
  'deepseek':      { name: 'DeepSeek',      color: '#5b6cff' },
  'moonshotai':    { name: 'Moonshot (Kimi)', color: '#7c3aed' },
  'minimax':       { name: 'MiniMax',       color: '#ff6b35' },
  'mistralai':     { name: 'Mistral',       color: '#ff7000' },
  'meta-llama':    { name: 'Meta (Llama)',  color: '#0866ff' },
  'qwen':          { name: 'Qwen (Alibaba)', color: '#ff6a00' },
  'nvidia':        { name: 'NVIDIA',        color: '#76b900' },
  'cohere':        { name: 'Cohere',        color: '#39594d' },
  'perplexity':    { name: 'Perplexity',    color: '#22b6b5' },
  'amazon':        { name: 'Amazon (Nova)', color: '#ff9900' },
  'microsoft':     { name: 'Microsoft',     color: '#5e5e5e' },
  'ibm-granite':   { name: 'IBM Granite',   color: '#0530ad' },
  'z-ai':          { name: 'Z.AI (GLM)',    color: '#7c5cff' },
  'xiaomi':        { name: 'Xiaomi (MiMo)', color: '#ff6900' },
  'bytedance':     { name: 'ByteDance',     color: '#3c8cff' },
  'bytedance-seed':{ name: 'ByteDance Seed',color: '#3c8cff' },
  'baidu':         { name: 'Baidu',         color: '#2932e1' },
  'tencent':       { name: 'Tencent',       color: '#0052d9' },
  'stepfun':       { name: 'StepFun',       color: '#7c5cff' },
  'inclusionai':   { name: 'InclusionAI',   color: '#7c5cff' },
  'ai21':          { name: 'AI21',          color: '#ff6b35' },
  'rekaai':        { name: 'Reka',          color: '#7c5cff' },
  'writer':        { name: 'Writer',        color: '#5a4ad1' },
  'inflection':    { name: 'Inflection',    color: '#7c5cff' },
  'liquid':        { name: 'Liquid',        color: '#0ea5e9' },
  'allenai':       { name: 'Allen AI',      color: '#7c5cff' },
  'openrouter':    { name: 'OpenRouter',    color: '#7c5cff' },
  'nousresearch':  { name: 'Nous Research', color: '#7c5cff' },
};
function providerMeta(slug) {
  const clean = (slug || '').replace(/^~/, '');
  return PROVIDER_META[clean] || { name: clean.replace(/-/g,' ').replace(/\b\w/g, c => c.toUpperCase()), color: '#7c5cff' };
}
function providerInitial(slug) {
  const meta = providerMeta(slug);
  return meta.name.split(/[\s()]/).filter(Boolean)[0]?.[0] || '?';
}

// ---------- Category colors ----------
const CAT_COLOR = {
  coding: '#22c55e', agentic: '#3b82f6', reasoning: '#a855f7', writing: '#ec4899',
  design: '#f59e0b', vision: '#06b6d4', speed: '#f43f5e', value: '#10b981',
  math: '#8b5cf6', 'long-context': '#0ea5e9', multilingual: '#84cc16', search: '#94a3b8',
};
function catColor(c) { return CAT_COLOR[c] || '#7c5cff'; }

// ---------- Format helpers ----------
function fmtPrice(n) {
  if (n == null || n < 0) return '—';
  if (n === 0) return 'free';
  if (n < 0.01) return `$${n.toFixed(4)}`;
  if (n < 1) return `$${n.toFixed(3)}`;
  return `$${n.toFixed(2)}`;
}
function fmtContext(n) {
  if (!n) return '—';
  if (n >= 1_000_000) return `${(n/1_000_000).toFixed(n%1_000_000?'1':'0')}M`;
  if (n >= 1000) return `${(n/1000).toFixed(0)}K`;
  return String(n);
}
function fmtDate(iso) {
  if (!iso) return '—';
  try { return new Date(iso).toLocaleDateString(undefined, { year:'numeric', month:'short', day:'numeric' }); }
  catch { return iso; }
}
function fmtRelative(iso) {
  if (!iso) return '—';
  const ms = Date.now() - new Date(iso).getTime();
  const mins = Math.floor(ms/60000);
  if (mins < 1) return 'just now';
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins/60);
  if (hrs < 24) return `${hrs}h ago`;
  const days = Math.floor(hrs/24);
  return `${days}d ago`;
}
function escapeHtml(s) { return String(s||'').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }
function escapeAttr(s) { return escapeHtml(s).replace(/`/g,''); }

// ---------- Provider detection ----------
function getProvider(m) { return (m.provider || (m.id || '').split('/')[0] || '').replace(/^~/, ''); }
function isOpenWeights(m) {
  const id = m.id || '';
  if ((m.specialties || []).includes('open-weights')) return true;
  // Heuristic: model id matches an open-source family
  return /llama|qwen|deepseek|phi|^mistralai\/mistral-|nemotron|granite|minimax|hermes|olmo|glm-|qwen|mimo|cogito|magistral|codestral|mistral\.|(^|[\/:])minimax|mistral-nemo|llama-3|llama-4|mistral-7b|llama-3\.1|llama-3\.2|llama-3\.3|qwen2|qwen3|qwen-2|mistral-large|ministral|deepseek-coder|deepseek-v|gemma|flux|whisper/.test(id);
}

function totalPrice(m) {
  const a = m.pricing_in_per_m, b = m.pricing_out_per_m;
  const ai = (a == null || a < 0) ? Infinity : a;
  const bi = (b == null || b < 0) ? Infinity : b;
  if (ai === 0 && bi === 0) return 0;
  return ai + bi * 4;
}
function scores(m) { return m.scores || {}; }

// ---------- Filter / sort ----------
function getVisibleModels() {
  let ms = state.data.models.slice();
  const q = state.search.toLowerCase().trim();
  if (q) {
    ms = ms.filter(m =>
      (m.name || '').toLowerCase().includes(q) ||
      (m.id || '').toLowerCase().includes(q) ||
      (m.description || '').toLowerCase().includes(q) ||
      (m.specialties || []).some(s => s.includes(q)) ||
      getProvider(m).toLowerCase().includes(q)
    );
  }
  if (state.filters.free)   ms = ms.filter(m => m.pricing_in_per_m === 0 && m.pricing_out_per_m === 0);
  if (state.filters.open)   ms = ms.filter(m => isOpenWeights(m));
  if (state.filters.vision) ms = ms.filter(m => (m.modality_in || []).includes('image'));
  if (state.filters.tools)  ms = ms.filter(m => m.supports_tools);
  if (state.filters.reason) ms = ms.filter(m => !!m.supports_reasoning);

  const s = state.sort;
  ms.sort((a, b) => {
    if (s === 'name') return (a.name || '').localeCompare(b.name || '');
    if (s === 'context-desc') return (b.context_length || 0) - (a.context_length || 0);
    if (s === 'price-asc')  return (totalPrice(a) - totalPrice(b));
    if (s === 'price-desc') return (totalPrice(b) - totalPrice(a));
    if (s === 'speed-desc') return ((scores(a).speed || 0) - (scores(b).speed || 0));
    if (s === 'newest') return (b.created || 0) - (a.created || 0);
    return (getProvider(a) || '').localeCompare(getProvider(b) || '') || (a.name || '').localeCompare(b.name || '');
  });
  return ms;
}

// ---------- Promo rail ----------
function renderPromos() {
  const rail = $('#promoRail');
  const items = (state.data.free_promos_section || []).slice(0, 24);
  if (!items.length) {
    rail.innerHTML = '<div class="no-results" style="grid-column:1/-1;padding:24px">No free promos tracked right now.</div>';
    return;
  }
  rail.innerHTML = items.map(m => {
    const p = (m.promos || [])[0];
    const ongoing = !p || p.end === 'ongoing' || !p.end;
    const endHtml = p && p.end && p.end !== 'ongoing'
      ? `<div class="pend">${ICON.calendar} Ends ${fmtDate(p.end)}</div>`
      : (p ? `<div class="pend ongoing">${ICON.infinity} ${escapeHtml(p.promo || 'Ongoing')}</div>` : '');
    return `
      <div class="promo-card" data-id="${escapeAttr(m.id)}">
        <span class="ribbon">Free</span>
        <div class="pname">${escapeHtml(m.name || m.id)}</div>
        <div class="pprov">${escapeHtml(providerMeta(m.provider).name)}</div>
        <div class="pmeta">
          <span><b>${fmtContext(m.context_length)}</b> ctx</span>
          ${(m.modality_in||[]).includes('image') ? '<span class="pip">·</span><span>vision</span>' : ''}
          ${m.supports_tools ? '<span class="pip">·</span><span>tools</span>' : ''}
        </div>
        ${endHtml}
      </div>
    `;
  }).join('');
  $$('#promoRail .promo-card').forEach(card => {
    card.addEventListener('click', () => {
      const m = state.data.models.find(x => x.id === card.dataset.id);
      if (m) showModal(m);
    });
  });
}

// ---------- Model card ----------
function renderCard(m) {
  const specs = m.specialties || [];
  const sc = m.scores || {};
  const isFree = m.pricing_in_per_m === 0 && m.pricing_out_per_m === 0;
  const isOpen = isOpenWeights(m);
  const hasVision = (m.modality_in || []).includes('image');
  const hasTools = !!m.supports_tools;
  const hasReason = !!m.supports_reasoning;
  const cat = state.activeCategory;
  const catScore = cat ? (sc[cat] || 0) : null;
  const isHighlighted = cat && (specs.includes(cat) || (catScore && catScore >= 80));
  const hl = cat ? catColor(cat) : null;

  const total = (m.pricing_in_per_m || 0) + (m.pricing_out_per_m || 0) * 4;

  const tags = (cat ? specs.filter(s => s === cat) : specs).slice(0, 4).map(s => {
    const hot = cat && s === cat;
    return `<span class="tag ${hot ? 'hot' : ''}" ${hot ? `style="--hl:${catColor(cat)}"` : ''}>${s}</span>`;
  }).join('');

  const scoreOrder = ['coding','agentic','reasoning','speed','value','math','writing','design'];
  const scoreChips = scoreOrder.filter(k => sc[k] != null).slice(0, 4).map(k => {
    const v = sc[k];
    const strong = cat === k || (cat && v >= 80);
    return `<span class="score-chip ${strong?'strong':''}" ${strong?`style="--hl:${catColor(cat||k)}"`:''}><b>${v}</b>${k.slice(0,4)}</span>`;
  }).join('');

  const freeIn  = m.pricing_in_per_m === 0;
  const freeOut = m.pricing_out_per_m === 0;
  const inVal  = freeIn  ? '<span class="free">free</span>' : fmtPrice(m.pricing_in_per_m);
  const outVal = freeOut ? '<span class="free">free</span>' : fmtPrice(m.pricing_out_per_m);

  return `
    <div class="model-card ${isHighlighted ? 'highlighted' : ''}" data-id="${escapeAttr(m.id)}" ${isHighlighted ? `style="--hl:${hl}"` : ''}>
      <div class="mc-top">
        <div class="mc-title">
          <div class="mc-name">${escapeHtml(m.name || m.id)}</div>
          <div class="mc-provider">${escapeHtml(providerMeta(getProvider(m)).name)}</div>
        </div>
        <div class="mc-badges">
          ${isFree ? '<span class="badge badge-free">Free</span>' : ''}
          ${isOpen ? '<span class="badge badge-open">Open</span>' : ''}
          ${hasVision ? `<span class="badge badge-vision">${ICON.eye}</span>` : ''}
          ${hasTools  ? `<span class="badge badge-tools">${ICON.wrench}</span>` : ''}
          ${hasReason ? `<span class="badge badge-reason">${ICON.brain}</span>` : ''}
        </div>
      </div>
      <div class="mc-stats">
        <div class="mc-stat">
          <div class="mc-stat-label">Context</div>
          <div class="mc-stat-val">${fmtContext(m.context_length)}</div>
        </div>
        <div class="mc-stat">
          <div class="mc-stat-label">In / Out <span class="small">per 1M</span></div>
          <div class="mc-stat-val">${inVal} <span class="small">/</span> ${outVal}</div>
        </div>
        <div class="mc-stat">
          <div class="mc-stat-label">Speed</div>
          <div class="mc-stat-val">${sc.speed != null ? sc.speed + '<span class="small">/100</span>' : '—'}</div>
        </div>
        <div class="mc-stat">
          <div class="mc-stat-label">Est total*</div>
          <div class="mc-stat-val">${(freeIn && freeOut) ? '<span class="free">free</span>' : fmtPrice(total) + '<span class="small">/1M</span>'}</div>
        </div>
      </div>
      ${scoreChips ? `<div class="mc-scores">${scoreChips}</div>` : ''}
      ${tags ? `<div class="mc-tags">${tags}</div>` : ''}
      ${m.blurb ? `<div class="mc-blurb">${escapeHtml(m.blurb)}</div>` : ''}
    </div>
  `;
}

// ---------- Provider sections ----------
function renderModels() {
  const container = $('#providerSections');
  const visible = getVisibleModels();
  $('#visibleCount').textContent = `${visible.length} model${visible.length===1?'':'s'}`;
  $('#noResults').hidden = visible.length > 0;

  if (!visible.length) return;

  const groups = {};
  visible.forEach(m => {
    const p = getProvider(m);
    (groups[p] = groups[p] || []).push(m);
  });
  const providerKeys = Object.keys(groups).sort();

  container.innerHTML = providerKeys.map(p => {
    const meta = providerMeta(p);
    const models = groups[p];
    return `
      <div class="provider-section">
        <div class="provider-head">
          <span class="logo" style="background:${meta.color}">${escapeHtml(providerInitial(p))}</span>
          <h3>${escapeHtml(meta.name)}</h3>
          <span class="count">${models.length}</span>
          <a href="#" class="show-all" data-prov="${escapeAttr(p)}">View all <svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"/></svg></a>
        </div>
        <div class="models-grid">
          ${models.map(renderCard).join('')}
        </div>
      </div>
    `;
  }).join('');

  $$('.model-card').forEach(el => el.addEventListener('click', () => {
    const m = state.data.models.find(x => x.id === el.dataset.id);
    if (m) showModal(m);
  }));
  $$('.show-all').forEach(el => el.addEventListener('click', e => {
    e.preventDefault();
    const p = el.dataset.prov;
    // Scroll to provider
    const sect = [...$$('.provider-section')].find(s => s.querySelector('h3')?.textContent === providerMeta(p).name);
    if (sect) sect.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }));
}

// ---------- Subscriptions ----------
function renderSubs() {
  const grid = $('#subsGrid');
  const subs = state.data.subscriptions || [];
  grid.innerHTML = subs.map(s => {
    const price = s.price_usd_per_month;
    const cls = price === 0 ? 'free' : 'sub';
    const badgeText = price === 0 ? 'Free tier' : 'Subscription';
    const badgeCls = price === 0 ? 'free' : 'sub';
    const priceHtml = price === null
      ? '<div class="sub-price custom">Custom pricing</div>'
      : `<div class="sub-price">${price === 0 ? 'Free' : '$' + price}<span class="per"> /mo</span></div>`;
    return `
      <div class="sub-card">
        <div class="sub-top">
          <div>
            <div class="sub-name">${escapeHtml(s.name)}</div>
            <div class="sub-provider">${escapeHtml(s.provider)}</div>
          </div>
          <span class="sub-badge ${badgeCls}">${badgeText}</span>
        </div>
        ${priceHtml}
        <div class="sub-limits">${escapeHtml(s.limits || '')}</div>
        ${s.notes ? `<div class="sub-notes">${escapeHtml(s.notes)}</div>` : ''}
      </div>
    `;
  }).join('');
}

// ---------- Modal ----------
function showModal(m) {
  const sc = m.scores || {};
  const specs = m.specialties || [];
  const hosting = m.hosting || [];
  const scoreOrder = ['coding','agentic','reasoning','writing','design','vision','speed','value','math','long-context','multilingual','search'];
  const meta = providerMeta(getProvider(m));

  const inFree  = m.pricing_in_per_m === 0;
  const outFree = m.pricing_out_per_m === 0;
  const inVal  = inFree  ? '<span class="free">free</span>' : '$' + fmtPrice(m.pricing_in_per_m).replace('$','');
  const outVal = outFree ? '<span class="free">free</span>' : '$' + fmtPrice(m.pricing_out_per_m).replace('$','');

  $('#modalBody').innerHTML = `
    <div class="modal-inner">
      <div class="mh-eyebrow">
        <span class="logo" style="background:${meta.color}">${escapeHtml(providerInitial(getProvider(m)))}</span>
        ${escapeHtml(meta.name)} · <span style="font-family:var(--font-mono); text-transform:none; letter-spacing:0">${escapeHtml(m.id)}</span>
      </div>
      <h2 class="mh-title" id="modalTitle">${escapeHtml(m.name || m.id)}</h2>
      ${m.blurb ? `<p class="mh-blurb">${escapeHtml(m.blurb)}</p>` : (m.description ? `<p class="mh-blurb">${escapeHtml(m.description)}</p>` : '')}

      <div class="modal-section">
        <h3>Pricing &amp; specs</h3>
        <div class="modal-pricing">
          <div class="metric">
            <div class="label">Context</div>
            <div class="val">${fmtContext(m.context_length)}</div>
          </div>
          <div class="metric">
            <div class="label">Max output</div>
            <div class="val ${!m.max_completion_tokens ? 'muted' : ''}">${fmtContext(m.max_completion_tokens)}</div>
          </div>
          <div class="metric">
            <div class="label">$ input / 1M</div>
            <div class="val ${inFree ? 'free' : ''}">${inVal}</div>
          </div>
          <div class="metric">
            <div class="label">$ output / 1M</div>
            <div class="val ${outFree ? 'free' : ''}">${outVal}</div>
          </div>
        </div>
      </div>

      <div class="modal-section">
        <h3>Capabilities</h3>
        <div class="modal-badges">
          ${(m.modality_in || []).map(x => `<span class="cap-chip">in: ${x}</span>`).join('')}
          ${(m.modality_out || []).map(x => `<span class="cap-chip">out: ${x}</span>`).join('')}
          ${m.supports_tools ? `<span class="cap-chip on">tools ✓</span>` : ''}
          ${m.supports_structured_output ? `<span class="cap-chip on">JSON schema ✓</span>` : ''}
          ${m.supports_reasoning ? `<span class="cap-chip on">reasoning ✓</span>` : ''}
        </div>
      </div>

      ${specs.length ? `
        <div class="modal-section">
          <h3>Specialties</h3>
          <div class="modal-badges">
            ${specs.map(s => `<span class="cap-chip" style="color:${catColor(s)}; border-color:color-mix(in srgb, ${catColor(s)} 30%, var(--line)); background:color-mix(in srgb, ${catColor(s)} 10%, var(--bg-2))">${s}</span>`).join('')}
          </div>
        </div>
      ` : ''}

      ${Object.keys(sc).length ? `
        <div class="modal-section">
          <h3>Performance scores</h3>
          <div class="modal-scores">
            ${scoreOrder.filter(k => sc[k] != null).map(k => `
              <div class="modal-score" style="--c:${catColor(k)}">
                <div class="row"><span>${k}</span><b>${sc[k]}<span style="opacity:.6">/100</span></b></div>
                <div class="bar"><div class="fill" style="width: ${sc[k]}%"></div></div>
              </div>
            `).join('')}
          </div>
        </div>
      ` : ''}

      <div class="modal-section">
        <h3>Where to use it · ${hosting.length} service${hosting.length===1?'':'s'}</h3>
        ${hosting.length ? `
          <div class="hosting-list">
            ${hosting.map(h => `
              <div class="hosting-item">
                <span class="hi-type ${h.type}">${h.type}</span>
                <div>
                  <div class="hi-name">${escapeHtml(h.name)}</div>
                  ${h.notes ? `<div class="hi-notes">${escapeHtml(h.notes)}</div>` : ''}
                </div>
                <div class="hi-price">${h.price_usd_per_month != null ? (h.price_usd_per_month === 0 ? 'Free' : '$' + h.price_usd_per_month + '/mo') : ''}</div>
                <a class="hi-link" href="${h.url}" target="_blank" rel="noopener">Open <svg viewBox="0 0 24 24" width="11" height="11" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg></a>
              </div>
            `).join('')}
          </div>
        ` : '<p style="color:var(--text-2); font-size:13px">No hosting services tracked yet for this model. Try <a href="https://openrouter.ai" target="_blank">OpenRouter</a> — most models appear there within hours of release.</p>'}
      </div>

      <div class="modal-section" style="border-top: none; padding-top: 8px;">
        <p style="font-size:11px; color:var(--text-3); margin: 0; display: flex; align-items: center; gap: 12px; flex-wrap: wrap;">
          ${m.created ? `<span>Released ${fmtDate(new Date(m.created*1000).toISOString())}</span>` : ''}
          ${m.knowledge_cutoff ? `<span>Knowledge: ${m.knowledge_cutoff}</span>` : ''}
          <span style="margin-left:auto; font-style:italic">Pricing &amp; specs via OpenRouter</span>
        </p>
      </div>
    </div>
  `;
  $('#modal').hidden = false;
  // Center card with JS (CSS %/vh don't work in fixed containers on iOS for tall pages)
  const card = document.querySelector('.modal-card');
  if (card) {
    const positionCard = () => {
      const vh = window.innerHeight;
      const ch = card.offsetHeight;
      const top = Math.max(8, Math.floor((vh - ch) / 2));
      card.style.marginTop = `${top}px`;
      card.style.maxHeight = `${vh - 32}px`;
    };
    positionCard();
    window.addEventListener('resize', positionCard, { once: true });
  }
  // Lock scroll without breaking position:fixed on iOS Safari
  document.documentElement.style.overflow = 'hidden';
}
function hideModal() {
  $('#modal').hidden = true;
  const card = document.querySelector('.modal-card');
  if (card) { card.style.marginTop = ''; card.style.maxHeight = ''; }
  document.documentElement.style.overflow = '';
}

// ---------- Top bar stats ----------
function updateStats() {
  if (!state.data) return;
  $('#statProviders').textContent = state.data.provider_count;
  $('#statModels').textContent = state.data.model_count;
  $('#statFree').textContent = state.data.free_model_count;
  $('#brandSub').textContent = `Live frontier model comparison · ${state.data.model_count} models, ${state.data.provider_count} providers`;
}

// ---------- Sync indicator ----------
let syncPolling = null;
let syncState = { syncing: false, last_sync_at: null, last_sync_status: null };

function setSyncIndicator(syncing, lastSyncAt, status) {
  const dot = document.querySelector('.pulse-dot');
  const txt = $('#lastUpdated');
  const icon = $('#syncIcon');
  if (syncing) {
    if (dot) dot.style.background = 'var(--amber)';
    if (txt) txt.textContent = 'Syncing…';
    if (icon) icon.style.animation = 'spin 1s linear infinite';
  } else {
    if (dot) dot.style.background = status === 'error' ? 'var(--red)' : 'var(--green)';
    if (txt) txt.textContent = lastSyncAt ? `Synced ${fmtRelative(lastSyncAt)}` : 'Not synced yet';
    if (icon) icon.style.animation = '';
  }
}

async function pollSync() {
  try {
    const r = await fetch('api/status', { cache: 'no-store' });
    if (!r.ok) return;
    const data = await r.json();
    syncState = data;
    setSyncIndicator(data.syncing, data.last_sync_at, data.last_sync_status);
    // If we were syncing and now we're not, reload the page to pick up new data
    if (!data.syncing && sessionStorage.getItem('llm-tracker-was-syncing') === '1') {
      sessionStorage.removeItem('llm-tracker-was-syncing');
      showToast('Data synced — refreshing');
      setTimeout(() => location.reload(), 800);
    }
    if (data.syncing) {
      sessionStorage.setItem('llm-tracker-was-syncing', '1');
    }
  } catch (e) { /* ignore */ }
}

async function triggerManualSync() {
  try {
    const r = await fetch('api/refresh', { method: 'POST', cache: 'no-store' });
    if (!r.ok) throw new Error('HTTP ' + r.status);
    const data = await r.json();
    if (data.status === 'already_running') {
      showToast('Sync already in progress…');
    } else {
      showToast('Sync started…');
      sessionStorage.setItem('llm-tracker-was-syncing', '1');
    }
    // Start polling more aggressively
    if (syncPolling) clearInterval(syncPolling);
    syncPolling = setInterval(pollSync, 1500);
    setTimeout(() => {
      if (syncPolling) { clearInterval(syncPolling); syncPolling = setInterval(pollSync, 30_000); }
    }, 60_000);
    pollSync();
  } catch (e) {
    showToast('Sync failed: ' + e.message, true);
  }
}

function showToast(msg, isError = false) {
  const t = $('#toast');
  if (!t) return;
  t.textContent = msg;
  t.classList.toggle('error', isError);
  t.hidden = false;
  requestAnimationFrame(() => t.classList.add('show'));
  setTimeout(() => {
    t.classList.remove('show');
    setTimeout(() => { t.hidden = true; }, 250);
  }, 3000);
}

// ---------- Filter count badge ----------
function updateFilterCount() {
  const c = $('#filterCount');
  if (!c) return;
  const activeFilters = Object.values(state.filters).filter(Boolean).length;
  const activeCat = state.activeCategory ? 1 : 0;
  const activeSearch = state.search.trim() ? 1 : 0;
  const total = activeFilters + activeCat + activeSearch;
  if (total > 0) {
    c.textContent = total;
    c.hidden = false;
    $('#filterToggle')?.classList.add('active-filters');
  } else {
    c.hidden = true;
    $('#filterToggle')?.classList.remove('active-filters');
  }
}

// ---------- Event wiring ----------
const $ = (s, r=document) => r.querySelector(s);
const $$ = (s, r=document) => Array.from(r.querySelectorAll(s));

function setupEvents() {
  $('#searchBox').addEventListener('input', e => { state.search = e.target.value; renderModels(); updateFilterCount(); });
  $('#sortBy').addEventListener('change', e => { state.sort = e.target.value; renderModels(); });

  ['filterFree','filterOpen','filterVision','filterTools','filterReason'].forEach(id => {
    const el = $('#' + id);
    if (el) el.addEventListener('change', e => {
      const k = id.replace('filter','').toLowerCase();
      state.filters[k] = e.target.checked;
      renderModels();
      updateFilterCount();
    });
  });

  // Filter bar collapse toggle
  const filterToggle = $('#filterToggle');
  const filterBody = $('#filterBody');
  const filterbar = $('#filterbar');
  if (filterToggle && filterBody) {
    // On desktop (>= 920px) start expanded; on mobile start collapsed.
    // We detect by checking the CSS that .filter-row-top layout switches.
    const startExpanded = window.matchMedia('(min-width: 920px)').matches;
    function setExpanded(open) {
      filterToggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      filterBody.hidden = !open;
      filterbar.classList.toggle('expanded', open);
    }
    setExpanded(startExpanded);
    filterToggle.addEventListener('click', () => {
      const open = filterToggle.getAttribute('aria-expanded') === 'true';
      setExpanded(!open);
    });
    // Auto-collapse when user scrolls past the hero on mobile
    let lastY = 0, ticking = false;
    function onScroll() {
      if (ticking) return; ticking = true;
      requestAnimationFrame(() => {
        const y = window.scrollY;
        if (window.innerWidth < 920 && y > 240 && !filterToggle._manuallyOpened) {
          setExpanded(false);
        }
        lastY = y;
        ticking = false;
      });
      positionCard();
      window.addEventListener('resize', positionCard, { once: true });
      }

  $$('.cat-pill').forEach(btn => {
    btn.addEventListener('click', () => {
      const cat = btn.dataset.cat;
      if (!cat) {
        state.activeCategory = null;
        $$('.cat-pill').forEach(b => b.classList.remove('active'));
      } else {
        if (state.activeCategory === cat) {
          state.activeCategory = null;
          btn.classList.remove('active');
        } else {
          state.activeCategory = cat;
          $$('.cat-pill').forEach(b => b.classList.remove('active'));
          btn.classList.add('active');
        }
      }
      renderModels();
      updateFilterCount();
    });
  });

  $$('[data-close]').forEach(el => el.addEventListener('click', hideModal));
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape') hideModal();
    if (e.key === '/' && document.activeElement.tagName !== 'INPUT') {
      e.preventDefault();
      $('#searchBox').focus();
    }
  });

  $('#resetFilters')?.addEventListener('click', () => {
    state.search = ''; state.activeCategory = null;
    Object.keys(state.filters).forEach(k => state.filters[k] = false);
    Object.keys(state.filters).forEach(k => { const el = $('#filter' + k[0].toUpperCase() + k.slice(1)); if (el) el.checked = false; });
    $$('.cat-pill').forEach(b => b.classList.remove('active'));
    $('#searchBox').value = '';
    renderModels();
    updateFilterCount();
  });

  // Theme toggle
  $('#themeBtn')?.addEventListener('click', () => {
    const cur = document.documentElement.getAttribute('data-theme');
    const next = cur === 'light' ? 'dark' : 'light';
    if (next === 'dark') document.documentElement.removeAttribute('data-theme');
    else document.documentElement.setAttribute('data-theme', next);
    try { localStorage.setItem('llm-tracker-theme', next); } catch {}
  });
  // Restore theme
  try {
    const t = localStorage.getItem('llm-tracker-theme');
    if (t === 'light') document.documentElement.setAttribute('data-theme', 'light');
  } catch {}

  // Sync button
  $('#syncBtn')?.addEventListener('click', triggerManualSync);
}

// ---------- Boot ----------
async function boot() {
  // Use embedded data immediately — zero network delay
  if (window.__LLM_TRACKER_DATA__) {
    state.data = window.__LLM_TRACKER_DATA__;
  }
  // Then try to fetch fresh data in background (non-blocking)
  let retries = 0;
  const maxRetries = 2;
  const tryFetch = async () => {
    try {
      const r = await fetch(`models.json?v=${Date.now()}`, { cache: 'no-store' });
      if (r.ok) {
        const fresh = await r.json();
        if (fresh && fresh.models) { state.data = fresh; }
      }
    } catch (e) {
      // Fall back to embedded data silently
      retries++;
      if (retries < maxRetries) { setTimeout(tryFetch, 2000 * retries); }
    }
  };
  if (!state.data) {
    retries = maxRetries; // Force fetch loop
    await tryFetch();
    if (!state.data) {
      $('#providerSections').innerHTML = `
        <div class="no-results" style="padding: 80px 20px">
          <svg viewBox="0 0 24 24" width="40" height="40" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
          <h3>Couldn't load model data</h3>
          <p>Try refreshing the page. If the problem persists, the data source may be down.</p>
        </div>`;
      return;
    }
  } else {
    // Fire-and-forget background refresh
    tryFetch();
  }

  updateStats();
  setupEvents();
  renderPromos();
  renderModels();
  renderSubs();

  function tickUpdated() { $('#lastUpdated').textContent = state.data?.generated_at ? `Synced ${fmtRelative(state.data.generated_at)}` : `Embedded data`; }
  tickUpdated();
  setInterval(tickUpdated, 60_000);

  pollSync();
  setInterval(pollSync, 30_000);
}

document.addEventListener('DOMContentLoaded', boot);
