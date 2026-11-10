# Skill envanteri

Tarih: 10 Kas 2026. Etiket ve durum sözlüğü: [README.md](README.md).
Kabul kuralları: depo [CLAUDE.md](../../CLAUDE.md) ve [PROVENANCE.md](../../.claude/skills/PROVENANCE.md).

Bu oturumda hiçbir skill depoya eklenmedi, güncellenmedi ya da çıkarılmadı.
Skill metinleri okundu (D); skill'ler çağrılarak denenmedi. Bu yüzden çoğu satır "test edilmedi" etiketlidir.

## 1. Sayım (D)

Diskte 180 `SKILL.md` bulundu. Dağılım: 71 `anthropic-skills:` senkron kovası, 8 Furkiozknn, 43 claude.ai yerleşik örneği (`/mnt/skills`).
Kalanı plugin önbellekleri ve npm paket kopyalarıdır.
Senkron kovada `curl | sh` deseni hiç yok (D: grep boş döndü).

## 2. Furkiozknn kilitli skill'leri (8)

Kanıt (D): `python3 .claude/skills/kilit.py --kontrol` → `KILIT: 79 dosya kilitle ayni`, çıkış 0.
Diskteki 8 skill, PROVENANCE tablosundaki 8 satırla birebir eşleşiyor.

| Skill | Yayıncı @ pin | Ne yapar | Bu projede rolü | Durum |
|---|---|---|---|---|
| playwright-cli | Microsoft, npm `@playwright/cli@0.1.21` | Tarayıcı otomasyonu, Playwright testi | Ink sayfası ve lore sitesi denemeleri (T) | `Kuruldu ve doğrulandı` |
| false-green-gate | FURKIOZKNN | "Yeşil" sonucun gerçek olup olmadığını doğrular | Her kapıda: test, render, medya çıktısı (T) | `Kuruldu ve doğrulandı` |
| frontend-design | `anthropics/skills@3337550` | Belirgin, bilinçli arayüz tasarımı | Lore sitesi tasarımında ilk tercih | `Kuruldu ve doğrulandı` |
| animate | `emilkowalski/skills@d16ebe6` | Arayüz hareketini sıfırdan kurma | Web/arayüz geçişleri. **Karakter animasyonu için değil** | `Kuruldu ve doğrulandı` |
| review-animations | `emilkowalski/skills@d16ebe6` | Hareket kodu incelemesi | Web/arayüz geçişleri | `Kuruldu ve doğrulandı` |
| accessibility | `addyosmani/web-quality-skills@afa8da9` | WCAG 2.2 denetimi | Lore sitesi ve hikâye oyunu denetimi | `Kuruldu ve doğrulandı` |
| core-web-vitals | `addyosmani/web-quality-skills@afa8da9` | LCP / INP / CLS iyileştirme | Lore sitesi denetimi | `Kuruldu ve doğrulandı` |
| performance | `addyosmani/web-quality-skills@afa8da9` | Web performansı | Lore sitesi denetimi | `Kuruldu ve doğrulandı` |

Hiçbiri dış servise gitmiyor (D). Hikâye, dünya kurma ya da maskot işine özel kilitli skill yok (D).

## 3. `anthropic-skills:` senkron kovası (71)

Bu önek bir **yayıncı değil**, claude.ai senkron kovasıdır. Kovadaki her skill'in kaynağı ayrıca doğrulanmalıdır (depo kuralı).
Aşağıdaki etiketler "oturumda hazır mı" sorusunu yanıtlar; depoya kabul ayrı bir karardır.
Raporlarda ayrı etiketi olmayan skill'ler bulundukları grubun etiketini aldı (T).

### 3a. Kullanılabilir: yerel ve ücretsiz, ama denenmedi (40)

Hepsi `Mevcut ancak test edilmedi`. Dış anahtar istemiyorlar (D: skill metni tarandı).

| Alan | Skill'ler | Not |
|---|---|---|
| Hikâye ve doküman | doc-coauthoring, docx, pptx, xlsx, pdf, docs, internal-comms | doc-coauthoring'in "Reader Testing" aşaması bağlamsız alt ajanla çelişki denetimi tarif ediyor (D). docx kendi notunda önce Claude Docs'u öneriyor (D) |
| Ajan ve meta | deep-research, subagent-driven-development, skill-creator, mcp-builder, karpathy-guidelines, task-observer, learn, import-memory, morning | deep-research alt ajan aracı ister; web erişimi bulutta kısıtlı (D). skill-creator ve mcp-builder isteğe bağlı `ANTHROPIC_API_KEY` kullanabiliyor (D) |
| Animasyon ve kod | remotion, manim-composer, manimgl-best-practices, lottie-bodymovin, threejs-* (10 adet) | remotion metni diskte olmayan bir "video toolkit" deposunu varsayıyor; yalnız rehber metin olarak işe yarar (D). lottie-bodymovin After Effects varsayıyor (D) |
| Görsel ve tasarım | canvas-design, algorithmic-art, theme-factory, visual-style, brand-guidelines, d3-viz, slack-gif-creator, flux-best-practices | flux-best-practices yalnız prompt rehberi. slack-gif-creator maskot çıkartması için kullanılabilir (T) |
| Yerel video | ffmpeg, video-edit | ffmpeg komutunun kendisi bu oturumda çalıştı (D); skill çağrılmadı. video-studio'nun kendi tarifleri daha projeye özel (D) |

### 3b. Kurulum ya da başka ortam bekleyenler (5)

Hepsi `Kullanılabilir ancak kurulum bekliyor`.

| Skill | Eksik olan | Kanıt |
|---|---|---|
| manimce-best-practices | Manim CE kurulu değil. Maskot için değil, açıklayıcı animasyon için | D |
| video-download | yt-dlp kurulu değil | D: `command -v` |
| built-in-browser, chrome-browser, computer-use | Masaüstü uygulaması ya da Chrome eklentisi gerekir | D: skill metni |

### 3c. Ücretli anahtar isteyenler (12)

Hepsi `Ücretli veya onay gerektiriyor`. Servis ayrıntısı: [AI_TOOLS_INVENTORY.md](AI_TOOLS_INVENTORY.md).

| Skill'ler | Servis ve anahtar | Not |
|---|---|---|
| create-video, avatar-video, video-translate | HeyGen, `HEYGEN_API_KEY` | Ücretli (D) |
| elevenlabs, music, sound-effects, speech-to-text, agents, setup-api-key | ElevenLabs, `ELEVENLABS_API_KEY` | Ücretsiz planda ticari kullanım yok (D: depo notu) |
| azure-speech-to-text | Azure, `AZURE_SPEECH_KEY` | Maliyet raporlarda yok |
| acestep | RunPod, `RUNPOD_API_KEY` | Skill'in varsaydığı `tools/music_gen.py` da diskte yok (D) |
| bfl-api | BFL, `BFL_API_KEY` | Ücretli (D) |

### 3d. Kırık ya da bu yığına uymayanlar (4)

Hepsi `Uyumsuz`.

| Skill | Neden | Kanıt |
|---|---|---|
| ltx2 | Varsaydığı `tools/ltx2.py` diskte yok. Ayrıca Modal GPU ve `HF_TOKEN` ister (ücretli) | D: `find` boş |
| ui-ux-pro-max | Klasörde yalnız `SKILL.md` var; çağırdığı `scripts/search.py` yok. PROVENANCE'ta zaten ret | D |
| beautiful-mermaid (skill) | `scripts/render.ts` ve `create-html.ts` yok; olmayan bir `agent-browser` skill'ini istiyor; pinsiz `npx tsx`; `--allow-net`. Karar: ret. Kütüphanenin kendisi ayrı ve çalışıyor | D |
| web-artifacts-builder | Betiği pinsiz kurulum yapıyor; bağımlılıksız tek dosya oyun yığınına uymaz. claude.ai artifact'leri için olur | D |

### 3e. Reddedilen ya da gereksiz olanlar (10)

Hepsi `Gereksiz veya önerilmiyor`.

| Skill | Neden | Kanıt |
|---|---|---|
| web-design-guidelines | Her koşuda uzak bir deponun `main` dalından talimat çekip **talimat olarak uyguluyor**. Depo kuralına aykırı. Karar: ret; PROVENANCE'ta zaten ret | D: `SKILL.md` satır 23-36 |
| website-to-video | Pinsiz `npx hyperframes` (her koşuda en son sürüm); olmayan bir skill'e yönlendiriyor. Karar: ret | D: satır 39, 106 |
| text-to-speech | Gemini'ye değil HeyGen'e gidiyor; mevcut Gemini TTS ile çakışıyor. Karar: ret | D: satır 5-24 |
| faceswap | Gerçek yüz değiştirir; kişilik hakları riski | D/T |
| playwright-recording | Pinsiz `npm install` ve `npx playwright install`; video-studio'da aynı işi yapan betikler var | D |
| framer-motion | React yok. PROVENANCE: "Emil ile çelişen değerler" | D |
| tailwind-design-system | Site ve oyunlar Tailwind kullanmıyor | D |
| vercel-react-best-practices, vercel-composition-patterns | React/Next yok | D |
| video-understand | Yerel whisper ister, burada yok; PC'de whisper-ctranslate2 aynı işi görüyor | D |

## 4. Diskteki diğer skill kaynakları (D)

| Kaynak | İçerik | Durum |
|---|---|---|
| `/mnt/skills/public` (8) | docx, pdf, pptx, xlsx, pdf-reading, file-reading, frontend-design, product-self-knowledge | `Mevcut ancak test edilmedi` |
| `/mnt/skills/examples` (35) | Yaratıcı işe uyanlar: `paint` (kodla suluboya, görüntü modeli kullanmaz), `video-making`, `artifact-emulator` | `Mevcut ancak test edilmedi` |
| computer-use-desktop | Konteynerin kendi Linux masaüstünde GUI kullanımı | `Mevcut ancak test edilmedi` |
| Plugin skill'leri | canva, dropbox, tinyfish, fastly, vpai, grasp, cowork | Bkz. [PLUGINS_AND_MCP_INVENTORY.md](PLUGINS_AND_MCP_INVENTORY.md) |

doc-coauthoring ve docx kopyaları senkron kova ile `/mnt/skills` arasında birebir aynı (D: `diff -rq`).

## 5. Dış skill depoları ve kabul kararları

Hiçbiri kurulmadı. Klonlar yalnız **statik** okundu; klonlanan kodu çalıştırma girişimi oturum izin sınıflandırıcısı tarafından reddedildi (D).

| Depo @ pin | Lisans, son commit | İçerik | Tarama sonucu | Kabul kararı | Durum |
|---|---|---|---|---|---|
| `danjdewhurst/story-skills` @ `3c0e034` | MIT, 2026-11-04, ★406, plugin 0.24.1 | 24 skill + `story` CLI (Node ≥18, sıfır bağımlılık). Süreklilik motoru: ölüm, vaat/ödeme, açık sorular, sahne kadrosu | Çalışma zamanında ağ yok. Shell yalnız PDF motoru ve salt okuyan git. Proje dışına yalnız geçici dizin. Hook yok (D) | **Pin sonrası kabul, koşullu** | `Kullanılabilir ancak kurulum bekliyor` |
| gamedev `dialogue-systems` + `visual-novel` @ `4cce500` | Apache-2.0, 2026-11-09 | Düz markdown, betik yok. Ink/Yarn karar akışı, "dalları yürü" doğrulaması | Dış bağlantı yok; hook yok (D) | **Pin sonrası kabul** (yalnız bu 2 skill) | `Kullanılabilir ancak kurulum bekliyor` |
| `gamedev-skills/awesome-gamedev-agent-skills` (geri kalanı) | Apache-2.0 | Godot, Unity, Unreal, web motorları, tür ve disiplin skill'leri | Zararlı kod yok; ama kurulum yolu `main`'i çekiyor, pin yok (D) | Alınmaz | `Gereksiz veya önerilmiyor` |
| `zenstory-ai/oh-story-claudecode` @ `7e26aa0` | MIT, 2026-11-09, ★8.467 | 14 skill, Çince web romanı | `browser-cdp` kimlik bilgisi topluyor (aşağıda) | **Ret (kritik)** | `Gereksiz veya önerilmiyor` |
| `jtydhr88/screenwriting-skills` | MIT, 2026-10-02, ★2.011 | 26 skill: diyalog, çatışma, dizi yazımı. Zanaat rehberi, araç değil | Yalnız markdown ve bir kontrol betiği; ağ ve hook yok (D: hikâye raporu) | Güvenlik raporu incelemedi; karar yok | `Kullanılabilir ancak kurulum bekliyor` |
| `eternityspring/shuohao-skills` | Apache-2.0, 2026-11-09, ★6.355 | 7 skill, Çince kısa drama hattı | Bir betik OpenAI/ComfyUI'ye istek atıyor (anahtar ister); `install.sh` var (D) | Alınmaz | `Gereksiz veya önerilmiyor` |
| `NachaFromMars/novel-guardian` | MIT, 2026-06-23, ★2 | Tek skill, Vietnamca'ya ayarlı | Ağ çağrısı yok (D) | Alınmaz | `Gereksiz veya önerilmiyor` |

Kod aramasında çıkan derleme depoları (`sickn33/agentic-awesome-skills`, `tobyilee/book-writer`) okunmadı; değerlendirme yok.

### story-skills: kabul koşulları (güvenlik raporu)

1. Yayıncı doğrulaması yapılmadı (tek kişi; güven düzeyi belirlenmedi).
2. Paketlenmiş `story.js` 36.649 satır; elle denetlenemiyor. Kaynakla eşitliği bizim tarafımızdan yeniden üretilip doğrulanmadı.
3. İzole bir çalıştırma testi (`story continuity` örneği) yapılmadı.
4. `/plugin install` ile kurulursa `main` izlenir ve kurala takılır. Elle kopyalanıp tam SHA'ya pinlenmeli: `3c0e0346ee09ded32546d9481ac18ec5324f02c3`.
5. Kendi klasör yapısını ister (`characters/`, `chapters/`, `continuity/`); kanonun `evren/` yapısıyla eşleme işi çıkar (T).

### gamedev iki skill: kabul koşulları

- Tam SHA: `4cce500ce1a779b12fdd824be581c7d2ab4e7ba2`. İki klasör elle kopyalanır; `npx skills update` ve marketplace yolu kullanılmaz.
- Apache-2.0 madde 4: LICENSE ve NOTICE korunur; değişen dosyalara not düşülür. PROVENANCE'ın "Proje değişiklikleri" bölümü bunun içindir.
- Depodaki 223 commit'in 126'sı bot benzeri bir hesaptan (T); yayıncı güven düzeyi düşük.
- `fay-hatti/skills-lock.json` bu depodan skill'leri listeliyor ama commit ya da ref tutmuyor; dosyalar depoda değil (D).
  Lock'taki hash'ler bugünkü depoyla iki aday algoritmada da eşleşmedi. Algoritma bilinmediği için bu kurcalama kanıtı değildir (D).

### oh-story `browser-cdp`: neden ret (D, statik okuma)

- Kullanıcının Chrome profilinin tamamını kopyalıyor; buna Cookies, Login Data (kayıtlı parolalar) ve Web Data dahil.
- Chrome'u açık bir uzaktan hata ayıklama portunda, origin kısıtı olmadan başlatıyor.
- Açıklamasında oturum token'ı çıkarmayı tarif ediyor.
- Sonuç: kimlik bilgisi toplayan desen. Depo güvenlik önceliğine aykırı.

## 6. Kabul kapısı (özet)

Sıra: yayıncı doğrulaması → güvenlik taraması → mevcut sistemle karşılaştırma → commit pin → PROVENANCE satırı → `kilit.py --uret`.
Eklenmeyenler: `@latest`, çalışma anında `main`'den talimat çeken skill, `curl | sh` kuran skill.
Skill kabulü her zaman sahibin onayını ister; sıradaki adımlar [NEXT_STEPS.md](NEXT_STEPS.md) içinde.

## 7. Düzeltmeler ve sayım farkları

- **website-to-video.** Oyun-web raporu "HeyGen girişi istiyor" demişti. Düzeltme (güvenlik): giriş isteğe bağlı; asıl sorun pinsiz `npx`.
- **oh-story.** Hikâye raporu "token çıkarma" demişti. Güvenlik raporu doğruladı ve ağırlaştırdı: profil ve parola veritabanı kopyası da var.
- **story-skills.** Hikâye raporunun "ağ yok" bulgusu doğrulandı. Ek: PDF motorları arasında Chrome da var; yayıncının CI betiğinde bir ağ çağrısı var (skill kullanımında çalışmıyor).
- **threejs skill sayısı.** Envanter ve oyun-web 10, görsel raporu 11 diyor. 71'lik toplam 10 ile tutuyor; 10 yazıldı.
- **fay-hatti lock sayısı.** Envanter 78, oyun-web "76 skill + router" diyor. Kesin sayı bu belgeye yazılmadı.
