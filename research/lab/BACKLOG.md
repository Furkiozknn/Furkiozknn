# Backlog — Fikir / Araştırma / Teknik Borç

Üç ayrı liste tek dosyada: yeni fikirler kaybolmasın, teknik borç ertelenip unutulmasın. Her öğe kısa değerlendirmeyle birlikte kaydedilir (öncelik: **P0** kritik/hemen, **P1** yüksek değer, **P2** orta, **P3** "bir gün, işe yararsa").

Bu dosya sürekli güncellenir — tamamlanan bir iş çıkar, her tamamlanan iş yeni satır(lar) ekler.

---

## Sıradaki İş (aktif seçim)

**Yeni misyon çerçevesi (2026-09-04): FEWER REPOS + DEEPER ENGINEERING. Yeni repo yok; aşağıdaki her şey mevcut repoların içine gider.**
- **Faz 1 denetim raporları** (8 ajan; scratchpad `audits/` dizininde toplanıyor) → sentez → portföy yeniden sıralaması → top-10 aksiyon. Denetim bitmeden büyük implementasyona başlama.
- **`buradane` ana ürün hattı:** denetim çıktısına göre ilk gerçek kullanıcı için eksikler (veri tazeliği, moderasyon, duplicate tespiti, auth/rate-limit, spatial index doğrulaması) önceliklendirilecek.
- **Portföy anlatısı:** profil README en fazla 5-6 projeyi AI SYSTEMS + AGENT TOOLING + DEVELOPER INFRASTRUCTURE + REAL PRODUCTS hikâyesiyle öne çıkaracak; kalabalık liste kaldırılacak.

**2026-09-04 — platform artık gerçek iş yapıyor.** `ai-job-gateway` `generate-image` (hosted, keysiz) + 10 `media-*` (yerel) capability'si ile geliyor; `ai-workflow-engine` pipeline'ları canlı gateway'e karşı uçtan uca doğrulandı. Bu, aşağıdaki PoC'lerin önünü açtı: yeni bir Provider yazmak artık `Provider.run()` + registry'ye ekleme; `mini-creative-toolkit`'e yeni bir araç eklemek otomatik olarak `media-<op>` capability'si olur (OPERATIONS tablosuna bir satır).

- **`generate-image` canlı doğrulaması** (P1) — bu oturumun sandbox'ından Pollinations.ai'ye çıkış yoktu; provider mock HTTP'ye karşı tam test edildi ama gerçek servise karşı bir kez çalıştırılmalı (`uv run ai-job-gateway submit generate-image '{"prompt":"..."}'`).
- **`buradane` bbox filtresi için fonksiyonel indeks** (P3) — `location::geometry` cast'i GiST indeksini devre dışı bırakıyor; veri büyürse `CREATE INDEX ... USING gist ((location::geometry))`.
- **Kokoro-82M TTS → `ai-job-gateway` provider** (P1) — artık somut bir hedef var: `providers_local.py` deseninde `voice-io-mcp`'nin Kokoro yolunu `tts` capability'si olarak sarmak.

Tamamlanan: `asset-provenance-toolkit`, `research/lab/shared/gateway_poll.py` çıkarımı (ADR-008), `ai-workflow-engine`, `ai-repo-scaffold`, `ai-cost-estimator`, `webhook-sink` (bkz. `STATUS.md` ekosistem haritası).

**Şimdi en yüksek öncelik — API key gerektirmeyenler:**
- **FLUX.2 yerleşik çoklu-referans testi** (P1) — PuLID-FLUX'tan önce denenmeli, InsightFace lisans riskini baştan bypass edebilir. **Blokaj: gerçek FLUX.2 API key gerekiyor**, aynı P1 provider blokajıyla aynı.
- **Kokoro-82M TTS PoC** (P1) — Apache 2.0, self-host, API key gerekmiyor. `ai-job-gateway`'e `tts-fast` capability adayı.
- **ACE-Step 1.5 müzik PoC** (P1) — Apache 2.0, self-host, API key gerekmiyor. `music-generation` capability adayı.
- **Ses klonlama rıza/watermark politikası ADR'si** (P0 — ADR-010, kabul edildi) — herhangi bir klonlama Provider'ından önce şart, henüz uygulama yok.
- **PuLID-FLUX InsightFace lisans zinciri doğrulaması** (P0/P1) — teknik PoC'den önce, InstantID'nin başına gelenin tekrarlanıp tekrarlanmadığı netleşmeli.

---

## Yeni Repo: `ai-workflow-engine` (tamamlandı, push bekliyor)

DAG tabanlı pipeline orkestratörü — `ai-job-gateway` job'larını (generate → upscale → lip-sync gibi) YAML dosyasıyla zincirliyor, bağımsız adımları eşzamanlı çalıştırıyor (execution layers), Jinja2 ile adımlar arası sonuç referansı (`{{ steps.generate.result.x }}`). `gateway_poll.py` (ADR-008) vendor edildi. 32 test, gerçek `ai-job-gateway` sunucusuna karşı uçtan uca doğrulandı (generate→upscale zinciri). Yerel commit `613e85e`, kullanıcının boş repo açması bekleniyor.

---

## Reviewer Denetimi Bulguları (2026-08-31, iki bağımsız arka plan ajanı)

İki Reviewer Agent, sırasıyla (a) 3 backend/CLI reposunu (`ai-job-gateway`, `prompt-template-manager`, `model-comparison-harness`) ve (b) 5 ajan-yapımı reposunu (`mini-creative-toolkit`, `nvidia-nim-mcp`, `mcp-vet`, `kalp-animasyon`, `nova-drift`) tam kaynak koduyla denetledi. Ucuz/güvenli düzeltmeler doğrudan uygulanıp commit edildi (aşağıda ✅ işaretli, hepsi push edildi); mimari karar gerektiren veya riskli bulgular sadece kaydedildi.

**Doğrudan düzeltilip push edildi:**
- ✅ `ai-job-gateway`: `JobManager._run()`'da store-katmanı hatası job'ı sonsuza kadar askıda bırakabiliyordu (provider değil, `store.update_status` hatası yakalanmıyordu) — outer try/except + best-effort ERROR yazımı eklendi. Commit `2428311`, push edildi.
- ✅ `prompt-template-manager`: `submit_and_wait()`, süresi geçmiş job'ın `410 Gone` yanıtında `raise_for_status()`'u kontrolsüz çağırıp ham `httpx.HTTPStatusError` fırlatıyordu (dokümante edilen `GatewayJobFailedError` yerine) — 410 kontrolü öne alındı. Commit `9f368d2`, push edildi.
- ✅ `model-comparison-harness`: `GatewayBackend.run()`'da aynı 410 hatası, bağımsız olarak aynı şekilde tekrarlanmış — aynı düzeltme. Commit `da908ff`, henüz push edilmedi (repo boş GitHub deposu bekliyor, bkz. "bekleyen kullanıcı eylemleri").
- ✅ `nvidia-nim-mcp`: `check_provider_health`'te sınırsız eşzamanlı probe (yapısal rate-limit riski, model listesi büyürse) — `asyncio.Semaphore(6)` eklendi. Commit `c7073bc`, push edildi (`claude/improve-nvidia-nim-mcp` branch, açık PR).

**Yeni teknik borç/güvenlik kayıtları aşağıdaki tabloya eklendi (bkz. Teknik Borç Kaydı).**

---

## Fikir Backlog'u (henüz araştırılmamış/prototiplenmemiş)

| Fikir | Öncelik | Not |
|---|---|---|
| **Benchmark/evaluation altyapısı** | P1 | Aynı prompt/input'u birden fazla modelde çalıştırıp kalite+hız+maliyet karşılaştırması. `model-comparison-harness` bunun temelini attı (latency/success) — kalite skorlaması (ör. CLIP score, bir vision-LLM judge) eklenerek genişletilebilir. Kullanıcının açıkça istediği "benchmark/evaluation altyapısı" maddesiyle birebir örtüşüyor. |
| **Provider abstraction katmanı (görsel/video modelleri için)** | P1 | `ai-job-gateway`'in `Provider` arayüzü zaten bunun iskeleti. Gerçek bir FLUX/Wan2.2/MuseTalk provider implementasyonu (hosted API'ler üzerinden, self-host değil — maliyet/GPU erişimi olmadığı için) eklenmesi, ekosistemi "demo"dan "gerçek kullanılabilir"e taşır. **Blokaj:** gerçek API key'ler gerekiyor (kullanıcı sağlamadıkça sadece mock/echo provider'larla sınırlıyız). |
| **Workflow/pipeline engine** | P2 | ComfyUI'nin "graph = sürdürülebilir artifact" dersinin (araştırmadan) genellenmesi — birden fazla `ai-job-gateway` job'ını (görsel üret → üst-çözünürlük → lip-sync) bir DAG olarak zincirleyen küçük bir orkestratör. `prompt-template-manager` + `ai-job-gateway` üzerine inşa edilebilir. |
| **Asset/queue/worker sistemi ayrımı (SwarmUI dersi)** | P2 | `ai-job-gateway`'in ADR-004'te not edilen "gerçek kuyruğa geçiş" ihtiyacı büyüdüğünde ayrı bir repo olarak çıkarılabilir. Şimdilik erken. |
| **Design system / frontend component library** | P2 | Henüz hiçbir frontend/UI repo yok. Araştırma (`AI-CREATIVE-PLATFORM-ARASTIRMA-VE-MIMARI.md` §4.2) "kalıcı işbirlikçi canvas" en yüksek farklılaştırıcı olarak işaretliyor — bu, en büyük/en riskli parça, dikkatli bir tasarım fazı gerektirir. Kişisel site araştırmasıyla (`KISISEL-SITE-PLANI.md`) paylaşılan bir tipografi/renk/motion token seti üzerinden başlanabilir. |
| **Kişisel site prototipi (ayrı çalışma alanı)** | P2 | `KISISEL-SITE-PLANI.md`'de planlanan Next.js + Tailwind + Framer Motion yaklaşımının küçük bir iskelet/prototipi — kullanıcı gerçek bir domain almadan da yerel olarak geliştirilebilir. Framer şablonunu kopyalamadan, aynı kalite barına ulaşan özgün bir tasarım dili gerektiriyor — bu, doğrudan bir "tasarım fazı" ister, aceleyle prototiplenmemeli. |
| **AI model benchmark sonuçları için bir "model radar" görselleştirmesi** | P3 | `TECH-RADAR.md`'deki verinin bir web sayfası/dashboard haline getirilmesi — güzel ama işlevsel değer düşük, ertelenebilir. |
| **Kimlik doğrulama / kullanıcı yönetimi / billing abstraction** | P3 | Gerçek bir kullanıcı tabanı olmadan bu katmanları inşa etmek erken optimizasyon. Sadece bir gerçek "ürün" (frontend + gerçek provider'lar) ortaya çıktığında gündeme gelmeli. |

## Araştırma Backlog'u (takip edilecek teknolojiler/gelişmeler)

| Konu | Öncelik | Not |
|---|---|---|
| FLUX.2 / Wan2.2 / MuseTalk fiyat-performans güncellemeleri | P2 | `AI-CREATIVE-PLATFORM-ARASTIRMA-VE-MIMARI.md` Ağustos 2026 itibarıyla güncel; model sağlayıcı manzarası hızlı değişiyor, 2-3 ayda bir yeniden gözden geçirilmeli. |
| Yeni "pipeline-as-artifact" / node-graph araçları | P3 | ComfyUI dışında bu deseni kullanan yeni araçlar çıkarsa (`workflow engine` fikrini besler). |
| Self-host GPU maliyeti eşiği (ne zaman hosted API'den self-host'a geçmeye değer) | P2 | Gerçek trafik verisi olmadan teorik kalıyor; ürün gerçek kullanıcı kazandığında somut hesap yapılmalı. |

## Teknik Borç Kaydı

| Kayıt | Repo | Öncelik | Not |
|---|---|---|---|
| ~~Repo'lar arası kod tekrarı (submit/poll istemci mantığı)~~ | `ai-job-gateway`, `prompt-template-manager`, `model-comparison-harness` | ✅ Çözüldü | ADR-008 uygulandı: `research/lab/shared/gateway_poll.py` kanonik dosyası üç repoya vendor edildi, testler yeşil (46/43/37). |
| ~~HTTP istemci çağrılarında per-request timeout tutarsızlığı (`model-comparison-harness`)~~ | `model-comparison-harness` | ✅ Çözüldü | `gateway_poll.py` çıkarımı sırasında `GatewayBackend.run()`'a `timeout=self.timeout` eklendi, `HttpBackend` ile tutarlı hale geldi. |
| SSRF: `webhook_url` host/IP filtresi yok | `ai-job-gateway` | **P1 (güvenlik)** | Reviewer bulgusu (HIGH): `manager.py::_deliver_webhook`, submitter'ın verdiği herhangi bir URL'ye (ör. `169.254.169.254` cloud metadata, `localhost:<iç port>`) hiçbir host/IP kısıtı olmadan POST atıyor. Hızlı bir düzeltme değil — local-dev webhook testini kırmadan bir `webhook_allowed_hosts` allowlist politikası tasarlanmalı. Public deployment öncesi zorunlu. |
| `POST /v1/{capability}` gövde boyutu sınırsız | `ai-job-gateway` | P2 (güvenlik) | Reviewer bulgusu (MEDIUM): `request.json()` hiçbir boyut sınırı olmadan tam belleğe okunuyor — ucuz bellek tükenmesi DoS'u. `Content-Length` kontrolü + streaming cap gerekiyor (spoofable header, dikkatli tasarlanmalı). |
| Sandboxsız Jinja2 `Environment` | `prompt-template-manager`, `ai-workflow-engine` | P2 (güvenlik, koşullu) | Reviewer bulgusu (MEDIUM): aynı desen iki repoda — tam Jinja2 dilini (loop/filter/makro) çalıştırıyor, sadece `{{ var }}` değil — şablonlar/pipeline'lar güvenilmeyen bir kaynaktan gelirse (paylaşılan pazar, webhook, yükleme) SSTI/DoS riski. `ai-workflow-engine`'de bu artık kodda (docstring) ve README'de açıkça belgelendi (Reviewer Agent tarafından, commit `93c6597`); `prompt-template-manager`'da henüz sadece bu tabloda kayıtlı. Ya her ikisinde de `SandboxedEnvironment`'a geçilmeli ya da varsayım tutarlı şekilde belgelenmeli — ikisi de "operatör-yazdığı = kod kadar güvenilir" varsayımını paylaşıyor. |
| HTTP istemci çağrılarında per-request timeout tutarsızlığı (kalan) | `ai-job-gateway`, `prompt-template-manager` | P3 | `model-comparison-harness` yukarıda düzeltildi. `ai-job-gateway`'in `client.py`'si ve `prompt-template-manager`'ın `gateway_client.py`'si hâlâ submit/poll çağrılarına açık bir `timeout` geçmiyor (httpx varsayılanına güveniyor). Düşük risk, birlikte düzeltilebilir. |
| `yaml.safe_load` anchor-expansion'a karşı korumasız | `prompt-template-manager`, `model-comparison-harness` | P3 | Şablon/config dosyaları operatör tarafından yazıldığı için düşük öncelik, ama kodda zorlanmıyor. |
| `nvidia-nim-mcp`: hata mesajları `str(e)` olarak ham döndürülüyor | `nvidia-nim-mcp` | P2 (güvenlik, doğrulama gerekli) | `check_provider_health`'in 4 probe yardımcı fonksiyonu, provider hata metnini olduğu gibi rapor metnine yazıyor — teorik olarak kısmi API key sızıntısı riski (litellm'in bazı sağlayıcı hata şekillerinde). Güvenli redaksiyon için önce her sağlayıcının gerçek hata şeklini doğrulamak gerekiyor — kör düzeltme yapılmadı. |
| `nvidia-nim-mcp`: kullanılmayan `httpx` bağımlılığı | `nvidia-nim-mcp` | P3 | Sadece `httpx2` kullanılıyor; `httpx` ya gereksiz (kaldırılmalı) ya da transitif bir ihtiyaç var (dokümante edilmeli). |
| `mini-creative-toolkit`: `generate_image_free` boyut doğrulaması yok | `mini-creative-toolkit` | P3 | Diğer tüm araçlarda `_require_positive` var, bu araçta yok — 0/negatif değer yerel yerine uzak Pollinations API'sinde hata veriyor. |
| `kalp-animasyon`: `prefers-reduced-motion` canlı değişikliği izlenmiyor | `kalp-animasyon` | P3 | Sayfa yüklendiğinde bir kez okunuyor, `matchMedia('change')` dinleyicisi yok. |
| `nova-drift`: PRNG mantığı test dosyasında elle kopyalanmış | `nova-drift` | P3 | `mulberry32`/seed mantığı `script.js` ve `test/prng.spec.js`'de ayrı ayrı yazılı (yorumla belgelenmiş bilinçli tercih) — gerçek implementasyon değişirse test sessizce eskimiş kopyayı doğrulamaya devam eder. Saf fonksiyonları bağımlılıksız ortak bir modüle çıkarmak ya da CI'da iki kopyayı diff'leyen bir adım eklemek düşünülebilir. |
| `ai-job-gateway`'de gerçek kuyruk yok | `ai-job-gateway` | P2 | ADR-004'te dokümante edildi, bilinçli v1 sınırı — gerçek trafik/çoklu-worker ihtiyacı doğduğunda ele alınacak. |
| Hiçbir repoda gerçek provider yok (hepsi mock/echo) | `ai-job-gateway` ve türevleri | P1 | En büyük "demo'dan öteye geçme" engeli — gerçek API key'ler olmadan ilerlenemez, kullanıcı girdisi gerekiyor. |
| Frontend/UI katmanı hiç yok | ekosistem geneli | P2 | Backend/orkestrasyon tarafı olgunlaştı, kullanıcı yüzü hâlâ eksik. |

## Reddedilen / "Kullanılmamalı" Kararlar (değerli negatif sonuçlar)

Bunlar da araştırma çıktısıdır — tekrar zaman kaybetmemek için:

- **HunyuanVideo'yu ana video modeli olarak seçmek** — 100M MAU tavanı + AB/UK/Güney Kore hariç tutma lisans kısıtı nedeniyle reddedildi (bkz. araştırma raporu C).
- **Wav2Lip orijinal ağırlıklarını doğrudan kullanmak** — ticari olmayan lisans, ekosistemde çok yaygın bir tuzak (bkz. araştırma raporu D).
- **GitHub topic sayfalarını doğrudan güvenilir kaynak olarak kullanmak** — SEO/spam repo'larla dolu, sadece bir "keşif sinyali", asıl değerlendirme bağımsız araştırmadan geldi.
- **Paylaşılan bir `ai-ecosystem-common` paketi (şimdilik)** — ADR-006, henüz erken, sadece 3 küçük kod tekrarı var.
- **Hunyuan3D-2.1'i 3D üretim modeli olarak seçmek** — HunyuanVideo ile birebir aynı Tencent lisans şablonu (AB/UK/Güney Kore hariç + 1M MAU tavanı). Tencent-Hunyuan ailesinden gelecek her yeni model varsayılan olarak şüpheyle kontrol edilmeli.
- **RMBG-2.0 (BRIA)'yı arka plan kaldırma modeli olarak seçmek** — CC BY-NC 4.0. **Not: bu teorik değildi** — `rembg` 2.0.81'in `session=None` iç varsayılanı zaten sessizce buna çözümleniyordu, `mini-creative-toolkit` fiilen bunu kullanıyordu ta ki commit `74d5dad` düzeltene kadar (bkz. ADR-009).
- **MusicGen/AudioCraft ağırlıklarını müzik üretim modeli olarak seçmek** — CC-BY-NC 4.0. ACE-Step/Stable Audio Open aynı alanı ticari lisanslarla kapsıyor.
- **Coqui XTTS-v2'yi ses klonlama modeli olarak seçmek** — CPML (ticari olmayan) VE Coqui Inc. Ocak 2024'te kapandığı için ticari lisans satın alma yolu da artık yok. Kalite referansı olarak anılabilir, üretime asla alınmaz.
- **InstantID'yi yüz kimliği tutarlılığı için seçmek** — InsightFace embedding'i ticari olmayan araştırma lisanslı, ayrıca SDXL'e kilitli (FLUX portları kararsız). PuLID-FLUX aynı riski taşıyabilir, doğrulama bekleniyor (ADR listesinde P0).
