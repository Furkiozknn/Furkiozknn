# AI Creative Platform — Lab Status

**Bu dosya, her yeni oturumun/devamın ilk okuması gereken dosyadır.** Mevcut ekosistem durumu, aktif işler, ve "kaldığımız yer" burada tutulur. Diğer lab dosyaları: [`BACKLOG.md`](./BACKLOG.md) (fikir/araştırma/teknik borç), [`DECISIONS.md`](./DECISIONS.md) (mimari kararlar, ADR), [`TECH-RADAR.md`](./TECH-RADAR.md) (teknoloji değerlendirmeleri), [`shared/gateway_poll.py`](./shared/gateway_poll.py) (vendored ortak modül, ADR-008).

Son güncelleme: 2026-08-31

---

## Ekosistem Haritası

| Repo | Amaç | Durum | Kalite Kapısı |
|---|---|---|---|
| [`Furkiozknn/Furkiozknn`](https://github.com/Furkiozknn/Furkiozknn) | Profil + araştırma/mimari dokümanları + lab durumu (bu dosyalar) | Aktif, PR #2 açık (draft) | — (doküman reposu) |
| [`ai-job-gateway`](https://github.com/Furkiozknn/ai-job-gateway) | Provider-agnostic async job gateway (submit/poll/webhook) — ekosistemin orkestrasyon çekirdeği | ✅ main'e push edildi | ✅ 46/46 test, uçtan uca doğrulandı, Reviewer denetiminden geçti |
| [`prompt-template-manager`](https://github.com/Furkiozknn/prompt-template-manager) | Versiyonlanmış, git-diff'lenebilir prompt/pipeline şablonları + CLI (`ptm`) | ✅ main'e push edildi | ✅ 43/43 test, ai-job-gateway ile uçtan uca entegre, Reviewer denetiminden geçti |
| [`model-comparison-harness`](https://github.com/Furkiozknn/model-comparison-harness) | Aynı isteği birden fazla backend'e paralel gönderip gecikme/başarı/sonuç karşılaştırması (`mch`) | ⏳ Yerel commit hazır (3 commit ileride), kullanıcının boş repo açması bekleniyor | ✅ 37/37 test, ai-job-gateway ile uçtan uca entegre, Reviewer denetiminden geçti |
| [`asset-provenance-toolkit`](https://github.com/Furkiozknn/asset-provenance-toolkit) | Üretilen dosyalara pipeline provenance (capability/provider/params/job id) gömme/çıkarma — PNG native + evrensel sidecar | ⏳ Yerel commit hazır, kullanıcının boş repo açması bekleniyor | ✅ 48/48 test, `ai-job-gateway`'e karşı uçtan uca doğrulandı (`from-job`) |
| [`mini-creative-toolkit`](https://github.com/Furkiozknn/mini-creative-toolkit) | Yerel, CPU-only görsel/video araçları (MCP server) | ✅ PR #1 açık, CI yeşil | ✅ 23/23 test, Reviewer denetiminden geçti (1 düşük öncelikli bulgu backlog'da) |
| [`nvidia-nim-mcp`](https://github.com/Furkiozknn/nvidia-nim-mcp) | NVIDIA NIM ücretsiz katman modellerini Claude Code'a bağlayan MCP server | ✅ PR açık (branch push edildi), CI yeşil | ✅ 40/40 test, Reviewer denetiminde bulunan sınırsız eşzamanlılık düzeltildi ve push edildi |
| [`mcp-vet`](https://github.com/Furkiozknn/mcp-vet) | MCP server keşfi/doğrulama Claude Code skill'i + bağımsız CLI | ✅ PR #1 açık, CI yeşil | ✅ 30/30 test, Reviewer denetiminden geçti (temiz, sadece kozmetik not) |
| [`kalp-animasyon`](https://github.com/Furkiozknn/kalp-animasyon) | Three.js sanat parçası (kişisel/hediye) | ✅ PR #1 açık, CI yeşil | ✅ Playwright smoke test yeşil, Reviewer denetiminden geçti (XSS yüzeyi doğrulandı temiz) |
| [`nova-drift`](https://github.com/Furkiozknn/nova-drift) | Three.js tarayıcı oyunu | ✅ PR #1 açık, CI yeşil | ✅ Playwright smoke test yeşil, Reviewer denetiminden geçti (seeded RNG additive doğrulandı) |

**Bekleyen kullanıcı aksiyonu:** İki repo için boş GitHub repository açılması gerekiyor (GitHub App'in repo oluşturma izni yok — bkz. `DECISIONS.md` ADR-007):
- `model-comparison-harness` (kod hazır, yerelde 3 commit push bekliyor)
- `asset-provenance-toolkit` (kod hazır, yerelde 1 commit push bekliyor)

Aynı blokaj gelecekteki her yeni repo için de geçerli olacak; her seferinde tek tek sormak yerine, birikimli bir liste tutulur (yukarıdaki iki madde).

---

## Aktif Çalışma (bu oturumda)

**Tamamlanan bu turda:**
1. İki Reviewer Agent'ın (backend/CLI repoları + agent-yapımı repolar) denetim raporları okundu, senkronize edildi. Ucuz/güvenli düzeltmeler (`ai-job-gateway` job-sonsuza-askıda-kalma, `prompt-template-manager`+`model-comparison-harness` 410-Gone hatası, `nvidia-nim-mcp` sınırsız eşzamanlılık) push edildi. Riskli/mimari-kararı gereken bulgular (SSRF, gövde boyutu, Jinja2 sandboxing, hata mesajı sızıntısı) `BACKLOG.md`'ye kaydedildi.
2. `asset-provenance-toolkit` tamamlandı: kaynak+test zaten yazılmıştı, `.gitignore`/CI/README/examples eklendi, 48 test yeşil, `ai-job-gateway`'e karşı canlı uçtan uca doğrulama yapıldı (`aprov from-job`), commit alındı.
3. **ADR-008 uygulandı:** İki bağımsız Reviewer denetiminin ortaya çıkardığı somut kod-tekrarı hatası (410-Gone kontrolünün iki repoda bağımsız olarak yanlış implemente edilmesi) üzerine, `research/lab/shared/gateway_poll.py` kanonik dosyası yazıldı ve `ai-job-gateway`, `prompt-template-manager`, `model-comparison-harness`'a vendor edildi. Her repo kendi public API/exception tiplerini korudu, sadece iç implementasyon paylaşılan modüle devredildi. Üç reponun testleri de yeşil (46/43/37). `model-comparison-harness`'ta ek olarak düşük öncelikli bir timeout tutarsızlığı da bu vesileyle düzeltildi.

**Sıradaki iş (henüz başlanmadı, backlog'dan seçilecek):** `BACKLOG.md`'nin P1 kalan maddeleri arasından — gerçek bir model provider (API key gerektirir, kullanıcı girdisi olmadan ilerlenemez) veya benchmark/evaluation altyapısının kalite-skorlama tarafı (mock backend'lerle bile genişletilebilir, API key gerektirmez) değerlendirilecek.

## Otonom Döngü Kuralları (özet)

- Kullanıcı yeni bir görev vermediği sürece sistem kendi iş planını `BACKLOG.md`'den çıkarır, en yüksek değerli işi seçer, üretir, test eder, dokümante eder ve push eder (izin varsa) veya push için bekleyen listeye ekler.
- Her tamamlanan iş, `BACKLOG.md`'ye yeni fikir(ler) eklemeli — sistem asla "iş bitti, bekliyorum" durumuna düşmemeli.
- Geri dönüşü olmayan/maliyetli/kullanıcı onayı gerektiren işlemler (yeni repo oluşturma izni, mevcut bir repoya force-push, üçüncü taraf ücretli bir API'ye gerçek para harcanması vb.) ayrı işaretlenip kullanıcıya sorulur; geri kalan her şey bağımsız karar verilir.
- Rate limit / oturum kesintisi durumunda: bu dosya + `BACKLOG.md` + `TaskList` (harness task tracker) kaldığımız yeri gösterir. Baştan başlamak yerine buradan devam edilir.
- Reviewer Agent deseni: bağımsız bir arka plan ajanı, ucuz/güvenli/düşük-riskli bulguları doğrudan düzeltip commit alır (push etmeden — ana oturum inceleyip push eder); mimari karar gerektiren veya riskli bulgular sadece raporlanır, `BACKLOG.md`'ye işlenir.
