# How this account is put together

The profile, the 28 public repositories and the directory site are one
system. This page is the design of that system: what goes where, why, and
which parts are generated so that nobody has to keep them in sync by hand.

## The visitor's path

A stranger should never have to ask *what is this*, *where do I click*,
or *is this current*. The profile answers in that order:

| Section | Question it answers | Source |
|---|---|---|
| Hero (`assets/hero*.svg`) | Whose page, what kind of work, how much of it (repositories and tests; no commit count) | hand-drawn; numbers rewritten by `schema/testler.py` |
| Intro, **Currently**, link line | What I build, what I am doing this week, where everything else lives | hand-written; three sentences, one status line, one `<samp>` line |
| **Featured** | Which four are finished and worth a first look | selection rule below |
| **More** | Everything else, one line each, by area; ▸ marks what plays in the browser | hand-written, checked against the catalogue |
| **Recently** | Is the account alive | `schema/vitrin.py`, daily: `yazilar/` + latest releases |
| **Every project** (collapsed) | All public repositories, with test counts | table; counts rewritten by `schema/testler.py` |
| Closing line + **Work with me** | Why the numbers can be trusted; what can be hired | hand-written; details in `HIRE.md` |

The page is kept short on purpose. The strongest individual profiles on
GitHub (karpathy, charliermarsh, tiangolo, antfu, simonw) say what they build
in a sentence or two and let the pinned repositories carry the rest; none of
them shows stat cards, trophies or a commit count. The long material here -
the full table, the ledger, the hiring terms - sits one click away.

Anything that can go stale is generated or checked in CI. The rest is
short enough to reread when it changes.

## Pins and sidebar (set by hand on github.com)

GitHub has no API for pinned repositories or the profile bio, so this part
is a checklist, not a script. Pins do more work than the README: a visitor
sees them first, and every strong profile keeps them to six on-theme repos
with one-line descriptions short enough not to be cut off (`about/uygula.py`
now holds every description to 100 characters for that reason).

| Pin | Why this one |
|---|---|
| mcp-vet | the flagship; audits before install |
| godot-refcheck | checked against 237 real Godot projects |
| repo-vet | calibrated on 29 public repositories |
| claude-code-intelligence | the tool with the widest audience here |
| buradane | the one full-stack app, with a demo GIF |
| nova-drift | plays in the browser in one click |

- **Bio** (160 characters at most): *I build what AI agents run on, and the
  tools that check it works. MCP, Python, Godot. Türkiye, UTC+3.*
- **Website field:** `https://furkiozknn.github.io/`
- **Status:** what is being finished right now, matching the README's
  *Currently* line (today: mcp-vet 0.6.0).
- **Social preview:** upload `assets/social/<repo>.png` under each pinned
  repository's Settings → Social preview.

## Areas

Every repository belongs to exactly one area. The area decides its place
on the profile and the accent colour of its social card.

| Area | Accent | Repositories |
|---|---|---|
| Tools that check other work | `#58a6ff` | mcp-vet, godot-refcheck, repo-vet, claude-code-intelligence, mcp-census, repo-ratchet, Furkiozknn.github.io |
| Agent infrastructure | `#e3b341` | ai-job-gateway, ai-workflow-engine, model-comparison-harness, prompt-template-manager, asset-provenance-toolkit |
| MCP servers | `#3fb950` | mini-creative-toolkit, local-notes-search-mcp, voice-io-mcp, nvidia-nim-mcp |
| Apps | `#39c5cf` | buradane, ajans-os, turkce-ajanlar, masal |
| Games | `#db61a2` | nova-drift, tek-tus-kosu, yercekimi-cevir, derin-kazi, kanca, godot-2d-sablon |

`claude-quota-monitor` is archived; `claude-code-intelligence` replaced it.

## Featured: the selection rule

A repository is featured only if **all** of these hold, checked when the
list changes:

1. **Finished for its stated scope.** No "coming soon" in the README.
2. **Documented.** Quick start, usage, and known limits.
3. **Tested in CI.** A suite whose count is in `TESTLER.md`.
4. **Shown, not described.** A demo GIF recorded from real output.
5. **Useful to a stranger today.** It solves a problem someone other than
   the author has.

Today: mcp-vet, godot-refcheck, buradane, repo-vet. Stars and recency are
not criteria: the list should be the same whether or not anyone is
watching.

## README standard

Scale the README to the project. A single-purpose tool gets the short
form; a flagship gets the full one. Never add an empty section.

| Order | Section | Short form | Full form |
|---:|---|:--:|:--:|
| 1 | Hero image or demo GIF, then one sentence of what it does | ✓ | ✓ |
| 2 | Quick start: install and the first command, copy-pasteable | ✓ | ✓ |
| 3 | Usage and one real example output | ✓ | ✓ |
| 4 | What it checks / how it works | | ✓ |
| 5 | Configuration | | ✓ |
| 6 | Known limits, stated plainly | ✓ | ✓ |
| 7 | Development and testing: the command, and the count it prints | ✓ | ✓ |
| 8 | Releases and changelog link | | ✓ |
| 9 | Related repositories on this account | ✓ | ✓ |
| 10 | Licence | ✓ | ✓ |

Games replace 2–3 with: a play link (or download), controls, and a
gameplay capture. A Turkish-first project opens with a folded English
summary.

## Writing

Short sentences. Say what it does, then show it. No *powerful*,
*revolutionary*, *next-generation*. A number is either re-derivable from a
run or it is not written down.

## Visual system

- **Background** `#0f1117`, **text** `#f2efe6` / `#ece8de`, **muted** `#9ba3ae`,
  **label** `#d4a95c`.
- **Type:** monospace for names and code (DejaVu Sans Mono), serif for the
  one-sentence claim (DejaVu Serif), sans for everything else. GitHub
  strips web fonts from SVG, so assets use fonts every machine has.
- **Accent** comes from the area, never from the project.
- **Light and dark:** the hero ships in both (`<picture>` with
  `prefers-color-scheme`); diagrams are drawn to read on either.
- **Sizes:** social cards 1280×640; profile GIFs under 400 KB each; no
  image is decoration only, every one has alt text that says what it
  shows.

### Asset names

| Asset | Path | Made by |
|---|---|---|
| Profile hero | `assets/hero.svg`, `assets/hero-light.svg` | hand; numbers by `schema/testler.py` |
| Ecosystem diagram | `assets/ecosystem.svg` | hand |
| Social card, per repository | `assets/social/<repo>.png` | `assets/social/kart.py` from `kartlar.json` |
| Demo GIF, per repository | `<repo>/assets/demo.gif` | recorded from real output in that repository |
| Article images | `yazilar/<slug>/…` | with the article |

## What is generated, and from where

| Output | Generator | Input | When |
|---|---|---|---|
| `project-meta.json` in every repository | `schema/uret.py` | clone + API + `schema/meta-source.json` | weekly |
| Directory site | Furkiozknn.github.io | every `project-meta.json` | on change |
| Test counts on the profile | `schema/testler.py` | `schema/meta-source.json` | on change; checked in CI |
| Recently | `schema/vitrin.py` | `yazilar/` + GitHub releases | daily; checked in CI |
| Repository descriptions and homepages | `about/uygula.py` | `about/about.json` | by hand, with `gh`; checked in CI |
| Social cards | `assets/social/kart.py` | `assets/social/kartlar.json` | by hand; uploaded by hand |
| Daily health audit | `schema/denetim.py` | every repository | daily |

## What only the account owner can do

GitHub gives no API, or no API a session token may use, for these:

- merging pull requests and approving workflow runs from forks,
- pushing release tags,
- enabling GitHub Pages on a repository,
- writing repository settings (description, homepage) — run
  `python3 about/uygula.py --uygula` once with `gh`,
- uploading social preview images.

## README banners

Every repository except nova-drift (its own game logo) and turkce-ajanlar
(whose banner is generated from the live agent count by its own tested
script) uses one banner template: `assets/banner/banner.py` renders
`assets/banner/banners.json` into `assets/banner/out/<repo>.svg`, which is
copied to the repository's existing banner path.

- 1280×320 SVG, system fonts only, no external requests.
- Area colour from the same table as the social cards.
- Left: area label, name, a one- or two-line pitch, up to three chips.
- Right: five fact rows, each a verifiable property of the code.
- **No counts.** No test numbers, versions or totals: those drift, and a
  banner that cannot drift is the point. `--kontrol` rejects a count.
- Long names are fitted with `textLength`, so they never cross the divider
  whatever font the viewer has.
