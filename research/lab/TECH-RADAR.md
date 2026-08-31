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
