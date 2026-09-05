# Architecture Decision Records (ADR)

Önemli teknik kararların neden alındığını, hangi alternatiflerin değerlendirildiğini ve neden reddedildiğini kaydeder — aynı araştırmayı ileride tekrar yapmamak için. Yeni bir ADR eklerken sırayı koru (en yeni en üstte), numarayı artır.

Format: **ADR-NNN: Başlık** — Tarih, Durum (Kabul edildi / Reddedildi / Değiştirildi), Bağlam, Karar, Alternatifler, Sonuç.

---

## ADR-011: `research/lab/*` asla `main`'e merge edilmez — kalıcı olarak sadece `claude/ai-creative-platform-research-fwh2vt` branch'inde yaşar

**Tarih:** 2026-08-31 · **Durum:** Kabul edildi (kullanıcı kararı)

**Bağlam:** `Furkiozknn/Furkiozknn` reposu, kullanıcının **halka açık GitHub profil reposu**. PR #2, tüm araştırma içeriğini (sentez dokümanları + `research/raw/*.md` + bu lab altyapısı — `STATUS.md`/`DECISIONS.md`/`BACKLOG.md`/`TECH-RADAR.md`/`DESIGN-SYSTEM.md`/`shared/gateway_poll.py`) `main`'e taşımayı öneriyordu. Kullanıcı, PR'ı **merge etmeden kapattı** ve şu ayrımı yaptı: "güvenli" araştırma içeriği (README linki, sentez dokümanları, 5 `research/raw/*.md` dosyası) doğrudan `main`'e ayrı commit'ler halinde uygulandı; ama `research/lab/*` — "iç planlama/ADR/backlog/tech-radar içeriği, halka açık profil reposu için değil" — bilinçli olarak `main`'in dışında bırakıldı.

**Karar:** `research/lab/*` dizini (bu dosya dahil) bir daha asla `main`'e merge edilmeye çalışılmayacak. Bu dizin, ekosistemin R&D lab'inin **sürekli çalışma alanı** olarak `claude/ai-creative-platform-research-fwh2vt` branch'inde kalıcı olarak yaşayacak — bir "bekleyen PR" değil, kendi başına kalıcı bir çalışma branch'i, neredeyse ayrı bir "lab reposu" gibi davranılacak (gerçek ayrı bir repo GitHub App izin kısıtı yüzünden şu an açılamıyor, bkz. ADR-007). Her oturum bu branch'e commit atmaya ve push etmeye devam eder; `main`'e karşı bir PR açmak/açık tutmak artık hedef değil.

**Alternatifler değerlendirildi:**
- Lab içeriğini yine de `main`'e merge etmek — kullanıcı tarafından reddedildi, halka açık profil reposunun temiz/profesyonel kalması isteniyor.
- Lab içeriği için PR'ı açık bırakıp draft'ta tutmak — reddedildi (kullanıcı PR'ı kapattı), gereksiz bir "bekleyen" durum yaratırdı.
- Lab içeriğini tamamen ayrı bir repoya taşımak — ideal olurdu ama GitHub App'in repo oluşturma izni yok (ADR-007); kullanıcı üç yeni repo (`model-comparison-harness`, `asset-provenance-toolkit`, `ai-workflow-engine`) için zaten manuel repo açıyor, lab altyapısı için dördüncüsünü istemek şu an gereksiz sürtünme — branch zaten işlevsel olarak aynı amaca hizmet ediyor.

**Sonuç:** `STATUS.md`'nin en üstüne bu gerçek açıkça yazıldı — gelecekteki her oturum, `main`'e değil bu branch'e bakmalı ve bu branch'e commit/push etmeye devam etmeli. `main` sadece halka açık, "bitmiş" araştırma içeriğini taşır (sentez dokümanları + raw research), asla lab'in çalışan iç durumunu değil.

---

## ADR-010: Ses klonlama capability'si için rıza/watermark politikası, herhangi bir modelden önce şart

**Tarih:** 2026-08-31 · **Durum:** Kabul edildi (politika, henüz uygulama yok)

**Bağlam:** Ses/müzik/konuşma domain araştırması (bkz. `TECH-RADAR.md`), ses klonlamanın diğer tüm domain'lerden (görsel, video, lip-sync) farklı olarak doğrudan gerçek bir kişinin kimliğini taklit ettiğini ve düzenleyici ortamın hızla sıkılaştığını (AB AI Act Madde 50, ABD Tennessee ELVIS Act) ortaya koydu. Chatterbox gibi bazı modeller yerleşik watermark (PerTh) sunarken F5-TTS gibi başkaları sunmuyor.

**Karar:** Herhangi bir ses klonlama `Provider`'ı (Chatterbox, F5-TTS, OpenVoice V2, ya da başka biri) `ai-job-gateway`'e eklenmeden **önce**, `tts-clone` capability'sinin API sözleşmesi şu üç unsuru zorunlu alan olarak içerecek: (1) referans ses yükleyenin o sese yasal hakkı/rızası olduğunu onaylayan bir doğrulama adımı (basit bir checkbox yetmez), (2) üretilen her klon çıktısına watermark veya en azından audit-trail metadata'sı, (3) tanınmış kamu figürü/ünlü isimleriyle eşleşen taleplere ekstra sürtünme veya reddetme. Bu üç unsur netleşmeden hiçbir klonlama `Provider`'ı üretime alınmayacak — teknoloji seçimi (Chatterbox vs F5-TTS vs OpenVoice) bu kararın önünde değil, arkasında gelir.

**Alternatifler değerlendirildi:**
- Rıza kontrolünü sonraya erteleyip önce teknik PoC'yi tamamlamak — reddedildi. Ürün politikası bir mühendislik detayı değil, gerçek hukuki/itibari risk taşıyor; sonradan eklemek "önce çalıştır, sonra güvenli hale getir" tuzağına düşer.
- Sadece watermark'lı modelleri (yalnızca Chatterbox) kullanmak, ayrı bir rıza akışı kurmamak — reddedildi, watermark tek başına yeterli değil (kaldırılabilir/bozulabilir, sadece caydırıcı) ve rıza doğrulaması ayrı bir katman olarak gerekiyor.

**Sonuç:** `TECH-RADAR.md`'de "Ses Klonlama — Rıza/Etik" girdisi P0 olarak işaretlendi — klonlama özelliği için blokaj, teknoloji seçiminden bağımsız. Henüz uygulama yok, bu bir önden-alınan politika kararı.

---

## ADR-009: Bağımlılık-içi bir alt-modelin lisansı asla örtük/varsayılan davranışa bırakılmaz

**Tarih:** 2026-08-31 · **Durum:** Kabul edildi

**Bağlam:** `mini-creative-toolkit::remove_background()`, `rembg.remove(data)`'yı `session` parametresi vermeden çağırıyordu — herkesin (dahil kendi ilk varsayımım) bunun rembg'nin klasik varsayılanı "u2net"e çözümlendiğini düşünmesine rağmen, kurulu `rembg` 2.0.81'de bu çağrı **doğrudan doğrulandı**: `rembg/bg.py`'nin kaynak kodu, `session=None` olduğunda `new_session("bria-rmbg", ...)` çağırıyor — yani sessizce **CC BY-NC 4.0 (ticari olmayan) lisanslı bir modele** geçilmiş durumdaydı, hiçbir kod değişikliği olmadan, sadece bir `rembg` sürüm güncellemesiyle. Bu, `TECH-RADAR.md`'nin zaten belgelediği "iyi görünen ama ticari olmayan lisans" tuzağının (HunyuanVideo, Wav2Lip) üçüncü, ama ilk kez **teorik değil bu ekosistemde zaten gerçekleşmiş** örneği.

**Karar:** Lisans açısından hassas bir üçüncü-taraf kütüphane çağrısında (bir üretim/inference kütüphanesinin altında birden fazla alt-model/backend barındırdığı her durumda — rembg, gelecekte benzer şekilde çoklu-model sağlayan başka kütüphaneler), çağıran kod **hiçbir zaman** kütüphanenin kendi iç varsayılanına güvenmemeli; hangi alt-modelin kullanıldığı her zaman kodda açıkça, isim vererek belirtilmeli (`new_session("u2net")` gibi). Bu, hem lisans güvenliği hem de "sürüm güncellemesi davranışı sessizce değiştirmesin" öngörülebilirliği için geçerli.

**Alternatifler:**
- Sadece `rembg`'yi belirli bir sürüme sabitlemek (`rembg==2.0.65`) — reddedildi, kırılganlığı sadece erteler (güvenlik yaması için sürüm yükseltmesi gerektiğinde aynı risk geri döner), kök nedeni çözmez.
- Hiçbir şey yapmamak, riski kabul etmek — reddedildi, gerçek ve aktif bir lisans ihlali riskiydi (ürün "ticari, API key gerektirmeyen" olarak pazarlanıyor).

**Sonuç:** `mini-creative-toolkit` commit `74d5dad` ile düzeltildi — `remove_background()` artık her zaman açık `new_session(model)` çağırıyor, varsayılan `model="u2net"`. Bu ilke, benzer "kütüphane-içi model seçimi" deseni taşıyan gelecekteki her entegrasyon için (ör. TTS/müzik provider'ları, çoklu-checkpoint destekleyen kütüphaneler) geçerli sayılacak.

---

## ADR-008: ADR-006'nın "3 tekrar" eşiği aşıldı — paylaşılan gateway-client modülü çıkarılacak (ama paket değil, vendored dosya)

**Tarih:** 2026-08-31 · **Durum:** Kabul edildi

**Bağlam:** İki bağımsız Reviewer Agent denetimi (`ai-job-gateway`/`prompt-template-manager`/`model-comparison-harness` odaklı), ADR-006'nın kendi belirlediği "3+ tekrar oluşursa yeniden değerlendir" eşiğinin somut, hipotetik olmayan bir kanıtla aşıldığını gösterdi: submit→poll→terminal-durum-eşleme mantığı üç repoda bağımsız olarak yazıldı (`ai_job_gateway/client.py`, `prompt_template_manager/gateway_client.py`, `model_comparison_harness/backends.py::GatewayBackend`), ve aynı ince hata (`GET .../jobs/{id}`'in süresi geçmiş bir job için döndürdüğü `410 Gone`'u `raise_for_status()`'tan *önce* kontrol etmek gerektiği) doğru implementasyonda (#1, orijinal referans) doğru yazıldı, diğer ikisinde (#2, #3) bağımsız olarak *aynı şekilde* yanlış yazıldı. Bu, tekrarın teorik değil gerçek bir bakım/doğruluk riski olduğunun kanıtı.

**Karar:** Paylaşılan mantığı çıkar, ama ADR-006'nın "repo'lar arası Python-seviyesi bağımlılık yok" ilkesini bozmadan: submit/poll/terminal-durum-eşleme (yalnızca bu ~15-20 satır) için bağımlılıksız, tek dosyalık, her repoya **vendored** (kopyalanan, pip ile kurulmayan) bir referans modül tutulacak — `research/lab/shared/gateway_poll.py` (bu repoda, kanonik kaynak olarak) — ve her tüketici repo bu dosyayı olduğu gibi kopyalar, üstüne kendi ince sarmalayıcısını (senkron/async, hata tipi mapping'i) yazar. Gerçek bir pip paketi (`ai-ecosystem-common`) hâlâ reddedilir — ayrı sürümleme/yayın yükü, bu ölçekte gereksiz. Vendored dosyanın başına, kaynağını ve "elle senkronize et" uyarısını belirten bir yorum eklenir (nova-drift'in `prng.spec.js` içinde zaten kullandığı desenin aynısı — bkz. Reviewer raporu).

**Alternatifler değerlendirildi:**
- Gerçek bir pip paketi olarak çıkarmak — reddedildi, ADR-006'nın "bağımsız sürümlenebilir repo" hedefiyle çelişir, bu ölçekteki 3 repo için aşırı.
- Hiçbir şey yapmama, sadece 3 repoda ayrı ayrı düzeltmeye devam etme — reddedildi, Reviewer raporu bunun tam olarak neden başarısız olduğunu (aynı hata iki kez bağımsız tekrarlandı) somut olarak gösterdi.
- Sadece dokümantasyon (BACKLOG.md'de "bu mantık drift riski taşıyor" notu, kod değişikliği yok) — yetersiz, Reviewer'ın önerdiği minimum çözüm ama gerçek riski azaltmıyor, sadece kaydediyor.

**Sonuç:** Uygulandı. `research/lab/shared/gateway_poll.py` yazıldı ve üç repoya (`ai-job-gateway/src/ai_job_gateway/gateway_poll.py`, `prompt-template-manager/src/prompt_template_manager/gateway_poll.py`, `model-comparison-harness/src/model_comparison_harness/gateway_poll.py`) vendor edildi. Her repo kendi public API'sini (fonksiyon imzaları, exception tipleri: `JobNotFoundError`/`GatewaySubmissionError`/`BackendError` vb.) korudu — sadece iç implementasyon paylaşılan, bağımlılıksız, transport-agnostik fonksiyonlara (`parse_submission`, `classify_poll_body`, `is_expired_poll_response`, URL yardımcıları) devredildi. Üç reponun testleri de yeşil kaldı (46/43/37). `asset-provenance-toolkit`'in `gateway_client.py`'si kapsam dışı bırakıldı — o bir poll döngüsü çalıştırmıyor (tek seferlik `fetch_job_record`), ve zaten genel `>=400` kontrolü 410'u da doğru kapsıyor, orada hata yoktu.

---

## ADR-007: GitHub App'in repo oluşturma izni yok — kullanıcı manuel açıyor

**Tarih:** 2026-08-31 · **Durum:** Kabul edildi (geçici kısıtlama)

**Bağlam:** `mcp__github__create_repository` çağrısı sürekli `403 Resource not accessible by integration` döndürüyor. Bu, oturumun GitHub App entegrasyonunun hesap genelinde yeni repository oluşturma iznine sahip olmadığı anlamına geliyor.

**Karar:** Yeni bir repo gerektiğinde: (1) kodu/testleri/dokümantasyonu yerelde tam olarak hazırla ve commit al, (2) kullanıcıdan GitHub üzerinden boş (README/license/gitignore'suz, ya da mobil uygulama zorluyorsa sadece minimal README ile — bu durumda merge ile birleştirilir) bir repo açmasını iste, (3) `add_repo` ile ekleyip mevcut yerel commit'i push et. Her yeni repo için ayrı ayrı sormak yerine, `STATUS.md`'deki "bekleyen repo listesi"ni biriktirip toplu iste.

**Alternatifler değerlendirildi:**
- GitHub App'i yeniden yetkilendirmek (kullanıcıya önerildi, henüz yapılmadı/etkisi görülmedi).
- Furkiozknn/Furkiozknn içinde monorepo alt-klasörü olarak tutmak — reddedildi, kullanıcı ayrı repo istiyor ve ekosistem vizyonu (bağımsız, birleştirilebilir küçük repolar) buna uymuyor.

**Sonuç:** İş akışı kuruldu, `ai-job-gateway` ve `prompt-template-manager` bu yöntemle başarıyla push edildi.

---

## ADR-006: Repo'lar arası bağlantı sadece HTTP kontratı üzerinden, Python import yok

**Tarih:** 2026-08-31 · **Durum:** Kabul edildi

**Bağlam:** `prompt-template-manager` ve `model-comparison-harness`, `ai-job-gateway`'in submit/poll kontratını kullanıyor. Doğrudan `pip install ai-job-gateway` bağımlılığı eklenebilirdi.

**Karar:** Repo'lar arasında hiçbir Python-seviyesi bağımlılık yok — her repo, diğerinin HTTP API kontratını (dokümante edilmiş submit/poll/webhook şekli) bağımsız olarak implemente ediyor/tüketiyor. `GatewayBackend`/`gateway_client.py` gibi küçük istemci kodları her repoda ayrı ayrı (ama tutarlı şekilde) yazıldı.

**Alternatifler:**
- Paylaşılan bir `ai-ecosystem-common` paketi — şimdilik reddedildi (henüz 3 kod tekrarı var, "3 kural"ı henüz tetiklemiyor — bkz. `BACKLOG.md` teknik borç, izlenecek).
- Doğrudan Python import/monorepo — reddedildi, repo'ların bağımsız sürümlenebilir/dağıtılabilir kalması isteniyor.

**Sonuç:** Gevşek bağlaşım (loose coupling) korunuyor; her repo tek başına anlamlı ve kullanılabilir.

---

## ADR-005: Job sonuçları için kısa ömürlü expiry (BFL deseni)

**Tarih:** 2026-08-31 · **Durum:** Kabul edildi

**Bağlam:** Araştırma (bkz. `research/AI-CREATIVE-PLATFORM-ARASTIRMA-VE-MIMARI.md` §4) BFL'nin sonuç URL'lerini 10 dakikada expire ettiğini, RunPod'un benzer bir desen izlediğini gösterdi.

**Karar:** `ai-job-gateway`'de her `JobRecord`'a `result_expires_at` eklendi; `JobStore.get()`/`list()` okuma anında expiry'yi hesaplıyor (storage'a yazmadan, pure function) ve `GET /v1/jobs/{id}` süresi geçmiş bir job için `410 Gone` döndürüyor. Varsayılan pencere 30 dakika (BFL'nin 10 dakikasından daha cömert, referans implementasyon için).

**Alternatifler:** Sonuçları süresiz saklamak (basit ama depolama maliyeti sınırsız büyür) — reddedildi.

**Sonuç:** Test edildi (`test_terminal_job_past_ttl_reads_as_expired` vb.), doğru çalışıyor.

---

## ADR-004: Job execution = in-process asyncio task (v1), gerçek kuyruk değil

**Tarih:** 2026-08-31 · **Durum:** Kabul edildi (bilinçli v1 sınırı)

**Bağlam:** Araştırma, "önce hosted API / basit worker, sonra ölçek geldiğinde gerçek kuyruk" stratejisini öneriyordu (Faz 1→2).

**Karar:** `JobManager._run()` işi `asyncio.create_task` ile arka planda çalıştırıyor. README'de açıkça "bu bir referans implementasyon sınırı, production'da Redis/RQ/Celery/RunPod-tarzı worker'lara geçilmeli" diye belirtildi — gizli bir varsayım değil, dokümante edilmiş bir kapsam sınırı.

**Alternatifler:** Gerçek bir kuyruk (Redis/RQ) entegre etmek — v1 için erken optimizasyon olur, reddedildi. Public kontrat (`submit()` hemen job id döner) korunduğu için ileride worker değişimi API'yi kırmadan yapılabilir.

**Sonuç:** MVP hızlı teslim edildi, gelecekteki geçiş yolu README'de net.

---

## ADR-003: Şablon değişken ikamesi — Jinja2 string + `${var}` tip-koruyan sigil

**Tarih:** 2026-08-31 · **Durum:** Kabul edildi

**Bağlam:** `prompt-template-manager` tasarlanırken: prompt gibi metin alanlarında string interpolasyonu (Jinja2 doğal), ama `width`/`seed` gibi sayısal alanlarda değişkenin int/bool tipini stringify etmeden koruma ihtiyacı vardı.

**Karar:** İki ayrı ikame formu: `{{ var }}` (Jinja2, `StrictUndefined` ile — yazım hatası sessizce boş render etmek yerine hemen hata verir) ve tam olarak `"${var}"` olan değerler için doğrudan tipli ikame.

**Alternatifler:** Tek bir Jinja2 mekanizması + sonradan tip zorlama (daha kırılgan, "1024" string'i her yerde int'e çevirmeye çalışmak gerekir) — reddedildi. Özel bir DSL yazmak — aşırı mühendislik, reddedildi.

**Sonuç:** 42 testle doğrulandı, iki form da net ve öngörülebilir.

---

## ADR-002: Python + `uv` tüm yeni prototip repolarında standart stack

**Tarih:** 2026-08-31 · **Durum:** Kabul edildi

**Bağlam:** Ekosistemdeki mevcut Python repoları (`mini-creative-toolkit`, `nvidia-nim-mcp`) zaten `uv` kullanıyor.

**Karar:** Yeni backend/orkestrasyon/CLI repoları (`ai-job-gateway`, `prompt-template-manager`, `model-comparison-harness`) tutarlılık için Python 3.11+ + `uv` + `hatchling` build backend kullanıyor. Frontend/tarayıcı projeleri (`kalp-animasyon`, `nova-drift`) vanilla JS + Three.js'de kalıyor (build adımı yok — bilinçli tercih, "no build step" onların kendi kimliği).

**Alternatifler:** TypeScript/Node backend'ler — reddedildi (mevcut ekosistemle tutarsız, gereksiz ikinci bir dil/toolchain).

**Sonuç:** Tüm yeni repolar `uv sync && uv run pytest` ile aynı şekilde test ediliyor, CI şablonu tekrar kullanılabilir.

---

## ADR-001: Job/generation API kontratı — submit → poll/webhook, BFL/RunPod deseni

**Tarih:** 2026-08-31 · **Durum:** Kabul edildi

**Bağlam:** Derin araştırma (`research/raw/B_flux_fal_alternatives.md`), BFL'nin kendi hosted API'sinin ve RunPod'un `worker-comfyui`'sinin bağımsız olarak aynı sözleşmeye yakınsadığını gösterdi: `POST` hemen `{id, polling_url}` döner, `GET` durum sorgular, opsiyonel webhook.

**Karar:** `ai-job-gateway` bu kontratı doğrudan referans implementasyon olarak inşa etti; ekosistemdeki her şey (template manager, comparison harness) bu kontrata göre tasarlandı.

**Alternatifler:** Senkron/blocking API (basit ama GPU-bound işler için uygun değil) — reddedildi. GraphQL subscriptions (gereksiz karmaşıklık, ekosistemin geri kalanıyla uyumsuz) — reddedildi.

**Sonuç:** Üç repo arasında gerçek, çalışan bir entegrasyon kanıtlandı (bkz. `STATUS.md`).
