<img src="assets/hero.svg" alt="Furki Özkan — agent systems, MCP and developer tooling. 16 repos, 2,168 tests, 569 commits." width="100%">

I build the infrastructure AI agents run on — async job contracts, pipeline DAGs, MCP servers — and the tooling that checks whether any of it actually works.

### Start here

- **[mcp-vet](https://github.com/Furkiozknn/mcp-vet)** — audits an MCP server *before* you install it. Every claim carries a file and a line, it reads the code rather than the star count, and it never executes what it audits. Standard library only, no dependencies. <sub>`289 tests`</sub>
- **[buradane](https://github.com/Furkiozknn/buradane)** — "what do I need, and where is the nearest one?" 167,829 real OpenStreetMap places across all 81 provinces of Türkiye, on FastAPI + PostGIS with a Next.js/MapLibre front end. <sub>`324 tests`</sub>
- **[claude-code-intelligence](https://github.com/Furkiozknn/claude-code-intelligence)** — where the tokens went, what it cost, and when the quota resets. An OTLP receiver and transcript parser that never phones home; nothing leaves the machine. <sub>`261 tests`</sub>

Or skip the reading and **[play nova-drift](https://furkiozknn.github.io/nova-drift/)** — an endless browser space-runner with real bloom, synthesized audio and a 0.7 MB first load. No build step, no install.

<p align="center">
  <a href="https://github.com/Furkiozknn/buradane">
    <img src="https://raw.githubusercontent.com/Furkiozknn/buradane/main/assets/demo.gif" alt="buradane: picking categories on a map of Istanbul, then typing free text and watching the results narrow to 19" width="760">
  </a>
</p>

<p align="center"><sub>A real session, captured by a script in that repo. Typing “ücretsiz tuvalet” takes 167,829 places down to the 19 nearest free toilets.</sub></p>

**[2,168 tests across 16 repositories](TESTLER.md)** — and that link is the point: every count on this page is traced to the suite run that printed it. No generated stat cards here. A number is checkable or it isn't on the page.

> **Available for remote contract work** — MCP and agent infrastructure, and turning code that works into code that ships. Remote, Türkiye, European hours. **[What I can be hired for, and what it costs →](HIRE.md)**

---

## How I work

**Tests before claims.** Every count here is re-derived, not remembered. This page itself has lost two numbers that way: a "1,426 tests" figure that turned out to be a grep rather than a suite, and a 1.4 MB load that measured 0.7 MB.

**Hermetic CI.** Suites run offline, so a CDN outage cannot redden a build. The gate is tested too — `ajans-os` plants a deliberate violation in its own tree and fails if its validator misses it.

**Honest READMEs.** Known limits are listed, not hidden: a measured seven-minute upscale stall on integrated graphics, a gateway column headed *deliberately absent*, voice cloning left out on purpose.

**Licences checked down the tree.** `rembg`'s default model is CC-BY-NC — caught by reading the dependency tree, and refused unless you opt in knowingly. `buradane` splits ODbL data from MIT code in a NOTICE file.

## Agent systems

- **[ajans-os](https://github.com/Furkiozknn/ajans-os)** — an agency OS built research-first: 40 agent projects read with file-and-line evidence, then 11 ADRs, 6 machine-readable contracts, 13 modules. Nothing enters the architecture without four answers — the problem it solves, the failure it prevents, the cost it adds, and evidence from two independent projects. Five candidates were refused on that rule and parked with the conditions that would let them in.
- **[turkce-ajanlar](https://github.com/Furkiozknn/turkce-ajanlar)** — eight Claude Code sub-agents whose output language is Turkish, not a translated system prompt. They know PowerShell 5.1 has no `&&`, that cp1254 breaks a Python tool's stdout before it prints a line, and that a heredoc quietly eats backslashes. One source, exported to Cursor, OpenCode, Copilot and Codex, with CI that fails on a stale copy.

## Infrastructure

- **[ai-job-gateway](https://github.com/Furkiozknn/ai-job-gateway)** — submit a generative-AI job, get an id back instantly, then poll or take a webhook. Idempotency keys that survive a restart, SSRF-guarded signed webhooks, and a queryable dead letter.
- **[ai-workflow-engine](https://github.com/Furkiozknn/ai-workflow-engine)** — pipelines as plain YAML DAGs, validated before they run. Cycles, undeclared dependencies and unbounded fan-out are rejected at parse time rather than at 3 a.m.

<sub>Supporting cast: <a href="https://github.com/Furkiozknn/prompt-template-manager">prompt-template-manager</a> (prompts versioned in git, so a change is a diff) · <a href="https://github.com/Furkiozknn/model-comparison-harness">model-comparison-harness</a> (same prompt, N providers, one report, and a judge that says <i>unparseable</i> instead of guessing) · <a href="https://github.com/Furkiozknn/asset-provenance-toolkit">asset-provenance-toolkit</a> (which model, job and prompt made this file, written into the file)</sub>

## MCP servers — local, keyless

- **[mini-creative-toolkit](https://github.com/Furkiozknn/mini-creative-toolkit)** — 23 CPU-only media tools behind one server: background removal, resize, thumbnails, GIFs, video trim. Twenty-two never touch the network, and the README names the one that does.
- **[local-notes-search-mcp](https://github.com/Furkiozknn/local-notes-search-mcp)** — semantic search over your own files. No server, no API key, no upload at query time.
- **[voice-io-mcp](https://github.com/Furkiozknn/voice-io-mcp)** — speech in and out, with a hosted fast path and a fully local, keyless fallback.
- **[nvidia-nim-mcp](https://github.com/Furkiozknn/nvidia-nim-mcp)** — NVIDIA NIM's free tier inside Claude Code, falling back to Groq, Mistral, Gemini or Cerebras when a model is rate-limited.

## Things people can just use

- **[nova-drift](https://github.com/Furkiozknn/nova-drift)** — endless browser space-runner. Real bloom post-processing, fully synthesized audio, a seeded daily run, adaptive render scaling, 0.7 MB first load, no build step. **[Play it](https://furkiozknn.github.io/nova-drift/)**
- **[masal](https://github.com/Furkiozknn/masal)** — a bedtime story written around one child's name, age and town, with the colouring page embedded in it. A Turkish suffix engine inflects the name correctly, which template substitution cannot: Sinop takes *-ta*, Trabzon takes *-da*. Nothing downloads, and CI fails if a path to export the drawing ever appears. **[Read one](https://furkiozknn.github.io/masal/)**

<p align="center">
  <a href="https://furkiozknn.github.io/nova-drift/">
    <img src="https://raw.githubusercontent.com/Furkiozknn/nova-drift/master/assets/gameplay.gif" alt="Nova Drift gameplay: a ship threading between red obstacles down a glowing space tunnel, score climbing" width="620">
  </a>
</p>

<p align="center"><sub>Real play, not a mockup — captured by a script in that repo that opens the game through the same fixture its tests use. That run scored 446.</sub></p>

---

<p align="center">
  <sub>
    <a href="TESTLER.md">Where the 2,168 comes from</a> ·
    <a href="HIRE.md">Hire me</a> ·
    <a href="https://x.com/furkiozkan">@furkiozkan</a>
  </sub>
</p>
