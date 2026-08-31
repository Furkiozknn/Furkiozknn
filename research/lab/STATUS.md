# AI Creative Platform — Lab Status

**Bu dosya, her yeni oturumun/devamın ilk okuması gereken dosyadır.** Mevcut ekosistem durumu, aktif işler, ve "kaldığımız yer" burada tutulur. Diğer lab dosyaları: [`BACKLOG.md`](./BACKLOG.md) (fikir/araştırma/teknik borç), [`DECISIONS.md`](./DECISIONS.md) (mimari kararlar, ADR), [`TECH-RADAR.md`](./TECH-RADAR.md) (teknoloji değerlendirmeleri), [`DESIGN-SYSTEM.md`](./DESIGN-SYSTEM.md) (ürün UX/tasarım sistemi araştırması), [`shared/gateway_poll.py`](./shared/gateway_poll.py) (vendored ortak modül, ADR-008).

> ⚠️ **ÖNEMLİ — ADR-011 (2026-08-31):** Bu `research/lab/*` dizini **`main`'e asla merge edilmeyecek**. Kullanıcı, PR #2'yi (araştırma içeriğini `main`'e taşıyan PR) bilinçli olarak bu dizini dışarıda bırakarak kapattı — `Furkiozknn/Furkiozknn` halka açık bir profil reposu, bu iç lab altyapısı orada görünmemeli. **Bu dizin kalıcı olarak sadece `claude/ai-creative-platform-research-fwh2vt` branch'inde yaşar** — neredeyse ayrı bir "lab reposu" gibi düşünün, sadece GitHub App izin kısıtı (ADR-007) yüzünden gerçek ayrı repo değil. Her yeni oturum bu branch'e commit/push etmeye devam etmeli; `main`'e karşı yeni bir PR açmaya **çalışmayın**. `main`'de sadece halka açık, "bitmiş" araştırma içeriği var (sentez dokümanları + `research/raw/*.md`).

Son güncelleme: 2026-08-31

---

## Ekosistem Haritası

| Repo | Amaç | Durum | Kalite Kapısı |
|---|---|---|---|
| [`Furkiozknn/Furkiozknn`](https://github.com/Furkiozknn/Furkiozknn) | `main`: profil + halka açık araştırma dokümanları. Bu branch (`claude/ai-creative-platform-research-fwh2vt`): lab durumu (bu dosyalar, `main`'e asla merge edilmez — ADR-011) | `main` güncel (araştırma içeriği merge edildi, PR #2 kapatıldı); bu branch aktif çalışma alanı | — (doküman reposu) |
| [`ai-job-gateway`](https://github.com/Furkiozknn/ai-job-gateway) | Provider-agnostic async job gateway (submit/poll/webhook) — ekosistemin orkestrasyon çekirdeği | ✅ main'e push edildi | ✅ 46/46 test, uçtan uca doğrulandı, Reviewer denetiminden geçti |
| [`prompt-template-manager`](https://github.com/Furkiozknn/prompt-template-manager) | Versiyonlanmış, git-diff'lenebilir prompt/pipeline şablonları + CLI (`ptm`) | ✅ main'e push edildi | ✅ 43/43 test, ai-job-gateway ile uçtan uca entegre, Reviewer denetiminden geçti |
| [`model-comparison-harness`](https://github.com/Furkiozknn/model-comparison-harness) | Aynı isteği birden fazla backend'e paralel gönderip gecikme/başarı/sonuç karşılaştırması (`mch`) | ⏳ Yerel commit hazır (3 commit ileride), kullanıcının boş repo açması bekleniyor | ✅ 37/37 test, ai-job-gateway ile uçtan uca entegre, Reviewer denetiminden geçti |
| [`asset-provenance-toolkit`](https://github.com/Furkiozknn/asset-provenance-toolkit) | Üretilen dosyalara pipeline provenance (capability/provider/params/job id) gömme/çıkarma — PNG native + evrensel sidecar | ⏳ Yerel commit hazır, kullanıcının boş repo açması bekleniyor | ✅ 48/48 test, `ai-job-gateway`'e karşı uçtan uca doğrulandı (`from-job`) |
| [`ai-workflow-engine`](https://github.com/Furkiozknn/ai-workflow-engine) | DAG pipeline orkestratörü — YAML ile tanımlı, `ai-job-gateway` job'larını zincirliyor (generate→upscale→lipsync), bağımsız adımlar eşzamanlı | ⏳ Yerel commit hazır (2 commit — biri Reviewer Agent düzeltmesi), kullanıcının boş repo açması bekleniyor | ✅ 34/34 test, `ai-job-gateway`'e karşı uçtan uca doğrulandı, Reviewer denetiminden geçti (1 HIGH bulgu bulundu ve düzeltildi: malformed Jinja2 syntax artık ham exception yerine temiz `PipelineRunError`) |
| [`mini-creative-toolkit`](https://github.com/Furkiozknn/mini-creative-toolkit) | Yerel, CPU-only görsel/video araçları (MCP server) | ✅ **PR #1 kullanıcı tarafından merge edildi** (`master`'da, CI yeşil) | ✅ 25/25 test, Reviewer denetiminden geçti, rembg lisans düzeltmesi (ADR-009) dahil |
| [`nvidia-nim-mcp`](https://github.com/Furkiozknn/nvidia-nim-mcp) | NVIDIA NIM ücretsiz katman modellerini Claude Code'a bağlayan MCP server | ✅ **PR #1 kullanıcı tarafından merge edildi** | ✅ 40/40 test, Reviewer denetiminde bulunan sınırsız eşzamanlılık düzeltmesi dahil |
| [`mcp-vet`](https://github.com/Furkiozknn/mcp-vet) | MCP server keşfi/doğrulama Claude Code skill'i + bağımsız CLI | ✅ **PR #1 kullanıcı tarafından merge edildi** | ✅ 30/30 test, Reviewer denetiminden geçti (temiz, sadece kozmetik not) |
| [`kalp-animasyon`](https://github.com/Furkiozknn/kalp-animasyon) | Three.js sanat parçası (kişisel/hediye) | ✅ **PR #1 kullanıcı tarafından merge edildi** | ✅ Playwright smoke test yeşil, Reviewer denetiminden geçti (XSS yüzeyi doğrulandı temiz) |
| [`nova-drift`](https://github.com/Furkiozknn/nova-drift) | Three.js tarayıcı oyunu | ✅ **PR #1 kullanıcı tarafından merge edildi** | ✅ Playwright smoke test yeşil, Reviewer denetiminden geçti (seeded RNG additive doğrulandı) |

**Bekleyen kullanıcı aksiyonu:** 5 eski PR'ın tamamı (mini-creative-toolkit, nvidia-nim-mcp, mcp-vet, kalp-animasyon, nova-drift) kullanıcı tarafından merge edildi ✅. Kalan tek aksiyon: üç repo için boş GitHub repository açılması gerekiyor (GitHub App'in repo oluşturma izni yok — bkz. `DECISIONS.md` ADR-007):
- `model-comparison-harness` (kod hazır, yerelde 3 commit push bekliyor)
- `asset-provenance-toolkit` (kod hazır, yerelde 1 commit push bekliyor)
- `ai-workflow-engine` (kod hazır, yerelde 2 commit push bekliyor)

Aynı blokaj gelecekteki her yeni repo için de geçerli olacak; her seferinde tek tek sormak yerine, birikimli bir liste tutulur (yukarıdaki iki madde).

---

## Aktif Çalışma (bu oturumda)

**Tamamlanan bu turda (Faz 3 — R&D lab derinleştirme):**
1. İki Reviewer Agent'ın (backend/CLI repoları + agent-yapımı repolar) denetim raporları okundu, senkronize edildi. Ucuz/güvenli düzeltmeler (`ai-job-gateway` job-sonsuza-askıda-kalma, `prompt-template-manager`+`model-comparison-harness` 410-Gone hatası, `nvidia-nim-mcp` sınırsız eşzamanlılık) push edildi.
2. `asset-provenance-toolkit` tamamlandı: 48 test yeşil, `ai-job-gateway`'e karşı canlı uçtan uca doğrulama (`aprov from-job`), commit alındı.
3. **ADR-008 uygulandı:** `research/lab/shared/gateway_poll.py` kanonik dosyası yazıldı, üç repoya vendor edildi (410-Gone kod-tekrarı hatasının kök nedeni). Testler yeşil (46/43/37).
4. **Yeni repo `ai-workflow-engine` inşa edildi:** DAG pipeline orkestratörü, YAML tanımlı, `ai-job-gateway` job'larını zincirliyor. 32 test, gerçek sunucuya karşı uçtan uca doğrulandı (2 adımlı generate→upscale zinciri, adımlar arası Jinja2 sonuç referansı).
5. **İki paralel araştırma ajanı** yeni domainleri derinlemesine tarad: (a) 3D üretim (TRELLIS/Hunyuan3D-2.1/TripoSR/InstantMesh) + segmentasyon (BiRefNet/RMBG-2.0/SAM), (b) ses/müzik/konuşma (ACE-Step/Kokoro/Chatterbox/F5-TTS/XTTS-v2) + karakter tutarlılığı (IP-Adapter/PuLID/InstantID). Tüm bulgular `TECH-RADAR.md`'ye işlendi.
6. **Gerçek, aktif bir lisans riski bulundu ve düzeltildi:** `mini-creative-toolkit::remove_background()`, `rembg` 2.0.81'in sessizce değişen iç varsayılanı yüzünden CC-BY-NC (ticari olmayan) "bria-rmbg" modelini kullanıyordu — teorik değil, doğrudan koddan doğrulandı. Commit `74d5dad` ile düzeltildi (her zaman açık `new_session(model)`, varsayılan `u2net`), ADR-009 olarak kaydedildi. Aynı düzeltmeyle BiRefNet de opt-in bir `model` parametresi olarak eklendi (`TECH-RADAR.md`'deki P1 madde artık ✅ uygulandı).
7. **ADR-010:** Ses klonlama için rıza/watermark politikası — herhangi bir klonlama modelinden önce şart, P0 blokaj olarak kaydedildi.
8. **`research/lab/DESIGN-SYSTEM.md` yazıldı** — 7 referans ürünün (Midjourney, Krea, Leonardo, Ideogram, Runway, ComfyUI, ElevenLabs) job/kuyruk-UX'i merceğinden analizi, token/etkileşim deseni önerileri, Next.js+TanStack Query+Tailwind v4+shadcn/ui teknik yığın önerisi.
9. **`ai-workflow-engine` + `mini-creative-toolkit` rembg düzeltmesi bağımsız Reviewer denetiminden geçirildi** (kendi yazdığım kod da kural dışı değil — hiçbir şey Reviewer'sız "mezun olmuyor"). Sonuç: rembg/bria-rmbg iddiası satır satır doğrulandı (gerçek); `ai-workflow-engine`'de 1 HIGH bulgu bulundu ve düzeltildi (malformed Jinja2 syntax artık `PipelineRunError`'a düzgün eşleniyor, 2 yeni test), Jinja2 sandboxsız-çalıştırma riski `prompt-template-manager`'daki eşdeğeriyle birlikte belgelendi.

**Sıradaki iş (backlog'dan seçilecek, hepsi API key gerektirmiyor):** Kokoro-82M TTS PoC, ACE-Step müzik PoC, FLUX.2 yerleşik çoklu-referans testi (blokajlı — FLUX API key gerekiyor), PuLID-FLUX InsightFace lisans doğrulaması. **Not:** Bu oturumda sandbox ağ bağlantısı zaman zaman çok yavaştı (pip kurulumları/model indirmeleri timeout'a uğradı) — bir sonraki oturumda ağ durumu tekrar kontrol edilmeli, canlı model kurulumu gerektiren işler (Kokoro/ACE-Step PoC'leri gibi) buna göre planlanmalı.

## Otonom Döngü Kuralları (özet)

- Kullanıcı yeni bir görev vermediği sürece sistem kendi iş planını `BACKLOG.md`'den çıkarır, en yüksek değerli işi seçer, üretir, test eder, dokümante eder ve push eder (izin varsa) veya push için bekleyen listeye ekler.
- Her tamamlanan iş, `BACKLOG.md`'ye yeni fikir(ler) eklemeli — sistem asla "iş bitti, bekliyorum" durumuna düşmemeli.
- Geri dönüşü olmayan/maliyetli/kullanıcı onayı gerektiren işlemler (yeni repo oluşturma izni, mevcut bir repoya force-push, üçüncü taraf ücretli bir API'ye gerçek para harcanması vb.) ayrı işaretlenip kullanıcıya sorulur; geri kalan her şey bağımsız karar verilir.
- Rate limit / oturum kesintisi durumunda: bu dosya + `BACKLOG.md` + `TaskList` (harness task tracker) kaldığımız yeri gösterir. Baştan başlamak yerine buradan devam edilir.
- Reviewer Agent deseni: bağımsız bir arka plan ajanı, ucuz/güvenli/düşük-riskli bulguları doğrudan düzeltip commit alır (push etmeden — ana oturum inceleyip push eder); mimari karar gerektiren veya riskli bulgular sadece raporlanır, `BACKLOG.md`'ye işlenir.
