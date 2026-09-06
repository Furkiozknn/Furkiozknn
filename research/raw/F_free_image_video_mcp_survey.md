# Free Image / Video Generation MCP Servers — Survey and Risk Assessment

**Scope:** GitHub search for MCP servers that generate images or video and can be used
without paying. Goal was not the best-looking output but the *lowest-risk thing that
works*, installable immediately and reusable across sessions.
**Method:** GitHub repository search (`mcp` × `image generation`, `pollinations`,
`text-to-image free no api key`), then reading each candidate's actual README and
auth requirements rather than trusting its description. Live API behaviour checked
against Pollinations' published `APIDOCS.md` (168 KB, fetched from `main`).
**Date:** September 2026.

---

## 0. The finding that reframes the question

Nearly every "free image generation MCP" on GitHub is a wrapper around
**Pollinations**. That is not a coincidence — it is the only generative image API with
a genuinely anonymous tier, so it is the only thing anyone can build a keyless wrapper
around. The search therefore collapses from "which MCP?" to two real questions:

1. Is Pollinations still keyless? **Partly.** The current API host,
   `gen.pollinations.ai`, states plainly: *"Everything else | Bearer key required
   unless the endpoint documents `?key=` support."* Only media reads and the model
   catalogue are exempt. The older `image.pollinations.ai/prompt/{prompt}` host still
   answers anonymously, but it is visibly the legacy path.
2. Given that, which wrapper do you trust in your tool list? That is where every
   candidate fell down.

**Video** turned out to be better than expected on capability and worse on cost:
`GET /video/{prompt}` exists and returns MP4 from `veo`, `seedance-2.5`, `wan-3.0`,
`grok-video-pro`, `minimax-h3`, `nova-reel` and others, with `duration`, `aspectRatio`,
`audio` and first/last-frame controls. It requires a key. There is **no keyless
text-to-video anywhere** in this survey — that option does not exist, at any quality.

---

## 1. Candidates

| Repo | Stars | Free without a key? | Verdict |
|---|---:|---|---|
| [pinkpixel-dev/MCPollinations](https://github.com/pinkpixel-dev/MCPollinations) | 39 | Yes (old API) | **Rejected — archived.** The most-starred option is read-only and unmaintained; its author redirects to `nectar-mcp`. |
| [pinkpixel-dev/nectar-mcp](https://github.com/pinkpixel-dev/nectar-mcp) | 2 | **No** | **Rejected.** Its README: *"Generation and balance tools require `POLLINATIONS_API_KEY`."* Seven tools, npm-distributed, 2 stars, ~2 months old. Fails the "free" requirement and carries the most supply-chain exposure of the set. |
| [MohamedAbdallah-14/prompt-to-asset](https://github.com/MohamedAbdallah-14/prompt-to-asset) | 18 | Claims "zero-key first" | **Rejected.** Genuinely interesting (30+ model routing, asset validation), but 17 open issues on 18 stars, and it is a large TypeScript dependency tree for what is ultimately one HTTP GET. |
| [Tolerable/pollinations-claude-code](https://github.com/Tolerable/pollinations-claude-code) | 5 | Yes, BYOP | Plausible but unproven; a Claude Code plugin rather than a portable MCP server. |
| [bendusy/pollinations-mcp](https://github.com/bendusy/pollinations-mcp) | 9 | Unclear | Stale (last touched Feb 2026), no description beyond its own name. |
| [jpbester](https://github.com/jpbester/pollinations-mcp-server) · [setmpp](https://github.com/setmpp/mcp-pollinations) · [tomdacatto](https://github.com/tomdacatto/pollinations-mcp-server) | 0–3 | Various | Long tail of near-identical thin wrappers, none with a maintenance signal. |
| [SamurAIGPT/Generative-Media-Skills](https://github.com/SamurAIGPT/Generative-Media-Skills) | 4.2k | **No** — muapi.ai, paid | High stars, but a paid-API skill pack. Not applicable. |
| [Anil-matcha/Open-Generative-AI](https://github.com/Anil-matcha/Open-Generative-AI) | 27.8k | Self-hosted, MIT | Not an MCP server — a self-hosted studio over 600+ models. Worth knowing about; wrong shape for a tool list. |

Also noted and set aside: `pollinations/chucknorris` (67 stars) is an MCP server from the
Pollinations org itself, but it is a jailbreak-prompt server, not image generation.

## 2. Why none of them got installed

The stars are in the wrong places. The 39-star option is archived; the actively
maintained one requires a key and so is not free; everything else is a 0–9 star,
single-author npm or PyPI package that would sit in the tool list with network access
and filesystem write permission, auto-updating on every `npx` invocation.

For a wrapper this thin — one HTTP GET, one file write — accepting an unaudited
auto-updating dependency is a bad trade. The whole useful surface of every candidate
above is a few hundred lines.

## 3. What was installed instead

`tools/pollinations-mcp/server.py` — a single-file, zero-dependency MCP server
(Python standard library only), pinned in this repo, wired up via `.mcp.json`.

- `generate_image` works with **no key** via the legacy anonymous host.
- `generate_video` uses `gen.pollinations.ai` and states plainly that it needs a key,
  with the free-registration URL, rather than failing obscurely.
- `list_models` needs no key on either path.
- 41 hermetic tests: path-traversal refusal, host routing, content-type rejection,
  error-code mapping, MCP handshake. All stubbed, so they run offline.

**Not verified against the live API.** The session that built this had
`image.pollinations.ai` and `text.pollinations.ai` blocked at the egress proxy
(403 on CONNECT), so URL shapes come from the published API docs and the first real
call from an unrestricted machine remains the actual proof.

## 4. Recommendation

Register a free key at <https://enter.pollinations.ai/keys>. It is the single change
that matters: it unlocks video entirely, drops the image throttle from ~15s to ~3s,
and moves image generation off a legacy host that is being retired. The server picks
up `POLLINATIONS_KEY` from the environment and switches hosts automatically — no code
change, no reinstall.
