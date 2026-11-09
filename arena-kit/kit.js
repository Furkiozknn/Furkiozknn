/* ARENA-KIT v1 — shared layer for the 21 Claude Game Arena games.
 *
 * Injected inline into each game's index.html (between begin/end marker comments) by
 * arena-kit/inject.py, so every game stays a single file. Plain script, no imports, no network.
 * Everything is optional: a game that never calls Arena.* behaves exactly as before.
 *
 *   Arena.perf.attach(renderer)        dynamic pixel ratio for weak GPUs (Intel UHD)
 *   Arena.hint(id, text)               one-time hint toast (first 30 s guidance)
 *   Arena.endCard({...})               end-of-session card: reason, score, "again", another game
 *   Arena.daily(game, {dayKey})        UTC-day seed (or the game's own day key) + mulberry32 rng + streak
 *   Arena.quiet                        true on ?auto / ?nosave / ?demo: nothing is written to localStorage
 *   Arena.share({...})                 Web Share / clipboard text + optional PNG card
 *   Arena.profile(), Arena.award(id)   cross-game passport (shared origin localStorage)
 *   Arena.settings / openSettings()    accessibility panel (text size, contrast, motion, vibration, auto-pause)
 *
 * Storage: every key starts with "arena." and is versioned; every access is wrapped in try/catch
 * (private mode, quota, portals). Pure logic lives in Arena._core so it can be tested in Node.
 */
(function (root) {
  'use strict';
  if (root.Arena && root.Arena.version) return; // injected twice (e.g. iframe) -> keep the first
  var VERSION = '1.0.1';
  var hasDOM = typeof document !== 'undefined';

  /* ---------- core (pure, Node-testable) ---------- */
  var core = {};

  core.dayKey = function (date) { // UTC YYYYMMDD
    var d = date || new Date();
    return d.getUTCFullYear() * 10000 + (d.getUTCMonth() + 1) * 100 + d.getUTCDate();
  };
  core.localDayKey = function (date) { // local-time YYYYMMDD (for games whose own daily turns at local midnight)
    var d = date || new Date();
    return d.getFullYear() * 10000 + (d.getMonth() + 1) * 100 + d.getDate();
  };
  // Bot / demo / no-save runs must not touch the player's storage: ?auto, ?nosave, ?demo (any value).
  core.isQuiet = function (search) { return /[?&](auto|nosave|demo)(=|&|$)/.test(search || ''); };
  core.prevDayKey = function (key) {
    var y = Math.floor(key / 10000), m = Math.floor(key / 100) % 100, d = key % 100;
    return core.dayKey(new Date(Date.UTC(y, m - 1, d) - 86400000));
  };
  core.hash = function (str) { // FNV-1a 32-bit
    var h = 0x811c9dc5;
    for (var i = 0; i < str.length; i++) { h ^= str.charCodeAt(i); h = Math.imul(h, 0x01000193) >>> 0; }
    return h >>> 0;
  };
  core.mulberry32 = function (seed) {
    var a = seed >>> 0;
    return function () {
      a = (a + 0x6D2B79F5) >>> 0;
      var t = a;
      t = Math.imul(t ^ (t >>> 15), t | 1);
      t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  };
  // Streak after finishing the daily run on `today`: same day keeps it, yesterday +1, gap resets to 1.
  core.nextStreak = function (rec, today) {
    rec = rec || { last: 0, streak: 0, best: 0 };
    var out = { last: today, streak: 1, best: rec.best || 0 };
    if (rec.last === today) out.streak = rec.streak || 1;
    else if (rec.last && rec.last === core.prevDayKey(today)) out.streak = (rec.streak || 0) + 1;
    out.best = Math.max(out.best, out.streak);
    return out;
  };
  // Dynamic-resolution controller. Feed frame times (ms); returns the pixel ratio to use.
  core.perfController = function (opts) {
    opts = opts || {};
    var s = {
      min: opts.min || 0.6, max: opts.max || 2, ratio: opts.start || opts.max || 2,
      slow: opts.slowMs || 22, fast: opts.fastMs || 14, avg: 16.7, n: 0, cool: 0,
    };
    s.feed = function (dt, now) {
      if (!(dt > 0) || dt > 250) return s.ratio; // tab switch / breakpoint: ignore
      s.avg += (dt - s.avg) * (1 / 30); s.n++;
      if (s.n < 60 || now < s.cool) return s.ratio;
      if (s.avg > s.slow && s.ratio > s.min) { s.ratio = Math.max(s.min, +(s.ratio * 0.85).toFixed(3)); s.cool = now + 2000; }
      else if (s.avg < s.fast && s.ratio < s.max) { s.ratio = Math.min(s.max, +(s.ratio * 1.1).toFixed(3)); s.cool = now + 4000; }
      return s.ratio;
    };
    return s;
  };
  core.shareText = function (o) {
    var lines = [o.title || o.game || 'Claude Game Arena'];
    (o.lines || []).forEach(function (l) { lines.push(String(l)); });
    if (o.url) lines.push(o.url);
    return lines.join('\n');
  };

  /* ---------- storage ---------- */
  var mem = {};
  var quiet = false;
  try { quiet = hasDOM && core.isQuiet(location.search); } catch (e) {}
  function store() { if (quiet) return null; try { return root.localStorage; } catch (e) { return null; } }
  function get(key, fallback) {
    var s = store(), raw = null;
    try { raw = s ? s.getItem('arena.' + key) : (key in mem ? mem[key] : null); } catch (e) { raw = null; }
    if (raw == null) return fallback;
    try { var v = JSON.parse(raw); return v == null ? fallback : v; } catch (e) { return fallback; }
  }
  function set(key, val) {
    var raw = JSON.stringify(val), s = store();
    try { if (s) s.setItem('arena.' + key, raw); else mem[key] = raw; } catch (e) { mem[key] = raw; }
  }

  /* ---------- language ---------- */
  var STR = {
    tr: { again: 'Bir daha', another: 'Başka bir oyun dene', close: 'Kapat', settings: 'Erişilebilirlik',
      textSize: 'Yazı boyutu', contrast: 'Yüksek karşıtlık', motion: 'Hareketi azalt', vibration: 'Titreşim',
      autoPause: 'Sekme değişince duraklat', copied: 'Panoya kopyalandı', streak: 'Seri', days: 'gün', share: 'Paylaş' },
    en: { again: 'Play again', another: 'Try another game', close: 'Close', settings: 'Accessibility',
      textSize: 'Text size', contrast: 'High contrast', motion: 'Reduce motion', vibration: 'Vibration',
      autoPause: 'Pause when the tab is hidden', copied: 'Copied to clipboard', streak: 'Streak', days: 'days', share: 'Share' },
  };
  var lang = 'en';
  try { lang = /^tr/i.test((hasDOM && document.documentElement.lang) || (root.navigator && navigator.language) || '') ? 'tr' : 'en'; } catch (e) {}
  function t(k) { return (STR[lang] && STR[lang][k]) || STR.en[k] || k; }

  /* ---------- game id + passport ---------- */
  var GAMES = ['bogaz-vapuru', 'carsi-kacisi', 'cay-ocagi', 'cini-ustasi', 'dolmus', 'ebru', 'fay-hatti', 'hamsi',
    'kale-savunmasi', 'kapadokya-balonu', 'karagoz', 'kervan', 'kirkpinar', 'lale-bahcesi', 'marti', 'mehter',
    'mimar-sinan', 'pamukkale', 'peri-golf', 'simit-firini', 'topkapi-gecesi'];
  var gameId = 'unknown';
  try {
    var seg = (hasDOM && location.pathname.split('/').filter(Boolean)[0]) || '';
    var meta = hasDOM && document.querySelector('meta[name="arena-game"]');
    gameId = (meta && meta.content) || (GAMES.indexOf(seg) >= 0 ? seg : 'unknown');
  } catch (e) {}
  function profile() { return get('profile.v1', { plays: {}, badges: {}, last: null, first: null }); }
  function touchProfile() {
    var p = profile(), now = Date.now();
    p.plays[gameId] = (p.plays[gameId] || 0) + 1; p.last = { game: gameId, at: now }; p.first = p.first || now;
    set('profile.v1', p); return p;
  }
  function award(id, label) {
    var p = profile(); if (p.badges[id]) return false;
    p.badges[id] = { at: Date.now(), game: gameId, label: label || id }; set('profile.v1', p); return true;
  }

  /* ---------- settings ---------- */
  var DEFAULTS = { textScale: 1, highContrast: false, reducedMotion: null, vibration: true, autoPause: true };
  var settings = Object.assign({}, DEFAULTS, get('settings.v1', {}));
  if (settings.reducedMotion === null) {
    try { settings.reducedMotion = !!(root.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches); } catch (e) { settings.reducedMotion = false; }
  }
  var listeners = { pause: [], resume: [], settings: [] };
  function emit(name, arg) { (listeners[name] || []).forEach(function (f) { try { f(arg); } catch (e) {} }); }
  function applySettings() {
    if (!hasDOM) return;
    var h = document.documentElement;
    h.style.setProperty('--arena-text-scale', String(settings.textScale));
    h.toggleAttribute('data-arena-contrast', !!settings.highContrast);
    h.toggleAttribute('data-arena-reduced-motion', !!settings.reducedMotion);
    emit('settings', settings);
  }
  // Vibration toggle without touching game code: wrap navigator.vibrate once.
  try {
    if (root.navigator && typeof navigator.vibrate === 'function' && !navigator.__arenaWrapped) {
      var vib = navigator.vibrate.bind(navigator);
      navigator.vibrate = function (p) { return settings.vibration ? vib(p) : false; };
      navigator.__arenaWrapped = true;
    }
  } catch (e) {}

  /* ---------- DOM helpers (kit UI) ---------- */
  var CSS = '' +
    '.arena-toast{position:fixed;left:50%;bottom:calc(18px + env(safe-area-inset-bottom));transform:translateX(-50%);z-index:2147483000;' +
    'max-width:min(92vw,520px);padding:10px 14px;border-radius:10px;background:rgba(14,13,11,.88);color:#f6f1e6;' +
    'font:500 calc(14px*var(--arena-text-scale,1))/1.35 system-ui,sans-serif;box-shadow:0 6px 20px rgba(0,0,0,.35);pointer-events:none;' +
    'opacity:0;transition:opacity .25s}' +
    '.arena-toast.on{opacity:1}' +
    '.arena-modal{position:fixed;inset:0;z-index:2147483001;display:flex;align-items:center;justify-content:center;background:rgba(0,0,0,.45)}' +
    '.arena-card{width:min(92vw,420px);padding:20px;border-radius:14px;background:#f6f1e6;color:#1a1712;' +
    'font:500 calc(15px*var(--arena-text-scale,1))/1.45 system-ui,sans-serif;box-shadow:0 18px 50px rgba(0,0,0,.4)}' +
    '.arena-card h2{margin:0 0 6px;font-size:1.3em}.arena-card p{margin:4px 0}' +
    '.arena-card button,.arena-card a.arena-btn{display:block;width:100%;margin-top:10px;padding:11px;border:0;border-radius:10px;' +
    'font:inherit;font-weight:700;cursor:pointer;text-align:center;text-decoration:none;box-sizing:border-box}' +
    '.arena-primary{background:#e2552f;color:#fff}.arena-secondary{background:#e7dfd0;color:#1a1712}' +
    '.arena-card label{display:flex;justify-content:space-between;align-items:center;gap:12px;margin:8px 0}' +
    '.arena-card button:focus-visible,.arena-card a:focus-visible,.arena-card input:focus-visible{outline:3px solid #3fd4dc;outline-offset:2px}' +
    '.arena-gear{position:fixed;right:calc(10px + env(safe-area-inset-right));bottom:calc(10px + env(safe-area-inset-bottom));z-index:2147482999;' +
    'width:40px;height:40px;border-radius:50%;border:0;background:rgba(14,13,11,.7);color:#f6f1e6;font:20px/40px system-ui;cursor:pointer;opacity:.7}' +
    '.arena-gear:hover,.arena-gear:focus-visible{opacity:1}' +
    'html[data-arena-contrast] body{filter:contrast(1.25) saturate(1.1)}' +
    'html[data-arena-reduced-motion] *{animation-duration:.001s!important;animation-iteration-count:1!important;transition-duration:.001s!important}';
  var styled = false;
  function style() {
    if (styled || !hasDOM) return; styled = true;
    var s = document.createElement('style'); s.id = 'arena-kit-style'; s.textContent = CSS; document.head.appendChild(s);
  }
  function el(tag, attrs, kids) {
    var e = document.createElement(tag);
    Object.keys(attrs || {}).forEach(function (k) { if (k === 'text') e.textContent = attrs[k]; else e.setAttribute(k, attrs[k]); });
    (kids || []).forEach(function (c) { e.appendChild(c); });
    return e;
  }
  var live = null;
  function announce(text) { // screen readers
    if (!hasDOM) return;
    if (!live) { live = el('div', { 'aria-live': 'polite', style: 'position:absolute;left:-9999px;width:1px;height:1px;overflow:hidden' }); document.body.appendChild(live); }
    live.textContent = ''; setTimeout(function () { live.textContent = text; }, 30);
  }
  var toastTimer = null, toastEl = null;
  function toast(text, ms) {
    if (!hasDOM || !document.body) return;
    style();
    if (!toastEl) { toastEl = el('div', { class: 'arena-toast', role: 'status' }); document.body.appendChild(toastEl); }
    toastEl.textContent = text; toastEl.classList.add('on'); announce(text);
    clearTimeout(toastTimer); toastTimer = setTimeout(function () { toastEl.classList.remove('on'); }, ms || 4000);
  }
  function modal(card) {
    style();
    var m = el('div', { class: 'arena-modal', role: 'dialog', 'aria-modal': 'true' }, [card]);
    function close() { if (m.parentNode) m.parentNode.removeChild(m); document.removeEventListener('keydown', onKey, true); }
    function onKey(e) { if (e.key === 'Escape') { e.stopPropagation(); close(); } }
    m.addEventListener('click', function (e) { if (e.target === m) close(); });
    document.addEventListener('keydown', onKey, true);
    document.body.appendChild(m);
    var f = card.querySelector('button,a,input'); if (f) f.focus();
    return close;
  }

  /* ---------- features ---------- */
  function hint(id, text, opts) {
    var seen = get('hints.v1', {});
    if (seen[gameId + ':' + id]) return false;
    seen[gameId + ':' + id] = Date.now(); set('hints.v1', seen);
    setTimeout(function () { toast(text, (opts && opts.ms) || 5000); }, (opts && opts.delay) || 0);
    return true;
  }

  function endCard(o) {
    if (!hasDOM) return function () {};
    o = o || {};
    var others = GAMES.filter(function (g) { return g !== gameId; });
    var pick = others[core.hash(String(Date.now() / 60000 | 0) + gameId) % others.length];
    var kids = [el('h2', { text: o.title || '' })];
    if (o.reason) kids.push(el('p', { text: o.reason }));
    (o.lines || []).forEach(function (l) { kids.push(el('p', { text: l })); });
    var again = el('button', { class: 'arena-primary', type: 'button', text: o.againLabel || t('again') });
    kids.push(again);
    if (o.share) {
      var sh = el('button', { class: 'arena-secondary', type: 'button', text: t('share') });
      sh.addEventListener('click', function () { share(o.share); });
      kids.push(sh);
    }
    if (o.another !== false) {
      kids.push(el('a', { class: 'arena-btn arena-secondary', href: 'https://furkiozknn.github.io/' + pick + '/', target: '_blank', rel: 'noopener', text: t('another') }));
    }
    var close = modal(el('div', { class: 'arena-card' }, kids));
    again.addEventListener('click', function () { close(); if (o.onAgain) o.onAgain(); });
    return close;
  }

  function daily(game, opts) {
    game = game || gameId;
    var own = opts && /^\d{8}$/.test(String(opts.dayKey || '')) ? +opts.dayKey : 0;
    var q = null;
    try { q = hasDOM && new URLSearchParams(location.search).get('d'); } catch (e) {}
    var day = /^\d{8}$/.test(q || '') ? +q : (own || core.dayKey());
    var seed = core.hash(game + ':' + day);
    var recs = get('daily.v1', {});
    var rec = recs[game] || { last: 0, streak: 0, best: 0 };
    return {
      day: day, seed: seed, rng: core.mulberry32(seed), streak: rec.last === day || rec.last === core.prevDayKey(day) ? rec.streak : 0,
      done: rec.last === day, best: rec.best || 0,
      complete: function (score) {
        var all = get('daily.v1', {});
        var next = core.nextStreak(all[game], day);
        next.score = Math.max(score || 0, (all[game] && all[game].last === day && all[game].score) || 0);
        all[game] = next; set('daily.v1', all);
        if (next.streak >= 3) award('streak3-' + game, game + ' 3');
        if (next.streak >= 7) award('streak7', '7');
        return next;
      },
    };
  }

  function share(o) {
    o = o || {};
    var text = core.shareText(o);
    var nav = root.navigator || {};
    if (nav.share) return nav.share({ title: o.title, text: text, url: o.url }).catch(function () {});
    if (nav.clipboard && nav.clipboard.writeText) return nav.clipboard.writeText(text).then(function () { toast(t('copied'), 2500); }, function () {});
    return Promise.resolve();
  }
  function shareCard(o) { // 1080x1350 PNG blob; returns Promise<Blob|null>
    if (!hasDOM) return Promise.resolve(null);
    var c = document.createElement('canvas'); c.width = 1080; c.height = 1350;
    var g = c.getContext('2d'); if (!g) return Promise.resolve(null);
    g.fillStyle = o.bg || '#1a1712'; g.fillRect(0, 0, 1080, 1350);
    g.fillStyle = o.accent || '#e2552f'; g.fillRect(0, 0, 1080, 18);
    g.fillStyle = '#f6f1e6'; g.font = '700 84px system-ui,sans-serif'; g.fillText(o.title || gameId, 72, 220);
    g.font = '500 52px system-ui,sans-serif';
    (o.lines || []).forEach(function (l, i) { g.fillText(String(l), 72, 340 + i * 78); });
    g.font = '500 36px system-ui,sans-serif'; g.fillStyle = '#c9bda4'; g.fillText(o.url || ('furkiozknn.github.io/' + gameId), 72, 1270);
    return new Promise(function (res) { c.toBlob ? c.toBlob(function (b) { res(b); }, 'image/png') : res(null); });
  }

  function openSettings() {
    if (!hasDOM) return;
    function row(label, input) { return el('label', {}, [el('span', { text: label }), input]); }
    function check(key) {
      var i = el('input', { type: 'checkbox' }); i.checked = !!settings[key];
      i.addEventListener('change', function () { settings[key] = i.checked; set('settings.v1', settings); applySettings(); });
      return i;
    }
    var size = el('input', { type: 'range', min: '0.85', max: '1.6', step: '0.05', 'aria-label': t('textSize') });
    size.value = String(settings.textScale);
    size.addEventListener('input', function () { settings.textScale = +size.value; set('settings.v1', settings); applySettings(); });
    var closeBtn = el('button', { class: 'arena-secondary', type: 'button', text: t('close') });
    var close = modal(el('div', { class: 'arena-card' }, [
      el('h2', { text: t('settings') }), row(t('textSize'), size), row(t('contrast'), check('highContrast')),
      row(t('motion'), check('reducedMotion')), row(t('vibration'), check('vibration')), row(t('autoPause'), check('autoPause')), closeBtn]));
    closeBtn.addEventListener('click', close);
  }
  function mountSettingsButton() {
    if (!hasDOM || document.querySelector('.arena-gear')) return;
    style();
    var b = el('button', { class: 'arena-gear', type: 'button', 'aria-label': t('settings'), title: t('settings'), text: '♿' });
    b.addEventListener('click', openSettings);
    document.body.appendChild(b);
  }

  var perf = {
    attach: function (renderer, opts) {
      if (!renderer || typeof renderer.setPixelRatio !== 'function' || !root.requestAnimationFrame) return null;
      var dpr = Math.min((root.devicePixelRatio || 1), (opts && opts.max) || 2);
      var ctl = core.perfController(Object.assign({ max: dpr, start: dpr }, opts || {}));
      var last = 0, applied = dpr, stopped = false;
      function loop(now) {
        if (stopped) return;
        if (last) {
          var r = ctl.feed(now - last, now);
          if (Math.abs(r - applied) > 0.01 && settingsQuality() === 'auto') { applied = r; try { renderer.setPixelRatio(r); } catch (e) {} }
        }
        last = now; root.requestAnimationFrame(loop);
      }
      root.requestAnimationFrame(loop);
      perf.state = ctl;
      return { stop: function () { stopped = true; }, state: ctl };
    },
  };
  function settingsQuality() { return settings.quality || 'auto'; }

  if (hasDOM) {
    document.addEventListener('visibilitychange', function () {
      if (!settings.autoPause) return;
      emit(document.hidden ? 'pause' : 'resume');
    });
    var boot = function () { applySettings(); touchProfile(); };
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot); else boot();
  }

  root.Arena = {
    version: VERSION, quiet: quiet, game: gameId, games: GAMES.slice(), lang: function (l) { if (l) lang = l === 'tr' ? 'tr' : 'en'; return lang; },
    perf: perf, hint: hint, toast: toast, endCard: endCard, daily: daily, share: share, shareCard: shareCard,
    profile: profile, award: award, settings: settings, openSettings: openSettings, mountSettingsButton: mountSettingsButton,
    on: function (name, fn) { (listeners[name] = listeners[name] || []).push(fn); },
    _core: core, _store: { get: get, set: set },
  };
})(typeof window !== 'undefined' ? window : globalThis);
