# Tasarım Sistemi Araştırması — Yaratıcı-AI Ürün UX

Bu dosya, ürünün (henüz inşa edilmemiş) frontend/UI katmanı için araştırma girdisidir. `KISISEL-SITE-PLANI.md`'deki ayrı kişisel-site iş akışına dokunmaz — konusu üründür, portfolyo sitesi değil. `BACKLOG.md`'deki "Design system / frontend component library" (P2) maddesinin başlangıç araştırmasıdır.

Son güncelleme: 2026-08-31 (Faz 3 — R&D lab derinleştirme)

---

## Çekirdek çerçeve: bu ürün "sohbet" veya "form" değil, "job" arayüzü

Ekosistemin temel etkileşim döngüsü (`ai-job-gateway`'in submit/poll kontratı, ADR-001) **asenkron/job-tabanlı**: kullanıcı bir istek gönderir, sistem kuyruğa alır/işler, sonuç saniyeler ile dakikalar arasında bir gecikmeyle gelir. Referans ürünleri değerlendirirken kullanılacak tek en önemli mercek: görsel cila değil, **"bekleme/kuyruk/ilerleme durumunu nasıl yönetiyorlar"** sorusu.

---

## 1. Referans ürünler — iş temelli etkileşim modeli değerlendirmesi

| Ürün | Kuyruk/bekleme şeffaflığı | Mühendislik maliyeti | Taşınabilirlik |
|---|---|---|---|
| **Midjourney** | Yüksek — Fast/Relax ikili kota + net süre beklentisi | Düşük (iki kuyruk sınıfı + kota UI'ı) | **Yüksek — P1** |
| **Krea.ai** | Kuyruğu görünmez kılıyor (<50ms gerçek-zamanlı önizleme, submit/spinner yok) | Yüksek (özel düşük-gecikme altyapısı) | Düşük (tam hali); **Orta** (progressive-preview deseni olarak) |
| **Leonardo.ai** | Orta — plan-bağımlı kuyruk ("Priority Queue"), galeri/remix | Düşük-orta | **Orta-Yüksek** |
| **Ideogram** | Düşük görünürlük ama süre zaten kısa (10-15sn), "yaz ve git" sadeliği | Çok düşük (tek buton, batch sonuç) | **Yüksek** — sade prompt kutusu deseni |
| **Runway (Apps/Workflows)** | Orta, near-real-time feedback | Yüksek (graph motoru) ama paylaşılan workflow paketleme ucuz | **Yüksek** — "App Mode" deseni |
| **ComfyUI** | Düşük — ham node graph, dik öğrenme eğrisi, minimal kuyruk UI'ı | Teknik güç yüksek, UX maliyeti kullanıcıya yükleniyor | **Orta** — "App Mode" dersi: graph'ı gizle, sadece ilgili kontrolleri göster |
| **ElevenLabs** | Orta — modalite-özgü bekleme göstergeleri (waveform yüklenme) | Düşük — **açık kaynak `elevenlabs-ui`, shadcn/ui üzerine kurulu** | **Yüksek** — doğrudan teknik temel emsali |

**En değerli iki ders:**
1. **Runway/ComfyUI "App Mode" deseni** — güçlü bir iç graph motorunu (`ai-workflow-engine`'in DAG'ı) son kullanıcıya sadece ilgili parametreleri gösteren sade bir form olarak sunmak. İç mimari graph, dış yüz basit form.
2. **ElevenLabs zaten shadcn/ui üzerine kendi tasarım sistemini açık kaynak yapmış** — bu, aşağıdaki teknik öneri için doğrudan bir alan-emsali/kanıt.

Krea'nın gerçek-zamanlı canvas'ı yüksek algısal değerli ama egzotik altyapı gerektiriyor — **ruhu** ucuza taşınabilir: kaba/hızlı bir önizleme job'ı + arkada tam-kaliteli job'ı ardışık tetiklemek (`ai-workflow-engine`'in DAG deseniyle doğrudan örtüşüyor).

---

## 2. Tasarım sistemi temelleri (bu ürün şekli için)

**Genel SaaS dashboard'undan farkı:** İçerik (görsel/video/ses) birincil vatandaş (tablo/form değil); karanlık tema varsayılan eğilimde (üretilen renkli içeriği öne çıkarıyor — Midjourney/Krea/Leonardo/ElevenLabs hepsi koyu birincil); bekleme/yükleme durumu kenar değil **merkezi** durum (dakikalar sürebilir).

**Token önerisi:**
- **Tipografi:** UI metni için nötr grotesk (Inter/Geist), display font sadece boş-durum/onboarding'de (üretim ekranında dikkat medyaya gitmeli).
- **Renk:** OKLCH tabanlı (Tailwind v4 varsayılanı), durum renkleri (queued/processing/success/error) modalite-bağımsız tutarlı, tek vurgu rengi — üretilen içerik zaten renk çeşitliliği getiriyor.
- **Spacing:** Standart 4/8px + ayrı bir "galeri/canvas" ölçeği (`aspect-ratio` ile responsive medya grid'i).
- **Motion:** Job durumu geçişleri için tutarlı dil (skeleton/pulse → fade+scale-in), `prefers-reduced-motion` zorunlu (`kalp-animasyon` repo'sundaki teknik borç dersi tasarım sistemine baştan gömülmeli).

**Alana özgü etkileşim desenleri:**
1. Prompt girişi — Ideogram'ın "tek kutu + generate" sadeliği varsayılan, ileri parametreler progressive disclosure ile.
2. Parametre kontrolleri — aspect ratio preset-buton grid'i, seed kilitle/rastgele toggle, slider+sayısal girdi birlikte.
3. Sonuç galerisi — değişken en-boy oranlı masonry/grid hibriti, hover'da meta veri.
4. **Karşılaştırma görünümü** — `model-comparison-harness` için Arena-tarzı kör yan-yana UI; backend zaten latency/success ölçüyor, kalite-oylama verisi de toplanabilir hale gelir.
5. Öncesi/sonrası — kaydırmalı slider (upscale/bg-removal/lip-sync gibi "düzenleme" job'ları için).
6. Yükleniyor durumları — süreye göre 3 seviye (<5sn spinner, 5sn-1dk ilerleme+adım metni, >1dk arka plan bildirimi+kuyruk paneli); **optimistic UI** (submit anında kart hemen listeye eklenir).
7. **Hata durumları (en sık atlanan alan)** — genel "Generation failed" yetersiz: (a) içerik politikası ihlali → düzenleme yönlendirmesi, retry yok; (b) geçici hata (502/503/429) → üstel geri çekilmeyle otomatik retry; (c) parametre hatası → retry yok, forma dön.

**Erişilebilirlik:** Büyük medya önizlemeleri mobilde tam genişlik, kontrol paneli ayrı drawer'a; uzun job'lar için push/e-posta fallback; durum renkleri ikon+metin ile de ayrışmalı (WCAG); `prefers-reduced-motion` canlı dinlenmeli.

---

## 3. Teknik altyapı önerisi

- **Next.js (App Router) + React + TypeScript** — FastAPI backend'lerle temiz API sınırı, yaygın/iyi belgelenmiş eşleşme.
- **TanStack Query** — submit/poll döngüsü `useQuery` + `refetchInterval` desenine tam oturuyor; çoklu-job kuyruğu senaryosu için SWR'den daha uygun (zengin cache/mutation yönetimi).
- **Tailwind CSS v4 + shadcn/ui** — ElevenLabs emsali + 2026 endüstri konsensüsü. shadcn/ui'nin "kopyala-yapıştır, npm bağımlılığı değil" modeli, ekosistemin "vendored shared code" felsefesiyle örtüşüyor (ADR-008'in `gateway_poll.py` vendoring kararıyla aynı ruh).
- **Bespoke vs hazır:** Genel form/panel/tablo için shadcn/ui yeterli; **bespoke olması gereken tek katman** medya galerisi, job durumu kartları, karşılaştırma (arena) görünümü, ve ileride canvas editörü (React Flow — araştırma raporunda zaten işaretli, ayrı ve daha büyük bir sonraki-faz kararı).
- Bu ortamın kendi `ui-ux-pro-max`/`tailwind-design-system` skill'leriyle metodolojik olarak örtüşüyor — çelişki yok.

---

## Öncelikli Öneriler

| # | Öneri | Öncelik | Gerekçe |
|---|---|---|---|
| 1 | Token seti tanımı (tipografi/renk/spacing/motion) — Tailwind v4 `@theme` + OKLCH, kişisel site planıyla paylaşılan temel | **P1** | Tek seferlik, düşük efor, her sonraki UI kararını hızlandırır |
| 2 | Job durumu bileşen ailesi (queued/processing/done/error kartı + optimistic submit + kuyruk paneli) | **P1** | Ekosistemin temel gerekliliği — submit/poll kontratı zaten var, doğru yapılmazsa tüm ürün "neden bekliyorum" belirsizliğiyle kırılgan hisseder |
| 3 | shadcn/ui + Tailwind v4 temelli bileşen kütüphanesi (ElevenLabs UI emsaline dayanarak) | **P1** | Jenerik problemleri "çözülmüş" kabul edip efor domain-özgü parçalara yönlendirilir |
| 4 | Hata durumu taksonomisi + UI eşlemesi (moderation/timeout/param-error üçlü ayrımı) | **P1** | En sık atlanan alan; düşük efor, yüksek güven kazandırıcı |
| 5 | Model karşılaştırma (arena) görünümü — `model-comparison-harness` için kör yan-yana UI | P2 | Kalite-oylama verisi toplar + kullanıcı değeri, ama önce 1-4 oturmalı |
| 6 | Prompt kutusu + progressive-disclosure parametre paneli | P2 | İlk gerçek "generate" ekranını mümkün kılar |
| 7 | İki kademeli kuyruk şeffaflığı (tahmini bekleme + kuyruk pozisyonu) | P3 | Gerçek çoklu-worker kuyruk olmadan tam güç kazanmıyor (ADR-004) |
| 8 | Progressive-preview zinciri (Krea'nın hissini submit/poll ile taklit) | P3 | Yüksek algısal değer, `ai-workflow-engine` DAG'ıyla yaklaşık taklit edilebilir |

---

## Kaynak

Tam araştırma raporu (7 referans ürünün detaylı analizi, kaynak linkleri dahil): background research agent tarafından üretildi, 2026-08-31. Bu dosya onun özetlenmiş/kalıcı versiyonudur.
