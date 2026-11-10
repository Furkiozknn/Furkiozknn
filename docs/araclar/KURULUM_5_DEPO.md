# Beş GitHub deposu: inceleme ve kurulum sonucu

Tarih: 10 Kas 2026. Etiket sözlüğü: [README.md](README.md). İstek: beş depoyu incele, projeye uygun olanı kur, çalıştığını doğrula.
Kalıcı kurulum bu depoya commit demektir (bulut konteyneri geçici). Kabul sırası `CLAUDE.md`'deki gibidir: yayıncı → güvenlik taraması → karşılaştırma → pin → PROVENANCE → kilit.
Bu oturumda çalışan tek yapay zekâ Claude'dur (ana oturum + alt ajanlar); Gemini/NVIDIA çalıştırılmadı.

## Özet

| Depo @ incelenen commit | Lisans | Karar | Durum |
|---|---|---|---|
| nvidia/skillspector @ `16db7a0` (v2.12.0) | Apache-2.0 | **Kuruldu**: CI kapısı (`.github/workflows/skill-tarama.yml`); araç depoya kopyalanmaz, commit + özet pinli kurulur | `Kuruldu ve doğrulandı` (yerelde; GitHub'daki ilk koşu bu PR'da) |
| gamedev-skills/awesome-gamedev-agent-skills @ `4cce500` | Apache-2.0 | **Kısmen kuruldu**: yalnız `dialogue-systems` ve `visual-novel` (78 skill'in 2'si) | `Kuruldu ve doğrulandı` |
| tashfeenahmed/freellmapi @ `8b4c7a3` | MIT | **PC'de kurulur** (anahtarlar yalnız PC'de); burada derlendi ve çevrimdışı sınandı | `Kullanılabilir ancak kurulum bekliyor` |
| arjun988/blender-skills @ `904f095` | MIT | **Şimdilik kurulmadı**: Blender + Blender MCP ister; 3D maskot sonraki fazda | `Kullanılabilir ancak kurulum bekliyor` |
| dietrichgebert/ponytail @ `96608e0` | MIT | **Kurulmadı**: hook'ları her oturuma kural enjekte eder, ev dizinine yazar | `Gereksiz veya önerilmiyor` |

Mevcut kurulumlar: depoda 8 kilitli skill vardı (şimdi 10); `fay-hatti/skills-lock.json` gamedev skill'lerini commit'siz, yalnız özetle listeliyor ve dosyalar depoda yok — güncellenecek bir kurulum değil, dokunulmadı.

## 1. SkillSpector (skill güvenlik tarayıcısı)

- Ne yapar: skill dosyalarını statik tarar (71 kalıp), taranan kodu çalıştırmaz. `--no-llm` ile hiçbir modele içerik gitmez; tek dış çağrı, skill bağımlılık dosyası taşıyorsa `api.osv.dev` (bugün öyle bir skill yok). (K, D)
- Nasıl kuruldu: `skill-tarama.yml` her PR'da (skill ya da kapı dosyası değişince) SkillSpector'ı tam commit SHA'sı ve `gereksinimler.txt`'teki sha256 özetleriyle kurar, önce kapının kırmızıya dönebildiğini sınar (çalışma anında yazılan kötü skill), sonra `.claude/skills/` altını tarar. Baseline dışında HIGH/CRITICAL bulgu = kırmızı. (D)
- Doğrulama (D): kötü örnek skill → çıkış 1, skor 100, 6 HIGH; temiz örnek → çıkış 0, SAFE. `tara.py` 10 skill'de PASS; bozulmuş kopyada çıkış 1. İş akışı adımları yerelde tek tek koşuldu; `zizmor` bulgusuz, `politika.py --kati` PASS.
- Aracın kendi test paketi tam yeşil **değil**: 21907 geçti, 1 kaldı (LLM yığınlama testi; tiktoken indirmesi proxy'de 403). Statik yolla ilgisi yok; yine de "geçti" denmiyor.
- Mevcut 8 skill'de 22 HIGH bulgu çıktı; hepsi tek tek incelendi, gerçek zafiyet yok (15'i tarayıcının "dosyayı tam ayrıştıramadım" uyarısı, 5'i yanlış pozitif, 2'si `false-green-gate` betiğinin bilinen yetenekleri). Her biri gerekçesiyle `.github/skill-tarama/baseline.yaml`'da; toplu bastırma yok, MEDIUM/LOW her koşuda listelenir.

## 2. gamedev skill'leri: `dialogue-systems`, `visual-novel`

- Ne için: Ink ile dallanan hikâye/diyalog (bkz. [CREATIVE_PRODUCTION_PIPELINE.md](CREATIVE_PRODUCTION_PIPELINE.md)); düz Markdown, betik ve URL yok. (D)
- Tek değişiklik: frontmatter'a `disable-model-invocation: true` (depodaki diğer üçüncü taraf skill'ler gibi yalnız açık çağrıyla yüklenir). Gövde ve `references/` pinli commit ile bayt bayt aynı; Apache-2.0 gereği `LICENSE` + `NOTICE` kopyalandı. Kayıt: `.claude/skills/PROVENANCE.md`, kilit 79 → 88 dosya (`kilit.py --kontrol` geçer). (D)
- SkillSpector: ikisi de SAFE (0 HIGH). Upstream'in kendi örnek testi kurulu kopyada 2/2 geçti. `visual-novel` yalnız okunarak ve taranarak doğrulandı (çalıştırılacak kodu yok).
- Kalan 76 skill ilgisiz motorlar için; alınmadı.

## 3. FreeLLMAPI (ücretsiz LLM katmanlarını tek `/v1` uç noktasında toplayan yönlendirici)

- Bulutta yapılan (D): Node 22 ile `npm ci --ignore-scripts`, derleme, sunucu birim testleri (398 dosya, 5104 geçti, 6 atlandı), ağsız ortamda başlatma; yerel sahte sağlayıcıyla `POST /v1/chat/completions`, akış ve `/v1/messages` uçtan uca 200. Açılışta tek dış deneme: `api.freellmapi.co` (katalog akışı).
- Yapılamayan: gerçek sağlayıcı çağrıları (anahtar yok), Windows'a özgü her şey.
- Güvenlik notları (K): varsayılan bağlama tüm arayüzler → `HOST=127.0.0.1` şart; `/v1` her zaman anahtar ister, varsayılan parola yok; sağlayıcı anahtarları AES-256-GCM, ama birleşik `/v1` anahtarı veritabanında düz metin; imzalı katalog akışı yalnız model listesini değiştirebilir (`CATALOG_SYNC_DISABLED=1` ile kapanır); `npm audit` 13 yüksek uyarı; README'deki `curl … | bash`, `:latest` Docker etiketi ve imzasız, kendini güncelleyen Windows `.exe` **kullanılmaz**.
- Kullanım koşulu riski: sağlayıcı başına birden çok anahtarı havuzlayabiliyor; sağlayıcı başına **tek** anahtarla kullanın.
- ai-router ile ilişki: Gemini/NVIDIA çağrısı örtüşür; kuyruk, relay ve QA'nın yerini tutmaz. İstenirse ai-router'a tek satırlık sağlayıcı kaydıyla eklenir (denenmedi).

PC adımları (sahibi yapar; anahtarlar depo klasörüne yazılmaz):

```powershell
git clone https://github.com/tashfeenahmed/freellmapi.git D:\araclar\freellmapi
cd D:\araclar\freellmapi
git checkout 8b4c7a36e3e147bb5add2a5ba4fd95dd6f5120d3
npm ci --ignore-scripts
npm rebuild better-sqlite3
npm run build -w server ; npm run build -w client
mkdir D:\freellmapi-veri
$env:NODE_ENV='production'; $env:HOST='127.0.0.1'; $env:PORT='3001'
$env:FREEAPI_DB_PATH='D:\freellmapi-veri\freeapi.db'
$env:CATALOG_SYNC_DISABLED='1'
$env:ENCRYPTION_KEY='<64 hex; parola yöneticisinde saklanır>'
node server\dist\index.js
```

Sonra: `http://127.0.0.1:3001` adresinde hemen yönetici hesabını açın (hesap açılana kadar yerel her istemci açabilir), sağlayıcı başına tek anahtar girin, `netstat` ile yalnız `127.0.0.1:3001` dinlendiğini doğrulayın. Çağrı biçimi: `OPENAI_BASE_URL=http://127.0.0.1:3001/v1` + birleşik anahtar.

## 4. blender-skills (94 skill)

- Düz Markdown, betik yok; SkillSpector 94/94 SAFE. Risk kurulum tarafında: `.mcp.json` pinsiz `uvx blender-mcp` çalıştırır, kurulum belgesi `main`'den `addon.py` indirtir (depo kuralına aykırı). (K)
- Gerçek deneme (D): resmî `bpy` 5.2.3 tekerleği geçici klasöre kuruldu, skill'in örnek kodu ve GLB dışa aktarımı çalıştı (geçerli glTF 2.0, 1 ağ), sonra kaldırıldı. Rig, turnaround render ve Blender MCP denenmedi.
- Neden şimdi değil: 3D maskot hattı ertelendi, PC donanımı (8 GB RAM, Intel UHD) sınırda, 94 skill açıklaması her oturuma yük. Gerekince en küçük alt küme: `character-artist`, `rigging`, `export-pipeline` + ortak `references/`, pinli ve MCP kurulumu elden.

## 5. ponytail

- Skill metinleri temiz (6/6 SAFE) ve test/kanıt atlamayı söylemiyor. Ret nedeni hook'lar (K): her oturuma kural seti enjekte eder, `~/.claude` ve `~/.config/ponytail/` altına yazar, ajana kullanıcının `settings.json`'unu değiştirmeyi önertir, isteğe bağlı webhook'a ilk istemi içeren görev satırını gönderebilir, oturum dökümlerini okuyan bir içe aktarma komutu vardır; pazar yeri kurulumu `main`'i izler.
- İstenirse güvenli biçim: yalnız `skills/ponytail` + `skills/ponytail-review`, pinli, yalnız açık çağrı, hook'suz. Ana skill her kod işinde kendini çağırdığı ve depodaki kurallarla örtüştüğü için şimdilik alınmadı.

## Sahibin kararına kalanlar

- FreeLLMAPI'yi PC'ye kurmak, anahtarları girmek, katalog akışını açık tutup tutmamak.
- ponytail skill'lerini hook'suz biçimde isteyip istemediği.
- 3D maskot fazı açılınca blender alt kümesi.
