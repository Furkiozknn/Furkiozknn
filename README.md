<picture>
  <source media="(prefers-color-scheme: light)" srcset="assets/hero-light.svg">
  <img src="assets/hero.svg" alt="Furki Özkan — agent infrastructure, MCP and developer tooling. 28 public repositories, 5,247 tests." width="100%">
</picture>

I build the parts AI agents run on — MCP servers, a job contract, a pipeline engine — and then the tools that check whether any of it works. Each checker was tried on real outside projects before release. Independent, in Türkiye (UTC+3); some evenings, Godot.

**Currently:** finishing [mcp-vet 0.6.0](https://github.com/Furkiozknn/mcp-vet) and [godot-refcheck 0.3.0](https://github.com/Furkiozknn/godot-refcheck).

<samp>[directory](https://furkiozknn.github.io/) · [writing](yazilar/) · [all projects](#every-project) · [where the numbers come from](TESTLER.md) · [<b>hire me</b>](HIRE.md) · [x.com/furkiozkan](https://x.com/furkiozkan)</samp>

## Featured

<table>
<tr>
<td width="50%" valign="top">

**🛡️ [mcp-vet](https://github.com/Furkiozknn/mcp-vet)** — audits an MCP server *before* you install it. Reads the source, not the star count; every finding carries a `file:line`; it never executes what it audits. Zero dependencies.

<a href="https://github.com/Furkiozknn/mcp-vet"><img src="https://raw.githubusercontent.com/Furkiozknn/mcp-vet/master/assets/audit.gif" alt="mcp-vet auditing an MCP server and listing findings with file and line" width="100%"></a>

</td>
<td width="50%" valign="top">

**🧩 [godot-refcheck](https://github.com/Furkiozknn/godot-refcheck)** — finds the broken references and dead signal connections Godot only reports when a scene loads, or never. Repairs the ones with a single provable answer. Checked against 237 real projects.

<a href="https://github.com/Furkiozknn/godot-refcheck"><img src="https://raw.githubusercontent.com/Furkiozknn/godot-refcheck/main/assets/demo.gif" alt="godot-refcheck finding three broken references, repairing them with --fix, then passing clean" width="100%"></a>

</td>
</tr>
<tr>
<td width="50%" valign="top">

**🗺️ [buradane](https://github.com/Furkiozknn/buradane)** — *"what do I need, and where is the nearest one?"* 167,829 OpenStreetMap places across all 81 provinces of Türkiye. FastAPI + PostGIS, Next.js + MapLibre.

<a href="https://github.com/Furkiozknn/buradane"><img src="https://raw.githubusercontent.com/Furkiozknn/buradane/main/assets/demo.gif" alt="buradane: typing 'ücretsiz tuvalet' narrows 167,829 places on a map of Istanbul to the 19 nearest free toilets" width="100%"></a>

</td>
<td width="50%" valign="top">

**🔎 [repo-vet](https://github.com/Furkiozknn/repo-vet)** — your README is a promise. It tries the install command, the badges, the links and the release chain over the GitHub API, without cloning. Calibrated on 29 public repositories so it stays quiet on the ones that work.

<a href="https://github.com/Furkiozknn/repo-vet"><img src="https://raw.githubusercontent.com/Furkiozknn/repo-vet/main/assets/demo.gif" alt="repo-vet checking a repository's README claims over the GitHub API" width="100%"></a>

</td>
</tr>
</table>

## More

**Check other work** — [repo-vet](https://github.com/Furkiozknn/repo-vet): tries a README's install command, badges and links over the API · [claude-code-intelligence](https://github.com/Furkiozknn/claude-code-intelligence): where your Claude Code tokens went · [mcp-census](https://github.com/Furkiozknn/mcp-census): why the MCP Registry has three sizes · [repo-ratchet](https://github.com/Furkiozknn/repo-ratchet): picks the repository to open next

**Agent infrastructure** — [ai-job-gateway](https://github.com/Furkiozknn/ai-job-gateway): submit, poll, signed webhook, one contract · [ai-workflow-engine](https://github.com/Furkiozknn/ai-workflow-engine): YAML DAGs validated before they run · [model-comparison-harness](https://github.com/Furkiozknn/model-comparison-harness): one prompt, N providers, a judge · [prompt-template-manager](https://github.com/Furkiozknn/prompt-template-manager): prompts as diffs · [asset-provenance-toolkit](https://github.com/Furkiozknn/asset-provenance-toolkit): which model made this file, written into the file

**MCP servers for Claude Code** — [mini-creative-toolkit](https://github.com/Furkiozknn/mini-creative-toolkit): 23 CPU-first media tools · [local-notes-search-mcp](https://github.com/Furkiozknn/local-notes-search-mcp): ask your own notes · [voice-io-mcp](https://github.com/Furkiozknn/voice-io-mcp): speech in and out, no key · [nvidia-nim-mcp](https://github.com/Furkiozknn/nvidia-nim-mcp): NVIDIA's free tier, with fallbacks

**Apps** — [buradane](https://github.com/Furkiozknn/buradane): the nearest free toilet, park or fountain in Türkiye · [ajans-os](https://github.com/Furkiozknn/ajans-os): an agency OS that survives being killed mid-task · [turkce-ajanlar](https://furkiozknn.github.io/turkce-ajanlar/) ▸: 71 sub-agents that think in Turkish · [masal](https://furkiozknn.github.io/masal/) ▸: a bedtime story around one child's name

**Games**, each played headlessly in CI — [nova-drift](https://furkiozknn.github.io/nova-drift/) ▸: space-runner, 0.8 MB, no sound files · [tek-tus-kosu](https://github.com/Furkiozknn/tek-tus-kosu): one button, on the beat · [yercekimi-cevir](https://github.com/Furkiozknn/yercekimi-cevir): flip gravity · [derin-kazi](https://github.com/Furkiozknn/derin-kazi): dig to the core · [kanca](https://github.com/Furkiozknn/kanca): hook and swing · [godot-2d-sablon](https://github.com/Furkiozknn/godot-2d-sablon): a starter whose jump was measured

<sub>▸ plays in the browser, nothing to install. The Godot games have web builds; their pages go live with GitHub Pages.</sub>

## Recently

<!-- vitrin:bas -->

**Writing**

- [Fifty broken references in 237 Godot projects](yazilar/godot-demolarindaki-kirik-referanslar.md) — The official demos, material-maker and godot-open-rpg, checked without opening the editor. Most of what turned up, Godot never mentions. <sub>25 Sep 2026</sub>
- [Your README is a promise](yazilar/readme-bir-sozdur.md) — Checking the install commands, badges, links and releases of 29 well-known repositories over the GitHub API, without cloning anything. <sub>25 Sep 2026</sub>

<!-- vitrin:son -->

## Every project

<details>
<summary><b>Every public repository, with its test count</b> — 5,247 tests, each traced to the run that printed it</summary>

<br>

**Agent infrastructure and MCP**

| | Project | What it does | Tests |
|:--:|---|---|---:|
| 🛡️ | **[mcp-vet](https://github.com/Furkiozknn/mcp-vet)** | Reads an MCP server's source before you install it. 31 rules, `file:line` on every finding, never runs what it audits. | `319` |
| 🛰️ | **[ai-job-gateway](https://github.com/Furkiozknn/ai-job-gateway)** | The contract fal.ai, BFL and RunPod each reached independently. Idempotency across restarts, SSRF-guarded webhooks. | `156` |
| 🔗 | **[ai-workflow-engine](https://github.com/Furkiozknn/ai-workflow-engine)** | Pipelines as YAML DAGs, validated *before* they run. An undeclared dependency is rejected at load time. | `80` |
| ⚖️ | **[model-comparison-harness](https://github.com/Furkiozknn/model-comparison-harness)** | One prompt, N providers, one report — plus a judge model scoring each answer against your own rubric. | `74` |
| ✍️ | **[prompt-template-manager](https://github.com/Furkiozknn/prompt-template-manager)** | Prompts versioned in git, so a change is a diff instead of an argument. `StrictUndefined` throughout. | `61` |
| 🔖 | **[asset-provenance-toolkit](https://github.com/Furkiozknn/asset-provenance-toolkit)** | Which model made this file, written **into** the file. JPEG and MP4 get it spliced in with no re-encoding. | `125` |
| 🎨 | **[mini-creative-toolkit](https://github.com/Furkiozknn/mini-creative-toolkit)** | 23 CPU-first media tools in one MCP server. 20 never touch the network; remove_background fetches its weights once. | `327` |
| ⚡ | **[nvidia-nim-mcp](https://github.com/Furkiozknn/nvidia-nim-mcp)** | NVIDIA NIM's free tier in Claude Code. Two of its seven tools need no API key at all. | `80` |
| 🔍 | **[local-notes-search-mcp](https://github.com/Furkiozknn/local-notes-search-mcp)** | Ask your own files a question, in any language the multilingual model covers. No server, no key; offline after a one-time model download. | `64` |
| 🎙️ | **[voice-io-mcp](https://github.com/Furkiozknn/voice-io-mcp)** | Speech in and out, no key needed. Refuses `transcribe the audio at .env` before it opens the file. | `35` |
| 🔢 | **[mcp-census](https://github.com/Furkiozknn/mcp-census)** | "How many MCP servers are there?" asked three ways, giving three different numbers — and a measurement of why. | `55` |
| 🏛️ | **[ajans-os](https://github.com/Furkiozknn/ajans-os)** | An agency OS built research-first. Its acceptance run is killed mid-task, reloaded from disk and resumed. | `142` |
| 🇹🇷 | **[turkce-ajanlar](https://github.com/Furkiozknn/turkce-ajanlar)** | 71 Claude Code sub-agents that *think* in Turkish. Exported to Cursor, OpenCode, Copilot and Codex. | `160` |

**Developer tooling — tools that check other work**

| | Project | What it does | Tests |
|:--:|---|---|---:|
| 🧩 | **[godot-refcheck](https://github.com/Furkiozknn/godot-refcheck)** | Broken references and dead signal connections in Godot projects, found without the editor and repaired where the answer is provable. | `133` |
| 🔎 | **[repo-vet](https://github.com/Furkiozknn/repo-vet)** | Tries a README's install command, badges, links and tags over the API, without cloning. | `103` |
| 📊 | **[claude-code-intelligence](https://github.com/Furkiozknn/claude-code-intelligence)** | Where the tokens went and when the limit resets. No prompt or file content exists in any type — a privacy review is a `grep`. | `273` |
| 🔁 | **[repo-ratchet](https://github.com/Furkiozknn/repo-ratchet)** | Picks the repository to open next from twelve measured signals, and will not record an improvement that left no commit. | `131` |
| 🗂️ | **[Furkiozknn.github.io](https://github.com/Furkiozknn/Furkiozknn.github.io)** | The project directory, generated from every repository's `project-meta.json`. Nothing on it is hand-written. | `37` |

**Apps, and games — Godot 4, each one played headlessly in CI**

| | Project | The one idea it is built on | Tests |
|:--:|---|---|---:|
| 🗺️ | **[buradane](https://github.com/Furkiozknn/buradane)** | The nearest toilet, park, fountain or library. 167,829 OSM places; all 973 district centres covered within 15 km. | `347` |
| 📚 | **[masal](https://github.com/Furkiozknn/masal)** | A bedtime story around one child's name. A Turkish suffix engine gets *Sinop'ta* and *Trabzon'da* right. | `92` |
| 🚀 | **[nova-drift](https://github.com/Furkiozknn/nova-drift)** | Endless browser space-runner. Real bloom, live-synthesized audio — not one sound file in the repo. | `38` |
| 🎵 | **[tek-tus-kosu](https://github.com/Furkiozknn/tek-tus-kosu)** | One button, every obstacle on the music's beat grid. A post-run histogram shows how early or late each press landed. | `961` |
| 🔄 | **[yercekimi-cevir](https://github.com/Furkiozknn/yercekimi-cevir)** | No jump button — one key flips gravity. 20 precision rooms, each finished by the suite. | `841` |
| ⛏️ | **[derin-kazi](https://github.com/Furkiozknn/derin-kazi)** | Dig, sell, upgrade, go deeper — the fuel gauge is the real timer. Five layers down to the core. | `477` |
| 🪝 | **[kanca](https://github.com/Furkiozknn/kanca)** | Hook, swing, release and carry the momentum. Medal times measured by a bot, not guessed. | `115` |
| 🧱 | **[godot-2d-sablon](https://github.com/Furkiozknn/godot-2d-sablon)** | Two Godot 4 starter projects whose jump feel was *measured*: coyote time, jump buffering, variable jump height. | `21` |
| | | **Total, across 26 repositories with suites** | **`5,247`** |

<sub>Not counted: this repository (its suite checks the page, so it should not be able to raise the total) and the archived `claude-quota-monitor`, superseded by `claude-code-intelligence`. **[The full ledger →](TESTLER.md)**</sub>

</details>

---

> A number on this page is checkable, or it is not on the page. Every test count is re-derived from the run that printed it — [the ledger](TESTLER.md).

**Work with me** — an MCP / agent security review of a server before you run it (from $900), a test suite and release path for code that works but doesn't ship (from $1,500), or ongoing contract work at $50/hour. [Scope, evidence and how to start →](HIRE.md)
