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

---

# Part 2 — The wider free-provider landscape (rotation targets)

Follow-up pass, same date. The goal here was breadth: enough separate free tiers
that when one throttles or dries up, you move to the next rather than stopping.

## 5. Free image-generation tiers, compared

| Provider | Free allowance | Card? | Key? | Video | Verified |
|---|---|:--:|:--:|:--:|---|
| **Cloudflare Workers AI** | 10,000 neurons/day ≈ ~2,000 small FLUX images, resets 00:00 UTC | No | Yes (free) | No | Search only |
| **Google Gemini** (Nano Banana) | ~100–500 images/day; Imagen capped ~2 IPM | No | Yes (free) | No (Veo is paid) | Search only |
| **NVIDIA NIM** | 5,000 credits, ~40 RPM, credits do not expire | No | Yes (free) | Some video models | Search only |
| **Together AI** | FLUX.1-schnell-Free endpoint | No | Yes (free) | No | Search only |
| **ModelScope** | 2,000 req/day total, 500 RPD per model | No | Yes (free) | Some | Search only |
| **Hugging Face** | ~$0.10/month inference credits + free Spaces | No | Yes (free) | Limited | Search only |
| **Pollinations** (anon) | ~1 req/15s | No | **No** | No | Docs |
| **Pollinations** (keyed) | ~1 req/3s | No | Yes (free) | **Yes** | Docs |
| **SiliconFlow** | ~$1 starter credit; some models permanently free | No | Yes | Some | Weak — also now requires real-name ID verification |

**Ranking for our purposes.** Cloudflare is the clear first choice: the largest
free allowance by an order of magnitude, no card, and it starts immediately.
Gemini is the best second because its failure mode is different (daily request
cap rather than a compute budget), so the two rarely exhaust together. Pollinations
belongs last but must stay in the chain — it is the only one that works with no
configuration at all, which makes it the floor that keeps the tool from ever being
completely dead.

**Already in-house:** [nvidia-nim-mcp](https://github.com/Furkiozknn/nvidia-nim-mcp)
already covers NIM. That is a fifth free tier reachable without writing anything new.

**Caveats worth carrying:**
- Gemini's free tier may use submitted prompts for training. Not for anything private.
- Together's free FLUX access started as a 3-month promotion; treat "still free" as
  unverified until `--selfcheck` says otherwise.
- Google cut free-tier daily quotas across the board in December 2025 — quoted
  numbers age fast, so the design must tolerate a tier shrinking without notice.

## 6. Video: the honest answer has not changed

Searching specifically for free text-to-video APIs returns mostly SEO content farms
making unverifiable claims ("unlimited free video generation, no credit card"). Set
against primary sources, the real picture is:

- **Pollinations** (`GET /video/{prompt}`) is the only documented API here that
  returns MP4 — `veo`, `seedance-2.5`, `wan-3.0`, `grok-video-pro`, `minimax-h3`,
  `nova-reel`, with `duration`, `aspectRatio`, `audio` and first/last-frame control.
  It requires a key.
- **No keyless text-to-video exists**, at any quality.
- The genuinely free path with real headroom is **self-hosting**: Alibaba's **Wan**
  family is Apache 2.0 and runs on one consumer GPU — no credits, no queue, no
  watermark. That is a hardware cost, not a subscription, and it is the only option
  that does not have somebody else's quota attached. It matches what
  `research/raw/C_video_generation.md` already concluded independently.

## 7. Rotation strategy, as implemented

`tools/pollinations-mcp/` now runs a provider chain rather than a single provider:

- Default order `cloudflare → gemini → together → pollinations`, best free tier
  first, keyless floor last.
- Unconfigured providers are skipped, never attempted.
- `IMAGE_PROVIDERS` reorders the chain for a session; `provider=` pins one for a
  single call and then fails loudly instead of falling back, because a pinned
  provider that silently redirects hides the thing you were testing.
- Fall-through is reported in the result, so a chain quietly burning its first
  provider on every call is visible.
- `list_providers` shows what is wired up and what each missing one needs, with no
  network call.

**Verification gap, stated plainly.** Only the Pollinations request shape was read
from vendor documentation. Cloudflare, Gemini and Together were written from
knowledge of those APIs, because this environment's egress proxy blocks
`developers.cloudflare.com`, `ai.google.dev`, `api.cloudflare.com`,
`api.together.xyz` and `huggingface.co` — and, as it turns out, GitHub API access
outside the one allowed repo. `server.py --selfcheck` exists precisely to close
that gap in one command on an unrestricted machine.

## 8. Sources

- [Cloudflare Workers AI free tier (10k neurons/day)](https://costbench.com/software/llm-api-providers/cloudflare-workers-ai/free-plan/) · [neuron guide](https://freeaiapi.org/article/cloudflare-api-key-guide)
- [Gemini image generation free tier](https://www.aifreeapi.com/en/posts/gemini-image-generation-free-api) · [rate limits](https://www.aifreeapi.com/en/posts/gemini-api-free-tier-rate-limits)
- [Together AI free FLUX.1 [schnell]](https://www.together.ai/blog/flux-api-is-now-available-on-together-ai-new-pro-free-access-to-flux-schnell)
- [NVIDIA NIM free tier](https://yangmao.ai/en/providers/nvidia-build/) · [limits](https://costbench.com/software/llm-api-providers/nvidia-nim/free-plan/)
- [Hugging Face Inference Providers](https://huggingface.co/docs/inference-providers/index) · [free tier limits](https://klymentiev.com/blog/huggingface-inference-api)
- [ModelScope free limits](https://www.free-model.com/providers/modelscope/) · [awesome-free-llm-apis](https://github.com/mnfst/awesome-free-llm-apis/blob/main/README.md)
- [Free image API comparison](https://www.edenai.co/post/top-free-image-generation-tools-apis-and-open-source-models) · [what is actually free in 2026](https://apiframe.ai/blog/free-ai-image-generation-api-2026)
