// Browser check for an index.html that has arena-kit injected.
//   node arena-kit/browser_check.cjs <game dir> [cdn package dir]
// Serves the directory, loads the page in Chromium and exercises the kit UI. Prints JSON, exit 1 on failure.
// Needs the `playwright` package (resolved from the game's tools/node_modules or NODE_PATH).
const path = require('path');
const fs = require('fs');
const http = require('http');
const dir = path.resolve(process.argv[2]);
const cdn = process.argv[3];
const pw = require(require.resolve('playwright', { paths: [path.join(dir, 'tools'), dir, process.cwd()] }));

const srv = http.createServer((q, r) => {
  const f = path.join(dir, decodeURIComponent(new URL(q.url, 'http://x').pathname).replace(/^\/+/, '') || 'index.html');
  if (!f.startsWith(dir) || !fs.existsSync(f) || fs.statSync(f).isDirectory()) { r.writeHead(404).end(); return; }
  r.writeHead(200, { 'content-type': f.endsWith('.html') ? 'text/html' : 'application/octet-stream' }).end(fs.readFileSync(f));
});

(async () => {
  await new Promise((ok) => srv.listen(0, '127.0.0.1', ok));
  const base = `http://127.0.0.1:${srv.address().port}/index.html`;
  const b = await pw.chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const p = await b.newPage({ viewport: { width: 1280, height: 800 } });
  const errors = [];
  p.on('pageerror', (e) => errors.push('pageerror: ' + e.message));
  p.on('console', (m) => { if (m.type() === 'error') errors.push('console: ' + m.text()); });
  await p.route(/zgo\.at|fonts\.(googleapis|gstatic)/, (r) => r.fulfill({ status: 200, contentType: r.request().resourceType() === 'stylesheet' ? 'text/css' : 'text/javascript', body: '' }));
  if (cdn) await p.route(/cdn\.jsdelivr\.net\/npm\/three@0\.170\.0\//, (r) => r.fulfill({ status: 200, contentType: 'text/javascript', headers: { 'access-control-allow-origin': '*' }, body: fs.readFileSync(path.join(cdn, r.request().url().split('three@0.170.0/')[1])) }));
  await p.goto(base + '?d=20261109', { waitUntil: 'load' });
  await p.waitForFunction(() => [...document.querySelectorAll('canvas')].some((c) => c.width * c.height > 100000), null, { timeout: 30000 }).catch(() => errors.push('no canvas'));
  const r = await p.evaluate(async () => {
    const A = window.Arena, out = {};
    out.version = A && A.version;
    out.plays = A.profile().plays[A.game] || 0;
    out.hintFirst = A.hint('test', 'hello'); out.hintSecond = A.hint('test', 'hello');
    const d = A.daily(); out.day = d.day; out.streak = d.complete(10).streak; out.done = A.daily().done;
    let again = 0; A.endCard({ title: 'T', reason: 'R', lines: ['1'], onAgain: () => { again++; } });
    out.cardShown = !!document.querySelector('.arena-card');
    document.querySelector('.arena-card .arena-primary').click(); out.again = again; out.cardClosed = !document.querySelector('.arena-card');
    A.mountSettingsButton(); document.querySelector('.arena-gear').click();
    const boxes = document.querySelectorAll('.arena-card input[type=checkbox]'); boxes[0].click(); // high contrast
    out.contrast = document.documentElement.hasAttribute('data-arena-contrast');
    document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' })); out.settingsClosed = !document.querySelector('.arena-card');
    boxes[0].click && (A.settings.highContrast = false);
    let ratios = []; const fake = { setPixelRatio: (x) => ratios.push(x) };
    const h = A.perf.attach(fake); await new Promise((r) => setTimeout(r, 1500)); h.stop();
    out.perfFrames = h.state.n; out.perfRatio = h.state.ratio;
    return out;
  });
  const reload = await (async () => { await p.reload({ waitUntil: 'load' }); return p.evaluate(() => window.Arena.profile().plays[window.Arena.game]); })();
  r.playsAfterReload = reload;
  r.errors = errors;
  const ok = r.version && r.hintFirst === true && r.hintSecond === false && r.streak === 1 && r.done && r.cardShown && r.again === 1 &&
    r.cardClosed && r.contrast && r.settingsClosed && r.perfFrames > 10 && reload === r.plays + 1 && errors.length === 0;
  console.log(JSON.stringify({ ok, ...r }, null, 1));
  await b.close(); srv.close();
  process.exit(ok ? 0 : 1);
})();
