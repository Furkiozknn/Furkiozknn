# Kurulum ve test raporu

Tarih: 10 Kas 2026. Etiket ve durum sözlüğü: [README.md](README.md).
Bu belgedeki her sonuç araştırma oturumunda çalıştırılmış ya da okunmuştur (D). Çıkarımlar ayrıca (T) ile işaretlidir.

## 1. Kapsam

- **Projeye hiçbir araç kurulmadı.** Hiçbir depoda dosya değişmedi, commit ya da push yapılmadı.
- Çalışan tek yapay zekâ Claude'dur: ana oturum ve Claude alt ajanları (4 alan araştırmacısı, 1 güvenlik/lisans denetçisi).
- Gemini, NVIDIA, OpenAI, ElevenLabs, HeyGen ve benzerleri **çalıştırılmadı**: anahtarları bu oturumda yok.
- Ücretli hiçbir çağrı yapılmadı; kredi harcanmadı. Dış sistemlere yazılmadı.
- Yerel denemeler yalnız oturumun geçici (scratch) klasöründe koştu. Paketler oraya indirildi; depolara eklenmedi.
- Klonlanan dış depoların kodu **çalıştırılmadı**; yalnız statik okundu.

## 2. Ortam (bulut konteyneri)

- 4 çekirdek, 15 GB RAM, GPU yok.
- Var: ffmpeg 6.1.1, ImageMagick 6.9, Chrome 153, node 22, pnpm 10, bun, uv, Python 3.13 (numpy, PIL), cargo, java, xvfb-run, pandoc.
- Yok: godot, blender, yt-dlp, whisper, inkscape, dotnet.
- Ağ: ayar `limited`, izinli host listesi boş. Açılanlar: npm kayıt defteri, PyPI, GitHub ham dosyaları, `git clone`.
- Açılmayanlar: `ai.google.dev`, `higgsfield.ai`, `copyright.gov`, `turkpatent.gov.tr`, `huggingface.co`, `blender.org`, `krita.org`, `inkscape.org`, `remotion.dev`; ayrıca Obsidian, Yarn Spinner, Fountain, Aeon Timeline, World Anvil ve Campfire siteleri.
  Bu sitelerdeki bilgi yalnız arama özetinden geldi (K-ikincil) ya da doğrulanmadı.

## 3. MCP salt okuma çağrıları

Bağlı her MCP'ye en az bir salt okuma çağrısı yapıldı. Çağrı ve sonuç tablosu: [PLUGINS_AND_MCP_INVENTORY.md](PLUGINS_AND_MCP_INVENTORY.md).

Özet:

- Bir çağrı başarısız oldu: Vercel `get_auth_user` → `404 not_found: User not found`. Yedek çağrı `list_teams` çalıştı.
- Higgsfield_Bridge bağlı ama bağlı uygulama sayısı 0.
- Canva, Dropbox ve TinyFish bağlanamadı: proxy 403.
- Drive üzerinden `osmanli-evreni/` kanonu bulundu ve okundu. Notion'da evren/karakter araması 0 sonuç verdi.
- Higgsfield'da yalnız bakiye, plan, katalog ve iş akışı metni okundu. Sonuç: 64,03 kredi, plan "starter".

## 4. Envanter kontrolleri

| Kontrol | Komut ya da çağrı | Sonuç |
|---|---|---|
| Skill sayımı | `find / -name SKILL.md` | 180 dosya |
| Furkiozknn kilidi | `python3 .claude/skills/kilit.py --kontrol` | `KILIT: 79 dosya kilitle ayni`, çıkış 0 |
| Senkron kovada pipe-to-shell | `grep` ile `curl ... \| sh` deseni | Eşleşme yok |
| Anahtar adları | Ortam değişkeni adları listelendi (değerler basılmadı) | Yapay zekâ servis anahtarı yok |
| Google Cloud | `gcloud config list` | Proje ve hesap tanımlı değil |
| Proxy durumu | Proxy durum uç noktası | Canva ve Dropbox hostları için 403 kaydı |
| Oturum ortamı | `get_environment` | Ağ `limited`; izinli host yok; MCP sunucularına izin açık |
| Diğer oturumlar | `list_sessions`, `list_computer_folders` | A oturumu boşta; 2 PC klasörü kullanılamıyor |
| Artifacts | Liste | 4 yayın |
| Zamanlanmış görevler | Liste | 2 görev; ikisinin de son çalışması `ACCESS_DENIED` |
| Eksik toolkit dosyaları | `find / -name ltx2.py -o -name music_gen.py` | Boş |

## 5. Yerel scratch denemeleri

Hepsi ücretsiz ve geri alınabilir. Hiçbiri depoya kurulum değildir.

| Deneme | Ne yapıldı | Sonuç | Sınır |
|---|---|---|---|
| inkjs 2.4.0, Node | `npm i inkjs@2.4.0`; `inkjs-compiler` ile derleme; `Story` ile oynatma | Seçim listesi doğru; değişken artışı doğru. Kırık hedefte çıkış 1, "Divert target not found" | İlk denemede araştırmacının sözdizimi hatası vardı; düzeltildi |
| inkjs 2.4.0, tarayıcı | `npm pack`; `ink-full.js` (249 KB) ile tarayıcıda derleme; headless Chromium'da Playwright sürücüsü | İki dal oynandı; koşullu seçenek ikinci dalda sunulmadı; 0 hata; `RESULT OK`, çıkış 0 | Tek seferlik duman testi. Gate'e bağlı değil; dal yürüyücü bot yazılmadı |
| inkjs negatif kontrol | Bir seçeneğin sözdizimi bozuldu | Sürücü `TimeoutError` ile çıkış 1 verdi | Testin boşuna yeşil vermediğini gösterir |
| inkjs bütünlük | `sha256sum`; `grep` ile ağ çağrısı sayımı; `npm view` | sha256 `100cf088…f88622`; ağ çağrısı 0; sha512 kayıt defteriyle aynı | — |
| extwee 2.3.18 | `parseTwee`; bağlantı denetimi; Twine 2 HTML'e çevirip geri alma | 3 pasaj; kırık bağlantı yok; gidiş-dönüş tamam | CLI derlemesi hikâye formatı dosyası ister; indirilmedi |
| fountain-js 1.2.4 | Bir deneme senaryosu ayrıştırıldı | 2 sahne başlığı ve karakterler çıktı | — |
| screenplain 0.12.0 | Sanal ortamda FDX, HTML ve PDF üretimi | FDX 972 B; HTML 3.719 B; PDF 26.499 B. Türkçe karakterler PDF'te doğru (görüntü okundu) | — |
| beautiful-mermaid 1.1.3 | `npm i`; Türkçe etiketli ilişki grafiği | SVG 5.396 bayt ve ASCII çıktı | Yalnız kütüphane. Aynı adlı skill çalışmıyor |
| Parametrik SVG turnaround | Python (stdlib) betiği; headless Chrome ile PNG | 4 görünüş aynı renk ve boyda; PNG 1200 × 460 | Yer tutucu figür. Yan ve arka görünüş basit |
| Remotion 2 sn klip | Ayrı mini proje, sürümler video-studio ile aynı; `pnpm install` 6,7 sn; render 26,4 sn | h264, 540 × 960, 30 fps, 60 kare, 2,000 sn; tam çözme hatasız | Hata: en yüksek noktada figür çerçeveden taşıp kırpılıyor. "Yayına hazır" değil |

## 6. Süreklilik deneyi

1. Uydurma, özgün 3 paragraflık bir "kutsal kitap", tutarlı bir sahne ve çelişki ekilmiş bir sahne yazıldı.
2. Cevap anahtarı geçişten **önce** yazıldı ve sha256'sı alındı. Sonunda doğrulama 4/4 tuttu.
3. Anahtar: 1 SERT çelişki, 1 YUMUŞAK çelişki ve çelişki olmayan 2 tuzak.
4. **Yapay zekâ geçişi (Claude):** 2/2 çelişki bulundu; 0 yanlış pozitif; tuzaklar "temiz" listesinde kaldı.
5. **Deterministik geçiş (stdlib betik + kural dosyası):** çıkış 1, 2 bulgu; takvim hesabı temiz.

Sınırlar:

- Yapay zekâ geçişi **kör değildi**: çelişkiyi aynı ajan yazmıştı. Gerçek kör test bağlamsız bir alt ajanla yapılmalı.
- Deterministik geçiş kırılgan: bir yerde yalnız cümle bölme şansıyla doğru sonuç verdi.
- Ölçek: 3 paragraf, iki kitaplık bir kanonla aynı şey değil.

## 7. Statik güvenlik okumaları

| Hedef | Ne okundu | Sonuç |
|---|---|---|
| `story-skills` @ `3c0e034` | Kaynak, paketlenmiş betik, plugin tanımı, skill metinleri | Çalışma zamanında ağ yok; hook yok. Karar: koşullu kabul |
| gamedev deposu @ `4cce500` | İki skill klasörü ve depo geneli | Düz markdown; dış bağlantı yok. Karar: 2 skill pin sonrası kabul |
| `oh-story-claudecode` @ `7e26aa0` | `browser-cdp` skill'i ve kurulum betiği | Kimlik bilgisi toplayan desen. Karar: ret |
| Senkron kova bayrakları | web-design-guidelines, ui-ux-pro-max, website-to-video, text-to-speech, beautiful-mermaid | Beşi de doğrulandı. Karar: ret |
| Kütüphane bütünlüğü | `npm view` ile bağımlılık, kurulum betiği ve bütünlük değerleri | inkjs, extwee, fountain-js, beautiful-mermaid ve remotion'da kurulum betiği yok |
| Lisans dosyaları | Remotion, Rhubarb, Piper, Kokoro, Supertonic, ComfyUI, IP-Adapter ham dosyaları | Bulgular [TOOL_COMPATIBILITY.md](TOOL_COMPATIBILITY.md) içinde |

Ayrıntı ve kararlar: [SKILLS_INVENTORY.md](SKILLS_INVENTORY.md).

## 8. Başarısız olanlar ve nedenleri

| Ne | Sonuç | Neden |
|---|---|---|
| Vercel `get_auth_user` | 404 | Bilinmiyor; `list_teams` çalıştı |
| Canva, Dropbox, TinyFish MCP | Bağlanamadı | Proxy bu hostları reddediyor (403); TinyFish anahtarı da yok |
| ImageMagick ile SVG → PNG | "no images defined" | SVG delegesi yok. Headless Chrome ile aşıldı |
| `beautiful-mermaid` skill'i | Skill tarifiyle çalışmaz | `scripts/` dosyaları ve istediği başka bir skill yok |
| `extwee -c` derleme | Derlemedi | Hikâye formatı dosyası gerekli; indirilmedi |
| `extwee -d` ilk deneme | "Not Twine 2 HTML" | Araştırmacı hatası: girdi yanlış türdeydi. API yolu çalıştı |
| Klonlanan skill kodunu çalıştırma | Reddedildi | Oturum izin sınıflandırıcısı ("dış kaynaklı kod"). Bu yüzden `story continuity` örneği koşmadı |
| `gh api` ile depo meta verisi | 403 | Depo oturuma ekli değil. Depo araması ve `git clone` ile aşıldı |
| fay-hatti lock hash'lerini yeniden üretme | Eşleşmedi | Algoritma bilinmiyor; iki aday denendi. Kurcalama kanıtı değil |
| Yarn Spinner denemesi | Yapılamadı | dotnet yok; resmî JS paketi bulunamadı |
| Araç ve servis sitelerine erişim | Reddedildi | Proxy. Fiyat ve şart bilgileri bu yüzden doğrulanmadı |
| Zamanlanmış görevler | Son çalışmalar başarısız | `ACCESS_DENIED`; izin sorunu çözülmedi |

## 9. Bilerek yapılmayanlar

- **Ücretli üretim:** Higgsfield üretim araçları ve fiyat hazırlama çağrısı çağrılmadı.
- **Dış yazma:** Notion, Drive, Slack, Buffer, Figma ve Claude Docs'ta hiçbir şey oluşturulmadı.
- **Hesap, izin ve anahtar:** hiçbir anahtar istenmedi; oturum ağına host eklenmedi; hiçbir izin değiştirilmedi.
- **Başka oturuma mesaj:** A oturumuna mesaj gönderilmedi; yeni oturum açılmadı.
- **Depoya kurulum:** hiçbir kütüphane, skill ya da plugin depolara eklenmedi. PROVENANCE ve kilit dosyalarına dokunulmadı.
- **Masaüstü araçları:** Krita, Inkscape, Blender, Manim, Rhubarb ve Godot bu konteynerde yok; kurulmadı ve denenmedi.
- **İndirilmeyenler:** inklecate ikilisi, Twine hikâye formatı, yt-dlp, whisper.
- **Kör süreklilik testi:** ek maliyet ve izin yüzeyi nedeniyle ayrı oturum açılmadı.

Sıradaki adımlar: [NEXT_STEPS.md](NEXT_STEPS.md).
