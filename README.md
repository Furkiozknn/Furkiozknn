<img src="assets/hero.svg" alt="Furki Özkan — agent systems, MCP and developer tooling. 28 public repositories, 5,226 tests, 1,089 commits." width="100%">

<p align="center">
  <a href="TESTLER.md"><img src="https://img.shields.io/badge/tests-5%2C226_passing-c9a961?style=for-the-badge&labelColor=0b0b0f" alt="5,226 tests passing"></a>
  <a href="TESTLER.md"><img src="https://img.shields.io/badge/every_number-traced_to_its_run-e7dcc0?style=for-the-badge&labelColor=0b0b0f" alt="Every number traced to the run that printed it"></a>
  <a href="https://github.com/Furkiozknn?tab=repositories"><img src="https://img.shields.io/badge/public_repos-28-c9a961?style=for-the-badge&labelColor=0b0b0f" alt="28 public repositories"></a>
  <a href="HIRE.md"><img src="https://img.shields.io/badge/available-for_contract_work-2ea043?style=for-the-badge&labelColor=0b0b0f" alt="Available for contract work"></a>
</p>

<p align="center">
  <b>I build the infrastructure AI agents run on</b> — async job contracts, pipeline DAGs, MCP servers —<br>
  <b>and the tooling that checks whether any of it actually works.</b><br>
  <sub>Some evenings, a game engine instead.</sub>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-0b0b0f?style=flat-square&logo=python&logoColor=c9a961">
  <img src="https://img.shields.io/badge/TypeScript-0b0b0f?style=flat-square&logo=typescript&logoColor=c9a961">
  <img src="https://img.shields.io/badge/FastAPI-0b0b0f?style=flat-square&logo=fastapi&logoColor=c9a961">
  <img src="https://img.shields.io/badge/PostGIS-0b0b0f?style=flat-square&logo=postgresql&logoColor=c9a961">
  <img src="https://img.shields.io/badge/Next.js-0b0b0f?style=flat-square&logo=nextdotjs&logoColor=c9a961">
  <img src="https://img.shields.io/badge/Three.js-0b0b0f?style=flat-square&logo=threedotjs&logoColor=c9a961">
  <img src="https://img.shields.io/badge/Godot-0b0b0f?style=flat-square&logo=godotengine&logoColor=c9a961">
  <img src="https://img.shields.io/badge/MCP-0b0b0f?style=flat-square&logo=anthropic&logoColor=c9a961">
  <img src="https://img.shields.io/badge/OpenTelemetry-0b0b0f?style=flat-square&logo=opentelemetry&logoColor=c9a961">
  <img src="https://img.shields.io/badge/Playwright-0b0b0f?style=flat-square&logo=playwright&logoColor=c9a961">
</p>

---

## ▸ No install, no signup — just click

<table>
<tr>
<td width="34%" valign="top">

### 🚀 [nova-drift →](https://furkiozknn.github.io/nova-drift/)

An endless browser space-runner with **real bloom post-processing**, fully
synthesized audio and a seeded daily run everyone plays the same.
**0.7 MB first load. No build step.** It is flying before you finish reading this.

</td>
<td width="33%" valign="top">

### 📖 [masal →](https://furkiozknn.github.io/masal/)

A bedtime story written around **one child's name, age and hometown**, with the
colouring page drawn into the page itself. A Turkish suffix engine gets the name
right where template substitution never could — *Sinop* takes `-ta`, *Trabzon* takes `-da`.

</td>
<td width="33%" valign="top">

### 🇹🇷 [turkce-ajanlar →](https://furkiozknn.github.io/turkce-ajanlar/)

All **70** Claude Code sub-agents, searchable in the browser before you install anything. `/` jumps to the search box, `Enter` opens the first hit. Taking one means copying **one markdown file** into `.claude/agents/`.

</td>
</tr>
</table>

<p align="center">
  <a href="https://github.com/Furkiozknn/buradane">
    <img src="https://raw.githubusercontent.com/Furkiozknn/buradane/main/assets/demo.gif" alt="buradane: picking categories on a map of Istanbul, then typing free text and watching the results narrow to 19" width="760">
  </a>
</p>

<p align="center"><sub><b>A real session, captured by a script committed in that repo.</b> Typing “ücretsiz tuvalet” takes <b>167,829 places</b> down to the 19 nearest free toilets.</sub></p>

---

## ▸ This is one system, not twenty-seven side projects

![How the repositories hold each other up: a layer of tools that check other work, a generation pipeline of four repositories around one HTTP job contract, the MCP servers, the games and web apps, and project-meta.json in every repository with a daily audit underneath](assets/ecosystem.svg)

<p align="center"><b><a href="https://furkiozknn.github.io/">Every repository, searchable, in one page →</a></b><br>
<sub>Generated from the <code>project-meta.json</code> each one carries, rebuilt weekly. Nothing on it is hand-written.</sub></p>

<sub>Four repositories share one job contract and no Python dependency. Four more exist to check work — a repository's README, an MCP server's source, a Godot project's references, a Claude Code session's token spend — and each was calibrated against real outside projects before it was published. Underneath all of them, one metadata schema and one audit that runs every morning.</sub>

---

## ▸ Start here

> 🛡️ **[mcp-vet](https://github.com/Furkiozknn/mcp-vet)** — audits an MCP server *before* you install it. Every claim carries a file and a line, it reads the code rather than the star count, and **it never executes what it audits**. Standard library only, zero dependencies. <sub>`319 tests`</sub>
>
> 🧩 **[godot-refcheck](https://github.com/Furkiozknn/godot-refcheck)** — Godot names a broken reference only when that scene loads, and a dead signal connection never. This finds both without opening the editor, and **repairs the ones with a single provable answer**. Checked against **237 real Godot projects** and against a headless engine. <sub>`133 tests`</sub>
>
> 🔎 **[repo-vet](https://github.com/Furkiozknn/repo-vet)** — your README is a promise: it tries the install command, the badges, the links and the release chain over the GitHub API, without cloning. Calibrated on **30 public repositories** so it stays quiet on the ones that work. <sub>`103 tests`</sub>
>
> 🗺️ **[buradane](https://github.com/Furkiozknn/buradane)** — *"what do I need, and where is the nearest one?"* **167,829 real OpenStreetMap places** across all 81 provinces of Türkiye, on FastAPI + PostGIS with a Next.js/MapLibre front end. <sub>`347 tests`</sub>
>
> 📊 **[claude-code-intelligence](https://github.com/Furkiozknn/claude-code-intelligence)** — where the tokens went, what it cost, and when the quota resets. An OTLP receiver and transcript parser that **never phones home**. <sub>`273 tests`</sub>

<p align="center">
  <a href="https://github.com/Furkiozknn/godot-refcheck">
    <img src="https://raw.githubusercontent.com/Furkiozknn/godot-refcheck/main/assets/demo.gif" alt="godot-refcheck finding three broken references in a Godot project, repairing them with --fix, and finding nothing on the next run" width="760">
  </a>
</p>

<p align="center"><sub><b>A real run, on a fixture committed in that repository.</b> Three references broken by a moved folder, three repairs, then a clean pass — and a headless Godot agrees before and after.</sub></p>

---

## ▸ Everything, in one table

<sub>Every test count below is traced to the suite run that printed it. **[The full ledger →](TESTLER.md)**</sub>

### Agent infrastructure, MCP and developer tooling

| | Project | What it does | Tests |
|:--:|---|---|---:|
| 🧩 | **[godot-refcheck](https://github.com/Furkiozknn/godot-refcheck)** | Godot names a broken reference only when that scene loads, and a dead signal connection never. Finds both, and repairs what has one provable answer. | `133` |
| 🔎 | **[repo-vet](https://github.com/Furkiozknn/repo-vet)** | Your README is a promise: it tries the install command, the badges, the links and the tags, over the API, without cloning. | `103` |
| 🛡️ | **[mcp-vet](https://github.com/Furkiozknn/mcp-vet)** | Reads an MCP server's source before you install it. 31 rules, `file:line` on every finding, never runs what it audits. | `319` |
| 🗺️ | **[buradane](https://github.com/Furkiozknn/buradane)** | The nearest toilet, park, fountain or library. 167,829 OSM places; all 973 district centres covered within 15 km. | `347` |
| 📊 | **[claude-code-intelligence](https://github.com/Furkiozknn/claude-code-intelligence)** | Where the tokens went and when the limit resets. No prompt or file content exists in any type — a privacy review is a `grep`. | `273` |
| 🎨 | **[mini-creative-toolkit](https://github.com/Furkiozknn/mini-creative-toolkit)** | 23 CPU-first media tools in one MCP server. 22 report `"network": "none"` in their own payload, not in a README. | `327` |
| 🏛️ | **[ajans-os](https://github.com/Furkiozknn/ajans-os)** | An agency OS built research-first. Its acceptance run is killed mid-task, reloaded from disk and resumed. | `142` |
| 📚 | **[masal](https://github.com/Furkiozknn/masal)** | A bedtime story around one child's name. Six themes, a branch on page three — twelve readings. | `92` |
| 🇹🇷 | **[turkce-ajanlar](https://github.com/Furkiozknn/turkce-ajanlar)** | **70** Claude Code sub-agents that *think* in Turkish, not translate into it. Exported to Cursor, OpenCode, Copilot, Codex. | `160` |
| 🔁 | **[repo-ratchet](https://github.com/Furkiozknn/repo-ratchet)** | Decides which repository to open next from twelve measured signals — and will not record an improvement that left no commit and no passing check. | `131` |
| 🔖 | **[asset-provenance-toolkit](https://github.com/Furkiozknn/asset-provenance-toolkit)** | Which model made this file, written **into** the file. JPEG gets a marker spliced in with no re-encoding. | `125` |
| ⚡ | **[nvidia-nim-mcp](https://github.com/Furkiozknn/nvidia-nim-mcp)** | NVIDIA NIM's free tier in Claude Code. Two of its seven tools need no API key at all. | `80` |
| ⚖️ | **[model-comparison-harness](https://github.com/Furkiozknn/model-comparison-harness)** | One prompt, N providers, one report — plus a judge model scoring each answer against your own rubric. | `74` |
| 🔗 | **[ai-workflow-engine](https://github.com/Furkiozknn/ai-workflow-engine)** | Pipelines as YAML DAGs, validated *before* they run. An undeclared dependency is rejected at load time, typo and all. | `80` |
| ✍️ | **[prompt-template-manager](https://github.com/Furkiozknn/prompt-template-manager)** | Prompts versioned in git, so a change is a diff instead of an argument. `StrictUndefined` throughout. | `61` |
| 🔍 | **[local-notes-search-mcp](https://github.com/Furkiozknn/local-notes-search-mcp)** | Ask your own files a question, in any language the multilingual model covers. No server, no API key, no network. | `64` |
| 🔢 | **[mcp-census](https://github.com/Furkiozknn/mcp-census)** | "How many MCP servers are there?" asked three ways, giving three different numbers — and a measurement of why. | `55` |
| 🎙️ | **[voice-io-mcp](https://github.com/Furkiozknn/voice-io-mcp)** | Speech in and out, needing no key at all. Refuses `transcribe the audio at .env` before it opens the file. | `35` |
| 🛰️ | **[ai-job-gateway](https://github.com/Furkiozknn/ai-job-gateway)** | The contract fal.ai, BFL and RunPod each reached independently. Idempotency across restarts, SSRF-guarded webhooks. | `156` |
| 🚀 | **[nova-drift](https://github.com/Furkiozknn/nova-drift)** | Endless browser space-runner. Real bloom, live-synthesized audio — not one sound file in the repo. | `38` |

### Games — Godot 4, each one tested headlessly in CI

<sub>These counts are large because the suites play the game: `yercekimi-cevir`'s 841 checks include finishing all 20 rooms and confirming a medal in each. Windows and web (HTML5) export presets ship in every repository; there is no hosted build yet.</sub>

| | Project | The one idea it is built on | Tests |
|:--:|---|---|---:|
| 🎵 | **[tek-tus-kosu](https://github.com/Furkiozknn/tek-tus-kosu)** | One button, and every obstacle laid on the music's beat grid. A post-run histogram shows how early or late each press landed. | `961` |
| 🔄 | **[yercekimi-cevir](https://github.com/Furkiozknn/yercekimi-cevir)** | There is no jump button — one key flips gravity and you fall onto the ceiling. 20 hand-built precision rooms. | `841` |
| ⛏️ | **[derin-kazi](https://github.com/Furkiozknn/derin-kazi)** | Dig, sell, upgrade, go deeper — with the fuel gauge as the real timer. Five layers down to the core at 250 m. | `477` |
| 🪝 | **[kanca](https://github.com/Furkiozknn/kanca)** | Hook the ceiling, swing, release at the right moment and carry the momentum. Medal times measured by a bot, not guessed. | `115` |
| | | **Total, across 25 repositories with suites** | **`5,226`** |

<sub>Also here: **[godot-2d-sablon](https://github.com/Furkiozknn/godot-2d-sablon)** — two Godot 4.7 starter projects whose jump feel was *measured*, not guessed (coyote time, jump buffering, variable jump height). No suite, so it is not in the count.</sub>

---

## ▸ Every repository carries its own metadata

Each one has a `project-meta.json` at its root: identity, version, status,
platform, the images its README actually shows, and the test count together
with the runner line it came from and the date of that run.

Mechanical fields are read from the repository; editorial fields are written
by hand and checked against the code. **Nothing is filled in with a guess** — an
unknown value is `null` rather than a plausible-looking string, and a test
count with no source line does not go in the file at all.

**[The schema and the rule it follows →](schema/README.md)**

---

## ▸ How I work

<table>
<tr><td width="33%" valign="top">

### 🧪 Tests before claims

Every count here is re-derived, not remembered. **This page has lost three numbers that way:** a “1,426 tests” figure that turned out to be a grep rather than a suite, a 1.4 MB load that measured 0.7 MB, and a commit count taken from clones that had not been fetched, undercounting by 53.

</td><td width="33%" valign="top">

### 🔒 Hermetic CI

Suites run offline, so a CDN outage cannot redden a build. **The gate is tested too** — `ajans-os` plants a deliberate violation in its own tree and fails if its own validator misses it.

</td><td width="33%" valign="top">

### 📄 Honest READMEs

Known limits are listed, not hidden: a measured seven-minute upscale stall on integrated graphics, a gateway column headed *deliberately absent*, voice cloning left out on purpose.

</td></tr>
<tr><td valign="top">

### ⚖️ Licences checked down the tree

`rembg`'s default model is **CC-BY-NC** — caught by reading the dependency tree, and refused unless you opt in knowingly. `buradane` splits ODbL data from MIT code in a `NOTICE` file.

</td><td valign="top">

### 🔧 Windows and Turkish locales

Where things break that nobody documents: `cp1254` killing a tool before it prints its first line, PowerShell 5.1 without `&&`, a heredoc quietly eating a backslash.

</td><td valign="top">

### 🔢 No generated stat cards

Every badge on this page carries a **hand-checked** value, traced to the run that printed it. A number is checkable, or it is not on the page. **[Check them →](TESTLER.md)**

</td></tr>
</table>

---

<div align="center">

## ▸ Available for remote contract work

**MCP and agent infrastructure** · **turning code that works into code that ships**<br>
Remote · Türkiye · European hours

### [→ What I can be hired for, and what it costs](HIRE.md)

<br>

<sub>
  <a href="https://furkiozknn.github.io/">Project directory</a> ·
  <a href="TESTLER.md">Where the 5,226 comes from</a> ·
  <a href="schema/README.md">project-meta.json</a> ·
  <a href="HIRE.md">Hire me</a> ·
  <a href="https://github.com/Furkiozknn?tab=repositories">All repositories</a> ·
  <a href="https://x.com/furkiozkan">@furkiozkan</a>
</sub>

</div>
