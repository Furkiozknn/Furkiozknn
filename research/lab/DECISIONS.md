# Architecture Decision Records (ADR)

Önemli teknik kararların neden alındığını, hangi alternatiflerin değerlendirildiğini ve neden reddedildiğini kaydeder — aynı araştırmayı ileride tekrar yapmamak için. Yeni bir ADR eklerken sırayı koru (en yeni en üstte), numarayı artır.

Format: **ADR-NNN: Başlık** — Tarih, Durum (Kabul edildi / Reddedildi / Değiştirildi), Bağlam, Karar, Alternatifler, Sonuç.

---

## ADR-008: ADR-006'nın "3 tekrar" eşiği aşıldı — paylaşılan gateway-client modülü çıkarılacak (ama paket değil, vendored dosya)

**Tarih:** 2026-08-31 · **Durum:** Kabul edildi

**Bağlam:** İki bağımsız Reviewer Agent denetimi (`ai-job-gateway`/`prompt-template-manager`/`model-comparison-harness` odaklı), ADR-006'nın kendi belirlediği "3+ tekrar oluşursa yeniden değerlendir" eşiğinin somut, hipotetik olmayan bir kanıtla aşıldığını gösterdi: submit→poll→terminal-durum-eşleme mantığı üç repoda bağımsız olarak yazıldı (`ai_job_gateway/client.py`, `prompt_template_manager/gateway_client.py`, `model_comparison_harness/backends.py::GatewayBackend`), ve aynı ince hata (`GET .../jobs/{id}`'in süresi geçmiş bir job için döndürdüğü `410 Gone`'u `raise_for_status()`'tan *önce* kontrol etmek gerektiği) doğru implementasyonda (#1, orijinal referans) doğru yazıldı, diğer ikisinde (#2, #3) bağımsız olarak *aynı şekilde* yanlış yazıldı. Bu, tekrarın teorik değil gerçek bir bakım/doğruluk riski olduğunun kanıtı.

**Karar:** Paylaşılan mantığı çıkar, ama ADR-006'nın "repo'lar arası Python-seviyesi bağımlılık yok" ilkesini bozmadan: submit/poll/terminal-durum-eşleme (yalnızca bu ~15-20 satır) için bağımlılıksız, tek dosyalık, her repoya **vendored** (kopyalanan, pip ile kurulmayan) bir referans modül tutulacak — `research/lab/shared/gateway_poll.py` (bu repoda, kanonik kaynak olarak) — ve her tüketici repo bu dosyayı olduğu gibi kopyalar, üstüne kendi ince sarmalayıcısını (senkron/async, hata tipi mapping'i) yazar. Gerçek bir pip paketi (`ai-ecosystem-common`) hâlâ reddedilir — ayrı sürümleme/yayın yükü, bu ölçekte gereksiz. Vendored dosyanın başına, kaynağını ve "elle senkronize et" uyarısını belirten bir yorum eklenir (nova-drift'in `prng.spec.js` içinde zaten kullandığı desenin aynısı — bkz. Reviewer raporu).

**Alternatifler değerlendirildi:**
- Gerçek bir pip paketi olarak çıkarmak — reddedildi, ADR-006'nın "bağımsız sürümlenebilir repo" hedefiyle çelişir, bu ölçekteki 3 repo için aşırı.
- Hiçbir şey yapmama, sadece 3 repoda ayrı ayrı düzeltmeye devam etme — reddedildi, Reviewer raporu bunun tam olarak neden başarısız olduğunu (aynı hata iki kez bağımsız tekrarlandı) somut olarak gösterdi.
- Sadece dokümantasyon (BACKLOG.md'de "bu mantık drift riski taşıyor" notu, kod değişikliği yok) — yetersiz, Reviewer'ın önerdiği minimum çözüm ama gerçek riski azaltmıyor, sadece kaydediyor.

**Sonuç:** Backlog'a P1 iş olarak eklendi: `research/lab/shared/gateway_poll.py` kanonik dosyasını yaz, üç repoya vendor et, her reponun kendi `gateway_client.py`/`backends.py`/`client.py` dosyasını bunun üzerine ince bir sarmalayıcıya indirge, testleri koru.

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
