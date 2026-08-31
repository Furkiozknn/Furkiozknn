# Backlog — Fikir / Araştırma / Teknik Borç

Üç ayrı liste tek dosyada: yeni fikirler kaybolmasın, teknik borç ertelenip unutulmasın. Her öğe kısa değerlendirmeyle birlikte kaydedilir (öncelik: **P0** kritik/hemen, **P1** yüksek değer, **P2** orta, **P3** "bir gün, işe yararsa").

Bu dosya sürekli güncellenir — tamamlanan bir iş çıkar, her tamamlanan iş yeni satır(lar) ekler.

---

## Sıradaki İş (aktif seçim)

**`asset-provenance-toolkit`** (P1) — Üretilen görsel/video dosyalarına pipeline metadata gömme/çıkarma (A1111'in PNG-metadata-roundtrip deseninin sağlayıcıdan bağımsız genellenmiş hali). `ai-job-gateway`'in job kayıtlarını tamamlayıcı: bir job sonucu indirildiğinde, hangi capability/provider/params ile üretildiği dosyanın kendisinde saklanır — veritabanı olmadan tam yeniden-üretilebilirlik.

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
| Repo'lar arası kod tekrarı (submit/poll istemci mantığı) | `ai-job-gateway`, `prompt-template-manager`, `model-comparison-harness` | P3 (izleniyor) | ADR-006 gereği bilinçli olarak paylaşılmıyor. Üçüncü bir tekrar (dördüncü repo) eklenirse "3 kural"ı tetiklenir, ortak bir `ai-gateway-client` mini-paketi değerlendirilmeli. |
| `ai-job-gateway`'de gerçek kuyruk yok | `ai-job-gateway` | P2 | ADR-004'te dokümante edildi, bilinçli v1 sınırı — gerçek trafik/çoklu-worker ihtiyacı doğduğunda ele alınacak. |
| Hiçbir repoda gerçek provider yok (hepsi mock/echo) | `ai-job-gateway` ve türevleri | P1 | En büyük "demo'dan öteye geçme" engeli — gerçek API key'ler olmadan ilerlenemez, kullanıcı girdisi gerekiyor. |
| Frontend/UI katmanı hiç yok | ekosistem geneli | P2 | Backend/orkestrasyon tarafı olgunlaştı, kullanıcı yüzü hâlâ eksik. |

## Reddedilen / "Kullanılmamalı" Kararlar (değerli negatif sonuçlar)

Bunlar da araştırma çıktısıdır — tekrar zaman kaybetmemek için:

- **HunyuanVideo'yu ana video modeli olarak seçmek** — 100M MAU tavanı + AB/UK/Güney Kore hariç tutma lisans kısıtı nedeniyle reddedildi (bkz. araştırma raporu C).
- **Wav2Lip orijinal ağırlıklarını doğrudan kullanmak** — ticari olmayan lisans, ekosistemde çok yaygın bir tuzak (bkz. araştırma raporu D).
- **GitHub topic sayfalarını doğrudan güvenilir kaynak olarak kullanmak** — SEO/spam repo'larla dolu, sadece bir "keşif sinyali", asıl değerlendirme bağımsız araştırmadan geldi.
- **Paylaşılan bir `ai-ecosystem-common` paketi (şimdilik)** — ADR-006, henüz erken, sadece 3 küçük kod tekrarı var.
