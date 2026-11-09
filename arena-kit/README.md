# arena-kit

Shared layer for the 21 Claude Game Arena games. `kit.js` is copied **inline** into each game's
`index.html` by `inject.py`, so every game stays a single file and works offline. A game that never
calls `Arena.*` behaves exactly as before; the kit only adds a global `Arena`, one `<style>` tag and,
if the game mounts it, an accessibility button.

| API | What it does |
|---|---|
| `Arena.perf.attach(renderer)` | Dynamic pixel ratio for weak GPUs: drops to as low as 0.6× when frames average over 22 ms, climbs back when under 14 ms. |
| `Arena.hint(id, text)` | One-time hint toast (also announced to screen readers). |
| `Arena.endCard({title, reason, lines, onAgain, share})` | End-of-session card: reason, score lines, **again**, optional share, "try another game". |
| `Arena.daily(game, {dayKey})` | UTC-day seed (`?d=YYYYMMDD` to replay a day), `rng()`, `complete(score)` → streak. A game whose own daily turns at local midnight passes `{dayKey: Arena._core.localDayKey()}` so the streak follows the same day (v1.0.1). |
| `Arena.share({...})` / `Arena.shareCard({...})` | Web Share or clipboard text; 1080×1350 PNG card. |
| `Arena.profile()`, `Arena.award(id)` | Cross-game passport: plays per game, badges (games share one origin). |
| `Arena.settings`, `Arena.openSettings()`, `Arena.mountSettingsButton()`, `Arena.on('pause'|'resume'|'settings', fn)` | Accessibility: text size, high contrast, reduced motion, vibration on/off, pause when the tab is hidden. |

On `?auto`, `?nosave` or `?demo` (`Arena.quiet === true`, v1.0.1) the kit writes nothing to localStorage: bot and demo runs never touch the player's profile, streaks or settings.

Storage keys all start with `arena.` and carry a version (`profile.v1`, `daily.v1`, …); every access
is wrapped in try/catch and falls back to memory.

## Use

```bash
python3 arena-kit/inject.py ../hamsi           # insert or refresh the block before <script type="importmap">
python3 arena-kit/inject.py --kontrol ../hamsi # exit 1 if missing or stale
python3 schema/degisim.py --kok ../hamsi --taban origin/main --dosya index.html   # first run: additions only
```

Integration in a game is a few lines inside its own code, e.g. `Arena.perf.attach(renderer)` after the
renderer is created, `Arena.endCard({...})` on game over. Do not inject into a game while it still
has pending bot jobs: the relay edits the same `index.html`.

## Tests

```bash
node --test arena-kit/test_kit.mjs        # pure logic: seeds, streak, perf controller, fallbacks
python3 arena-kit/test_inject.py          # insert / refresh / no-op / errors / CLI exit codes
node arena-kit/browser_check.cjs <game>   # injected game in Chromium: every kit feature, 0 page errors
```

Measured on pamukkale (2026-11-09): degisim PASS (additions only), browser_check ok with 0 errors,
the game's own smoke test (SRI + load + tamper) still RESULT OK.
