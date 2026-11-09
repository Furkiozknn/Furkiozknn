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
  assert.equal(A.version, '1.0.0');
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
