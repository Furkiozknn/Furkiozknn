# The Connector Channel — Why Some Tools Work When the Network Is Blocked

**Scope:** An audit triggered by an empirical discovery: in a cloud session whose egress
proxy blocks 15 of 16 AI provider hosts, a Canva image generation call succeeded anyway.
This document explains why, inventories what that makes available, and ranks what to add.
**Date:** September 2026.

---

## 1. The mechanism, verified

Cloud sessions have a **Network access** level. Ours is `Trusted`, which allowlists
package registries, GitHub and cloud SDK hosts and nothing else. Direct HTTPS to
`image.pollinations.ai`, `api.cloudflare.com`, `integrate.api.nvidia.com` and twelve
other provider hosts returns 403 at the CONNECT.

But the platform documentation states that regardless of access level, sessions can still
reach **"MCP connectors you enable, whose traffic travels through Anthropic's servers."**
Connector traffic does not go through the session's network allowlist at all.

**Verified, not assumed.** A Canva `generate-design` call returned four real design
candidates; `create-design-from-candidate` and `export-design` then produced a downloadable
PNG. Every one of those succeeded while `curl` to the same class of host was still being
refused. The one thing that failed was fetching the finished PNG *into* the session — that
is a direct HTTP GET to `export-download.canva.com`, so it goes through the blocked path.

**The rule this establishes:**

> Anything reachable as an MCP connector works in a locked-down cloud session.
> Anything reachable only as a raw HTTPS API does not.

This is a genuinely different axis from "is it free". A free API behind a blocked host is
worth less here than a free connector, and our own `genmedia-mcp` — which is a raw HTTPS
client — is on the wrong side of that line in this environment while being on the right
side on any ordinary machine.

## 2. What is already connected

| Connector | Free capability | Tested |
|---|---|---|
| **Canva** | Design generation from a prompt; export to **PDF / JPG / PNG / GIF / MP4 / PPTX**; asset upload; brand kits | ✅ **Verified working** — generated and exported an image |
| **Figma** | Read designs, screenshots, metadata, Code Connect | ⚠️ **Starter tier, "View" seat** — read-only; creation tools will fail. Weave not linked. |
| **Higgsfield** | Image, video, audio, 3D generation | ❌ **0.03 credits** — effectively empty |
| github, Supabase, Vercel, Notion, Slack, Linear, Asana, Gmail, Google Drive/Calendar, Microsoft Learn | Non-media, all working | — |

**Canva is the finding.** It generates images *and* exports MP4, which makes it the only
video path in this session that needs neither a key nor a network change. It is not a
diffusion model and will not replace FLUX for photographic work, but for posters, social
formats, thumbnails and short motion pieces it is available right now at zero cost.

## 3. Worth adding, ranked

Connectors are added by the account owner at claude.ai — including from a phone browser.
No code change here; nothing in this repo needs to change for any of them.

### Tier 1 — authless, free, zero setup

| Connector | Why it matters |
|---|---|
| **Parallel Search** | `web_search` + `web_fetch`, free, **authless**. This closes the single biggest gap in all of this work: vendor documentation hosts (`developers.cloudflare.com`, `ai.google.dev`) are blocked, which is exactly why the Cloudflare, Gemini, NVIDIA and Together adapters remain unverified. A `web_fetch` on the connector channel reaches them. **Highest-value addition by a distance.** |

Other authless connectors exist (AccuWeather, Anthropic Economic Index, ICD-10, Airfield
Directory) but none is relevant to this work.

### Tier 2 — free tier, free account

| Connector | Why it matters |
|---|---|
| **Unsplash** | Free HD photography, searchable, licensed for commercial use. Real photographs where generation is the wrong tool — site imagery, textures, backgrounds. Complements generation rather than competing with it. |
| **TomTom Maps** | Geocoding, reverse geocoding, POI and area search on a free tier. Directly relevant to **buradane**, which is a need-driven place finder — this is the one connector here that serves a shipped product rather than the tooling. |
| **Cloudflare Developer Platform** | Workers, KV, R2 on your own free account. Worth a look for a second reason: if it exposes Workers AI, it would put Cloudflare's 10k-neurons/day image tier on the connector channel, i.e. reachable without the network change. Unconfirmed — the visible tool list does not show AI tools. |
| **Whimsical** | Flowcharts and diagrams on a free tier. Marginal — `beautiful-mermaid` and inline SVG already cover most of it. |

### Tier 3 — rejected

- **Exa, Firecrawl** — good search, but paid keys, and Parallel Search covers the need free.
- **Adobe for creativity** — 60+ tools including `animate_design`, but requires a paid Adobe subscription.
- **Riverside, vidIQ, Metricool, OpenRush** — paid, and aimed at publishing/marketing rather than production.

## 4. What this changes about our own server

`genmedia-mcp` is a raw HTTPS client, so in a locked-down cloud session it can only reach
Gemini. That is not a flaw to fix — on a normal machine it works fully, and the whole point
of the provider chain is surviving exactly this kind of environmental difference. But it
sets the priority order for anyone using it from the cloud:

1. `GEMINI_API_KEY` — works today, no network change.
2. Network access → `Custom` with the provider domains — unlocks the rest of the chain.
3. Canva — already there, needs neither.

And it adds a check worth running before writing any future adapter: **is this capability
available as a connector?** If it is, the connector is strictly more available than an
adapter, in exactly the environments where availability is hardest.

## 5. Sources

Behaviour in sections 1–2 was established by direct testing in this session. Connector
inventory from the MCP connector registry. Platform behaviour from
[Configure cloud environments](https://code.claude.com/docs/en/cloud-environments) and
[Claude Code on the web](https://code.claude.com/docs/en/claude-code-on-the-web).
