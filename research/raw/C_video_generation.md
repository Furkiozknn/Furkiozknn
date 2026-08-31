# Open-Source Video Generation Landscape (Aug 2026)
### Research for an AI Creative Platform — Image-to-Video / Text-to-Video / AI Video Editing

---

## 0. GitHub Topic Snapshot: `topics/image-to-video`

Source: https://github.com/topics/image-to-video

The topic page's current top repos (by stars) give a good pulse-check of what the community is actively building around:

| Repo | Stars | Note |
|---|---|---|
| [Anil-matcha/Open-Generative-AI](https://github.com/anil-matcha/open-generative-ai) | 27.4k | Aggregator/wrapper app exposing 500+ models (Flux, Kling, Sora-like, Midjourney-style) — not a model itself, MIT licensed self-hosted "studio" |
| [zai-org/CogVideo](https://github.com/zai-org/CogVideo) | 13k | CogVideoX text/image-to-video model family |
| [Lightricks/LTX-Video](https://github.com/Lightricks/LTX-Video) | 10.9k | Fast DiT video model, T2V+I2V |
| [AILab-CVC/VideoCrafter](https://github.com/AILab-CVC/VideoCrafter) | 5.1k | Earlier open video diffusion model, largely superseded |
| [dramaclaw/dramaclaw](https://github.com/dramaclaw/dramaclaw) | 4.8k | End-to-end "script to finished film" AIGC pipeline/orchestrator |
| [Tencent-Hunyuan/HunyuanVideo-1.5](https://github.com/Tencent-Hunyuan/HunyuanVideo-1.5) | 4.5k | Newer, lighter (8.3B) Hunyuan model, T2V+I2V |
| [Robbyant/lingbot-world](https://github.com/Robbyant/lingbot-world) | 4.4k | Open "world model" video generation research |
| [ArcReel/ArcReel](https://github.com/ArcReel/ArcReel) | 4.3k | Self-hosted AI video workspace for storyboards/short-form video |
| [Lightricks/ComfyUI-LTXVideo](https://github.com/Lightricks/ComfyUI-LTXVideo) | 4.1k | Official ComfyUI node pack for LTX-Video |
| [Doubiiu/DynamiCrafter](https://github.com/Doubiiu/DynamiCrafter) | 3k | Open-domain image animation via video diffusion priors (ECCV'24 Oral) |

Other repos surfaced on the page worth noting: `HunyuanVideo-I2V`, `stable-virtual-camera` (camera-controllable NVS/video), `HunyuanWorld-Voyager` (world model + camera control), `PIA` (Personalized Image Animator), `SEINE` (image-to-video + transition generation), `videosos`, `DepthFlow` (depth-based parallax animation from a single image).

By mid-2026 the topic page itself is dominated by **model wrappers/orchestrators built on top of a handful of base models** (Wan, LTX, Hunyuan, CogVideoX) rather than net-new foundation models — confirming the base-model layer has consolidated to a short list, which is good news for a platform deciding what to integrate.

---

## 1. Foundation / Diffusion Video Models

### 1.1 Wan2.1 / Wan2.2 (Alibaba)
- **URL:** https://github.com/Wan-Video/Wan2.2 (supersedes https://github.com/Wan-Video/Wan2.1)
- **One-line:** Alibaba's flagship open video-generation family — currently the strongest fully open, Apache-licensed base model line for both T2V and I2V.
- **Architecture:** Latent video diffusion; Wan2.2 introduces a **Mixture-of-Experts (MoE) DiT** — a high-noise expert for coarse layout in early denoising steps and a low-noise expert for detail refinement later. ~27B total params / ~14B active per step for the A14B models; a lightweight dense 5B model (TI2V-5B) uses a high-compression VAE (16×16×4).
- **Capabilities:** T2V (480p/720p), I2V (480p/720p, preserves aspect ratio), unified hybrid TI2V, **Speech-to-Video** (audio-driven, optional pose control), and **Character Animation/Replacement** (Animate-14B). Wan2.1 also has community/derivative work adding camera-control LoRAs and VACE (video/animate/composite editing).
- **Resolution/Duration:** 480p–720p; 5-second clips are the practical default (TI2V-5B: 5s 720p in <9 min on a consumer GPU).
- **VRAM/inference:** 14B models need ≥80GB VRAM (multi-GPU/offload for less); the 5B TI2V model runs on ≥24GB (RTX 4090-class). FSDP + DeepSpeed Ulysses for distributed inference; `--offload_model`, dtype conversion, and T5-on-CPU flags exist for consumer setups.
- **Deployment:** Official Diffusers pipelines, native ComfyUI support, HF Spaces demos, raw `generate.py` CLI.
- **License:** **Apache 2.0** — fully permissive, no MAU caps, no territory restrictions. This is a major differentiator.
- **Strengths:** Best all-around open quality/feature breadth in 2026 (T2V, I2V, audio-driven, animation) under a truly commercial-friendly license; strong ecosystem (quantized GGUF/FP8 builds, LoRA training tools, ComfyUI-Wan nodes) has grown fast.
- **Weaknesses:** Large models genuinely need datacenter-class GPUs; MoE routing adds engineering complexity for self-hosted serving (need both experts resident); prompt-extension features depend on an external LLM/API (Dashscope) unless self-hosted.
- **Platform relevance:** The single best self-host candidate today if the roadmap includes I2V + camera/character control and the team can afford ≥1×80GB GPU (or lean on the 5B model for a cheaper/faster tier). License removes all commercial-use legal risk.

### 1.2 CogVideoX / CogVideo (Zhipu / Tsinghua, now zai-org)
- **URL:** https://github.com/zai-org/CogVideo
- **One-line:** Diffusion Transformer (DiT) video model family from the ChatGLM/GLM lineage, one of the first well-documented, Diffusers-native open T2V/I2V models.
- **Architecture:** DiT with an "Expert Transformer" design; CogVideoX-2B and -5B, plus a 1.5 upgrade (Nov 2024) supporting higher resolution and longer clips.
- **Capabilities:** T2V, dedicated I2V checkpoints, community V2V via Colab/pipelines.
- **Resolution/Duration:** CogVideoX1.5-5B: 1360×768, 5–10s; CogVideoX-5B-I2V: 768–1360px variable; CogVideoX-2B: 720×480, 6s @ 8fps.
- **VRAM/inference:** 2B model runs from ~5GB VRAM (BF16, optimized) — genuinely consumer-friendly; 5B from ~10GB with optimizations, down to ~3.6–4.4GB with INT8 quantization. ~90s (2B) to ~550s (1.5-5B) per clip on an H100 at 50 steps — i.e. noticeably slower than Wan/LTX per unit of quality.
- **Deployment:** Diffusers (primary), SAT for research, ComfyUI via `ComfyUI-CogVideoXWrapper`, HF Spaces Gradio demo, and a commercial hosted tier (QingYing/Zhipu API) for the larger checkpoints.
- **License:** **Code is Apache 2.0; the 2B model weights are Apache 2.0, but the 5B model uses a separate, more restrictive "CogVideoX License."** Must check the 5B license terms carefully before commercial use — the 2B is the safe, fully-open tier.
- **Strengths:** Lowest VRAM floor of any capable model here (great for a "fast/cheap tier" or edge/on-device experiments); very mature Diffusers integration; large community tooling (RIFLEx for length extrapolation, LeMiCa, VideoTuna).
- **Weaknesses:** English-only prompts; slower wall-clock generation than LTX/Wan-5B for comparable quality; license bifurcation between 2B (open) and 5B (restricted) is an easy trap for a commercial team.
- **Platform relevance:** Good complementary/cheap-tier or fallback model (2B, Apache 2.0) for previews, and a proven, low-friction Diffusers on-ramp if the team wants to self-host something small before committing to Wan/LTX-scale infrastructure.

### 1.3 LTX-Video / LTX-2 (Lightricks)
- **URL:** https://github.com/Lightricks/LTX-Video (companion: https://github.com/Lightricks/ComfyUI-LTXVideo)
- **One-line:** The speed-optimized open DiT video model — built explicitly for fast, near-real-time generation and consumer-hardware deployment, now with a companion desktop editor (LTX-2/2.3, released fully open-source Jan–Mar 2026).
- **Architecture:** "First DiT-based" open video model per its own docs; ships a 13B model (standard + distilled) and a 2B distilled model. Distillation is the core trick enabling its speed.
- **Capabilities:** T2V, I2V, forward/backward **video extension**, **multi-keyframe conditioning**, and IC-LoRA control adapters (depth, pose, canny) for guided/video-to-video style generation.
- **Resolution/Duration:** Up to native 4K (practically best under 720×1280); up to **60 seconds** with the distilled 13B variant, up to 50 fps — the longest native duration of any model surveyed here.
- **VRAM/inference:** Distilled 13B on H100: full-HD clip in ~10s, low-res preview in ~3s — the fastest model in this survey by a wide margin. FP8-quantized/distilled variants can run in ~1GB-class VRAM footprints for smaller configs. TeaCache gives up to 2x further speedup without retraining.
- **Deployment:** ComfyUI (primary, first-class support via Lightricks' own node pack), Diffusers, hosted on fal.ai and Replicate, plus **LTX-Studio** (Lightricks' own browser app) and, as of 2026, a **desktop video editor** running the full pipeline locally.
- **License:** OpenRAIL-M variant explicitly permitting commercial use (verify the exact clause per release, since RAIL licenses can carry use-based restrictions, but Lightricks markets LTX-2 as commercially usable).
- **Strengths:** Best speed/VRAM trade-off of any model surveyed — makes low-latency, interactive "preview then upscale" UX patterns realistic; native long-duration support (60s) is unique; strong first-party ComfyUI + desktop tooling suggests Lightricks is building this as production infrastructure, not just a research drop.
- **Weaknesses:** Distilled variants trade some quality for speed; full 13B (non-distilled) still needs serious VRAM; less "flagship benchmark" prestige than Wan2.2/HunyuanVideo in raw quality comparisons, though the gap has narrowed a lot by 2026.
- **Platform relevance:** The strongest pragmatic pick for a **product-facing, latency-sensitive image-to-video feature** — e.g., quick previews in an editor, or a "fast" generation tier — given real-time-ish speed and native long-clip support.

### 1.4 HunyuanVideo / HunyuanVideo-1.5 (Tencent)
- **URL:** https://github.com/Tencent-Hunyuan/HunyuanVideo, newer: https://github.com/Tencent-Hunyuan/HunyuanVideo-1.5
- **One-line:** Tencent's large-scale (13B, later a lighter 8.3B "1.5") unified video diffusion model, historically benchmarked as beating Runway Gen-3 on some evals at release.
- **Architecture:** "Dual-stream to single-stream" hybrid transformer — video and text tokens are processed in separate streams through early blocks, then concatenated for joint processing. Causal 3D VAE (4x temporal / 8x spatial / 16x channel compression). Uses a Multimodal LLM as the text encoder instead of CLIP/T5, which reportedly helps instruction-following.
- **Capabilities:** T2V (core), I2V via a separate HunyuanVideo-I2V release, community V2V wrappers.
- **Resolution/Duration:** 720p family (720×1280, 1280×720, 960×960) down to 540p; fixed **129-frame** output (~5s).
- **VRAM/inference:** 45GB minimum (544×960), 60GB recommended (720×1280), 80GB for best quality; FP8 quant saves ~10GB. ~1900s per clip on a single GPU at 50 steps (very slow); xDiT multi-GPU (8x) gives 5.64x speedup (~338s).
- **Deployment:** Diffusers, ComfyUI (native + community FP8/V2V wrappers), Replicate API, Gradio.
- **License:** **Tencent Hunyuan Community License Agreement (THCLA)** — permits commercial use with two hard restrictions: (1) a **100M MAU cap** — above that, you must separately request a license from Tencent at their discretion; (2) **geographic exclusion of the EU, UK, and South Korea**. Also prohibits using outputs to train/improve competing AI models. This is materially more restrictive than Apache 2.0 and is a real legal consideration for a growing commercial platform, especially one with EU/UK users.
- **Strengths:** Very strong raw quality and prompt adherence historically (unified MLLM text encoder is a genuine architectural edge); large, active community ecosystem.
- **Weaknesses:** Highest VRAM/latency cost in this survey by a wide margin (impractical to self-host cheaply); the license's MAU cap and EU/UK/KR exclusion make it a poor fit for a platform with EU users or ambitions of scale — this alone likely disqualifies it for many commercial builders.
- **Platform relevance:** Consider only if targeting non-EU/UK/KR markets, staying under 100M MAU, and quality justifies the very high GPU spend — otherwise Wan2.2 covers similar ground with a cleaner license.

### 1.5 Mochi 1 (Genmo)
- **URL:** https://github.com/genmoai/mochi
- **One-line:** Genmo's 10B-parameter open video diffusion model, notable for being one of the largest fully Apache-2.0 open releases at launch (late 2024) and for strong motion/prompt-adherence claims.
- **Architecture:** Asymmetric Diffusion Transformer (AsymmDiT) — the visual stream carries ~4x the parameters of the text stream (asymmetric hidden dims), paired with an AsymmVAE (362M params) achieving 128x compression (8x spatial, 6x temporal). Uses a single T5-XXL for text encoding (simpler than multi-encoder setups).
- **Capabilities:** T2V only at open-source release (no official I2V in the base repo).
- **Resolution/Duration:** 480p max; short clips (~31 frames in reference examples) — noticeably behind Wan/LTX/Hunyuan on both fronts by 2026.
- **VRAM/inference:** ~60GB on a single GPU as shipped; ComfyUI-optimized paths bring this under 20GB.
- **Deployment:** Hugging Face, direct download/torrent, Gradio UI, CLI, native ComfyUI integration.
- **License:** **Apache 2.0** — fully permissive.
- **Strengths:** Clean, permissive license; efficient/hackable architecture; decent motion quality for photorealistic content.
- **Weaknesses:** Capped at 480p, short clips, T2V-only (no native I2V) — by mid-2026 standards this is behind the frontier (Wan2.2/LTX-2/Hunyuan1.5 all do more at higher res). Reportedly weak on animated/stylized content ("optimized for photorealistic content"), with warping on extreme motion.
- **Platform relevance:** Largely superseded for a new build in 2026; worth knowing about as the historical bridge between SVD-era and Wan/LTX-era models, but not a first choice today.

### 1.6 Open-Sora 2.0 (hpcaitech) & Open-Sora-Plan (PKU-YuanGroup)
- **URLs:** https://github.com/hpcaitech/Open-Sora, https://github.com/PKU-YuanGroup/Open-Sora-Plan
- **One-line:** Two independent academic/community efforts to build an open reproduction of OpenAI's Sora; both emphasize training-cost transparency over being the top benchmark model.
- **Architecture (hpcaitech):** 11B transformer, rectified-flow diffusion, spatial-temporal VAE. **Architecture (PKU Plan v1.5):** "Sparse 3D" DiT with sparse attention (~35% speedup vs. dense) plus a high-compression WFVAE (8x8x8).
- **Capabilities:** Both support unified T2V+I2V in one model. hpcaitech's version: 256px/768px, up to 129 frames, multiple aspect ratios. PKU's version: up to 121×576×1024.
- **VRAM:** hpcaitech Open-Sora 2.0 needs ~52.5GB single-GPU (44.3GB with sequence parallelism across GPUs) — heavy for its resolution ceiling.
- **License:** Both **fully open** — hpcaitech is Apache 2.0; PKU's Open-Sora-Plan is MIT.
- **Notable constraint:** As of PKU's v1.5.0 (mid-2025), the flagship checkpoint is trained/inferred **only on Huawei Ascend 910-series NPUs**, with GPU support "coming soon" — a real deployment blocker for a team standardized on NVIDIA/CUDA infra.
- **Strengths:** Fully transparent, reproducible training pipelines (hpcaitech notably documents a ~$200K total training cost, positioning itself as the "cheap to replicate" proof-of-concept); genuinely open licenses.
- **Weaknesses:** Quality trails Wan2.2/LTX-2/HunyuanVideo-1.5 in most comparisons by 2026; resolution capped at 768px; PKU's NPU-only requirement is a hard blocker for most commercial teams; both projects read more as research/community efforts than production-hardened releases.
- **Platform relevance:** Interesting for engineering learning/reference (both projects publish unusually detailed technical reports on data pipeline and VAE design) but not competitive as a production base model versus Wan2.2/LTX-Video today.

### 1.7 AnimateDiff (guoyww)
- **URL:** https://github.com/guoyww/AnimateDiff
- **One-line:** A "motion module" plug-in that turns any existing Stable Diffusion (1.5/SDXL) checkpoint into a video generator — not a standalone foundation model, but an adapter architecture.
- **Architecture:** Three-stage design — a Domain Adapter (reduces visual artifacts), a Motion Module (learns transferable motion, trained on video data, then dropped into any compatible SD checkpoint), and optional **MotionLoRA** adapters specialized for 8 camera movements (pan/zoom/tilt/roll). SparseCtrl adds RGB-image/sketch-based conditioning, effectively enabling I2V-style control.
- **Capabilities:** Turns thousands of existing community SD/SDXL checkpoints and LoRAs (anime, photoreal, art styles) into animators without retraining them; camera-motion LoRAs; sketch/image-guided animation via SparseCtrl.
- **Resolution/Duration:** V3: up to 1024×1024, 16 frames — short clips, clearly below dedicated video-DiT models on length/resolution.
- **VRAM:** ~13GB for SDXL-based inference.
- **License:** **Apache 2.0.**
- **Deployment:** Official Diffusers integration; extremely popular via `ComfyUI-AnimateDiff-Evolved` and the Automatic1111/SD-WebUI extension ecosystem — arguably the most widely deployed open video tool by install count, due to riding on the SD ecosystem.
- **Strengths:** Unmatched style flexibility (any SD/SDXL LoRA/checkpoint "just animates"); tiny incremental footprint (950MB–1.7GB motion modules, ~74MB LoRAs) on top of image models people already have; huge, mature community tooling.
- **Weaknesses:** Flickering artifacts, short clips, lower fidelity than dedicated video-DiT models; not really competitive as a "hero" video generator in 2026, better thought of as a stylization/motion layer.
- **Platform relevance:** Valuable specifically for a **stylized/artistic image-animation feature** (e.g., "animate this illustration in an anime/oil-painting style") where the enormous SD LoRA ecosystem gives instant style breadth that dedicated video-DiT models don't have. Also the reference architecture for CameraCtrl (below).

### 1.8 Stable Video Diffusion — SVD/SVD-XT (Stability AI)
- **URL:** https://github.com/Stability-AI/generative-models
- **One-line:** Stability's 2023 image-to-video diffusion model — historically important as one of the first credible open I2V models, now dated relative to 2025-26 DiT models.
- **Architecture:** Latent video diffusion built on an SD 2.1-derived image encoder plus a temporally-aware "deflickering" decoder.
- **Capabilities:** I2V only. SVD: 14 frames @ 576×1024; SVD-XT: 25 frames, same base architecture fine-tuned longer.
- **License:** **Stability AI Non-Commercial Research Community License** for the original SVD weights — **not usable in a commercial product without a separate Stability commercial license.**
- **Strengths:** Historically significant, simple architecture, still a reasonable teaching/reference example of I2V diffusion.
- **Weaknesses:** Short clips (≤25 frames), capped resolution, non-commercial license, and outclassed on every capability axis by Wan2.2/LTX-Video/CogVideoX in 2026.
- **Platform relevance:** Not recommended for production integration — mainly relevant as the architectural ancestor that shaped later I2V designs (and Stability's SD3/newer video work carries different, sometimes still-restrictive, licensing that should be re-checked before use).

### 1.9 SkyReels-V2 (Skywork AI)
- **URL:** https://github.com/SkyworkAI/SkyReels-V2
- **One-line:** A "Diffusion Forcing Transformer" model built specifically for **autoregressive, effectively infinite-length** video generation with camera-direction control.
- **Architecture:** Diffusion-forcing autoregressive transformer (1.3B/5B/14B variants) — generates video incrementally rather than as one fixed-length denoising pass, which is what enables arbitrarily long output.
- **Capabilities:** T2V, I2V, **infinite-length generation** (documented examples from 10s up to 30s+ by extending frame count), camera-direction control, multi-subject consistency (via companion SkyReels-A2), video extension, start/end-frame conditioning.
- **Resolution/Duration:** 540p (544×960×97 frames) and 720p (720×1280×121 frames) as base units, extended arbitrarily via the autoregressive scheme.
- **VRAM:** 1.3B model: ~14.7GB peak (540p) — quite accessible; 14B model: ~51.2GB peak.
- **License:** Custom `LICENSE.txt` — **must be reviewed carefully**; not confirmed Apache/MIT-equivalent, terms not fully detailed in the repo summary. Treat as restrictive until verified.
- **Deployment:** Hugging Face, ModelScope, single/multi-GPU inference code, xDiT for multi-GPU, a hosted playground at skyreels.ai.
- **Strengths:** Best-in-class approach to **long-form/continuous video** among open models — the autoregressive diffusion-forcing design is architecturally distinct from every other model here and directly addresses the "AI video is always 4-10 seconds" limitation.
- **Weaknesses:** High VRAM at the 14B tier; motion-quality scores reportedly trail resolution/consistency scores in evals; needs careful tuning for long sequences; license clarity is a blocker to resolve before commercial commitment.
- **Platform relevance:** The most interesting model for a platform that wants to offer **longer-form clips or "extend this video" functionality** rather than fixed 4-10s outputs — but license terms need direct legal review before any commercial integration.

---

## 2. AI Video Editing / Node-Based Workflow & Post-Processing Tools

### 2.1 ComfyUI (comfyanonymous)
- **URL:** https://github.com/comfyanonymous/ComfyUI
- **One-line:** The de facto standard node-graph GUI/API/backend for running diffusion models (image, video, 3D, audio) — the "IDE" of open generative AI.
- **Architecture:** Graph/node execution engine with async queueing, partial re-execution of only-changed graph nodes, and smart VRAM/RAM offload management; workflows are serializable JSON, which is what makes it embeddable as a backend rather than just a desktop app.
- **Video model support:** First-class/native nodes for **Wan 2.1/2.2, LTX-Video 2/2.3, HunyuanVideo 1.5, CogVideoX, Kandinsky 5 Video**, with more added via community/partner custom nodes almost immediately after any new model drops.
- **License:** **GPL-3.0.** Important nuance for a commercial product: GPL-3.0 governs the ComfyUI *application/engine* code; running it as an internal backend service (not distributing modified ComfyUI source to end users) is generally fine, but bundling/distributing a modified ComfyUI binary inside a commercial closed product requires GPL compliance review.
- **Deployment:** Self-hosted server with a REST/WebSocket API for programmatic control — the standard way production apps proxy user requests into a diffusion backend without building CUDA orchestration from scratch.
- **Platform relevance:** This is less "a competing product" and more **the likely backend runtime** for any self-hosted piece of the platform's video pipeline — it already solves model loading/offloading, workflow chaining (e.g., generate → upscale → interpolate → encode), and has day-one support for every serious open video model. Building custom nodes for the platform's specific pipeline (prompt templating, brand LoRAs, output format constraints) on top of ComfyUI is a well-trodden path many production AI video startups (Krea, Leonardo-style tools) actually follow.

### 2.2 RIFE (hzwer/ECCV2022-RIFE, "Practical-RIFE")
- **URL:** https://github.com/hzwer/ECCV2022-RIFE
- **One-line:** Fast, optical-flow-based real-time video frame interpolation — the standard tool for turning low-fps AI video output into smooth 24/30/60fps footage.
- **Architecture:** Intermediate flow estimation network (not a full diffusion model) — deliberately lightweight for speed.
- **Performance:** 30+ FPS for 2x interpolation at 720p on a 2080Ti — extremely cheap relative to the video generation step itself.
- **License:** **MIT.**
- **Deployment:** Standalone Python/PyTorch, Docker images, and widely wrapped into third-party interpolation GUIs (FlowFrames, SVFI) and video pipelines.
- **Platform relevance:** A near-mandatory post-processing step for any I2V/T2V product — base video-DiT models mostly output 16-24fps at 5-10s; RIFE is the standard cheap way to (a) smooth motion and (b) synthesize higher perceived frame rate/slow-motion without re-running the expensive generation model. MIT license makes it trivially safe to bundle.

### 2.3 FILM — Frame Interpolation for Large Motion (Google Research)
- **URL:** https://github.com/google-research/frame-interpolation
- **One-line:** Google's single-network frame interpolation model, particularly strong on **large motion** (vs. RIFE's strength on speed/small motion).
- **Architecture:** Unified network with a shared multi-scale feature extractor — no dependency on pretrained optical flow/depth models, trained end-to-end from frame triplets.
- **License:** **Apache 2.0.**
- **Status:** Repo is **archived (Oct 2025)** — no active maintenance, a real consideration for long-term dependency planning.
- **Platform relevance:** Good quality reference/fallback for large-motion interpolation cases where RIFE artifacts, but the archived status means the platform would be inheriting unmaintained code — reasonable to vendor a frozen copy but not to rely on upstream fixes.

### 2.4 CameraCtrl (hehao13)
- **URL:** https://github.com/hehao13/CameraCtrl
- **One-line:** Adds precise, frame-by-frame camera trajectory control (pans, zooms, orbits) on top of AnimateDiff/SD1.5-based video generation.
- **Architecture:** A dedicated camera-control adapter module trained on RealEstate10K camera-pose annotations, layered onto AnimateDiffV3's motion module and an SD1.5 (or stylized LoRA, e.g. Realistic Vision/ToonYou) base.
- **License:** **Apache 2.0.**
- **Capabilities/limits:** Works across photoreal and stylized domains; demonstrated training used 8 GPUs; inference requires careful multi-component setup (base model + motion module + camera adapter).
- **Platform relevance:** A concrete open reference for how to bolt **camera-motion control** onto a video pipeline via an adapter rather than retraining a whole foundation model — directly useful as a design pattern even if the platform ultimately implements camera control against Wan2.2/LTX-Video instead of the older SD1.5/AnimateDiff stack (Wan2.2/SkyReels-V2 both have their own native or community camera-control paths, which are the more modern equivalents of this idea).

---

## 3. How the Landscape Breaks Down

- **Frontier open base models (2025-26):** Wan2.2 > LTX-2/2.3 ≈ HunyuanVideo-1.5 > CogVideoX/SkyReels-V2 in general quality mindshare, but each wins on a different axis — Wan2.2 on capability breadth + license, LTX-2 on speed + duration, HunyuanVideo on raw fidelity (with license cost), SkyReels-V2 on infinite-length generation.
- **License is the single biggest differentiator for a commercial product**, more than raw benchmark quality: Apache 2.0 (Wan2.2, CogVideoX-2B, Mochi 1, Open-Sora, Open-Sora-Plan, AnimateDiff, CameraCtrl, FILM) vs. custom/restrictive (HunyuanVideo's 100M-MAU-cap + EU/UK/KR exclusion, SVD's non-commercial research license, CogVideoX-5B's separate license, SkyReels-V2's unverified custom license).
- **Editing/post-processing tools (ComfyUI, RIFE, FILM, CameraCtrl) are commodity infrastructure** at this point — the real product differentiation for a new platform is in orchestration (prompt engineering, model routing, editing UX, consistency across shots) rather than which base model is used, since ComfyUI can swap models behind one workflow graph.

---

## 4. Synthesis — Practical Recommendation for a Commercial Product (Aug 2026)

### Most practical models/approaches, ranked
1. **Wan2.2 (Apache 2.0)** — the default self-host choice. Broadest capability set (T2V/I2V/TI2V/S2V/animation) under a fully clean commercial license. Use the 5B TI2V model for a fast/cheap tier on single high-end consumer GPUs, and the 14B A14B MoE models on ≥80GB datacenter GPUs for a premium tier.
2. **LTX-Video/LTX-2.3 (OpenRAIL-M, commercial-permitting)** — best choice for **low-latency, interactive** experiences (in-editor previews, "generate in seconds" UX) and for **longer clips** (native 60s support) without the VRAM bill of Wan's larger tier. Pair with its first-party ComfyUI nodes.
3. **CogVideoX-2B (Apache 2.0)** — cheapest self-host fallback/edge tier; useful when the product needs to run on minimal GPU budget (~5GB VRAM) for free-tier users or quick drafts, with paid users routed to Wan2.2/LTX-2 for full quality. (Avoid the 5B checkpoint's separate license unless verified acceptable.)
4. **A hosted API (fal.ai or Replicate) as the primary launch path, not a self-hosted model, for the first 6-12 months.** As of 2026, fal.ai/Replicate already host Wan, LTX, and Hunyuan behind a metered API (roughly $0.05-$0.15/sec for Wan-class quality), which removes the GPU-ops burden (provisioning, queueing, autoscaling, model updates) entirely during early product-market-fit. This is the pragmatic default for a *new* platform: call fal.ai/Replicate for Wan2.2/LTX-2 inference at launch, and only invest in self-hosting (via ComfyUI + owned GPUs) once volume makes the per-second API cost exceed dedicated-GPU amortized cost — a threshold most teams cross in the tens-of-thousands-of-clips/month range.
5. **RIFE (MIT) as a mandatory, cheap post-processing step**, self-hosted regardless of whether the core generation is via API or self-hosted model — interpolating a 16-24fps generated clip to 30/60fps is inexpensive and meaningfully improves perceived quality for near-zero marginal cost.

### Recommended integration strategy
- **Phase 1 (launch):** Route all generation through a hosted API aggregator (fal.ai and/or Replicate) offering Wan2.2 and LTX-2 endpoints. Build the platform's own orchestration layer (prompt templates, queueing, moderation, billing) independent of the specific backend so models can be swapped later — this is the standard "don't build GPU ops before you have PMF" pattern.
- **Phase 2 (scale):** Stand up a self-hosted ComfyUI-based inference cluster (GPL-3.0 backend, used internally — not redistributed — so no GPL-compliance conflict with a closed commercial frontend) running Wan2.2 (broad features) and LTX-2 (fast tier) once volume justifies the GPU capex; keep RIFE and (optionally) a frozen FILM copy as local post-processing regardless of where generation happens.
- **Phase 3 (differentiation):** Invest platform-specific engineering in things the base models don't solve out of the box — shot-to-shot character/style consistency, camera-control UX (informed by CameraCtrl's adapter pattern and Wan2.2/SkyReels-V2's native camera controls), and longer-form continuity (SkyReels-V2's diffusion-forcing approach, once its license is confirmed, or LTX-2's native 60s support) — since the base T2V/I2V generation step itself is rapidly becoming commoditized across providers.

### Rejected candidates and why
- **HunyuanVideo / HunyuanVideo-1.5 (Tencent):** Strong quality, but the **100M MAU cap** (requiring Tencent's discretionary approval above that) and **EU/UK/South Korea exclusion** in the license make it a legal liability for a platform aiming at global scale or EU users. Rejected for core infrastructure; could be *evaluated* later for non-EU/UK/KR markets under 100M MAU if quality differentiation is proven to matter, but not a launch choice.
- **Stable Video Diffusion (SVD/SVD-XT):** Non-commercial research license outright blocks commercial use of the original weights; also outclassed technically (short clips, low res) by every 2025-26 model surveyed. Rejected outright for production; only useful as an architectural reference.
- **CogVideoX-5B:** The 2B tier is fine (Apache 2.0), but the 5B model's separate, more restrictive license and slower wall-clock generation (vs. Wan/LTX at similar quality) make it a weaker pick than Wan2.2/LTX-2 for the mid/premium tier. Rejected in favor of Wan2.2 for the higher tier and CogVideoX-2B (only) for the cheap tier.
- **Mochi 1 (Genmo):** Clean Apache 2.0 license, but capped at 480p, T2V-only (no native I2V), and reportedly weak on stylized/animated content — behind the 2026 frontier on every capability axis needed for an I2V-centric product. Rejected as superseded.
- **Open-Sora 2.0 / Open-Sora-Plan:** Fully open licenses (Apache 2.0 / MIT) and valuable as transparent research references, but quality trails the frontier and PKU's flagship checkpoint is Ascend-NPU-only (no GPU support at time of research), a hard deployment blocker for a CUDA-standardized stack. Rejected for production; worth revisiting if/when GPU support ships and benchmarks close the gap.
- **AnimateDiff:** Not rejected outright — it's the right tool for a specific niche (stylized image animation riding the SD LoRA ecosystem) rather than a general-purpose video generator, so it's recommended as a **secondary/stylization feature**, not the core video engine.
- **SkyReels-V2:** Not rejected on technical merit (its infinite-length approach is genuinely differentiated) but flagged as **license-unverified** — hold pending legal review of its custom `LICENSE.txt` before any commercial commitment; re-evaluate for the "extend/long-form video" feature once terms are confirmed acceptable.
- **VideoCrafter, PIA, SEINE, DynamiCrafter (earlier open-domain image animators):** Historically important and still functional, but superseded in quality/features by Wan2.2/LTX-2/CogVideoX by 2026; not worth new integration effort, though DynamiCrafter's "animating open-domain images" framing is a useful conceptual reference for I2V UX (e.g., handling arbitrary user-uploaded photos rather than curated inputs).

---

## Sources
- https://github.com/topics/image-to-video
- https://github.com/Wan-Video/Wan2.2
- https://github.com/Wan-Video/Wan2.1
- https://github.com/zai-org/CogVideo
- https://github.com/Lightricks/LTX-Video
- https://github.com/Lightricks/ComfyUI-LTXVideo
- https://github.com/Tencent-Hunyuan/HunyuanVideo
- https://github.com/Tencent-Hunyuan/HunyuanVideo-1.5
- https://github.com/Tencent-Hunyuan/HunyuanVideo-1.5/blob/main/LICENSE
- https://github.com/genmoai/mochi
- https://github.com/hpcaitech/Open-Sora
- https://github.com/PKU-YuanGroup/Open-Sora-Plan
- https://github.com/guoyww/AnimateDiff
- https://github.com/Stability-AI/generative-models
- https://github.com/SkyworkAI/SkyReels-V2
- https://github.com/comfyanonymous/ComfyUI
- https://github.com/hzwer/ECCV2022-RIFE
- https://github.com/google-research/frame-interpolation
- https://github.com/hehao13/CameraCtrl
- https://www.siliconflow.com/articles/best-open-source-text-to-video-models
- https://videodubber.ai/blogs/best-opensource-ai-video-generator-2026/
- https://www.buildfastwithai.com/ai-tools/fal-ai
- https://techsy.io/en/blog/best-ai-video-providers
- https://www.buildmvpfast.com/api-costs/ai-video
