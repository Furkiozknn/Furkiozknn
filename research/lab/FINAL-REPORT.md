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

---

# ADVERSARIAL SENIOR REVIEW (bağımsız ikinci geçiş)

Tarih: 2026-09-05 · Rol: Principal Engineer / Security Reviewer — yukarıdaki raporun iddialarını **koda karşı** doğrulamak, düzeltmek ya da çürütmek. Hiçbir iddia rapordan doğru kabul edilmedi; her önemli iddia diff/test/çalıştırma ile sınandı.

## Executive Summary

Önceki turun işi büyük ölçüde gerçek: 20 PR'ın merge'i, test sayıları, güvenlik düzeltmeleri ve ölçümler koddan doğrulandı. **Ama iki iddia saldırı altında çöktü ve düzeltildi:** (1) "Alembic downgrade temiz" — YANLIŞTI: downgrade 6 Postgres enum tipini sızdırıyordu ve up→down→up döngüsünde ikinci upgrade `DuplicateObject` ile ölüyordu (canlı reprodüksiyon); (2) gateway'in "restart artık double-run üretmez" iddiası — KISMEN doğruydu: submit'te kayıt anahtar'dan ÖNCE yazıldığı için aradaki crash penceresi hâlâ double-run üretiyordu, ve crash sırasında kaybolan webhook'lar sessizce hiç ateşlenmiyordu. Ayrıca bir P1 güvenlik konfigürasyon tuzağı bulundu: varsayılan JWT secret + bootstrap admin = forge edilebilir admin (tek savunma bir log satırıydı). Üçü de kanıtlı, testli, merge yolunda.

## Previous Claims vs Verified Reality

| İddia | Durum | Kanıt |
|---|---|---|
| 20 PR merge, CI yeşil | **VERIFIED** | 13 repo'nun default-branch son run'ları squash SHA'larıyla eşleşiyor, hepsi success |
| buradane konsensüs falsifikasyon P0'ı kapandı | **VERIFIED** | Kod okundu + mutasyon testi: `>` → `>=` zayıflatması mevcut testçe öldürülüyor |
| JWT: algoritma confusion yok | **VERIFIED** | `jwt.decode(..., algorithms=[HS256])` pinli; jose 3.5.0 (CVE-2024-33663/64 kapalı) |
| Rate limiter spoof edilemez | **VERIFIED** | `request.client.host`, XFF'e asla bakmıyor; proxy davranışı docstring'de |
| "Alembic downgrade temiz" | **INCORRECT → FIXED** | up→down→up hiç koşulmamıştı; 6 enum tipi sızıyordu, 2. upgrade çöküyordu. Downgrade artık tipleri düşürüyor + scratch-DB regresyon testi (buradane #6) |
| "Idempotency restart'a dayanıklı" | **PARTIALLY → FIXED** | Restart: evet. Create-ile-remember arası crash: double-run penceresi vardı. Sıra ters çevrildi (anahtar önce; ters pencere zaten self-healing), call-order + simüle-crash testleri (gateway #8) |
| "Webhook dead-letter sorgulanabilir" | **PARTIALLY → FIXED** | Canlı süreçte evet; crash mid-delivery'de webhook_status sonsuza dek null kalıyor, alıcı hiç duymuyordu. Startup sweep artık outcome'suz terminal işlerin webhook'unu yeniden ateşliyor (at-least-once, README'de) |
| autoflush=False düzeltmesi tam mı | **VERIFIED** | resolve/create yollarında explicit flush'lar; drag-release testleri flush'sız kırmızı |
| awe: DAG + Jinja güvenli | **VERIFIED** | Kahn katmanlama + açık cycle raise; `SandboxedEnvironment` + `StrictUndefined` (ptm de sandbox'lı) |
| mcp-vet "audit ettiğini çalıştırmaz" | **VERIFIED** | Pakette çalıştırma primitifi yok; subprocess geçişleri yalnızca taranan pattern string'leri |
| nim bounded download / describe guard | **VERIFIED** | Kod + 7 test master'da; magic-sniff kısa gövdede güvenli (slice) |
| Ölçümler (30MB→1.4MB, 740ms→45ms, cache 0.23s) | **VERIFIED (in-session)** | Oturum içinde ölçülerek üretilmişti; asset boyutları ve EXPLAIN çıktıları kayıtlı |

## Critical Findings (bu geçişte bulunanlar)

| Sev | Repo | Bulgu | Etki | Fix |
|---|---|---|---|---|
| P1 | buradane | Migration döngüsü geri döndürülemez (enum sızıntısı) | Rollback sonrası redeploy imkânsız; "verified migration" iddiası yanlış | Downgrade'de 6 enum drop (checkfirst) + up→down→up scratch-DB regresyon testi — **#6 merged** |
| P1 | buradane | Default JWT secret + bootstrap admin = forge edilebilir admin; savunma tek log satırı | Konsensüsün koruduğu moderasyon gücü konfigürasyonla yeniden açılıyor | Bootstrap default secret'ta **açıkça reddediyor** (fail-loud startup); admin'siz keşif kurulumları etkilenmez — **#6 merged** |
| P1 | ai-job-gateway | Submit: kayıt→anahtar sırası; aradaki crash = double-run | Özelliğin önlediği tam hata, dar pencerede hâlâ mevcut | Sıra ters; iki yeni test (order-spy, crash+retry=tek run) — **#8 merged** |
| P1 | ai-job-gateway | Crash mid-delivery webhook'ları sessizce kaybediyor | Alıcı asla duymuyor, dead-letter alanı boş kalıyor | Sweep outcome'suz terminal işleri yeniden ateşliyor; at-least-once + "job id ile dedupe edin" README'de — **#8 merged** |
| P2 | ai-job-gateway | Recovery sweep'in tek-süreç varsayımı yalnızca implicit'ti | İkinci süreç ilkinin canlı işlerini error'a süpürür | Docstring + README'de açıkça adlandırıldı — **#8 merged** |

## Security / Reliability / Performance / Test Quality / Docs / Architecture — özet bulgular

- **Security:** MCP beşlisinde yeni açık yok (nim'in iki yüzeyi önceki turda kapanmış, doğrulandı; lns'in tek MATCH'i parametrize vec0 KNN; mct path/shell disiplini yerinde). buradane moderasyon eşzamanlılığı: iki admin aynı raporu yarıştırırsa ikisi de 200 alır (idempotent etkiler, veri bozulmaz) — tek-moderatör v1 için kabul, P3 not. nim `describe_image` stat→read TOCTOU — teorik, P3.
- **Reliability:** "İki worker + network failure altında güvenilir mi?" — **HAYIR**, ve artık bu açıkça yazıyor: SQLite tek-yazarlı, sweep tek-süreç varsayar, in-process rate-limit/queue paylaşılmaz. Tek süreçte ise crash pencereleri bu geçişle kapandı; kalan bilinen pencere: webhook 2xx sonrası-outcome öncesi crash → 1 duplicate (standart at-least-once, belgeli).
- **Performance:** Yeni bulgu yok; bilinenler duruyor (gateway /v1/jobs O(n) — belgeli; buradane detail endpoint küçük N+1 ≤4 — P3).
- **Test quality:** Mutasyon sınaması geçti (konsensüs tie-break). Backoff testi beklentiyi bağımsız yeniden hesaplıyor (formül drift'ini yakalar). Yeni testler crash/restart senaryolarını gerçek davranış üzerinden sınıyor (order-spy + simüle crash + re-fire), mock'lar transport seviyesinde. Zayıf nokta: buradane'de eşzamanlılık testi yok (tek-süreç TestClient sınırı) — bilinen boşluk.
- **Docs:** README'ler bu geçişten sonra kodun önünde iddia taşımıyor. Kalan tek yumuşatılacak iddia: nova-drift "installable PWA" (service worker yok) — önceki raporda da listeli, P3. mct'nin `mcp[cli]>=2.0.0` pini hâlâ sınırsız (diğer üçü `>=2.1,<3`) — P3 tutarlılık.
- **Architecture:** awe "çalışan runner ↔ production-grade orchestrator" farkı: run persistence/resume/cancel/retry YOK ve README bunu iddia da etmiyor ("durable" olan YAML grafiği). Doğru konumlanmış; orchestrator'a terfi ancak gerçek bir kullanıcı ihtiyacıyla yapılmalı.

## Portfolio (ikinci görüş)

Featured-six seçimi kanıtla uyumlu; değişiklik gerekmedi. **ptm ↔ awe:** ptm bağımsız bir şablon KÜTÜPHANESİ (CLI + kütüphane, kendi hata yüzeyi), awe bir ÇALIŞTIRICI; awe'nin templating.py'si ptm'yi çağırmıyor (ayrı sandbox ortamları). Örtüşme "ikisi de Jinja kullanıyor" seviyesinde — kod tekrarı değil. **Öneri: fold ETME**; bunun yerine awe'nin bir sonraki gerçek özelliği ptm şablonlarını `params` içinde referans alabilmek olursa dependency olarak bağla. Repo sayısı azaltmak için birleştirme, iki dürüst README'yi bir bulanık README yapar. lumen arşivi ve üç push-bekleyen repo önerileri değişmedi.

## Production Readiness Matrix

| Repo | Technical | Security | Reliability | Tests | Production | Portfolio |
|---|---|---|---|---|---|---|
| mcp-vet | A | A | A | A (237) | A (araç) | 1 |
| mini-creative-toolkit | A | A | A− | A (319) | A− (yerel araç) | 2 |
| ai-job-gateway | A− | A− | B+ (tek-süreç; pencereler kapandı) | A (142) | B+ referans | 3 |
| buradane | A− | A− (bootstrap guard sonrası) | B+ | A− (78) | B (deploy bekliyor) | 4 |
| ai-workflow-engine | B+ | A (sandbox) | B (runner, resume yok — bilinçli) | B+ (59) | B | 5 |
| nova-drift / kalp | A− | n/a | A− | B+ (12/22) | A (statik) | 6 |
| lns / voice-io / nim | B+ | B+ (bu turda kapandı) | B+ | B+ | B+ (yerel araç) | şerit |
| ptm / mch / apt | B+ | B+ | B+ | B+ | B | şerit |

**Final Ranking: değişmedi** — bulgular sıralamayı bozmadı, iki lider reponun iddialarını gerçeğe eşitledi.

## Changes Made / Tests Run

- buradane #6 (78 test yeşil, PostGIS'e karşı): enum-drop'lu downgrade + döngü regresyon testi; bootstrap default-secret reddi + testi; README eşitlendi.
- ai-job-gateway #8 (142 test yeşil): submit sırası + iki crash testi; webhook re-fire + testi; tek-süreç varsayımı belgelendi.
- Değiştirilmeyenler bilinçli: moderasyon SELECT FOR UPDATE (tek moderatör, P3), nim TOCTOU (teorik), mct mcp pini (P3), awe orchestrator özellikleri (ihtiyaç yok).

## Remaining Risks (dürüst liste)

1. buradane demo `/api/admin/*` auth'suz — deploy öncesi shared-secret ŞART (değişmedi, bilinçli: deploy görevinin parçası).
2. Webhook at-least-once → alıcı dedupe sorumluluğu (belgeli).
3. Tek-süreç varsayımları (rate limit, sweep, SQLite) — belgeli; Postgres'e geçiş `JobStore`/proxy seviyesinde planlı.
4. nova PWA iddiası; mct mcp pini; buradane detail N+1 — P3'ler.

## Top 10 Next Actions (revize)

| # | Aksiyon | Etki | Efor | Neden | Bağımlılık | Öncelik |
|---|---|---|---|---|---|---|
| 1 | PAT: metadata + 3 repo push (SEN) | YÜKSEK | S | Profil hikâyesi + DEVELOPER INFRA şeridi | — | P1 |
| 2 | Pinned repos = featured six (SEN) | YÜKSEK | S | İlk ekran = tez | — | P1 |
| 3 | buradane deploy (önce demo admin'e shared-secret) | YÜKSEK | M | Ulaşılamayan ürün = sıfır değer | #1 değil | P1 |
| 4 | Demo → gerçek backend bağlantısı | YÜKSEK | M | Katkı döngüsü gerçek DB'ye | 3 | P1 |
| 5 | lumen arşivi (SEN) | ORTA | S | Bilinçli arşiv ≠ terk | — | P2 |
| 6 | gateway store.list(limit) SQL'e | ORTA | S | 470ms@20k ölçülü | — | P2 |
| 7 | buradane moderasyon SLA sinyali | ORTA | S | Sessiz kuyruk döngüyü öldürür | — | P2 |
| 8 | ptm→awe: fold DEĞİL, ihtiyaç doğarsa dependency | ORTA | S | Bu geçişin analizi: örtüşme yüzeysel | — | P2 |
| 9 | nova service worker VEYA iddia yumuşatma; mct mcp pini | DÜŞÜK | S | Son doğrulanmamış iddialar | — | P3 |
| 10 | MCP dörtlüsüne stdio smoke testi | DÜŞÜK | S | Tek eksik test sınıfı | — | P3 |

## Self-Critique

Bu geçişin kendisi de aynı oturumun modeli tarafından yapıldı — kör nokta riski gerçek. Buna karşı alınan önlemler: her doğrulama fiilî çalıştırma/diff üzerinden (üç iddia bu sayede düştü), bir mutasyon testi koşuldu, ve "sorun bulamadım" denilen alanlar (awe, mcp-vet, lns) için ne arandığı yazıldı. Bulunamayan ama aranan şeyler: SQL injection (parametrize), SSRF regresyonu (validator fail-closed), Jinja sandbox kaçışı (SandboxedEnvironment iki repoda), XFF spoof (bakılmıyor). En büyük kalan belirsizlik: eşzamanlılık davranışları tek-süreç testlerle sınırlı — çok-süreç senaryoları test edilmiyor, yalnızca belgelenmiş durumda.

## ADDENDUM — Review'ün en önemli bulgusu: "CI yeşil" ≠ "CI değişikliği gördü" (P0, süreç)

Adversarial geçişin kendi doğrulama adımı (merge sonrası CI logundan **toplanan test sayısını** okumak) şunu yakaladı: **buradane #5 ("Alembic baseline") gerçekte yalnızca README'yi merge etmişti.** Kök neden: `git add -A ../README.md` — pathspec'li `-A` yalnızca o dosyaya uygulanır. Migration dosyası, env.py filtreleri, iki model düzeltmesi (çift GiST index dahil!) ve parite testi working tree'de commit'siz kaldı. Lokal süit geçmeye devam etti (dosyalar diskteydi); **CI da geçmeye devam etti — çünkü 75 eski testi koşuyordu ve kimse toplanan sayıyı beklenen sayıyla karşılaştırmadı.** Main'in README'si var olmayan migration'ları belgeledi. #6'nın ilk commit'i de aynı hatayı taşıyordu.

- **Etki alanı (tarandı):** yalnızca buradane #5 + #6 ilk commit. Diğer 19 PR'ın tamamı pathspec'siz `git add -A` ile hazırlanmıştı; tüm klonlar temiz doğrulandı; #4'ün CI sayısı (75 = 62+13) içeriğin gerçekten indiğini bağımsız doğruluyor.
- **Düzeltme:** tüm gerçek içerik #6'ya ikinci commit olarak indi (7 dosya, 378 satır); merge kabulü artık "yeşil check" değil, "CI logunda `collected 78 items`".
- **Süreç dersi (kalıcı):** (1) `git add -A`'ya asla pathspec verme; (2) her merge'te PR diffstat'ını niyetle karşılaştır; (3) test-sayısı-artışı iddiası, CI logundaki collected sayısıyla kanıtlanmadan rapora yazılmaz. Yukarıdaki tabloda #5 için "VERIFIED" görünen satırların doğrulaması bu geçişte fiilen KOŞULARAK yapılmıştı — kodun kendisi doğruydu; merge edilmiş OLDUĞU iddiası yanlıştı. İkisini ayırt edememek, bu raporun uyarmayı amaçladığı false-confidence'ın ta kendisiydi.
