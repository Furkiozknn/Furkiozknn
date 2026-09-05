# FURKIOZKNN — Otonom Ajan Takımı Misyonu · FİNAL RAPORU

Tarih: 2026-09-05 · Kapsam: hesaptaki tüm repolar (17 yerel, 14 GitHub'da)

Misyon hedefi: **daha az repo + daha derin mühendislik + daha iyi ürünler + gerçek kullanıcı değeri + üretim kalitesi + güçlü portfolyo.** Yöntem: 8 paralel denetim ajanı (mimari/perf/QA, ürün, cross-repo güvenlik, dış araştırma, MCP ekosistemi, AI-infra ekosistemi, frontend+portfolyo) → doğrulanmış bulgular → en yüksek ROI'li düzeltmeler → ölçüm → merge. Hiçbir bulgu kod okunmadan rapor edilmedi; hiçbir düzeltme test olmadan merge edilmedi.

---

## 1. Ne düzeldi (merge edilen 20 PR)

### Güvenlik (denetimde canlı gösterilen açıklar dahil)

| Repo | Düzeltme | Kanıt |
|---|---|---|
| buradane | **Veri tahrifatı P0'ı kapandı**: 21 anonim curl isteğiyle `wheelchair_accessible` çevrilip güvenilirlik skoru 0.5→0.85 pompalanabiliyordu (canlı gösterildi). Şimdi: konsensüs kapısı (≥2 bağımsız kimlik, destek > itiraz), kimliksiz doğrulama alan çeviremez, IP başına token-bucket limit, distinct-kimlik sayımı. | #3 |
| buradane | **Moderasyon çıkışı P0'ı kapandı**: auth yığını tamamen ölü koddu (login yok, passlib hiç import edilmemiş, AdminUser erişilemez) ve her rapor skoru kalıcı aşağı çekiyordu. Şimdi: bootstrap admin, `/auth/login` (aynı 401, düz zamanlama, brute-force limiti), `GET /reports` + `PATCH /reports/{id}` accept/reject, karar drag'i serbest bırakıyor. | #4 |
| ai-job-gateway | **SSRF savunması**: webhook URL'i submit anında çözülür, global olmayan adresler 422, çözülemeyen host fail-closed; `--allow-private-webhooks` bilinçli opt-in. `AJG_API_KEY` ile opsiyonel Bearer auth (sabit-zaman karşılaştırma); istemci anahtarı her istekte taşır. | #5, #6 |
| nvidia-nim-mcp | **describe_image exfiltration primitifi kapandı**: herhangi bir yerel dosyayı üçüncü tarafa yükleyebiliyordu ("describe /etc/shadow"). Uzantı allowlist + 10 MB tavan, tek bayt okunmadan reddediliyor. Pollinations indirmesi 20 MB tavan + Content-Type + magic-byte doğrulaması (HTML hata sayfası .jpg olarak diske yazılamaz). | #4 |
| mcp-vet | Heuristiklerin güvenlik garantisi gibi sunulduğu tek yer ("safely install") düzeltildi — kendi kuralı zaten "not suspicious ≠ safe" idi. | #4 |
| voice-io / lns | Tasarlanmış hata mesajları mcp ≥2.1 altında jenerik "Error executing tool"a maskeleniyordu (SDK'ya karşı çalıştırılarak doğrulandı) → `ToolError` ile aynen ulaşıyor. | voice-io #1, lns #2 |

### Performans (hepsi ölçülmüş, tahmin yok)

- **nova-drift**: ilk yükleme **30.1 MB → ~1.5 MB** (altı PNG 28.8 MB'dı; 16 px'te render edilen 2048px ikonlar). Ayrıca "boş gökyüzü" bug'ı: yıldızlar hiç geri dönüşmüyordu, 20-30 sn'de gök kalıcı boşalıyordu → ring'lerle aynı recycle deseni. (#3)
- **buradane**: viewport (bbox) sorgusu **740 ms → 45 ms** @300k satır — geography→geometry cast'li expression GiST index; EXPLAIN ile planner'ın kullandığı doğrulandı. (#2) Alembic baseline yazılırken bulunan **çift GiST index** (GeoAlchemy2 implicit + explicit; her yazmada iki index güncelleniyordu) kaldırıldı. (#5)
- **mcp-vet 0.5.0**: ETag'li disk önbelleği + eşzamanlı registry araması — soğuk denetim **11.8 s → 3.4 s**, sıcak **0.23 s / 0 istek**. (#3)
- **litellm zaman aşımları** (3 repo): takılı sağlayıcı bir tool'u litellm varsayılanı **600 sn** tutabiliyordu → 120 sn tavan her zincir çağrısında. (nim #4, voice-io #1, lns #2)

### Dayanıklılık / üretim hazırlığı

- **ai-job-gateway #7**: idempotency anahtarları restart'ta kayboluyordu (double-run canlı gösterildi) → store'da kalıcı; restart'ta `processing`'de mahsur kalan işler dürüstçe `error`a süpürülüyor (sağlayıcı otomatik yeniden ÇALIŞTIRILMIYOR — yan etki kararı çağırana ait); webhook: 5 deneme, tam jitter'lı üstel backoff, `webhook_status: delivered/failed` sorgulanabilir dead-letter; SQLite yazmaları `BEGIN IMMEDIATE`.
- **buradane #5**: sıfır migration → gerçek PostGIS'e karşı üretilip **uçtan uca doğrulanmış** baseline (upgrade → boş autogenerate → temiz downgrade) + CI'da model/migration parite testi.
- **local-notes-search #1**: Türkçe korpusa İngilizce-only embedding modeli → `paraphrase-multilingual-MiniLM-L12-v2` (aynı 384 boyut; araştırmanın önerdiği e5-small bu fastembed'de yok — dürüstçe düzeltildi); vektör tablosu boyutu artık registry'den, yanlış override tabloyu sessizce bozamaz.
- **prompt-template-manager #2**: bozuk Jinja sözdizimi ham traceback yerine satır numaralı `TemplateError`.
- Latent bug (buradane): `autoflush=False` yüzünden reliability yeniden hesabı az önce eklenen/çözülen raporu görmüyordu — drag bir hesap geç iniyor, çözümde hiç kalkmıyordu. Explicit flush'larla düzeltildi; yeni testler onsuz kırmızı.

### Test büyümesi (bu misyon penceresi)

buradane 48→**76** · ai-job-gateway 110→**139** · nvidia-nim 60→**67** · voice-io 31→**33** · mcp-vet 192→**237** · ptm 56→**58** · lns 37→**38** · mct **319** · nova **12** · kalp **22** — hepsi CI'da yeşil.

---

## 2. Ne atlandı ve neden (dürüst liste)

- **ptm→awe katlama (5→4 repo)**: yalnızca öneri olarak bırakıldı — cilalı bir repoyu arşivleyip kod tabanlarını birleştirmek yapısal bir karar; iki seçenek: (a) awe, ptm'yi bağımlılık olarak kullanır (repolar kalır), (b) tam birleştirme + ptm arşivi. Karar senin.
- **gateway `/v1/jobs` O(n)** (~470 ms @20k satır): endpoint bunun referans-dükkan davranışı olduğunu açıkça belgeliyor; ürün acısı eşiğinin altında. Sıradaki adım listesinde.
- **buradane demo'nun `/api/admin/*` uçları hâlâ auth'suz**: bilinçli, belgelenmiş demo sınırı; gerçek backend artık JWT'li eşdeğerine sahip. Public deploy öncesi demo tarafına shared-secret şart (aşağıda).
- **DNS rebinding kalıntısı** (gateway webhook): çözümleme submit anında; belgelendi — client içi resolution pinning bir referans implementasyonun elle yazacağı şey değil.
- **PWA "installable" iddiası** (nova): service worker yok; iddia yumuşatılmalı ya da 20 satırlık SW eklenmeli. Kalan tek bilinen abartı.
- **Kullanıcı gerektirenler (denendi, 403 — tekrar denemedim)**: 3 yerel repo'nun (ai-repo-scaffold, ai-cost-estimator, webhook-sink) GitHub'a itilmesi; 12 repo'nun açıklama/konu etiketleri (`research/lab/apply-github-metadata.py --apply` bir PAT ile); lumen'in arşivlenmesi (Settings → Archive); pinned repos'un öne çıkan altıya ayarlanması.

---

## 3. Portfolyo yeniden sıralaması (FİNAL RANKING)

Kanıt = test sayısı, CI, uçtan uca kanıt, dürüst dokümantasyon, güvenlik duruşu.

| # | Repo | Neden burada |
|---|---|---|
| 1 | **mcp-vet** | 237 test, sıfır bağımlılık, SECURITY.md, ölçülmüş cache işi, dürüst iddia dili — hesabın imza reposu. |
| 2 | **mini-creative-toolkit** | 319 test, 23 tool, tek belgeli ağ teması, rembg CC-BY-NC yakalayışı (ADR-009) — az portfolyoda olan hikâye. |
| 3 | **ai-job-gateway** | 139 test; SSRF+auth+idempotency+recovery+dead-letter ile referans-kalite async iş sunucusu. |
| 4 | **buradane** | İki P0'ı kapanmış, migration'lı, konsensüs-kapılı gerçek ürün omurgası; 76 test + 11.406 gerçek mekanlı demo. |
| 5 | **ai-workflow-engine** | 59 test; çalıştırmadan önce doğrulanan YAML DAG'ler, canlı gateway'e karşı e2e kanıt. |
| 6 | **nova-drift** | 1.4 MB, hermetik CI, canlı oynanabilir — artık portfolyo linki olmaya layık. |
| 7 | **kalp-animasyon** | Bitmiş, zarif; slot 6'nın kardeş parçası. |
| 8 | **local-notes-search-mcp** | Dil düzeltmesinden sonra amacına uygun; sağlam guard'lar. |
| 9 | **voice-io-mcp** | Temiz fallback mimarisi, artık zaman aşımlı ve doğru hata kanallı. |
| 10 | **nvidia-nim-mcp** | En güçlü fallback zinciri tasarımı; exfiltration/DoS yüzeyleri kapandı. |
| 11 | ptm / model-comparison-harness / asset-provenance-toolkit | İyi test edilmiş yardımcı oyuncular (58/62/86 test). |
| 12 | **lumen** | LICENSE + durum notu eklendi → arşivle. |

Profil README'si bu sıralamaya göre yeniden yazıldı: İngilizce, metin-öncelikli, 6 öne çıkan kart (AI SYSTEMS ×2, AGENT TOOLING ×2, REAL PRODUCTS ×2), destek şeritleri, "How I work" bloğu. Model adı ve oturum linki yok.

---

## 4. TOP 10 SIRADAKİ AKSİYON

| # | Aksiyon | Etki | Efor | Neden |
|---|---|---|---|---|
| 1 | PAT ile `apply-github-metadata.py --apply` + 3 yerel repoyu it (SEN) | YÜKSEK | DÜŞÜK | Repo listesi daha README açılmadan hikâyeyi anlatır; DEVELOPER INFRASTRUCTURE şeridi ancak o zaman eklenebilir. |
| 2 | Pinned repos = öne çıkan altı (SEN) | YÜKSEK | DÜŞÜK | Profilin ilk ekranı = tez. |
| 3 | buradane demo'yu Vercel/Fly'a deploy et; öncesinde `/api/admin/*`'a shared-secret | YÜKSEK | ORTA | Kimsenin ulaşamadığı ürünün kullanıcı değeri sıfır; ön-koşul üçlüsünün ikisi (rate limit, backend auth) tamam. |
| 4 | buradane demo'yu gerçek backend'e bağla (adapter kontratı hazır) | YÜKSEK | ORTA | "Base-URL swap" iddiasını gerçeğe çevirir; katkı döngüsü gerçek veritabanına akar. |
| 5 | lumen'i arşivle (SEN, tek tık) | ORTA | DÜŞÜK | Bilinçli fikir arşivi ≠ terk edilmiş proje. |
| 6 | ptm→awe katlama kararı | ORTA | ORTA | 5→4 repo, "daha az + daha derin" hedefinin son adımı; öneri §2'de. |
| 7 | gateway: `store.list(limit, offset)` — filtre/limit SQL'e insin | ORTA | DÜŞÜK | 470 ms @20k ölçüldü; arayüz zaten buna hazır. |
| 8 | buradane: moderasyon SLA sinyali ("N gündür bekleyen rapor" + basit uyarı) | ORTA | DÜŞÜK | Sessizce şişen kuyruk katkı döngüsünü öldürür; artık çözüm uçları var. |
| 9 | nova-drift: 20 satır service worker ya da PWA iddiasını yumuşat | DÜŞÜK | DÜŞÜK | Son bilinen doğrulanmamış README iddiası. |
| 10 | MCP dörtlüsüne mct-tarzı stdio smoke testi | DÜŞÜK | DÜŞÜK | "Sunucu gerçekten stdio'da açılıyor" tek test sınıfı eksiği. |

---

## 5. Misyon karnesi

- **20 PR** açıldı-yeşillendi-merge edildi (hiçbiri kırmızı CI ile itilmedi; 1 kendi hatam — #5'in istemciyi kilitleyen API-key regresyonu — aynı gün #6 ile kapandı ve raporda saklanmadı).
- Denetimlerin 3 P0'ı (buradane ×2, gateway restart double-run) kod + regresyon testiyle kapandı.
- Canlı gösterilen saldırılar artık testlerde yaşıyor: falsifikasyon döngüsü, restart double-run, HTML-as-JPG, describe_image exfiltration.
- "Ölçmeden optimizasyon yok" tutuldu: her perf iddiasının yanında sayı var.
- Yeni repo açılmadı (kural); repo silinmedi; force-push/history-rewrite yapılmadı; hiçbir test geçsin diye değiştirilmedi (ToolError sözleşme güncellemeleri mesaj metnini aynen korudu).
