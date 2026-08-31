# AI Creative Platform — Araştırma Sentezi ve Ürün Mimarisi

**Tarih:** 2026-08-31
**Kapsam:** Görsel üretim, FLUX/fal.ai-tarzı çıkarım altyapısı, image-to-video/video üretimi, lip-sync/dublaj ve rakip "creative tools" ekosisteminin analizi; bunlardan hareketle özgün bir AI creative platform için somut mimari öneri.
**Yöntem:** 5 paralel araştırma ajanı ile GitHub topic sayfaları (`ai-art-generator`, `creative-tools`, `fal-ai-alternative`, `flux-1`, `image-to-video`, `lipsync`, `generative-ai`) ve bunların ötesinde bağımsız araştırma; her repo için README/dokümantasyon doğrudan incelendi. Ham raporlar `research/raw/` altında, kaynak URL'leriyle birlikte referans olarak duruyor — bu doküman onların sentezidir.

> **Not:** Bu doküman hiçbir projeyi birebir kopyalamayı önermez. Amaç, mevcut açık kaynak ekosistemindeki **mimari desenleri, teknik dersleri ve lisans tuzaklarını** çıkarıp bunlardan ilham alan, kendi mimarisi ve uygulaması bize ait bir ürün tasarlamaktır.

---

## 1. Yönetici Özeti

Araştırılan ~50 proje şu ana sonucu ortaya koyuyor: **temel üretim modeli katmanı (image/video/lip-sync) hızla emtia (commodity) haline geliyor** — FLUX, Wan2.2, LTX-2, MuseTalk/LatentSync gibi açık modeller kaliteyi neredeyse kapalı API'lerle eşitledi. Gerçek farklılaşma artık modelde değil, üç yerde ortaya çıkıyor:

1. **Orkestrasyon mimarisi** — job kuyruğu, model soyutlama katmanı, maliyet/kalite kademelendirmesi (tier'lama).
2. **Yaratıcı UX metaforu** — tek seferlik "prompt → sonuç" formu değil, kalıcı, işbirlikçi, canlı-geri-bildirimli bir **canvas/workspace**.
3. **Pipeline'ın kendisinin bir ürün olması** — üretilen görsel/video değil, onu üreten iş akışı (graph) paylaşılabilir, sürümlenebilir, yeniden çalıştırılabilir bir varlık.

Önerilen strateji: **Faz 1'de hosted API'lerle (fal.ai/Replicate/RunPod) hızlı çıkış, Faz 2'de hacim arttıkça ComfyUI tabanlı self-host altyapıya geçiş, Faz 3'de gerçek farklılaşmayı canvas/collaboration/consistency katmanında inşa etmek.**

---

## 2. Rekabet Ortamı — Kategori Bazlı Özet

### 2.1 Görsel Üretim & Yaratıcı Araçlar (bkz. `research/raw/A_image_creative_tools.md`)

| Proje | Mimari Deseni | Bizim İçin Değeri |
|---|---|---|
| **ComfyUI** | DAG/node-graph motoru, kısmi yeniden-yürütme, ayrık frontend/backend | Pipeline'ı JSON olarak serileştirilebilir bir "artifact" haline getirme deseni — **en yüksek kaldıraçlı fikir** |
| **InvokeAI** | Katmanlı "Unified Canvas", tek backend üzerinde basit/gelişmiş çift-mod UI | Canvas-merkezli UX metaforu; generation = tuval üzerindeki bir araç, izole bir işlem değil |
| **Fooocus** (artık dondurulmuş) | Gizli, otomatik ayarlanmış parametreler, minimum kullanıcı müdahalesi | "Akıllı varsayılanlar + gelişmiş moda kaçış kapısı" felsefesi |
| **SwarmUI** | Orkestrasyon/çalıştırma ayrımı, çoklu-GPU/backend dağıtımı | Multi-tenant SaaS ölçeği için "iş kuyruğuna dağıtılan stateless worker'lar" tasarımı |
| **Krita AI Diffusion** | Var olan bir profesyonel araca (Krita) eklenti + canlı boyama geri bildirimi | "Kullanıcının zaten bulunduğu araca git" stratejisi + sürekli/canlı üretim modu |
| **Penpot** | Gerçek zamanlı çoklu-kullanıcı işbirlikçi canvas (Figma alternatifi) | Takım-tabanlı işbirlikçi oturumlar için referans mimari (presence, canlı imleç, çakışmasız eşzamanlı düzenleme) |
| **StableStudio** | Backend'i plugin ile değiştirilebilir frontend | Hem "yönetilen bulut çıkarımı" hem "kendi donanımın" katmanını tek frontend'den sunma |
| **Texel Studio** | Diffusion değil, LLM-agent + araç kullanımı ile piksel sanatı | Her "AI creative" özelliğin diffusion olması gerekmiyor; "üret → kendi kendine incele (vision) → düzelt" döngüsü ucuz bir kalite kaldıracı |

**En değerli 3 fikir:** (1) Üretim pipeline'ının kendisi paylaşılabilir/sürümlenebilir bir varlık olmalı; (2) tek güçlü motor üzerinde basit-mod/güçlü-mod ayrımı; (3) kalıcı işbirlikçi canvas, tek seferlik form yerine.

### 2.2 FLUX & fal.ai-Tarzı Altyapı (bkz. `research/raw/B_flux_fal_alternatives.md`)

BFL'nin kendi hosted API'si ve RunPod'un `worker-comfyui`'si **bağımsız olarak aynı mimariye** yakınsıyor — bu, kopyalanacak "altın standart" sözleşme:

```
POST /v1/{model} → { id, polling_url }   (iş gönder, hemen dön)
GET  {polling_url} → { status: pending|ready|error, result? }
webhook_url (opsiyonel) → tamamlanınca callback
Sonuç URL'leri kısa ömürlü (BFL: 10 dk) → istemciyi hemen kalıcı depolamaya zorlar
```

- **Model soyutlama:** Cog'un tip-anotasyonlu `predict()` → otomatik OpenAPI şeması deseni ve Open-Generative-AI'ın tek `models.js` kayıt dosyası, birden fazla modeli/sağlayıcıyı tek iç sözleşmeye bağlamanın kanıtlanmış yolu.
- **v1 için en hızlı yol:** ComfyUI'yi çalıştırma motoru olarak, RunPod Serverless'i (veya Modal) otomatik ölçekleyici olarak kullanmak — model ağırlıklarını Docker image'ına gömüp sync/async/webhook endpoint'leri açmak. Bu, fal.ai'nin kendi mühendisliğinin de yaptığına çok yakın (container-per-model + sağlayıcı-yönetimli ölçekleme).
- **Maliyet kademelendirmesi:** GGUF/NF4 kuantizasyonu ile ucuz/hızlı katman, tam hassasiyetle kaliteli katman — BFL'nin kendi klein/pro/max/flex fiyatlandırmasının aynısı.
- **Lisans uyarısı:** FLUX.1 `[dev]` ve çoğu görev-özel varyant **ticari olmayan lisans**; sadece `[schnell]` ve FLUX.2 `[klein-4B]` Apache 2.0 ve tamamen self-host edilebilir.

### 2.3 Image-to-Video / Video Üretimi (bkz. `research/raw/C_video_generation.md`)

| Model | Lisans | Güç | Zayıflık |
|---|---|---|---|
| **Wan2.2** (Alibaba) | Apache 2.0 | En geniş yetenek seti (T2V/I2V/TI2V/konuşma-videosu/karakter animasyonu), tam ticari kullanım | 14B modelleri ≥80GB VRAM gerektirir |
| **LTX-2/2.3** (Lightricks) | OpenRAIL-M (ticari izinli) | En hızlı (H100'de ~10sn/720p klip), yerel 60sn süre desteği | Distile varyantlarda kalite ödünü |
| **CogVideoX-2B** | Apache 2.0 | En düşük VRAM tabanı (~5GB) — ücretsiz katman/önizleme için ideal | 5B model ayrı ve kısıtlayıcı lisansa sahip — **kaçınılmalı** |
| **HunyuanVideo(-1.5)** (Tencent) | Kısıtlayıcı özel lisans | Çok güçlü kalite | **100M MAU tavanı + AB/UK/Güney Kore hariç tutma** — büyüme hedefli bir platform için ciddi hukuki risk, **önerilmiyor** |
| **SVD** (Stability) | Ticari olmayan | Tarihsel referans | Üretime uygun değil |
| **SkyReels-V2** | Belirsiz özel lisans | Sonsuz-uzunlukta video (autoregressive diffusion-forcing) — benzersiz | Ticari kullanım öncesi hukuki inceleme şart |

**Önerilen strateji:** Faz 1'de fal.ai/Replicate üzerinden Wan2.2 + LTX-2'ye hosted API ile erişim (GPU-ops yükü yok); Faz 2'de hacim arttıkça ComfyUI + kendi GPU'larımızla self-host. Son işleme adımı olarak **RIFE (MIT)** ile frame interpolation her zaman self-host edilmeli — ucuz ve algılanan kaliteyi belirgin şekilde artırıyor.

### 2.4 Lip-Sync & Dublaj (bkz. `research/raw/D_lipsync.md`)

| Model | Teknik | Lisans | Rol |
|---|---|---|---|
| **MuseTalk** (Tencent) | Latent-uzayda tek-geçişli inpainting | MIT | **Gerçek zamanlı / hızlı önizleme katmanı** (30fps+ V100'de) |
| **LatentSync** (ByteDance) | Uçtan uca latent diffusion | Apache 2.0 | **"Pro" kalite / offline render katmanı** (en keskin sonuç, ama yavaş) |
| **SadTalker / EchoMimic** | 3DMM / diffusion tabanlı foto-animasyon | Apache 2.0 | Tek fotoğraftan avatar oluşturma (farklı bir ürün yüzeyi — video değil, imge girdisi) |
| **Ditto** (Ant Group) | Motion-space diffusion, native streaming config | Apache 2.0 | MuseTalk'a karşı bake-off için gelecek vaat eden aday |
| **Wav2Lip** (orijinal ağırlıklar) | GAN, ağız-yaması | **Ticari olmayan** | **En yaygın hukuki tuzak** — ekosistemdeki birçok fork/dublaj pipeline'ında lisanssız şekilde gömülü; doğrudan kullanılmamalı |

**Önerilen mimari:** MuseTalk (hızlı/self-host) + LatentSync (kaliteli/self-host) iki üretim katmanı + burst kapasitesi ve zor girdiler (yan profil, gürültülü ses) için hosted API (sync.so, HeyGen dubbing) yedeği. Standart dublaj tarifi: **vokal ayrıştırma (Demucs/UVR5) → ASR (Whisper) → çeviri → ses klonlama/TTS → lip-sync modeli → yeniden birleştirme.**

---

## 3. Lisans ve Maliyet Haritası (Kritik Karar Tablosu)

| Katman | Ticari Açıdan Güvenli (Faz 1'den itibaren self-host edilebilir) | Dikkatli Kullanılmalı / Hosted API'ye Yönlendir |
|---|---|---|
| Görsel | FLUX.1 `[schnell]`, FLUX.2 `[klein-4B]` (Apache 2.0) | FLUX.1 `[dev]`, FLUX.2 `[dev]`/`[klein-9B]` → BFL hosted API üzerinden |
| Video | Wan2.2, CogVideoX-2B, AnimateDiff, LTX-2 (OpenRAIL-M) | HunyuanVideo (MAU tavanı + bölge kısıtı), SVD (ticari olmayan), CogVideoX-5B, SkyReels-V2 (lisans belirsiz) |
| Lip-sync | MuseTalk, LatentSync, SadTalker, EchoMimic, Ditto (hepsi MIT/Apache 2.0) | Wav2Lip orijinal ağırlıkları, FLOAT, DreamTalk (gated checkpoint) |
| Çalıştırma motoru | ComfyUI (GPL-3.0 — **iç kullanım için sorun değil**, dağıtım değil) | — |

> **Kural:** Hiçbir zaman Wav2Lip/FLOAT/DreamTalk'un orijinal ağırlıklarını ticari üründe doğrudan sevk etme. HunyuanVideo'yu AB/UK kullanıcı tabanı olan bir platformda ana model olarak seçme.

---

## 4. Önerilen Ürün Mimarisi

```
┌─────────────────────────────────────────────────────────────────┐
│  CLIENT — Yaratıcı Canvas (web, opsiyonel masaüstü)              │
│  • Kalıcı, katmanlı, çoklu-kullanıcı işbirlikçi tuval             │
│  • "Basit mod" (niyet → sonuç) + "Güçlü mod" (node/graph editörü)│
│  • Her üretim = pipeline JSON + versiyon + provenance metadata   │
└───────────────────────────┬───────────────────────────────────────┘
                            │ REST/WebSocket
┌───────────────────────────▼───────────────────────────────────────┐
│  API GATEWAY  (submit → poll/webhook sözleşmesi, BFL/RunPod deseni)│
│  • POST /v1/{capability} → {id, polling_url}                     │
│  • Auth, rate-limit, kota, faturalama                             │
└───────────────────────────┬───────────────────────────────────────┘
                            │
┌───────────────────────────▼───────────────────────────────────────┐
│  MODEL ABSTRACTION LAYER  (Cog-tarzı tipli şema + tek registry)   │
│  • Her "capability" (image-gen, i2v, lipsync) için ortak istek/   │
│    yanıt kontratı; backend'in FLUX/Wan2.2/MuseTalk/hosted-API     │
│    olması bu katmanın arkasında saklanır                          │
│  • Kalite/hız/maliyet kademesi (tier) modelin bir parametresi     │
└───────────────────────────┬───────────────────────────────────────┘
                            │
┌───────────────────────────▼───────────────────────────────────────┐
│  ORCHESTRATION / JOB QUEUE  (SwarmUI-tarzı ayrım: scale-out ≠     │
│  execution)                                                        │
│  • Stateless worker havuzuna dağıtılan job'lar                   │
│  • Faz 1: RunPod/Modal serverless otomatik ölçekleme              │
│  • Faz 2: kendi GPU filomuz + K8s/Triton (ensemble/BLS)           │
└───────┬─────────────┬─────────────┬─────────────┬─────────────────┘
        │             │             │             │
┌───────▼───┐  ┌──────▼──────┐ ┌────▼────────┐ ┌──▼───────────────┐
│ GÖRSEL     │  │ VİDEO       │ │ LIP-SYNC /  │ │ HOSTED API       │
│ (ComfyUI + │  │ (ComfyUI +  │ │ DUBLAJ      │ │ FALLBACK         │
│ FLUX.2     │  │ Wan2.2 /    │ │ (MuseTalk + │ │ (fal.ai/         │
│ klein+dev, │  │ LTX-2, RIFE │ │ LatentSync, │ │ Replicate/BFL/   │
│ GGUF/NF4   │  │ interp.)    │ │ Whisper+TTS)│ │ sync.so)         │
│ kuantizasyon)│ │             │ │             │ │ burst/edge-case  │
└────────────┘  └─────────────┘ └─────────────┘ └──────────────────┘
                            │
┌───────────────────────────▼───────────────────────────────────────┐
│  STORAGE & PROVENANCE                                             │
│  • Her çıktıya gömülü/bağlı pipeline metadata (A1111 PNG-roundtrip│
│    deseninden esinli) → tam yeniden üretilebilirlik               │
│  • Kısa ömürlü sinyal URL'leri, kalıcı depolamaya zorunlu kopyalama│
└─────────────────────────────────────────────────────────────────┘
```

### 4.1 Neden bu katmanlaşma

- **API Gateway ve Model Abstraction ayrı katmanlar**: BFL/RunPod'un submit-poll-webhook sözleşmesini gün 1'den itibaren sabitlemek, hangi model/sağlayıcı arkada çalışırsa çalışsın istemci tarafını hiç değiştirmeden backend'i evrimleştirmeyi sağlar (self-host ↔ hosted API geçişi şeffaf olur).
- **Orkestrasyon ve çalıştırma motoru ayrımı** (SwarmUI dersi): Tek kullanıcı/tek GPU varsayımıyla başlayıp sonra multi-tenant'a geçmek pahalı bir yeniden yazıma yol açar; bu yüzden gün 1'den "job → worker havuzu" modeliyle tasarlanmalı.
- **ComfyUI çekirdek çalıştırma motoru olarak**: Hem görsel hem video hem (custom node'larla) lip-sync için tek motor — model değiştirmek graph'ta node değiştirmektir, ayrı entegrasyon kodu yazmaya gerek kalmaz. GPL-3.0 lisansı, ComfyUI'yi **içeride servis olarak** çalıştırıp değiştirilmiş halini dağıtmadığımız sürece sorun teşkil etmez.

### 4.2 Farklılaştırıcı katman — asıl rekabet avantajı burada

Araştırmanın en net sonucu: temel modeller emtia hâline geldi, gerçek farklılaşma şurada:

1. **Kalıcı işbirlikçi canvas** (InvokeAI Unified Canvas + Penpot'un gerçek-zamanlı çoklu-kullanıcı deseni): Üretim, tuval üzerindeki katmanlardan biri; kullanıcılar birlikte aynı proje üzerinde çalışabilir (presence, canlı imleç, yorum).
2. **Canlı geri bildirim döngüsü** (Krita AI Diffusion'ın "Live Painting"i): Kullanıcı fırça darbesi attıkça arka planda sürekli reinterpretasyon — "tıkla-bekle" yerine sürekli/akan bir etkileşim modeli.
3. **Pipeline-as-artifact** (ComfyUI): Kullanıcının oluşturduğu bir "marka ürün fotoğrafı" veya "karakter tutarlılığı" pipeline'ı kaydedilebilir, forklanabilir, API/MCP tool olarak dışa açılabilir (Langflow'un "workflow → deploy edilebilir API/tool" deseni).
4. **Self-critique/inceleme döngüsü** (Texel Studio): Her üretimden önce ucuz bir vision-model kontrolü ("bu, istenen ile eşleşiyor mu?") veya çok-geçişli iyileştirme — training gerektirmeden algılanan kaliteyi artırır.
5. **Kompozit üretim**: Görsel + video + lip-sync tek bir sürekli iş akışında zincirlenebilir (örn. "bu karakteri çiz → bu karakteri canlandır → bu sesle dublajla") — hiçbir rakip bunu tek bir kesintisiz canvas deneyiminde sunmuyor.

---

## 5. Faz Planı

**Faz 1 — MVP (0-3 ay):**
- Model Abstraction + API Gateway katmanını submit/poll/webhook sözleşmesiyle inşa et.
- Görsel: FLUX.2 klein (hızlı/ücretsiz katman, self-host) + BFL hosted API (pro/dev katman).
- Video: fal.ai/Replicate üzerinden Wan2.2 + LTX-2 (hosted, GPU-ops yükü yok).
- Lip-sync: Hosted API (sync.so benzeri) ile başla, MuseTalk'ı paralel olarak self-host ortamda pilot et.
- Basit-mod canvas UI (Fooocus felsefesi: gizli akıllı varsayılanlar).

**Faz 2 — Ölçek (3-9 ay):**
- ComfyUI tabanlı self-host çıkarım kümesi (RunPod/Modal serverless → kendi GPU filosu geçişi, hacim eşiği aşıldığında).
- GGUF/NF4 kuantizasyon katmanı ile maliyet kademeleri.
- MuseTalk + LatentSync'i üretim katmanına al, hosted API'yi burst/edge-case yedeğine indir.
- Canvas'a katman sistemi, non-destructive history, temel çoklu-kullanıcı presence ekle.

**Faz 3 — Farklılaşma (9+ ay):**
- Pipeline-as-artifact: kullanıcı iş akışlarının kaydı/forklanması/API olarak dışa açılması.
- Krita-tarzı canlı-geri-bildirim üretim modu (prototip).
- Karakter/stil tutarlılığı, kamera kontrolü (CameraCtrl deseninden esinli adapter mimarisi), uzun-form video (SkyReels-V2 lisansı netleşirse).
- Self-critique/vision-check otomatik kalite katmanı.

---

## 6. Teknoloji Stack Önerisi (Somut)

- **Çalıştırma motoru:** ComfyUI (self-host, iç servis olarak; GPL-3.0 uyumluluğu için dağıtılmaz).
- **Model soyutlama:** Cog-tarzı tipli `predict()` şeması + tek model registry (Open-Generative-AI'nin `models.js` desenine benzer).
- **Job/queue:** Faz 1'de RunPod Serverless veya Modal; Faz 2'de kendi K8s + Triton Ensemble/BLS.
- **Görsel modeller:** FLUX.2 klein-4B (self-host, Apache 2.0) + BFL API (dev/pro).
- **Video modelleri:** Wan2.2 (Apache 2.0, geniş yetenek) + LTX-2 (OpenRAIL-M, hız/uzun-süre) + CogVideoX-2B (ücretsiz katman).
- **Lip-sync:** MuseTalk (hızlı, MIT) + LatentSync (kaliteli, Apache 2.0).
- **Post-processing:** RIFE (MIT, frame interpolation).
- **Frontend:** React tabanlı canvas editörü; node-graph gücü için React Flow (Langflow'un kullandığı kütüphane) değerlendirilebilir.
- **Depolama/provenance:** Her çıktıya gömülü pipeline metadata (PNG metadata round-trip deseni); kısa ömürlü sinyal URL + kalıcı obje depolama (S3-uyumlu).

---

## 7. Riskler ve Açık Sorular

1. **HunyuanVideo'nun lisans kısıtları** — büyüme hedefiyle çelişir, ana model olarak seçilmemeli.
2. **SkyReels-V2 lisansı belirsiz** — uzun-form video özelliği için cazip ama hukuki inceleme şart.
3. **Wav2Lip türevi kod tabanları** — dublaj/lip-sync ekosisteminde çok yaygın, dikkatli denetim gerektirir.
4. **ComfyUI'nin GPL-3.0'ı** — sadece iç servis olarak çalıştırıldığı sürece güvenli; ComfyUI'nin değiştirilmiş bir dağıtımını üçüncü taraflara vermek farklı bir hukuki durum yaratır.
5. **GPU maliyeti** — Faz 1'in hosted-API-öncelikli olması bilinçli bir tercih: self-host GPU capex'i, hacim onu haklı çıkarana kadar ertelenmeli.

---

## 8. Kaynaklar

Tüm ham araştırma raporları (repo bazında derinlemesine analiz, kaynak URL'leriyle) `research/raw/` klasöründe:
- `A_image_creative_tools.md` — Görsel üretim & yaratıcı araçlar (13 proje)
- `B_flux_fal_alternatives.md` — FLUX & fal.ai-tarzı altyapı (17 proje)
- `C_video_generation.md` — Video üretim modelleri (12+ model/araç)
- `D_lipsync.md` — Lip-sync & dublaj (9 derin analiz + ek teknikler)
- `E_framer_site_analysis.md` — Framer site analizi (bkz. `research/KISISEL-SITE-PLANI.md` için sentez)

Kişisel web sitesi planı için ayrı doküman: [`research/KISISEL-SITE-PLANI.md`](./KISISEL-SITE-PLANI.md)
