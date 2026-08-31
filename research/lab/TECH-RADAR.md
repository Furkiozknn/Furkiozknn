# Technology Radar — Teknoloji Kararları

Her önemli teknoloji değerlendirmesi şu şablonla kaydedilir: ne işe yarıyor, neden önemli, nerede kullanılabilir, alternatifler, avantaj/dezavantaj, lisans notu, kendi çözüm vs. mevcut çözüm, prototip gerekli mi, öncelik. Sadece popülerlik (star sayısı) tek başına karar kriteri değildir — kod kalitesi, aktif geliştirme, lisans, mimari, sürdürülebilirlik birlikte değerlendirilir.

Durum etiketleri: 🟢 **Benimsendi** · 🟡 **Değerlendiriliyor** · 🔴 **Reddedildi** · ⚪ **İzleniyor** (henüz karar yok)

---

## 🟢 FLUX.2 (Black Forest Labs) — Görsel üretim

- **Ne işe yarıyor?** Rectified-flow tabanlı görsel üretim modeli ailesi; `[klein]` (4B, hızlı/ucuz), `[dev]`/`[pro]`/`[max]` (kaliteli, pahalı) katmanları var.
- **Neden önemli?** Açık kaynak görsel üretimde şu an en güçlü aile; `klein-4B` tamamen Apache 2.0 ve tüketici GPU'da çalışabiliyor.
- **Nerede kullanılabilir?** `ai-job-gateway`'in ilk gerçek `Provider` implementasyonu için doğal aday — hem self-host (klein) hem hosted API (dev/pro/max) katmanı sunuyor.
- **Alternatifler:** Wan2.2 (video için ayrı), Stable Diffusion 3.5, Qwen-Image.
- **Avantaj:** İki kademeli lisans (ücretsiz hızlı katman + ücretli kaliteli katman) tam olarak `ai-job-gateway`'in tier'lama felsefesiyle örtüşüyor. **Dezavantaj:** `[dev]`/`[pro]`/`[max]` ticari olmayan/API-only, kendi altyapımızda barındırılamaz.
- **Lisans notu:** `[klein-4B]` Apache 2.0 (güvenli); diğer katmanlar ticari olmayan lisans veya sadece BFL'nin kendi hosted API'si üzerinden — dikkat.
- **Kendi çözüm mü, mevcut mu?** Mevcut çözüm — model eğitmek kapsam dışı, sadece API/self-host entegrasyonu yazılır.
- **Prototip gerekli mi?** Evet — gerçek bir `FluxProvider` implementasyonu (bkz. `BACKLOG.md`, P1). **Blokaj:** API key gerekiyor, kullanıcı sağlamadan ilerlenemez.
- **Öncelik:** P1

---

## 🟢 Wan2.2 (Alibaba) — Video üretim

- **Ne işe yarıyor?** MoE tabanlı video difüzyon modeli; T2V/I2V/TI2V/konuşma-videosu/karakter animasyonu tek ailede.
- **Neden önemli?** Apache 2.0, MAU tavanı yok, bölge kısıtı yok — 2026 itibarıyla en temiz lisanslı, en geniş yetenekli açık video modeli.
- **Nerede kullanılabilir?** `ai-job-gateway`'in ikinci `Provider`'ı (video capability).
- **Alternatifler:** LTX-2 (daha hızlı, daha kısa/uzun klip esnekliği), HunyuanVideo (🔴 reddedildi — bkz. aşağı), CogVideoX-2B (ücretsiz katman için).
- **Avantaj:** Lisans temiz, yetenek geniş. **Dezavantaj:** 14B modeller ≥80GB VRAM gerektiriyor — self-host maliyeti yüksek, hosted API (fal.ai/Replicate) ile başlamak daha mantıklı.
- **Lisans notu:** Apache 2.0 — tamamen güvenli.
- **Kendi çözüm mü?** Mevcut çözüm, hosted API üzerinden.
- **Prototip gerekli mi?** Evet, ama API key/bütçe gerektiriyor — ertelendi.
- **Öncelik:** P2 (görsel öncelikli, video ikinci sırada)

---

## 🔴 HunyuanVideo (Tencent) — Video üretim (Reddedildi)

- **Ne işe yarıyor?** Yüksek kaliteli video difüzyon modeli, bazı benchmark'larda Wan2.2'yi geçiyor.
- **Neden reddedildi?** Lisansı **100M MAU tavanı + AB/UK/Güney Kore hariç tutma** içeriyor. Büyüme hedefleyen ve global kullanıcı tabanına açık bir platform için gerçek hukuki risk.
- **Alternatif:** Wan2.2 (🟢 benimsendi) aynı yetenek genişliğini temiz lisansla sunuyor.
- **Not:** Sadece bu kısıtların dışında kalan pazarlara özel bir ürün için yeniden değerlendirilebilir — genel ekosistem için değil.

---

## 🟢 MuseTalk (Tencent) + LatentSync (ByteDance) — Lip-sync

- **Ne işe yarıyor?** MuseTalk: gerçek-zamanlı yakın hızda latent-uzay lip-sync (MIT). LatentSync: tam difüzyon tabanlı, en yüksek kalite (Apache 2.0), daha yavaş.
- **Neden önemli?** İkisi birlikte hız/kalite ekseninin iki ucunu kapsıyor — `ai-job-gateway`'de iki ayrı capability (`lipsync-fast`, `lipsync-quality`) olarak doğal bir eşleşme.
- **Nerede kullanılabilir?** Üçüncü `Provider` çifti.
- **Alternatifler:** Wav2Lip (🔴 reddedildi, ticari olmayan lisans), Ditto (⚪ izleniyor — Apache 2.0, gerçek-zamanlı, MuseTalk'a rakip olabilir, henüz derinlemesine denenmedi).
- **Avantaj:** Her ikisi de commercial-friendly. **Dezavantaj:** Self-host için GPU gerektiriyor (LatentSync 8-18GB VRAM).
- **Lisans notu:** MIT / Apache 2.0 — güvenli.
- **Kendi çözüm mü?** Mevcut çözüm.
- **Prototip gerekli mi?** Evet, API key/GPU erişimi netleştiğinde.
- **Öncelik:** P2

---

## 🟢 ComfyUI — Çalıştırma motoru (gelecekteki self-host katmanı için)

- **Ne işe yarıyor?** Node-graph tabanlı difüzyon/video/ses çalıştırma motoru; iş akışı JSON olarak serileştirilir.
- **Neden önemli?** Ekosistemin araştırdığı hemen her modelin (FLUX, Wan2.2, MuseTalk) gün-1 desteği var; "workflow = job tanımı" deseni `ai-job-gateway`'in `params` şeklinin ilham kaynaklarından biri.
- **Nerede kullanılabilir?** Self-host'a geçildiğinde `ai-job-gateway`'in arkasındaki gerçek çalıştırma motoru (RunPod/Modal + ComfyUI kombinasyonu, araştırmada "en hızlı MVP yolu" olarak işaretlendi).
- **Alternatifler:** Doğrudan `diffusers`/model-özel kod yazmak (daha fazla kontrol, çok daha fazla mühendislik yükü).
- **Avantaj:** Model kapsamı geniş, topluluk büyük. **Dezavantaj:** GPL-3.0 — sadece iç servis olarak çalıştırıldığı sürece güvenli, değiştirilmiş bir dağıtımı üçüncü taraflara vermek ayrı bir hukuki inceleme gerektirir.
- **Lisans notu:** GPL-3.0, dikkatli kullanım (bkz. yukarıda).
- **Kendi çözüm mü?** Mevcut çözüm — kendi çalıştırma motorumuzu yazmak şu an için gereksiz mühendislik olur.
- **Prototip gerekli mi?** Henüz değil — self-host eşiği (`BACKLOG.md`) tetiklenene kadar erteleniyor.
- **Öncelik:** P3 (şimdilik hosted API'ler yeterli)

---

## 🟢 Python + `uv` + FastAPI + Jinja2 — Backend/CLI stack

- **Ne işe yarıyor?** Ekosistemin tüm yeni backend/CLI repolarının (`ai-job-gateway`, `prompt-template-manager`, `model-comparison-harness`) ortak stack'i.
- **Neden önemli?** Tutarlılık — tek bir kurulum/test/CI deseni her repoda tekrarlanabiliyor, öğrenme eğrisi tek seferlik.
- **Alternatifler:** Node/TypeScript (reddedildi — ekosistemin geri kalanıyla tutarsız), Go (daha hızlı ama ekip için gereksiz ikinci dil).
- **Avantaj:** Hızlı geliştirme, `uv`'nin hızlı dependency resolution'ı, FastAPI'nin otomatik OpenAPI şeması. **Dezavantaj:** Python'un GIL'i yüksek eşzamanlılıkta bir tavan oluşturabilir — şimdilik (I/O-bound job orkestrasyonu) sorun değil.
- **Lisans notu:** Hepsi MIT/BSD-türü, sorun yok.
- **Kendi çözüm mü?** N/A — dil/framework seçimi.
- **Prototip gerekli mi?** Hayır, zaten üç repoda kanıtlandı.
- **Öncelik:** Benimsendi, değişiklik gerekmiyor.

---

# 3D Üretim ve Segmentasyon (2026-08-31 eklendi)

## ⚪ TRELLIS / TRELLIS.2 (Microsoft) — Görüntüden 3D üretim

- **Ne işe yarıyor?** "Structured Latents" (SLAT) tabanlı 3D üretim ailesi; tek görüntüden mesh, radiance field ve 3D Gaussian Splat çıktısını aynı temsilden üretebiliyor. TRELLIS.2 (4B parametre) PBR malzeme haritaları da ekliyor.
- **Neden önemli?** Açık kaynak image-to-3D'de mimari olarak en esnek seçenek — InstantMesh/TripoSR'a göre daha temiz topoloji, oyun motoruna doğrudan giren PBR haritaları.
- **Nerede kullanılabilir?** `ai-job-gateway`'e üçüncü capability (`3d-generation`) — `ai-workflow-engine` ile görsel üretim → 3D dönüşüm zinciri kurulabilir.
- **Alternatifler:** Hunyuan3D-2.1 (🔴 reddedildi), InstantMesh, TripoSR, SAM 3D Objects, hosted API (Meshy/Rodin).
- **Avantaj:** MIT lisans, çıktı formatı esnekliği, düşük-VRAM (GGUF, 6-8GB) modları mevcut. **Dezavantaj:** Tam kalite için 40GB+ VRAM — self-host pahalı.
- **Lisans notu:** MIT — tamamen güvenli (doğrudan `microsoft/TRELLIS/LICENSE`'dan doğrulandı).
- **Kendi çözüm mü, mevcut mu?** Mevcut çözüm.
- **Prototip gerekli mi?** Henüz değil — `ai-job-gateway`'de görsel/video provider'ları bile mock durumda, 3D daha erken bir aşama.
- **Öncelik:** P2

---

## 🔴 Hunyuan3D-2.1 (Tencent) — Görüntüden 3D üretim (Reddedildi)

- **Ne işe yarıyor?** Şekil üretimi + gerçek PBR doku boyama; açık kaynakta en iyi PBR doku kalitesi.
- **Neden reddedildi?** Lisans metni doğrulandı: **AB/UK/Güney Kore hariç tutuluyor + 1M MAU tavanı** — `TECH-RADAR.md`'de zaten reddedilen HunyuanVideo ile birebir aynı Tencent lisans şablonu. Ayrıca "çıktı başka bir AI modeli eğitmek için kullanılamaz" maddesi `model-comparison-harness` için ayrı bir risk.
- **Alternatif:** TRELLIS/TRELLIS.2 — benzer/üstün esneklik, temiz MIT lisans.
- **Not:** Tencent'in 3D ve video modellerinde aynı kısıtlayıcı şablonu tekrarlaması artık bir örüntü — Tencent-Hunyuan ailesinden her yeni model varsayılan olarak şüpheyle kontrol edilmeli.
- **Öncelik:** N/A (reddedildi)

---

## ⚪ TripoSR / InstantMesh / SAM 3D Objects — Diğer 3D üretim seçenekleri (izleniyor)

- **TripoSR** (Stability AI + Tripo AI): MIT, saniyenin altında hızlı mesh üretimi ama kaotik topoloji — sadece hızlı önizleme için uygun. **Dikkat:** halefi Stable Fast 3D farklı ve kısıtlayıcı bir lisansa sahip (Community License, $1M gelir üstü kurumsal lisans zorunlu), TripoSR ile karıştırılmamalı. P3.
- **InstantMesh** (TencentARC): Apache 2.0 (Hunyuan3D'nin aksine Tencent'in kısıtlayıcı şablonunu kullanmıyor), hız/kalite dengesi orta, sadece mesh çıktısı. P3.
- **SAM 3D Objects** (Meta, Kasım 2025): Çok yeni, tıkanık sahnelerde bile tam rekonstrüksiyon iddiası; Meta'nın özel "SAM License"ı (Apache'ye benzer ama askeri/ITAR kısıtları var). Olgunluk henüz sınırlı, izlemede kalıyor. P3.
- **Hosted API alternatifi:** Meshy (Pro $20/ay + kredi, ~$0.60/model) ve Rodin/Hyper3D (Business $120/ay veya fal.ai üzerinden ~$0.40-0.50/generation) — self-host GPU maliyeti olmadan MVP için uygun, FLUX/Wan2.2'deki "önce hosted API" desenine uygun. `ai-job-gateway`'in ilk gerçek 3D provider'ı muhtemelen bunlardan biri olmalı, self-host TRELLIS değil.

---

## 🟢 BiRefNet — Yüksek çözünürlüklü arka plan kaldırma

- **Ne işe yarıyor?** İki paralel dal (kaba konum + ince yapı: saç teli, kürk, yarı-saydam kenar) + füzyon mimarisiyle yüksek-çözünürlüklü segmentasyon.
- **Neden önemli?** `mini-creative-toolkit`'in kullandığı `rembg` kütüphanesi BiRefNet'i zaten paketli sunuyor — yeni bağımlılık gerektirmiyor. **2026-08-31'de uygulandı:** `remove_background()`'a opsiyonel `model` parametresi eklendi (bkz. `mini-creative-toolkit` commit `74d5dad`). Bu değişiklik sırasında ayrıca daha kritik bir bulgu ortaya çıktı — bkz. RMBG-2.0 girdisi aşağıda.
- **Nerede kullanılabilir?** `mini-creative-toolkit::remove_background(image_path, model="birefnet-general")` — opt-in, varsayılan değil (ölçülen gerçek maliyet aşağıda).
- **Alternatifler:** u2net (mevcut varsayılan, hızlı ama kaba kenar), InSPyReNet (ince yapılarda özel avantajlı, ayrı bağımlılık gerektiriyor), BEN2, RMBG-2.0 (🔴 reddedildi), SAM 2/3 (farklı problem sınıfı).
- **Avantaj:** MIT, zaten paketli, ölçülebilir kalite artışı (saç/kürk kenarlarında). **Dezavantaj — doğrudan ölçüldü:** bu sandbox'ta bir `birefnet-general` session'ının soğuk yüklenmesi tek başına 100 saniyeyi aştı (zaman aşımına uğradı) — bu yüzden varsayılan yapılmadı, opt-in bırakıldı. Üretim ortamında (daha hızlı ağ/disk) bu süre çok daha kısa olabilir ama "ücretsiz yükseltme" iddiası doğrulanmadan varsayılan yapmak riskliydi.
- **Lisans notu:** MIT — tamamen güvenli.
- **Kendi çözüm mü, mevcut mu?** Mevcut çözüm, entegre edildi (opt-in).
- **Prototip gerekli mi?** Hayır, tamamlandı.
- **Öncelik:** P1 → ✅ Uygulandı (opt-in olarak)

---

## 🔴 RMBG-2.0 (BRIA AI) — Arka plan kaldırma (Reddedildi) — GERÇEK, ZATEN AKTİF BİR RİSKTİ

- **Ne işe yarıyor?** BRIA AI'nin ticari-kalite arka plan kaldırma modeli, `rembg` içinde `bria-rmbg` session'ı olarak paketli.
- **Neden reddedildi — ve neden bu bir teorik değil GERÇEK bulgu:** Model ağırlıkları CC BY-NC 4.0 (sadece ticari olmayan kullanım). Araştırma bunu teorik bir tuzak olarak işaretlemişti, ama BiRefNet entegrasyonu sırasında **doğrudan doğrulandı**: `rembg` 2.0.81'in `remove(data, session=None)` iç mekanizması artık **varsayılan olarak `bria-rmbg`'ye çözümleniyor** (`u2net`'e değil, genel kabul edilenin aksine) — yani `mini-creative-toolkit`'in `remove_background()` fonksiyonu, hiçbir kod değişikliği olmadan, sadece bir `rembg` sürüm güncellemesiyle, sessizce ticari olmayan lisanslı bir modele geçmiş durumdaydı. **Bu, "iyi görünen ama ticari olmayan lisans" tuzağının teorik değil, bu ekosistemde zaten gerçekleşmiş somut bir örneği.**
- **Düzeltme:** `mini-creative-toolkit` commit `74d5dad` — artık her zaman açık bir `new_session(model)` çağrısı yapılıyor (varsayılan `model="u2net"`), rembg'nin kendi iç varsayılanına asla güvenilmiyor.
- **Alternatif:** BiRefNet (🟢 yukarıda) — MIT lisanslı, aynı kalite sınıfında.
- **Ders:** Bir bağımlılığın (`rembg`) İÇİNDEKİ bir alt-modelin lisansı, o bağımlılığın kendi lisansından (rembg = MIT) tamamen bağımsızdır ve bir sürüm güncellemesiyle sessizce değişebilir. Kritik yol (`remove_background` gibi lisans-hassas fonksiyonlar) için "varsayılan davranış" asla örtük bırakılmamalı, her zaman açıkça hangi alt-modelin çağrıldığı koda yazılmalı.
- **Öncelik:** N/A (reddedildi) — ama bu bulgu `DECISIONS.md`'ye ayrı bir ADR olarak da düşüldü (ADR-009).

---

## ⚪ InSPyReNet / BEN2 / SAM 2 / SAM 3 — Diğer segmentasyon seçenekleri (izleniyor)

- **InSPyReNet** (`transparent-background`): MIT, ince yapılarda (tel, saçak) BiRefNet'i geçebiliyor ama ayrı bağımlılık gerektiriyor (rembg içinde paketli değil). P3.
- **BEN2** (PramaLLC): MIT (Base model), saç/kürk odaklı, ayrı entegrasyon gerektiriyor — hangi checkpoint'in gerçekten MIT olduğu dikkatle doğrulanmalı. P3.
- **SAM 2 / SAM 3**: Farklı bir problem sınıfı çözüyor — BiRefNet "tek özneyi otomatik kes", SAM ailesi "kullanıcının işaret ettiği/adlandırdığı HERHANGİ bir nesneyi (video boyunca takip ederek) seç". SAM 2 Apache 2.0 (temiz), SAM 3/3.1 Meta'nın özel "SAM License"ı (ticari kullanıma izin veriyor, askeri/ITAR istisnası var). Bugünkü kullanım deseni için gereksiz — gelecekte bir "canvas" ürününde etkileşimli çoklu-nesne seçimi gerekirse asıl aday. P3 (izleme).

---

# Ses / Müzik / Konuşma Üretimi ve Karakter/Yüz Tutarlılığı (2026-08-31 eklendi)

## 🟡 ACE-Step 1.5 — Metinden müzik üretimi

- **Ne işe yarıyor?** Diffusion tabanlı, uçtan uca müzik üretimi — enstrümantal + vokal (şarkı sözü hizalamalı), LoRA ile kişiselleştirme.
- **Neden önemli?** Kalite iddiaları güçlü, aşırı hafif (RTX 3090'da tam şarkı ~10sn, 4GB altı VRAM). Vokal+enstrümantal birlikte üreten nadir açık modellerden biri.
- **Nerede kullanılabilir?** `ai-job-gateway`'e dördüncü capability (`music-generation`) — self-host maliyeti düşük, API key beklemeden prototiplenebilir.
- **Alternatifler:** Stable Audio Open (enstrümantal, kaynak-şeffaf ama gelir tavanlı), MusicGen (🔴 reddedildi), YuE (henüz incelenmedi).
- **Avantaj:** Apache 2.0, hızlı, düşük VRAM, ticari kullanım serbest. **Dezavantaj:** Genç proje, eğitim verisi telif zinciri şeffaflığı büyük laboratuvarlar kadar net değil.
- **Lisans notu:** Apache 2.0 (kod+ağırlık) — ticari çıktı kullanımına izin veriyor.
- **Kendi çözüm mü?** Mevcut çözüm.
- **Prototip gerekli mi?** Evet — düşük maliyetli, API key gerekmiyor.
- **Öncelik:** P1

---

## 🟡 Stable Audio Open (Stability AI) — Metinden müzik/ses efekti

- **Ne işe yarıyor?** Enstrümantal müzik + kısa ses efekti üretimi; 3.0 sürümü 6dk20sn'ye kadar stereo çıktı.
- **Neden önemli?** Eğitim verisi kaynağı (AudioSparx lisanslı + Freesound CC) açıkça belgelenmiş — ACE-Step'in belirsizliğine karşı önemli bir fark.
- **Nerede kullanılabilir?** Ayrı bir `sfx-generation` capability'si; ACE-Step'in yanında "temiz kaynaklı ama gelir tavanlı" alternatif.
- **Alternatifler:** ACE-Step (vokal de üretiyor, tavan yok), MusicGen (reddedildi).
- **Avantaj:** Kaynak şeffaf, ~7GB VRAM ile self-host edilebilir. **Dezavantaj:** $1M yıllık gelir tavanı var — ekosistem büyüdüğünde ayrı ticari lisans gerekir; vokal üretemiyor.
- **Lisans notu:** Stability AI Community License — $1M altı ücretsiz, üstü ayrı anlaşma gerekiyor. Büyüme senaryosu için izleme noktası.
- **Kendi çözüm mü?** Mevcut çözüm.
- **Prototip gerekli mi?** Evet, ACE-Step ile paralel.
- **Öncelik:** P2

---

## 🔴 MusicGen / AudioCraft (Meta) — Metinden müzik (Reddedildi)

- **Neden reddedildi?** Kod MIT ama **model ağırlıkları CC-BY-NC 4.0** — ticari üründe kullanılamaz. HunyuanVideo ile aynı risk kategorisi.
- **Alternatif:** ACE-Step ve Stable Audio Open aynı yetenek alanını ticari lisanslarla kapsıyor.
- **Öncelik:** N/A (reddedildi)

---

## 🟢 Kokoro-82M — Metinden konuşma (klonlama hariç)

- **Ne işe yarıyor?** 82M parametreli, çok küçük ama TTS Arena'da üst sıralarda; önceden tanımlı ses setiyle çalışıyor, klonlama desteklemiyor.
- **Neden önemli?** FLUX.2 `klein` ile aynı "hızlı/ucuz katman" felsefesi — Apache 2.0, tavan yok, neredeyse gerçek-zamanlı (A100'de RTF ~0.03).
- **Nerede kullanılabilir?** `ai-job-gateway`'de "hızlı/ücretsiz TTS katmanı" (`tts-fast`) — klonlama gerekmeyen tüm seslendirme ihtiyaçlarının varsayılanı.
- **Alternatifler:** F5-TTS/Chatterbox (klonlama destekli, daha ağır), XTTS-v2 (reddedildi), hosted API'ler.
- **Avantaj:** En düşük VRAM/gecikme, tam ticari kullanım. **Dezavantaj:** Klonlama yok, ses çeşitliliği sınırlı.
- **Lisans notu:** Apache 2.0 — tam güvenli.
- **Kendi çözüm mü?** Mevcut çözüm.
- **Prototip gerekli mi?** Evet — düşük maliyet, API key gerekmiyor.
- **Öncelik:** P1

---

## 🟢 Chatterbox (Resemble AI) — Metinden konuşma + ses klonlama (watermark'lı)

- **Ne işe yarıyor?** 23+ dilde sıfır-atış ses klonlama (5sn referans), duygu/abartı kontrolü, her üretimde yerleşik PerTh watermark.
- **Neden önemli?** Listedeki **kötüye kullanım engelleme mekanizması yerleşik olan tek model** — ses klonlama gibi hassas bir alanda "sorumlu varsayılan". Kör dinleme testlerinde ElevenLabs'e tercih edildiği raporlanıyor.
- **Nerede kullanılabilir?** `tts-clone` capability'si için **birincil aday** — yerleşik watermark rıza/kötüye kullanım riskini azaltıyor.
- **Alternatifler:** F5-TTS (watermark yok), OpenVoice V2, XTTS-v2 (reddedildi).
- **Avantaj:** MIT, watermark yerleşik, çok-dilli, Resemble AI arkasında (sürdürülebilirlik sinyali). **Dezavantaj:** Watermark kötüye kullanımı tamamen engellemiyor (caydırıcı + adli iz), 8GB+ VRAM gerekiyor.
- **Lisans notu:** MIT — hem kod hem ağırlık.
- **Kendi çözüm mü?** Mevcut çözüm.
- **Prototip gerekli mi?** Evet — ama **rıza akışı olmadan üretime yaklaştırılmamalı** (bkz. aşağıdaki P0 madde).
- **Öncelik:** P1

---

## 🟡 F5-TTS / OpenVoice V2 — Klonlama alternatifleri (izleniyor/değerlendiriliyor)

- **F5-TTS** (SWivid): MIT (resmi repo teyitli — bazı ikincil kaynaklar hâlâ yanlış CC-BY-NC iddiası taşıyor, dikkat), ~3sn referansla klonlama, RTF~3 (gerçek-zamanlı değil, sadece batch), **watermark yok**. P2.
- **OpenVoice V2** (MyShell): MIT (V1+V2), ton/tını transferi odaklı farklı mimari, watermark yok, topluluk ivmesi Chatterbox kadar güçlü değil. P3.

---

## 🔴 Coqui XTTS-v2 — Metinden konuşma + klonlama (Reddedildi)

- **Neden reddedildi?** Ağırlıklar CPML 1.0.0 (ticari olmayan). **Coqui Inc. Ocak 2024'te kapandı** — önceden mevcut ticari lisans satın alma yolu da artık yok. Şu an hiçbir yasal yoldan ticari kullanılamıyor.
- **Alternatif:** Chatterbox ve F5-TTS aynı yetenek sınıfını ticari lisanslarla sunuyor.
- **Not:** Kalite referansı olarak (araştırma/kıyaslama) değerli olabilir, üretime asla alınmamalı.
- **Öncelik:** N/A (reddedildi)

---

## ⚪ Ses Klonlama — Rıza/Etik/Kötüye Kullanım Politikası (domain-genelinde kısıt, teknoloji değil)

- **Neden önemli?** Ses klonlama, diğer domain'lerden farklı olarak doğrudan gerçek bir kişinin kimliğini taklit ediyor. AB AI Act Madde 50 (2 Ağustos 2026 yürürlükte), ABD Tennessee ELVIS Act, ElevenLabs'in rıza doğrulama + "no-go voices" mekanizmaları — düzenleyici ortam hızla sıkılaşıyor. Klonlanmış sesler zaten finansal dolandırıcılık vakalarında kullanıldı.
- **Gereksinim:** `tts-clone` capability'sinin API sözleşmesine zorunlu alan olarak: (1) rıza onayı + doğrulama adımı, (2) her klon çıktısına watermark/audit-trail, (3) tanınmış kamu figürü isimleriyle eşleşen taleplere ekstra sürtünme.
- **Öncelik:** **P0 — klonlama özelliği için blokaj, teknoloji seçiminden bağımsız, önce bu karar netleşmeli.** ADR-009 olarak kaydedildi.

---

## 🟢 IP-Adapter — Görsel referanslı stil/genel görünüm koşullandırma

- **Ne işe yarıyor?** Referans görselin CLIP embedding'ini difüzyon modelinin cross-attention katmanına enjekte eden hafif adaptör — modeli yeniden eğitmeden çalışıyor.
- **Neden önemli?** En olgun/yaygın temel teknik, PuLID/InstantID gibi daha spesifik yöntemlerin üzerine inşa edildiği mimari.
- **Nerede kullanılabilir?** Genel "referans görsele benzer üret" ihtiyacı; saf yüz kimliği için PuLID/InstantID daha güçlü.
- **Alternatifler:** PuLID (yüz kimliği için daha güçlü), FLUX.2'nin kendi çoklu-referans desteği.
- **Avantaj:** Hafif, hızlı, geniş model desteği (SD1.5/SDXL/FLUX), temiz lisans. **Dezavantaj:** Saf yüz kimliğinde PuLID'e göre zayıf.
- **Lisans notu:** Apache 2.0 (düz IP-Adapter). **İstisna:** IP-Adapter-**FaceID** varyantı InsightFace embedding'ine dayanıyor — sadece araştırma amaçlı, ticari kullanım yasak. Düz (CLIP tabanlı) varyant bu kısıttan etkilenmiyor.
- **Kendi çözüm mü?** Mevcut çözüm.
- **Prototip gerekli mi?** Hayır, olgun; asıl kıyaslama PuLID-FLUX ile yapılmalı.
- **Öncelik:** P2

---

## 🟡 PuLID / PuLID-FLUX — Ayarsız yüz kimliği özelleştirme

- **Ne işe yarıyor?** Kontrastif hizalama ile kimlik-koruyan üretim; IP-Adapter'ın CLIP-tabanlı yaklaşımına göre hem kimlik sadakati hem prompt uyumu (editability) dengesini daha iyi kuruyor.
- **Neden önemli?** FLUX.2 için resmi/topluluk desteği zaten mevcut (`iFayens/ComfyUI-PuLID-Flux2`, Klein 4B/9B ve Dev destekli, "plug-and-play").
- **Nerede kullanılabilir?** `character-consistency` alt-özelliği — FLUX.2 provider'ının üzerine eklenecek katman.
- **Alternatifler:** InstantID (reddedildi), IP-Adapter (daha hafif, daha zayıf), FLUX.2 yerleşik çoklu-referans.
- **Avantaj:** FLUX.2 ile doğrudan uyumlu, IP-Adapter'dan güçlü kimlik koruma, kod Apache 2.0. **Dezavantaj:** InsightFace + EVA-CLIP kullanıyor — **IP-Adapter-FaceID/InstantID ile aynı lisans riski taşıma potansiyeli, doğrulanmamış.** VRAM: FP8 ile 11-16GB, bf16 ile 45GB'a kadar.
- **Lisans notu:** Kod Apache 2.0. **Kritik açık soru:** InsightFace bağımlılığının ticari kısıt getirip getirmediği doğrulanmalı — InstantID'nin başına gelen tam olarak bu oldu.
- **Kendi çözüm mü?** Mevcut çözüm.
- **Prototip gerekli mi?** Evet — hem teknik kalite hem InsightFace lisans zincirinin doğrulanması için. **Lisans netleşmeden üretime alınmamalı.**
- **Öncelik:** P1 (lisans doğrulaması P0 önceliğinde ele alınmalı)

---

## 🔴 InstantID — Ayarsız yüz kimliği özelleştirme (Reddedildi)

- **Neden reddedildi?** (1) Kod Apache 2.0 ama InsightFace yüz embedding'i (AntelopeV2/buffalo_l) sadece ticari olmayan araştırma için — checkpoint'ler de "sadece araştırma amaçlı" işaretli. (2) SDXL'e özel tasarlandı, FLUX portları kararsız/olgunlaşmamış — FLUX.2 kararıyla çelişiyor.
- **Alternatif:** PuLID-FLUX (aynı problem sınıfını FLUX.2 ile çözüyor, ama InsightFace riski orada da doğrulanmalı), IP-Adapter (düz varyant, lisans temiz ama kimlik sadakati zayıf).
- **Öncelik:** N/A (reddedildi) — SDXL hattı açılır ve InsightFace'ten ticari lisans alınabilirse yeniden değerlendirilebilir.

---

## ⚪ FLUX.2 Yerleşik Çoklu-Referans Desteği — Karakter/ürün/sahne tutarlılığı

- **Ne işe yarıyor?** FLUX.2, harici adaptör eklemeden, modelin kendi mimarisinde en fazla 10 referans görsele kadar destekliyor — karakter/ürün/kamera/ışık kurulumunu "kilitleyip" tutarlı seri üretebiliyor.
- **Neden önemli?** Eğer yeterli kalite veriyorsa PuLID/IP-Adapter gibi ek adaptörlere hiç gerek kalmayabilir — InsightFace lisans riskini tamamen ortadan kaldırır, mimariyi basitleştirir.
- **Nerede kullanılabilir?** Karakter tutarlılığı ihtiyacının **ilk denenmesi gereken yolu** — mevcut `FluxProvider` üzerine ek bağımlılık olmadan, sadece çoklu referans görsel parametresiyle test edilebilir.
- **Alternatifler:** PuLID-FLUX (muhtemelen daha güçlü ama lisans riski taşıyor), IP-Adapter.
- **Avantaj:** Ek bağımlılık yok, lisans zinciri tamamen FLUX.2'nin kendi lisansına bağlı (InsightFace riski sıfır), muhtemelen en düşük entegrasyon karmaşıklığı. **Dezavantaj:** Henüz PuLID ile doğrudan kalite karşılaştırması yok; `klein` (4B) katmanında yeterliliği belirsiz.
- **Lisans notu:** FLUX.2'nin kendi lisans katmanına tabi (klein: Apache 2.0).
- **Kendi çözüm mü?** Mevcut çözüm — model zaten benimsendi, sadece bu yetenek test edilmeli.
- **Prototip gerekli mi?** Evet — **PuLID-FLUX'tan önce** denenmeli; yeterliyse InsightFace lisans sorunu baştan kaçınılmış olur.
- **Öncelik:** P1 (PuLID prototipinden önce)
