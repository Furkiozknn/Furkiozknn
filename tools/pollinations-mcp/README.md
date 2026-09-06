# genmedia-mcp

Six free-tier image providers behind one MCP tool, tried in order until one
works, plus video, speech and music. No dependencies — no `pip install`, no `npx`, nothing that
updates itself between the audit and the run. The whole supply chain is
`server.py`, `providers.py` and `http_client.py`.

## Providers

| Provider | Free tier | Card? | Video | Notes |
|---|---|---|---|---|
| **cloudflare** | 10,000 neurons/day ≈ ~2,000 small images | No | No | Most generous free image tier found. FLUX.1-schnell. |
| **gemini** | ~100–500 images/day | No | No | Nano Banana. **Free-tier prompts may be used for training** — do not send anything private. |
| **nvidia** | ~5,000 credits that **never expire**, ~40 RPM | No | No | NVIDIA NIM, FLUX.1. Email signup only. |
| **bfl** | Free FLUX.2 [dev] + FLUX Kontext [dev], rate limited | No | No | Black Forest Labs, the people who make FLUX. Async polling. |
| **together** | Free FLUX.1-schnell endpoint | No | No | Free access has historically been promo-based; verify it is still on. |
| **pollinations** | ~1 req/15s anonymous, ~1 req/3s keyed | No | **Yes** | The only one here that needs *no key at all*, and the only one doing video. |

Default chain: `cloudflare → gemini → nvidia → bfl → together → pollinations`. Best free tier
first, keyless Pollinations last so there is always a floor that works with zero
configuration. Unconfigured providers are skipped, never attempted.

## Tools

| Tool | What it does | Needs a key? |
|---|---|---|
| `generate_image` | Text → image, saved to disk, preview inlined into the reply | No |
| `generate_video` | Text → MP4, saved to disk | **Yes** (Pollinations) |
| `generate_speech` | Text → spoken audio, 100+ voice presets | **Yes** (Pollinations) |
| `generate_music` | Text → music or sound effect | **Yes** (Pollinations) |
| `list_providers` | What is configured, the active chain, what each missing one needs | No (no network) |
| `list_models` | Pollinations image/video catalogue | No |

## Switching between providers

Three levers, in order of how targeted they are:

```bash
# 1. Change the chain for the whole session
export IMAGE_PROVIDERS=gemini,pollinations

# 2. Pin one provider for a single call — it fails loudly instead of falling back,
#    because if you asked for Cloudflare you want to know Cloudflare broke
generate_image(prompt="...", provider="cloudflare")

# 3. Do nothing. The default chain already falls through on 429s and outages.
```

When a call falls through, the result says so (`fell back after: gemini: 429 …`),
so a chain quietly burning its first provider every time is visible rather than
invisible.

## Setup

Wired up in this repo's `.mcp.json`, so it loads in any session opened here and
works immediately with no key via Pollinations. Add providers by exporting their
credentials before starting Claude Code:

```bash
export CLOUDFLARE_ACCOUNT_ID=...  CLOUDFLARE_API_TOKEN=...   # best free image tier
export GEMINI_API_KEY=...                                     # aistudio.google.com/apikey
export TOGETHER_API_KEY=...
export NVIDIA_API_KEY=...                                     # build.nvidia.com
export BFL_API_KEY=...                                        # dashboard.bfl.ai
export POLLINATIONS_KEY=...                                   # unlocks video
```

Then prove each one with a single real call:

```bash
python3 tools/pollinations-mcp/server.py --selfcheck
```

## Configuration

| Variable | Default | Meaning |
|---|---|---|
| `IMAGE_PROVIDERS` | *(unset)* | Comma-separated chain override. |
| `POLLINATIONS_KEY` | *(unset)* | Unlocks video and Pollinations' faster image tier. |
| `CLOUDFLARE_ACCOUNT_ID` / `CLOUDFLARE_API_TOKEN` | *(unset)* | Workers AI. Token needs the Workers AI permission. |
| `GEMINI_API_KEY` | *(unset)* | Google AI Studio. |
| `TOGETHER_API_KEY` | *(unset)* | Together AI. |
| `NVIDIA_API_KEY` | *(unset)* | build.nvidia.com, NVIDIA Developer Program. |
| `BFL_API_KEY` | *(unset)* | dashboard.bfl.ai. |
| `POLLINATIONS_OUTPUT_DIR` | `./generated-media` | Where media is written. |
| `POLLINATIONS_TIMEOUT` | `300` | Per-request timeout, seconds. Video is slow. |
| `POLLINATIONS_MIN_INTERVAL` | per-provider | Override request spacing. |

## Design notes

- **Zero dependencies.** Python 3.9+ standard library only.
- **Writes cannot escape the output directory.** Names are slugified and the
  resolved path is checked; `../../etc/passwd` as an `output_name` lands harmlessly
  inside the output dir.
- **Content types are verified before saving.** An HTML error page or a JSON error
  body is reported, never written to disk as a `.jpg` that will not open.
- **Throttling is per host,** so Pollinations' 15-second anonymous spacing never
  delays a Cloudflare call.
- **Tool failures are `isError` results, not JSON-RPC protocol errors,** so the
  model reads what went wrong and adjusts instead of the session breaking.
- **A pinned provider never silently falls back.** Only the chain falls through.
- **Large images are not inlined.** Over 3 MB is referenced by path only.

## Tests

```bash
python3 -m unittest discover -s tests -v
```

97 tests, all hermetic — every HTTP call is stubbed, so the suite passes offline.
They cover path-traversal refusal, chain resolution and ordering, each provider's
response parsing (including Cloudflare's base64 envelope vs. raw binary, Gemini's
camelCase/snake_case `inlineData`, and a Gemini text-only refusal), fall-through
behaviour, per-host throttling, the audio tools' model and format handling, and
the MCP handshake.

## Known limits

- **Adding an OpenAI-compatible provider is three lines.** Subclass
  `OpenAICompatibleImages` in `providers.py`, set `base_url` / `default_model` /
  `key_env`, and add it to `REGISTRY`. That is how `nvidia` was added.
- **Verification status differs per provider.** Pollinations' request shape was read
  from its published `APIDOCS.md`, and BFL's submit/poll/download shape from the
  BFL-authored `bfl-api` skill. The Cloudflare, Gemini, NVIDIA and Together adapters,
  and BFL's free-model endpoint names, were written from knowledge of those APIs; the environment they were built in blocks every one of those hosts at its
  egress proxy, so they could not be checked against primary documentation or a
  live call. **Run `--selfcheck` before trusting them.** If one is wrong, it is
  wrong in `providers.py` in about ten lines.
- Together's free FLUX endpoint began as a time-limited promotion; it may no
  longer be free.
- Gemini's free tier may train on submitted prompts.
- Video, speech and music are Pollinations-only and share one free key. No free
  provider surveyed offers keyless text-to-video at any quality.
- The audio endpoint's request shape was read from Pollinations' APIDOCS.md, but
  like everything else here it has not been proven against a live call from this
  environment.
- No streaming or progress reporting: a video call blocks until the MP4 arrives.
