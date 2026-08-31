# Open-Source Lip-Sync & Talking-Head / Dubbing Landscape (Aug 2026)

Research pass for an AI creative platform's lip-sync / dubbing feature. Sources: GitHub topic page, individual repo READMEs (fetched directly), and web search for 2025-2026 diffusion-based and real-time work.

---

## 1. GitHub Topic Snapshot — `github.com/topics/lipsync`

Top hits on the topic page (name — stars — one-liner):

| Repo | Stars | Note |
|---|---|---|
| [facefusion/facefusion](https://github.com/facefusion/facefusion) | 29.7k | Face-manipulation platform (swap + lip-sync module) |
| [bytedance/LatentSync](https://github.com/bytedance/LatentSync) | 6k | Stable-Diffusion-based lip sync |
| [numz/sd-wav2lip-uhq](https://github.com/numz/sd-wav2lip-uhq) | 1.4k | Wav2Lip-UHQ extension for Automatic1111 |
| [SamKhoze/ComfyUI-DeepFuze](https://github.com/SamKhoze/ComfyUI-DeepFuze) | 461 | Face transform + lip-sync ComfyUI nodes |
| [yuvraj108c/ComfyUI-FLOAT](https://github.com/yuvraj108c/ComfyUI-FLOAT) | 271 | ComfyUI wrapper for FLOAT (flow-matching talking portrait) |
| [instant-high/wav2lip-onnx-HQ](https://github.com/instant-high/wav2lip-onnx-HQ) | 160 | ONNX Wav2Lip + face alignment/enhancement |
| [mowshon/lipsync](https://github.com/mowshon/lipsync) | 152 | Maintained Python wrapper around Wav2Lip |
| [AaronComo/LipFD](https://github.com/AaronComo/LipFD) | 139 | NeurIPS'24 — *detects* lip-sync deepfakes (adversarial-relevant) |
| [indianajson/wav2lip-HD](https://github.com/indianajson/wav2lip-HD) | 132 | Wav2Lip + GFPGAN upscale, marketed as TrueSync alternative |

Notably absent from the topic tag itself (they're tagged under "talking-head"/"deepfake"/"digital-human" instead) but essential to this space: SadTalker, MuseTalk, VideoReTalking, DINet, DreamTalk, EchoMimic, Hallo, Ditto, LivePortrait — covered below via direct/independent research as the task requested.

---

## 2. Core Projects (Deep Dive)

### 2.1 Wav2Lip
- **URL:** https://github.com/Rudrabha/Wav2Lip
- **One-liner:** The foundational "put any audio onto any talking face video" model; still the most forked/deployed lip-sync baseline in the ecosystem.
- **Technique:** GAN-based. A pretrained lip-sync **expert discriminator** (trained on LRS2) scores audio-visual sync; the generator is trained against it plus a visual-quality discriminator. No 3D/landmark intermediate — direct video-frame generation conditioned on a mel-spectrogram window.
- **Stack:** PyTorch, S3FD face detector, FFmpeg. Python 3.6+.
- **I/O:** Video (any face video) + arbitrary audio (any language, even singing/TTS) → MP4 with re-synced lips, identity/background otherwise untouched.
- **Real-time vs offline:** Offline only in the open release. A hosted commercial version (sync.so) claims much faster/near-real-time turnaround.
- **Quality:** Best around 96×96–720p mouth crops; famous for a soft/blurred mouth region and visible seam/blending artifacts, especially at extreme angles or fast speech. Identity (rest of face) is well preserved since only the mouth region is regenerated.
- **License:** Non-commercial/research only per the original authors' terms; commercial use requires directly contacting them. **This is the single biggest practical blocker** for a commercial product building directly on the original weights.
- **Strengths:** Battle-tested, huge community, dozens of forks fixing quality (GFPGAN/GPEN enhancement, ONNX export, face-parsing masks), cheap to run, works on arbitrary identities without fine-tuning.
- **Weaknesses:** License; blurry/low-res mouth; no head-pose or expression modeling (pure lip-region patch); needs padding/smoothing hand-tuning per video.
- **Platform relevance:** Good reference architecture and a useful "cheap fallback" tier, but the license means any production use must go through a licensed fork/derivative (see `mowshon/lipsync`, `wav2lip-onnx-HQ`) with independently clarified terms, or a hosted API (sync.so, and similar), not the original weights directly.

### 2.2 SadTalker
- **URL:** https://github.com/OpenTalker/SadTalker
- **One-liner:** Single portrait photo + audio → full talking-head video (head pose + expression + lips), not just mouth patching.
- **Technique:** Audio-to-motion via learned 3D Morphable Model (3DMM) coefficients: ExpNet generates expression coefficients, PoseVAE generates head-pose coefficients, a MappingNet composes them, and a face-vid2vid-style renderer turns coefficients back into video. Effectively **landmark/3DMM-driven**, diffusion-free.
- **Stack:** PyTorch 1.12, 3DMM extraction, Wav2Lip used internally for a lip-refinement pass, GFPGAN for face enhancement, Gradio UI.
- **I/O:** Single image (or short video) + WAV → MP4 talking head with pose/expression.
- **Real-time vs offline:** Offline; GPU strongly recommended, CPU works but slow.
- **Quality:** 256px native, 512px "beta"; identity preserved well since it's driven from the same source image, but resolution and fine detail (teeth, hair motion) are limited; can look "animatronic" on large head movements.
- **License:** **Apache-2.0** — genuinely commercial-friendly (upgraded from an earlier non-commercial stance), a real differentiator vs. Wav2Lip.
- **Strengths:** True single-image avatar generation (no driving video needed), permissive license, CVPR 2023 pedigree, huge community/ports (Colab, HF Spaces, Discord bots).
- **Weaknesses:** Resolution ceiling, occasional identity drift on extreme poses, install complexity (many pinned deps), not real-time.
- **Platform relevance:** A strong "photo-to-avatar" onboarding feature (no video capture needed from the user) — different use case from re-dubbing existing footage. Good complementary feature alongside a video-to-video lip-sync engine.
- **Differentiator:** Unlike Wav2Lip/LatentSync/VideoReTalking, SadTalker's input is a **still image**, not an existing talking video — it's a generation task, not a re-sync task.

### 2.3 MuseTalk (Tencent)
- **URL:** https://github.com/TMElyralab/MuseTalk
- **One-liner:** Real-time-capable latent-space lip-sync for existing video, positioned for live/virtual-human dubbing.
- **Technique:** Not a full diffusion sampler — a **latent-space inpainting model**: VAE encodes the face region, Whisper-tiny encodes audio, and a Stable-Diffusion-derived UNet with cross-attention fuses audio into the latent and inpaints the mouth region in one forward pass (no multi-step denoising loop), which is what enables its speed.
- **Stack:** PyTorch 2.0.1, CUDA 11.7, Whisper (audio), DWPose (pose/keypoints), FFmpeg, Gradio.
- **I/O:** Video (256×256 face crop) + audio (Chinese/English/Japanese demonstrated) → synced video.
- **Real-time vs offline:** Both — the standout in this list for **real-time streaming inference** (reported 30fps+ on an NVIDIA V100 after a short prep/caching phase). Also usable in pure offline batch mode.
- **Hardware:** Runs on modest cards for fp16 (as low as ~4GB, e.g., RTX 3050 Ti, generating an 8s clip in ~5 min in that constrained mode); training is heavy (74–85GB, i.e., multi-A100/H20 territory) but inference is the relevant number for a product.
- **Quality:** Capped at 256×256 working resolution; single-frame (non-temporal) generation causes visible frame-to-frame jitter; fine identity details (mustache, exact lip color/texture) are not perfectly preserved.
- **License:** **MIT for code**, models usable commercially — one of the most commercially permissive options here (upstream deps like Whisper/DWPose carry their own separate but generally permissive licenses).
- **Strengths:** Real-time, permissive license, multilingual, part of a broader open virtual-human stack (pairs with MuseV for full body/motion), active Tencent-backed development (v1.5 released 2025).
- **Weaknesses:** 256px ceiling, jitter, needs a `bbox_shift` tuning step per identity to avoid over/under-shooting mouth motion.
- **Platform relevance:** Currently the **strongest self-hostable candidate for a live/near-real-time dubbing or lip-sync preview feature**, and its MIT license removes the legal ambiguity that plagues Wav2Lip-derived stacks.

### 2.4 LatentSync (ByteDance)
- **URL:** https://github.com/bytedance/LatentSync
- **One-liner:** "Taming Stable Diffusion for Lip Sync" — full diffusion-based, no intermediate 3D/landmark representation, currently the highest-quality open lip-sync model by community consensus.
- **Technique:** **End-to-end audio-conditioned latent diffusion.** Whisper embeddings are injected into a Stable-Diffusion UNet (AnimateDiff-derived temporal layers) via cross-attention; TREPA-style temporal consistency losses reduce flicker; PySceneDetect + InsightFace handle preprocessing/face alignment.
- **Stack:** Stable Diffusion base, Whisper, AnimateDiff, InsightFace, PySceneDetect, PyTorch.
- **I/O:** Video + audio → lip-synced video.
- **Real-time vs offline:** Offline only — diffusion sampling (20-50 steps) is inherently multi-pass; a "speed vs quality" knob exists via step count but it's not remotely real-time.
- **Hardware:** 8-18GB VRAM for inference (varies by version/resolution); training is heavier (23-55GB depending on stage/resolution). Consumer 12-24GB GPUs (3090/4090) are viable for inference.
- **Quality:** v1.5/1.6 moved to 512×512 training resolution specifically to fix an earlier "blurriness problem," and improved temporal consistency — currently regarded as producing the sharpest, most artifact-free mouths of the open models, at the cost of speed.
- **License:** **Apache-2.0** — commercial-friendly, full training code released.
- **Strengths:** Best visual quality in the open-source tier; actively maintained by ByteDance with real version iteration (1.0 → 1.5 → 1.6); strong community adoption already (used inside other pipelines like `video-translator`).
- **Weaknesses:** Slowest of the mainstream options (diffusion steps), highest VRAM floor, heavier preprocessing pipeline (scene detection, face alignment, quality filtering) before you can even run inference.
- **Platform relevance:** Best candidate for a **"high-quality/offline render" tier** — e.g., a "Pro" export mode — while a faster model handles live preview.
- **Differentiator vs MuseTalk:** Both are Stable-Diffusion-derived, but MuseTalk sacrifices the iterative diffusion process (single-pass latent inpainting) for speed, while LatentSync keeps full diffusion sampling for quality. This is effectively the core speed/quality axis of the whole category.

### 2.5 VideoReTalking
- **URL:** https://github.com/OpenTalker/video-retalking
- **One-liner:** Full pipeline for editing an existing talking-head video's lips *and* expression to new audio (e.g., changing tone from neutral to smiling/angry) — from the same OpenTalker group as SadTalker.
- **Technique:** Three-stage, learning-based, no diffusion: (1) expression normalization to a canonical neutral template, (2) audio-driven lip generation, (3) GAN-based face enhancement for photorealism restoration.
- **Stack:** PyTorch (CUDA 11.1), FFmpeg, multiple pretrained sub-networks per stage.
- **I/O:** Existing talking video + new audio → re-synced, enhanced video.
- **Real-time vs offline:** Offline, multi-stage pipeline (heavier than a single-model approach).
- **Quality:** Handles "in the wild" unconstrained video without manual keypoint alignment — a genuine strength — but explicitly **cannot handle extreme head poses** (its own documented limitation).
- **License:** Apache-2.0.
- **Strengths:** Fully automated (no manual landmark work required from the user), SIGGRAPH Asia 2022 pedigree, built-in expression re-styling is a genuinely unique feature (not just lip patching).
- **Weaknesses:** Pose-angle limits, three separate pretrained sub-models to maintain/version, heavier compute than single-stage approaches, project has slowed in commits/maintenance since ~2023 relative to MuseTalk/LatentSync.
- **Platform relevance:** The expression-normalization idea (retarget to neutral, then resynthesize) is worth borrowing conceptually for dubbing use cases where the source performance's mouth shape actively conflicts with the new language's visemes.

### 2.6 DINet
- **URL:** https://github.com/MRzzm/DINet
- **One-liner:** "Deformation Inpainting Network" for high-resolution facial dubbing via spatial deformation + inpainting rather than direct pixel generation.
- **Technique:** Coarse-to-fine training combining perceptual loss, GAN loss, and an audio-visual sync loss; deforms the facial region (via a learned deformation field, similar in spirit to first-order-motion-model) then inpaints missing texture. Landmark-driven (uses OpenFace landmarks + DeepSpeech audio features as conditioning, not raw waveform/Whisper).
- **Stack:** PyTorch, OpenFace (landmarks), DeepSpeech (audio features), borrows components from AdaAT and AD-NeRF.
- **I/O:** Video + facial landmarks (CSV) + WAV → dubbed video.
- **Real-time vs offline:** Offline; heavy preprocessing (external landmark extraction is a separate step, not integrated).
- **Quality:** Generalizes poorly outside its training distribution (HDTF, 363 videos, "normal lighting, frontal view" only) — per-identity fine-tuning is effectively required for good results on new subjects, which is a meaningful integration cost.
- **License:** Not specified in the repo (defaults to full copyright — **not safe for commercial use as-is**).
- **Strengths:** Progressive/scalable architecture supports arbitrary output resolution in principle; full training code released.
- **Weaknesses:** Weak zero-shot generalization, older/more fragmented preprocessing stack (OpenFace + DeepSpeech are both showing their age vs. modern Whisper-based audio encoders), unclear license, and the project has seen little activity in the last couple of years.
- **Platform relevance:** Largely of historical/architectural interest now — its deformation+inpainting idea predates and partially inspired newer inpainting-style approaches (MuseTalk). Not recommended to build on directly.

### 2.7 DreamTalk
- **URL:** https://github.com/ali-vilab/dreamtalk (Alibaba)
- **One-liner:** Diffusion-based expressive talking-head generation with an explicit "style" control (multiple speaking styles from a reference clip).
- **Technique:** Diffusion model operating over 3DMM parameter space (not raw pixels) conditioned on audio (wav2vec2.0) and a style/reference clip via PIRenderer as the final neural renderer.
- **Stack:** PyTorch 1.8, wav2vec2.0, PIRenderer, dlib, HF Transformers.
- **I/O:** Audio (wav/mp3/m4a/mp4, incl. singing/noisy audio) + portrait image + reference style clip → MP4.
- **Real-time vs offline:** Offline; optional super-resolution passes are notably slow (CodeFormer ~1fps).
- **Quality:** Good expression diversity and robustness to out-of-domain/non-frontal-ish portraits and unusual audio (singing, noise) — a genuine strength versus most peers which assume clean speech. Native resolution is only 256×256, and applying super-resolution can flatten emotional intensity.
- **License:** Code MIT, but **checkpoints are gated to "academic research purposes"** and require an email request — a real deployment blocker despite the permissive code license.
- **Strengths:** Style/emotion control is a differentiated feature most competitors lack; robust to noisy/musical audio.
- **Weaknesses:** Checkpoint licensing friction, low native resolution, manual 3DMM reference-parameter extraction step adds pipeline complexity.
- **Platform relevance:** The "style-conditioned" idea (drive expression intensity/style separately from lip content) is a good product feature to design toward, even if this exact repo isn't the implementation to ship.

### 2.8 EchoMimic (Ant Group / Alipay)
- **URL:** https://github.com/antgroup/echomimic
- **One-liner:** Audio- (and optionally pose-) driven portrait/half-body animation with editable landmark conditioning, part of Ant Group's open digital-human stack.
- **Technique:** Diffusion-based (Stable Diffusion VAE + AnimateDiff-style temporal layers), conditioned on Whisper audio features plus **editable facial landmarks**, with an optional pose-video input for combined audio+pose driving (useful for full upper-body avatars, not just a face crop).
- **Stack:** PyTorch/diffusion, Whisper, FFmpeg, Gradio/WebUI, ComfyUI nodes available.
- **I/O:** Portrait image + audio (+ optional pose video) → animated video (240+ frames typical clip length).
- **Real-time vs offline:** Offline. Standard inference ~7 min for 240 frames on a V100; distilled/accelerated checkpoints cut this to ~50s (10x speedup) — notable because it shows the same diffusion-distillation trend seen across the field in 2025.
- **Hardware:** 16GB+ VRAM recommended; tested on V100 (16GB) up to A100 (80GB); RTX 4090 (24GB) also supported.
- **Quality:** Good expressiveness from the editable-landmark control; multiple driving modes (audio-only / pose+audio / pose-only) give flexibility other single-mode models lack.
- **License:** **Apache-2.0**, permissive. (Repo carries a standard responsible-use disclaimer about deepfake misuse, which is boilerplate across this category, not a licensing restriction.)
- **Strengths:** V1→V3 active iteration, distilled fast-inference variants, flexible multi-modal driving signals, full upper-body option (not face-only).
- **Weaknesses:** Still fundamentally offline/batch even with distillation; VRAM floor excludes lower-end hardware; documentation is Chinese-community-heavy which can slow Western integration.
- **Platform relevance:** The distilled "fast checkpoint" pattern (train a many-step diffusion teacher, ship a few-step distilled student) is exactly the technique to watch for turning any of these diffusion models into something closer to real-time — this is the same idea behind Ditto/REST/Lip-Forcing found in the 2025-2026 literature search below.

### 2.9 Hallo (Fudan University)
- **URL:** https://github.com/fudan-generative-vision/hallo
- **One-liner:** Hierarchical audio-driven portrait animation aiming for high visual fidelity and strong lip-sync from a single square portrait.
- **Technique:** Diffusion-based, wav2vec2 audio embeddings, MediaPipe for facial landmark guidance, Stable Diffusion v1.5 + AnimateDiff motion module as the generative backbone, InsightFace for identity-consistency conditioning.
- **Stack:** PyTorch, CUDA 12.1, Hugging Face Accelerate, Kim Vocal 2 (vocal source separation, useful for noisy/music-backed audio).
- **I/O:** Square portrait (face 50-70% of frame, <30° rotation) + **English** WAV → MP4.
- **Real-time vs offline:** Offline batch; tested/tuned around A100-class hardware.
- **Quality:** Strong lip-sync and realism praised by the community; explicit limitations are documented: English-audio-only support, side-profile faces unsupported, and a known frame-loss bug in outputs plus audio-volume sensitivity affecting results — i.e., real robustness gaps for a multi-language dubbing product.
- **License:** MIT.
- **Strengths:** High output quality, comprehensive released training code, large community ecosystem (Windows ports, ComfyUI, WebUI variants), Hallo2/Hallo3 follow-ups extend to longer/4K-ish generation.
- **Weaknesses:** English-only in the base release (a real problem for a dubbing-focused product needing multilingual support without extra work), heavy compute, known bugs (frame loss, volume sensitivity).
- **Platform relevance:** Good quality bar to benchmark against; the vocal-separation preprocessing step (Kim Vocal 2) is a good idea to borrow for any pipeline that must dub over videos with background music.

---

## 3. Additional / 2025-2026 Real-Time & Adjacent Techniques

Beyond the eight core deep-dives, these are directly relevant and came up strongly in both the topic page and web search for "2025-2026 diffusion talking-head":

- **FLOAT** (DeepBrain AI Research, ICCV 2025) — https://github.com/deepbrainai-research/float. Moves the diffusion/flow process from **pixel space into a learned motion-latent space**, using flow matching (not classic denoising diffusion) with a transformer vector-field predictor. Reported to beat prior diffusion methods on speed *and* quality with fewer sampling steps. **License: non-commercial only** (explicitly stated) — good to study, not to ship on directly. ComfyUI wrappers exist (`yuvraj108c/ComfyUI-FLOAT`, `set-soft/ComfyUI-FLOAT_Optimized`) for prototyping.
- **Ditto (Motion-Space Diffusion)** (Ant Group) — https://github.com/antgroup/ditto-talkinghead. Also motion-space (not pixel-space) diffusion, HuBERT audio features, and ships **explicit online/streaming config files** alongside offline ones — one of the few repos in this space with a real streaming inference mode out of the box. TensorRT-optimized for Ampere GPUs. **License: Apache-2.0** — commercially usable and worth prototyping seriously for a "live preview" feature.
- **LivePortrait** (Kuaishou) — https://github.com/KwaiVGI/LivePortrait. Not audio-driven — it's **video-to-video motion transfer/reenactment** (a driving video's motion is retargeted onto a source portrait). 19k+ stars, used in production at Kuaishou/Douyin, and community forks (`video-translator`) use it as the "cinema-quality HD" step in a dubbing pipeline after a separate audio-to-motion or Wav2Lip pass. Useful as a **post-processing upscale/stabilization layer** on top of a lower-res lip-sync model rather than as the lip-sync engine itself. License unclear from README — verify the LICENSE file before commercial use.
- **FaceFusion** — https://github.com/facefusion/facefusion (29.7k stars, by far the most-starred repo on the topic page). Primarily a **face-swap** platform with lip-sync as one of its manipulation modules; well-built job-queue/CLI/GUI tooling. License is OpenRAIL-AS (behavioral-use restrictions, not a blanket non-commercial ban), but its core focus (identity swapping) is a different product surface than dubbing/lip-sync-only, and OpenRAIL's responsible-use clauses need legal review before commercial packaging.
- **Literature trend (2025-2026, not yet stable/starred repos):** REST (ID-context caching + streaming distillation), IF-MDM, TalkingMachines (autoregressive video-diffusion, FaceTime-style), Lip Forcing (few-step autoregressive diffusion for real-time sync) — all arXiv-stage work as of the search, signaling the field's clear direction: **distill multi-step diffusion talking-head models into few-step or autoregressive real-time variants.** None of these have a mature, widely-adopted open-source repo yet as of Aug 2026; worth revisiting in 6-12 months. See the community-curated survey lists [Kedreamix/Awesome-Talking-Head-Synthesis](https://github.com/Kedreamix/Awesome-Talking-Head-Synthesis) and [harlanhong/awesome-talking-head-generation](https://github.com/harlanhong/awesome-talking-head-generation) for ongoing tracking.

---

## 4. Open Dubbing / Translation-with-Lip-Sync Pipelines

These wrap ASR + MT + TTS/voice-cloning + a lip-sync model into an end-to-end dubbing tool — directly relevant as *system architecture* references even where individual components would be swapped:

- **overcrash66/video-translator** — https://github.com/overcrash66/video-translator. Fully local pipeline (no cloud APIs): Whisper/WhisperX ASR → translation → voice cloning → **LivePortrait for the visual lip-sync step** (marketed as "cinema-quality HD"), plus on-screen subtitle translation. Good reference for an all-local architecture.
- **Kedreamix/Linly-Dubbing** — multi-language video translation integrating Demucs/UVR5 for vocal separation before dubbing — the vocal-isolation step is a pattern worth adopting broadly (also seen in Hallo's Kim Vocal 2 usage) since dubbing over music-heavy source video is a common failure mode if skipped.
- **bprimal22/Video_Translation_with_LipSync** and **M-SRIKAR-VARDHAN/speech-to-speech-with-lipsync** — smaller reference implementations chaining Whisper → YourTTS/RVC voice cloning → Wav2Lip. Useful as minimal end-to-end examples, but built directly on Wav2Lip's non-commercial weights, so **not deployable as-is** commercially.
- **aws-samples/media-localization-with-visual-dubbing-lip-sync** — AWS reference architecture for visual dubbing at scale — a useful blueprint for how a cloud-native pipeline (queueing, GPU batch jobs, storage) might be organized even though it's a sample, not a model.

**Takeaway for our platform:** the "recipe" (separate vocals → ASR → MT → voice clone/TTS → lip-sync model → recombine with background audio) is now a fairly settled pattern across all of these; the open-source differentiation is really only in *which lip-sync model* sits at the end of the chain, which is why the model comparison above matters most.

---

## 5. Comparison Table

| Project | Technique | Input | Speed | Res. | License | Commercial-friendly? |
|---|---|---|---|---|---|---|
| Wav2Lip | GAN, mouth-patch | video+audio | offline (fast per-frame) | ~96-720px crop | Non-commercial | No (as-is) |
| SadTalker | 3DMM audio→motion | image+audio | offline | 256 (512 beta) | Apache-2.0 | Yes |
| MuseTalk | Latent inpainting (1-pass, SD-derived) | video+audio | **real-time capable** | 256 | MIT | Yes |
| LatentSync | Full latent diffusion | video+audio | offline (20-50 steps) | 512 | Apache-2.0 | Yes |
| VideoReTalking | 3-stage GAN pipeline | video+audio | offline | mid-high (enhanced) | Apache-2.0 | Yes (pose limits) |
| DINet | Deformation + inpainting | video+landmarks+audio | offline | scalable but poor generalization | Unspecified | No |
| DreamTalk | 3DMM-space diffusion | image+audio+style clip | offline | 256 | MIT code / gated ckpts | Partial (checkpoint request) |
| EchoMimic | SD+AnimateDiff diffusion (distilled variants) | image+audio(+pose) | offline (fast w/ distilled ckpt) | mid-high | Apache-2.0 | Yes |
| Hallo | SD+AnimateDiff diffusion | image+audio (English) | offline | high | MIT | Yes (English-only base) |
| FLOAT | Motion-latent flow matching | image+audio | fast offline | mid-high | Non-commercial | No |
| Ditto | Motion-space diffusion | image+audio | **real-time capable** | mid-high | Apache-2.0 | Yes |
| LivePortrait | Motion transfer (video-driven, not audio) | video+video | offline (real-time forks exist) | high | Unclear — verify | Verify |

---

## 6. Synthesis: What's Practical for a Commercial Product, Aug 2026

**Recommended shortlist (2-4 approaches), by role:**

1. **MuseTalk (self-host)** — for a **live/near-real-time preview or fast-turnaround dubbing tier**. It's the only project here combining (a) genuine real-time inference numbers, (b) a fully permissive MIT license on both code and models, and (c) an active maintainer (Tencent) with 2025 version updates. The 256px ceiling and per-identity `bbox_shift` tuning are real costs but solvable with a face-super-resolution post-pass.
2. **LatentSync (self-host)** — for a **"Pro"/high-quality offline render tier** where users are willing to wait longer for noticeably sharper mouths and better temporal stability than MuseTalk. Apache-2.0, ByteDance-maintained, and already the community's reference point for "best open lip-sync quality." Pair with a GPU batch queue (Modal/RunPod/own cluster) since it needs real VRAM (8-18GB+) and isn't fast.
3. **SadTalker or EchoMimic (self-host)** — for the **"animate a single photo" avatar-creation flow** (distinct product surface from re-dubbing existing video). SadTalker is simpler/lighter and Apache-2.0; EchoMimic adds pose-driving and has distilled fast checkpoints if the avatar flow needs to feel snappier, and is Apache-2.0 as well.
4. **Ditto, as an emerging real-time candidate to prototype now** — Apache-2.0 and explicitly ships streaming/online config, positioning it as MuseTalk's most credible near-term competitor for the real-time tier; worth a bake-off before committing MuseTalk to production long-term.

**Integration strategy recommendation:**
- **Self-host MuseTalk + LatentSync as the two production tiers** (fast/preview vs. high-quality/final) behind an internal API — both are commercially licensed and the field's speed/quality frontier is currently defined by exactly this pair (see LatentSync 2.4 vs MuseTalk 2.3 above). This avoids per-minute hosted-API costs at scale and gives full control over data/privacy (important for user-uploaded faces/voices).
- **Also budget for a hosted API fallback** (e.g., sync.so, or a commercial dubbing API such as HeyGen's video-translate/dubbing endpoints) for (a) burst capacity beyond your own GPU fleet, (b) markets/edge cases where your self-hosted model underperforms (extreme poses, non-frontal faces — VideoReTalking's and DINet's documented failure modes apply broadly across this whole model family), and (c) a fast go-to-market path before your self-hosted pipeline is fully hardened. A hybrid "self-hosted default, hosted-API overflow/premium" architecture is the pragmatic 2026 answer — pure self-host underestimates the long tail of hard inputs (side profiles, heavy accents/singing, background music, non-English audio) that these open models still handle unevenly.
- **Wrap the whole thing in the now-standard dubbing recipe**: vocal separation (Demucs/UVR5, or Kim Vocal 2 as in Hallo) → ASR (Whisper) → MT → voice cloning/TTS → lip-sync model → audio/video recombination — this is the pattern every open dubbing project above converges on, and building your own orchestration around swappable lip-sync backends (MuseTalk today, Ditto or a 2026-27 few-step-diffusion model tomorrow) is more future-proof than hard-coupling to one model.
- **Legal note:** never ship the original Wav2Lip weights, FLOAT weights, or DreamTalk's gated checkpoints in a commercial product without a separate commercial license/agreement — this is the single most common licensing trap in this space, since Wav2Lip-derived code appears (often unlicensed-for-commercial-use) inside a large fraction of the ecosystem's forks and pipelines.

**Rejected candidates and why:**
- **Original Wav2Lip weights** — non-commercial license is an outright blocker for direct use in a commercial product; only acceptable as an architectural reference or via a separately-licensed derivative/API.
- **DINet** — no stated license (defaults to full copyright, unsafe), poor zero-shot generalization outside its narrow training set (HDTF, frontal/normal-lighting only), effectively requiring per-identity fine-tuning — too much integration overhead and legal risk for the quality delivered, especially with newer alternatives available.
- **FLOAT** — despite being one of the best 2025 results on quality/speed, its explicit non-commercial license removes it from consideration for direct production use; keep it on the research-radar for its motion-latent flow-matching technique, which will likely reappear in a commercially-licensed successor.
- **DreamTalk** — MIT code is promising, but gated/email-request checkpoints for anything beyond academic research introduce approval-process risk and uncertainty incompatible with a product roadmap; revisit only if Alibaba changes checkpoint distribution terms.
- **VideoReTalking / DINet's landmark-heavy, multi-stage pipelines generally** — compared to unified diffusion or single-pass latent models (LatentSync, MuseTalk), multi-stage classical pipelines (separate pose-normalization, lip-gen, enhancement networks) are harder to maintain, harder to keep in sync across model updates, and are documented to fail on extreme poses — the field has clearly moved toward simpler, end-to-end models, and new engineering effort is better spent there.
- **LivePortrait as a lip-sync engine** — excellent at what it does (video-driven motion transfer/reenactment) but it is not itself audio-driven, so it doesn't solve the core lip-sync problem; only relevant as a downstream quality/stabilization layer, not the core model to build the feature around.

---

*Report compiled Aug 31, 2026. All findings sourced from direct README fetches of the linked repositories plus supplementary web search for 2025-2026 developments; URLs are cited inline throughout.*
