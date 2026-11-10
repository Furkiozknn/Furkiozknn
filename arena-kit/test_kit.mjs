// Node tests for the pure parts of arena-kit/kit.js (no DOM, no dependencies).
//   node --test arena-kit/test_kit.mjs
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import vm from 'node:vm';

function load(extra = {}) {
  const ctx = vm.createContext({ Math, Date, JSON, Object, String, Number, Promise, setTimeout, clearTimeout, ...extra });
  vm.runInContext(readFileSync(new URL('./kit.js', import.meta.url), 'utf8'), ctx);
  return ctx.Arena;
}
const A = load();
const C = A._core;

test('dayKey is UTC and prevDayKey crosses month and year', () => {
  assert.equal(C.dayKey(new Date(Date.UTC(2026, 10, 9, 23, 59))), 20261109);
  assert.equal(C.prevDayKey(20261101), 20261031);
  assert.equal(C.prevDayKey(20260101), 20251231);
  assert.equal(C.prevDayKey(20240301), 20240229); // leap year
});

test('mulberry32 is deterministic and in [0,1)', () => {
  const a = C.mulberry32(42), b = C.mulberry32(42);
  for (let i = 0; i < 1000; i++) { const x = a(); assert.equal(x, b()); assert.ok(x >= 0 && x < 1); }
  assert.notEqual(C.mulberry32(1)(), C.mulberry32(2)());
});

test('hash differs per game and day (daily seeds are not shared)', () => {
  assert.notEqual(C.hash('hamsi:20261109'), C.hash('dolmus:20261109'));
  assert.notEqual(C.hash('hamsi:20261109'), C.hash('hamsi:20261110'));
  assert.equal(C.hash('x'), C.hash('x'));
});

test('streak: same day keeps, next day +1, gap resets, best kept', () => {
  let r = C.nextStreak(null, 20261109);
  assert.deepEqual([r.streak, r.best], [1, 1]);
  r = C.nextStreak(r, 20261109); assert.equal(r.streak, 1);
  r = C.nextStreak(r, 20261110); assert.equal(r.streak, 2);
  r = C.nextStreak(r, 20261111); assert.equal(r.streak, 3);
  r = C.nextStreak(r, 20261114); assert.deepEqual([r.streak, r.best], [1, 3]);
});

test('perf controller lowers the ratio on slow frames and raises it on fast ones', () => {
  const p = C.perfController({ min: 0.6, max: 2, start: 2 });
  let now = 0;
  for (let i = 0; i < 400; i++) { now += 33; p.feed(33, now); } // 30 fps
  assert.ok(p.ratio < 2, `ratio dropped: ${p.ratio}`);
  assert.ok(p.ratio >= 0.6);
  const low = p.ratio;
  for (let i = 0; i < 2000; i++) { now += 8; p.feed(8, now); } // 120 fps
  assert.ok(p.ratio > low, `ratio recovered: ${p.ratio}`);
  assert.ok(p.ratio <= 2);
});

test('perf controller ignores tab-switch spikes and stays at min/max bounds', () => {
  const p = C.perfController({ min: 0.75, max: 1.5, start: 1.5 });
  let now = 0;
  for (let i = 0; i < 100; i++) { now += 16; p.feed(i % 10 ? 16 : 5000, now); }
  assert.equal(p.ratio, 1.5);
  for (let i = 0; i < 5000; i++) { now += 50; p.feed(50, now); }
  assert.equal(p.ratio, 0.75);
});

test('shareText joins title, lines and url', () => {
  assert.equal(C.shareText({ title: 'Hamsi', lines: ['Gün 3', '🐟 1200'], url: 'https://x/' }), 'Hamsi\nGün 3\n🐟 1200\nhttps://x/');
});

test('without DOM or storage the API still works (memory fallback)', () => {
  assert.equal(A.version, '1.1.0');
  assert.equal(A.award('b1'), true);
  assert.equal(A.award('b1'), false);
  assert.ok(A.profile().badges.b1);
  const d = A.daily('hamsi');
  assert.equal(typeof d.rng(), 'number');
  const r = d.complete(50);
  assert.equal(r.streak, 1);
  assert.equal(A.daily('hamsi').done, true);
});

test('a second injection keeps the first instance', () => {
  const ctx = vm.createContext({ Math, Date, JSON, Object, String, Number, Promise, setTimeout, clearTimeout });
  const src = readFileSync(new URL('./kit.js', import.meta.url), 'utf8');
  vm.runInContext(src, ctx); const first = ctx.Arena;
  vm.runInContext(src, ctx);
  assert.equal(ctx.Arena, first);
});

test('v1.0.1: localDayKey uses local time; isQuiet matches bot/demo/no-save flags only', () => {
  const d = new Date(2026, 10, 9, 1, 30); // local 01:30
  assert.equal(C.localDayKey(d), 20261109);
  for (const q of ['?auto', '?auto=1', '?x=1&nosave', '?demo=b', '?auto&mode=quick']) assert.equal(C.isQuiet(q), true, q);
  for (const q of ['', '?d=20261109', '?autopilot=1', '?lang=tr', '?x=auto']) assert.equal(C.isQuiet(q), false, q);
});

test('v1.0.1: daily accepts the game\'s own day key; without DOM it is not quiet', () => {
  const B = load();
  const a = B.daily('fay-hatti', { dayKey: 20261109 }), b = B.daily('fay-hatti', { dayKey: 20261110 });
  assert.equal(a.day, 20261109); assert.equal(b.day, 20261110); assert.notEqual(a.seed, b.seed);
  assert.equal(B.daily('fay-hatti', { dayKey: 'bad' }).day, C.dayKey());
  assert.equal(B.quiet, false);
});

test('v1.0.1: quiet page (?auto) never touches localStorage', () => {
  const writes = [];
  const ls = { getItem: () => null, setItem: (k, v) => writes.push(k), removeItem: () => {} };
  const doc = { readyState: 'complete', addEventListener() {}, documentElement: { lang: 'tr', style: { setProperty() {} }, toggleAttribute() {} },
    querySelector: () => null, head: { appendChild() {} }, body: { appendChild() {} }, createElement: () => ({ setAttribute() {}, appendChild() {}, addEventListener() {}, classList: { add() {}, remove() {} } }) };
  const Q = load({ document: doc, localStorage: ls, location: { search: '?auto', pathname: '/hamsi/' }, navigator: {}, matchMedia: () => ({ matches: false }), requestAnimationFrame() {} });
  assert.equal(Q.quiet, true);
  Q.award('x'); Q.daily('hamsi').complete(5);
  assert.deepEqual(writes, []);
});

// ---- v1.1: play events + feedback (handed to the page's own GoatCounter) ----
function fakePage(search, store = {}) {
  const listeners = {}, appended = [], counted = [];
  const mk = (tag) => {
    const e = { tag, attrs: {}, kids: [], textContent: '', parentNode: null, _l: {},
      setAttribute(k, v) { this.attrs[k] = v; }, appendChild(c) { c.parentNode = this; this.kids.push(c); },
      removeChild(c) { this.kids = this.kids.filter((k) => k !== c); c.parentNode = null; },
      remove() { if (this.parentNode) this.parentNode.removeChild(this); },
      addEventListener(n, f) { this._l[n] = f; }, classList: { add() {}, remove() {} } };
    return e;
  };
  const body = mk('body');
  const doc = { readyState: 'complete', body, head: mk('head'), createElement: mk,
    addEventListener(n, f) { (listeners[n] = listeners[n] || []).push(f); },
    removeEventListener(n, f) { listeners[n] = (listeners[n] || []).filter((x) => x !== f); },
    documentElement: { lang: 'tr', style: { setProperty() {} }, toggleAttribute() {} }, querySelector: () => null };
  const ls = { getItem: (k) => (k in store ? store[k] : null), setItem: (k, v) => { store[k] = v; }, removeItem: (k) => { delete store[k]; } };
  const gc = { count: (o) => counted.push(o) };
  const A = load({ document: doc, localStorage: ls, location: { search, pathname: '/dolmus/' }, navigator: {},
    matchMedia: () => ({ matches: false }), requestAnimationFrame() {}, goatcounter: gc });
  const fire = (n, isTrusted = true) => (listeners[n] || []).slice().forEach((f) => f({ isTrusted }));
  return { A, body, counted, store, fire };
}

test('v1.1: isReturn — earlier day of this game, or (old profile) any earlier play', () => {
  assert.equal(C.isReturn(20261109, 3, 0, 20261110), true);
  assert.equal(C.isReturn(20261110, 3, 0, 20261110), false);
  assert.equal(C.isReturn(undefined, 0, 0, 20261110), false);
  assert.equal(C.isReturn(undefined, 2, Date.UTC(2026, 10, 8), 20261110), true);
  assert.equal(C.isReturn(undefined, 2, Date.UTC(2026, 10, 10, 5), 20261110), false);
  assert.equal(C.eventName('Like!'), 'like');
});

test('v1.1: first real input sends <game>/start once; synthetic events do not', () => {
  const p = fakePage('');
  p.fire('pointerdown', false); assert.equal(p.counted.length, 0);
  p.fire('pointerdown'); p.fire('keydown');
  assert.deepEqual(p.counted.map((o) => [o.path, o.event]), [['dolmus/start', true]]);
});

test('v1.1: returning player (played on an earlier day) also sends <game>/return', () => {
  const p = fakePage('', { 'arena.profile.v1': JSON.stringify({ plays: { dolmus: 2 }, badges: {}, lastDay: { dolmus: 20200101 }, last: null, first: 1 }) });
  p.fire('touchstart');
  assert.deepEqual(p.counted.map((o) => o.path), ['dolmus/start', 'dolmus/return']);
  assert.equal(JSON.parse(p.store['arena.profile.v1']).lastDay.dolmus, C.dayKey());
});

test('v1.1: complete() counts once and shows 👍/👎 once a day; a vote is counted and remembered', () => {
  const p = fakePage('');
  p.A.complete(); p.A.complete();
  assert.deepEqual(p.counted.map((o) => o.path), ['dolmus/complete']);
  const panel = p.body.kids.find((k) => k.attrs.class === 'arena-fb');
  assert.ok(panel, 'feedback panel shown');
  const up = panel.kids.find((k) => k.textContent === '👍');
  up._l.click();
  assert.deepEqual(p.counted.map((o) => o.path), ['dolmus/complete', 'dolmus/like']);
  assert.equal(JSON.parse(p.store['arena.feedback.v1']).dolmus, C.dayKey());
  const again = fakePage('', p.store); again.A.complete();
  assert.equal(again.body.kids.filter((k) => k.attrs.class === 'arena-fb').length, 0, 'not asked twice a day');
});

test('v1.1: quiet runs (?auto) send nothing and show nothing', () => {
  const p = fakePage('?auto');
  p.fire('pointerdown'); p.A.complete(); p.A.track('x');
  assert.equal(p.counted.length, 0);
  assert.equal(p.body.kids.length, 0);
});

test('v1.1: complete({mount}) puts the row inline in the game\'s end screen', () => {
  const p = fakePage('');
  const mount = { kids: [], appendChild(c) { c.parentNode = this; this.kids.push(c); }, removeChild(c) { this.kids = this.kids.filter((k) => k !== c); } };
  p.A.complete({ mount });
  assert.equal(mount.kids.length, 1);
  assert.equal(mount.kids[0].attrs.class, 'arena-fb arena-fb-inline');
  assert.equal(p.body.kids.filter((k) => /arena-fb/.test(k.attrs.class || '')).length, 0);
});
