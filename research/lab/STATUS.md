# AI Creative Platform — Lab Status

**Bu dosya, her yeni oturumun/devamın ilk okuması gereken dosyadır.** Mevcut ekosistem durumu, aktif işler, ve "kaldığımız yer" burada tutulur. Diğer lab dosyaları: [`BACKLOG.md`](./BACKLOG.md) (fikir/araştırma/teknik borç), [`DECISIONS.md`](./DECISIONS.md) (mimari kararlar, ADR), [`TECH-RADAR.md`](./TECH-RADAR.md) (teknoloji değerlendirmeleri).

Son güncelleme: 2026-08-31

---

## Ekosistem Haritası

| Repo | Amaç | Durum | Kalite Kapısı |
|---|---|---|---|
| [`Furkiozknn/Furkiozknn`](https://github.com/Furkiozknn/Furkiozknn) | Profil + araştırma/mimari dokümanları + lab durumu (bu dosyalar) | Aktif, PR #2 açık (draft) | — (doküman reposu) |
| [`ai-job-gateway`](https://github.com/Furkiozknn/ai-job-gateway) | Provider-agnostic async job gateway (submit/poll/webhook) — ekosistemin orkestrasyon çekirdeği | ✅ main'e push edildi | ✅ 45/45 test, uçtan uca doğrulandı |
| [`prompt-template-manager`](https://github.com/Furkiozknn/prompt-template-manager) | Versiyonlanmış, git-diff'lenebilir prompt/pipeline şablonları + CLI (`ptm`) | ✅ main'e push edildi | ✅ 42/42 test, ai-job-gateway ile uçtan uca entegre |
| [`model-comparison-harness`](https://github.com/Furkiozknn/model-comparison-harness) | Aynı isteği birden fazla backend'e paralel gönderip gecikme/başarı/sonuç karşılaştırması (`mch`) | ⏳ Yerel commit hazır, kullanıcının boş repo açması bekleniyor | ✅ 36/36 test, ai-job-gateway ile uçtan uca entegre |
| [`mini-creative-toolkit`](https://github.com/Furkiozknn/mini-creative-toolkit) | Yerel, CPU-only görsel/video araçları (MCP server) | ✅ PR #1 açık, CI yeşil | ✅ 23/23 test |
| [`nvidia-nim-mcp`](https://github.com/Furkiozknn/nvidia-nim-mcp) | NVIDIA NIM ücretsiz katman modellerini Claude Code'a bağlayan MCP server | ✅ PR #1 açık, CI yeşil | ✅ 40/40 test |
| [`mcp-vet`](https://github.com/Furkiozknn/mcp-vet) | MCP server keşfi/doğrulama Claude Code skill'i + bağımsız CLI | ✅ PR #1 açık, CI yeşil | ✅ 30/30 test |
| [`kalp-animasyon`](https://github.com/Furkiozknn/kalp-animasyon) | Three.js sanat parçası (kişisel/hediye) | ✅ PR #1 açık, CI yeşil | ✅ Playwright smoke test yeşil |
| [`nova-drift`](https://github.com/Furkiozknn/nova-drift) | Three.js tarayıcı oyunu | ✅ PR #1 açık, CI yeşil | ✅ Playwright smoke test yeşil |

**Bekleyen kullanıcı aksiyonu:** `model-comparison-harness` için boş bir GitHub repository açılması gerekiyor (GitHub App'in repo oluşturma izni yok — bkz. `DECISIONS.md` "GitHub App repo-creation izni yok" kaydı). Aynı blokaj gelecekteki her yeni repo için de geçerli olacak; her seferinde tek tek sormak yerine, birikimli bir "bekleyen repo" listesi tutulacak (aşağıda).

**Bekleyen repo listesi (kullanıcı toplu açabilir):**
- `model-comparison-harness` (kod hazır, push bekliyor)
- `asset-provenance-toolkit` (bir sonraki sırada, henüz kod yazılmadı)

---

## Aktif Çalışma (bu oturumda)

1. **Lab altyapısı kuruluyor** (bu dosyalar) — backlog, ADR, tech radar.
2. **Reviewer/QA denetimi** — mevcut 8 repo bağımsız bir gözle (mimari, güvenlik, performans, gereksiz bağımlılık, teknik borç) taranacak; bulgular `BACKLOG.md`'nin teknik borç bölümüne eklenecek.
3. **Sıradaki geliştirme:** `asset-provenance-toolkit` (görsel/video çıktılarına pipeline metadata gömme/çıkarma, A1111 PNG-roundtrip deseninin genellenmiş hali).

## Otonom Döngü Kuralları (özet)

- Kullanıcı yeni bir görev vermediği sürece sistem kendi iş planını `BACKLOG.md`'den çıkarır, en yüksek değerli işi seçer, üretir, test eder, dokümante eder ve push eder (izin varsa) veya push için bekleyen listeye ekler.
- Her tamamlanan iş, `BACKLOG.md`'ye yeni fikir(ler) eklemeli — sistem asla "iş bitti, bekliyorum" durumuna düşmemeli.
- Geri dönüşü olmayan/maliyetli/kullanıcı onayı gerektiren işlemler (yeni repo oluşturma izni, mevcut bir repoya force-push, üçüncü taraf ücretli bir API'ye gerçek para harcanması vb.) ayrı işaretlenip kullanıcıya sorulur; geri kalan her şey bağımsız karar verilir.
- Rate limit / oturum kesintisi durumunda: bu dosya + `BACKLOG.md` + `TaskList` (harness task tracker) kaldığımız yeri gösterir. Baştan başlamak yerine buradan devam edilir.
