# Adjacent Free Tiers and Tooling — Audio, LLMs, Post-Production, MCP Security

**Scope:** A follow-on to `F_free_image_video_mcp_survey.md`, applying the same test to
four neighbouring areas: what is genuinely free, what the licence actually permits, and
what is low-risk enough to install today.
**Date:** September 2026.
**Standing caveat:** vendor documentation hosts are blocked by this environment's egress
proxy, so figures below come from secondary sources unless marked otherwise. Treat quoted
quotas as "check before you depend on it" — Google cut its free daily quotas across the
board in December 2025, which is how fast these age.

---

## 1. Audio and music

### 1.1 The finding that was already paid for

Pollinations' `GET /audio/{text}` — the same host, same free key already needed for video —
does **three** things, and this was read directly from its `APIDOCS.md`:

- **Speech:** 100+ voice presets. The list includes the Kokoro voice ids (`af_bella`,
  `am_michael`, `bf_emma`, `jf_alpha`, `zf_xiaoxiao` …), so Kokoro is reachable without
  running it yourself. Formats: mp3, opus, aac, flac, wav, pcm.
- **Dialogue:** `eleven-dialogue` takes one `voice: text` turn per line.
- **Music and SFX:** `elevenmusic` (3–300s, instrumental mode), `lyria-3-clip` (fixed 30s),
  `stable-audio-3-medium` / `-large` (1–380s, steps, seed, negative prompt), `eleven-sfx`
  (looping, prompt influence).

**One free registration now covers image, video, speech, music and sound effects.** That is
the single highest-leverage fact in this document, and `generate_speech` / `generate_music`
are implemented in `tools/pollinations-mcp/` as of this pass.

### 1.2 Local, offline, no quota

| Model | Licence | Size / cost | Verdict |
|---|---|---|---|
| **Kokoro-82M** | Apache 2.0 | 82M params, ~327 MB, ~2–3 GB VRAM **or CPU** | Best quality-per-byte. Topped the TTS Arena at launch; 54 voices, 8 languages. The pick if English is enough. |
| **Piper** | MIT | Smallest and fastest, ONNX, runs on a Raspberry Pi | 900+ voices, 47 languages. More robotic. The pick for breadth of language and minimum hardware. |
| **XTTS v2** | Coqui (check terms) | Higher latency and memory | Clones a voice from seconds of audio. Only worth it if cloning is the point. |

### 1.3 The licensing trap, again

**MusicGen (Meta) is CC BY-NC 4.0.** Using its output in anything commercial violates the
licence *regardless of self-hosting* — the weights being downloadable says nothing about
what you may do with what comes out. This is precisely the class of bug
`mini-creative-toolkit` already caught with rembg's default model, and it is worth stating
as a rule rather than a one-off: **for generative media, read the licence on the model, not
just the repo.**

Safe alternatives: **ACE-Step 1.5** (Apache 2.0, vocals and instrumentals, ~4 min, fast on
consumer GPUs) is the best permissive pick. **Stable Audio Open** ships under Stability's
Community Licence, which allows commercial use only below a revenue threshold — permissive
until you succeed, which is a strange shape to build on.

*Note: this session already exposes an `acestep` skill, so ACE-Step is reachable without
new tooling.*

---

## 2. Free LLM / text API tiers

Directly relevant to `model-comparison-harness` and `ai-job-gateway`, and the same chain
pattern the image providers now use applies unchanged.

> **Correction (later pass, same date).** An earlier version of this section
> listed Cerebras as offering ~1M tokens/day on a permanent free tier and
> recommended it first. That is wrong as of July 2026 and the recommendation
> below has been rewritten. Mistral's allowance was also overstated. Both are
> corrected in the table.

| Provider | Free allowance | Card? | Notable |
|---|---|:--:|---|
| **Groq** | ~30 RPM, Llama 3.3 70B | No | Fastest generation by a distance — ~320 tok/s on LPU hardware. Now the top pick. |
| **Google AI Studio** | Gemini free tier | No | Same key as the image provider already wired up. |
| **OpenRouter** | ~30 free models, 20 RPM | No | One key, many models — the natural comparison-harness backend. |
| **Mistral** | **~$10/month in API credits**, ~1 RPS, 500K TPM | No | Requires phone verification, and free-mode prompts may train Mistral models unless you opt out. |
| **GitHub Models** | Mixed catalogue incl. OpenAI and Llama | No | Worth a look given the GitHub identity is already there. |
| **SambaNova** | $5 credits (30-day), 20 RPM, 200K tokens/day | No | Fast RDU inference; time-limited rather than permanent. |
| ~~**Cerebras**~~ | ⚠️ **Free tier ended July 2026** | **Yes** | Replaced by $5 trial credits that expire in 30 days *and require a verified payment method*. No longer a permanent free tier. |
| ~~**Chutes.ai**~~ | ⚠️ **Free tier ended** | — | Paid only now. |
| ~~**Nebius**~~ | ⚠️ **Trial suspended July 13 2026** | **Yes** | ~$1 trial credit, $25 minimum deposit. |
| ~~**DeepInfra**~~ | ⚠️ **No free tier** | **Yes** | Card or pre-pay required before any API use. |

**The rule that matters more than the numbers:** free tiers are funded by your prompts.
Assume anything sent to one may train a model. Keep customer data and anything from
`buradane` off them entirely; on a paid tier, part of what you buy is that guarantee.

**Shape for us:** Groq first (speed, and a free tier that is still actually free),
OpenRouter as the breadth fallback, Mistral for batch work where ~1 RPS is fine. Same
`resolve_chain` logic, different registry.

**The meta-lesson is the correction itself.** Four of the providers in this table
withdrew or gutted their free tier inside a few months, and two of them did it *after*
being written down here. Any design that pins one free provider is a design with an
expiry date; the chain-with-fallback is not a nicety, it is the only shape that survives
this churn. Re-check quotas before depending on them, and treat every figure above as
decaying.

---

## 3. Image and video post-production

The gap this fills: generation gives you a file, not a deliverable.

### 3.1 Already in hand

This session already exposes local, key-free skills covering much of it: `ffmpeg`,
`video-edit` (trim, concat, resize, overlay, compress), `video-download` (yt-dlp),
`video-understand` (local frame extraction + Whisper transcription). Before writing
anything new, that is the baseline — and it costs nothing and calls no API.

### 3.2 Upscaling and matting

- **Real-ESRGAN** is the best local upscaler for general photos: 67 MB, 2×/4×, runs on any
  Vulkan GPU (NVIDIA, AMD, Intel), ~2–4 GB VRAM. **Hard constraint: it needs a real GPU** —
  Upscayl, its usual front end, will not run on CPU or an iGPU. That makes it a workstation
  tool, not something to put behind an MCP server that might run anywhere.
- **rembg** remains the practical background remover: one `pip install`, fully local,
  17k+ stars. The licence caveat on its default model is already documented in
  `mini-creative-toolkit` and does not need relitigating.

### 3.3 Honest gap assessment

Against `mini-creative-toolkit`'s existing 23 CPU-first tools, the genuine gaps are
**upscaling** (blocked on the GPU requirement above) and **subtitle burn-in from the local
Whisper transcript** — the latter is pure ffmpeg, has no licence or quota problem, and is the
obvious next tool if one is wanted.

---

## 4. MCP security and the ecosystem

The systematic version of the problem this project already hit by hand: the most-starred
free-image MCP was archived, and the maintained one was a 2-star single-author npm package
that would auto-update on every `npx` run.

### 4.1 The threat landscape is not theoretical

- **30+ CVEs in a single 60-day window.**
- **CVE-2026-33032 (CVSS 9.8)** was actively exploited in a supply-chain attack that
  silently BCC'd emails out of **437,000+ environments**.
- **Tool poisoning is described as the highest-leverage attack on enterprise AI agents in
  2026** — and its mechanism is the important part: it exploits *tool metadata the agent
  reads but a human never sees*. A tool's description is a prompt. Nobody reviews it.
- **Repository pollution:** typosquatting, fake updates injecting code, and manipulated
  schemas that change tool behaviour without changing the tool's name.
- **Configuration poisoning:** insecure defaults and tampered config files.

### 4.2 What the registry does and does not solve

The official MCP registry (still in preview as of July 2026) gives **namespace
verification**: nobody publishes under `io.github.microsoft/…` without authenticating as
that GitHub identity, and nobody claims a reverse-domain namespace without proving control
of the domain. Serious research goes further — **Sigstore keyless signing** to bind
artifacts to audited CI/CD without long-lived keys, and **RFC 8785 JSON canonicalization +
JWS** for per-message integrity of live capability updates.

But the load-bearing sentence is this: *registries improve discovery and provenance;
security approval remains the responsibility of the organisation consuming the server.*

**That gap is exactly `mcp-vet`'s niche** — a registry can tell you who published a server;
it cannot tell you what the code does.

### 4.3 Concrete backlog for mcp-vet

Ordered by leverage, each checkable statically without executing anything:

1. **Tool-description injection.** Scan `inputSchema` descriptions and tool docstrings for
   imperative instructions aimed at the model ("ignore previous", "always call", "do not
   tell the user"). This is the tool-poisoning vector and nothing else is looking at it.
2. **Schema drift between versions.** Flag a tool whose description or schema changed
   without a corresponding change in its implementation — the manipulated-schema attack.
3. **Typosquat distance.** Levenshtein distance from a server or package name to the
   popular names in the ecosystem.
4. **Install-time execution.** `postinstall` hooks, `npx` invocations without a pinned
   version, and anything fetching code at start-up.
5. **Registry provenance status.** Whether the server is namespace-verified in the official
   registry, surfaced as a signal alongside the code findings rather than as a verdict.

Items 1 and 2 have no equivalent in ordinary dependency scanners, because ordinary scanners
do not treat text as executable. In MCP it is.

---

## 5. Sources

**Audio/music:** [Kokoro vs Piper vs XTTS](https://contracollective.com/blog/kokoro-vs-piper-vs-xtts-local-text-to-speech-m5-max-2026) · [local TTS models tested](https://localaimaster.com/blog/best-local-tts-models) · [open-source TTS ranked](https://texttolab.com/blog/open-source-text-to-speech) · [ACE-Step](https://github.com/ace-step/ACE-Step) · [ACE-Step 1.5 guide](https://dev.to/czmilo/ace-step-15-the-complete-2026-guide-to-open-source-ai-music-generation-522e) · [music model licensing](https://www.spheron.network/blog/deploy-open-source-ai-music-generation-gpu-cloud-2026/)

**LLM tiers:** [free LLM APIs compared](https://openrouter.ai/blog/tutorials/free-llm-apis-compared/) · [Groq/Cerebras/GitHub Models](https://wetheflywheel.com/en/ai-model-access/free-llm-api-tiers-2026/) · [tested limits, no credit card](https://tokenmix.ai/blog/free-llm-api) · [13 providers compared](https://klymentiev.com/blog/free-llm-api)

**Post-production:** [local AI upscaling](https://localaimaster.com/blog/ai-image-upscaling-local) · [rembg guide](https://knightli.com/en/2026/04/19/rembg-background-removal-notes/)

**MCP security:** [MCP security vulnerabilities guide](https://aembit.io/blog/the-ultimate-guide-to-mcp-security-vulnerabilities/) · [risks and real incidents](https://checkmarx.com/learn/mcp-security-risks-real-world-incidents-and-security-controls/) · [CSA research note on tool poisoning](https://labs.cloudsecurityalliance.org/research/csa-research-note-mcp-tool-poisoning-auto-execution-20260701/) · [MCP security statistics 2026](https://www.practical-devsecops.com/mcp-security-statistics-2026-report/) · [registry: discover, verify, connect](https://digitalthoughtdisruption.com/2026/07/20/mcp-registry-discover-verify-safely-connect-servers/) · [trustworthy MCP registry (paper)](https://doi.org/10.3390/fi18050243)
